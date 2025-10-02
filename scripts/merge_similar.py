#!/usr/bin/env python3
"""寻找并合并相似文本文件：
- 只处理可解码为 UTF-8 的文本文件
- 按文件名分组（相同 basename），对同组内两两比较相似度
- 如果相似度 >= THRESHOLD（默认 0.85），把较短/较旧的内容合并到较长的文件（作为注释段），并删除副本
- 生成脚本报告：scripts/_merge_similar_report.txt

警告：自动合并有风险。脚本尽量保守（只在高相似度时合并），并在合并时添加注释标记。
"""
from pathlib import Path
import difflib
import datetime
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {'.git', 'node_modules', 'out', 'archive', '__pycache__', '.venv', '.venv_broken_'}
THRESHOLD = 0.85
REPORT = ROOT / 'scripts' / '_merge_similar_report.txt'


def iter_text_files(root: Path):
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        if set(p.parts) & IGNORE_DIRS:
            continue
        # skip binary-like by try decode small chunk
        try:
            with p.open('rb') as fh:
                sample = fh.read(4096)
            sample.decode('utf-8')
        except Exception:
            continue
        yield p


def read_text(p: Path):
    return p.read_text(encoding='utf-8', errors='ignore')


def write_text(p: Path, txt: str):
    p.write_text(txt, encoding='utf-8')


def group_by_basename(files):
    d = {}
    for f in files:
        key = f.name
        d.setdefault(key, []).append(f)
    return d


def similar(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def merge_pair(keep: Path, remove: Path):
    # Keep content of keep, but if remove has non-overlapping parts, append them with markers
    s_keep = read_text(keep)
    s_rem = read_text(remove)
    if s_keep == s_rem:
        # identical: simply remove the duplicate
        remove.unlink()
        return f"IDENTICAL: removed {remove}"
    # if remove fully contained in keep, just delete
    if s_rem in s_keep:
        remove.unlink()
        return f"CONTAINED: removed {remove} (content already in {keep})"
    # else create an appended section, with clear markers
    marker = f"\n\n/* MERGED FROM: {remove} AT {datetime.datetime.utcnow().isoformat()}Z */\n"
    combined = s_keep + marker + s_rem
    write_text(keep, combined)
    remove.unlink()
    return f"MERGED: {remove} -> {keep} (appended)"


def main():
    files = list(iter_text_files(ROOT))
    groups = group_by_basename(files)
    reports = []
    merged_count = 0
    for name, flist in groups.items():
        if len(flist) < 2:
            continue
        # compare every pair
        # sort by file size desc so first is likely canonical
        flist_sorted = sorted(flist, key=lambda p: p.stat().st_size, reverse=True)
        keep = flist_sorted[0]
        keep_text = read_text(keep)
        for other in flist_sorted[1:]:
            other_text = read_text(other)
            sim = similar(keep_text, other_text)
            if sim >= THRESHOLD:
                try:
                    res = merge_pair(keep, other)
                    reports.append(f'[{sim:.3f}] {res}')
                    merged_count += 1
                except Exception as e:
                    reports.append(f'ERROR merging {other} into {keep}: {e}')
            else:
                reports.append(f'[{sim:.3f}] SKIP (below threshold) {other} vs {keep}')
    if not reports:
        REPORT.write_text('No similar files merged.\n')
        print('No similar files merged.')
    else:
        REPORT.write_text('\n'.join(reports) + '\n')
        print(f'Merged {merged_count} files. See {REPORT}')


if __name__ == '__main__':
    main()
