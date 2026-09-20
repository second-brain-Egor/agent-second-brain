"""Bounded CLI execution and durable checkpoints, independent of model polling."""
from __future__ import annotations

import contextvars
import json
import os
import queue
import signal
import subprocess
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

CURRENT_EXECUTION = contextvars.ContextVar('dbrain_execution', default=None)
TERMINAL = {'completed', 'error', 'stopped', 'limit', 'interrupted', 'superseded', 'delegated'}


class ExecutionLimit(RuntimeError):
    """A job exhausted its locally enforced budget."""


class ExecutionStopped(BaseException):
    """Cancellation must escape legacy handlers' broad Exception catches."""


def positive_env(name: str, default: int) -> int:
    try:
        return max(1, int(os.environ.get(name, default)))
    except (TypeError, ValueError):
        return default


class Execution:
    def __init__(self, project: Path, *, scope='', request='', origin='cli',
                 seconds=None, max_calls=None, max_steps=None):
        self.id = uuid.uuid4().hex
        self.directory = Path(project) / 'vault' / '.session' / 'tasks'
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / f'{self.id}.json'
        self.seconds = seconds
        self.max_calls = max_calls
        self.max_steps = max_steps
        self.deadline = time.monotonic() + self.seconds if self.seconds is not None else float("inf")
        self.lock = threading.RLock()
        self.cancelled = threading.Event()
        self.idle = threading.Event()
        self.idle.set()
        self.process = None
        self.descendants = {}
        self.seen = set()
        self.wait_steps = 0
        self.data = dict(id=self.id, scope=str(scope), request=request, origin=origin,
                         state='queued', calls=0, steps=0, owner_pid=os.getpid(),
                         seconds=self.seconds, max_calls=self.max_calls,
                         max_steps=self.max_steps, started=self.now())
        self.update()

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    def update(self, **values):
        with self.lock:
            self.data.update(values, updated=self.now())
            temporary = self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2))
            temporary.chmod(0o600)
            temporary.replace(self.path)

    def check(self):
        if self.cancelled.is_set():
            raise ExecutionStopped()
        if time.monotonic() >= self.deadline:
            self.limit('Достигнут предел времени выполнения.')

    def limit(self, reason):
        self.update(state='limit', error=reason)
        raise ExecutionLimit(reason)

    def begin_call(self):
        with self.lock:
            self.check()
            if self.max_calls is not None and self.data['calls'] >= self.max_calls:
                self.limit('Достигнут предел запусков модели. Автоповтор отключён.')
            self.update(calls=self.data['calls'] + 1, state='running')

    def stop(self, state='stopped'):
        with self.lock:
            self.cancelled.set()
            self.update(state=state)
            self.signal(signal.SIGTERM)

    @staticmethod
    def process_info(pid):
        try:
            fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
            return int(fields[1]), fields[19]
        except (OSError, ValueError, IndexError):
            return None

    def signal(self, sig):
        if self.process is not None:
            # CLI tools can create their own process groups. Track descendants
            # before terminating the parent, and retain start times against PID reuse.
            table = {}
            for path in Path('/proc').glob('[0-9]*/stat'):
                pid = int(path.parent.name)
                info = self.process_info(pid)
                if info:
                    table[pid] = info
            parents = {self.process.pid}
            while parents:
                children = {pid for pid, (ppid, _) in table.items()
                            if ppid in parents and pid not in self.descendants}
                for pid in children:
                    self.descendants[pid] = table[pid][1]
                parents = children
            for pid, started in list(self.descendants.items()):
                info = self.process_info(pid)
                if info and info[1] == started:
                    try:
                        os.kill(pid, sig)
                    except ProcessLookupError:
                        pass
            try:
                os.killpg(self.process.pid, sig)
            except ProcessLookupError:
                pass

    def observe(self, line: str, backend: str):
        """Count observable steps; never present them as exact provider API usage."""
        try:
            event = json.loads(line)
        except (ValueError, TypeError):
            return
        if not isinstance(event, dict):
            return
        kind = event.get('type')
        if kind in {'turn.failed', 'error'}:
            raise RuntimeError('Исполнитель сообщил об ошибке. Автоповтор отключён.')
        if kind == 'turn.completed' and event.get('usage'):
            self.update(usage=event['usage'])
        item = event.get('item') or {}
        identity = None
        if backend == 'codex' and kind in {'item.started', 'item.completed'}:
            identity = item.get('id')
        elif backend == 'claude' and kind == 'assistant':
            identity = (event.get('message') or {}).get('id') or event.get('uuid')
        identity = (self.data['calls'], identity) if identity else None
        if identity and identity not in self.seen:
            self.seen.add(identity)
            steps = self.data['steps'] + 1
            self.update(steps=steps, last_event=kind,
                        last_step=item.get('type', kind))
            if self.max_steps is not None and steps > self.max_steps:
                self.limit('Достигнут предел шагов задачи.')
        if kind == 'thread.started' and event.get('thread_id'):
            self.update(thread_id=event['thread_id'])


