#!/usr/bin/env python3
"""Dry-run to find similar-but-different files across the repo.
Writes scripts/_merge_candidates_dryrun.txt and scripts/_merge_dryrun_log.txt.
Does NOT modify or move any files.
"""
from pathlib import Path
import difflib
import time

BASE = Path(__file__).resolve().parents[1]
ALL = BASE / 'scripts' / '_all_scripts.txt'
OUT = BASE / 'scripts' / '_merge_candidates_dryrun.txt'
LOG = BASE / 'scripts' / '_merge_dryrun_log.txt'
TS = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())

THRESH = 0.30
SUPPORTED = {'.py', '.sh', '.js', '.service'}


def read_list():
    if not ALL.exists():
        return []
    lines = [ln.strip() for ln in ALL.read_text(encoding='utf-8').splitlines() if ln.strip()]
    files = [Path(p) for p in lines if not p.startswith('archive/') and Path(p).is_file()]
    return [f for f in files if f.suffix in SUPPORTED]


def tokens_of_name(p: Path):
    name = p.stem.lower()
    toks = [t for t in name.replace('-', '_').split('_') if t]
    return set(toks)


def sim(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def main():
    files = read_list()
    txt = {f: f.read_text(encoding='utf-8', errors='ignore') for f in files}
    by_token = {}
    for f in files:
        by_token.setdefault(tuple(sorted(tokens_of_name(f))), []).append(f)

    candidates = []
    logs = []
    # compare within token groups and also compare files sharing any token
    for i, f1 in enumerate(files):
        t1 = tokens_of_name(f1)
        for j in range(i + 1, len(files)):
            f2 = files[j]
            t2 = tokens_of_name(f2)
            if not t1 and not t2:
                continue
            # require at least one token overlap OR identical basename
            if t1.intersection(t2) or f1.name == f2.name:
                a = txt.get(f1, '')
                b = txt.get(f2, '')
                if a == b:
                    continue
                s = sim(a, b)
                if s >= THRESH:
                    candidates.append((s, f1, f2))
                    logs.append(f'{s:.3f} {f1} {f2}')

    candidates.sort(reverse=True, key=lambda x: x[0])
    OUT.write_text('\n'.join(f'{s:.3f} {p1} {p2}' for s, p1, p2 in candidates), encoding='utf-8')
    LOG.write_text('\n'.join(logs), encoding='utf-8')
    print('Dry-run complete. Candidates:', len(candidates))


if __name__ == '__main__':
    main()
