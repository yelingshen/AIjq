"""Proxy for ai/report_generator.py

This proxy imports the ReportGenerator class from ai/report_generator.py
and exposes it at module level so other modules can `from utils.report_generator import ReportGenerator`.
"""
from pathlib import Path
import importlib.util
import sys

AI_DIR = Path(__file__).resolve().parents[1] / 'ai'
sys.path.insert(0, str(AI_DIR))

try:
    # Attempt direct import if package layout allows
    from report_generator import ReportGenerator  # type: ignore
except Exception:
    # Fallback: load module via importlib and bind ReportGenerator
    spec = importlib.util.spec_from_file_location('ai_report_generator', str(AI_DIR / 'report_generator.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    ReportGenerator = getattr(mod, 'ReportGenerator')

__all__ = ['ReportGenerator']
