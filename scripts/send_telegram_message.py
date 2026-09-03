#!/usr/bin/env python3
"""Отправка длинного простого текста в Telegram несколькими сообщениями."""

from __future__ import annotations

import argparse
import json
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


def send(token: str, chat_id: str, text: str) -> int:
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
    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--chat-id", required=True)
    args = parser.parse_args()
    text = __import__("sys").stdin.read()
    send(args.token, args.chat_id, text)


if __name__ == "__main__":
    main()
