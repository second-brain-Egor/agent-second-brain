"""Очередь ответов чата: порядок прихода, свежая беседа, общий ответ на ждавшие сообщения.

Модель не вызывается: `_run_chat` подменён.
"""
import re
import threading
import time

import pytest

from d_brain.services import processor as module
from d_brain.services.chat_queue import ChatQueue, leave_turn, wait_turn
from d_brain.services.execution import Execution, ExecutionStopped, execution_context
from d_brain.services.session import SessionStore


class FakeExecution:
    def __init__(self):
        self.cancelled = threading.Event()
        self.data = {}

    def update(self, **values):
        self.data.update(values)

    def check(self):
        if self.cancelled.is_set():
            raise ExecutionStopped()


def spawn(function, *args):
    box = {}

    def target():
        try:
            box['value'] = function(*args)
        except BaseException as error:
            box['error'] = error

    box['thread'] = threading.Thread(target=target, daemon=True)
    box['thread'].start()
    return box


def blocked(box, seconds=0.3):
    box['thread'].join(seconds)
    return box['thread'].is_alive()


def result(box, seconds=5):
    box['thread'].join(seconds)
    assert not box['thread'].is_alive(), 'поток ожидания завис'
    if 'error' in box:
        raise box['error']
    return box['value']


def test_replies_keep_arrival_order_and_waiting_messages_share_one_reply():
    queue = ChatQueue()
    first, second, third = (queue.register(7, number) for number in (1, 2, 3))
    executions = [FakeExecution() for _ in range(3)]
    a = queue.acquire(first, 'A', executions[0])
    assert a.queued == () and a.answered is None
    # Третье дошло до модели раньше второго (долгое распознавание голоса), но ждёт второе.
    t3 = spawn(queue.acquire, third, 'C', executions[2])
    assert blocked(t3)
    t2 = spawn(queue.acquire, second, 'B', executions[1])
    assert blocked(t2)
    assert executions[1].data['waiting'] is True
    a.commit()
    queue.finish(7, 1)
    b = result(t2)
    assert [text for _, text in b.queued] == ['C']
    assert blocked(t3)  # «Ответил выше» уйдёт только после самого ответа
    b.commit()
    queue.finish(7, 2)
    c = result(t3)
    assert re.fullmatch(r'\d\d:\d\d', c.answered) and c.queued == ()
    queue.finish(7, 3)
    assert not queue.turns
    assert executions[1].data['waiting'] is False and executions[2].data['waiting'] is False


def test_message_still_busy_elsewhere_breaks_the_batch_and_cannot_be_skipped():
    queue = ChatQueue()
    first, busy, third = (queue.register(7, number) for number in (1, 2, 3))
    t3 = spawn(queue.acquire, third, 'C', FakeExecution())
    assert blocked(t3)
    a = queue.acquire(first, 'A', FakeExecution())
    assert a.queued == ()  # второе сообщение не готово: пачка обрывается, порядок не нарушен
    a.commit()
    queue.finish(7, 1)
    assert blocked(t3)  # третье ждёт второе
    queue.finish(7, 2)  # второе ушло в тяжёлую работу и очередь чата больше не держит
    c = result(t3)
    assert c.queued == () and c.answered is None


def test_failed_reply_returns_waiting_messages_to_the_queue():
    queue = ChatQueue()
    first, second = (queue.register(7, number) for number in (1, 2))
    t2 = spawn(queue.acquire, second, 'B', FakeExecution())
    assert blocked(t2)
    a = queue.acquire(first, 'A', FakeExecution())
    assert [text for _, text in a.queued] == ['B']
    with a:  # ответ не получился: commit не вызван
        pass
    queue.finish(7, 1)
    b = result(t2)
    assert b.answered is None and b.queued == ()  # второе отвечает само


def test_leader_finished_without_reply_uncovers_even_without_release():
    queue = ChatQueue()
    first, second = (queue.register(7, number) for number in (1, 2))
    t2 = spawn(queue.acquire, second, 'B', FakeExecution())
    assert blocked(t2)
    queue.acquire(first, 'A', FakeExecution())
    queue.finish(7, 1)  # обработчик оборвался: ни commit, ни release
    assert result(t2).answered is None


