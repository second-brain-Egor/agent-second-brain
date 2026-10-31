"""Однократные уведомления мониторинга с квитанцией и историей беседы."""

from __future__ import annotations

import asyncio
import fcntl
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramConflictError,
    TelegramForbiddenError,
    TelegramMigrateToChat,
    TelegramNotFound,
    TelegramRetryAfter,
    TelegramUnauthorizedError,
)
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from d_brain.config import get_settings
from d_brain.services.session import SessionStore

EGOR_CHAT_ID = 6144231826
SOURCE = "avia-monitor"
MOSCOW = ZoneInfo("Europe/Moscow")
REJECTIONS = (
    TelegramBadRequest,
    TelegramConflictError,
    TelegramForbiddenError,
    TelegramMigrateToChat,
    TelegramNotFound,
    TelegramRetryAfter,
    TelegramUnauthorizedError,
)


def _now() -> str:
    return datetime.now(MOSCOW).isoformat()


def _save(path: Path, data: dict) -> None:
    """Сначала fsync временного файла, затем атомарная замена и fsync каталога."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        directory = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def _locked(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(str(path) + ".lock", os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def _validate_url(url: str | None) -> None:
    if url is None:
        return
    try:
        parsed = urlsplit(url)
        valid = (
            isinstance(url, str) and len(url) <= 2048
            and not any(character.isspace() for character in url)
            and parsed.scheme == "https" and parsed.netloc == "www.bgoperator.ru"
            and parsed.path == "/price.shtml" and not parsed.fragment
            and parse_qs(parsed.query).get("action") == ["biletnew"]
        )
    except (TypeError, ValueError, AttributeError):
        valid = False
    if not valid:
        raise RuntimeError("Кнопка может вести только на поиск билетов Библио-Глобуса.")


async def _send_once(token: str, chat_id: int, text: str, url: str | None):
    bot = Bot(token)
    markup = None
    if url is not None:
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Открыть предложения", url=url),
        ]])
    try:
        return await bot.send_message(
            chat_id=chat_id, text=text, parse_mode=None, request_timeout=20,
            reply_markup=markup,
        )
    finally:
        try:
            await bot.session.close()
        except Exception:
            # Ошибка закрытия соединения не отменяет полученную квитанцию.
            pass


def _record_history(settings, state_path: Path, state: dict) -> None:
    if state.get("history_saved"):
        return
    receipt = state["receipt"]
    try:
        store = SessionStore(settings.vault_path)
        already_saved = any(
            entry.get("msg_id") == receipt["message_id"]
            and entry.get("chat_id") == receipt["chat_id"]
            and entry.get("source") == SOURCE
            for entry in store.get_recent(receipt["chat_id"], limit=1000)
        )
        if not already_saved:
            store.append(
                receipt["chat_id"], "assistant", ts=receipt["sent_at"],
                text=state["text"], msg_id=receipt["message_id"],
                chat_id=receipt["chat_id"], chat_title=None,
                automatic=True, source=SOURCE,
            )
        # Квитанция об истории должна пережить перезапуск вместе с самой записью.
        with store._get_session_file(receipt["chat_id"]).open("rb") as history:
            os.fsync(history.fileno())
        directory = os.open(store.sessions_dir, os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        state["history_saved"] = True
        state.pop("history_error", None)
        _save(state_path, state)
    except Exception:
        state["history_saved"] = False
        state["history_error"] = "Не удалось подтвердить запись в историю."
        try:
            _save(state_path, state)
        except OSError:
            pass
        raise RuntimeError(
            "Уведомление отправлено, но запись в историю не подтверждена. "
            "Повторной отправки не будет."
        ) from None


def notify(
    text: str, *, state_path: Path, chat_id: int = EGOR_CHAT_ID,
    url: str | None = None,
) -> dict:
    """Отправить одно событие один раз; один state_path принадлежит одному тексту.

    Незавершённая или неоднозначная отправка требует проверки человеком.
    Подтверждённая квитанция сохраняется до истории: при сбое её записи
    следующий вызов допишет историю, но не отправит сообщение повторно.
    """
    if chat_id != EGOR_CHAT_ID:
        raise RuntimeError("Уведомления этого мониторинга предназначены только Егору.")
    if not isinstance(text, str) or not text.strip() or len(text) > 4000:
        raise RuntimeError("Текст уведомления должен содержать от 1 до 4000 символов.")
    _validate_url(url)
    state_path = Path(state_path)
    try:
        settings = get_settings()
    except Exception:
        raise RuntimeError("Не удалось прочитать настройки уведомлений.") from None
    if chat_id not in settings.allowed_user_ids:
        raise RuntimeError("Этот экземпляр помощника не разрешает уведомления Егору.")

    with _locked(state_path):
        state = None
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                raise RuntimeError(
                    "Не удалось прочитать квитанцию. Повторная отправка остановлена."
                ) from None
            if not isinstance(state, dict) or state.get("text") != text \
                    or state.get("chat_id") != chat_id or state.get("url") != url:
                raise RuntimeError(
                    "Квитанция относится к другому уведомлению. Отправка остановлена."
                )
            if state.get("state") == "sent" and isinstance(state.get("receipt"), dict):
                _record_history(settings, state_path, state)
                return state["receipt"]
            if state.get("state") in {"sending", "send_unknown"}:
                raise RuntimeError(
                    "Результат прежней отправки неизвестен. "
                    "Повторная отправка остановлена до проверки."
                )
            if state.get("state") == "rejected":
                raise RuntimeError(
                    "Telegram отклонил уведомление. Автоматический повтор остановлен."
                )
            raise RuntimeError("Неизвестное состояние квитанции. Отправка остановлена.")

        state = {
            "state": "sending", "text": text, "created": _now(),
            "chat_id": chat_id, "source": SOURCE, "url": url,
        }
        _save(state_path, state)
        try:
            sent = asyncio.run(_send_once(settings.telegram_bot_token, chat_id, text, url))
        except REJECTIONS:
            state.update(state="rejected", updated=_now())
            _save(state_path, state)
            raise RuntimeError(
                "Telegram отклонил уведомление. Автоматический повтор остановлен."
            ) from None
        except Exception:
            state.update(state="send_unknown", updated=_now())
            _save(state_path, state)
            raise RuntimeError(
                "Доставка уведомления не подтверждена. "
                "Повторная отправка остановлена до проверки."
            ) from None

        receipt = {
            "message_id": sent.message_id,
            "chat_id": sent.chat.id,
            "sent_at": sent.date.astimezone(MOSCOW).isoformat(),
        }
        state.update(state="sent", receipt=receipt, history_saved=False, updated=_now())
        _save(state_path, state)
        _record_history(settings, state_path, state)
        return receipt
