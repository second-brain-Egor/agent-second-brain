"""Task controls stay responsive while an earlier request runs."""
import asyncio
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram import Bot
from aiogram.types import Update, Message, Chat, User

from d_brain.bot.request_jobs import RequestJobs
from d_brain.services.execution import CURRENT_EXECUTION, Execution


def message(text, number=1, user=7, **kwargs):
    return SimpleNamespace(text=text, caption=None, message_id=number,
        date=datetime.now(timezone.utc), chat=SimpleNamespace(id=user,type='private',title=None),
        from_user=SimpleNamespace(id=user), voice=None, photo=None, document=None,
        video=None, video_note=None, answer=AsyncMock(), **kwargs)


@pytest.fixture
def jobs(tmp_path):
    settings=SimpleNamespace(vault_path=tmp_path/'vault',work_chat_ids=[],treat_all_group_chats_as_work=True)
    return RequestJobs(settings)


async def test_stop_bypasses_blocked_handler(jobs):
    started=asyncio.Event()
    async def handler(event,data):
        started.set()
        await asyncio.Event().wait()
    first=message('Выполни задачу')
    await jobs(handler,SimpleNamespace(message=first),{})
    await asyncio.wait_for(started.wait(),1)
    execution=jobs.active['7:message:1'][0]
    stop=message('Стоп!',2)
    await asyncio.wait_for(jobs(handler,SimpleNamespace(message=stop),{}),1)
    assert not jobs.active
    assert execution.data['state']=='stopped'
    assert stop.answer.await_count==1
    assert 'Остановил' in stop.answer.call_args.args[0]
    assert not first.answer.called


async def test_followups_and_new_requests_keep_running_job(jobs):
    started = asyncio.Event()
    release = asyncio.Event()
    handled = []
    async def handler(event, data):
        handled.append(event.message.text)
        if event.message.message_id == 1:
            started.set()
            await release.wait()
        await event.message.answer('Готово')
    first = message('Долгое поручение')
    await jobs(handler, SimpleNamespace(message=first), {})
    await asyncio.wait_for(started.wait(), 1)
    old = jobs.active['7:message:1'][0]
    for number, text in enumerate(['Дополнение: оставь только Binance', 'Ещё сохрани журнал', 'Найди другое видео'], 2):
        await jobs(handler, SimpleNamespace(message=message(text, number)), {})
    assert old.data['state'] == 'running'
    assert len(jobs.active) == 4
    assert handled == ['Долгое поручение']
    assert 'в очереди: 3' in jobs.status(7)
    release.set()
    await asyncio.wait_for(asyncio.gather(*list(jobs.tasks)), 1)
    assert old.data['state'] == 'completed'
    assert len(handled) == 4
    assert handled[1:] == ['Дополнение: оставь только Binance', 'Ещё сохрани журнал', 'Найди другое видео']
    assert first.answer.await_count == 1
    assert not jobs.turns


async def test_status_does_not_call_model_or_interrupt(jobs):
    gate=asyncio.Event()
    handler=AsyncMock(side_effect=lambda *a: None)
    async def work(*args):
        await gate.wait()
    await jobs(work,SimpleNamespace(message=message('Делай')), {})
    task=jobs.active['7:message:1'][1]
    status=message('/tasks',2)
    await jobs(handler,SimpleNamespace(message=status),{})
    assert not handler.called and not task.cancelled()
    assert 'очереди' in status.answer.call_args.args[0]
    gate.set()
    await asyncio.gather(*list(jobs.tasks))


async def test_user_isolation(jobs):
    async def work(*args):
        await asyncio.Event().wait()
    await jobs(work,SimpleNamespace(message=message('Делай',user=7)),{})
    await jobs(work,SimpleNamespace(message=message('Делай',user=8)),{})
    await jobs(work,SimpleNamespace(message=message('/stop',2,user=7)),{})
    assert {e.data['scope'] for e, _ in jobs.active.values()} == {'8'}
    await jobs.close()


