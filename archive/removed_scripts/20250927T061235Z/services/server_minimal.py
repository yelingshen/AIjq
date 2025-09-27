"""Proxy for ai/server_minimal.py"""
from pathlib import Path
import runpy, sys

AI_DIR = Path(__file__).resolve().parents[1] / 'ai'
sys.path.insert(0, str(AI_DIR))

def start():
    runpy.run_path(str(AI_DIR / 'server_minimal.py'), run_name='__main__')
