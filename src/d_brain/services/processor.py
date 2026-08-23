"""AI processing service."""

from __future__ import annotations

import contextlib
import fcntl
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from collections.abc import Iterator
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path
from typing import Any

from d_brain.services.session import SessionStore


# Per v3: separate locks для диалога и тяжёлой обработки.
# Диалог не блокирует обработку и наоборот, но два диалога / два process одновременно — нет.
_CHAT_LOCK_PATH = "/tmp/claude-chat.lock"
_HEAVY_LOCK_PATH = "/tmp/claude-heavy.lock"

# Маркеры «до этого места обработано» в daily-файлах: блок `processed: <ISO>`
# пишет агент при обработке, `<!-- ✓ processed -->` дописывает cron process.sh.
_PROCESSED_MARKER_RE = re.compile(r"^processed:\s|<!-- ✓ processed -->")
# Служебные строки маркер-блока, не считающиеся содержимым.
_MARKER_NOISE_RE = re.compile(r"^(---|thoughts:.*|tasks:.*|<!--.*-->)\s*$")
# Сколько дней назад искать необработанные записи.
_PENDING_LOOKBACK_DAYS = 14


@contextlib.contextmanager
def _file_lock(path: str) -> Iterator[None]:
    """Blocking flock на файле. Освобождается автоматически при выходе из контекста."""
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _claude_chat_lock() -> Any:
    """Lock для диалогового режима (light model)."""
    return _file_lock(_CHAT_LOCK_PATH)


def _claude_heavy_lock() -> Any:
    """Lock для тяжёлой обработки (heavy model, /process, /do)."""
    return _file_lock(_HEAVY_LOCK_PATH)

logger = logging.getLogger(__name__)

AGENT_MARKER = "[NEED_AGENT]"
AGENT_MARKER_PATTERN = re.compile(
    r"^\s*(?:<[^>]+>\s*)*" + re.escape(AGENT_MARKER) + r"(?:\s|$)",
    re.IGNORECASE,
)

PENDING_ACTION_TTL_SECONDS = 300
CHAT_TIMEOUT_SECONDS = 900
MEDIA_GENERATION_TIMEOUT_SECONDS = 300
ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

CLAUDE_AUTH_ERROR_PATTERN = re.compile(
    r"(auth_required|failed to authenticate|request not allowed|api error:\s*403|"
    r"invalid api key|not authenticated|login required)",
    re.IGNORECASE,
)

MEDIA_REQUEST_PATTERN = re.compile(
    r"\b(фото|картинк\w*|изображени\w*|видео|ролик\w*|image|photo|picture|video)\b",
    re.IGNORECASE,
)
GENERATION_ACTION_PATTERN = re.compile(
    r"\b("
    r"сгенерир\w*|генерир\w*|созда[йт]\w*|нарису\w*|сдела[йт]\w*|"
    r"generate|create|draw|make"
    r")\b",
    re.IGNORECASE,
)

CONFIRMATION_WORDS = frozenset({
    "делай", "делайте",
    "да", "ага", "угу",
    "ок", "окей", "ok", "okay",
    "го", "поехали", "пошёл", "пошел", "пошли",
    "давай", "давайте",
    "запускай", "запускайте",
    "начинай", "начинайте", "начни",
    "старт", "стартуй",
    "валяй",
    "хорошо", "ладно",
    "разрешаю", "одобряю", "утверждаю",
    "именно", "точно", "верно", "правильно",
    "yes", "yep", "yeah",
})

CANCELLATION_WORDS = frozenset({
    "нет", "неа", "не-а",
    "отмена", "отмени", "отменить", "отменяй",
    "стоп", "стой",
    "отставить",
    "забудь", "забей",
    "хватит",
    "ошибся",
})

CANCELLATION_PHRASES = (
    "не делай", "не надо", "не нужно", "не запускай", "не стоит", "не сейчас",
)

MAX_TOOL_STEPS = 24
SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".data",
}
SUPPORTED_REASONING_EFFORTS = {"none", "low", "medium", "high", "xhigh"}
SUPPORTED_VERBOSITY = {"low", "medium", "high"}
PLANNING_GUARDRAILS = """
Planning guardrails:
- Do not impose deadlines, reminders, urgency, or overdue framing unless the user explicitly asked for that or provided a concrete external date.
- Do not turn long-horizon projects into weekly or today tasks by default. This includes the planer/thicknesser build, the bathhouse project, and similar workshop or construction projects.
- Treat old weekly or monthly planning files as background context, not as proof of current urgency.
- If memory or recent session context says a project belongs to a seasonal, yearly, or long horizon, preserve that horizon in both wording and actions.
- Do not create or update Todoist due dates just to make planning look concrete.
- Repetition is a bug: if the user already knows or just discussed something, do not repeat it unless asked.
""".strip()