def test_stop_interrupts_waiting_and_does_not_block_later_messages():
    queue = ChatQueue()
    first, second, third = (queue.register(7, number) for number in (1, 2, 3))
    a = queue.acquire(first, 'A', FakeExecution())
    stopped = FakeExecution()
    t2 = spawn(queue.acquire, second, 'B', stopped)
    assert blocked(t2)
    stopped.cancelled.set()
    with pytest.raises(ExecutionStopped):
        result(t2)
    assert second.text is None and stopped.data['waiting'] is False
    queue.finish(7, 2)  # RequestJobs.finish_turn при остановке
    t3 = spawn(queue.acquire, third, 'C', FakeExecution())
    a.commit()
    queue.finish(7, 1)
    c = result(t3)
    assert c.queued == () and c.answered is None


def test_scopes_do_not_wait_for_each_other():
    queue = ChatQueue()
    mine, other = queue.register(7, 1), queue.register(8, 1)
    queue.acquire(mine, 'A', FakeExecution())
    assert queue.acquire(other, 'B', FakeExecution()).queued == ()


def test_finished_turns_leave_no_trace():
    queue = ChatQueue()
    queue.register(7, 1)
    queue.finish(7, 1)
    queue.finish(7, 1)
    queue.finish(9, 5)
    assert not queue.turns and queue.pending(7) == []


def test_wait_turn_without_queue_passes_at_once():
    with wait_turn('привет') as grant:
        assert grant.queued == () and grant.answered is None
        grant.commit()
    leave_turn()


def test_wait_turn_and_leave_turn_use_current_execution(tmp_path):
    queue = ChatQueue()
    execution = Execution(tmp_path, scope=7, origin='bot')
    execution.turn = queue.register(7, 1)
    with execution_context(execution):
        with wait_turn('привет') as grant:
            assert re.fullmatch(r'\d\d:\d\d', grant.stamp)
        assert queue.pending(7) == [1]
        leave_turn()
    assert not queue.turns


@pytest.fixture
def chat(tmp_path, monkeypatch):
    (tmp_path / 'vault').mkdir(exist_ok=True)
    processor = object.__new__(module.AgentProcessor)
    processor.vault_path = tmp_path / 'vault'
    processor.project_path = tmp_path
    monkeypatch.setattr(processor, '_get_memory_context', lambda **kwargs: 'память')
    monkeypatch.setattr('d_brain.services.memory_rag.search_memory', lambda query, limit=5: '')
    return processor


def handle(chat, tmp_path, queue, number, text):
    """Как обработчик сообщения: запись в беседу сразу, ответ по очереди, запись ответа, конец."""
    SessionStore(chat.vault_path).append(7, 'text', text=text, msg_id=number)
    execution = Execution(tmp_path, scope=7, origin='bot')
    execution.turn = queue.turn(number)
    try:
        with execution_context(execution):
            reply = chat.execute_raw_prompt(text, 7, session_scope=7)
            SessionStore(chat.vault_path).append(
                7, 'assistant', text=reply.get('report') or reply.get('error'))
            return reply
    finally:
        queue.finish(7, number)


class Line(ChatQueue):
    """Очередь, которая сама помнит места сообщений, как RequestJobs."""

    def arrive(self, number):
        self.places = getattr(self, 'places', {})
        self.places[number] = self.register(7, number)

    def turn(self, number):
        return self.places[number]


def waiting(queue, *numbers):
    end = time.monotonic() + 5
    while time.monotonic() < end:
        if all(queue.turns[str(7)][number].text for number in numbers):
            return
        time.sleep(0.01)
    raise AssertionError('сообщения не дошли до ожидания очереди')


