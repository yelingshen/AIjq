"""Minimal and robust Ollama adapter.

This adapter prefers the python `ollama` client when available and falls
back to invoking the `ollama` CLI. It returns a standardized schema:
    {'text': '<string>', 'meta': { ... }}
"""
from typing import Dict, Any, Optional
import shutil
import subprocess
import json
import logging
import concurrent.futures
import time
import asyncio

LOG = logging.getLogger(__name__)
if not LOG.handlers:
    handler = logging.StreamHandler()
    fmt = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    handler.setFormatter(logging.Formatter(fmt))
    LOG.addHandler(handler)
LOG.setLevel(logging.INFO)


def _run_with_timeout(fn, timeout: float):
    """Run function with timeout using ThreadPoolExecutor and return (result, error, took_seconds)."""
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(fn)
        try:
            res = fut.result(timeout=timeout)
            return res, None, time.time() - start
        except concurrent.futures.TimeoutError:
            fut.cancel()
            return None, f'timeout after {timeout}s', time.time() - start
        except Exception as e:
            return None, str(e), time.time() - start


class Adapter:
    name = 'ollama'

    def __init__(self, timeout: float = 20.0):
        """timeout: seconds to wait for a model response before aborting"""
        self.timeout = float(timeout)
        try:
            import ollama as _ollama
            self._client = _ollama
            LOG.debug('Ollama python client available')
        except Exception:
            self._client = None
            LOG.debug('Ollama python client not available')
        # detect CLI presence
        self._cli_path = shutil.which('ollama') or '/usr/local/bin/ollama'
        if self._cli_path:
            LOG.debug('Ollama CLI found at %s', self._cli_path)

    def load(self, model_path: str, **kwargs) -> Dict[str, Any]:
        if not model_path:
            raise RuntimeError('No model name supplied for Ollama adapter')
        return {'model_name': model_path}

    def _infer_via_client(self, model_name: str, prompt: str) -> Dict[str, Any]:
        # return {'text': str(...), 'meta': {...}}
        if not hasattr(self, '_client') or self._client is None:
            raise RuntimeError('Python Ollama client not available')
        messages = [{"role": "user", "content": prompt}]
        if hasattr(self._client, 'chat'):
            out = self._client.chat(model=model_name, messages=messages)
            return {'text': str(out), 'meta': {'backend': 'ollama_python'}}
        if hasattr(self._client, 'run'):
            out = self._client.run(model_name, prompt)
            return {'text': str(out), 'meta': {'backend': 'ollama_python'}}
        raise RuntimeError('Unsupported python ollama client API')

    def _infer_via_cli(self, model_name: str, prompt: str) -> Dict[str, Any]:
        if not self._cli_path:
            raise RuntimeError('Ollama CLI not available')
        cmd = [self._cli_path, 'run', model_name, prompt, '--format', 'json']
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, stdin=subprocess.DEVNULL)
        out = p.stdout.decode('utf-8').strip()
        err = p.stderr.decode('utf-8').strip()
        if p.returncode != 0:
            # prefer stderr for error details
            raise RuntimeError(f'Ollama CLI failed (rc={p.returncode}): {err or out}')

        # Prefer parsing stdout JSON if present
        if out:
            try:
                data = json.loads(out)
                # common keys used by different ollama versions
                text = None
                if isinstance(data, dict):
                    text = data.get('output') or data.get('result') or data.get('text')
                if text is None:
                    # empty JSON object (e.g. {}), try fallback to plain text CLI
                    if isinstance(data, dict) and len(data) == 0:
                        # run CLI without --format to get plain textual output
                        fb = subprocess.run([self._cli_path, 'run', model_name, prompt], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, stdin=subprocess.DEVNULL)
                        fb_out = fb.stdout.decode('utf-8').strip()
                        if fb_out:
                            return {'text': fb_out, 'meta': {'backend': 'ollama_cli', 'raw_stdout_fallback': fb_out}}
                    text = str(data)
                return {'text': text, 'meta': {'backend': 'ollama_cli', 'raw_json': data}}
            except Exception:
                # stdout not JSON, return as-is
                return {'text': out, 'meta': {'backend': 'ollama_cli', 'raw_stdout': out}}

        # If stdout empty, but stderr contains useful output, return that
        if err:
            try:
                data = json.loads(err)
                text = data.get('output') or data.get('result') or data.get('text') or str(data)
                return {'text': text, 'meta': {'backend': 'ollama_cli', 'raw_json_err': data}}
            except Exception:
                return {'text': err, 'meta': {'backend': 'ollama_cli', 'raw_stderr': err}}

        # Nothing returned by CLI but succeeded: return empty text with meta
        return {'text': '', 'meta': {'backend': 'ollama_cli', 'note': 'empty_output'}}

    def infer(self, model, prompt: str, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        model_name = model.get('model_name') if isinstance(model, dict) else model
        timeout = float(timeout) if timeout is not None else self.timeout

        def try_client():
            return self._infer_via_client(model_name, prompt)

        def try_cli():
            return self._infer_via_cli(model_name, prompt)

        # Prefer python client but fall back to CLI; each call is wrapped with timeout
        if self._client is not None:
            res, err, took = _run_with_timeout(try_client, timeout)
            if err:
                LOG.warning('Ollama python client failed or timed out (%s), took %.2fs; falling back to CLI; err=%s', model_name, took, err)
            else:
                LOG.info('Ollama python client success for %s (%.2fs)', model_name, took)
                return res

        # Try CLI fallback
        res, err, took = _run_with_timeout(try_cli, timeout)
        if err:
            LOG.error('Ollama CLI failed or timed out for %s (%.2fs): %s', model_name, took, err)
            raise RuntimeError(f'Ollama inference failed: {err}')
        LOG.info('Ollama CLI success for %s (%.2fs)', model_name, took)
        return res

    async def ainfer(self, model, prompt: str, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        """Async inference entry. Prefer async client APIs when available. Falls back to running sync infer in a thread."""
        model_name = model.get('model_name') if isinstance(model, dict) else model
        timeout = float(timeout) if timeout is not None else self.timeout

        # If python client provides an async chat, use it
        if self._client is not None and hasattr(self._client, 'chat'):
            try:
                maybe_coro = self._client.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
                if asyncio.iscoroutine(maybe_coro):
                    res = await asyncio.wait_for(maybe_coro, timeout=timeout)
                else:
                    # sync return, keep backwards compat
                    res = maybe_coro
                return {'text': str(res), 'meta': {'backend': 'ollama_python_async'}}
            except asyncio.TimeoutError:
                raise RuntimeError(f'ollama python async chat timeout after {timeout}s')
            except Exception as e:
                LOG.warning('async python client failed: %s', e)

        # Fall back to running sync infer in executor
        loop = asyncio.get_event_loop()
        try:
            res = await asyncio.wait_for(loop.run_in_executor(None, lambda: self.infer(model_name, prompt, timeout=timeout, **kwargs)), timeout=timeout)
            return res
        except asyncio.TimeoutError:
            raise RuntimeError(f'ollama inference timed out after {timeout}s')

