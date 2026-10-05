"""Button selections reach both CLI routes and survive a settings reload."""
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from d_brain.bot.handlers import backend, buttons
from d_brain.bot.keyboards import (
    ACTIVE_CHAT_BUTTON, ACTIVE_WORK_BUTTON, CHAT_BUTTON, WORK_BUTTON, get_main_keyboard,
)
from d_brain.bot.states import DoCommandState
from d_brain.config import Settings
from d_brain.services import processor as module


@pytest.mark.parametrize('button,effort,model', [
    (buttons.btn_chat, 'max', 'gpt-6.1-sol'),
    (buttons.btn_work, 'xhigh', 'gpt-6-astra'),
])
@pytest.mark.parametrize('active,key', [('codex', 'CODEX_REASONING_EFFORT'), ('claude', 'CLAUDE_EFFORT')])
async def test_button_persists_effort_and_leaves_do_mode(tmp_path, monkeypatch, active, key, button, effort, model):
    env_path = tmp_path / '.env'
    original = (f'AI_BACKEND={active}\nPROCESS_BACKEND={active}\n'
                f'CODEX_MODEL=gpt-6-astra\n{key}=high\n'
                'CODEX_MODEL_CHAT=old-chat\nCODEX_MODEL_AGENT=old-agent\n'
                'TELEGRAM_BOT_TOKEN=test\nDEEPGRAM_API_KEY=test\n')
    env_path.write_text(original)
    keys = ('AI_BACKEND', 'PROCESS_BACKEND', 'CODEX_MODEL', 'CODEX_MODEL_CHAT',
            'CODEX_MODEL_AGENT', 'CODEX_REASONING_EFFORT', 'CLAUDE_EFFORT',
            'CLAUDE_MODEL', 'CLAUDE_MODEL_CHAT', 'CLAUDE_MODEL_AGENT')
    for name in keys:
        monkeypatch.setenv(name, 'high' if name == key else '')
    monkeypatch.setenv('AI_BACKEND', active)
    monkeypatch.setenv('PROCESS_BACKEND', active)
    monkeypatch.setattr(backend, 'ENV_PATH', env_path)
    monkeypatch.setattr(buttons, 'get_settings', lambda: SimpleNamespace(
        ai_backend=active, admin_user_ids=[7]))
    monkeypatch.setattr('d_brain.bot.keyboards.get_settings', lambda: Settings(_env_file=env_path))
    state = FSMContext(MemoryStorage(), StorageKey(bot_id=1, chat_id=7, user_id=7))
    await state.set_state(DoCommandState.waiting_for_input)
    await state.update_data(voice_mode=True)
    message = SimpleNamespace(from_user=SimpleNamespace(id=7), answer=AsyncMock())

    await button(message, state)

    effort = effort if active == 'claude' else 'max'
    assert f'{key}={effort}' in env_path.read_text()
    assert os.environ[key] == effort
    assert await state.get_state() is None
    assert (await state.get_data())['voice_mode'] is True
    assert 'TELEGRAM_BOT_TOKEN=test' in env_path.read_text()
    assert f'PROCESS_BACKEND={active}' in env_path.read_text()
    if active == 'claude':
        assert 'CODEX_MODEL=gpt-6-astra' in env_path.read_text()
        assert 'CODEX_MODEL_CHAT=old-chat' in env_path.read_text()
    # Check live settings and a restart without inherited environment overrides.
    for restarted in (False, True):
        if restarted:
            for name in keys:
                monkeypatch.delenv(name, raising=False)
        settings = Settings(_env_file=env_path)
        assert settings.ai_backend == settings.process_backend == active
        monkeypatch.setattr('d_brain.config.get_settings', lambda: settings)
        instance = module.AgentProcessor(tmp_path / 'vault', '')
        assert getattr(instance, 'claude_effort' if active == 'claude' else 'codex_reasoning_effort') == effort
        if active == 'codex':
            for mode in ('chat', 'agent'):
                assert instance._backend_model_for_mode(mode) == model
            run = Mock(return_value=SimpleNamespace(returncode=0, stderr='', stdout=(
                '{"type":"item.completed","item":{"type":"agent_message","text":"Готово"}}')))
            monkeypatch.setattr(module, 'run_bounded', run)
            monkeypatch.setattr(instance, '_get_codex_bin', lambda: 'codex')
            for mode in ('chat', 'agent'):
                instance._run_codex_exec('Проверка', read_only=True,
                                         model=instance._backend_model_for_mode(mode))
                command = run.call_args.args[0]
                assert command[command.index('--model') + 1] == model
                assert 'model_reasoning_effort="max"' in command
        else:
            expected = 'claude-opus-5-5' if button == buttons.btn_work else 'claude-sonnet-5-5'
            assert instance._backend_model_for_mode('chat') == expected
            assert instance._backend_model_for_mode('agent') == expected


