"""Adapter for pygpt4all backend (optional).

This adapter tries to import pygpt4all at runtime. If the package isn't
installed, the adapter will raise an informative error when used.
"""
from typing import Any, Dict

class Adapter:
    def __init__(self):
        try:
            import pygpt4all
            self.pg = pygpt4all
        except Exception as e:
            raise RuntimeError('pygpt4all is not installed or failed to import') from e

    def load(self, model_path: str, **kwargs) -> Dict[str, Any]:
        # This is intentionally simple; real code should handle model config
        model = self.pg.GPT(model=model_path)
        return {'_internal': model}

    def infer(self, model, prompt: str, **kwargs) -> Dict[str, Any]:
        g = model.get('_internal') if isinstance(model, dict) else model
        # pygpt4all generate may vary by version; try common call
        try:
            out = g.generate(prompt)
            return {'text': out}
        except Exception:
            try:
                out = g.create(prompt)
                return {'text': out}
            except Exception as e:
                raise