class AgentProcessor:
    """Project AI processor."""

    _memory_cache: dict[str, Any] = {}
    _memory_cache_time: float = 0.0
    # Pending actions awaiting user confirmation. Key: str(scope). Lost on bot restart — by design.
    _pending_actions: dict[str, dict[str, Any]] = {}

    def __init__(self, vault_path: Path, todoist_api_key: str = "") -> None:
        self.vault_path = Path(vault_path).resolve()
        self.project_path = self.vault_path.parent.resolve()
        self.todoist_api_key = todoist_api_key

        from d_brain.config import get_settings

        settings = get_settings()
        self.ai_backend = (settings.ai_backend or "codex").strip().lower()
        if self.ai_backend not in {"codex", "claude"}:
            self.ai_backend = "codex"

        self.codex_bin = settings.codex_bin.strip() or "codex"
        self.codex_model = settings.codex_model.strip() or "gpt-5.5"
        self.codex_model_chat = settings.codex_model_chat.strip() or self.codex_model
        self.codex_model_agent = settings.codex_model_agent.strip() or self.codex_model
        self.codex_sandbox_mode = settings.codex_sandbox_mode.strip().lower() or "bypass"

        self.claude_bin = settings.claude_bin.strip() or "claude"
        self.claude_model = settings.claude_model.strip() or "sonnet"
        self.claude_model_chat = settings.claude_model_chat.strip() or self.claude_model
        self.claude_model_agent = settings.claude_model_agent.strip() or self.claude_model
        claude_effort = settings.claude_effort.strip().lower() or "medium"
        if claude_effort not in {"low", "medium", "high", "xhigh", "max"}:
            claude_effort = "medium"
        self.claude_effort = claude_effort

        effort = os.environ.get("CODEX_REASONING_EFFORT", "medium").strip().lower()
        if effort not in SUPPORTED_REASONING_EFFORTS:
            effort = "medium"
        self.codex_reasoning_effort = effort

    def _load_skill_content(self) -> str:
        """Load dbrain-processor skill content for extra context."""
        for skill_path in (
            self.vault_path / ".codex/skills/dbrain-processor/SKILL.md",
            self.vault_path / ".claude/skills/dbrain-processor/SKILL.md",
        ):
            if skill_path.exists():
                return skill_path.read_text(encoding="utf-8", errors="ignore")
        return ""

    def _load_todoist_reference(self) -> str:
        """Load Todoist reference for prompt context."""
        for ref_path in (
            self.vault_path / ".codex/skills/dbrain-processor/references/todoist.md",
            self.vault_path / ".claude/skills/dbrain-processor/references/todoist.md",
        ):
            if ref_path.exists():
                return ref_path.read_text(encoding="utf-8", errors="ignore")
        return ""

    def _load_telegram_formatting_skill(self) -> str:
        """Load the project Telegram formatting skill."""
        skill_path = self.project_path / "Скиллы" / "telegram-formatting" / "SKILL.md"
        if skill_path.exists():
            return skill_path.read_text(encoding="utf-8", errors="ignore")
        return ""

    def _planning_guardrails(self) -> str:
        """Shared prompt rules for planning horizon and reminders."""
        return PLANNING_GUARDRAILS

    @staticmethod
    def _is_media_generation_request(text: str) -> bool:
        """Detect photo/image/video requests (generation OR processing) — bump timeout to 300s.

        2026-05-10: убрано требование глагола генерации. Любое упоминание медиа
        (фото/картинка/изображение/видео/ролик/image/photo/picture/video) даёт 300с,
        иначе анализ/обработка/транскрипция валились на 90-сек чат-таймауте.
        """
        return bool(MEDIA_REQUEST_PATTERN.search(text or ""))

    @staticmethod
    def _render_session_entry(entry: dict[str, Any]) -> str:
        """Render a session entry without truncating stored text."""
        ts = entry.get("ts", "")[11:16]
        entry_type = entry.get("type", "unknown")
        text = entry.get("text", "")
        if not text:
            return ""
        return f"{ts} [{entry_type}] {text}"

    def _get_session_context(self, session_scope: int | str | None) -> str:
        """Get today's session context for the AI backend."""
        if session_scope in (0, "0", None, ""):
            return ""

        session = SessionStore(self.vault_path)
        today_entries = session.get_today(session_scope)
        if not today_entries:
            return ""

        # Берём ВЕСЬ сегодняшний день, а не последние N записей: жёсткое окно
        # обрезало утренние сообщения и было причиной «амнезии» внутри дня.
        # Чтобы очень болтливый день не раздул промпт — режем по бюджету символов,
        # сохраняя самые свежие записи (старые отбрасываем первыми).
        char_budget = 24000
        rendered_entries: list[str] = []
        for entry in reversed(today_entries):
            rendered = self._render_session_entry(entry)
            if not rendered:
                continue
            char_budget -= len(rendered)
            if char_budget < 0:
                break
            rendered_entries.append(rendered)

        lines = ["=== TODAY SESSION ===", *reversed(rendered_entries), "=== END SESSION ==="]
        return "\n".join(lines)

    @staticmethod
    def _extract_markdown_section(content: str, heading: str) -> str:
        pattern = re.compile(
            rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
            re.MULTILINE,
        )
        match = pattern.search(content)
        return match.group(0).strip() if match else ""

    def _get_work_memory_context(self) -> str:
        parts: list[str] = []

        policy_path = self.vault_path / "references" / "work-group-rules.md"
        if policy_path.exists():
            content = policy_path.read_text(encoding="utf-8", errors="ignore")[:2000]
            parts.append(f"=== {policy_path.name} ===\n{content}")

        user_path = self.vault_path / "memory" / "user.md"
        if user_path.exists():
            user_content = user_path.read_text(encoding="utf-8", errors="ignore")
            work_section = self._extract_markdown_section(user_content, "Работа")
            if work_section:
                parts.append(f"=== user.md / Работа ===\n{work_section[:1500]}")

        return "\n\n".join(parts)

    @staticmethod
    def _strip_frontmatter(content: str) -> str:
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) == 3:
                return parts[2].lstrip()
        return content

    def _read_context_file(self, path: Path, limit: int) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]

    def _build_project_catalog_context(self, limit: int = 18) -> str:
        projects_dir = self.vault_path / "thoughts" / "projects"
        if not projects_dir.exists():
            return ""

        entries: list[str] = []
        for readme in sorted(projects_dir.glob("*/README.md"))[:limit]:
            content = self._strip_frontmatter(
                readme.read_text(encoding="utf-8", errors="ignore")
            )
            title = readme.parent.name
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    title = stripped.lstrip("#").strip() or title
                    break

            body = " ".join(
                line.strip()
                for line in content.splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            )
            body = re.sub(r"\s+", " ", body)
            if len(body) > 220:
                body = body[:217].rstrip() + "..."
            entries.append(f"- {title}: {body}" if body else f"- {title}")

        if not entries:
            return ""
        return "=== PROJECT CATALOG ===\n" + "\n".join(entries)

    def _is_first_reply_today(self, session_scope: int | str | None) -> bool:
        if session_scope in (0, "0", None, ""):
            return False

        session = SessionStore(self.vault_path)
        today_entries = session.get_today(session_scope)
        return not any(entry.get("type") == "assistant" for entry in today_entries)

    def _prime_context_cache(self, work_mode: bool = False) -> str:
        return self._get_memory_context(work_mode=work_mode, cold_start=True, force=True)

    def _html_to_markdown(self, html: str) -> str:
        """Convert Telegram HTML to Obsidian Markdown."""
        import re

        text = html
        text = re.sub(r"<b>(.*?)</b>", r"**\1**", text)
        text = re.sub(r"<i>(.*?)</i>", r"*\1*", text)
        text = re.sub(r"<code>(.*?)</code>", r"`\1`", text)
        text = re.sub(r"<s>(.*?)</s>", r"~~\1~~", text)
        text = re.sub(r"</?u>", "", text)
        text = re.sub(r'<a href="([^"]+)">([^<]+)</a>', r"[\2](\1)", text)
        return text

    def _save_weekly_summary(self, report_html: str, week_date: date) -> Path:
        """Save weekly summary to vault/summaries/YYYY-WXX-summary.md."""
        year, week, _ = week_date.isocalendar()
        filename = f"{year}-W{week:02d}-summary.md"
        summary_path = self.vault_path / "summaries" / filename

        content = self._html_to_markdown(report_html)
        frontmatter = f"""---
date: {week_date.isoformat()}
type: weekly-summary
week: {year}-W{week:02d}
---

"""
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(frontmatter + content, encoding="utf-8")
        logger.info("Weekly summary saved to %s", summary_path)
        return summary_path

    def _update_weekly_moc(self, summary_path: Path) -> None:
        """Add link to a new summary in MOC-weekly.md."""
        moc_path = self.vault_path / "MOC" / "MOC-weekly.md"
        if not moc_path.exists():
            return

        content = moc_path.read_text(encoding="utf-8", errors="ignore")
        link = f"- [[summaries/{summary_path.name}|{summary_path.stem}]]"
        if summary_path.stem not in content:
            content = content.replace("## Previous Weeks\n", f"## Previous Weeks\n\n{link}\n")
            moc_path.write_text(content, encoding="utf-8")
            logger.info("Updated MOC-weekly.md with %s", summary_path.stem)

    def _get_codex_bin(self) -> str:
        """Resolve the Codex CLI binary."""
        resolved = shutil.which(self.codex_bin)
        if not resolved:
            raise RuntimeError(f"Codex CLI not found: {self.codex_bin}")
        return resolved

    @staticmethod
    def _is_claude_auth_error(exc: BaseException) -> bool:
        """Return True when Claude CLI failed because its local auth is invalid."""
        return bool(CLAUDE_AUTH_ERROR_PATTERN.search(str(exc)))

    def _persist_backend(self, backend: str) -> None:
        """Persist active backend in .env so restarts do not return to a broken sim."""
        if backend not in {"codex", "claude"}:
            raise ValueError(f"Unsupported backend: {backend}")

        try:
            content = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
            if re.search(r"^AI_BACKEND=", content, flags=re.MULTILINE):
                new_content = re.sub(
                    r"^AI_BACKEND=.*$",
                    f"AI_BACKEND={backend}",
                    content,
                    count=1,
                    flags=re.MULTILINE,
                )
            else:
                sep = "" if not content or content.endswith("\n") else "\n"
                new_content = f"{content}{sep}AI_BACKEND={backend}\n"
            ENV_PATH.write_text(new_content, encoding="utf-8")
        except OSError:
            logger.exception("Failed to persist AI_BACKEND=%s", backend)

    def _fallback_to_codex_after_claude_auth_error(
        self,
        prompt: str,
        *,
        read_only: bool,
        images: list[str] | None,
        timeout_sec: int,
        mode: str,
        error: BaseException,
    ) -> str:
        """Switch to Codex when Claude auth is broken and serve the same request."""
        logger.warning("Claude auth failed, switching AI_BACKEND to codex: %s", error)
        self.ai_backend = "codex"
        self._persist_backend("codex")
        return self._run_codex_exec(
            prompt,
            read_only=read_only,
            images=images,
            timeout_sec=timeout_sec,
            model=self._backend_model_for_mode(mode),
        )

    def _normalize_effort(self, effort: str | None) -> str:
        value = (effort or self.codex_reasoning_effort).strip().lower()
        if value not in SUPPORTED_REASONING_EFFORTS:
            return self.codex_reasoning_effort
        return value

    @staticmethod
    def _normalize_verbosity(verbosity: str | None) -> str:
        value = (verbosity or "medium").strip().lower()
        if value not in SUPPORTED_VERBOSITY:
            return "medium"
        return value

    def _build_exec_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        read_only: bool,
    ) -> str:
        mode = "read-only" if read_only else "workspace-write"
        return (
            f"{system_prompt}\n\n"
            "Execution constraints:\n"
            f"- Run inside project root: {self.project_path.as_posix()}\n"
            f"- Sandbox expectation: {mode}\n"
            "- Reply in Russian.\n"
            "- Return only the final answer for the user, without tool logs or extra commentary.\n\n"
            "Internet tools:\n"
            "- Internet access is available.\n"
            "- For web search ALWAYS run (do not use built-in web tools): "
            "`uv run python scripts/web_search.py \"query\" --max-results 5`.\n"
            "- To read a page by URL, run: "
            "`uv run python scripts/web_fetch.py \"https://example.com\"`.\n"
            "- These scripts use the direct server-IP web/browser contour from "
            "`direct_web/` and must be preferred over inherited proxy/browser tools.\n"
            "- Use web access for current facts, prices, schedules, docs, "
            "product pages, and links.\n"
            "- NEVER claim «не могу / нет доступа / не получится» without actually "
            "trying at least one tool (web_search, web_fetch, Bash) first. If a tool "
            "failed — say which one and what the error was, then suggest the next step.\n\n"
            f"{user_prompt.strip()}\n"
        )

    def _run_codex_exec(
        self,
        prompt: str,
        *,
        read_only: bool,
        images: list[str] | None = None,
        timeout_sec: int = 600,
        model: str | None = None,
    ) -> str:
        """Run Codex CLI and return its final message."""
        codex_bin = self._get_codex_bin()
        codex_model = (model or "").strip() or self.codex_model
        with tempfile.TemporaryDirectory(prefix="dbrain-codex-") as temp_dir:
            output_file = Path(temp_dir) / "last-message.txt"
            cmd = [
                codex_bin,
                "exec",
                "--skip-git-repo-check",
                "--color",
                "never",
                "--cd",
                str(self.project_path),
                "--output-last-message",
                str(output_file),
                "--model",
                codex_model,
            ]

            sandbox_mode = self.codex_sandbox_mode
            if read_only and sandbox_mode == "workspace-write":
                sandbox_mode = "read-only"

            if sandbox_mode == "bypass":
                cmd.append("--dangerously-bypass-approvals-and-sandbox")
            elif sandbox_mode in {"read-only", "workspace-write", "danger-full-access"}:
                cmd.extend(["--sandbox", sandbox_mode])
                if not read_only and sandbox_mode == "workspace-write":
                    cmd.append("--full-auto")
            else:
                raise RuntimeError(f"Unsupported CODEX_SANDBOX_MODE: {self.codex_sandbox_mode}")

            for image in images or []:
                cmd.extend(["-i", image])

            cmd.append("-")

            env = os.environ.copy()
            env.pop("OPENAI_API_KEY", None)

            result = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                cwd=self.project_path,
                env=env,
                timeout=timeout_sec,
                check=False,
            )

            final_text = ""
            if output_file.exists():
                final_text = output_file.read_text(encoding="utf-8", errors="ignore").strip()
            if not final_text:
                final_text = (result.stdout or "").strip()

            if result.returncode != 0:
                details = (result.stderr or result.stdout or "codex exec failed").strip()
                raise RuntimeError(details.splitlines()[-1] if details else "codex exec failed")

            if not final_text:
                raise RuntimeError("codex exec returned an empty response")

            return final_text

    def _get_claude_bin(self) -> str:
        """Resolve the Claude Code CLI binary."""
        resolved = shutil.which(self.claude_bin)
        if not resolved:
            # Fallback: попробовать стандартное место установки под пользователем
            home_local = Path(os.path.expanduser("~/.local/bin/claude"))
            if home_local.exists():
                return str(home_local)
            raise RuntimeError(f"Claude CLI not found: {self.claude_bin}")
        return resolved

    def _run_claude_exec(
        self,
        prompt: str,
        *,
        read_only: bool,
        images: list[str] | None = None,
        timeout_sec: int = 600,
        model: str | None = None,
    ) -> str:
        """Run Claude Code CLI in --print mode and return its final message.

        Used when AI_BACKEND=claude. Uses the local Claude Code subscription
        (no API key); auth is managed by the `claude` binary itself.
        """
        claude_bin = self._get_claude_bin()
        claude_model = (model or "").strip() or self.claude_model
        permission_mode = "default" if read_only else "bypassPermissions"
        cmd = [
            claude_bin,
            "-p",
            "--model", claude_model,
            "--effort", self.claude_effort,
            "--permission-mode", permission_mode,
            "--add-dir", str(self.vault_path),
            "--output-format", "text",
            "--no-session-persistence",
        ]

        # Images: Claude CLI принимает их как @-references прямо в промпте.
        if images:
            image_refs = "\n".join(f"@{img}" for img in images)
            prompt = f"{image_refs}\n\n{prompt}"

        env = os.environ.copy()
        # Подписка Claude Max — не пускаем ANTHROPIC_API_KEY если случайно есть.
        env.pop("ANTHROPIC_API_KEY", None)

        result = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=self.project_path,
            env=env,
            timeout=timeout_sec,
            check=False,
        )

        if result.returncode != 0:
            details = (result.stderr or result.stdout or "claude exec failed").strip()
            raise RuntimeError(details.splitlines()[-1] if details else "claude exec failed")

        final_text = (result.stdout or "").strip()
        if not final_text:
            raise RuntimeError("claude exec returned an empty response")

        return final_text

    def _backend_model_for_mode(self, mode: str) -> str:
        """Pick the model for current backend based on mode (chat | agent)."""
        if self.ai_backend == "claude":
            return self.claude_model_chat if mode == "chat" else self.claude_model_agent
        return self.codex_model_chat if mode == "chat" else self.codex_model_agent

    def _run_backend_exec(
        self,
        prompt: str,
        *,
        read_only: bool,
        images: list[str] | None = None,
        timeout_sec: int = 600,
        mode: str = "chat",
    ) -> str:
        """Dispatch to active AI backend (codex or claude) based on AI_BACKEND.

        `mode` selects the model:
          - "chat"  → light/fast model for dialog (Sonnet on Claude, default on Codex)
          - "agent" → heavy/capable model for processing (Opus on Claude)
        """
        model = self._backend_model_for_mode(mode)
        if self.ai_backend == "claude":
            try:
                return self._run_claude_exec(
                    prompt,
                    read_only=read_only,
                    images=images,
                    timeout_sec=timeout_sec,
                    model=model,
                )
            except RuntimeError as exc:
                if self._is_claude_auth_error(exc):
                    return self._fallback_to_codex_after_claude_auth_error(
                        prompt,
                        read_only=read_only,
                        images=images,
                        timeout_sec=timeout_sec,
                        mode=mode,
                        error=exc,
                    )
                raise
        return self._run_codex_exec(
            prompt,
            read_only=read_only,
            images=images,
            timeout_sec=timeout_sec,
            model=model,
        )

    def _run_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        reasoning: str | None = None,
        verbosity: str | None = None,
        max_output_tokens: int = 2000,
        timeout_sec: int = CHAT_TIMEOUT_SECONDS,
    ) -> str:
        """Dialog / chat request → chat model (см. CLAUDE_MODEL_CHAT).

        Тайм-аут диалога — CHAT_TIMEOUT_SECONDS: если модель не ответила,
        это затык (rate limit Claude Max / сетевой блип / API проблема).
        Подвисания рандомны (то 9 сек, то висит до упора), поэтому после
        первого фейла делаем один быстрый повтор с коротким бюджетом —
        обычно он спасает ответ. После второго фейла — исключение наружу,
        хендлер покажет пользователю честную ошибку.
        """
        del reasoning, verbosity, max_output_tokens
        # 2026-05-11: чат-сессия больше не read-only. С момента перехода на pure Opus
        # (2026-05-10) обычный диалог тоже должен уметь ходить на Барыгу, запускать
        # скрипты, читать сетевые ресурсы. read_only=True оставался legacy от
        # Sonnet-чата и блокировал --permission-mode → default → Bash недоступен в
        # subprocess --print. Возвращать True имеет смысл только если снова разделить
        # light/heavy и вернуть привратника.
        prompt = self._build_exec_prompt(system_prompt, user_prompt, read_only=False)
        with _claude_chat_lock():
            try:
                return self._run_backend_exec(
                    prompt,
                    read_only=False,
                    timeout_sec=timeout_sec,
                    mode="chat",
                )
            except (subprocess.TimeoutExpired, RuntimeError) as exc:
                retry_timeout = min(600, timeout_sec)
                logger.warning(
                    "chat exec failed (%s) — one retry with %ss budget",
                    type(exc).__name__,
                    retry_timeout,
                )
                return self._run_backend_exec(
                    prompt,
                    read_only=False,
                    timeout_sec=retry_timeout,
                    mode="chat",
                )

    def _run_agent(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        read_only: bool = False,
        reasoning: str | None = None,
        verbosity: str | None = None,
        max_output_tokens: int = 2500,
    ) -> str:
        """Agent / processing request → heavy model (Opus on Claude). Per v3."""
        del reasoning, verbosity, max_output_tokens
        prompt = self._build_exec_prompt(system_prompt, user_prompt, read_only=read_only)
        with _claude_heavy_lock():
            return self._run_backend_exec(
                prompt,
                read_only=read_only,
                timeout_sec=900 if not read_only else 600,
                mode="agent",
            )

    def analyze_image(self, image_path: str, caption: str | None = None) -> str | None:
        """Analyze an image via active backend CLI subprocess.

        2026-06-11: SDK-ветка удалена — `anthropic.Anthropic()` требует API-ключ,
        которого при подписке Claude Max нет, поэтому она всегда молча падала в
        CLI-фоллбэк (лишняя задержка + ложная ошибка в логах). CLI-путь работает
        по подписке и для Claude, и для Codex (диспетчеризация в _run_backend_exec).
        """
        image_file = Path(image_path)
        if not image_file.exists():
            return None

        return self._analyze_image_cli(image_file, caption)

    @staticmethod
    def _vision_prompt(caption: str | None) -> str:
        prompt = (
            "Опиши что на изображении. "
            "Если есть текст — извлеки его полностью (OCR). "
            "Если это скриншот, документ или заметка — передай содержание. "
            "Если это фото — опиши кратко что изображено. "
            "Отвечай на русском, кратко и по делу."
        )
        if caption:
            prompt += f"\n\nПодпись: {caption}"
        return prompt

    def _analyze_image_cli(self, image_file: Path, caption: str | None) -> str | None:
        """Vision через CLI subprocess активного бэкенда (Claude или Codex)."""
        try:
            return self._run_backend_exec(
                self._vision_prompt(caption),
                read_only=True,
                images=[str(image_file)],
                timeout_sec=300,
                mode="chat",
            )
        except Exception:
            logger.exception("Vision analysis via CLI subprocess failed")
            return None

    def web_quick_summary(self, query: str, results_block: str, timeout_sec: int = 90) -> str | None:
        """Короткая выжимка результатов веб-поиска для fast-path (/web и интент).

        Лёгкий вызов: fable, без инструментов, cwd во временной папке — CLAUDE.md
        проекта НЕ подхватывается, память и правила не грузятся, в промпте только
        результаты поиска. Идёт через claude fable напрямую, поэтому работает на
        ОБЕИХ симках (бинарь claude есть независимо от AI_BACKEND). Best effort:
        любой фейл → None (карточки уже отправлены, выжимка — необязательный бонус).
        """
        prompt = (
            f"Вопрос пользователя: {query}\n\n"
            f"Результаты веб-поиска:\n{results_block}\n\n"
            "Дай выжимку ответа в 2–4 предложениях на русском строго по этим "
            "результатам. В конце одной строкой укажи 1–2 самые полезные ссылки. "
            "Без вступлений и оговорок."
        )
        try:
            claude_bin = self._get_claude_bin()
            env = os.environ.copy()
            env.pop("ANTHROPIC_API_KEY", None)
            with tempfile.TemporaryDirectory(prefix="dbrain-web-") as temp_dir:
                result = subprocess.run(
                    [
                        claude_bin,
                        "-p",
                        "--model", "fable",
                        "--output-format", "text",
                        "--no-session-persistence",
                    ],
                    input=prompt,
                    text=True,
                    capture_output=True,
                    cwd=temp_dir,
                    env=env,
                    timeout=timeout_sec,
                    check=False,
                )
            if result.returncode != 0:
                logger.warning("web_quick_summary failed: %s", (result.stderr or "")[-200:])
                return None
            return (result.stdout or "").strip() or None
        except Exception:
            logger.exception("web_quick_summary failed")
            return None

    def _tool_schemas(self, *, read_only: bool) -> list[dict[str, Any]]:
        """Return OpenAI function tool schemas."""
        schemas: list[dict[str, Any]] = [
            {
                "type": "function",
                "name": "list_files",
                "description": "List files and directories under a path inside the project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path relative to project root."},
                        "max_depth": {"type": "integer", "minimum": 1, "maximum": 8},
                        "max_entries": {"type": "integer", "minimum": 1, "maximum": 500},
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "read_file",
                "description": "Read a UTF-8 text file inside the project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path relative to project root."},
                        "max_chars": {"type": "integer", "minimum": 200, "maximum": 40000},
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "search_memory",
                "description": "Search indexed memory facts in the local SQLite RAG cache.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "todoist_get_projects",
                "description": "Get Todoist projects visible to the current API token.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "todoist_search_tasks",
                "description": "Search active Todoist tasks by text in content or description.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "todoist_get_completed_tasks",
                "description": "Get completed Todoist tasks within an ISO datetime range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "since_iso": {"type": "string"},
                        "until_iso": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    "required": ["since_iso", "until_iso"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        ]

        if read_only:
            return schemas

        schemas.extend(
            [
                {
                    "type": "function",
                    "name": "write_file",
                    "description": "Write a UTF-8 text file inside the project, creating parent directories.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path relative to project root."},
                            "content": {"type": "string"},
                        },
                        "required": ["path", "content"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
                {
                    "type": "function",
                    "name": "append_file",
                    "description": "Append UTF-8 text to a file inside the project.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path relative to project root."},
                            "content": {"type": "string"},
                        },
                        "required": ["path", "content"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
                {
                    "type": "function",
                    "name": "todoist_add_task",
                    "description": "Create a Todoist task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "description": {"type": "string"},
                            "due_string": {"type": "string"},
                            "priority": {"type": "integer", "minimum": 1, "maximum": 4},
                        },
                        "required": ["content"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
                {
                    "type": "function",
                    "name": "todoist_update_task",
                    "description": "Update an existing Todoist task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "content": {"type": "string"},
                            "description": {"type": "string"},
                            "due_string": {"type": "string"},
                            "priority": {"type": "integer", "minimum": 1, "maximum": 4},
                        },
                        "required": ["task_id"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
                {
                    "type": "function",
                    "name": "todoist_complete_task",
                    "description": "Mark a Todoist task as completed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                        },
                        "required": ["task_id"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            ]
        )
        return schemas

    def _dispatch_tool(self, name: str, raw_arguments: str | None) -> str:
        """Dispatch a tool call and return JSON text."""
        try:
            arguments = json.loads(raw_arguments) if raw_arguments else {}
        except json.JSONDecodeError as exc:
            return json.dumps({"ok": False, "error": f"Invalid tool arguments: {exc}"}, ensure_ascii=False)

        try:
            if name == "list_files":
                result = self._tool_list_files(**arguments)
            elif name == "read_file":
                result = self._tool_read_file(**arguments)
            elif name == "write_file":
                result = self._tool_write_file(**arguments)
            elif name == "append_file":
                result = self._tool_append_file(**arguments)
            elif name == "search_memory":
                result = self._tool_search_memory(**arguments)
            elif name == "todoist_get_projects":
                result = self._tool_todoist_get_projects()
            elif name == "todoist_search_tasks":
                result = self._tool_todoist_search_tasks(**arguments)
            elif name == "todoist_get_completed_tasks":
                result = self._tool_todoist_get_completed_tasks(**arguments)
            elif name == "todoist_add_task":
                result = self._tool_todoist_add_task(**arguments)
            elif name == "todoist_update_task":
                result = self._tool_todoist_update_task(**arguments)
            elif name == "todoist_complete_task":
                result = self._tool_todoist_complete_task(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as exc:
            logger.exception("Tool %s failed", name)
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

        return json.dumps({"ok": True, "result": result}, ensure_ascii=False)

    def _resolve_path(self, raw_path: str) -> Path:
        """Resolve a relative path and keep it inside the project root."""
        candidate = Path(raw_path)
        if candidate.is_absolute():
            resolved = candidate.resolve()
        else:
            resolved = (self.project_path / candidate).resolve()

        if resolved != self.project_path and self.project_path not in resolved.parents:
            raise ValueError(f"Path is outside the project: {raw_path}")
        return resolved

    def _tool_list_files(
        self,
        path: str,
        max_depth: int = 3,
        max_entries: int = 200,
    ) -> dict[str, Any]:
        target = self._resolve_path(path)
        if not target.exists():
            raise FileNotFoundError(path)

        if target.is_file():
            rel = str(target.relative_to(self.project_path).as_posix())
            return {"root": rel, "items": [{"path": rel, "type": "file"}], "truncated": False}

        items: list[dict[str, str]] = []
        truncated = False
        for entry in sorted(target.rglob("*")):
            rel_to_target = entry.relative_to(target)
            if len(rel_to_target.parts) > max_depth:
                continue
            if any(part in SKIP_DIR_NAMES for part in rel_to_target.parts):
                continue
            items.append(
                {
                    "path": str(entry.relative_to(self.project_path).as_posix()),
                    "type": "dir" if entry.is_dir() else "file",
                }
            )
            if len(items) >= max_entries:
                truncated = True
                break

        return {
            "root": str(target.relative_to(self.project_path).as_posix()),
            "items": items,
            "truncated": truncated,
        }

    def _tool_read_file(self, path: str, max_chars: int = 12000) -> dict[str, Any]:
        target = self._resolve_path(path)
        if not target.exists():
            raise FileNotFoundError(path)
        if not target.is_file():
            raise IsADirectoryError(path)

        content = target.read_text(encoding="utf-8", errors="ignore")
        truncated = len(content) > max_chars
        if truncated:
            content = content[:max_chars]

        return {
            "path": str(target.relative_to(self.project_path).as_posix()),
            "content": content,
            "truncated": truncated,
        }

    def _tool_write_file(self, path: str, content: str) -> dict[str, Any]:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "path": str(target.relative_to(self.project_path).as_posix()),
            "bytes": len(content.encode("utf-8")),
        }

    def _tool_append_file(self, path: str, content: str) -> dict[str, Any]:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        prefix = ""
        if target.exists():
            existing = target.read_text(encoding="utf-8", errors="ignore")
            if existing and not existing.endswith("\n"):
                prefix = "\n"

        with target.open("a", encoding="utf-8") as handle:
            handle.write(prefix + content)

        return {
            "path": str(target.relative_to(self.project_path).as_posix()),
            "bytes_appended": len((prefix + content).encode("utf-8")),
        }

    def _tool_search_memory(self, query: str, limit: int = 5) -> dict[str, Any]:
        from d_brain.services.memory_rag import search_memory

        return {"query": query, "results": search_memory(query, limit=limit)}

    def _get_todoist_api(self) -> Any:
        if not self.todoist_api_key:
            raise RuntimeError("TODOIST_API_KEY is not set")

        from todoist_api_python.api import TodoistAPI

        return TodoistAPI(self.todoist_api_key)

    @staticmethod
    def _task_to_dict(task: Any) -> dict[str, Any]:
        due = getattr(task, "due", None)
        due_data = None
        if due is not None:
            due_data = {
                "date": getattr(due, "date", None),
                "string": getattr(due, "string", None),
                "datetime": getattr(due, "datetime", None),
                "timezone": getattr(due, "timezone", None),
            }

        return {
            "id": getattr(task, "id", ""),
            "content": getattr(task, "content", ""),
            "description": getattr(task, "description", ""),
            "priority": getattr(task, "priority", 1),
            "project_id": getattr(task, "project_id", None),
            "section_id": getattr(task, "section_id", None),
            "labels": list(getattr(task, "labels", []) or []),
            "is_completed": getattr(task, "is_completed", False),
            "due": due_data,
            "url": getattr(task, "url", None),
        }

    @staticmethod
    def _project_to_dict(project: Any) -> dict[str, Any]:
        return {
            "id": getattr(project, "id", ""),
            "name": getattr(project, "name", ""),
            "color": getattr(project, "color", ""),
            "is_inbox_project": getattr(project, "is_inbox_project", False),
            "is_shared": getattr(project, "is_shared", False),
            "url": getattr(project, "url", None),
        }

    def _flatten_task_pages(self, pages: Any, limit: int) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in pages:
            for task in page:
                items.append(self._task_to_dict(task))
                if len(items) >= limit:
                    return items
        return items

    def _tool_todoist_get_projects(self) -> dict[str, Any]:
        api = self._get_todoist_api()
        projects = api.get_projects()
        return {"projects": [self._project_to_dict(project) for project in projects]}

    def _tool_todoist_search_tasks(self, query: str, limit: int = 20) -> dict[str, Any]:
        api = self._get_todoist_api()
        pages = api.get_tasks(limit=min(max(limit, 1), 100))
        tasks = self._flatten_task_pages(pages, min(max(limit, 1), 100))

        lowered = query.casefold()
        matched = [
            task for task in tasks
            if lowered in (task["content"] or "").casefold()
            or lowered in (task["description"] or "").casefold()
        ]
        return {"tasks": matched[:limit]}

    def _tool_todoist_get_completed_tasks(
        self,
        since_iso: str,
        until_iso: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        api = self._get_todoist_api()
        since = datetime.fromisoformat(since_iso)
        until = datetime.fromisoformat(until_iso)
        pages = api.get_completed_tasks_by_completion_date(since=since, until=until, limit=limit)
        return {"tasks": self._flatten_task_pages(pages, limit)}

    def _tool_todoist_add_task(
        self,
        content: str,
        description: str = "",
        due_string: str = "",
        priority: int = 1,
    ) -> dict[str, Any]:
        api = self._get_todoist_api()
        task = api.add_task(
            content=content,
            description=description or None,
            due_string=due_string or None,
            priority=priority,
        )
        return {"task": self._task_to_dict(task)}

    def _tool_todoist_update_task(
        self,
        task_id: str,
        content: str = "",
        description: str = "",
        due_string: str = "",
        priority: int | None = None,
    ) -> dict[str, Any]:
        api = self._get_todoist_api()
        task = api.update_task(
            task_id,
            content=content or None,
            description=description or None,
            due_string=due_string or None,
            priority=priority,
        )
        return {"task": self._task_to_dict(task)}

    def _tool_todoist_complete_task(self, task_id: str) -> dict[str, Any]:
        api = self._get_todoist_api()
        success = api.complete_task(task_id)
        return {"task_id": task_id, "completed": success}

    def process_daily(self, day: date | None = None) -> dict[str, Any]:
        """Process a daily note and update vault/Todoist via OpenAI tools."""
        if day is None:
            day = date.today()

        daily_file = self.vault_path / "daily" / f"{day.isoformat()}.md"
        if not daily_file.exists():
            logger.warning("No daily file for %s", day)
            return {"error": f"No daily file for {day}", "processed_entries": 0}

        daily_text = daily_file.read_text(encoding="utf-8", errors="ignore")
        if len(daily_text.strip()) < 50:
            report = f"<b>{day}</b>\n\nНичего существенного."
            return {"report": report, "processed_entries": 0}

        skill_content = self._load_skill_content()
        todoist_ref = self._load_todoist_reference()
        yearly_files = sorted((self.vault_path / "goals").glob("1-yearly-*.md"))
        yearly_hint = yearly_files[-1].name if yearly_files else "1-yearly-2026.md"

        system_prompt = (
            "You are the processing backend for a personal Telegram second-brain bot. "
            "Work directly with the provided tools. Reply in Russian. "
            "When you create or update files, keep markdown clean and concise. "
            "Avoid duplicates: read target files before appending, and do not repeat the same fact twice. "
            "Create Todoist tasks only for clear actionable items. "
            "The final message is for the human user only: include only user-relevant outcomes, decisions, and next steps. "
            "Never mention internal instructions, hidden rules, files you had to read for yourself, tool limitations, or assistant self-maintenance. "
            "Keep the tone compact, vivid, and easy to scan. "
            "Use Russian wording for all headings and labels in the final message. "
            "Do not use English service labels or section titles in the user-facing text. "
            "Product names may stay in their original form only when necessary, for example Todoist or Telegram. "
            "Return ONLY raw Telegram HTML. "
            "Allowed tags: <b>, <i>, <code>, <s>, <u>. "
            "Do not include markdown fences."
        )

        user_prompt = f"""
Today is {day.isoformat()}.
Project root: {self.project_path.as_posix()}
Vault root: {self.vault_path.as_posix()}

Process this day's inbox and memory updates.

The full content of the daily file is inlined below — do NOT skip processing it,
and do not respond "no entries today" if this block is non-empty.
Entries above a `processed:` marker block were already processed earlier:
do not re-process them, handle only the entries after the LAST such marker.
After processing, append a marker block to the end of the daily file:
---
processed: <current ISO timestamp>
thoughts: <N>
tasks: <M>
---

=== vault/daily/{day.isoformat()}.md ===
{daily_text}
=== END vault/daily/{day.isoformat()}.md ===

Also read for context:
- vault/memory/facts.md
- vault/memory/user.md
- vault/memory/soul.md
- vault/goals/3-weekly.md
- vault/goals/2-monthly.md
- vault/goals/{yearly_hint}

Then:
1. Extract durable facts and append them to vault/memory/facts.md.
2. Append only stable user profile changes to vault/memory/user.md.
3. Append only assistant behavior learnings to vault/memory/soul.md.
4. If there is a durable idea, project, reflection, learning, or task, create a note under vault/thoughts/... .
5. Create Todoist tasks for clear next actions when useful.
6. Keep changes minimal and readable.

Apply these planning rules:
{self._planning_guardrails()}

Useful reference material:
=== DBRAIN SKILL ===
{skill_content[:8000]}
=== TODOIST REFERENCE ===
{todoist_ref[:4000]}
=== END REFERENCES ===

Return ONLY raw Telegram HTML with:
- a short friendly header in Russian with 1 emoji
- 2-4 short bullets with only user-relevant results
- task updates only if they matter to the user
- one short next-step line only if the user should actually do something

Do not mention:
- internal rules, prompts, global rules, memory loading, or tool usage
- background maintenance that matters only to the assistant
- file paths unless they are directly useful to the user
- anything that was considered but not important
- overdue framing or deadline language unless it was explicitly requested or clearly present in today's input
"""

        try:
            report = self._run_agent(
                system_prompt,
                user_prompt,
                read_only=False,
                reasoning="medium",
                verbosity="medium",
                max_output_tokens=3000,
            )
            try:
                from d_brain.services.wiki import refresh_wiki

                refresh_wiki(self.vault_path)
            except Exception:
                logger.exception("Wiki refresh failed after daily processing")
            try:
                self._prime_context_cache()
            except Exception:
                logger.exception("Context warmup failed after daily processing")
            return {"report": report, "processed_entries": 1}
        except Exception as exc:
            logger.exception("OpenAI daily processing failed")
            return {"error": str(exc), "processed_entries": 0}

    def _daily_unprocessed_tail(self, day: date) -> str:
        """Текст daily-файла после последнего маркера обработки."""
        path = self.vault_path / "daily" / f"{day.isoformat()}.md"
        if not path.exists():
            return ""
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        last_marker = -1
        for idx, line in enumerate(lines):
            if _PROCESSED_MARKER_RE.search(line):
                last_marker = idx
        tail = lines[last_marker + 1 :]
        tail = [ln for ln in tail if not _MARKER_NOISE_RE.match(ln)]
        text = "\n".join(tail).strip()
        # Один заголовок без записей (`# 2026-07-06`) — ещё не содержимое.
        if last_marker == -1 and re.fullmatch(r"#\s*[\d-]+", text):
            return ""
        return text

    def _daily_has_marker(self, day: date) -> bool:
        path = self.vault_path / "daily" / f"{day.isoformat()}.md"
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8", errors="ignore")
        return any(
            _PROCESSED_MARKER_RE.search(line) for line in content.splitlines()
        )

    def pending_days(self, today: date | None = None) -> list[date]:
        """Дни с записями после последнего маркера обработки, от старых к новым.

        Отсчёт идёт «от обработки до обработки»: только дни начиная с последнего
        дня, где маркер уже есть. Дни до эпохи маркеров не перелопачиваем заново.
        """
        if today is None:
            today = date.today()
        last_marked = today
        for offset in range(_PENDING_LOOKBACK_DAYS + 1):
            day = today - timedelta(days=offset)
            if self._daily_has_marker(day):
                last_marked = day
                break
        days = []
        day = last_marked
        while day <= today:
            if len(self._daily_unprocessed_tail(day)) >= 10:
                days.append(day)
            day += timedelta(days=1)
        return days

    def _mark_daily_processed(self, day: date) -> None:
        """Дописать маркер обработки, если агент не оставил свой."""
        if not self._daily_unprocessed_tail(day):
            return
        path = self.vault_path / "daily" / f"{day.isoformat()}.md"
        stamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n---\nprocessed: {stamp}\nthoughts: -\ntasks: -\n---\n")

    def process_pending(self, today: date | None = None) -> dict[str, Any]:
        """Обработать все дни с необработанными записями — «от обработки до обработки».

        Кнопка могла не нажиматься несколько дней: пройти хвосты всех daily-файлов
        после их последнего маркера обработки, а не только сегодняшний день.
        """
        if today is None:
            today = date.today()
        days = self.pending_days(today)
        if not days:
            # Всё уже обработано — обычный статус-отчёт за сегодня.
            return self.process_daily(today)

        reports: list[str] = []
        errors: list[str] = []
        processed = 0
        for day in days:
            result = self.process_daily(day)
            if "error" in result:
                errors.append(f"{day.isoformat()}: {result['error']}")
                continue
            processed += int(result.get("processed_entries", 0))
            text = str(result.get("report", "")).strip()
            if text:
                reports.append(text)
            self._mark_daily_processed(day)

        if not reports and errors:
            return {"error": "; ".join(errors), "processed_entries": processed}
        report = "\n\n".join(reports)
        if errors:
            report += "\n\n⚠️ <b>Не обработано:</b> " + "; ".join(errors)
        return {
            "report": report,
            "processed_entries": processed,
            "days": [d.isoformat() for d in days],
        }

    def execute_prompt(
        self,
        user_prompt: str,
        user_id: int = 0,
        *,
        session_scope: int | str | None = None,
        work_context: bool = False,
    ) -> dict[str, Any]:
        """Execute an arbitrary user request with tools and HTML output."""
        today = date.today().isoformat()
        todoist_ref = self._load_todoist_reference()
        memory_context = self._get_memory_context(
            work_mode=work_context,
            cold_start=self._is_first_reply_today(session_scope or user_id),
        )
        session_context = self._get_session_context(session_scope or user_id)

        rag_context = ""
        try:
            from d_brain.services.memory_rag import search_memory

            relevant = search_memory(user_prompt, limit=5)
            if relevant:
                rag_context = f"\n=== MEMORY SEARCH ===\n{relevant}\n"
        except Exception:
            rag_context = ""

        system_prompt = (
            "You are the action backend for a personal Telegram second-brain bot. "
            "You have tools for local project files and Todoist. "
            "Reply in Russian. Act directly, keep changes inside the project, and be concise. "
            "The final message is for the user, not for developers: hide internal reasoning, rule-following, file-reading steps, and assistant-only maintenance. "
            "Mention only what affects the user: result and meaningful changes. "
            "Use an adaptive tone depending on context instead of one fixed style. "
            "For reminders and nudges, sound warm, supportive, and light. "
            "For completed actions and results, sound clear, confident, and compact. "
            "For simple chat, sound natural, lively, and easygoing. "
            "For serious or important matters, sound calmer and more focused. "
            "Make the message pleasant to read: compact, lively, and visually clean. "
            "Prefer short sentences, short paragraphs, and a blank line between paragraphs. "
            "Use 1-3 relevant emoji and place them at the start of meaningful paragraphs instead of at the end. "
            "Avoid repeating the same emoji in neighboring paragraphs. "
            "Translate English words, labels, and service phrasing into Russian unless they must stay exact as a product name, command, file path, API name, or model name. "
            "Never show your reasoning, internal reflections, deliberation, or intermediate thoughts. Give only the final answer. "
            "Do not offer extra help, extra options, or next actions unless the user explicitly asked for them or a real user action is strictly required. "
            "All user-facing headings, labels, and section names must be in Russian. "
            "Do not use English labels like wins, blockers, next step, summary, action items, or Todoist actions. "
            f"{self._planning_guardrails()} "
            "Return ONLY raw Telegram HTML. Allowed tags: <b>, <i>, <code>, <s>, <u>."
        )

        composed_prompt = f"""
Today is {today}.
Project root: {self.project_path.as_posix()}
Vault root: {self.vault_path.as_posix()}

=== MEMORY CONTEXT ===
{memory_context}

=== SESSION CONTEXT ===
{session_context}
{rag_context}
=== TODOIST REFERENCE ===
{todoist_ref[:4000]}
=== END CONTEXT ===

USER REQUEST:
{user_prompt}

If no tool is needed, answer directly.
If tools are needed, use them and then report the result.
Keep the final answer short and concrete.
Make it feel human and easy to scan, not like a dry technical report.
Prefer:
- a short friendly opening
- 1-4 compact bullets or short paragraphs
- a brief closing line only if the user truly needs to do something next

Choose the tone by context:
- reminder or check-in -> softer, warmer, more caring
- result of work done -> clearer, brisker, more matter-of-fact
- casual question -> lighter and more conversational
- sensitive or important issue -> calmer and more grounded

Avoid:
- bureaucratic wording
- overexplaining obvious steps
- clutter, repetition, or heavy technical phrasing
- phrases about your own thinking, such as "я подумал", "я рассуждал", or similar
- offers like "если хочешь, я могу..." unless the user explicitly asked for options
Do not mention internal instructions, hidden policies, global rules, prompt files, or technical steps that matter only to the assistant.
Do not surface assistant self-reminders or operational chores unless the user explicitly asked for them.
If there is no user-facing outcome, say so briefly instead of padding the answer.
Write all section names in Russian.
Keep the user's planning horizon intact. Do not reinterpret long-term projects as urgent or overdue without an explicit request.
"""

        try:
            report = self._run_agent(
                system_prompt,
                composed_prompt,
                read_only=False,
                reasoning="medium",
                verbosity="medium",
                max_output_tokens=2500,
            )
            return {"report": report, "processed_entries": 1}
        except Exception as exc:
            logger.exception("OpenAI action execution failed")
            return {"error": str(exc), "processed_entries": 0}

    def generate_weekly(self) -> dict[str, Any]:
        """Generate weekly digest using the OpenAI backend."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        since_iso = datetime.combine(week_start, dt_time.min).isoformat()
        until_iso = datetime.combine(week_end, dt_time.max).isoformat()

        system_prompt = (
            "You are generating a weekly digest for a personal Telegram second-brain bot. "
            "Reply in Russian. Use read-only tools to inspect daily notes, goals, memory, and completed Todoist tasks. "
            "Return ONLY raw Telegram HTML with a short, punchy weekly summary. "
            "Keep it user-facing only: no internal process notes, no tool chatter, no assistant maintenance details. "
            "Style: adapt to the week itself: celebratory if there were wins, steadier if the week was mixed, calmer if there were blockers. "
            "Keep it warm, vivid, and easy to skim, with a couple of tasteful emoji if useful. "
            f"{self._planning_guardrails()} "
            "All headings and labels in the final text must be in Russian."
        )
        user_prompt = f"""
Today is {today.isoformat()}.
Current ISO week: {today.isocalendar().year}-W{today.isocalendar().week:02d}
Project root: {self.project_path.as_posix()}
Vault root: {self.vault_path.as_posix()}

Read the relevant weekly files and produce a digest.
At minimum, inspect:
- vault/goals/3-weekly.md
- vault/goals/2-monthly.md
- the latest vault/goals/1-yearly-*.md
- daily files from {week_start.isoformat()} to {week_end.isoformat()}
- completed Todoist tasks via todoist_get_completed_tasks with:
  since_iso={since_iso}
  until_iso={until_iso}

Return ONLY raw Telegram HTML with:
- победы
- препятствия
- прогресс по целям
- фокус на следующую неделю

Important:
- do not present long-horizon projects as next-week commitments unless the current week's notes explicitly made them active
- do not use overdue framing just because an old planning file mentions something
"""

        try:
            report = self._run_agent(
                system_prompt,
                user_prompt,
                read_only=True,
                reasoning="medium",
                verbosity="medium",
                max_output_tokens=2500,
            )
            summary_path = self._save_weekly_summary(report, today)
            self._update_weekly_moc(summary_path)
            return {"report": report, "processed_entries": 1}
        except Exception as exc:
            logger.exception("OpenAI weekly digest failed")
            return {"error": str(exc), "processed_entries": 0}

    @staticmethod
    def needs_agent(response: str) -> bool:
        """Check if a response requests escalation."""
        return bool(AGENT_MARKER_PATTERN.match(response or ""))

    @staticmethod
    def strip_agent_marker(response: str) -> str:
        """Strip the escalation marker from a response."""
        cleaned = AGENT_MARKER_PATTERN.sub("", (response or ""), count=1)
        return cleaned.strip()

    def classify_message_weight(self, text: str, session_scope: int | str | None) -> str:
        """LLM-based pre-classification: 'light' (Sonnet handles directly) or 'heavy' (needs Opus).
        Uses the last 20 session entries as context (already loaded by _get_session_context).
        Minimal prompt, no memory/RAG/CLAUDE.md — short call, 10-sec timeout. Defaults to 'light'."""
        if not text or not text.strip():
            return "light"
        session_context = self._get_session_context(session_scope) if session_scope is not None else ""
        prompt = (
            "Ты — внутренний классификатор сообщений в Telegram-боте. "
            "По истории диалога и текущему сообщению пользователя реши, "
            "может ли быстрая модель (Sonnet) ответить сама, или нужен тяжёлый агент (Opus).\n\n"
            "light — простой вопрос, болтовня, статус, ответ на вопрос о возможности, короткое уточнение, "
            "отсылка к фактам без выполнения работы. Sonnet справится за один заход без работы с тулзами.\n"
            "heavy — нужно выполнить работу: разобрать/сравнить/проанализировать данные, изменить файлы или "
            "конфиги, ходить на удалённый сервер, читать большие наборы файлов, продолжать ранее начатую "
            "сложную задачу из контекста диалога (если в контексте уже шла такая работа). Нужен Opus.\n\n"
            f"{session_context}\n\n"
            f"=== ТЕКУЩЕЕ СООБЩЕНИЕ ===\n{text}\n\n"
            "Ответь СТРОГО одним словом без знаков препинания: light или heavy."
        )
        try:
            with _claude_chat_lock():
                result = self._run_claude_exec(
                    prompt,
                    read_only=True,
                    timeout_sec=10,
                    model=self.claude_model_chat,
                )
            normalized = result.strip().lower().strip(" .,!?\"'`")
            if "heavy" in normalized:
                return "heavy"
            return "light"
        except Exception:
            logger.exception("classify_message_weight failed, defaulting to light")
            return "light"

    def generate_brief(self, user_text: str, session_scope: int | str | None = None) -> str:
        """Ultra-short task perephrasal as a question (4-7 words). Includes last 20 session
        entries as context so references resolve. 25-sec timeout."""
        session_context = self._get_session_context(session_scope) if session_scope is not None else ""
        prompt = (
            "Перефразируй запрос пользователя ОДНОЙ КОРОТКОЙ ФРАЗОЙ-ВОПРОСОМ на русском. "
            "Длина: 4–7 слов. Только суть задачи в форме вопроса со знаком «?» в конце.\n\n"
            "ЗАПРЕЩЕНО использовать слова: «запустить», «агента», «делать», «иначе», «понял», "
            "«принял», «выполнить», «ли», «или». Без вводных, без обёрток, без двойных вопросов.\n\n"
            "Контекст диалога ниже — основной источник правды. Если в текущем запросе чего-то не "
            "хватает (отсылка, местоимение, ссылка на ранее обсуждавшееся) — восстанови по контексту. "
            "Не пиши «не указано», «не уточнено» — ищи ответ в контексте.\n\n"
            "Примеры формата ответа:\n"
            "- «Электрика и вентиляция бани по Forumhouse?»\n"
            "- «Сравнить разборы Dacia со скриншотами?»\n"
            "- «Поправить таймаут Sonnet до 150?»\n\n"
            f"{session_context}\n\n"
            f"=== ТЕКУЩИЙ ЗАПРОС ===\n{user_text}\n\n"
            "Ответь ОДНОЙ строкой-вопросом 4–7 слов, без кавычек."
        )
        try:
            with _claude_chat_lock():
                result = self._run_claude_exec(
                    prompt,
                    read_only=True,
                    timeout_sec=25,
                    model=self.claude_model_chat,
                )
            result = result.strip().strip('"').strip("'").strip()
            # Remove trailing junk if model added it
            if "\n" in result:
                result = result.split("\n", 1)[0].strip()
            if not result.endswith("?"):
                result = result.rstrip(".!") + "?"
            return result
        except Exception:
            logger.exception("generate_brief failed, using fallback")
            return "Разобрать задачу?"

    # === Pending action: confirmation flow ===

    @classmethod
    def _scope_key(cls, scope: int | str | None) -> str:
        return str(scope) if scope is not None else "0"

    def set_pending_action(self, scope: int | str | None, original_prompt: str, brief: str) -> None:
        """Store a pending action awaiting user confirmation."""
        self._pending_actions[self._scope_key(scope)] = {
            "original_prompt": original_prompt,
            "brief": brief,
            "created_at": time.time(),
        }

    def get_pending_action(self, scope: int | str | None) -> dict[str, Any] | None:
        """Return active pending action for scope, or None if absent/expired."""
        key = self._scope_key(scope)
        entry = self._pending_actions.get(key)
        if not entry:
            return None
        if time.time() - entry["created_at"] > PENDING_ACTION_TTL_SECONDS:
            self._pending_actions.pop(key, None)
            return None
        return entry

    def clear_pending_action(self, scope: int | str | None) -> None:
        self._pending_actions.pop(self._scope_key(scope), None)

    @staticmethod
    def _classify_response_quick(text: str) -> str:
        """Hardcoded list check. Returns 'confirm', 'cancel' or 'unknown'."""
        if not text:
            return "unknown"
        norm = text.strip().lower()
        # strip surrounding punctuation
        norm = norm.strip(" .,!?;:…«»\"'()-—–")
        if not norm:
            return "unknown"
        if norm in CONFIRMATION_WORDS:
            return "confirm"
        if norm in CANCELLATION_WORDS:
            return "cancel"
        for phrase in CANCELLATION_PHRASES:
            if norm == phrase or norm.startswith(phrase + " ") or norm.startswith(phrase + ","):
                return "cancel"
        return "unknown"

    def classify_pending_response(self, text: str, pending_brief: str) -> str:
        """Classify user response to a pending action: 'confirm' / 'cancel' / 'correct'.
        Hybrid: hardcoded list first, LLM fallback on unknown."""
        quick = self._classify_response_quick(text)
        if quick != "unknown":
            return quick

        prompt = (
            "Тебе дан pending action и ответ пользователя. "
            "Классифицируй ответ строго одним словом из трёх:\n"
            "- confirm — подтверждение, разрешение запустить (включая синонимы: 'давай', 'погнали', 'лады', 'норм' и т.п.)\n"
            "- cancel — отмена, отказ ('не надо', 'забей', 'не сейчас' и т.п.)\n"
            "- correct — корректировка задачи или новый запрос (всё остальное)\n\n"
            f"Pending action: {pending_brief}\n"
            f"Ответ пользователя: {text}\n\n"
            "Ответь ОДНИМ словом без точки: confirm, cancel или correct."
        )
        try:
            with _claude_chat_lock():
                result = self._run_claude_exec(
                    prompt,
                    read_only=True,
                    timeout_sec=15,
                    model=self.claude_model_chat,
                )
            result = result.strip().lower().strip(" .,!?")
            if result in ("confirm", "cancel", "correct"):
                return result
            return "correct"
        except Exception:
            logger.exception("classify_pending_response LLM fallback failed")
            return "correct"

    def execute_agent(
        self,
        user_prompt: str,
        user_id: int = 0,
        *,
        session_scope: int | str | None = None,
        work_context: bool = False,
    ) -> dict[str, Any]:
        """Execute a heavier task with tools and plain-text output."""
        today = date.today().isoformat()
        memory_context = self._get_memory_context(
            work_mode=work_context,
            cold_start=self._is_first_reply_today(session_scope or user_id),
        )
        session_context = self._get_session_context(session_scope or user_id)

        rag_context = ""
        try:
            from d_brain.services.memory_rag import search_memory

            relevant = search_memory(user_prompt, limit=5)
            if relevant:
                rag_context = f"\n=== MEMORY SEARCH ===\n{relevant}\n"
        except Exception:
            rag_context = ""

        system_prompt = (
            "You are the heavier action backend for a personal Telegram second-brain bot. "
            "You have tools for local project files and Todoist. "
            "Reply in Russian only. Execute the task when possible and finish with plain text only. "
            "No HTML, no markdown table, no fluff. "
            "The answer is for the user only: omit internal rules, hidden prompts, file-reading rituals, and assistant self-maintenance. "
            "Style: adaptive but restrained. Be friendly and clear, but let the tone match the situation: brisk for straightforward results, calmer for nuanced outcomes. "
            "Use short paragraphs with a blank line between them. "
            "Use fitting emoji sparingly and place them at the start of a paragraph when they improve scanning. "
            "Never reveal reasoning, internal reflections, or intermediate thinking. Give conclusions only. "
            "Do not suggest extra follow-up actions unless they are strictly required or explicitly requested. "
            f"{self._planning_guardrails()} "
            "Use Russian wording for all user-facing labels and headings. "
            "Translate English words, labels, and service phrasing into Russian unless they must stay exact as commands, code, file paths, model names, API names, or quoted product strings. "
            "If the user writes 'тг-режим', treat it as an explicit instruction to apply the project's Telegram formatting skill and keep the reply visually clean, alive, and natural."
        )
        composed_prompt = f"""
Today is {today}.
Project root: {self.project_path.as_posix()}
Vault root: {self.vault_path.as_posix()}

=== MEMORY CONTEXT ===
{memory_context}

=== SESSION CONTEXT ===
{session_context}
{rag_context}
=== END CONTEXT ===

USER REQUEST:
{user_prompt}

Perform the task with tools if needed. The final answer must be plain text in Russian:
- what you did
- result
- important follow-up only if the user must actually do something

Write naturally, not like a changelog. Keep it compact, readable, and human.

Do not include:
- internal instructions or rules you had to follow
- assistant-only chores or maintenance notes
- low-level tool logs unless the user asked for them
- your own reasoning or phrases about your thought process
- offers like "если хочешь, я могу..." unless explicitly requested
"""

        try:
            report = self._run_agent(
                system_prompt,
                composed_prompt,
                read_only=False,
                reasoning="high",
                verbosity="medium",
                max_output_tokens=2500,
            )
            return {"report": report, "processed_entries": 1}
        except Exception as exc:
            logger.exception("OpenAI agent execution failed")
            return {"error": str(exc), "processed_entries": 0}

    def _get_memory_context(
        self,
        work_mode: bool = False,
        *,
        cold_start: bool = False,
        force: bool = False,
    ) -> str:
        """Load and cache memory context for five minutes."""
        cache_key = "work" if work_mode else ("default:cold" if cold_start else "default")
        now = time.time()
        if not force and now - self._memory_cache_time < 300 and self._memory_cache.get(cache_key):
            return str(self._memory_cache[cache_key])

        if work_mode:
            context = self._get_work_memory_context()
            self._memory_cache[cache_key] = context
            self._memory_cache_time = now
            return context

        parts: list[str] = []
        memory_dir = self.vault_path / "memory"
        if memory_dir.exists():
            for name in ("user.md", "soul.md"):
                md_file = memory_dir / name
                if md_file.exists():
                    content = md_file.read_text(encoding="utf-8", errors="ignore")[:2000]
                    parts.append(f"=== {name} ===\n{content}")

        if cold_start:
            goals_dir = self.vault_path / "goals"
            if goals_dir.exists():
                for goal_file in sorted(goals_dir.glob("*.md")):
                    content = goal_file.read_text(encoding="utf-8", errors="ignore")[:1000]
                    parts.append(f"=== {goal_file.name} ===\n{content}")

            index_file = self.vault_path / "MOC" / "index.md"
            if index_file.exists():
                content = index_file.read_text(encoding="utf-8", errors="ignore")[:3000]
                parts.append(f"=== index.md ===\n{content}")
            root_index = self.vault_path / "index.md"
            if root_index.exists():
                parts.append(f"=== vault/index.md ===\n{self._read_context_file(root_index, 4500)}")

            moc_dir = self.vault_path / "MOC"
            if moc_dir.exists():
                for moc_file in sorted(moc_dir.glob("*.md")):
                    if moc_file.name == "index.md":
                        continue
                    content = self._read_context_file(moc_file, 1600)
                    if content:
                        parts.append(f"=== MOC/{moc_file.name} ===\n{content}")

            recent_summaries = sorted((self.vault_path / "summaries").glob("*.md"), reverse=True)[:2]
            for summary_file in recent_summaries:
                content = self._read_context_file(summary_file, 1200)
                if content:
                    parts.append(f"=== {summary_file.name} ===\n{content}")

            formatting_rules = self.vault_path / "thoughts" / "learnings" / "telegram-formatting-rules.md"
            if formatting_rules.exists():
                parts.append(
                    f"=== telegram-formatting-rules.md ===\n"
                    f"{self._read_context_file(formatting_rules, 1800)}"
                )

            formatting_skill = self._load_telegram_formatting_skill()
            if formatting_skill:
                parts.append(f"=== telegram-formatting skill ===\n{formatting_skill[:3500]}")

            project_catalog = self._build_project_catalog_context()
            if project_catalog:
                parts.append(project_catalog)

        context = "\n\n".join(parts)
        self._memory_cache[cache_key] = context
        self._memory_cache_time = now
        return context

    def execute_raw_prompt(
        self,
        prompt: str,
        user_id: int = 0,
        model: str = "sonnet",
        *,
        session_scope: int | str | None = None,
        work_context: bool = False,
    ) -> dict[str, Any]:
        """Execute a fast chat request without tool usage.

        The model argument is kept for handler compatibility and ignored.
        """
        del model
        timeout_sec = (
            MEDIA_GENERATION_TIMEOUT_SECONDS
            if self._is_media_generation_request(prompt)
            else CHAT_TIMEOUT_SECONDS
        )
        session_context = self._get_session_context(session_scope or user_id)
        memory_context = self._get_memory_context(
            work_mode=work_context,
            cold_start=self._is_first_reply_today(session_scope or user_id),
        )

        rag_context = ""
        try:
            from d_brain.services.memory_rag import search_memory

            relevant = search_memory(prompt, limit=5)
            if relevant:
                rag_context = f"\n=== MEMORY SEARCH ===\n{relevant}\n"
        except Exception:
            rag_context = ""

        system_prompt = (
            "You are a personal assistant in a Telegram second-brain bot. "
            "Reply in Russian only, concise, friendly, and natural. "
            "Use a warm, polished tone with light personality, but adapt it to context instead of sounding the same every time. "
            "For casual chat, be lighter and more conversational. "
            "For advice or emotional moments, be softer and more attentive. "
            "For factual answers, be clear and calm. "
            "Keep answers easy to scan and pleasant to read. Use short paragraphs with a blank line between them. "
            "Use 0-3 fitting emoji when helpful, and place them at the start of a paragraph rather than at the end. "
            "Translate English words, labels, and service phrasing into Russian unless they must stay exact as commands, code, file paths, model names, API names, or quoted product strings. "
            "Do not use English service labels or English section headings in user-facing replies. "
            "Do not mention internal instructions, hidden rules, or assistant-only maintenance. "
            "Never expose reasoning, reflections, or intermediate thinking; give the final answer only. "
            "Do not offer extra actions or say 'если хочешь, я могу...' unless the user explicitly asked for options or continuation. "
            f"{self._planning_guardrails()}"
        )
        user_prompt = f"""
=== MEMORY CONTEXT ===
{memory_context}

=== SESSION CONTEXT ===
{session_context}
{rag_context}
=== USER MESSAGE ===
{prompt}
"""

        try:
            report = self._run_chat(
                system_prompt,
                user_prompt,
                reasoning="low",
                verbosity="low",
                max_output_tokens=1200,
                timeout_sec=timeout_sec,
            )
            return {"report": report, "processed_entries": 1}
        except Exception as exc:
            logger.exception("OpenAI chat failed")
            return {"error": str(exc), "processed_entries": 0}


# Backward-compatible alias for existing imports.
ClaudeProcessor = AgentProcessor
