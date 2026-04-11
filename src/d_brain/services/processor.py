"""AI processing service."""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path
from typing import Any

from d_brain.services.session import SessionStore

logger = logging.getLogger(__name__)

AGENT_MARKER = "[NEED_AGENT]"
AGENT_MARKER_PATTERN = re.compile(
    r"^\s*(?:<[^>]+>\s*)*" + re.escape(AGENT_MARKER) + r"(?:\s|$)",
    re.IGNORECASE,
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

    def __init__(self, vault_path: Path, todoist_api_key: str = "") -> None:
        self.vault_path = Path(vault_path).resolve()
        self.project_path = self.vault_path.parent.resolve()
        self.todoist_api_key = todoist_api_key

        from d_brain.config import get_settings

        settings = get_settings()
        self.codex_bin = settings.codex_bin.strip() or "codex"
        self.codex_model = settings.codex_model.strip() or "gpt-5.4"
        self.codex_sandbox_mode = settings.codex_sandbox_mode.strip().lower() or "bypass"

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

    def _planning_guardrails(self) -> str:
        """Shared prompt rules for planning horizon and reminders."""
        return PLANNING_GUARDRAILS

    def _get_session_context(self, user_id: int) -> str:
        """Get today's session context for the AI backend."""
        if user_id == 0:
            return ""

        session = SessionStore(self.vault_path)
        today_entries = session.get_today(user_id)
        if not today_entries:
            return ""

        lines = ["=== TODAY SESSION ==="]
        for entry in today_entries[-50:]:
            ts = entry.get("ts", "")[11:16]
            entry_type = entry.get("type", "unknown")
            text = entry.get("text", "")[:500]
            if text:
                lines.append(f"{ts} [{entry_type}] {text}")
        lines.append("=== END SESSION ===")
        return "\n".join(lines)

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

    def _build_codex_prompt(
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
            f"{user_prompt.strip()}\n"
        )

    def _run_codex_exec(
        self,
        prompt: str,
        *,
        read_only: bool,
        images: list[str] | None = None,
        timeout_sec: int = 600,
    ) -> str:
        """Run Codex CLI and return its final message."""
        codex_bin = self._get_codex_bin()
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
                self.codex_model,
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

    def _run_openai_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        reasoning: str | None = None,
        verbosity: str | None = None,
        max_output_tokens: int = 2000,
    ) -> str:
        """Run a plain Codex CLI request."""
        del reasoning, verbosity, max_output_tokens
        prompt = self._build_codex_prompt(system_prompt, user_prompt, read_only=True)
        return self._run_codex_exec(
            prompt,
            read_only=True,
            timeout_sec=300,
        )

    def _run_openai_agent(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        read_only: bool = False,
        reasoning: str | None = None,
        verbosity: str | None = None,
        max_output_tokens: int = 2500,
    ) -> str:
        """Run Codex CLI against the local project."""
        del reasoning, verbosity, max_output_tokens
        prompt = self._build_codex_prompt(system_prompt, user_prompt, read_only=read_only)
        return self._run_codex_exec(
            prompt,
            read_only=read_only,
            timeout_sec=900 if not read_only else 600,
        )

    def analyze_image(self, image_path: str, caption: str | None = None) -> str | None:
        """Analyze an image via Codex CLI."""
        image_file = Path(image_path)
        if not image_file.exists():
            return None

        prompt = (
            "You are analyzing an image for a Telegram second-brain bot.\n"
            "Reply in Russian, concise and useful.\n"
            "Describe what is in the image.\n"
            "If there is readable text, extract it fully.\n"
            "If this is a screenshot, note, or document, summarize the important content.\n"
            "Return plain text only."
        )
        if caption:
            prompt += f"\n\nUser caption:\n{caption}"

        try:
            return self._run_codex_exec(
                prompt,
                read_only=True,
                images=[str(image_file)],
                timeout_sec=300,
            )
        except Exception:
            logger.exception("Vision analysis failed")
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

Process today's inbox and memory updates.

