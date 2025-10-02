#!/usr/bin/env python3
"""Loose dry-run: 采用低阈值列出可合并候选，但不做删除或写入。
"""
from pathlib import Path
import difflib

ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {'.git', 'node_modules', 'out', 'archive', '__pycache__', '.venv', '.venv_broken_'}
THRESHOLD = 0.6
OUT = ROOT / 'scripts' / '_merge_candidates_loose.txt'


def iter_text_files(root: Path):
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        if set(p.parts) & IGNORE_DIRS:
            continue
        try:
            with p.open('rb') as fh:
                sample = fh.read(4096)
            sample.decode('utf-8')
        except Exception:
            continue
        yield p


def read_text(p: Path):
    return p.read_text(encoding='utf-8', errors='ignore')


def similar(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def main():
    files = list(iter_text_files(ROOT))
    by_name = {}
    for f in files:
        by_name.setdefault(f.name, []).append(f)
    out_lines = []
    for name, flist in by_name.items():
        if len(flist) < 2:
            continue
        # choose largest as keep
        flist_sorted = sorted(flist, key=lambda p: p.stat().st_size, reverse=True)
        keep = flist_sorted[0]
        keep_text = read_text(keep)
        for other in flist_sorted[1:]:
            other_text = read_text(other)
            sim = similar(keep_text, other_text)
            if sim >= THRESHOLD:
                out_lines.append(f'[{sim:.3f}] {other} -> {keep}')
    if out_lines:
        OUT.write_text('\n'.join(out_lines)+"\n")
        print(f'Candidates written to {OUT}')
    else:
        OUT.write_text('No candidates\n')
        print('No candidates')


if __name__ == '__main__':
    main()
