"""Bot FSM states."""

from aiogram.fsm.state import State, StatesGroup


class DoCommandState(StatesGroup):
    """States for /do command flow."""

    waiting_for_input = State()  # Waiting for voice or text after /do


class SilentState(StatesGroup):
    """Silent mode — only save, no AI response."""

    active = State()


class TgConnectState(StatesGroup):
    """States for /tg_connect Telegram user auth flow."""

    waiting_phone = State()
    waiting_code = State()
    waiting_password = State()  # 2FA if needed


class VoiceReplyState(StatesGroup):
    """Voice reply mode — respond with TTS voice messages."""

    active = State()
