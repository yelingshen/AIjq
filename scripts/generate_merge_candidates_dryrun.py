#!/usr/bin/env python3
"""
Dry-run merge candidate generator.

Scans repository for script/config files, groups by filename tokens to avoid O(n^2) all-pairs,
and reports pairs with content-similarity >= threshold (default 0.30).

Outputs a short summary to stdout and verbose details to stderr (so callers can redirect separately).
"""
from __future__ import annotations

import argparse
import difflib
import os
import re
import sys
from collections import defaultdict
from typing import List, Set, Tuple


def is_ignored_path(path: str) -> bool:
    parts = path.split(os.sep)
    ignore_prefixes = {".git", "archive", "venv", ".venv", "node_modules", "build", "dist", "__pycache__"}
    return any(p in ignore_prefixes for p in parts)


def collect_files(root: str, exts: Set[str], max_size: int = 200 * 1024) -> List[str]:
    files: List[str] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        # skip hidden and ignored directories early
        if is_ignored_path(dirpath):
            continue
        for fn in filenames:
            if fn.startswith("."):
                continue
            path = os.path.join(dirpath, fn)
            if is_ignored_path(path):
                continue
            if not any(fn.endswith(ext) for ext in exts):
                continue
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            if size > max_size:
                print(f"Skipping large file: {path} ({size} bytes)", file=sys.stderr)
                continue
            files.append(path)
    return files


_token_re = re.compile(r"[A-Za-z0-9]{3,}")


def tokenize_filename(path: str) -> Set[str]:
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    tokens = set(m.group(0).lower() for m in _token_re.finditer(name))
    return tokens


def read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        try:
            with open(path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            print(f"Failed to read {path}: {e}", file=sys.stderr)
            return ""


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".", help="Repository root to scan")
    p.add_argument("--threshold", type=float, default=0.30, help="Similarity threshold (0-1)")
    p.add_argument("--max-size", type=int, default=200 * 1024, help="Max file size in bytes to consider")
    p.add_argument("--limit-per-file", type=int, default=200, help="Max candidates compared per file")
    args = p.parse_args(argv)

    exts = {".py", ".sh", ".service", ".yml", ".yaml", ".json", ".md", ".js", ".ts"}
    print(f"Scanning {args.root} for files with extensions: {sorted(exts)} (max-size={args.max_size})")
    files = collect_files(args.root, exts, max_size=args.max_size)
    print(f"Found {len(files)} candidate files (filtered)")

    # Build token groups
    token_map: defaultdict[str, List[str]] = defaultdict(list)
    file_tokens = {}
    for f in files:
        toks = tokenize_filename(f)
        file_tokens[f] = toks
        for t in toks:
            token_map[t].append(f)

    # For each file, build candidate set by union of token groups (avoid full n^2)
    seen_pairs: Set[Tuple[str, str]] = set()
    results: List[Tuple[str, str, float]] = []

    for f in files:
        toks = file_tokens.get(f, set())
        candidates: Set[str] = set()
        for t in toks:
            for other in token_map.get(t, []):
                if other != f:
                    candidates.add(other)
        # If no tokens (odd filenames), fallback to same-extension grouping
        if not candidates:
            _, ext = os.path.splitext(f)
            for other in files:
                if other != f and other.endswith(ext):
                    candidates.add(other)

        # Limit candidate comparisons
        candidates_list = sorted(candidates)
        if len(candidates_list) > args.limit_per_file:
            candidates_list = candidates_list[: args.limit_per_file]

        content_a = read_text(f)
        for other in candidates_list:
            a, b = (f, other) if f < other else (other, f)
            if (a, b) in seen_pairs:
                continue
            seen_pairs.add((a, b))
            content_b = read_text(other)
            score = similarity(content_a, content_b)
            if score >= args.threshold:
                results.append((f, other, score))
                print(f"CANDIDATE: {f} || {other} => {score:.3f}", file=sys.stderr)

    # Write concise summary to stdout
    if not results:
        print("Done. Candidates: 0")
        return 0

    results_sorted = sorted(results, key=lambda x: -x[2])
    print(f"Done. Candidates: {len(results_sorted)}")
    print()
    print("Top candidates:")
    for f1, f2, s in results_sorted[:200]:
        print(f"{s:.3f}\t{f1}\t{f2}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