def test_three_overlapping_messages_are_answered_in_order_on_fresh_conversation(chat, tmp_path, monkeypatch):
    calls, gate = [], threading.Event()

    def fake_chat(system, user, **kwargs):
        calls.append(user)
        if len(calls) == 1:
            assert gate.wait(5)
        return f'Ответ {len(calls)}'

    monkeypatch.setattr(chat, '_run_chat', fake_chat)
    queue = Line()
    queue.arrive(1)
    first = spawn(handle, chat, tmp_path, queue, 1, 'Проверяй')
    end = time.monotonic() + 5
    while not calls and time.monotonic() < end:
        time.sleep(0.01)
    assert calls, 'первый запрос к модели не начался'
    queue.arrive(2)
    second = spawn(handle, chat, tmp_path, queue, 2, 'Вопрос про Ирину')
    queue.arrive(3)
    third = spawn(handle, chat, tmp_path, queue, 3, 'Вопрос про Швецию')
    waiting(queue, 2, 3)
    assert len(calls) == 1 and blocked(second) and blocked(third)

    gate.set()
    assert result(first)['report'] == 'Ответ 1'
    assert result(second)['report'] == 'Ответ 2'
    one_line = result(third)['report']
    assert re.fullmatch(r'☝️ Ответил выше, в сообщении от \d\d:\d\d', one_line)

    assert len(calls) == 2  # на третье сообщение модель не вызывалась
    assert '=== USER MESSAGE ===\nПроверяй' in calls[0] and 'USER MESSAGES' not in calls[0]
    assert 'Ответ 1' in calls[1]  # беседа собрана уже после первого ответа
    block = calls[1].split('=== USER MESSAGES ===')[1]
    assert block.index('Вопрос про Ирину') < block.index('Вопрос про Швецию')
    assistant = [e['text'] for e in SessionStore(chat.vault_path).get_recent(7) if e['type'] == 'assistant']
    assert assistant == ['Ответ 1', 'Ответ 2', one_line]
    assert not queue.turns


def test_failed_batch_reply_is_not_reported_as_answered_above(chat, tmp_path, monkeypatch):
    calls, gate = [], threading.Event()

    def fake_chat(system, user, **kwargs):
        calls.append(user)
        if len(calls) == 1:
            assert gate.wait(5)
        if len(calls) == 2:
            raise RuntimeError('обрыв связи')
        return f'Ответ {len(calls)}'

    monkeypatch.setattr(chat, '_run_chat', fake_chat)
    queue = Line()
    queue.arrive(1)
    first = spawn(handle, chat, tmp_path, queue, 1, 'Проверяй')
    end = time.monotonic() + 5
    while not calls and time.monotonic() < end:
        time.sleep(0.01)
    queue.arrive(2)
    second = spawn(handle, chat, tmp_path, queue, 2, 'Второе')
    queue.arrive(3)
    third = spawn(handle, chat, tmp_path, queue, 3, 'Третье')
    waiting(queue, 2, 3)
    gate.set()
    result(first)
    assert 'error' in result(second)
    reply = result(third)
    assert reply['report'] == 'Ответ 3'  # не «Ответил выше»: у третьего свой ответ
    assert len(calls) == 3 and 'USER MESSAGES' not in calls[2]


def test_message_without_queue_keeps_working_as_before(chat, monkeypatch):
    monkeypatch.setattr(chat, '_run_chat', lambda system, user, **kwargs: 'Привет')
    assert chat.execute_raw_prompt('Привет', 7, session_scope=7)['report'] == 'Привет'


def incoming(text, number, **fields):
    import asyncio  # noqa: F401  (событийный цикл нужен только тестам ниже)
    from datetime import datetime, timezone
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    return SimpleNamespace(message=SimpleNamespace(
        text=text, caption=None, message_id=number, date=datetime.now(timezone.utc),
        chat=SimpleNamespace(id=7, type='private', title=None), from_user=SimpleNamespace(id=7),
        voice=None, photo=None, document=None, video=None, video_note=None,
        answer=AsyncMock(), **fields))


@pytest.fixture
def jobs(tmp_path):
    from types import SimpleNamespace
    from d_brain.bot.request_jobs import RequestJobs
    settings = SimpleNamespace(vault_path=tmp_path / 'vault', work_chat_ids=[],
                               treat_all_group_chats_as_work=True)
    return RequestJobs(settings)


def chat_handler(chat):
    import asyncio

    async def handler(event, data):
        message = event.message
        # Сообщение попадает в беседу сразу, как у настоящего обработчика.
        SessionStore(chat.vault_path).append(7, 'text', text=message.text, msg_id=message.message_id)
        reply = await asyncio.to_thread(chat.execute_raw_prompt, message.text, 7, session_scope=7)
        SessionStore(chat.vault_path).append(7, 'assistant', text=reply.get('report') or reply.get('error'))
        await message.answer(reply.get('report') or reply.get('error'))
    return handler