async def test_restart_marks_unfinished_without_relaunch(jobs):
    execution=Execution(jobs.settings.vault_path.parent,scope=7,origin='bot')
    execution.update(state='running')
    restored=RequestJobs(jobs.settings)
    assert json.loads(execution.path.read_text())['state']=='interrupted'
    assert not restored.active


async def test_context_reaches_worker_thread(jobs):
    captured=[]
    async def handler(*args):
        captured.append(await asyncio.to_thread(CURRENT_EXECUTION.get))
    await jobs(handler,SimpleNamespace(message=message('Выполни')), {})
    await asyncio.gather(*list(jobs.tasks))
    assert captured[0] is not None
    assert captured[0].data['state']=='completed'


async def test_voice_stop_transcribed_once(jobs,monkeypatch):
    async def handler(*args):
        await asyncio.Event().wait()
    transcribe=AsyncMock(return_value='Стоп.')
    monkeypatch.setattr('d_brain.bot.handlers.voice._transcribe_voice',transcribe)
    await jobs(handler,SimpleNamespace(message=message('Делай')), {})
    speech=message(None,2)
    speech.voice=SimpleNamespace(file_id='voice')
    await jobs(handler,SimpleNamespace(message=speech), {'bot':object()})
    assert transcribe.await_count==1
    assert not jobs.active
    assert 'Остановил' in speech.answer.call_args.args[0]


async def test_dispatcher_auth_still_precedes_stop(tmp_path,monkeypatch):
    from d_brain.bot.main import create_auth_middleware, create_dispatcher
    from d_brain.config import Settings
    settings=Settings(telegram_bot_token='123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi',
                      deepgram_api_key='test',vault_path=tmp_path/'vault',allowed_user_ids=[7])
    dp=create_dispatcher()
    jobs=RequestJobs(settings)
    dp.update.middleware(create_auth_middleware(settings))
    dp.update.middleware(jobs)
    bot=Bot(token=settings.telegram_bot_token)
    send=AsyncMock()
    monkeypatch.setattr(bot.session,'make_request',send)
    event=Update(update_id=10,message=Message(message_id=1,date=datetime.now(timezone.utc),
                 chat=Chat(id=8,type='private'),from_user=User(id=8,is_bot=False,first_name='Test'),text='/stop'))
    await dp.feed_update(bot,event)
    assert not send.called
    event=Update(update_id=11,message=Message(message_id=2,date=datetime.now(timezone.utc),
                 chat=Chat(id=7,type='private'),from_user=User(id=7,is_bot=False,first_name='Test'),text='/stop'))
    await dp.feed_update(bot,event)
    assert send.await_count==1
    assert 'Активной задачи' in send.call_args.args[1].text
    # The conversation button must beat /do's catch-all state handler.
    from d_brain.bot.handlers import buttons
    from d_brain.bot.keyboards import CHAT_BUTTON
    from d_brain.bot.states import DoCommandState
    from unittest.mock import Mock
    settings.admin_user_ids = [7]
    monkeypatch.setattr(buttons, 'get_settings', lambda: settings)
    save = Mock()
    monkeypatch.setattr(buttons, '_replace_env_value', save)
    monkeypatch.setenv('CODEX_REASONING_EFFORT', 'xhigh')
    state = dp.fsm.get_context(bot=bot, chat_id=7, user_id=7)
    await state.set_state(DoCommandState.waiting_for_input)
    event = Update(update_id=12, message=event.message.model_copy(
        update={'message_id': 3, 'text': CHAT_BUTTON}))
    await dp.feed_update(bot, event)
    save.assert_called_once_with('CODEX_REASONING_EFFORT', 'medium')
    assert await state.get_state() is None
    assert not jobs.active  # Switching itself needs no background/model job.
    assert 'средний уровень' in send.call_args.args[1].text
    await bot.session.close()


async def test_deadline_stops_job_without_model_retry(jobs,monkeypatch):
    monkeypatch.setenv('TASK_TIMEOUT_SECONDS','1')
    async def wait(*args):
        await asyncio.Event().wait()
    msg=message('Долгая задача')
    await jobs(wait,SimpleNamespace(message=msg),{})
    execution=jobs.active['7:message:1'][0]
    await asyncio.wait_for(asyncio.gather(*list(jobs.tasks)),2)
    assert execution.data['state']=='limit'
    assert 'Достигнут предел' in msg.answer.call_args.args[0]
    assert execution.data['calls']==0


