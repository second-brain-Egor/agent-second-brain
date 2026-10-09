"""8 October 2026: the bot no longer searches the web or deletes files on its own.

At 18:49 Egor asked by voice to switch off web search and deletion; the voice message
itself was caught by the search fast-path and answered with irrelevant links.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from d_brain.services.session import SessionStore


def message(text, number=201):
    return Message(message_id=number, date=datetime.now(timezone.utc),
                   chat=Chat(id=7, type='private'),
                   from_user=User(id=7, is_bot=False, first_name='Егор'), text=text)


@pytest.mark.parametrize('text', [
    'А я думаю, почему поиск в интернете так работает плохо? Отключи у бота, в том числе, '
    'и поиск в интернете, и удаление тоже отключи. Этим будешь заниматься ты.',
    'Найди цены на осб в интернете',
    'Погугли расписание электричек',
])
def test_search_requests_go_to_assistant(text):
    from d_brain.bot.handlers.web import matches_web_intent
    assert not matches_web_intent(text)


def test_switch_still_controls_old_fast_path(monkeypatch):
    import d_brain.bot.handlers.web as web
    monkeypatch.setattr(web, 'AUTOMATIC_SEARCH', True)
    assert web.matches_web_intent('Найди цены на осб в интернете')


async def test_web_command_does_not_search(monkeypatch):
    import d_brain.bot.handlers.web as web
    search = AsyncMock()
    monkeypatch.setattr(web, 'run_web_search', search)
    monkeypatch.setattr(Message, 'answer', AsyncMock())
    await web.handle_web_command(message('/web цена осб-3 9мм'))
    search.assert_not_called()
    Message.answer.assert_awaited_once()


async def test_delete_word_reaches_assistant_and_keeps_file(tmp_path, monkeypatch):
    import d_brain.bot.handlers.document as document
    import d_brain.bot.handlers.text as text
    monkeypatch.setattr(text, 'get_settings', lambda: SimpleNamespace(
        vault_path=tmp_path, work_chat_ids=[], treat_all_group_chats_as_work=False))
    reached = AsyncMock(return_value=True)
    monkeypatch.setattr(document, 'route_document_request', reached)
    monkeypatch.setattr(Message, 'answer', AsyncMock())

    photo = tmp_path / 'attachments' / '2026-10-08' / 'photo.jpg'
    photo.parent.mkdir(parents=True)
    photo.write_bytes(b'jpg')
    SessionStore(tmp_path).append(7, 'photo', path='attachments/2026-10-08/photo.jpg')

    await text.handle_text(message('Удали это'), state=None, bot=None)

    assert photo.exists()
    reached.assert_awaited_once()
    Message.answer.assert_not_called()
