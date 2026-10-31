#!/usr/bin/env python3
"""Fetch and extract readable text from a web page."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from direct_web.browser import fetch_html, validate_proxy  # noqa: E402
from direct_web.fetch import fetch_with_browser, fetch_with_httpx  # noqa: E402
from direct_web.network import ensure_direct_process  # noqa: E402

ensure_direct_process()


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a web page and extract text.")
    parser.add_argument("url", help="Page URL.")
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument(
        "--html", action="store_true", help="Вернуть HTML страницы для разбора формы."
    )
    parser.add_argument(
        "--wait-selector", help="Дождаться элемента динамической страницы при --html."
    )
    parser.add_argument(
        "--proxy", help="Явно указанный HTTP/SOCKS5-прокси без логина и пароля."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--browser", action="store_true", help="Читать браузером (режим по умолчанию)."
    )
    mode.add_argument(
        "--http", action="store_true", help="Только простой HTTP-запрос без браузера."
    )
    args = parser.parse_args()
    if args.html and args.http:
        parser.error("--html используется с браузерным чтением")
    if args.wait_selector and not args.html:
        parser.error("--wait-selector используется вместе с --html")
    try:
        proxy = validate_proxy(args.proxy)
    except ValueError as exc:
        parser.error(str(exc))

    max_chars = min(max(args.max_chars, 1000), 500000 if args.html else 50000)
    proxy_options = {"proxy": proxy} if proxy else {}

    if args.html:
        html_options = {"wait_selector": args.wait_selector} if args.wait_selector else {}
        text = fetch_html(args.url, **proxy_options, **html_options)
    elif args.http:
        text = fetch_with_httpx(args.url, **proxy_options)
    else:
        text = fetch_with_browser(args.url, **proxy_options)

    print(text[:max_chars].strip())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Ошибка чтения страницы: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
