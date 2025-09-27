"""Adapter for Ollama local models.

This adapter tries to use the `ollama` Python package if available. If not,
it falls back to invoking the `ollama` CLI via subprocess (requires ollama
installed on the host). The adapter implements `load` (a lightweight no-op
that returns model identifier) and `infer` which sends prompts and returns
text output.
"""
from typing import Dict, Any
import shutil
import subprocess
import json
import logging

LOG = logging.getLogger(__name__)

class Adapter:
    name = 'ollama'

    def __init__(self):
        # prefer python client if available
        try:
            import ollama as _ollama
            self._client = _ollama
            self._use_cli = False
        except Exception:
            self._client = None
            self._use_cli = shutil.which('ollama') is not None

    def load(self, model_path: str, **kwargs) -> Dict[str, Any]:
        # For Ollama the "model_path" will be treated as model name or tag
        if not model_path:
            raise RuntimeError('No model name supplied for Ollama adapter')
        return {'model_name': model_path}

    def infer(self, model, prompt: str, **kwargs) -> Dict[str, Any]:
        model_name = model.get('model_name') if isinstance(model, dict) else model
    if self._client:
            # hypothetical python client usage
            try:
                # many Ollama clients expose a `completion` or `chat` method
                out = self._client.chat(model_name, prompt)
                return {'text': str(out)}
            except Exception as e:
                LOG.exception('Ollama python client failed')
                raise RuntimeError(f'Ollama python client failed: {e}')
        if self._use_cli:
            try:
                # Use `ollama run MODEL PROMPT --format json`
                # Try passing prompt as argument
                cmd = ['ollama', 'run', model_name, prompt, '--format', 'json']
                LOG.debug('Running Ollama CLI: %s', ' '.join(cmd))
                p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, stdin=subprocess.DEVNULL)
                out = p.stdout.decode('utf-8').strip()
                try:
                    data = json.loads(out) if out else None
                    if data:
                        return {'text': data.get('output') or data.get('result') or str(data)}
                except Exception:
                    pass
                # Do not rely on stdin in server contexts (can cause bad file descriptor).
                # If first attempt didn't yield parseable JSON, return raw stdout so caller
                # gets something to display and can decide further action.
                if p.returncode != 0:
                    err = p.stderr.decode('utf-8')
                    LOG.warning('Ollama CLI exited with code %s: %s', p.returncode, err)
                    return {'text': err}
                LOG.debug('Ollama CLI output: %s', out)
                return {'text': out}
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f'Ollama CLI failed: {e.stderr.decode("utf-8") if e.stderr else str(e)}')
        raise RuntimeError('No Ollama client or CLI available on this host')
