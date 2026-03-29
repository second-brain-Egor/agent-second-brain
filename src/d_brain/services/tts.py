"""Text-to-speech service using edge-tts (free, no API key required)."""

import asyncio
import io
import logging

import edge_tts

logger = logging.getLogger(__name__)

# Russian female voice — good quality, natural
DEFAULT_VOICE = "ru-RU-SvetlanaNeural"


async def text_to_speech(text: str, voice: str = DEFAULT_VOICE) -> bytes:
    """Convert text to MP3 audio bytes using edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
    audio_bytes = audio_buffer.getvalue()
    if not audio_bytes:
        raise RuntimeError("TTS returned empty audio")
    return audio_bytes


async def mp3_to_ogg(mp3_bytes: bytes) -> bytes:
    """Convert MP3 bytes to OGG/Opus bytes using ffmpeg (required for Telegram voice messages)."""
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-i", "pipe:0",
        "-c:a", "libopus",
        "-b:a", "64k",
        "-f", "ogg",
        "pipe:1",
        "-loglevel", "error",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(input=mp3_bytes)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {stderr.decode()}")
    return stdout


async def text_to_voice(text: str, voice: str = DEFAULT_VOICE) -> bytes:
    """Convert text to OGG/Opus bytes for Telegram voice messages."""
    mp3_bytes = await text_to_speech(text, voice)
    return await mp3_to_ogg(mp3_bytes)
