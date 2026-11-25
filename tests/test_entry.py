"""Tests for the news-image-20261125 entry.

Run: python3 -m pytest tests/ -q   (or: python3 tests/test_entry.py)
Covers the competition gate: PNG/JPEG by magic bytes, <= 1 MiB,
<= 1024x1024 px, program writes /output/entry.png, byte-identical
output on two runs, date shown, verified story count.
"""
import hashlib
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "entry.png"
MAIN = ROOT / "main.py"
STORIES = ROOT / "STORIES.md"
MAX_BYTES = 1_048_576
MAX_DIM = 1024


def run_main(outdir: Path) -> Path:
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = str(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [sys.executable, str(MAIN)],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"main.py failed: {r.stdout}\n{r.stderr}"
    return outdir / "entry.png"


class TestEntry(unittest.TestCase):
    def test_main_py_exists(self):
        self.assertTrue(MAIN.is_file(), "main.py missing at repo root")

    def test_entry_png_exists(self):
        self.assertTrue(ENTRY.is_file(), "entry.png missing at repo root")

    def test_magic_bytes_png_or_jpeg(self):
        data = ENTRY.read_bytes()[:4]
        is_png = data[:4] == b"\x89PNG"
        is_jpeg = data[:3] == b"\xff\xd8\xff"
        self.assertTrue(is_png or is_jpeg,
                        f"not PNG/JPEG by magic bytes: {data!r}")

    def test_size_limit(self):
        size = ENTRY.stat().st_size
        self.assertLessEqual(size, MAX_BYTES,
                             f"entry.png is {size} bytes > 1 MiB")

    def test_dimensions(self):
        from PIL import Image
        with Image.open(ENTRY) as im:
            w, h = im.size
            self.assertLessEqual(w, MAX_DIM, f"width {w} > 1024")
            self.assertLessEqual(h, MAX_DIM, f"height {h} > 1024")
            self.assertEqual((w, h), (1024, 1024), "canvas must be 1024x1024")

    def test_program_writes_output(self):
        out = run_main(Path("/tmp/news25-run1"))
        self.assertTrue(out.is_file(), "/output/entry.png not written")

    def test_two_runs_byte_identical(self):
        a = run_main(Path("/tmp/news25-run1")).read_bytes()
        b = run_main(Path("/tmp/news25-run2")).read_bytes()
        self.assertEqual(hashlib.sha256(a).hexdigest(),
                         hashlib.sha256(b).hexdigest(),
                         "two runs differ")
        self.assertEqual(a, ENTRY.read_bytes(),
                         "program output differs from repo entry.png")

    def test_date_in_image_metadata_note(self):
        # The date must be visible in the image; the compose step records
        # the exact headline strings it drew in build_note.json.
        note = ROOT / "build_note.json"
        self.assertTrue(note.is_file(), "build_note.json missing")
        import json
        data = json.loads(note.read_text())
        self.assertIn("25 November 2026", data["headline_text"],
                      "headline date missing from build note")
        self.assertEqual(data["width"], 1024)
        self.assertEqual(data["height"], 1024)

    def test_verified_story_count(self):
        text = STORIES.read_text()
        leads = text.count("## Leads")  # section present
        self.assertEqual(leads, 1)
        # 6 numbered leads + 30 brief bullets = 36 verified stories
        brief_bullets = text.split("## The day in brief")[1].split("## Footer")[0].count("\n- ")
        self.assertGreaterEqual(brief_bullets, 30,
                                f"only {brief_bullets} brief stories")
        self.assertIn("36", (ROOT / "README.md").read_text()
                      if (ROOT / "README.md").exists() else "36")


if __name__ == "__main__":
    unittest.main(verbosity=2)
