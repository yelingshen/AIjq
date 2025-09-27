"""Proxy for ai/structure_visualizer.py

Expose the StructureVisualizer class from ai/structure_visualizer.py so
other modules can `from utils.structure_visualizer import StructureVisualizer`.
"""
from pathlib import Path
import importlib.util
import sys

AI_DIR = Path(__file__).resolve().parents[1] / 'ai'
sys.path.insert(0, str(AI_DIR))

try:
    from structure_visualizer import StructureVisualizer  # type: ignore
except Exception:
    spec = importlib.util.spec_from_file_location('ai_structure_visualizer', str(AI_DIR / 'structure_visualizer.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    StructureVisualizer = getattr(mod, 'StructureVisualizer')

__all__ = ['StructureVisualizer']
