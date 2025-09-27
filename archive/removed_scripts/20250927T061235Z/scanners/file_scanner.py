"""Proxy for ai/scanner/file_scanner.py"""
from pathlib import Path
import runpy, sys

AI_DIR = Path(__file__).resolve().parents[1] / 'ai' / 'scanner'
sys.path.insert(0, str(AI_DIR.parent))

def load_module():
    return runpy.run_path(str(AI_DIR / 'file_scanner.py'))
