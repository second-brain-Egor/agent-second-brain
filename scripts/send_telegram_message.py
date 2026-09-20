#!/usr/bin/env python3
"""Отправка длинного простого текста в Telegram несколькими сообщениями."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import urllib.parse
import urllib.request


def split_message(text: str, limit: int = 3800) -> list[str]:
    """Разбить текст по абзацам, не превышая лимит Telegram."""
    if not text:
        return []

    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        while len(paragraph) > limit:
            split_at = paragraph.rfind("\n", 0, limit + 1)
            if split_at <= 0:
                split_at = paragraph.rfind(" ", 0, limit + 1)
            if split_at <= 0:
                split_at = limit
            chunks.append(paragraph[:split_at].rstrip())
            paragraph = paragraph[split_at:].lstrip()
        current = paragraph
    if current:
        chunks.append(current)
    return chunks


def send(token: str, chat_id: str, text: str, receipt_file: Path | None = None) -> int:
    chunks = split_message(text)
    for chunk in chunks:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": chunk}).encode()
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage", data=data
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.load(response)
        if not result.get("ok"):
            raise RuntimeError(f"Telegram отклонил сообщение: {result}")
        if receipt_file is not None:
            message = result["result"]
            receipt_file.parent.mkdir(parents=True, exist_ok=True)
            with receipt_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                    "message_id": message["message_id"],
                    "chat_id": message["chat"]["id"],
                    "characters": len(chunk),
                }, ensure_ascii=False) + "\n")
    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--receipt-file", type=Path)
    args = parser.parse_args()
    text = __import__("sys").stdin.read()
    send(args.token, args.chat_id, text, args.receipt_file)


if __name__ == "__main__":
    main()