async def test_request_jobs_log_messages_at_once_and_reply_in_arrival_order(jobs, chat, monkeypatch):
    import asyncio
    calls, gate = [], threading.Event()

    def fake_chat(system, user, **kwargs):
        calls.append(user)
        if len(calls) == 1:
            assert gate.wait(5)
        return f'Ответ {len(calls)}'

    monkeypatch.setattr(chat, '_run_chat', fake_chat)
    handler = chat_handler(chat)
    messages = [incoming(text, number) for number, text in enumerate(['Проверяй', 'Второе', 'Третье'], 1)]
    await jobs(handler, messages[0], {})
    for _ in range(500):
        if calls:
            break
        await asyncio.sleep(0.01)
    assert calls
    await jobs(handler, messages[1], {})
    await jobs(handler, messages[2], {})
    for _ in range(500):
        if all(turn.text for turn in jobs.turns['7'].values() if turn.message_id > 1):
            break
        await asyncio.sleep(0.01)
    logged = [e['text'] for e in SessionStore(chat.vault_path).get_recent(7)]
    assert logged == ['Проверяй', 'Второе', 'Третье']  # записаны сразу, не дожидаясь очереди
    assert len(calls) == 1
    assert 'очереди: 2' in jobs.status(7)  # ждущие считаются очередью, а не работой
    gate.set()
    await asyncio.wait_for(asyncio.gather(*list(jobs.tasks)), 5)
    assert len(calls) == 2 and 'Ответ 1' in calls[1]
    assert messages[0].message.answer.call_args.args[0] == 'Ответ 1'
    assert messages[1].message.answer.call_args.args[0] == 'Ответ 2'
    assert messages[2].message.answer.call_args.args[0].startswith('☝️ Ответил выше, в сообщении от ')
    assert not jobs.turns and not jobs.active


async def test_stop_frees_the_chat_queue(jobs, chat, monkeypatch):
    import asyncio
    gate, started = threading.Event(), threading.Event()

    def fake_chat(system, user, **kwargs):
        started.set()
        gate.wait(5)
        return 'Ответ'

    monkeypatch.setattr(chat, '_run_chat', fake_chat)
    handler = chat_handler(chat)
    await jobs(handler, incoming('Долгое', 1), {})
    for _ in range(500):
        if started.is_set():
            break
        await asyncio.sleep(0.01)
    await jobs(handler, incoming('Второе', 2), {})
    waiting_execution = jobs.active['7:message:2'][0]
    for _ in range(500):
        if waiting_execution.data.get('waiting'):
            break
        await asyncio.sleep(0.01)
    assert waiting_execution.data['waiting'] is True
    await jobs(handler, incoming('стоп', 3), {})
    assert not jobs.turns and not jobs.active
    for _ in range(500):  # ждущий поток видит остановку при ближайшей проверке
        if waiting_execution.data.get('waiting') is False:
            break
        await asyncio.sleep(0.01)
    assert waiting_execution.data['waiting'] is False
    assert waiting_execution.data['state'] == 'stopped'
    gate.set()


async def test_attachment_does_not_take_a_place_in_the_chat_queue(jobs):
    import asyncio
    from types import SimpleNamespace
    gate = asyncio.Event()

    async def handler(event, data):
        await gate.wait()

    photo = incoming(None, 5)
    photo.message.caption = 'Что на фото?'
    photo.message.photo = [SimpleNamespace(file_id='p')]
    await jobs(handler, photo, {})
    assert not jobs.turns
    assert jobs.active['7:message:5'][0].turn is None
    await jobs(handler, incoming('Текст', 6), {})
    assert list(jobs.turns['7']) == [6]
    assert jobs.active['7:message:6'][0].turn is jobs.turns['7'][6]
    gate.set()
    await asyncio.wait_for(asyncio.gather(*list(jobs.tasks)), 2)
    assert not jobs.turns


async def test_failure_while_admitting_a_message_does_not_hold_the_line(jobs, monkeypatch):
    def broken(*args, **kwargs):
        raise OSError('диск недоступен')

    monkeypatch.setattr('d_brain.bot.request_jobs.Execution', broken)
    with pytest.raises(OSError):
        await jobs(lambda *args: None, incoming('Привет', 1), {})
    assert not jobs.turns


def test_redelivered_message_keeps_its_place_and_frees_the_old_one():
    queue = ChatQueue()
    old = queue.register(7, 1)
    queue.register(7, 2)
    new = queue.register(7, 1)
    assert list(queue.turns['7']) == [1, 2] and queue.turns['7'][1] is new
    assert old.finished
