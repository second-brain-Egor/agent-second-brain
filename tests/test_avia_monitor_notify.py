"""Проверки квитанций без сетевых запросов и настоящих отправок."""

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.methods import SendMessage

SPEC = importlib.util.spec_from_file_location(
    "avia_monitor_notify", Path(__file__).parents[1] / "scripts" / "avia_monitor_notify.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    settings = SimpleNamespace(
        allowed_user_ids=[module.EGOR_CHAT_ID], telegram_bot_token="unused-secret",
        vault_path=vault,
    )
    monkeypatch.setattr(module, "get_settings", lambda: settings)
    message = SimpleNamespace(
        message_id=812, chat=SimpleNamespace(id=module.EGOR_CHAT_ID),
        date=datetime(2026, 10, 30, 10, 0, tzinfo=timezone.utc),
    )
    bot = SimpleNamespace(send_message=AsyncMock(return_value=message),
                          session=SimpleNamespace(close=AsyncMock()))
    monkeypatch.setattr(module, "Bot", lambda token: bot)
    return SimpleNamespace(
        bot=bot, settings=settings, state_path=tmp_path / "notice.json",
        history_path=vault / ".sessions" / f"{module.EGOR_CHAT_ID}.jsonl",
        monkeypatch=monkeypatch,
    )


def test_success_records_confirmed_full_history_and_sent_deduplicates(setup):
    def assert_saved_before_api(**kwargs):
        assert json.loads(setup.state_path.read_text())["state"] == "sending"
        assert not setup.history_path.exists()
        return setup.bot.send_message.return_value

    setup.bot.send_message.side_effect = assert_saved_before_api
    receipt = module.notify("✈️ Появились билеты\n\nРейс и цена.", state_path=setup.state_path)
    again = module.notify("✈️ Появились билеты\n\nРейс и цена.", state_path=setup.state_path)
    assert receipt == again
    assert receipt["message_id"] == 812
    setup.bot.send_message.assert_awaited_once()
    assert setup.bot.send_message.call_args.kwargs["request_timeout"] == 20
    history = [json.loads(line) for line in setup.history_path.read_text().splitlines()]
    assert len(history) == 1
    assert history[0] == {
        "ts": "2026-10-30T13:00:00+03:00", "type": "assistant",
        "text": "✈️ Появились билеты\n\nРейс и цена.", "msg_id": 812,
        "chat_id": module.EGOR_CHAT_ID, "chat_title": None,
        "automatic": True, "source": "avia-monitor",
    }
    state = json.loads(setup.state_path.read_text())
    assert state["state"] == "sent"
    assert state["history_saved"] is True


@pytest.mark.parametrize("state", ["sending", "send_unknown"])
def test_uncertain_existing_delivery_is_never_repeated(setup, state):
    setup.state_path.write_text(json.dumps({
        "state": state, "text": "Билеты", "chat_id": module.EGOR_CHAT_ID,
    }))
    with pytest.raises(RuntimeError, match="Результат прежней отправки неизвестен"):
        module.notify("Билеты", state_path=setup.state_path)
    setup.bot.send_message.assert_not_awaited()
    assert not setup.history_path.exists()


def test_network_error_becomes_unknown_without_history_or_retry(setup):
    setup.bot.send_message.side_effect = TelegramNetworkError(
        method=SendMessage(chat_id=module.EGOR_CHAT_ID, text="Билеты"),
        message="raw-secret must never appear",
    )
    with pytest.raises(RuntimeError) as caught:
        module.notify("Билеты", state_path=setup.state_path)
    assert "raw-secret" not in str(caught.value)
    assert json.loads(setup.state_path.read_text())["state"] == "send_unknown"
    with pytest.raises(RuntimeError):
        module.notify("Билеты", state_path=setup.state_path)
    setup.bot.send_message.assert_awaited_once()
    assert not setup.history_path.exists()


