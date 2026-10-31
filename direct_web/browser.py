"""Persistent Playwright browser using the server's existing network route."""

from __future__ import annotations

import fcntl
from contextlib import ExitStack, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

from .network import direct_env
from .responses import PageReadError, validate_response

ROOT = Path(__file__).resolve().parent
PROFILE_DIR = ROOT / "browser-profile"
DOWNLOADS_DIR = ROOT / "downloads"
LOCK_PATH = ROOT / "browser-profile.lock"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def validate_proxy(proxy: str | None) -> str | None:
    """Validate an explicit proxy without including its address in errors."""
    if proxy is None:
        return None
    try:
        parsed = urlsplit(proxy)
        valid = (
            bool(proxy)
            and not any(character.isspace() for character in proxy)
            and parsed.scheme in {"http", "https", "socks5"}
            and bool(parsed.hostname)
            and parsed.port is not None
            and parsed.port > 0
            and parsed.username is None
            and parsed.password is None
            and parsed.path in {"", "/"}
            and not parsed.query
            and not parsed.fragment
        )
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise ValueError(
            "Укажите прокси http://, https:// или socks5:// с адресом и портом, "
            "без логина, пароля и дополнительных параметров."
        )
    return proxy


@contextmanager
def _profile_lock():
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def fetch_html(
    url: str, timeout: int = 30, *, proxy: str | None = None,
    wait_selector: str | None = None,
) -> str:
    """Open a page in Chromium and return rendered HTML."""
    from playwright.sync_api import Error, TimeoutError, sync_playwright

    proxy = validate_proxy(proxy)

    with ExitStack() as stack:
        if proxy is None:
            stack.enter_context(_profile_lock())
            profile_dir, downloads_dir = PROFILE_DIR, DOWNLOADS_DIR
        else:
            temporary_dir = Path(
                stack.enter_context(TemporaryDirectory(prefix="direct-web-proxy-"))
            )
            profile_dir = temporary_dir / "profile"
            downloads_dir = temporary_dir / "downloads"
        profile_dir.mkdir(parents=True, exist_ok=True)
        downloads_dir.mkdir(parents=True, exist_ok=True)
        args = [
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-dev-shm-usage",
        ]
        proxy_options = {}
        if proxy is None:
            args.extend(["--proxy-server=direct://", "--proxy-bypass-list=*"])
        else:
            proxy_options["proxy"] = {"server": proxy}
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=True,
                accept_downloads=True,
                downloads_path=downloads_dir,
                locale="ru-RU",
                timezone_id="Europe/Moscow",
                env=direct_env(),
                args=args,
                **proxy_options,
            )
            try:
                page = context.new_page()
                main_response = None

                def remember_response(response):
                    nonlocal main_response
                    if (
                        response.request.is_navigation_request()
                        and response.frame == page.main_frame
                    ):
                        main_response = response

                page.on("response", remember_response)
                response = page.goto(
                    url, timeout=timeout * 1000, wait_until="domcontentloaded"
                )
                page.wait_for_timeout(2500)
                if wait_selector:
                    # Проверяем отказ до ожидания динамической выдачи.
                    current = main_response or response
                    if current is not None:
                        validate_response(current.status, page.content(), page.url,
                                          current.headers)
                    page.wait_for_selector(wait_selector, timeout=timeout * 1000)
                response = main_response or response
                if response is None:
                    raise PageReadError(url, "браузер не получил ответ страницы")
                html = page.content()
                validate_response(response.status, html, page.url, response.headers)
                return html
            except TimeoutError as exc:
                raise PageReadError(
                    url, f"сайт не ответил браузеру за {timeout} секунд"
                ) from exc
            except Error as exc:
                raise PageReadError(
                    url, "браузер не смог загрузить страницу"
                ) from exc
            finally:
                context.close()
