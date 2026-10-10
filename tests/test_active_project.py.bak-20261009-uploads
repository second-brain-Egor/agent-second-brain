"""Текущий проект беседы (Егор, 8 октября 2026).

Бот помнит, в каком проекте идёт работа, и кладёт туда документы и фото без вопросов.
Место каждого такого файла помощник проверяет в следующем ответе; без проекта бот спрашивает
папку кнопками последних проектов, и выбранный проект становится текущим.
"""
from __future__ import annotations

import asyncio
import io
import subprocess
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Document, Message, User

from d_brain.services.documents import ACTIVE_HOURS, DocumentStore

OWNER = User(id=7, is_bot=False, first_name='Егор')


def projects(vault: Path):
    irina = vault/'projects'/'Ирина работа'
    (irina/'Приводи своих друзей').mkdir(parents=True)
    (irina/'Журнал документов.md').write_text('# Журнал\n\n## Записи\n\n- старт\n', encoding='utf-8')
    (vault/'projects'/'dacha').mkdir()
    return irina


@pytest.fixture
def bot_env(tmp_path, monkeypatch):
    import d_brain.bot.handlers.document as module
    settings = SimpleNamespace(vault_path=tmp_path, treat_all_group_chats_as_work=True, work_chat_ids=[])
    monkeypatch.setattr(module, 'get_settings', lambda: settings)
    answers = AsyncMock()
    monkeypatch.setattr(Message, 'answer', answers)
    monkeypatch.setattr(Message, 'edit_reply_markup', AsyncMock())
    handed = []

    async def assistant(message, state=None, bot=None):
        handed.append(message.text)
    monkeypatch.setattr('d_brain.bot.handlers.text.handle_text', assistant)
    projects(tmp_path)
    return SimpleNamespace(module=module, answers=answers, store=DocumentStore(tmp_path), handed=handed)


def upload(number, name='Условия.pdf', data=b'%PDF one', caption=None):
    message = Message(message_id=number, date=datetime.now(timezone.utc), chat=Chat(id=7, type='private'),
                      from_user=OWNER, caption=caption,
                      document=Document(file_id=f'f{number}', file_unique_id=f'u{number}', file_name=name))
    bot = SimpleNamespace(get_file=AsyncMock(return_value=SimpleNamespace(file_path='file')),
                          download_file=AsyncMock(return_value=io.BytesIO(data)))
    return message, bot


def said(env):
    return [call.args[0] for call in env.answers.call_args_list]


def buttons(env):
    markup = env.answers.call_args.kwargs.get('reply_markup')
    return [b.text for row in markup.inline_keyboard for b in row] if markup else []


def click(env, data, message_id=500):
    message = Message(message_id=message_id, date=datetime.now(timezone.utc), chat=Chat(id=7, type='private'),
                      from_user=User(id=99, is_bot=True, first_name='Бот'), text='📄 Куда сохранить')
    return SimpleNamespace(data=data, answer=AsyncMock(), from_user=OWNER, message=message)


async def test_current_project_takes_document_without_questions(bot_env):
    env = bot_env
    env.store.set_active(7, 'ирина работа', 'Приводи своих друзей')
    await env.module.handle_document(*upload(11))
    doc = env.store.for_scope(7)[0]
    assert doc['path'] == 'projects/Ирина работа/Приводи своих друзей/Условия.pdf'
    assert len(said(env)) == 1 and not buttons(env)
    assert 'проект «Ирина работа», подпроект «Приводи своих друзей»' in said(env)[0]
    assert said(env)[0].endswith('Что сделать по документу?')
    # The assistant sees the file as unchecked in its next prompt and checks the place.
    context = env.store.context(7)
    assert 'Работаем в проекте: Ирина работа / Приводи своих друзей' in context
    assert '=== НОВЫЕ ФАЙЛЫ: ПРОВЕРЬ МЕСТО ===\n- projects/Ирина работа/Приводи своих друзей/Условия.pdf' in context
    env.store.mark_checked([p['id'] for p in env.store.unchecked(7)])
    assert 'ПРОВЕРЬ МЕСТО' not in env.store.context(7)


async def test_caption_task_goes_to_assistant_after_placing(bot_env):
    env = bot_env
    env.store.set_active(7, 'dacha')
    await env.module.handle_document(*upload(12, caption='Сравни со сметой'))
    assert env.store.for_scope(7)[0]['path'] == 'projects/dacha/Условия.pdf'
    assert env.handed == ['Сравни со сметой']


