"""Меню «⚙️ Обработать» → «VPN»: состояние шведского выхода, обновление, смена ссылки подписки.

Включается переменной VPN_GUARD_ENABLED=1 (только там, где установлен /usr/local/sbin/vpn-guard)
и работает только для администратора. Сами проверки и замену узла делает страж на сервере;
бот лишь вызывает его через sudo.

Ссылка подписки — секрет. Поэтому её перехватывает VpnLinkCapture ДО очереди сообщений,
журнала и временного чата: сообщение сразу удаляется из чата, а в журнал, входящую очередь,
историю и файлы дня не попадает. Саму ссылку страж получает только через стандартный ввод.
"""
from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from d_brain.config import get_settings

logger = logging.getLogger(__name__)
router = Router(name="vpn_menu")

GUARD = "/usr/local/sbin/vpn-guard"
LINK_TTL = 300  # сколько секунд бот ждёт ссылку после «Заменить ссылку»
# Начало сообщения, которое точно является ключом VPN, а не обычной ссылкой из переписки.
SECRET_SCHEMES = ("vless://", "vmess://", "trojan://", "ss://", "happ://")
MENU_TEXT = "⚙️ <b>Что запустить?</b>"
NO_ANSWER = "⚠️ Страж VPN не вернул ответа."
VPN_TEXT = "🔐 <b>VPN</b>\n\nШведский выход, через который сервер ходит в интернет. Что сделать?"

# user_id → (срок ожидания по monotonic, chat_id, id сообщения-приглашения)
waiting: dict[int, tuple[float, int, int]] = {}


def enabled_for(user_id: int | None) -> bool:
    return bool(user_id) and os.environ.get("VPN_GUARD_ENABLED") == "1" \
        and user_id in get_settings().admin_user_ids


