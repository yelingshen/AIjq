"""ModelLoader with light-weight Adapter pattern for model backends.

This implementation is conservative: it does not import heavy backends at
module import time. Instead it provides a registry and tries to load backend
adapters lazily when `load_model` is called. This keeps `import ai.model_loader`
cheap for CI and static checks while allowing runtime inference when backends
are installed.
"""
from pathlib import Path
import json
import importlib
import logging
from typing import Optional, Dict, Any, List

LOG = logging.getLogger(__name__)

SUPPORTED_FORMATS = {
    '.gguf': 'llm', '.bin': 'llm', '.pt': 'llm/cv', '.pth': 'llm/cv',
    '.onnx': 'onnx', '.pb': 'pb', '.h5': 'h5', '.tflite': 'tflite'
}


class BackendAdapterBase:
    """Base class for model backend adapters."""
    name = 'base'

    def load(self, model_path: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()

    def infer(self, model, prompt: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()


class ModelLoader:
    def __init__(self, model_dirs: Optional[List[Path]] = None):
        self.DEFAULT_DIRS = model_dirs or [Path.cwd(), Path.home() / 'models']
        self.adapters = {}  # name -> adapter class
        self._register_builtin_adapters()

    def _register_builtin_adapters(self):
        # Register lightweight adapters that attempt lazy imports
        self.adapters['pygpt4all'] = self._try_import_adapter('pygpt4all_adapter', 'pygpt4all')
        self.adapters['ollama'] = self._try_import_adapter('ollama_adapter', 'ollama')
        self.adapters['torch'] = self._try_import_adapter('torch_adapter', 'torch')
        self.adapters['onnxruntime'] = self._try_import_adapter('onnx_adapter', 'onnxruntime')

    def _try_import_adapter(self, adapter_module_name: str, import_name: str):
        """Try to import an adapter module (application-specific). If not found,
        keep a placeholder that raises at runtime in load()."""
        try:
            mod = importlib.import_module(f'ai.adapters.{adapter_module_name}')
            return getattr(mod, 'Adapter')
        except Exception:
            # fallback to a small proxy that raises when used
            class MissingAdapter(BackendAdapterBase):
                name = import_name

                def load(self, model_path: str, **kwargs):
                    raise RuntimeError(f"Adapter for {import_name} not installed or adapter module missing")

                def infer(self, model, prompt: str, **kwargs):
                    raise RuntimeError(f"Adapter for {import_name} not installed or adapter module missing")

            return MissingAdapter

    def find_all_models(self) -> List[Dict[str, Any]]:
        found = []
        for d in self.DEFAULT_DIRS:
            try:
                p = Path(d)
                if not p.exists():
                    continue
                for ext in SUPPORTED_FORMATS.keys():
                    for f in p.rglob(f'*{ext}'):
                        try:
                            found.append({
                                'path': str(f),
                                'name': f.stem,
                                'type': SUPPORTED_FORMATS.get(ext, 'unknown'),
                                'size': f.stat().st_size,
                                'mtime': f.stat().st_mtime,
                            })
                        except Exception:
                            found.append({'path': str(f), 'name': f.stem, 'type': SUPPORTED_FORMATS.get(ext, 'unknown')})
            except Exception:
                continue
        return found

    def _select_backend_for_path(self, model_path: str) -> str:
        for ext, kind in SUPPORTED_FORMATS.items():
            if model_path.endswith(ext):
                # map extension to preferred backend heuristics
                if kind == 'llm':
                    return 'pygpt4all'
                if kind == 'onnx':
                    return 'onnxruntime'
                if kind in ('pb', 'h5', 'tflite'):
                    return 'torch'
        return 'pygpt4all'

    def load_model(self, model_path: Optional[str] = None, backend: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Attempt to load a model using an adapter. Returns dict with keys: model, backend, meta, error"""
        models = self.find_all_models()
        chosen = model_path or (models[0]['path'] if models else None)
        if not chosen:
            return {'model': None, 'backend': None, 'error': 'no_model_found', 'path': None}

        selected_backend = backend or self._select_backend_for_path(chosen)
        adapter_cls = self.adapters.get(selected_backend)
        try:
            adapter = adapter_cls()
            model_obj = adapter.load(chosen, **kwargs)
            return {'model': model_obj, 'backend': selected_backend, 'error': None, 'path': chosen}
        except Exception as e:
            LOG.exception('Model load failed')
            return {'model': None, 'backend': selected_backend, 'error': str(e), 'path': chosen}

    def self_check(self) -> Dict[str, Any]:
        return {
            'model_dirs': [str(p) for p in self.DEFAULT_DIRS],
            'supported_formats': list(SUPPORTED_FORMATS.keys()),
            'models_found': len(self.find_all_models()),
        }

    def auto_infer_and_check(self, model_path: Optional[str] = None, prompt: str = 'hello') -> Dict[str, Any]:
        res = self.load_model(model_path)
        if res.get('error'):
            return {'success': False, 'error': res.get('error')}
        try:
            # attempt a simple infer via adapter
            selected_backend = res.get('backend')
            adapter_cls = self.adapters.get(selected_backend)
            adapter = adapter_cls()
            out = adapter.infer(res['model'], prompt)
            return {'success': True, 'output': out}
        except Exception as e:
            return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    ml = ModelLoader()
    print('ModelLoader - models found:', len(ml.find_all_models()))
    print('Self check:', ml.self_check())

