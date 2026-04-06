"""Photo message handler with OpenAI vision analysis."""

from __future__ import annotations

import asyncio
import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from aiogram import Bot, Router
from aiogram.types import Message

from d_brain.config import get_settings
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="photo")
logger = logging.getLogger(__name__)

VISION_PROMPT = (
    "Describe what is in the image. "
    "If there is readable text, extract it fully. "
    "If this is a screenshot, note, or document, summarize the important content. "
    "Reply in Russian, concise and useful."
)

MIME_BY_SUFFIX = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def _extract_output_text(response: Any) -> str:
    text = getattr(response, "output_text", "") or ""
    if text:
        return text.strip()

    parts: list[str] = []
    for item in getattr(response, "output", []):
        if getattr(item, "type", "") != "message":
            continue
        for content in getattr(item, "content", []):
            content_type = getattr(content, "type", "")
            if content_type in {"output_text", "text"}:
                value = getattr(content, "text", "") or ""
                if value:
                    parts.append(value)
    return "\n".join(parts).strip()


def _analyze_image_sync(image_path: str, caption: str | None = None) -> str | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    from openai import OpenAI

    image_file = Path(image_path)
    mime_type = MIME_BY_SUFFIX.get(image_file.suffix.lower(), "image/jpeg")
    image_b64 = base64.b64encode(image_file.read_bytes()).decode("ascii")

    prompt = VISION_PROMPT
    if caption:
        prompt += f"\n\nUser caption: {caption}"

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        instructions="Reply in Russian, concise, plain text.",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{image_b64}",
                    },
                ],
            }
        ],
        reasoning={"effort": "low"},
        text={"verbosity": "low"},
        max_output_tokens=1000,
    )
    return _extract_output_text(response) or None


async def _analyze_image(image_path: str, caption: str | None = None) -> str | None:
    """Analyze an image with the configured OpenAI model."""
    try:
        return await asyncio.to_thread(_analyze_image_sync, image_path, caption)
    except Exception:
        logger.exception("Vision analysis failed")
        return None


@router.message(lambda m: m.photo is not None)
async def handle_photo(message: Message, bot: Bot) -> None:
    """Handle photo messages: save them and analyze with vision."""
    if not message.photo or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
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

        extension = "jpg"
        if "." in file.file_path:
            extension = file.file_path.rsplit(".", 1)[-1]

        relative_path = storage.save_attachment(
            photo_bytes,
            timestamp.date(),
            timestamp,
            extension,
        )

        absolute_image_path = str((Path(settings.vault_path) / relative_path).resolve())

        await message.chat.do(action="typing")
        description = await _analyze_image(absolute_image_path, message.caption)

        content = f"![[{relative_path}]]"
        if message.caption:
            content += f"\n\n{message.caption}"
        if description:
            content += f"\n\n> [!note] Vision\n> {description.replace(chr(10), chr(10) + '> ')}"

        storage.append_to_daily(content, timestamp, "[photo]")

        session = SessionStore(settings.vault_path)
        session.append(
            message.from_user.id,
            "photo",
            path=relative_path,
            caption=message.caption,
            text=description,
            msg_id=message.message_id,
        )

        if description:
            try:
                await message.answer(f"Photo saved.\n\n{description}")
            except Exception:
                await message.answer(f"Photo saved.\n\n{description}", parse_mode=None)
        else:
            await message.answer("Photo saved.")

        logger.info("Photo saved and analyzed: %s", relative_path)

    except Exception as exc:
        logger.exception("Error processing photo")
        await message.answer(f"Error: {exc}")
