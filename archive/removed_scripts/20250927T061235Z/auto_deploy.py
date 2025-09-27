"""Compatibility wrapper: delegate to `scripts/auto_deploy.py`.

This file is intentionally minimal to preserve backward compatibility.
Full implementation lives in `scripts/auto_deploy.py`.
"""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
runpy.run_path(str(ROOT / 'scripts' / 'auto_deploy.py'), run_name='__main__')