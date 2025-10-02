#!/usr/bin/env python3
"""把在 find_duplicates.py 报告中出现的重复文件（每组的非首项）移动到 archive/removed_duplicates/<timestamp>/
并保留原始相对路径结构。
"""
from pathlib import Path
import datetime
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DRY = ROOT / 'scripts' / '_duplicates_dryrun.txt'
OUT_LIST = ROOT / 'scripts' / '_duplicates_to_move.txt'
MOVED_LOG = ROOT / 'scripts' / '_duplicates_moved.txt'


def parse_dry(dry_file: Path):
    groups = []
    if not dry_file.exists():
        print('Dry-run file not found:', dry_file)
        return groups
    cur = None
    with dry_file.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                cur = None
                continue
            if line.startswith('Hash:'):
                cur = []
                groups.append(cur)
                continue
            if cur is not None and line.strip().startswith('['):
                # line like: '  [0] path'
                parts = line.strip().split(']', 1)
                if len(parts) == 2:
                    idx = parts[0].lstrip('[').strip()
                    path = parts[1].strip()
                    cur.append((int(idx), path))
    return groups


def main():
    groups = parse_dry(DRY)
    if not groups:
        print('No groups to move.')
        return
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    archive_base = ROOT / 'archive' / 'removed_duplicates' / ts
    moved = []
    OUT_LIST.write_text('')
    MOVED_LOG.write_text('')
    for g in groups:
        # keep idx==0
        to_move = [p for idx, p in g if idx != 0]
        for rel in to_move:
            src = ROOT / rel
            if not src.exists():
                OUT_LIST.write_text(OUT_LIST.read_text() + f'MISSING {rel}\n')
                continue
            dst = archive_base / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            moved.append((rel, str(dst.relative_to(ROOT))))
            MOVED_LOG.write_text(MOVED_LOG.read_text() + f'{rel} -> {dst.relative_to(ROOT)}\n')
    if moved:
        OUT_LIST.write_text('\n'.join([m[0] for m in moved]))
        print(f'Moved {len(moved)} files to {archive_base}')
    else:
        print('No files moved.')


if __name__ == '__main__':
    main()
