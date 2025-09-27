import json
import subprocess
import types
import pytest

from ai.adapters.ollama_adapter import Adapter


class DummyClient:
    def __init__(self, response):
        self._response = response

    def chat(self, model, messages=None):
        return self._response


def test_client_success(monkeypatch):
    # Mock python client present and returns a simple string
    dummy = DummyClient("hello from client")
    monkeypatch.setitem(__import__('sys').modules, 'ollama', types.SimpleNamespace(chat=dummy.chat))

    adapter = Adapter(timeout=5.0)
    res = adapter.infer('some-model', 'prompt text')
    assert isinstance(res, dict)
    assert 'text' in res


def test_client_failure_then_cli(monkeypatch, tmp_path):
    # Simulate python client missing or failing, and CLI returning JSON
    monkeypatch.setitem(__import__('sys').modules, 'ollama', None)

    fake_output = json.dumps({'output': 'cli-response'})

    class FakeProc:
        def __init__(self):
            self.returncode = 0
            self.stdout = fake_output.encode()
            self.stderr = b''

    def fake_run(cmd, stdout, stderr, check, stdin):
        return FakeProc()

    monkeypatch.setattr(subprocess, 'run', fake_run)

    adapter = Adapter(timeout=5.0)
    res = adapter.infer('some-model', 'prompt')
    assert isinstance(res, dict)
    assert res['text'] == 'cli-response' or 'cli-response' in res['text']


def test_timeout_raises(monkeypatch):
    # Make _infer_via_client block by replacing the client with a function that sleeps
    def slow_chat(model, messages=None):
        import time
        time.sleep(2)
        return 'slow'

    monkeypatch.setitem(__import__('sys').modules, 'ollama', types.SimpleNamespace(chat=slow_chat))
    adapter = Adapter(timeout=0.5)
    with pytest.raises(RuntimeError):
        adapter.infer('m', 'p')
