#!/usr/bin/env python3
"""Entry point for the news-image-20261125 bounty.

Copies the front-page image built by compose.py (entry.png, held in this
repository) to the grader's output directory. No network, no writes
outside the output directory, deterministic: the same bytes every run.

The grader runs this twice; both runs must write the same bytes, so the
copy is byte-for-byte and the output directory itself is never removed.
"""
import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
