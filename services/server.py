"""Proxy for ai/server.py. Imports and exposes a start function and Flask app if available."""
from pathlib import Path
import runpy, sys

AI_DIR = Path(__file__).resolve().parents[1] / 'ai'
sys.path.insert(0, str(AI_DIR))

def start():
    # run as __main__ to preserve behavior
    runpy.run_path(str(AI_DIR / 'server.py'), run_name='__main__')

def get_app():
    # Attempt to import Flask app if defined
    try:
        mod = runpy.run_path(str(AI_DIR / 'server.py'))
        return mod.get('app')
    except Exception:
        return None