def test_explicit_rejection_is_stored_and_not_retried(setup):
    setup.bot.send_message.side_effect = TelegramBadRequest(
        method=SendMessage(chat_id=module.EGOR_CHAT_ID, text="Билеты"), message="raw-secret",
    )
    with pytest.raises(RuntimeError, match="Telegram отклонил"):
        module.notify("Билеты", state_path=setup.state_path)
    state = json.loads(setup.state_path.read_text())
    assert state["state"] == "rejected"
    assert "raw-secret" not in setup.state_path.read_text()
    with pytest.raises(RuntimeError, match="Telegram отклонил"):
        module.notify("Билеты", state_path=setup.state_path)
    setup.bot.send_message.assert_awaited_once()


def test_history_failure_preserves_receipt_and_next_call_repairs_without_resending(setup):
    original = module.SessionStore.append

    def append_failed(*args, **kwargs):
        raise OSError("disk")

    setup.monkeypatch.setattr(module.SessionStore, "append", append_failed)
    with pytest.raises(RuntimeError, match="Уведомление отправлено"):
        module.notify("Билеты", state_path=setup.state_path)
    assert json.loads(setup.state_path.read_text())["receipt"]["message_id"] == 812
    setup.monkeypatch.setattr(module.SessionStore, "append", original)
    module.notify("Билеты", state_path=setup.state_path)
    setup.bot.send_message.assert_awaited_once()
    assert len(setup.history_path.read_text().splitlines()) == 1


def test_crash_after_history_append_is_recovered_without_duplicate_history(setup):
    module.notify("Билеты", state_path=setup.state_path)
    state = json.loads(setup.state_path.read_text())
    state["history_saved"] = False
    setup.state_path.write_text(json.dumps(state))
    module.notify("Билеты", state_path=setup.state_path)
    setup.bot.send_message.assert_awaited_once()
    assert len(setup.history_path.read_text().splitlines()) == 1
    assert json.loads(setup.state_path.read_text())["history_saved"] is True


def test_other_bot_or_chat_cannot_send(setup):
    setup.settings.allowed_user_ids = [123]
    with pytest.raises(RuntimeError, match="не разрешает"):
        module.notify("Билеты", state_path=setup.state_path)
    with pytest.raises(RuntimeError, match="только Егору"):
        module.notify("Билеты", state_path=setup.state_path, chat_id=123)
    setup.bot.send_message.assert_not_awaited()
    assert not setup.state_path.exists()


def test_search_button_is_saved_sent_once_and_included_in_dedup_identity(setup):
    url = "https://www.bgoperator.ru/price.shtml?action=biletnew&params=021112026_SSH_MOW"
    module.notify("Билеты", state_path=setup.state_path, url=url)
    markup = setup.bot.send_message.call_args.kwargs["reply_markup"]
    assert len(markup.inline_keyboard) == 1
    assert len(markup.inline_keyboard[0]) == 1
    assert markup.inline_keyboard[0][0].text == "Открыть предложения"
    assert markup.inline_keyboard[0][0].url == url
    assert json.loads(setup.state_path.read_text())["url"] == url
    module.notify("Билеты", state_path=setup.state_path, url=url)
    with pytest.raises(RuntimeError, match="другому уведомлению"):
        module.notify("Билеты", state_path=setup.state_path)
    setup.bot.send_message.assert_awaited_once()


@pytest.mark.parametrize("url", [
    "https://www.bgoperator.ru/price.shtml?action=biletnewsorder",
    "https://www.bgoperator.ru/price.shtml?action=biletnew&action=biletnewsorder",
    "https://example.com/price.shtml?action=biletnew",
    "http://www.bgoperator.ru/price.shtml?action=biletnew",
    "https://www.bgoperator.ru/other?action=biletnew",
])
def test_order_links_and_other_urls_are_rejected_without_sending(setup, url):
    with pytest.raises(RuntimeError, match="только на поиск"):
        module.notify("Билеты", state_path=setup.state_path, url=url)
    setup.bot.send_message.assert_not_awaited()
    assert not setup.state_path.exists()
