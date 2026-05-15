#!/usr/bin/env python3
"""Fetch and extract readable text from a web page."""

from __future__ import annotations

import argparse
import sys

import httpx
import trafilatura


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a web page and extract text.")
    parser.add_argument("url", help="Page URL.")
    parser.add_argument("--max-chars", type=int, default=12000)
    args = parser.parse_args()

    with httpx.Client(
        follow_redirects=True,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    ) as client:
        response = client.get(args.url)
        response.raise_for_status()
        text = trafilatura.extract(
            response.text,
            url=str(response.url),
            include_comments=False,
            include_tables=True,
        ) or response.text

    max_chars = min(max(args.max_chars, 1000), 50000)
    print(text[:max_chars].strip())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Ошибка чтения страницы: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
