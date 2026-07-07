"""Claude model switcher handler.

Provides "🧠 Claude" reply-button and inline keyboard to flip Claude
model (Opus / Sonnet / Fable) without touching .env manually. Sets
CLAUDE_MODEL, CLAUDE_MODEL_CHAT and CLAUDE_MODEL_AGENT to the same
value — one knob for chat, agent and /do alike. After flipping, the
bot triggers ADMIN_RESTART_COMMAND so the new model is picked up by
the running process.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import shlex
from pathlib import Path

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from d_brain.bot.handlers.backend import _probe_claude_auth
from d_brain.bot.keyboards import get_claude_model_inline_keyboard
from d_brain.config import get_settings

router = Router(name="claude_model")
logger = logging.getLogger(__name__)

ENV_PATH = Path(__file__).resolve().parents[3].parent / ".env"
PENDING_SWITCH_PATH = Path("/tmp/d-brain-pending-model-switch.json")
SUPPORTED = {"opus", "sonnet", "fable"}
LABELS = {
    "opus": "Opus",
    "sonnet": "Sonnet",
    "fable": "Fable",
}
ENV_KEYS = ("CLAUDE_MODEL", "CLAUDE_MODEL_CHAT", "CLAUDE_MODEL_AGENT")


def _read_active_model() -> str:
    """Read CLAUDE_MODEL_CHAT directly from .env (truth source, not cached settings)."""
    if not ENV_PATH.exists():
        return "opus"
    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("CLAUDE_MODEL_CHAT="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            return value or "opus"
    return "opus"


def _read_active_backend() -> str:
    """Read AI_BACKEND directly from .env (truth source, not cached settings)."""
    if not ENV_PATH.exists():
        return "codex"
    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("AI_BACKEND="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            return value or "codex"
    return "codex"


def _is_admin(user_id: int) -> bool:
    return user_id in get_settings().admin_user_ids


@router.message(F.text == "🧠 Claude")
async def btn_claude_model(message: Message) -> None:
    """Show current Claude model and switcher."""
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("⛔ Только администратор может менять модель.")
        return

    current = _read_active_model()
    label = LABELS.get(current, current)
    await message.answer(
        f"<b>🧠 Активная модель Claude:</b> {label}\n\nВыбери:",
        reply_markup=get_claude_model_inline_keyboard(current),
    )


@router.callback_query(F.data.startswith("claude_model:"))
async def cb_claude_model(callback: CallbackQuery) -> None:
    """Apply model switch via .env edit + admin restart."""
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Не админ.", show_alert=True)
        return

    if callback.data is None:
        await callback.answer()
        return

    new_model = callback.data.split(":", 1)[1] if ":" in callback.data else ""
    if new_model not in SUPPORTED:
        await callback.answer("❌ Неизвестная модель", show_alert=True)
        return

    current = _read_active_model()
    backend = _read_active_backend()
    if current == new_model and backend == "claude":
        await callback.answer(f"Уже активна: {new_model}", show_alert=True)
        return

    # Picking a Claude model means the user wants Claude answering, so flip
    # AI_BACKEND to claude as well — otherwise the bot keeps talking to Codex
    # while reporting a successful "switch to Claude".
    switch_backend = backend != "claude"
    if switch_backend:
        ok, error = await _probe_claude_auth()
        if not ok:
            await callback.answer()
            if callback.message is not None:
                await callback.message.answer(
                    "⚠️ Claude сейчас недоступен по авторизации, поэтому не переключаюсь — "
                    "бэкенд остаётся прежним.\n\n"
                    f"{error}"
                )
            return

    try:
        content = ENV_PATH.read_text(encoding="utf-8")
        keys = ENV_KEYS + (("AI_BACKEND",) if switch_backend else ())
        values = {key: new_model for key in ENV_KEYS}
        values["AI_BACKEND"] = "claude"
        for key in keys:
            new_value = values[key]
            pattern = rf"^{key}=.*$"
            if re.search(pattern, content, flags=re.MULTILINE):
                content = re.sub(
                    pattern,
                    f"{key}={new_value}",
                    content,
                    count=1,
                    flags=re.MULTILINE,
                )
            else:
                sep = "" if content.endswith("\n") else "\n"
                content = f"{content}{sep}{key}={new_value}\n"
        ENV_PATH.write_text(content, encoding="utf-8")
    except OSError as exc:
        logger.exception("Failed to write .env")
        await callback.answer(f"❌ {exc}", show_alert=True)
        return

    label = LABELS.get(new_model, new_model)
    chat_id = callback.message.chat.id if callback.message is not None else None
    if chat_id is not None:
        try:
            PENDING_SWITCH_PATH.write_text(
                json.dumps({"model": new_model, "label": label, "chat_id": chat_id}),
                encoding="utf-8",
            )
        except OSError:
            logger.exception("Failed to write pending switch marker")

    if callback.message is not None:
        note = " и делаю Claude активным бэкендом" if switch_backend else ""
        await callback.message.answer(
            f"🔄 Переключаю Claude на <b>{label}</b>{note}… рестарт через ~3 сек."
        )
    await callback.answer()

    settings = get_settings()
    cmd = settings.admin_restart_command.strip()
    if not cmd:
        if callback.message is not None:
            await callback.message.answer(
                "⚠️ <code>ADMIN_RESTART_COMMAND</code> не задан в .env. "
                "Перезапусти бота вручную: <code>sudo systemctl restart d-brain-bot</code>."
            )
        return

    asyncio.create_task(_delayed_restart(cmd))


async def _delayed_restart(cmd: str) -> None:
    """Run admin restart command with a small delay so the ack message can leave."""
    await asyncio.sleep(2)
    args = shlex.split(cmd)
    if not args:
        return
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
    except Exception:
        logger.exception("Admin restart command failed")
