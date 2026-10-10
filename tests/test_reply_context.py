"""9 October 2026: replies to a specific message.

At 07:05 Egor answered «Почему?» with Telegram's «Reply» to the message about Nate Herk;
the bot saw only the bare word and answered about DASH. Now the quoted message goes into the
request. At 08:38 Egor narrowed the other half: the bot's answer comes back as a Telegram reply
only when three messages have passed since the question; in a live dialogue it is a plain message.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

from aiogram.types import Chat, Message, TextQuote, User, Voice

from d_brain.bot.chat_context import messages_since, reply_log, reply_prompt, send_chunks, send_reply
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore

CHAT = Chat(id=7, type='private')
EGOR = User(id=7, is_bot=False, first_name='Егор')
BOT = User(id=99, is_bot=True, first_name='Бот')
AT = datetime(2026, 10, 9, 4, 7, tzinfo=timezone.utc)  # 07:07 по Москве


def message(text, number=301, reply=None, quote=None):
    return Message(message_id=number, date=datetime.now(timezone.utc), chat=CHAT,
                   from_user=EGOR, text=text, reply_to_message=reply, quote=quote)


def bot_message(text, number=300):
    return Message(message_id=number, date=AT, chat=CHAT, from_user=BOT, text=text)


def test_plain_message_is_unchanged(tmp_path):
    assert reply_prompt(message('Почему?'), 'Почему?', tmp_path) == 'Почему?'
    assert reply_log(message('Почему?'), tmp_path) is None


def test_reply_to_bot_message_carries_the_quote(tmp_path):
    reply = bot_message('📺 Скачать ролики Нейта не получилось: YouTube потребовал подтверждение.')
    prompt = reply_prompt(message('Почему?', reply=reply), 'Почему?', tmp_path)
    assert prompt.startswith('[Ответ на твоё сообщение от ')
    assert 'Скачать ролики Нейта не получилось' in prompt
    assert prompt.endswith('\n\nПочему?')


def test_selected_fragment_wins_over_full_text(tmp_path):
    reply = bot_message('Первый абзац про DASH.\n\nВторой абзац про Нейта.')
    quote = TextQuote(text='Второй абзац про Нейта.', position=24, is_manual=True)
    prompt = reply_prompt(message('Почему?', reply=reply, quote=quote), 'Почему?', tmp_path)
    assert 'выделенный фрагмент' in prompt
    assert 'Второй абзац про Нейта.' in prompt
    assert 'DASH' not in prompt


def test_reply_to_own_voice_uses_saved_transcript(tmp_path):
    SessionStore(tmp_path).append(7, 'voice', text='Сколько стоит доска?', msg_id=250, chat_id=7)
    voice = Message(message_id=250, date=AT, chat=CHAT, from_user=EGOR,
                    voice=Voice(file_id='v', file_unique_id='u', duration=3))
    prompt = reply_prompt(message('А теперь?', reply=voice), 'А теперь?', tmp_path)
    assert '[Ответ на своё сообщение от ' in prompt
    assert 'голосовое: «Сколько стоит доска?»' in prompt


def test_session_log_shows_what_was_answered(tmp_path):
    reply = bot_message('Очень длинный ответ ' * 50)
    note = reply_log(message('Почему?', reply=reply), tmp_path)
    assert note.startswith(f"{AT.astimezone().strftime('%H:%M')} assistant: «Очень длинный ответ")
    assert len(note) < 260
    rendered = AgentProcessor._render_session_entry(
        {'ts': '2026-10-09T07:05:00+03:00', 'type': 'text', 'text': 'Почему?', 'reply_to': note})
    assert rendered.startswith('07:05 [text] (ответ на ')
    assert rendered.endswith(') Почему?')


def log_question(path, number=301):
    SessionStore(path).append(7, 'text', text='Почему?', msg_id=number, chat_id=7)


def log_later(path, count):
    for index in range(count):
        SessionStore(path).append(7, 'assistant' if index % 2 else 'text', text=f'потом {index}', chat_id=7)


async def test_live_dialogue_answer_is_plain(tmp_path, monkeypatch):
    monkeypatch.setattr(Message, 'reply', AsyncMock())
    monkeypatch.setattr(Message, 'answer', AsyncMock())
    log_question(tmp_path)
    log_later(tmp_path, 2)
    SessionStore(tmp_path).append(7, 'assistant', text='первый\n\nвторой', chat_id=7)  # свой ответ
    await send_chunks(message('Почему?'), ['первый', 'второй'], tmp_path)
    Message.reply.assert_not_awaited()
    assert [call.args[0] for call in Message.answer.await_args_list] == ['первый', 'второй']


async def test_answer_after_three_messages_is_a_reply(tmp_path, monkeypatch):
    monkeypatch.setattr(Message, 'reply', AsyncMock())
    monkeypatch.setattr(Message, 'answer', AsyncMock())
    log_question(tmp_path)
    log_later(tmp_path, 3)
    SessionStore(tmp_path).append(7, 'assistant', text='[agent-done] первый\n\nвторой', chat_id=7)
    await send_chunks(message('Почему?'), ['первый', 'второй'], tmp_path)
    Message.reply.assert_awaited_once_with('первый', allow_sending_without_reply=True)
    Message.answer.assert_awaited_once_with('второй')


async def test_single_message_follows_the_same_rule(tmp_path, monkeypatch):
    monkeypatch.setattr(Message, 'reply', AsyncMock())
    monkeypatch.setattr(Message, 'answer', AsyncMock())
    log_question(tmp_path)
    await send_reply(message('Почему?'), '⚠️ ошибка', tmp_path, parse_mode=None)
    Message.answer.assert_awaited_once_with('⚠️ ошибка', parse_mode=None)
    log_later(tmp_path, 3)
    await send_reply(message('Почему?'), '⚠️ ошибка', tmp_path, parse_mode=None)
    Message.reply.assert_awaited_once_with('⚠️ ошибка', allow_sending_without_reply=True, parse_mode=None)


def test_count_ignores_other_chats_and_service_lines(tmp_path):
    log_question(tmp_path)
    SessionStore(tmp_path).append(7, 'text', text='из группы', chat_id=-100)
    SessionStore(tmp_path).append(7, 'photo_batch', text='[photo_batch] 3 фото', chat_id=7)
    SessionStore(tmp_path).append(7, 'assistant', text='ответ', chat_id=7)
    assert messages_since(message('Почему?'), tmp_path) == 1
    assert messages_since(message('Почему?', number=999), tmp_path) == 0  # нет в журнале — без реплая


async def test_text_handler_sends_quote_to_model_and_answers_plainly(tmp_path, monkeypatch):
    import d_brain.bot.handlers.document as document
    import d_brain.bot.handlers.text as text
    monkeypatch.setattr(text, 'get_settings', lambda: SimpleNamespace(
        vault_path=tmp_path, todoist_api_key='', work_chat_ids=[],
        treat_all_group_chats_as_work=False))
    monkeypatch.setattr(document, 'route_document_request', AsyncMock(return_value=False))
    monkeypatch.setattr(text, 'maybe_evening_reminder', lambda _: None)
    seen = {}

    def fake_prompt(self, prompt, user_id, **kwargs):
        seen['prompt'] = prompt
        return {'report': 'Потому что YouTube закрыл адрес сервера.'}

    monkeypatch.setattr(AgentProcessor, 'execute_raw_prompt', fake_prompt)
    monkeypatch.setattr(Message, 'reply', AsyncMock())
    monkeypatch.setattr(Message, 'answer', AsyncMock())

    reply = bot_message('📺 Скачать ролики Нейта не получилось.')
    await text.handle_text(message('Почему?', reply=reply), state=None, bot=None)

    assert 'Скачать ролики Нейта не получилось' in seen['prompt']
    Message.reply.assert_not_awaited()  # ответ сразу следом за вопросом — без реплая
    assert 'YouTube закрыл' in Message.answer.await_args.args[0]
    logged = SessionStore(tmp_path).get_recent(7)
    assert logged[0]['reply_to'].endswith('assistant: «📺 Скачать ролики Нейта не получилось.»')
