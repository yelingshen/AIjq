#!/usr/bin/env python3
"""
Auto-merge similar files (conservative):
- Reads scripts/_all_scripts.txt and scripts/_hashes.txt
- Finds file pairs with high similarity (but not identical)
- For supported extensions (.py, .sh, .js, .service) creates a conservative merged file:
  keeper content followed by commented copies of other variants
- Moves non-keeper originals to archive/merged_originals/<ts>/...
- Writes reports: scripts/_merge_candidates.txt and scripts/_merge_log.txt

This is intentionally conservative to avoid breaking behavior; manual review recommended.
"""
import difflib
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ALL_LIST = BASE / 'scripts' / '_all_scripts.txt'
HASHES = BASE / 'scripts' / '_hashes.txt'
MERGE_CANDIDATES = BASE / 'scripts' / '_merge_candidates.txt'
MERGE_LOG = BASE / 'scripts' / '_merge_log.txt'

TS = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
ARCHIVE_DIR = BASE / 'archive' / 'merged_originals' / TS
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED = {'.py', '.sh', '.js', '.service'}


def read_all_scripts():
    if not ALL_LIST.exists():
        return []
    lines = [line.strip() for line in ALL_LIST.read_text(encoding='utf-8').splitlines() if line.strip()]
    # filter out archive, venv, node_modules
    def ok(p):
        if p.startswith('archive/') or p.startswith('.venv') or p.startswith('venv/') or p.startswith('node_modules/'):
            return False
        return True
    return [Path(p) for p in lines if ok(p) and Path(p).is_file()]


def load_text(p: Path):
    try:
        return p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''


def similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def choose_keeper(candidates):
    # prefer files in these directories
    priority = ['deployment', 'scripts', 'ai', 'services', 'utils']
    best = None
    best_score = -1
    for p in candidates:
        s = 0
        sp = str(p)
        for i, pref in enumerate(priority):
            if f'/{pref}/' in sp or sp.startswith(pref + '/'):
                s = 100 - i
                break
        # shorter path slightly preferred
        s += max(0, 10 - len(sp.split('/')))
        if s > best_score:
            best_score = s
            best = p
    return best or sorted(candidates)[0]


def comment_block(text: str, ext: str) -> str:
    # prefix each line with comment marker
    if ext == '.py' or ext == '.sh' or ext == '.service':
        prefix = '# '
    elif ext == '.js':
        prefix = '// '
    else:
        prefix = '# '
    return '\n'.join(prefix + line for line in text.splitlines())


def main():
    files = read_all_scripts()
    # only consider supported extensions
    files = [f for f in files if f.suffix in SUPPORTED]
    # number of candidate files (not used directly)
    _count_files = len(files)
    pairs = []
    # compute content cache
    contents = {f: load_text(f) for f in files}
    # quick filter by basename
    by_name = {}
    for f in files:
        by_name.setdefault(f.name, []).append(f)

    for _basename, group in by_name.items():
        if len(group) < 2:
            continue
        # pairwise compare within group
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                f1 = group[i]
                f2 = group[j]
                a = contents.get(f1, '')
                b = contents.get(f2, '')
                if not a and not b:
                    continue
                if a == b:
                    continue
                sim = similarity(a, b)
                if sim >= 0.45:  # threshold, conservative
                    pairs.append((sim, f1, f2))

    pairs.sort(reverse=True, key=lambda x: x[0])
    MERGE_CANDIDATES.write_text('\n'.join(f'{s:.3f} {p1} {p2}' for s, p1, p2 in pairs), encoding='utf-8')

    merged = []
    log_lines = []
    processed = set()
    limit = 200
    for sim, f1, f2 in pairs[:limit]:
        if f1 in processed or f2 in processed:
            continue
        group = [f1, f2]
        # extend group by other files with same name
        same = [p for p in by_name.get(f1.name, []) if p not in group]
        for p in same:
            if p not in group:
                group.append(p)
        keeper = choose_keeper(group)
        others = [p for p in group if p != keeper]
        if not others:
            continue
        # create merged content: keeper content, then commented alternatives
        ktext = contents.get(keeper, '')
        merged_text = []
        merged_text.append('# MERGED FILE - conservative merge created on %s' % TS)
        merged_text.append('# Keeper: %s' % str(keeper))
        merged_text.append('')
        merged_text.append(ktext)
        for o in others:
            otext = contents.get(o, '')
            merged_text.append('\n# === ALTERNATE ORIGINAL: %s ===\n' % str(o))
            merged_text.append(comment_block(otext, o.suffix))
        newtext = '\n'.join(merged_text)
        # backup others to archive
        for o in others:
            dest = ARCHIVE_DIR / o
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                o.rename(dest)
                log_lines.append(f'MOVED {o} -> {dest} (keeper: {keeper})')
            except Exception as e:
                log_lines.append(f'FAILED_MOVE {o} -> {dest}: {e}')
        # write merged text to keeper path
        try:
            keeper.write_text(newtext, encoding='utf-8')
            log_lines.append(f'MERGED into keeper {keeper} including {len(others)} alternates')
        except Exception as e:
            log_lines.append(f'FAILED_WRITE {keeper}: {e}')
        processed.update(group)
        merged.append((keeper, others, sim))

    MERGE_LOG.write_text('\n'.join(log_lines), encoding='utf-8')
    print('Done. Candidates:', len(pairs), 'Merged:', len(merged))


if __name__ == '__main__':
    main()
