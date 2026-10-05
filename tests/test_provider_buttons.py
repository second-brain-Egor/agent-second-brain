from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from d_brain.bot import keyboards
from d_brain.bot.handlers import backend, buttons, claude_model
from d_brain.config import Settings


@pytest.mark.parametrize('provider', ['claude', 'codex'])
@pytest.mark.parametrize('work', [True, False])
async def test_provider_keeps_mode(tmp_path, monkeypatch, provider, work):
    path = tmp_path / '.env'
    original = 'AI_BACKEND=codex\nPROCESS_BACKEND=codex\nSECRET=keep\n'
    path.write_text(original)
    monkeypatch.setattr(backend, 'ENV_PATH', path)
    settings = Settings(_env_file=None, telegram_bot_token='test', deepgram_api_key='test',
                        admin_user_ids=[7], ai_backend='codex',
                        codex_model_chat='gpt-6-astra' if work else 'gpt-6.1-sol')
    monkeypatch.setattr(buttons, 'get_settings', lambda: settings)
    monkeypatch.setattr(buttons, 'get_message_keyboard', lambda m: None)
    monkeypatch.setattr(backend, '_probe_claude_auth', AsyncMock(return_value=(True, '')))
    monkeypatch.setattr(buttons.Path, 'home', lambda: tmp_path)
    (tmp_path / '.codex').mkdir()
    (tmp_path / '.codex/auth.json').write_text('{}')
    for name in ('AI_BACKEND','CLAUDE_MODEL','CLAUDE_MODEL_CHAT','CLAUDE_MODEL_AGENT',
                 'CLAUDE_EFFORT','CODEX_MODEL','CODEX_MODEL_CHAT','CODEX_MODEL_AGENT',
                 'CODEX_REASONING_EFFORT'):
        monkeypatch.setenv(name, '')
    message = SimpleNamespace(from_user=SimpleNamespace(id=7), answer=AsyncMock())
    state = AsyncMock()
    if provider == 'claude':
        await claude_model.btn_claude_model(message, state)
    else:
        await buttons.btn_codex(message, state)
    text = path.read_text()
    assert f'AI_BACKEND={provider}' in text
    assert 'PROCESS_BACKEND=codex' in text and 'SECRET=keep' in text
    expected = (('claude-opus-5-5' if work else 'claude-sonnet-5-5') if provider == 'claude'
                else ('gpt-6-astra' if work else 'gpt-6.1-sol'))
    assert f'{provider.upper()}_MODEL_CHAT={expected}' in text
    if provider == 'claude':
        assert f"CLAUDE_EFFORT={'xhigh' if work else 'max'}" in text
    state.set_state.assert_awaited_once_with(None)
    assert message.answer.call_args.args[0] == f"Переключился на {'Claude' if provider == 'claude' else 'Codex'}."


async def test_failed_auth_preserves_provider(tmp_path, monkeypatch):
    path = tmp_path / '.env'
    path.write_text('AI_BACKEND=codex\n')
    monkeypatch.setattr(backend, 'ENV_PATH', path)
    monkeypatch.setattr(buttons, 'get_settings', lambda: SimpleNamespace(
        admin_user_ids=[7], ai_backend='codex', codex_model_chat='gpt-6-astra'))
    monkeypatch.setattr(backend, '_probe_claude_auth', AsyncMock(return_value=(False, '401')))
    message = SimpleNamespace(from_user=SimpleNamespace(id=7), answer=AsyncMock())
    state = AsyncMock()
    await buttons.select_provider(message, state, 'claude')
    assert path.read_text() == 'AI_BACKEND=codex\n'
    state.set_state.assert_not_called()


def test_exact_layout(tmp_path, monkeypatch):
    settings = Settings(_env_file=None, telegram_bot_token='test', deepgram_api_key='test',
                        temporary_chat_user_id=7, vault_path=tmp_path, show_help_button=False,
                        ai_backend='codex', codex_model_chat='gpt-6.1-sol', codex_reasoning_effort='max')
    monkeypatch.setattr(keyboards, 'get_settings', lambda: settings)
    labels = [[b.text for b in row] for row in keyboards.get_main_keyboard(7).keyboard]
    assert labels == [['🛠 Работа', '🧠 Claude', '⚙️ Обработать'],
                      ['💬 Обсудить ✓', '🤖 Codex ✓', '🕶 Временный чат']]


async def test_old_model_menu_cannot_change_model():
    callback = SimpleNamespace(answer=AsyncMock(), message=SimpleNamespace(edit_reply_markup=AsyncMock()))
    await claude_model.obsolete_model_menu(callback)
    callback.message.edit_reply_markup.assert_awaited_once_with(reply_markup=None)
