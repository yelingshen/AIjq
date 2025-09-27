#!/usr/bin/env python3
"""Wrapper to start the full Flask server (ai/server.py) from a centralized deployment folder.
This script does not modify original files; it adjusts sys.path and execs the module.
"""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AI_DIR = ROOT / 'ai'
sys.path.insert(0, str(AI_DIR))

if __name__ == '__main__':
    print('[deployment] Starting full server (ai/server.py)')
    runpy.run_path(str(AI_DIR / 'server.py'), run_name='__main__')
