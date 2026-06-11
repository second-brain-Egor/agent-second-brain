"""Helpers for running web access outside inherited proxy wrappers."""

from __future__ import annotations

import os
import sys

DIRECT_WEB_ENV = "D_BRAIN_DIRECT_WEB"

PROXY_ENV_VARS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "FTP_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "ftp_proxy",
    "no_proxy",
    "PROXYCHAINS_CONF_FILE",
    "PROXYCHAINS_QUIET_MODE",
)


def _looks_like_proxychains(value: str) -> bool:
    return "proxychains" in value.lower()


def direct_env() -> dict[str, str]:
    """Return an environment that avoids proxy env vars and proxychains preload."""
    env = os.environ.copy()
    for key in PROXY_ENV_VARS:
        env.pop(key, None)

    ld_preload = env.get("LD_PRELOAD")
    if ld_preload and _looks_like_proxychains(ld_preload):
        env.pop("LD_PRELOAD", None)

    env[DIRECT_WEB_ENV] = "1"
    return env


def ensure_direct_process() -> None:
    """Re-exec Python once if this process inherited proxy settings."""
    if os.environ.get(DIRECT_WEB_ENV) == "1":
        return

    needs_reexec = any(os.environ.get(key) for key in PROXY_ENV_VARS)
    ld_preload = os.environ.get("LD_PRELOAD", "")
    needs_reexec = needs_reexec or _looks_like_proxychains(ld_preload)
    if not needs_reexec:
        os.environ[DIRECT_WEB_ENV] = "1"
        return

    os.execve(sys.executable, [sys.executable, *sys.argv], direct_env())
