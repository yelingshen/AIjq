"""Proxy for ai/cli.py to keep CLI importable under cli.cli"""
from pathlib import Path
import runpy, sys

AI_DIR = Path(__file__).resolve().parents[1] / 'ai'
sys.path.insert(0, str(AI_DIR))

def main(argv=None):
    if argv is None:
        argv = []
    # emulate command-line by modifying sys.argv
    import sys as _sys
    old = _sys.argv
    try:
        _sys.argv = [_sys.argv[0]] + list(argv)
        runpy.run_path(str(AI_DIR / 'cli.py'), run_name='__main__')
    finally:
        _sys.argv = old
