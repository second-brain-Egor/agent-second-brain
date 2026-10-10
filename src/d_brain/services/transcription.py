"""Deepgram transcription service."""

import asyncio
import logging

import httpx
from deepgram import AsyncDeepgramClient

logger = logging.getLogger(__name__)

# Обрыв соединения (TLS, таймаут) повторяем: 9 октября 2026 часть запросов рвалась на сетевом пути.
RETRY_DELAYS = (1.0, 3.0)


class DeepgramTranscriber:
    """Service for transcribing audio using Deepgram Nova-3."""

    def __init__(self, api_key: str) -> None:
        self.client = AsyncDeepgramClient(api_key=api_key)

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text.

        Args:
            audio_bytes: Audio file content

        Returns:
            Transcribed text

        Raises:
            Exception: If transcription fails
        """
        logger.info("Starting transcription, audio size: %d bytes", len(audio_bytes))

        for attempt, delay in enumerate((*RETRY_DELAYS, None), start=1):
            try:
                response = await self.client.listen.v1.media.transcribe_file(
                    request=audio_bytes,
                    model="nova-3",
                    language="ru",
                    punctuate=True,
                    smart_format=True,
                )
                break
            except httpx.TransportError as error:
                if delay is None:
                    raise
                logger.warning("Transcription attempt %d failed (%s), retrying in %.0fs",
                               attempt, type(error).__name__, delay)
                await asyncio.sleep(delay)

        transcript = (
            response.results.channels[0].alternatives[0].transcript
            if response.results
            and response.results.channels
            and response.results.channels[0].alternatives
            else ""
        )

        logger.info("Transcription complete: %d chars", len(transcript))
        return transcript
