"""Меню «⚙️ Обработать» → «VPN»: ссылка подписки — секрет, он не должен остаться нигде."""
import asyncio
import json
import logging
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram import Bot
from aiogram.methods import DeleteMessage, EditMessageText, SendMessage
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from d_brain.bot import vpn_menu
from d_brain.bot.request_jobs import RequestJobs

LINK = "https://sub.example.com/api/sub/SECRET-TOKEN-4f9a1c"
KEY = "vless://11111111-2222-3333-4444-555555555555@203.0.113.10:443?security=reality&pbk=SECRETKEY"


def detach_routers():
    """Роутеры проекта — модульные одиночки: перед новым диспетчером их нужно отвязать от старого."""
    import importlib
    import pkgutil

    from d_brain.bot import handlers

    for info in pkgutil.iter_modules(handlers.__path__):
        router = getattr(importlib.import_module(f"d_brain.bot.handlers.{info.name}"), "router", None)
        if router is not None:
            router._parent_router = None
    vpn_menu.router._parent_router = None


@pytest.fixture(autouse=True)
def fresh_routers():
    detach_routers()
    yield
    detach_routers()


@pytest.fixture(autouse=True)
def enabled(monkeypatch):
    monkeypatch.setenv("VPN_GUARD_ENABLED", "1")
    monkeypatch.setattr(vpn_menu, "get_settings", lambda: SimpleNamespace(admin_user_ids=[7]))
    vpn_menu.waiting.clear()
    yield
    vpn_menu.waiting.clear()


def user(number):
    return User(id=number, is_bot=False, first_name="Тест")


def message(text, number=1, who=7):
    return Message(message_id=number, date=datetime.now(timezone.utc), chat=Chat(id=who, type="private"),
                   from_user=user(who), text=text)


def stub(text, who=7, kind="private"):
    """Лёгкий объект вместо сообщения для проверки промежуточного слоя."""
    return SimpleNamespace(text=text, from_user=SimpleNamespace(id=who),
                           chat=SimpleNamespace(type=kind, id=who), message_id=5,
                           delete=AsyncMock(), answer=AsyncMock())


async def build(tmp_path, monkeypatch):
    """Настоящий диспетчер в том же порядке слоёв, что и в run_bot."""
    from d_brain.bot.main import create_auth_middleware, create_dispatcher
    from d_brain.config import Settings

    settings = Settings(telegram_bot_token="123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi", deepgram_api_key="test",
                        vault_path=tmp_path / "vault", allowed_user_ids=[7, 8], admin_user_ids=[7], ai_backend="codex")
    dp = create_dispatcher()
    dp.update.middleware(create_auth_middleware(settings))
    dp.update.middleware(vpn_menu.VpnLinkCapture())
    jobs = RequestJobs(settings)
    dp["request_jobs"] = jobs
    dp.update.middleware(jobs)
    bot = Bot(token=settings.telegram_bot_token)
    send = AsyncMock(return_value=True)
    monkeypatch.setattr(bot.session, "make_request", send)
    return dp, bot, jobs, send


def methods(send, kind):
    return [call.args[1] for call in send.call_args_list if isinstance(call.args[1], kind)]


