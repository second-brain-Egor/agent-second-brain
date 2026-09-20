"""Regression coverage: real child processes, no paid model invocations."""
import contextlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest

from d_brain.services import document_extract
from d_brain.services import processor as module
from d_brain.services.execution import (
    Execution, ExecutionLimit, ExecutionStopped, execution_context, run_bounded,
)


@pytest.fixture
def processor(tmp_path, monkeypatch):
    cli = tmp_path / 'fake-model'
    cli.write_text(
        f'#!{sys.executable}\n'
        'import sys, json\nsys.stdin.read()\n'
        'if "--json" in sys.argv:\n'
        ' print(json.dumps({"type":"item.completed","item":{"id":"last","type":"agent_message","text":"Готово"}}))\n'
        'else:\n'
        ' print(json.dumps({"type":"result","result":"Готово"}))\n'
    )
    cli.chmod(0o755)
    instance = object.__new__(module.AgentProcessor)
    instance.project_path = tmp_path
    instance.vault_path = tmp_path / 'vault'
    instance.codex_model = instance.claude_model = 'test-model'
    instance.codex_sandbox_mode = 'read-only'
    instance.codex_reasoning_effort = ''
    instance.claude_effort = 'medium'
    monkeypatch.setattr(instance, '_get_codex_bin', lambda: str(cli))
    monkeypatch.setattr(instance, '_get_claude_bin', lambda: str(cli))
    monkeypatch.setattr(instance, '_backend_model_for_mode', lambda mode: 'test-model')
    monkeypatch.setattr(instance, '_build_exec_prompt', lambda *args, **kwargs: 'Проверка')
    monkeypatch.setattr(module, '_claude_heavy_lock', contextlib.nullcontext)
    return instance


@pytest.mark.parametrize('backend', ['codex', 'claude'])
@pytest.mark.parametrize('route', ['chat', 'agent', 'vision'])
def test_routes_use_bounded_structured_cli(processor, tmp_path, backend, route):
    processor.ai_backend = backend
    if route == 'chat':
        answer = processor._run_chat('system', 'request')
    elif route == 'agent':
        answer = processor._run_agent('system', 'request')
    else:
        answer = processor._analyze_image_cli(tmp_path / 'photo.png', 'Опиши')
    assert answer == 'Готово'
    states = [json.loads(p.read_text()) for p in (tmp_path/'vault/.session/tasks').glob('*.json')]
    assert len(states) == 1
    assert states[0]['calls'] == 1 and states[0]['state'] == 'completed'
    assert states[0]['seconds'] == 600


def test_chat_error_is_not_retried(processor, monkeypatch):
    run = Mock(side_effect=RuntimeError('connection interrupted'))
    monkeypatch.setattr(processor, '_run_backend_exec', run)
    with pytest.raises(RuntimeError):
        processor._run_chat('system', 'request')
    assert run.call_count == 1


def test_timeout_kills_child_group_and_keeps_checkpoint(tmp_path):
    child_file = tmp_path/'child.pid'
    code = ('import subprocess,sys,time,signal; '
            'signal.signal(signal.SIGTERM,signal.SIG_IGN); '
            'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"],start_new_session=True); '
            f'open({str(child_file)!r},"w").write(str(p.pid)); '
            'print("checkpoint",flush=True); time.sleep(60)')
    execution = Execution(tmp_path, seconds=0.5)
    started = time.monotonic()
    with execution_context(execution), pytest.raises(ExecutionLimit):
        run_bounded([sys.executable,'-c',code], input='', cwd=tmp_path, env=os.environ.copy(), backend='codex')
    assert time.monotonic()-started < 3
    assert json.loads(execution.path.read_text())['state'] == 'limit'
    assert 'checkpoint' in execution.path.with_suffix('.jsonl').read_text()
    pid = int(child_file.read_text())
    proc_stat = __import__('pathlib').Path(f'/proc/{pid}/stat')
    until = time.monotonic() + 1
    while proc_stat.exists() and proc_stat.read_text().split()[2] != 'Z' and time.monotonic() < until:
        time.sleep(.01)
    assert not proc_stat.exists() or proc_stat.read_text().split()[2] == 'Z'


def test_stop_cancels_real_cli(tmp_path):
    execution = Execution(tmp_path)
    def run():
        with execution_context(execution):
            return run_bounded([sys.executable,'-c','import time; time.sleep(60)'],
                               input='', cwd=tmp_path, env=os.environ.copy(), backend='codex')
    with ThreadPoolExecutor() as pool:
        future = pool.submit(run)
        until = time.monotonic()+2
        while execution.process is None and time.monotonic()<until:
            time.sleep(.01)
        execution.stop()
        with pytest.raises(ExecutionStopped):
            future.result(timeout=2)
    assert execution.idle.is_set()
    assert json.loads(execution.path.read_text())['state'] == 'stopped'


def test_step_budget_and_duplicate_events(tmp_path):
    execution = Execution(tmp_path, max_steps=2)
    event = lambda i: json.dumps(dict(type='item.started', item=dict(id=str(i),type='command_execution')))
    execution.observe(event(1),'codex')
    execution.observe(event(1),'codex')
    execution.observe(event(2),'codex')
    with pytest.raises(ExecutionLimit):
        execution.observe(event(3),'codex')
    assert execution.data['steps']==3


def test_repeated_model_waits_are_stopped(tmp_path):
    execution = Execution(tmp_path)
    for i in range(2):
        execution.observe(json.dumps(dict(type='item.started',item=dict(id=str(i),tool='wait'))),'codex')
    with pytest.raises(ExecutionLimit, match='ожидания'):
        execution.observe(json.dumps(dict(type='item.started',item=dict(id='3',tool='wait'))),'codex')


def test_launch_budget_prevents_retry(tmp_path):
    execution = Execution(tmp_path)
    execution.begin_call()
    with pytest.raises(ExecutionLimit):
        execution.begin_call()
    assert execution.data['calls']==1


def test_document_reader_has_no_implicit_deadline(monkeypatch):
    monkeypatch.setattr(document_extract.time, 'monotonic', Mock(side_effect=AssertionError('deadline checked')))
    assert document_extract.run([sys.executable, '-c', 'print("Прочитано")']).strip() == 'Прочитано'


def test_explicit_document_deadline_still_works(monkeypatch):
    monkeypatch.setattr(document_extract.time, 'monotonic', lambda: 100)
    with pytest.raises(TimeoutError):
        document_extract.run([sys.executable, '-c', 'print("unexpected")'], deadline=99)