async def test_without_project_recent_projects_are_buttons_and_choice_becomes_current(bot_env):
    env = bot_env
    await env.module.handle_document(*upload(13))
    assert 'Куда сохранить «Условия.pdf»' in said(env)[-1]
    shown = buttons(env)
    assert set(shown[:2]) == {'📁 Ирина работа', '📁 dacha'}
    assert shown[2:] == ['📋 Все проекты', 'В папку PDF']
    doc = env.store.for_scope(7)[0]
    dacha = shown.index('📁 dacha')
    await env.module.choose_project(click(env, f"docproj:{doc['id']}:{dacha}"))
    # No subprojects in «dacha»: straight to its root, no second question.
    assert env.store.get(doc['id'])['path'] == 'projects/dacha/Условия.pdf'
    assert 'Следующие файлы кладу сюда же' in said(env)[-1]
    assert env.store.active_project(7) == {'project': 'dacha', 'subproject': None}
    await env.module.handle_document(*upload(14, name='Смета.pdf', data=b'%PDF two'))
    assert env.store.for_scope(7)[0]['path'] == 'projects/dacha/Смета.pdf'
    assert 'Следующие файлы' not in said(env)[-1]


async def test_all_projects_button_shows_every_project(bot_env):
    env = bot_env
    for name in ('a', 'b', 'c', 'd', 'e'):
        (env.store.vault/'projects'/name).mkdir()
    await env.module.handle_document(*upload(15))
    assert len(buttons(env)) == 5 + 2
    doc = env.store.for_scope(7)[0]
    callback = click(env, f"docproj:{doc['id']}:all")
    await env.module.choose_project(callback)
    markup = callback.message.edit_reply_markup.call_args.kwargs['reply_markup']
    names = [b.text for row in markup.inline_keyboard for b in row]
    assert len(names) == 7 + 1 and names[-1] == 'В папку PDF'


async def test_spoken_project_name_then_subproject_sets_current(bot_env):
    env = bot_env
    await env.module.handle_document(*upload(16))
    doc = env.store.for_scope(7)[0]
    reply = Message(message_id=17, date=datetime.now(timezone.utc), chat=Chat(id=7, type='private'),
                    from_user=OWNER, text='В ирина работа.')
    assert await env.module.route_document_request(reply, 'В ирина работа.')
    assert buttons(env) == ['📁 Приводи своих друзей', 'В корень «Ирина работа»', '➕ Новый подпроект']
    await env.module.choose_subproject(click(env, f"docsub:{doc['id']}:0"))
    assert env.store.get(doc['id'])['path'] == 'projects/Ирина работа/Приводи своих друзей/Условия.pdf'
    assert env.store.active_project(7) == {'project': 'Ирина работа', 'subproject': 'Приводи своих друзей'}


async def test_stale_project_asks_again_with_it_first(bot_env):
    env = bot_env
    (env.store.vault/'projects'/'dacha'/'новый.md').write_text('свежее', encoding='utf-8')
    env.store.set_active(7, 'Ирина работа')
    with env.store.db() as db:
        db.execute('UPDATE active_project SET updated=updated-?', (ACTIVE_HOURS * 3600 + 60,))
    assert env.store.active_project(7) is None
    await env.module.handle_document(*upload(18))
    assert env.store.for_scope(7)[0]['state'] == 'destination'
    assert buttons(env)[0] == '📁 Ирина работа'


def test_move_carries_service_folder_and_updates_records(tmp_path):
    irina = projects(tmp_path)
    store = DocumentStore(tmp_path)
    store.set_active(7, 'Ирина работа')
    doc, _ = store.receive(b'%PDF', 'Зарплата.pdf', 7, 7, 1)
    doc = store.place(doc['id'], 'Ирина работа')
    store.record_placement(7, doc['path'], 'document')
    meta = irina/'.служебное'/'Зарплата'
    (meta/'текст.txt').write_text('текст', encoding='utf-8')
    moved = store.move(doc['path'], 'Ирина работа', 'Приводи своих друзей')
    assert moved == 'projects/Ирина работа/Приводи своих друзей/Зарплата.pdf'
    assert (tmp_path/moved).is_file() and not (irina/'Зарплата.pdf').exists()
    assert (irina/'Приводи своих друзей'/'.служебное'/'Зарплата'/'текст.txt').read_text(encoding='utf-8') == 'текст'
    assert store.get(doc['id'])['path'] == moved
    assert store.unchecked(7)[0]['path'] == moved
    away = store.move(moved, None)
    assert away.startswith('attachments/') and (tmp_path/away).is_file()


