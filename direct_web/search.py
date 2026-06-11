"""Direct web search helper."""

from __future__ import annotations

from typing import Any


def search(query: str, max_results: int) -> list[dict[str, Any]]:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS  # type: ignore[no-redef]

    with DDGS(proxy=None) as ddgs:
        return list(ddgs.text(query, region="ru-ru", max_results=max_results))
