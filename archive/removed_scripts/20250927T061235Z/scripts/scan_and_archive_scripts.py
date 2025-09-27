#!/usr/bin/env python3
"""Scan repository for duplicate or legacy scripts and move them to archive/.

This tool is conservative: it moves files to `archive/` rather than deleting them.
It will not move files in `test/`, `.github/`, `ai/`, `deployment/` except when duplicates
are detected or when files are clearly legacy (pattern matching on filename).
"""
import hashlib
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / 'archive'
ARCHIVE.mkdir(exist_ok=True)

# Files and directories to ignore at top-level
IGNORE_DIRS = {'test', '.git', '.github', 'ai', 'deployment', 'scripts', 'BXDM'}
KEEP_FILES = {'README.md', 'package.json', 'CHANGELOG.md', 'auto_deploy.py'}

def hash_file(p: Path):
    h = hashlib.sha256()
    try:
        with p.open('rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def is_legacy(filename: str):
    name = filename.lower()
    legacy_keywords = ['old', 'backup', 'bak', 'deprecated', 'legacy', 'tmp', 'copy']
    return any(k in name for k in legacy_keywords)

def scan_and_archive():
    # build hash map for duplicates
    hash_map = {}
    moved = []
    for p in ROOT.rglob('*'):
        if p.is_dir():
            continue
        rel = p.relative_to(ROOT)
        parts = rel.parts
        if parts[0] in IGNORE_DIRS:
            continue
        if rel.name in KEEP_FILES:
            continue
        if p.suffix not in ('.py', '.sh'):
            continue
        h = hash_file(p)
        if not h:
            continue
        if h in hash_map:
            # duplicate - move this one to archive
            dst = ARCHIVE / rel.name
            i = 1
            while dst.exists():
                dst = ARCHIVE / f"{rel.stem}.{i}{rel.suffix}"
                i += 1
            shutil.move(str(p), str(dst))
            moved.append((str(p), str(dst)))
        else:
            hash_map[h] = p

    # second pass: move legacy-named scripts at repo root
    for p in ROOT.iterdir():
        if p.is_file() and p.suffix in ('.py', '.sh') and p.name not in KEEP_FILES:
            if is_legacy(p.name) or p.name.endswith('~') or p.name.startswith('old_'):
                dst = ARCHIVE / p.name
                i = 1
                while dst.exists():
                    dst = ARCHIVE / f"{p.stem}.{i}{p.suffix}"
                    i += 1
                shutil.move(str(p), str(dst))
                moved.append((str(p), str(dst)))

    # also detect small one-liner scripts (<5 lines) that look like temp and archive them
    for p in ROOT.iterdir():
        if p.is_file() and p.suffix in ('.py', '.sh') and p.name not in KEEP_FILES:
            try:
                lines = p.read_text(errors='ignore').splitlines()
                if len(lines) <= 5 and any('TODO' in l or '# temporary' in l.lower() for l in lines):
                    dst = ARCHIVE / p.name
                    i = 1
                    while dst.exists():
                        dst = ARCHIVE / f"{p.stem}.{i}{p.suffix}"
                        i += 1
                    shutil.move(str(p), str(dst))
                    moved.append((str(p), str(dst)))
            except Exception:
                continue

    print(f"Archived {len(moved)} files to {ARCHIVE}")
    for src, dst in moved:
        print(f"  {src} -> {dst}")

    # Additional conservative root cleanups: move small known noisy files
    extra = ['1', 'README2.md', 'package-lock.json', 'server_dependency.log']
    for name in extra:
        p = ROOT / name
        if p.exists():
            dst = ARCHIVE / p.name
            i = 1
            while dst.exists():
                dst = ARCHIVE / f"{p.stem}.{i}{p.suffix}"
                i += 1
            shutil.move(str(p), str(dst))
            print(f"Conservatively archived root file: {p} -> {dst}")

if __name__ == '__main__':
    scan_and_archive()
