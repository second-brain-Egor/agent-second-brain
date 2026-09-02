"""Entry point for running d-brain as a module."""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    from d_brain.bot.main import run_bot
    from d_brain.config import get_settings
    from d_brain.logging_config import configure_logging

    settings = get_settings()
    configure_logging(settings.resolved_error_log_path)
    logger.info("d-brain starting...")
    logger.info("Vault path: %s", settings.vault_path)
    logger.info("Allowed users: %s", settings.allowed_user_ids)

    await run_bot(settings)


if __name__ == "__main__":
    asyncio.run(main())