def test_script_sets_lists_and_clears_project(tmp_path):
    projects(tmp_path)
    root = Path(__file__).resolve().parents[1]

    def run(*args):
        env = {'PATH': '/usr/bin:/bin', 'VAULT_PATH': str(tmp_path), 'TELEGRAM_BOT_TOKEN': 'test',
               'DEEPGRAM_API_KEY': 'test', 'HOME': str(tmp_path)}
        return subprocess.run([sys.executable, str(root/'scripts'/'project_context.py'), '--scope', '7', *args],
                              capture_output=True, text=True, env=env, cwd=tmp_path)
    assert run('set', 'нет такого').returncode == 1
    done = run('set', 'ирина работа', 'приводи своих друзей')
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == 'Текущий проект: Ирина работа / Приводи своих друзей'
    assert DocumentStore(tmp_path).active_project(7)['subproject'] == 'Приводи своих друзей'
    listed = run('list').stdout
    assert 'Ирина работа — подпроекты: Приводи своих друзей' in listed and 'dacha' in listed
    assert run('clear').returncode == 0
    assert DocumentStore(tmp_path).active_project(7) is None


async def test_photo_goes_to_current_project(tmp_path, monkeypatch):
    from d_brain.bot.handlers import photo as module
    from d_brain.config import Settings
    settings = Settings(_env_file=None, vault_path=tmp_path, telegram_bot_token='test',
                        deepgram_api_key='test', allowed_user_ids=[7], work_chat_ids=[],
                        treat_all_group_chats_as_work=True)
    monkeypatch.setattr(module, 'get_settings', lambda: settings)
    monkeypatch.setattr(module, 'BATCH_WINDOW_SECONDS', 0.2)

    @asynccontextmanager
    async def typing(*args):
        yield
    monkeypatch.setattr(module, 'keep_typing', typing)
    monkeypatch.setattr(module, '_analyze_image', AsyncMock(return_value='описание'))
    projects(tmp_path)
    DocumentStore(tmp_path).set_active(7, 'dacha')
    message = SimpleNamespace(message_id=21, photo=[SimpleNamespace(file_id='p')], caption=None,
                              date=datetime.now(timezone.utc), media_group_id=None, from_user=SimpleNamespace(id=7),
                              chat=SimpleNamespace(id=7, type='private', title=None), answer=AsyncMock())
    bot = SimpleNamespace(get_file=AsyncMock(return_value=SimpleNamespace(file_path='photos/p.jpg')),
                          download_file=AsyncMock(return_value=io.BytesIO(b'jpeg')))
    module._batches.clear()
    await module.handle_photo(message, bot)
    await asyncio.sleep(0.6)
    saved = list((tmp_path/'projects'/'dacha').glob('фото *.jpg'))
    assert len(saved) == 1 and not [p for p in (tmp_path/'attachments').rglob('*') if p.is_file()]
    assert message.answer.call_args.args[0] == '📸 Фото положил в корень проекта «dacha». Что с ним сделать?'
    assert DocumentStore(tmp_path).unchecked(7)[0]['kind'] == 'photo'


def test_reply_marks_files_checked_only_after_success(tmp_path, monkeypatch):
    from d_brain.services import processor as module
    projects(tmp_path)
    store = DocumentStore(tmp_path)
    store.set_active(7, 'dacha')
    store.record_placement(7, 'projects/dacha/фото.jpg', 'photo')
    chat = object.__new__(module.AgentProcessor)
    chat.vault_path = tmp_path
    chat.project_path = tmp_path
    monkeypatch.setattr(chat, '_get_memory_context', lambda **kwargs: 'память')
    monkeypatch.setattr('d_brain.services.memory_rag.search_memory', lambda query, limit=5: '')
    prompts = []

    def broken(system, user, **kwargs):
        prompts.append(user)
        raise RuntimeError('сбой')
    monkeypatch.setattr(chat, '_run_chat', broken)
    assert 'error' in chat.execute_raw_prompt('Привет', 7, session_scope=7)
    assert 'projects/dacha/фото.jpg' in prompts[0] and store.unchecked(7)
    monkeypatch.setattr(chat, '_run_chat', lambda system, user, **kwargs: 'Привет')
    assert chat.execute_raw_prompt('Ещё раз', 7, session_scope=7)['report'] == 'Привет'
    assert not store.unchecked(7)
