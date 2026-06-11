"""Web search fast-path: /web и интент «найди в интернете».

Поиск идёт мимо тяжёлого чат-пути (без CLAUDE.md-налога и таймаутов чата):
scripts/web_search.py напрямую → мгновенные карточки результатов → следом
короткая выжимка лёгким LLM-вызовом без памяти и правил (см.
processor.web_quick_summary). Роутер подключается ДО text (catch-all).
"""

import asyncio
import html
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from d_brain.bot.chat_context import build_msg_type, get_session_scope
from d_brain.bot.typing_indicator import keep_typing
from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="web")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SEARCH_SCRIPT = PROJECT_ROOT / "scripts" / "web_search.py"
SEARCH_TIMEOUT = 45
MAX_RESULTS = 5

# «найди/поищи/погугли … в интернете/в сети/в гугле/по сайтам» — узкие пары,
# чтобы не отнимать запросы у поиска по vault («найди в заметках…»).
_INTENT = re.compile(
    r"(найди|поищи|посмотри|погугли|загугли|глянь|узнай|проверь)"
    r"[^.\n]{0,60}?"
    r"(в\s+(интернете|инете|сети|гугле|яндексе)|по\s+сайтам|онлайн)"
    r"|^\s*(погугли|загугли)\b",
    re.IGNORECASE,
)


def matches_web_intent(text: str) -> bool:
    return bool(_INTENT.search(text))


def _clean_query(text: str) -> str:
    """Убираем интент-обороты, чтобы поисковику ушёл чистый запрос."""
    query = _INTENT.sub(" ", text)
    query = re.sub(r"\s+", " ", query).strip(" ,.!?—-")
    return query if len(query) >= 3 else text.strip()


def _run_search(query: str) -> list[dict]:
    result = subprocess.run(
        [sys.executable, str(SEARCH_SCRIPT), query, "--max-results", str(MAX_RESULTS), "--json"],
        capture_output=True,
        text=True,
        timeout=SEARCH_TIMEOUT,
        cwd=PROJECT_ROOT,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "web_search failed").strip().splitlines()[-1])
    return json.loads(result.stdout or "[]")


def _format_cards(results: list[dict]) -> str:
    lines = ["🔍 <b>Нашёл в интернете:</b>", ""]
    for index, item in enumerate(results, start=1):
        title = html.escape(item.get("title") or "Без названия")
        url = html.escape(item.get("href") or item.get("url") or "", quote=True)
        body = html.escape((item.get("body") or "").replace("\n", " ").strip())
        if len(body) > 180:
            body = body[:177].rstrip() + "…"
        lines.append(f'{index}. <a href="{url}">{title}</a>' if url else f"{index}. {title}")
        if body:
            lines.append(f"   {body}")
        lines.append("")
    return "\n".join(lines).strip()


def _results_block(results: list[dict]) -> str:
    parts = []
    for item in results:
        parts.append(
            f"- {item.get('title') or ''}\n"
            f"  URL: {item.get('href') or item.get('url') or ''}\n"
            f"  {(item.get('body') or '').strip()[:400]}"
        )
    return "\n".join(parts)


async def _do_web_search(message: Message, query: str) -> None:
    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
    session = SessionStore(settings.vault_path)
    scope = get_session_scope(message)

    timestamp = datetime.fromtimestamp(message.date.timestamp())
    storage.append_to_daily(message.text or query, timestamp, build_msg_type(message, "[web]"))
    session.append(
        scope,
        "text",
        text=message.text or query,
        msg_id=message.message_id,
        chat_id=message.chat.id,
        chat_title=message.chat.title,
    )

    status = await message.answer("🔍 Ищу в интернете…")
    try:
        results = await asyncio.to_thread(_run_search, query)
    except Exception:
        logger.exception("web search failed")
        await status.edit_text("⚠️ Поиск сейчас недоступен. Попробуй ещё раз через минуту.")
        return

    if not results:
        await status.edit_text("🔍 Ничего не нашлось. Попробуй переформулировать запрос.")
        return

    cards = _format_cards(results)
    try:
        await status.edit_text(cards, disable_web_page_preview=True)
    except Exception:
        await status.edit_text(cards, parse_mode=None, disable_web_page_preview=True)
    session.append(scope, "assistant", text=cards, chat_id=message.chat.id, chat_title=message.chat.title)

    # Выжимка — best effort: карточки уже у пользователя, фейл просто молчит.
    processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
    async with keep_typing(message.chat):
        summary = await asyncio.to_thread(
            processor.web_quick_summary, query, _results_block(results)
        )
    if summary:
        try:
            await message.answer(summary)
        except Exception:
            await message.answer(summary, parse_mode=None)
        session.append(scope, "assistant", text=summary, chat_id=message.chat.id, chat_title=message.chat.title)


@router.message(Command("web"))
async def handle_web_command(message: Message) -> None:
    if not message.text or not message.from_user:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("🔍 Напиши запрос после команды: <code>/web цена осб-3 9мм</code>")
        return
    await _do_web_search(message, parts[1].strip())


@router.message(
    StateFilter(None),
    lambda m: m.text is not None and not m.text.startswith("/") and matches_web_intent(m.text),
)
async def handle_web_intent(message: Message) -> None:
    if not message.text or not message.from_user:
        return
    await _do_web_search(message, _clean_query(message.text))