async def test_stop_cancels_queued_document_before_model_start(jobs):
    # Use the production ingest path tested by the document pipeline.
    import importlib.util
    from pathlib import Path
    spec=importlib.util.spec_from_file_location('document_test_helpers',Path(__file__).with_name('test_document_pipeline.py'))
    helpers=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    store,doc,job=helpers.ready_job(jobs.settings.vault_path)
    msg=message('/stop',2)
    await jobs(AsyncMock(),SimpleNamespace(message=msg),{})
    assert store.job(job['id'])['state']=='stopped'
    assert 'Остановил' in msg.answer.call_args.args[0]


async def test_background_notice_respects_no_notifications(jobs,monkeypatch):
    monkeypatch.setenv('TASK_BACKGROUND_NOTICE_SECONDS','1')
    async def work(*args):
        await asyncio.sleep(1.05)
    msg=message('Выполни без уведомлений')
    await jobs(work,SimpleNamespace(message=msg),{})
    await asyncio.gather(*list(jobs.tasks))
    assert not msg.answer.called


async def test_short_link_request_has_smaller_budget(jobs):
    async def work(*args):
        await asyncio.Event().wait()
    await jobs(work,SimpleNamespace(message=message('Дай просто ссылку на папку и всё')), {})
    execution=jobs.active['7:message:1'][0]
    assert execution.seconds==90 and execution.max_steps==8
    await jobs.close()


async def test_natural_stop_does_not_launch_another_model(jobs):
    async def work(*args):
        await asyncio.Event().wait()
    await jobs(work,SimpleNamespace(message=message('Делай')), {})
    handler=AsyncMock()
    await jobs(handler,SimpleNamespace(message=message('Стоп, не продолжай.',2)), {})
    assert not handler.called and not jobs.active


async def test_stop_cancels_running_and_all_queued_messages(jobs):
    started = asyncio.Event()
    handled = []
    async def work(event, data):
        handled.append(event.message.message_id)
        started.set()
        await asyncio.Event().wait()
    for number in range(1, 4):
        await jobs(work, SimpleNamespace(message=message('Делай', number)), {})
    await started.wait()
    executions = [execution for execution, _ in jobs.active.values()]
    await jobs(AsyncMock(), SimpleNamespace(message=message('отмени', 4)), {})
    assert handled == [1]
    assert not jobs.active
    assert all(execution.data['state'] == 'stopped' for execution in executions)
    # The explicit stop does not prevent a subsequent new request.
    handler = AsyncMock()
    await jobs(handler, SimpleNamespace(message=message('Новое поручение', 5)), {})
    await asyncio.gather(*list(jobs.tasks))
    assert handler.await_count == 1


async def test_slow_voice_and_later_text_are_both_processed_in_order(jobs, monkeypatch):
    entered = asyncio.Event()
    release = asyncio.Event()
    async def transcribe(*args):
        entered.set()
        await release.wait()
        return 'Первое поручение'
    monkeypatch.setattr('d_brain.bot.handlers.voice._transcribe_voice', transcribe)
    speech = message(None)
    speech.voice = SimpleNamespace(file_id='voice')
    handled = []
    async def handler(event, data):
        handled.append(data.get('transcript') or event.message.text)
    first = asyncio.create_task(jobs(handler, SimpleNamespace(message=speech), {'bot': object()}))
    await entered.wait()
    await jobs(handler, SimpleNamespace(message=message('Уточнение', 2)), {})
    await jobs(AsyncMock(), SimpleNamespace(message=message('/tasks', 3)), {})
    release.set()
    await first
    await asyncio.wait_for(asyncio.gather(*list(jobs.tasks)), 1)
    assert handled == ['Первое поручение', 'Уточнение']


