import os
import shutil
import argparse
import time
import socket
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIRS = [
    BASE_DIR.parent / 'ai' / '__pycache__',
    BASE_DIR.parent / 'scanner' / '__pycache__',
    BASE_DIR.parent / 'utils' / '__pycache__',
]

def clear_cache():
    cleared = []
    for cache_dir in CACHE_DIRS:
        abs_dir = cache_dir.resolve()
        if abs_dir.exists():
            shutil.rmtree(abs_dir)
            cleared.append(str(abs_dir))
    return cleared

def ai_cache_self_check():
    removed = []
    for cache_dir in CACHE_DIRS:
        abs_dir = cache_dir.resolve()
        if abs_dir.exists():
            for root, dirs, files in os.walk(str(abs_dir)):
                for f in files:
                    fp = Path(root) / f
                    if f.endswith('.pyc') and fp.stat().st_size == 0:
                        fp.unlink()
                        removed.append(str(fp))
                if not files and not dirs:
                    Path(root).rmdir()
                    removed.append(str(root))
    return removed