@pytest.mark.parametrize('effort', ['', 'medium', 'xhigh', 'max'])
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
    monkeypatch.setenv('CODEX_MODEL', 'previous-model')
    monkeypatch.setattr(buttons, '_replace_env_values', Mock(side_effect=OSError('read-only')))
    state = AsyncMock()
    message = SimpleNamespace(from_user=SimpleNamespace(id=7), answer=AsyncMock())
    await button(message, state)
    assert os.environ['CODEX_REASONING_EFFORT'] == 'xhigh'
    assert os.environ['CODEX_MODEL'] == 'previous-model'
    state.set_state.assert_not_called()
    assert 'Не удалось' in message.answer.call_args.args[0]


def test_keyboard_replaces_request_button():
    labels = [button.text for row in get_main_keyboard().keyboard for button in row]
    assert CHAT_BUTTON in labels or ACTIVE_CHAT_BUTTON in labels
    assert '✨ Запрос' not in labels

    assert WORK_BUTTON in labels or ACTIVE_WORK_BUTTON in labels
    assert '📊 Статус' not in labels


@pytest.mark.parametrize('active,model,effort,selected', [
    ('codex', 'gpt-6-astra', 'max', ACTIVE_WORK_BUTTON),
    ('codex', 'gpt-6.1-sol', 'max', ACTIVE_CHAT_BUTTON),
    ('codex', 'gpt-6-astra', 'xhigh', None),
    ('codex', 'gpt-6.1-sol', 'medium', None),
    ('codex', 'another-model', 'max', None),
    ('claude', 'gpt-6-astra', 'max', ACTIVE_CHAT_BUTTON),
    ('claude', 'gpt-6.1-sol', 'xhigh', ACTIVE_WORK_BUTTON),
    ('claude', 'gpt-6-astra', 'medium', None),
])
@pytest.mark.parametrize('explicit_chat_model', [False, True])
def test_keyboard_serializes_only_active_backend_selection(monkeypatch, active, model, effort, selected, explicit_chat_model):
    from d_brain.bot import keyboards

    monkeypatch.setattr(keyboards, 'get_settings', lambda: SimpleNamespace(
        ai_backend=active,
        claude_effort=effort if active == 'claude' else 'xhigh',
        codex_reasoning_effort=effort if active == 'codex' else 'medium',
        codex_model='other-model' if explicit_chat_model else model,
        codex_model_chat=model if explicit_chat_model else '',
        temporary_chat_user_id=0, show_help_button=False,
    ))
    markup = get_main_keyboard().model_dump(exclude_none=True)
    assert [len(row) for row in markup['keyboard']] == [3, 3]
    labels = [b['text'] for row in markup['keyboard'] for b in row]
    assert [label for label in labels if label in {ACTIVE_CHAT_BUTTON, ACTIVE_WORK_BUTTON}] == ([selected] if selected else [])
    assert labels[1] == ('🧠 Claude ✓' if active == 'claude' else '🧠 Claude')
    assert labels[4] == ('🤖 Codex ✓' if active == 'codex' else '🤖 Codex')
    assert labels[0] == (ACTIVE_WORK_BUTTON if selected == ACTIVE_WORK_BUTTON else WORK_BUTTON)
    assert labels[3] == (ACTIVE_CHAT_BUTTON if selected == ACTIVE_CHAT_BUTTON else CHAT_BUTTON)
    assert all('style' not in b for row in markup['keyboard'] for b in row)


async def test_non_admin_cannot_change_model(monkeypatch):
    monkeypatch.setattr(buttons, 'get_settings', lambda: SimpleNamespace(
        ai_backend='codex', admin_user_ids=[7]))
    save = Mock()
    monkeypatch.setattr(buttons, '_replace_env_values', save)
    state = AsyncMock()
    message = SimpleNamespace(from_user=SimpleNamespace(id=8), answer=AsyncMock())
    await buttons.btn_work(message, state)
    save.assert_not_called()
    state.set_state.assert_not_called()


def test_failed_atomic_save_preserves_complete_previous_selection(tmp_path, monkeypatch):
    from pathlib import Path
    env_path = tmp_path / '.env'
    original = 'CODEX_MODEL=gpt-6-astra\nCODEX_REASONING_EFFORT=xhigh\nSECRET=untouched\n'
    env_path.write_text(original)
    monkeypatch.setattr(backend, 'ENV_PATH', env_path)
    monkeypatch.setattr(Path, 'replace', Mock(side_effect=OSError('disk error')))
    with pytest.raises(OSError):
        backend._replace_env_values({'CODEX_MODEL': 'gpt-6.1-sol', 'CODEX_REASONING_EFFORT': 'max'})
    assert env_path.read_text() == original
    assert list(tmp_path.iterdir()) == [env_path]
