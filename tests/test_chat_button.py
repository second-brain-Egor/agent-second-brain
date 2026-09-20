"""Conversation mode changes the actual CLI effort without a model call."""
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from d_brain.bot.handlers import backend, buttons
from d_brain.bot.keyboards import CHAT_BUTTON, WORK_BUTTON, get_main_keyboard
from d_brain.bot.states import DoCommandState
from d_brain.config import Settings
from d_brain.services import processor as module


@pytest.mark.parametrize('button,effort', [(buttons.btn_chat, 'medium'), (buttons.btn_work, 'xhigh')])
@pytest.mark.parametrize('active,key', [('codex', 'CODEX_REASONING_EFFORT'), ('claude', 'CLAUDE_EFFORT')])
async def test_button_persists_effort_and_leaves_do_mode(tmp_path, monkeypatch, active, key, button, effort):
    env_path = tmp_path / '.env'
    env_path.write_text(f'AI_BACKEND={active}\nCODEX_MODEL=gpt-6-astra\n{key}=high\n')
    monkeypatch.setattr(backend, 'ENV_PATH', env_path)
    monkeypatch.setenv(key, 'high')
    monkeypatch.setattr(buttons, 'get_settings', lambda: SimpleNamespace(
        ai_backend=active, admin_user_ids=[7]))
    state = FSMContext(MemoryStorage(), StorageKey(bot_id=1, chat_id=7, user_id=7))
    await state.set_state(DoCommandState.waiting_for_input)
    await state.update_data(voice_mode=True)
    message = SimpleNamespace(from_user=SimpleNamespace(id=7), answer=AsyncMock())

    await button(message, state)

    assert f'{key}={effort}' in env_path.read_text()
    assert 'CODEX_MODEL=gpt-6-astra' in env_path.read_text()
    assert os.environ[key] == effort
    assert await state.get_state() is None
    assert (await state.get_data())['voice_mode'] is True
    # Fresh settings used by later text/voice processors see the selection.
    settings = Settings(_env_file=env_path, telegram_bot_token='test', deepgram_api_key='test')
    monkeypatch.setattr('d_brain.config.get_settings', lambda: settings)
    instance = module.AgentProcessor(tmp_path / 'vault', '')
    assert getattr(instance, 'claude_effort' if active == 'claude' else 'codex_reasoning_effort') == effort


@pytest.mark.parametrize('effort', ['', 'medium', 'xhigh'])
def test_codex_command_applies_only_selected_effort(tmp_path, monkeypatch, effort):
    instance = object.__new__(module.AgentProcessor)
    instance.project_path = tmp_path
    instance.codex_model = 'gpt-6-astra'
    instance.codex_sandbox_mode = 'read-only'
    instance.codex_reasoning_effort = effort
    monkeypatch.setattr(instance, '_get_codex_bin', lambda: 'codex')
    run = Mock(return_value=SimpleNamespace(returncode=0, stderr='', stdout=(
        '{"type":"item.completed","item":{"type":"agent_message","text":"Готово"}}')))
    monkeypatch.setattr(module, 'run_bounded', run)

    assert instance._run_codex_exec('Привет', read_only=True) == 'Готово'
    command = run.call_args.args[0]
    assert (f'model_reasoning_effort="{effort}"' in command) == bool(effort)
    assert ('-c' in command) == bool(effort)


@pytest.mark.parametrize('button', [buttons.btn_chat, buttons.btn_work])
async def test_save_failure_does_not_report_success(monkeypatch, button):
    monkeypatch.setattr(buttons, 'get_settings', lambda: SimpleNamespace(
        ai_backend='codex', admin_user_ids=[7]))
    monkeypatch.setenv('CODEX_REASONING_EFFORT', 'xhigh')
    monkeypatch.setattr(buttons, '_replace_env_value', Mock(side_effect=OSError('read-only')))
    state = AsyncMock()
    message = SimpleNamespace(from_user=SimpleNamespace(id=7), answer=AsyncMock())
    await button(message, state)
    assert os.environ['CODEX_REASONING_EFFORT'] == 'xhigh'
    state.set_state.assert_not_called()
    assert 'Не удалось' in message.answer.call_args.args[0]


def test_keyboard_replaces_request_button():
    labels = [button.text for row in get_main_keyboard().keyboard for button in row]
    assert CHAT_BUTTON in labels
    assert '✨ Запрос' not in labels

    assert WORK_BUTTON in labels
    assert '📊 Статус' not in labels
