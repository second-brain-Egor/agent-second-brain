"""Persistent Playwright browser for direct server-IP browsing."""

from __future__ import annotations

import fcntl
from contextlib import contextmanager
from pathlib import Path

from .network import direct_env

ROOT = Path(__file__).resolve().parent
PROFILE_DIR = ROOT / "browser-profile"
DOWNLOADS_DIR = ROOT / "downloads"
LOCK_PATH = ROOT / "browser-profile.lock"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@contextmanager
def _profile_lock():
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def fetch_html(url: str, timeout: int = 30) -> str:
    """Open a page in Chromium and return rendered HTML."""
    from playwright.sync_api import sync_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    with _profile_lock():
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                headless=True,
                accept_downloads=True,
                downloads_path=DOWNLOADS_DIR,
                locale="ru-RU",
                timezone_id="Europe/Moscow",
                user_agent=USER_AGENT,
                env=direct_env(),
                args=[
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--proxy-server=direct://",
                    "--proxy-bypass-list=*",
                ],
            )
            page = context.new_page()
            page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
            html = page.content()
            context.close()
            return html
