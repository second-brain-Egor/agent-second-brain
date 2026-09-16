"""Regression coverage for unlimited requests in both bot installations."""

import contextlib
import subprocess
import sys
from unittest.mock import Mock

import pytest

from d_brain.services import document_extract
from d_brain.services import processor as module


@pytest.fixture
def processor(tmp_path, monkeypatch):
    cli = tmp_path / "fake-model"
    cli.write_text(
        f"#!{sys.executable}\n"
        "import sys, time\n"
        "sys.stdin.read()\n"
        "time.sleep(0.03)\n"
        "print('Готово')\n"
    )
    cli.chmod(0o755)
    instance = object.__new__(module.AgentProcessor)
    instance.project_path = tmp_path
    instance.vault_path = tmp_path
    instance.codex_model = instance.claude_model = "test-model"
    instance.codex_sandbox_mode = "read-only"
    instance.claude_effort = "medium"
    monkeypatch.setattr(instance, "_get_codex_bin", lambda: str(cli))
    monkeypatch.setattr(instance, "_get_claude_bin", lambda: str(cli))
    monkeypatch.setattr(instance, "_backend_model_for_mode", lambda mode: "test-model")
    builder = "_build_exec_prompt" if hasattr(instance, "_build_exec_prompt") else "_build_codex_prompt"
    monkeypatch.setattr(instance, builder, lambda *args, **kwargs: "Проверка")
    monkeypatch.setattr(module, "_claude_chat_lock", contextlib.nullcontext)
    monkeypatch.setattr(module, "_claude_heavy_lock", contextlib.nullcontext)
    return instance


@pytest.mark.parametrize("backend", ["codex", "claude"])
@pytest.mark.parametrize("route", ["chat", "agent", "vision"])
def test_request_waits_for_cli_without_deadline(processor, monkeypatch, tmp_path, backend, route):
    processor.ai_backend = backend
    run = Mock(wraps=subprocess.run)
    monkeypatch.setattr(module.subprocess, "run", run)
    if route == "chat":
        method = getattr(processor, "_run_chat", None) or processor._run_openai_text
        answer = method("system", "request")
    elif route == "agent":
        method = getattr(processor, "_run_agent", None) or processor._run_openai_agent
        answer = method("system", "request")
    else:
        method = getattr(processor, "_analyze_image_cli", None) or processor._analyze_image_codex_cli
        answer = method(tmp_path / "photo.png", "Опиши")
    assert answer == "Готово"
    assert run.call_count == 1
    assert run.call_args.kwargs["timeout"] is None


def test_chat_retry_keeps_unlimited_wait(processor, monkeypatch):
    if not hasattr(processor, "_run_chat"):
        pytest.skip("This installation does not retry chat requests")
    run = Mock(side_effect=[RuntimeError("connection interrupted"), "Готово"])
    monkeypatch.setattr(processor, "_run_backend_exec", run)
    assert processor._run_chat("system", "request") == "Готово"
    assert run.call_count == 2
    assert all(call.kwargs["timeout_sec"] is None for call in run.call_args_list)


def test_document_reader_has_no_implicit_deadline(monkeypatch):
    # A default read must not construct or consult an elapsed-time budget.
    monkeypatch.setattr(document_extract.time, "monotonic", Mock(side_effect=AssertionError("deadline checked")))
    assert document_extract.run([sys.executable, "-c", "print('Прочитано')"]).strip() == "Прочитано"


def test_explicit_document_deadline_still_works(monkeypatch):
    monkeypatch.setattr(document_extract.time, "monotonic", lambda: 100)
    with pytest.raises(TimeoutError):
        document_extract.run([sys.executable, "-c", "print('unexpected')"], deadline=99)