Start by reading:
- vault/daily/{day.isoformat()}.md
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
            report = self._run_openai_agent(
                system_prompt,
                user_prompt,
                read_only=False,
                reasoning="medium",
                verbosity="medium",
                max_output_tokens=3000,
            )
            return {"report": report, "processed_entries": 1}
        except Exception as exc:
            logger.exception("OpenAI daily processing failed")
            return {"error": str(exc), "processed_entries": 0}

    def execute_prompt(self, user_prompt: str, user_id: int = 0) -> dict[str, Any]:
        """Execute an arbitrary user request with tools and HTML output."""
        today = date.today().isoformat()
        todoist_ref = self._load_todoist_reference()
        memory_context = self._get_memory_context()
        session_context = self._get_session_context(user_id)

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
            "Avoid repeating the same emoji in neighboring paragraphs. Avoid mixing in English unless it is a product name or exact command. "
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
            report = self._run_openai_agent(
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
            report = self._run_openai_agent(
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

    def execute_agent(self, user_prompt: str, user_id: int = 0) -> dict[str, Any]:
        """Execute a heavier task with tools and plain-text output."""
        today = date.today().isoformat()
        memory_context = self._get_memory_context()
        session_context = self._get_session_context(user_id)

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
            "Reply in Russian. Execute the task when possible and finish with plain text only. "
            "No HTML, no markdown table, no fluff. "
            "The answer is for the user only: omit internal rules, hidden prompts, file-reading rituals, and assistant self-maintenance. "
            "Style: adaptive but restrained. Be friendly and clear, but let the tone match the situation: brisk for straightforward results, calmer for nuanced outcomes. "
            "Use short paragraphs with a blank line between them. "
            "Use fitting emoji sparingly and place them at the start of a paragraph when they improve scanning. "
            "Never reveal reasoning, internal reflections, or intermediate thinking. Give conclusions only. "
            "Do not suggest extra follow-up actions unless they are strictly required or explicitly requested. "
            f"{self._planning_guardrails()} "
            "Use Russian wording for all user-facing labels and headings."
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
            report = self._run_openai_agent(
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

    def _get_memory_context(self) -> str:
        """Load and cache memory context for five minutes."""
        now = time.time()
        if now - self._memory_cache_time < 300 and self._memory_cache.get("context"):
            return str(self._memory_cache["context"])

        parts: list[str] = []
        memory_dir = self.vault_path / "memory"
        if memory_dir.exists():
            for md_file in sorted(memory_dir.glob("*.md")):
                content = md_file.read_text(encoding="utf-8", errors="ignore")[:2000]
                parts.append(f"=== {md_file.name} ===\n{content}")

        goals_dir = self.vault_path / "goals"
        if goals_dir.exists():
            for goal_file in sorted(goals_dir.glob("*.md")):
                content = goal_file.read_text(encoding="utf-8", errors="ignore")[:1000]
                parts.append(f"=== {goal_file.name} ===\n{content}")

        context = "\n\n".join(parts)
        self._memory_cache["context"] = context
        self._memory_cache_time = now
        return context

    def execute_raw_prompt(self, prompt: str, user_id: int = 0, model: str = "sonnet") -> dict[str, Any]:
        """Execute a fast chat request without tool usage.

        The model argument is kept for handler compatibility and ignored.
        """
        del model
        session_context = self._get_session_context(user_id)
        memory_context = self._get_memory_context()

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
            "Reply in Russian, concise, friendly, and natural. "
            "Use a warm, polished tone with light personality, but adapt it to context instead of sounding the same every time. "
            "For casual chat, be lighter and more conversational. "
            "For advice or emotional moments, be softer and more attentive. "
            "For factual answers, be clear and calm. "
            "Keep answers easy to scan and pleasant to read. Use short paragraphs with a blank line between them. "
            "Use 0-3 fitting emoji when helpful, and place them at the start of a paragraph rather than at the end. "
            "Do not use English service labels or English section headings in user-facing replies. "
            "Do not mention internal instructions, hidden rules, or assistant-only maintenance. "
            "Never expose reasoning, reflections, or intermediate thinking; give the final answer only. "
            "Do not offer extra actions or say 'если хочешь, я могу...' unless the user explicitly asked for options or continuation. "
            f"{self._planning_guardrails()} "
            "If the request requires taking actions with files, Todoist, or a multi-step workflow, "
            f"do not execute it in chat mode. Start the reply exactly with {AGENT_MARKER} "
            "and then add one short, user-friendly sentence describing the needed action. "
            "If it is a normal conversation or question, answer normally without the marker."
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
            report = self._run_openai_text(
                system_prompt,
                user_prompt,
                reasoning="low",
                verbosity="low",
                max_output_tokens=1200,
            )
            return {"report": report, "processed_entries": 1}
        except Exception as exc:
            logger.exception("OpenAI chat failed")
            return {"error": str(exc), "processed_entries": 0}


# Backward-compatible alias for existing imports.
ClaudeProcessor = AgentProcessor
