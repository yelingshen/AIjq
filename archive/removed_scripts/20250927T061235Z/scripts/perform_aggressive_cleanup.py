#!/usr/bin/env python3
"""Aggressive cleanup: move candidate files/directories into archive/.

This script is more aggressive than `scan_and_archive_scripts.py` and will
move whole directories (like legacy folders) if they appear unused. It is
conservative about core directories (`ai`, `scripts`, `deployment`, `.github`, `test`).
Always review `archive/` after running.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / 'archive'
ARCHIVE.mkdir(exist_ok=True)

PROTECT = {'ai', 'scripts', 'deployment', '.github', 'test', '.git'}
ARCHIVE_NAME = 'archive'
LIKELY_LEGACY_DIRS = ['old', 'backup', 'legacy', 'tmp', 'dist', 'build']

def move_to_archive(p: Path):
    dst = ARCHIVE / p.name
    i = 1
    while dst.exists():
        dst = ARCHIVE / f"{p.name}.{i}"
        i += 1
    shutil.move(str(p), str(dst))
    print(f"Archived {p} -> {dst}")

def run():
    for candidate in ROOT.iterdir():
        # never touch the archive dir itself
        if candidate.name == ARCHIVE_NAME:
            continue
        if candidate.name in PROTECT:
            continue
        if candidate.is_dir() and candidate.name.lower() in LIKELY_LEGACY_DIRS:
            move_to_archive(candidate)
            continue
        # if directory contains no .py files (likely not code), archive (but skip protected)
        if candidate.is_dir():
            py_files = list(candidate.rglob('*.py'))
            if not py_files and candidate.name not in PROTECT and candidate.name != ARCHIVE_NAME:
                move_to_archive(candidate)

if __name__ == '__main__':
    run()