@contextmanager
def execution_context(execution):
    token = CURRENT_EXECUTION.set(execution)
    try:
        yield execution
    finally:
        CURRENT_EXECUTION.reset(token)


def run_bounded(cmd, *, input, cwd, env, backend, timeout=None, project=None):
    """Drain pipes in threads; the watchdog uses no model calls and kills the group."""
    inherited = CURRENT_EXECUTION.get()
    execution = inherited or Execution(Path(project or cwd), request=input, seconds=timeout)
    call_deadline = execution.deadline
    if timeout is not None:
        call_deadline = min(call_deadline, time.monotonic() + timeout)
    if backend == "command":
        execution.check()
    else:
        execution.begin_call()
    events = queue.Queue()
    stdout, stderr = [], []
    process = None

    def drain(pipe, stream):
        try:
            for line in pipe:
                events.put((stream, line))
        finally:
            pipe.close()
            events.put((stream, None))

    try:
        with execution.lock:
            execution.check()
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True, cwd=cwd, env=env,
                                       start_new_session=True, bufsize=1)
            execution.process = process
            execution.descendants = {}
            execution.idle.clear()
            execution.update(pid=process.pid, state='running')
        readers = [threading.Thread(target=drain, args=(pipe, name), daemon=True)
                   for pipe, name in [(process.stdout, 'stdout'), (process.stderr, 'stderr')]]
        for reader in readers:
            reader.start()

        def write_input():
            try:
                process.stdin.write(input)
                process.stdin.close()
            except (BrokenPipeError, OSError):
                pass
        threading.Thread(target=write_input, daemon=True).start()
        closed = set()
        journal = execution.directory / f'{execution.id}.jsonl'
        with journal.open('a', encoding='utf-8') as log:
            journal.chmod(0o600)
            while len(closed) < 2 or process.poll() is None:
                execution.check()
                if time.monotonic() >= call_deadline:
                    execution.limit("Достигнут предел времени выполнения команды.")
                try:
                    stream, line = events.get(timeout=0.1)
                except queue.Empty:
                    continue
                if line is None:
                    closed.add(stream)
                    continue
                (stdout if stream == 'stdout' else stderr).append(line)
                if stream == 'stdout':
                    log.write(line)
                    log.flush()
                    if backend != "command":
                        execution.observe(line, backend)
        process.wait()
        execution.check()
        if inherited is None:
            execution.update(state='completed' if process.returncode == 0 else 'error')
        return subprocess.CompletedProcess(cmd, process.returncode, ''.join(stdout), ''.join(stderr))
    except ExecutionLimit:
        raise
    except ExecutionStopped:
        raise
    except BaseException:
        if execution.data['state'] not in TERMINAL:
            execution.update(state='error')
        raise
    finally:
        if process is not None:
            # Terminate descendants too, including shells left behind by the CLI.
            execution.signal(signal.SIGTERM)
            try:
                process.wait(timeout=0.3)
            except subprocess.TimeoutExpired:
                pass
            execution.signal(signal.SIGKILL)
            process.wait()
            with execution.lock:
                execution.process = None
                execution.idle.set()


def final_text(output: str, backend: str) -> str:
    """Extract user output from structured streams, never return raw tool logs."""
    answer = ''
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if backend == 'claude' and event.get('type') == 'result':
            if event.get('is_error'):
                raise RuntimeError('Claude завершил запрос с ошибкой или ограничением.')
            answer = event.get('result') or ''
        item = event.get('item') or {}
        if backend == 'codex' and event.get('type') == 'item.completed' and item.get('type') == 'agent_message':
            answer = item.get('text') or answer
    return answer
