#!/usr/bin/env python3
"""Small DuckDuckGo search helper for Claude/Codex subprocesses."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from direct_web.network import ensure_direct_process  # noqa: E402

ensure_direct_process()


def _search(query: str, max_results: int) -> list[dict[str, Any]]:
    from direct_web.search import search

    return search(query, max_results)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search the web via DuckDuckGo.")
    parser.add_argument("query", help="Search query.")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Print raw JSON.")
    args = parser.parse_args()

    max_results = min(max(args.max_results, 1), 10)
    results = _search(args.query, max_results)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    if not results:
        print("Ничего не найдено.")
        return 0

    for index, item in enumerate(results, start=1):
        title = item.get("title") or "Без названия"
        href = item.get("href") or item.get("url") or ""
        body = (item.get("body") or "").replace("\n", " ").strip()
        print(f"{index}. {title}")
        if href:
            print(f"   URL: {href}")
        if body:
            print(f"   {body[:500]}")
        print()

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Ошибка поиска: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
