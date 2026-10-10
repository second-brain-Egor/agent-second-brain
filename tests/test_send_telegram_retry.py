import importlib.util
import io
import json
import urllib.error
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'send_telegram_message.py'
spec = importlib.util.spec_from_file_location('send_telegram_message', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fake_urlopen(failures):
    calls = []

    def urlopen(request, timeout):
        calls.append(request)
        if len(calls) <= failures:
            raise urllib.error.URLError(TimeoutError('The handshake operation timed out'))
        return io.BytesIO(json.dumps({'ok': True}).encode())
    return urlopen, calls


def test_send_retries_network_failures(monkeypatch):
    urlopen, calls = fake_urlopen(failures=2)
    monkeypatch.setattr(module.urllib.request, 'urlopen', urlopen)
    monkeypatch.setattr(module.time, 'sleep', lambda _: None)
    assert module.send('token', '1', 'привет') == 1
    assert len(calls) == 3


def test_send_gives_up_after_three_attempts(monkeypatch):
    urlopen, calls = fake_urlopen(failures=5)
    monkeypatch.setattr(module.urllib.request, 'urlopen', urlopen)
    monkeypatch.setattr(module.time, 'sleep', lambda _: None)
    with pytest.raises(urllib.error.URLError):
        module.send('token', '1', 'привет')
    assert len(calls) == 3