async def test_stop_during_transcription_prevents_old_voice_start(jobs, monkeypatch):
    entered = asyncio.Event()
    release = asyncio.Event()
    async def transcribe(*args):
        entered.set()
        await release.wait()
        return 'Старое поручение'
    monkeypatch.setattr('d_brain.bot.handlers.voice._transcribe_voice', transcribe)
    speech = message(None)
    speech.voice = SimpleNamespace(file_id='voice')
    handler = AsyncMock()
    pending = asyncio.create_task(jobs(handler, SimpleNamespace(message=speech), {'bot': object()}))
    await entered.wait()
    await jobs(handler, SimpleNamespace(message=message('стоп', 2)), {})
    release.set()
    await pending
    assert not handler.called and not jobs.active and not jobs.turns


async def test_queue_wait_does_not_spend_execution_time(jobs, monkeypatch):
    monkeypatch.setenv('TASK_TIMEOUT_SECONDS', '1')
    release = asyncio.Event()
    async def first(*args):
        await release.wait()
    await jobs(first, SimpleNamespace(message=message('Первое')), {})
    second = AsyncMock()
    await jobs(second, SimpleNamespace(message=message('Следующее', 2)), {})
    execution = jobs.active['7:message:2'][0]
    # Simulate an elapsed queue wait; the budget starts when the handler starts.
    execution.deadline = 0
    release.set()
    await asyncio.wait_for(asyncio.gather(*list(jobs.tasks)), 1)
    assert second.await_count == 1
    assert execution.data['state'] == 'completed'


def durable_update(text, number, **fields):
    return Update(update_id=number, message=Message(
        message_id=number, date=datetime.now(timezone.utc),
        chat=Chat(id=7, type='private'), from_user=User(id=7, is_bot=False, first_name='Test'),
        text=text, **fields))


async def test_restart_restores_only_waiting_updates_in_order(jobs):
    started = asyncio.Event()
    async def blocked(event, data):
        started.set()
        await asyncio.Event().wait()
    await jobs(blocked, durable_update('Первое', 1), {})
    await started.wait()
    await jobs(blocked, durable_update('Второе', 2), {})
    await jobs(blocked, durable_update('Третье', 3), {})
    await jobs.close()
    recovered = RequestJobs(jobs.settings)
    received = []
    async def handler(event, data):
        received.append(event.message.text)
    async def feed(bot, event, **kwargs):
        await recovered(handler, event, kwargs)
    await recovered.restore(SimpleNamespace(feed_update=feed), object())
    await asyncio.gather(*list(recovered.tasks))
    assert received == ['Второе', 'Третье']
    # Re-delivery and a second restart cannot duplicate completed work.
    await recovered(handler, durable_update('Второе', 2), {})
    assert not RequestJobs(jobs.settings).inbox.pending()
    assert received == ['Второе', 'Третье']


async def test_stop_does_not_restore_waiting_updates(jobs):
    started = asyncio.Event()
    async def blocked(event, data):
        started.set()
        await asyncio.Event().wait()
    await jobs(blocked, durable_update('Первое', 1), {})
    await started.wait()
    await jobs(blocked, durable_update('Второе', 2), {})
    await jobs.stop_scope(7)
    await jobs.close()
    assert not RequestJobs(jobs.settings).inbox.pending()


async def test_crash_recovery_keeps_payload_and_transcript(jobs):
    update = durable_update(None, 9, voice={'file_id': 'voice', 'file_unique_id': 'unique', 'duration': 3})
    key = '7:message:9'
    jobs.inbox.accept(key, 7, update.model_dump_json())
    jobs.inbox.set(key, 'queued', 'Сохрани уточнение')
    jobs.inbox.accept('7:message:10', 7, durable_update('Начатое', 10).model_dump_json())
    jobs.inbox.set('7:message:10', 'running')
    recovered = RequestJobs(jobs.settings)
    feed = AsyncMock()
    await recovered.restore(SimpleNamespace(feed_update=feed), object())
    assert feed.await_count == 1
    assert feed.call_args.kwargs['transcript'] == 'Сохрани уточнение'
    assert feed.call_args.args[1].message.voice.file_id == 'voice'
