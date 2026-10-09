#!/usr/bin/env python3
"""Отправить готовый файл из хранилища в чат Telegram и записать отправку в историю беседы.

Запуск из корня проекта: uv run python scripts/send_telegram_file.py <путь> --chat-id <id> [--caption текст]
Путь — от корня vault или абсолютный; файлы вне vault не отправляются.
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile

from d_brain.config import get_settings
from d_brain.services.session import SessionStore


def resolve(path: str, vault: Path) -> Path:
    candidate = Path(path)
    file = (candidate if candidate.is_absolute() else vault / candidate).resolve()
    file.relative_to(vault)  # ValueError for anything outside the vault
    if not file.is_file():
        raise FileNotFoundError(file)
    return file


async def send(path: str, chat_id: int, caption: str | None) -> int:
    settings = get_settings()
    vault = settings.vault_path.resolve()
    file = resolve(path, vault)
    bot = Bot(settings.telegram_bot_token)
    try:
        sent = await bot.send_document(chat_id, FSInputFile(file), caption=caption or None, parse_mode=None)
    finally:
        await bot.session.close()
    relative = file.relative_to(vault).as_posix()
    scope = chat_id if chat_id > 0 else f'chat_{chat_id}'
    SessionStore(settings.vault_path).append(scope, 'assistant', text=f'Отправил файл: {relative}',
                                             path=relative, msg_id=sent.message_id, chat_id=chat_id)
    return sent.message_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--chat-id', required=True, type=int)
    parser.add_argument('--caption')
    args = parser.parse_args()
    print(f'Отправлено, сообщение {asyncio.run(send(args.path, args.chat_id, args.caption))}')


if __name__ == '__main__':
    main()
