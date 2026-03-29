"""Telegram user client for reading channels via MTProto (Telethon)."""

import logging
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


class TelegramReader:
    """Reads Telegram channels/groups on behalf of a user account."""

    def __init__(self, api_id: int, api_hash: str, session_path: Path) -> None:
        session_file = str(session_path / "user_session")
        self.client = TelegramClient(session_file, api_id, api_hash)
        self._phone: str | None = None
        self._phone_code_hash: str | None = None

    async def is_authorized(self) -> bool:
        await self.client.connect()
        return await self.client.is_user_authorized()

    async def send_code(self, phone: str) -> str:
        """Send auth code to phone. Returns phone_code_hash."""
        await self.client.connect()
        result = await self.client.send_code_request(phone)
        self._phone = phone
        self._phone_code_hash = result.phone_code_hash
        return result.phone_code_hash

    async def sign_in(self, code: str, password: str | None = None) -> bool:
        """Complete sign-in with received code. Returns True on success."""
        try:
            await self.client.sign_in(
                phone=self._phone,
                code=code,
                phone_code_hash=self._phone_code_hash,
            )
            return True
        except SessionPasswordNeededError:
            if password:
                await self.client.sign_in(password=password)
                return True
            raise

    async def get_messages(self, channel: str, limit: int = 10) -> list[dict]:
        """Fetch last N messages from channel/group.

        Args:
            channel: username (@channel), link, or chat ID
            limit: number of messages to fetch (max 100)

        Returns:
            List of dicts with keys: id, date, sender, text, fwd_from
        """
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError("Not authorized. Use /tg_connect first.")

        limit = min(limit, 100)
        entity = await self.client.get_entity(channel)
        messages = await self.client.get_messages(entity, limit=limit)

        result = []
        for msg in messages:
            if not isinstance(msg, Message):
                continue
            sender_name = ""
            try:
                if msg.sender_id:
                    sender = await self.client.get_entity(msg.sender_id)
                    sender_name = getattr(sender, "username", None) or getattr(sender, "first_name", "") or ""
            except Exception:
                pass

            fwd = ""
            if msg.fwd_from and msg.fwd_from.from_name:
                fwd = msg.fwd_from.from_name

            result.append({
                "id": msg.id,
                "date": msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "",
                "sender": sender_name,
                "text": msg.text or "",
                "fwd_from": fwd,
            })
        return result

    async def disconnect(self) -> None:
        await self.client.disconnect()
