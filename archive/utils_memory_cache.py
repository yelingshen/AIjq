"""Proxy for ai/memory_cache.py

This proxy tries to import the real `ai.memory_cache` module and forwards
the MemoryCache symbol (if present). This keeps the proxy importable without
executing heavy initialization.
"""
from importlib import import_module
try:
    _mod = import_module('ai.memory_cache')
except Exception:
    _mod = None

if _mod and hasattr(_mod, 'MemoryCache'):
    MemoryCache = getattr(_mod, 'MemoryCache')
else:
    # fallback: simple in-memory placeholder implementation used only for import-time
    class MemoryCache:
        def __init__(self, *args, **kwargs):
            self._store = {}
        def get(self, k, default=None):
            return self._store.get(k, default)
        def set(self, k, v):
            self._store[k] = v
        def clear(self):
            self._store.clear()

def load_module():
    """Compatibility loader that executes the original ai/memory_cache.py if needed."""
    if _mod:
        return _mod
    # last resort: run the source to produce the module dict
    import runpy, sys
    from pathlib import Path
    AI_DIR = Path(__file__).resolve().parents[1] / 'ai'
    sys.path.insert(0, str(AI_DIR))
    return runpy.run_path(str(AI_DIR / 'memory_cache.py'))
