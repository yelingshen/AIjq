#!/usr/bin/env python3
"""扫描仓库，按文件内容（MD5）分组，生成重复文件报告。
不会移动任何文件（dry-run）。
输出：scripts/_duplicates_dryrun.txt、scripts/_duplicates_full.txt
"""
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {'.git', 'archive', 'node_modules', 'out', '.venv', '.venv_broken_', '__pycache__'}


def iter_files(root: Path):
    for p in root.rglob('*'):
        if p.is_file():
            # skip files in ignore dirs
            parts = set(p.parts)
            if parts & IGNORE_DIRS:
                continue
            yield p


def md5_file(path: Path):
    h = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    by_hash = defaultdict(list)
    for f in iter_files(ROOT):
        try:
            h = md5_file(f)
        except Exception as e:
            print('skip', f, 'err', e, file=sys.stderr)
            continue
        by_hash[h].append(str(f.relative_to(ROOT)))

    dup_groups = {h: files for h, files in by_hash.items() if len(files) > 1}

    out_dir = ROOT / 'scripts'
    out_dir.mkdir(exist_ok=True)
    dry = out_dir / '_duplicates_dryrun.txt'
    full = out_dir / '_duplicates_full.txt'

    with dry.open('w', encoding='utf-8') as fd, full.open('w', encoding='utf-8') as ff:
        if not dup_groups:
            fd.write('No duplicates found.\n')
            ff.write('No duplicates found.\n')
            print('No duplicates found.')
            return
        for h, files in dup_groups.items():
            fd.write(f'Hash: {h}\n')
            for i, f in enumerate(files):
                fd.write(f'  [{i}] {f}\n')
            fd.write('\n')

            ff.write(f'Hash: {h}\n')
            for i, f in enumerate(files):
                ff.write(f'  [{i}] {f}\n')
            ff.write('\n')

    print(f'Dry-run report saved to {dry} and full report to {full}')


if __name__ == '__main__':
    main()
