"""Application configuration using Pydantic Settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str = Field(description="Telegram Bot API token")
    telegram_api_id: int = Field(default=0, description="Telegram API ID from my.telegram.org")
    telegram_api_hash: str = Field(default="", description="Telegram API Hash from my.telegram.org")
    deepgram_api_key: str = Field(description="Deepgram API key for transcription")
    todoist_api_key: str = Field(default="", description="Todoist API key for tasks")
    ai_backend: str = Field(
        default="codex",
        description="Active AI backend: 'codex' or 'claude'. Determines which sim is used (vault/.codex/ vs vault/.claude/). Currently only 'codex' is implemented; 'claude' is reserved for future re-activation of the dormant Claude sim.",
    )
    codex_bin: str = Field(default="codex", description="Path to the Codex CLI binary")
    codex_model: str = Field(default="gpt-5.5", description="Default Codex model (fallback)")
    codex_model_chat: str = Field(
        default="",
        description="Codex model for dialog mode (light, fast). Falls back to codex_model if empty.",
    )
    codex_model_agent: str = Field(
        default="",
        description="Codex model for processing/agent mode (heavy, capable). Falls back to codex_model if empty.",
    )
    codex_sandbox_mode: str = Field(
        default="bypass",
        description="Codex exec sandbox mode: read-only, workspace-write, danger-full-access, or bypass",
    )
    claude_bin: str = Field(
        default="claude",
        description="Path to the Claude Code CLI binary (used when AI_BACKEND=claude)",
    )
    claude_model: str = Field(
        default="sonnet",
        description="Default Claude model (fallback)",
    )
    claude_model_chat: str = Field(
        default="sonnet",
        description="Claude model for dialog (light, fast). Per v3: Sonnet without MCP.",
    )
    claude_model_agent: str = Field(
        default="opus",
        description="Claude model for processing/agent (heavy). Per v3: Opus with MCP.",
    )
    claude_effort: str = Field(
        default="medium",
        description="Claude effort level: low | medium | high | xhigh | max",
    )
    vault_path: Path = Field(
        default=Path("./vault"),
        description="Path to Obsidian vault directory",
    )
    allowed_user_ids: list[int] = Field(
        default_factory=list,
        description="List of Telegram user IDs allowed to use the bot",
    )
    admin_user_ids: list[int] = Field(
        default_factory=list,
        description="List of Telegram user IDs allowed to run admin commands",
    )
    allow_all_users: bool = Field(
        default=False,
        description="Whether to allow access to all users (security risk!)",
    )
    admin_restart_command: str = Field(
        default="",
        description="Shell command used by /restart admin command",
    )
    work_chat_ids: list[int] = Field(
        default_factory=list,
        description="Telegram group chat IDs treated as work-only context",
    )
    treat_all_group_chats_as_work: bool = Field(
        default=True,
        description="Whether all non-private chats should default to work-only context",
    )
    voice_replies: bool = Field(
        default=False,
        description="Reply to voice messages with TTS voice messages",
    )

    @property
    def daily_path(self) -> Path:
        """Path to daily notes directory."""
        return self.vault_path / "daily"

    @property
    def attachments_path(self) -> Path:
        """Path to attachments directory."""
        return self.vault_path / "attachments"

    @property
    def thoughts_path(self) -> Path:
        """Path to thoughts directory."""
        return self.vault_path / "thoughts"


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