class VpnAdmin(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return enabled_for(event.from_user.id if event.from_user else None)


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙️ Обработать", callback_data="menu:process")
    builder.button(text="🔐 VPN", callback_data="menu:vpn")
    builder.adjust(2)
    return builder.as_markup()


def vpn_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, data in (("📊 Состояние", "vpn:status"), ("🔄 Обновить сейчас", "vpn:refresh"),
                       ("🔗 Заменить ссылку", "vpn:url"), ("◀️ Назад", "menu:back")):
        builder.button(text=text, callback_data=data)
    builder.adjust(2, 2)
    return builder.as_markup()


def cancel_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✖️ Отмена", callback_data="vpn:cancel")
    return builder.as_markup()


async def run_guard(*args: str, stdin: str | None = None, timeout: int = 300) -> dict[str, Any]:
    """sudo vpn-guard …; ссылки и ключи идут только через stdin, в списке аргументов их нет."""
    import json

    process = None
    try:
        process = await asyncio.create_subprocess_exec(
            "sudo", "-n", GUARD, *args,
            stdin=asyncio.subprocess.PIPE if stdin is not None else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        output, _ = await asyncio.wait_for(
            process.communicate(stdin.encode() if stdin is not None else None), timeout)
    except asyncio.TimeoutError:
        with contextlib.suppress(ProcessLookupError):
            process.kill()
        return {"ok": False, "message": "⏳ Проверка VPN идёт дольше обычного. Нажми «Состояние» через минуту."}
    except OSError:
        return {"ok": False, "message": "⚠️ Не удалось запустить стража VPN на сервере."}
    try:
        return json.loads(output.decode().strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"ok": False, "message": "⚠️ Страж VPN ответил непонятно. Подробности в /var/log/vpn-guard.log."}


async def show(message: Message, text: str, markup: InlineKeyboardMarkup | None) -> Message:
    """Меняет текст сообщения с меню; если нельзя (удалено, не изменилось), присылает новое."""
    try:
        edited = await message.edit_text(text, reply_markup=markup)
        return edited if isinstance(edited, Message) else message
    except TelegramBadRequest as error:
        if "not modified" in str(error):
            return message
        return await message.answer(text, reply_markup=markup)


def start_supervised(jobs: Any, scope: int, request: str,
                     work: Callable[[], Awaitable[Any]]) -> asyncio.Task:
    """Запускает работу от кнопки под тем же надзором, что и сообщение: «стоп» её останавливает."""
    from d_brain.services.execution import TERMINAL, Execution, ExecutionStopped, execution_context

    if jobs is None:
        return asyncio.create_task(work())
    execution = Execution(jobs.settings.vault_path.parent, scope=scope, request=request, origin="bot")
    key = f"{scope}:button:{execution.id}"

    async def run() -> None:
        with execution_context(execution):
            try:
                execution.update(state="running")
                await work()
                if execution.data["state"] not in TERMINAL:
                    execution.update(state="completed")
            except (asyncio.CancelledError, ExecutionStopped):
                if execution.data["state"] not in TERMINAL:
                    execution.stop("interrupted")
            except Exception:
                execution.update(state="error")
                logger.exception("Button task %s failed", execution.id)
            finally:
                jobs.active.pop(key, None)

    task = asyncio.create_task(run())
    jobs.active[key] = (execution, task)
    jobs.tasks.add(task)
    task.add_done_callback(jobs.tasks.discard)
    return task


# ───────────────────────────── перехват ссылки ─────────────────────────────

class VpnLinkCapture:
    """Стоит в цепочке сразу после проверки доступа и до очереди, журнала и временного чата."""

    async def __call__(self, handler: Callable, event: Any, data: dict[str, Any]) -> Any:
        message = event.message
        user = message.from_user if message is not None else None
        if user is None or not enabled_for(user.id) or message.chat.type != "private":
            return await handler(event, data)
        text = (message.text or "").strip()
        pending = waiting.get(user.id)
        if pending and time.monotonic() > pending[0]:
            waiting.pop(user.id, None)
            pending = None
        if pending and "://" in text:
            waiting.pop(user.id, None)
            await capture(message, data["bot"], text, pending)
            return None
        if text.lower().startswith(SECRET_SCHEMES):
            # Ключ прислан не через меню: убираем из чата, пока он не попал в журнал.
            waiting.pop(user.id, None)
            await refuse(message)
            return None
        waiting.pop(user.id, None)  # обычное сообщение отменяет ожидание ссылки
        return await handler(event, data)


async def delete_quietly(message: Message) -> bool:
    try:
        await message.delete()
        return True
    except Exception:  # без текста ошибки: он не нужен, а сообщение содержит ключ
        return False


async def refuse(message: Message) -> None:
    deleted = await delete_quietly(message)
    logger.info("Ключ VPN прислан вне меню; сообщение %s", "удалено" if deleted else "НЕ удалено")
    await message.answer(
        "🔒 <b>Это похоже на ключ VPN.</b> "
        + ("Я удалил сообщение, чтобы ключ не остался в чате и журнале.\n\n" if deleted
           else "Удалить сообщение у меня не вышло, удали его сам.\n\n")
        + "Чтобы применить, нажми «⚙️ Обработать» → «VPN» → «Заменить ссылку» и пришли ещё раз.")


async def capture(message: Message, bot: Any, link: str, pending: tuple[float, int, int]) -> None:
    deleted = await delete_quietly(message)
    # В журнал — только длина и факт удаления: сама ссылка секретна.
    logger.info("Получена ссылка VPN (%d симв.), сообщение %s", len(link),
                "удалено" if deleted else "НЕ удалено")
    _, chat_id, prompt_id = pending
    try:
        result = await run_guard("set-url", stdin=link, timeout=420)
        text = result.get("message", NO_ANSWER)
    except Exception as error:  # без текста ошибки: он может содержать ввод
        logger.error("Не удалось применить ссылку VPN (%s)", type(error).__name__)
        text = "⚠️ Не удалось применить ссылку. Конфигурацию не менял."
    if not deleted:
        text += "\n\n⚠️ Сообщение со ссылкой удалить не удалось: удали его сам."
    try:
        await bot.edit_message_text(text, chat_id=chat_id, message_id=prompt_id, reply_markup=vpn_menu())
    except TelegramBadRequest:
        await bot.send_message(chat_id, text, reply_markup=vpn_menu())


# ───────────────────────────────── обработчики ─────────────────────────────────

@router.message(F.text == "⚙️ Обработать", F.chat.type == "private", VpnAdmin())
async def show_menu(message: Message) -> None:
    await message.answer(MENU_TEXT, reply_markup=main_menu())


@router.callback_query(F.data.startswith(("menu:", "vpn:")), ~VpnAdmin())
async def refuse_callback(callback: CallbackQuery) -> None:
    await callback.answer("Это меню доступно только администратору.", show_alert=True)


@router.callback_query(F.data == "menu:back", VpnAdmin())
async def menu_back(callback: CallbackQuery) -> None:
    waiting.pop(callback.from_user.id, None)
    await callback.answer()
    await show(callback.message, MENU_TEXT, main_menu())


@router.callback_query(F.data == "menu:vpn", VpnAdmin())
async def menu_vpn(callback: CallbackQuery) -> None:
    await callback.answer()
    await show(callback.message, VPN_TEXT, vpn_menu())


@router.callback_query(F.data == "menu:process", VpnAdmin())
async def menu_process(callback: CallbackQuery, request_jobs: Any = None) -> None:
    """То же, что прежняя кнопка «⚙️ Обработать»: обработка дня, затем коммит и отправка в git."""
    from d_brain.bot.handlers.process import cmd_process

    await callback.answer()
    message = callback.message
    await delete_quietly(message)
    start_supervised(request_jobs, callback.from_user.id, "⚙️ Обработать", lambda: cmd_process(message))


@router.callback_query(F.data == "vpn:status", VpnAdmin())
async def vpn_status(callback: CallbackQuery) -> None:
    await callback.answer()
    await show(callback.message, "⏳ Проверяю выход и Telegram…", None)
    result = await run_guard("status", timeout=120)
    await show(callback.message, result.get("message", NO_ANSWER), vpn_menu())


@router.callback_query(F.data == "vpn:refresh", VpnAdmin())
async def vpn_refresh(callback: CallbackQuery) -> None:
    await callback.answer()
    await show(callback.message, "⏳ Беру подписку и проверяю узел. Это может занять до пары минут.", None)
    result = await run_guard("refresh", "--force", timeout=420)
    await show(callback.message, result.get("message", NO_ANSWER), vpn_menu())


@router.callback_query(F.data == "vpn:url", VpnAdmin())
async def vpn_url(callback: CallbackQuery) -> None:
    await callback.answer()
    prompt = await show(
        callback.message,
        "🔗 <b>Жду ссылку.</b> Пришли её одним сообщением: я сразу удалю его из чата и нигде не запишу.\n\n"
        "Подойдёт ссылка подписки <code>https://…</code> (тогда включится автообновление) "
        "или одиночный узел <code>vless://…</code>.",
        cancel_menu())
    waiting[callback.from_user.id] = (time.monotonic() + LINK_TTL, prompt.chat.id, prompt.message_id)


@router.callback_query(F.data == "vpn:cancel", VpnAdmin())
async def vpn_cancel(callback: CallbackQuery) -> None:
    waiting.pop(callback.from_user.id, None)
    await callback.answer("Отменил.")
    await show(callback.message, VPN_TEXT, vpn_menu())
