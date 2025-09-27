#!/usr/bin/env python3
"""Consolidate scattered archive files into sensible groups.

This script scans `archive/` for patterns that look like virtualenv/site-packages
fragments (many __init__.N.py entries and top-level package modules) and prints
a preview of the proposed consolidation moves. Use --apply to perform the
moves. The script is conservative and will never delete; it only moves files
under archive/ into subfolders like `archive/venv_files/` or `archive/site_packages/`.
"""
import argparse
from pathlib import Path
import shutil
import re

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / 'archive'

PATTERNS = [
    re.compile(r"^__init__\.(?:\d+)$"),
    re.compile(r"^(pip|pkg_resources|setuptools|requests|urllib3|werkzeug|pygments|idna|certifi)(?:.*)\.py$"),
]


def find_candidates():
    candidates = []
    if not ARCHIVE.exists():
        return candidates
    for p in ARCHIVE.iterdir():
        if p.is_file():
            name = p.name
            if any(pat.match(name) for pat in PATTERNS):
                candidates.append(p)
            elif name.endswith('.py') and len(name.split('.'))<=2 and len(name) <= 30:
                # likely a top-level module moved into archive
                candidates.append(p)
    return candidates


def plan_moves(candidates):
    moves = []
    venv_dir = ARCHIVE / 'venv_files'
    site_dir = ARCHIVE / 'site_packages'
    venv_dir.mkdir(exist_ok=True)
    site_dir.mkdir(exist_ok=True)
    for p in candidates:
        # heuristics: names that look like __init__ or vendor libs -> site_packages
        if p.name.startswith('__init__') or p.name in ('requests.py', 'urllib3.py', 'werkzeug.py'):
            dst = site_dir / p.name
        else:
            dst = venv_dir / p.name
        # avoid clobber
        i = 1
        while dst.exists():
            dst = dst.with_name(f"{dst.stem}.{i}{dst.suffix}")
            i += 1
        moves.append((p, dst))
    return moves


def apply_moves(moves):
    for src, dst in moves:
        shutil.move(str(src), str(dst))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Apply changes')
    args = ap.parse_args()

    candidates = find_candidates()
    moves = plan_moves(candidates)

    if not moves:
        print('No consolidation candidates found in archive/.')
    else:
        print('Planned moves:')
        for s, d in moves:
            print(f'  {s} -> {d}')
        if args.apply:
            print('\nApplying moves...')
            apply_moves(moves)
            print('Done.')
        else:
            print('\nRun with --apply to perform these moves.')
