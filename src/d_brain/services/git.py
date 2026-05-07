"""Git automation service for vault."""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class VaultGit:
    """Service for git operations on vault."""

    def __init__(self, vault_path: Path) -> None:
        self.vault_path = Path(vault_path)

    def _run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run git command in vault directory."""
        return subprocess.run(
            ["git", *args],
            cwd=self.vault_path,
            capture_output=True,
            text=True,
            check=False,
        )

    def get_status(self) -> str:
        """Get git status."""
        result = self._run_git("status", "--porcelain")
        return result.stdout

    def has_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        return bool(self.get_status().strip())

    def commit_changes(self, message: str) -> bool:
        """Stage all changes and commit.

        Args:
            message: Commit message

        Returns:
            True if commit was made, False otherwise
        """
        if not self.has_changes():
            logger.info("No changes to commit")
            return False

        # Stage all changes
        add_result = self._run_git("add", "-A")
        if add_result.returncode != 0:
            logger.error("Git add failed: %s", add_result.stderr)
            return False

        # Commit
        commit_result = self._run_git("commit", "-m", message)
        if commit_result.returncode != 0:
            logger.error("Git commit failed: %s", commit_result.stderr)
            return False

        logger.info("Committed: %s", message)
        return True

    def pull_rebase_autostash(self) -> bool:
        """Pull + rebase from remote, autostashing any unstaged changes.

        `--autostash` сам стэшит грязный working tree (бот пишет в `daily/` и
        `attachments/` всё время) перед rebase и возвращает изменения после.
        Это решает класс проблем «нельзя pull при unstaged changes», без
        которого `commit_and_push` мог сломать синхронизацию когда remote
        ушёл вперёд (например пользователь правил vault через Obsidian
        с другого устройства).
        """
        result = self._run_git("pull", "--rebase", "--autostash", "origin", "main")
        if result.returncode != 0:
            logger.error("Git pull --rebase --autostash failed: %s", result.stderr)
            return False
        logger.info("Pulled with rebase (autostash)")
        return True

    def push(self) -> bool:
        """Push to remote. Caller must run pull_rebase_autostash first if needed."""
        result = self._run_git("push")
        if result.returncode != 0:
            logger.error("Git push failed: %s", result.stderr)
            return False

        logger.info("Pushed to remote")
        return True

    def commit_and_push(self, message: str) -> bool:
        """Commit, pull --rebase --autostash, then push.

        Алгоритм:
          1. Commit (no-op если нет изменений).
          2. Pull --rebase --autostash — подтягиваем remote, обрабатывая
             параллельную работу бота (он пишет в daily/attachments/).
          3. Push — отправляет накопленные локальные коммиты.

        Returns:
            True если push прошёл (или нечего отправлять).
        """
        self.commit_changes(message)  # no-op если нет изменений
        if not self.pull_rebase_autostash():
            # Если pull-rebase упал — не пытаемся push, иначе rejected.
            # Юзер увидит проблему в логах journalctl, отчёт в чат всё равно дойдёт.
            return False
        return self.push()
