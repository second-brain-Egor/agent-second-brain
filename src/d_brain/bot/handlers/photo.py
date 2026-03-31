"""Photo message handler with Claude Vision analysis."""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Router
from aiogram.types import Message

from d_brain.config import get_settings
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="photo")
logger = logging.getLogger(__name__)

VISION_PROMPT = (
    "Опиши что на изображении. "
    "Если есть текст — извлеки его полностью (OCR). "
    "Если это скриншот, документ или заметка — передай содержание. "
    "Если это фото — опиши кратко что изображено. "
    "Отвечай на русском, кратко и по делу."
)


async def _analyze_image(image_path: str, vault_path: Path, caption: str | None = None) -> str | None:
    """Analyze image using Claude CLI (subscription, no API key needed)."""
    try:
        user_prompt = VISION_PROMPT
        if caption:
            user_prompt += f"\n\nПодпись от пользователя: {caption}"

        full_prompt = f"Прочитай изображение по пути {image_path} и выполни задачу:\n{user_prompt}"

        env = os.environ.copy()
        result = subprocess.run(
            [
                "flock", "-w", "30", "/tmp/claude-chat.lock",
                "claude",
                "--print",
                "--dangerously-skip-permissions",
                "--model", "sonnet",
                "-p",
                full_prompt,
            ],
            cwd=str(vault_path.parent),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env=env,
        )

        if result.returncode != 0:
            logger.error("Vision CLI failed: %s", result.stderr)
            return None

        output = result.stdout.strip()
        return output if output else None

    except subprocess.TimeoutExpired:
        logger.error("Vision CLI timed out")
        return None
    except Exception:
        logger.exception("Vision analysis failed")
        return None


@router.message(lambda m: m.photo is not None)
async def handle_photo(message: Message, bot: Bot) -> None:
    """Handle photo messages — save and analyze with Vision."""
    if not message.photo or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)

    # Get largest photo
    photo = message.photo[-1]

    try:
        file = await bot.get_file(photo.file_id)
        if not file.file_path:
            await message.answer("Failed to download photo")
            return

        file_bytes = await bot.download_file(file.file_path)
        if not file_bytes:
            await message.answer("Failed to download photo")
            return

        timestamp = datetime.fromtimestamp(message.date.timestamp())
        photo_bytes = file_bytes.read()

        # Determine extension from file path
        extension = "jpg"
        if file.file_path and "." in file.file_path:
            extension = file.file_path.rsplit(".", 1)[-1]

        # Save photo and get relative path
        relative_path = storage.save_attachment(
            photo_bytes,
            timestamp.date(),
            timestamp,
            extension,
        )

        # Absolute path for Claude CLI
        vault_path = Path(settings.vault_path)
        absolute_image_path = str((vault_path / relative_path).resolve())

        # Analyze with Vision via Claude CLI
        await message.chat.do(action="typing")
        description = await _analyze_image(absolute_image_path, vault_path, message.caption)

        # Create content with Obsidian embed + description
        content = f"![[{relative_path}]]"
        if message.caption:
            content += f"\n\n{message.caption}"
        if description:
            content += f"\n\n> [!note] Vision\n> {description.replace(chr(10), chr(10) + '> ')}"

        storage.append_to_daily(content, timestamp, "[photo]")

        # Log to session
        session = SessionStore(settings.vault_path)
        session.append(
            message.from_user.id,
            "photo",
            path=relative_path,
            caption=message.caption,
            text=description,
            msg_id=message.message_id,
        )

        # Reply with description or just confirm
        if description:
            try:
                await message.answer(f"📷 ✓\n\n{description}")
            except Exception:
                await message.answer(f"📷 ✓\n\n{description}", parse_mode=None)
        else:
            await message.answer("📷 ✓ Сохранено")

        logger.info("Photo saved and analyzed: %s", relative_path)

    except Exception as e:
        logger.exception("Error processing photo")
        await message.answer(f"Error: {e}")
