#!/usr/bin/env python3
"""Wrapper to run `ai/start_ai_assistant.py` which performs scanning and reporting."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AI_DIR = ROOT / 'ai'
sys.path.insert(0, str(AI_DIR))

if __name__ == '__main__':
    print('[deployment] Starting assistant (ai/start_ai_assistant.py)')
    runpy.run_path(str(AI_DIR / 'start_ai_assistant.py'), run_name='__main__')
