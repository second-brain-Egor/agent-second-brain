"""Backend (active AI sim) switcher handler.

Provides "🤖 Модель" reply-button and inline keyboard to flip
AI_BACKEND between 'claude' and 'codex' without touching .env manually.
After flipping the value the bot triggers ADMIN_RESTART_COMMAND so the
new backend is picked up by the running process.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shlex
import shutil
from pathlib import Path

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from d_brain.bot.keyboards import get_backend_inline_keyboard
from d_brain.config import get_settings

router = Router(name="backend")
logger = logging.getLogger(__name__)

ENV_PATH = Path(__file__).resolve().parents[3].parent / ".env"
PENDING_SWITCH_PATH = Path("/tmp/d-brain-pending-backend-switch.json")
SUPPORTED = {"claude", "codex"}
LABELS = {
    "claude": "Claude (Claude Max подписка)",
    "codex": "Codex (OpenAI Codex Pro)",
}
AUTH_ERROR_PATTERN = re.compile(
    r"(auth_required|failed to authenticate|request not allowed|api error:\s*403|"
    r"not authenticated|login required|please log in|unauthorized)",
    re.IGNORECASE,
)


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


def _replace_env_value(key: str, value: str) -> None:
    """Replace or append one key in .env."""
    content = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
    if re.search(rf"^{re.escape(key)}=", content, flags=re.MULTILINE):
        new_content = re.sub(
            rf"^{re.escape(key)}=.*$",
            f"{key}={value}",
            content,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        sep = "" if not content or content.endswith("\n") else "\n"
        new_content = f"{content}{sep}{key}={value}\n"
    ENV_PATH.write_text(new_content, encoding="utf-8")


async def _probe_claude_auth() -> tuple[bool, str]:
    """Best-effort Claude CLI auth check before switching the bot to Claude."""
    settings = get_settings()
    claude_bin = shutil.which(settings.claude_bin.strip() or "claude")
    if not claude_bin:
        fallback = Path.home() / ".local" / "bin" / "claude"
        claude_bin = str(fallback) if fallback.exists() else ""
    if not claude_bin:
        return False, "Claude CLI не найден."

    model = settings.claude_model_chat.strip() or settings.claude_model.strip() or "sonnet"
    cmd = [
        claude_bin,
        "-p",
        "--model",
        model,
        "--effort",
        settings.claude_effort.strip() or "medium",
        "--permission-mode",
        "default",
        "--output-format",
        "text",
        "--no-session-persistence",
    ]
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ENV_PATH.parent,
            env=env,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate("Ответь одним словом: ok".encode("utf-8")),
            timeout=45,
        )
    except TimeoutError:
        try:
            proc.kill()
            await proc.wait()
        except Exception:
            pass
        return False, "Claude CLI не ответил за 45 секунд."
    except OSError as exc:
        return False, str(exc)

    details = (
        (stderr.decode("utf-8", errors="replace") or stdout.decode("utf-8", errors="replace"))
        .strip()
        .splitlines()
    )
    message = details[-1] if details else "Claude CLI вернул пустой ответ."
    if proc.returncode == 0:
        return True, ""
    if AUTH_ERROR_PATTERN.search(message):
        return False, "Claude сейчас не авторизован: " + message
    return False, message


@router.message(F.text == "🤖 Модель")
async def btn_backend(message: Message) -> None:
    """Show current backend and switcher."""
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("⛔ Только администратор может менять модель.")
        return

    current = _read_active_backend()
    label = LABELS.get(current, current)
    await message.answer(
        f"<b>🤖 Активная модель:</b> {label}\n\nВыбери:",
        reply_markup=get_backend_inline_keyboard(current),
    )


@router.callback_query(F.data.startswith("backend:"))
async def cb_backend(callback: CallbackQuery) -> None:
    """Apply backend switch via .env edit + admin restart."""
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Не админ.", show_alert=True)
        return

    if callback.data is None:
        await callback.answer()
        return

    new_backend = callback.data.split(":", 1)[1] if ":" in callback.data else ""
    if new_backend not in SUPPORTED:
        await callback.answer("❌ Неизвестный backend", show_alert=True)
        return

    # Codex requires local auth.json — abort early with hint.
    if new_backend == "codex":
        auth_path = Path.home() / ".codex" / "auth.json"
        if not auth_path.exists():
            await callback.answer()
            if callback.message is not None:
                await callback.message.answer(
                    "⚠️ Codex не авторизован — нет <code>~/.codex/auth.json</code>.\n"
                    "Залогинься под пользователем <b>egor</b> по SSH и запусти <code>codex login</code>, потом попробуй снова."
                )
            return

    # Claude can lose OAuth without the file disappearing. Do a real CLI probe and
    # keep the bot on Codex if Claude is unavailable, so the button cannot strand it
    # on a broken sim until manual re-login is possible.
    if new_backend == "claude":
        ok, error = await _probe_claude_auth()
        if not ok:
            try:
                _replace_env_value("AI_BACKEND", "codex")
            except OSError:
                logger.exception("Failed to force AI_BACKEND=codex after Claude probe failure")
            await callback.answer()
            if callback.message is not None:
                await callback.message.answer(
                    "⚠️ Claude сейчас недоступен по авторизации, поэтому оставляю активным <b>Codex</b>.\n\n"
                    f"{error}\n\n"
                    "Когда будет возможность, переавторизуй Claude на сервере и переключи обратно через «🤖 Модель»."
                )
            return

    current = _read_active_backend()
    if current == new_backend:
        await callback.answer(f"Уже активна: {new_backend}", show_alert=True)
        return

    # Replace AI_BACKEND= line in .env (or append if missing).
    try:
        _replace_env_value("AI_BACKEND", new_backend)
    except OSError as exc:
        logger.exception("Failed to write .env")
        await callback.answer(f"❌ {exc}", show_alert=True)
        return

    label = LABELS.get(new_backend, new_backend)
    chat_id = callback.message.chat.id if callback.message is not None else None
    if chat_id is not None:
        try:
            PENDING_SWITCH_PATH.write_text(
                json.dumps({"backend": new_backend, "label": label, "chat_id": chat_id}),
                encoding="utf-8",
            )
        except OSError:
            logger.exception("Failed to write pending backend switch marker")

    if callback.message is not None:
        await callback.message.answer(
            f"🔄 Переключаюсь на <b>{label}</b>… рестарт через ~3 сек."
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