async def test_link_flow_never_reaches_queue_files_or_log(tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    dp, bot, jobs, send = await build(tmp_path, monkeypatch)
    guard = AsyncMock(return_value={"ok": True, "message": "🔁 <b>Узел заменён.</b>"})
    monkeypatch.setattr(vpn_menu, "run_guard", guard)

    await dp.feed_update(bot, Update(update_id=1, message=message("⚙️ Обработать", 1)))
    await asyncio.gather(*list(jobs.tasks))  # обычное сообщение выполняется фоновой задачей слоя очереди
    assert "Что запустить" in methods(send, SendMessage)[-1].text

    prompt = message("Меню", 2, who=7)
    callback = lambda number, data: Update(update_id=number, callback_query=CallbackQuery(
        id=str(number), from_user=user(7), chat_instance="c", data=data, message=prompt))
    await dp.feed_update(bot, callback(2, "menu:vpn"))
    await dp.feed_update(bot, callback(3, "vpn:url"))
    assert 7 in vpn_menu.waiting

    await dp.feed_update(bot, Update(update_id=4, message=message(LINK, 9)))
    guard.assert_awaited_once()
    assert guard.await_args.args == ("set-url",) and guard.await_args.kwargs["stdin"] == LINK
    assert any(method.message_id == 9 for method in methods(send, DeleteMessage))
    assert methods(send, EditMessageText)[-1].text == "🔁 <b>Узел заменён.</b>"
    assert 7 not in vpn_menu.waiting

    # Ссылка не дошла ни до очереди, ни до журнала задач, ни до файлов хранилища, ни до лога.
    assert not jobs.active and jobs.inbox.pending() == []
    import sqlite3
    with sqlite3.connect(jobs.inbox.path) as db:
        assert db.execute("SELECT count(*) FROM inbox WHERE payload LIKE '%SECRET-TOKEN%'").fetchone()[0] == 0
    for path in (tmp_path).rglob("*"):
        if path.is_file():
            assert b"SECRET-TOKEN" not in path.read_bytes(), path
    assert "SECRET-TOKEN" not in caplog.text and "sub.example.com" not in caplog.text
    await bot.session.close()


async def test_secret_key_outside_menu_is_deleted_not_processed(tmp_path, monkeypatch):
    dp, bot, jobs, send = await build(tmp_path, monkeypatch)
    guard = AsyncMock()
    monkeypatch.setattr(vpn_menu, "run_guard", guard)
    await dp.feed_update(bot, Update(update_id=1, message=message(KEY, 3)))
    guard.assert_not_called()
    assert any(method.message_id == 3 for method in methods(send, DeleteMessage))
    assert "похоже на ключ VPN" in methods(send, SendMessage)[-1].text
    assert not jobs.active and jobs.inbox.pending() == []
    await bot.session.close()


async def test_plain_text_cancels_waiting_and_passes_through():
    vpn_menu.waiting[7] = (asyncio.get_event_loop().time() + 100, 7, 1)
    handler = AsyncMock(return_value="обработано")
    event = SimpleNamespace(message=stub("привет, как дела?"))
    result = await vpn_menu.VpnLinkCapture()(handler, event, {"bot": None})
    assert result == "обработано" and 7 not in vpn_menu.waiting
    event.message.delete.assert_not_called()


async def test_expired_wait_is_ignored_and_ordinary_link_passes(monkeypatch):
    monkeypatch.setattr(vpn_menu.time, "monotonic", lambda: 1000.0)
    vpn_menu.waiting[7] = (999.0, 7, 1)
    handler = AsyncMock(return_value="обработано")
    event = SimpleNamespace(message=stub("https://youtu.be/abc"))
    assert await vpn_menu.VpnLinkCapture()(handler, event, {"bot": None}) == "обработано"
    event.message.delete.assert_not_called()


async def test_non_admin_and_groups_are_untouched():
    handler = AsyncMock(return_value="дальше")
    for event in (SimpleNamespace(message=stub(KEY, who=8)),
                  SimpleNamespace(message=stub(KEY, kind="supergroup")),
                  SimpleNamespace(message=None)):
        assert await vpn_menu.VpnLinkCapture()(handler, event, {"bot": None}) == "дальше"
    assert handler.await_count == 3


async def test_menu_is_off_without_flag_and_for_non_admin(monkeypatch):
    assert vpn_menu.enabled_for(7) and not vpn_menu.enabled_for(8) and not vpn_menu.enabled_for(None)
    monkeypatch.delenv("VPN_GUARD_ENABLED")
    assert not vpn_menu.enabled_for(7)
    from d_brain.bot.main import create_dispatcher
    assert "vpn_menu" not in [router.name for router in create_dispatcher().sub_routers]


async def test_router_precedes_buttons_when_enabled():
    from d_brain.bot.main import create_dispatcher
    names = [router.name for router in create_dispatcher().sub_routers]
    assert names.index("vpn_menu") < names.index("buttons")


async def test_non_admin_callback_gets_alert(tmp_path, monkeypatch):
    dp, bot, jobs, send = await build(tmp_path, monkeypatch)
    guard = AsyncMock()
    monkeypatch.setattr(vpn_menu, "run_guard", guard)
    event = Update(update_id=1, callback_query=CallbackQuery(
        id="1", from_user=user(8), chat_instance="c", data="vpn:refresh", message=message("Меню", 2, who=8)))
    await dp.feed_update(bot, event)
    guard.assert_not_called()
    assert any(call.args[1].__class__.__name__ == "AnswerCallbackQuery" and call.args[1].show_alert
               for call in send.call_args_list)
    await bot.session.close()


async def test_process_button_runs_supervised_and_stop_cancels_it(tmp_path, monkeypatch):
    from d_brain.bot.handlers import process

    started = asyncio.Event()

    async def long_process(message):
        started.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(process, "cmd_process", long_process)
    settings = SimpleNamespace(vault_path=tmp_path / "vault", work_chat_ids=[], treat_all_group_chats_as_work=True)
    jobs = RequestJobs(settings)
    callback = SimpleNamespace(from_user=SimpleNamespace(id=7), answer=AsyncMock(),
                               message=SimpleNamespace(delete=AsyncMock()))
    await vpn_menu.menu_process(callback, request_jobs=jobs)
    await asyncio.wait_for(started.wait(), 1)
    ((execution, _),) = jobs.active.values()
    assert execution.data["scope"] == "7" and execution.data["state"] == "running"
    callback.message.delete.assert_awaited_once()

    stop = SimpleNamespace(text="Стоп", caption=None, message_id=2, date=datetime.now(timezone.utc),
                           chat=SimpleNamespace(id=7, type="private", title=None), from_user=SimpleNamespace(id=7),
                           voice=None, photo=None, document=None, video=None, video_note=None, answer=AsyncMock())
    await asyncio.wait_for(jobs(AsyncMock(), SimpleNamespace(message=stop), {}), 2)
    assert not jobs.active and execution.data["state"] == "stopped"
    assert "Остановил" in stop.answer.call_args.args[0]


async def test_process_button_finishes_and_clears_its_record(tmp_path, monkeypatch):
    from d_brain.bot.handlers import process

    done = AsyncMock()
    monkeypatch.setattr(process, "cmd_process", done)
    jobs = RequestJobs(SimpleNamespace(vault_path=tmp_path / "vault", work_chat_ids=[], treat_all_group_chats_as_work=True))
    callback = SimpleNamespace(from_user=SimpleNamespace(id=7), answer=AsyncMock(),
                               message=SimpleNamespace(delete=AsyncMock()))
    await vpn_menu.menu_process(callback, request_jobs=jobs)
    await asyncio.gather(*jobs.tasks)
    done.assert_awaited_once()
    assert not jobs.active
    states = [json.loads(path.read_text())["state"] for path in jobs.directory.glob("*.json")]
    assert states == ["completed"]


async def test_run_guard_sends_secret_only_through_stdin(monkeypatch):
    captured = {}

    class Process:
        async def communicate(self, data=None):
            captured["stdin"] = data
            return b'{"ok": true, "message": "ok"}\n', b""

    async def fake_exec(*args, **kwargs):
        captured["args"] = args
        return Process()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    assert (await vpn_menu.run_guard("set-url", stdin=LINK))["ok"]
    assert captured["stdin"] == LINK.encode()
    assert all("SECRET-TOKEN" not in str(part) for part in captured["args"])
    assert captured["args"][:3] == ("sudo", "-n", vpn_menu.GUARD)


async def test_run_guard_reports_garbage_and_timeout(monkeypatch):
    class Silent:
        async def communicate(self, data=None):
            return b"not json\n", b""

        def kill(self):
            pass

    async def fake_exec(*args, **kwargs):
        return Silent()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    assert "непонятно" in (await vpn_menu.run_guard("status"))["message"]

    class Slow(Silent):
        async def communicate(self, data=None):
            await asyncio.sleep(10)

    async def slow_exec(*args, **kwargs):
        return Slow()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", slow_exec)
    assert "дольше обычного" in (await vpn_menu.run_guard("status", timeout=0.05))["message"]


async def test_run_bot_wires_capture_between_auth_and_queue(tmp_path, monkeypatch):
    """Порядок слоёв определяет секретность: доступ → перехват ссылки → очередь/журнал."""
    from aiogram import Dispatcher

    from d_brain.bot import main as bot_main
    from d_brain.config import Settings

    seen = {}

    async def fake_polling(self, bot, **kwargs):
        seen["dp"] = self

    async def idle(*args, **kwargs):
        return None

    monkeypatch.setattr(Dispatcher, "start_polling", fake_polling)
    monkeypatch.setattr(bot_main, "_announce_pending_switches", idle)
    monkeypatch.setattr("d_brain.services.document_jobs.document_worker", idle)
    (tmp_path / "vault").mkdir()
    settings = Settings(_env_file=None, telegram_bot_token="123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi",
                        deepgram_api_key="test", vault_path=tmp_path / "vault", allowed_user_ids=[7],
                        admin_user_ids=[7], ai_backend="codex", temporary_chat_user_id=0)
    await bot_main.run_bot(settings)
    kinds = [getattr(item, "__name__", type(item).__name__)
             for item in seen["dp"].update.middleware._middlewares]
    assert kinds == ["auth_middleware", "VpnLinkCapture", "RequestJobs"], kinds
    assert isinstance(seen["dp"]["request_jobs"], RequestJobs)
