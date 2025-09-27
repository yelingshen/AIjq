"""Proxy for ai/context_manager.py"""
from pathlib import Path
import runpy, sys

AI_DIR = Path(__file__).resolve().parents[1] / 'ai'
sys.path.insert(0, str(AI_DIR))

def load_module():
    return runpy.run_path(str(AI_DIR / 'context_manager.py'))

