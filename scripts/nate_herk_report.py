#!/usr/bin/env python3
"""Извлекает обязательные поля Telegram-отчёта из карточки Nate Herk."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ALIASES = {
    "theme": ("тема", "тематика", "о чём ролик", "о чем ролик"),
    "content": ("краткое содержание", "кратко", "аннотация", "резюме"),
    "conclusion": ("основной вывод", "главный вывод", "вывод", "выводы"),
}


def clean(value: str) -> str:
    value = re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_`]", "", value)
    return re.sub(r"\s+", " ", value).strip(" -\n")


def sections(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    matches = list(re.finditer(r"^#{2,6}\s+(.+?)\s*$", text, re.MULTILINE))
    for index, match in enumerate(matches):
        heading = clean(match.group(1)).casefold().rstrip(":")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[heading] = clean(text[match.end():end])
    return result


def find_section(items: dict[str, str], field: str) -> str:
    aliases = ALIASES[field]
    for alias in aliases:
        if items.get(alias):
            return items[alias]
    # Допускаем уточнения заголовка: «Основные идеи и тезисы», «Вывод агента».
    for heading, value in items.items():
        if value and any(heading.startswith(alias + " ") for alias in aliases):
            return value
    return ""


def sentence_with(text: str, patterns: tuple[str, ...]) -> str:
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if any(re.search(pattern, sentence, re.IGNORECASE) for pattern in patterns):
            return sentence.strip()
    return ""


def extract(text: str) -> tuple[dict[str, str], list[str]]:
    title_match = re.search(r"^#\s+(?:Карточка ролика:\s*)?(.+?)\s*$", text, re.MULTILINE)
    title = clean(title_match.group(1)) if title_match else ""
    items = sections(text)
    content = find_section(items, "content")
    theme = find_section(items, "theme")
    conclusion = find_section(items, "conclusion")

    # Старые карточки объединяли обязательные поля в разделе «Кратко».
    if not theme and content:
        theme = re.split(r"(?<=[.!?])\s+", content, maxsplit=1)[0]
    if not conclusion and content:
        conclusion = sentence_with(
            content,
            (r"\b(?:главн|основн)\w*\s+вывод", r"\bвывод\s+(?:ролика|автора|агента)"),
        )

    values = {"title": title, "theme": theme, "content": content, "conclusion": conclusion}
    missing = [name for name, value in values.items() if not value]
    return values, missing


def main() -> int:
    if len(sys.argv) != 2:
        print("Использование: nate_herk_report.py analysis.md", file=sys.stderr)
        return 2
    values, missing = extract(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if missing:
        print("Не найдены обязательные поля: " + ", ".join(missing), file=sys.stderr)
        return 1
    print(
        f"Название: {values['title']}\n\nТема: {values['theme']}\n\n"
        f"Содержание: {values['content']}\n\nОсновной вывод: {values['conclusion']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
