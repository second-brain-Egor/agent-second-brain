from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
import json

import pytest
from aiogram import Bot
from aiogram.types import CallbackQuery, Chat, Message, User

from d_brain.services.documents import DocumentStore
from d_brain.services.presentations import PresentationChoices, explicit_format, format_reply
from d_brain.services.document_jobs import process_job, deliver_job
from d_brain.services.document_output import output_format


def message(text, number=101, user=7, reply=None):
    return Message(message_id=number, date=datetime.now(timezone.utc),
                   chat=Chat(id=7, type='private'),
                   from_user=User(id=user, is_bot=False, first_name='Ирина'),
                   text=text, reply_to_message=reply)


@pytest.fixture
def handler(tmp_path, monkeypatch):
    import d_brain.bot.handlers.document as module
    monkeypatch.setattr(module, 'get_settings', lambda: SimpleNamespace(vault_path=tmp_path))
    monkeypatch.setattr(Message, 'answer', AsyncMock(return_value=SimpleNamespace(message_id=500)))
    monkeypatch.setattr(Message, 'edit_reply_markup', AsyncMock())
    monkeypatch.setattr(CallbackQuery, 'answer', AsyncMock())
    return module


def document(tmp_path):
    store = DocumentStore(tmp_path)
    doc, _ = store.receive(b'Presentation source', 'source.txt', 7, 7, 100)
    return store, store.place(doc['id'])


@pytest.mark.parametrize('text,expected', [
    ('PowerPoint', 'pptx'), ('Пауэр Поинт', 'pptx'), ('Poyer Point', 'pptx'),
    ('В формате PowerPoint', 'pptx'), ('pptx', 'pptx'), ('PDF', 'pdf'),
    ('В пдф, пожалуйста', 'pdf'), ('В проект Банк', None),
])
def test_spoken_and_written_answers(text, expected):
    assert format_reply(text) == expected


@pytest.mark.parametrize('text,expected', [
    ('Сделай презентацию по PDF', None),
    ('Подготовь слайды из source.pdf', None),
    ('Сделай презентацию по PDF в PowerPoint', 'pptx'),
    ('Сделай презентацию по source.pdf в PDF', 'pdf'),
    ('Нужна презентация PowerPoint', 'pptx'),
    ('Сделай презентацию в PDF или PowerPoint', None),
    ('Сделай презентацию в PowerPoint или PDF', None),
])
def test_output_format_distinguishes_source(text, expected):
    assert explicit_format(text) == expected


@pytest.mark.parametrize('fmt', ['pptx', 'pdf'])
async def test_choice_survives_restart_and_delivers_selected_file(tmp_path, handler, fmt):
    store, doc = document(tmp_path)
    request = 'Подготовь 2 слайда по документу'
    assert await handler.route_document_request(message(request), request)
    assert not store.jobs(('queued',))
    pending = PresentationChoices(DocumentStore(tmp_path)).pending(7, 7)
    assert pending['request'] == request and pending['doc_id'] == doc['id']
    markup = Message.answer.call_args.kwargs['reply_markup']
    assert [b.text for b in markup.inline_keyboard[0]] == ['PowerPoint (.pptx)', 'PDF']
    store.recover()
    # The same function handles text and recognized voice answers.
    assert await handler.route_document_request(message(fmt, 102), fmt)
    job = store.latest_job(doc['id'])
    assert job['request'].startswith(request) and output_format(job['request']) == fmt
    assert PresentationChoices(store).pending(7, 7) is None
    answer = {'slides': [{'title': f'Тема {i}', 'bullets': ['Тезис'], 'sources': 'Документ, стр. 1'}
                         for i in range(2)]}
    process_job(store, job, SimpleNamespace(_run_backend_exec=Mock(return_value=json.dumps(answer))))
    job = store.job(job['id'])
    assert job['state'] == 'ready' and job['artifact'].endswith('.' + fmt)
    bot = SimpleNamespace(send_document=AsyncMock(return_value=SimpleNamespace(message_id=600)))
    await deliver_job(store, job, bot)
    assert bot.send_document.call_args.kwargs['document'].path.suffix == '.' + fmt
    assert store.job(job['id'])['state'] == 'sent'


async def test_callback_scoped_and_idempotent(tmp_path, handler):
    store, doc = document(tmp_path)
    await handler.route_document_request(message('Сделай презентацию'), 'Сделай презентацию')
    pending = PresentationChoices(store).pending(7, 7)
    query = CallbackQuery(id='q', from_user=User(id=8, is_bot=False, first_name='Другой'),
                          chat_instance='c', message=message('В каком формате?', 500),
                          data=f"presformat:{pending['id']}:pptx")
    await handler.choose_presentation_format(query)
    assert not store.jobs(('queued',))
    query = query.model_copy(update={'from_user': message('').from_user})
    await handler.choose_presentation_format(query)
    await handler.choose_presentation_format(query)
    assert len(store.jobs(('queued',))) == 1
    assert output_format(store.latest_job(doc['id'])['request']) == 'pptx'


@pytest.mark.parametrize('fmt', ['PowerPoint', 'PDF'])
async def test_explicit_format_does_not_ask(tmp_path, handler, fmt):
    store, doc = document(tmp_path)
    request = 'Сделай презентацию в ' + fmt
    assert await handler.route_document_request(message(request), request)
    assert store.latest_job(doc['id'])['state'] == 'queued'
    assert PresentationChoices(store).pending(7, 7) is None
    assert 'В каком формате' not in Message.answer.call_args.args[0]


async def test_unrelated_text_and_reply_do_not_select_format(tmp_path, handler):
    store, _ = document(tmp_path)
    await handler.route_document_request(message('Сделай презентацию'), 'Сделай презентацию')
    assert not await handler.route_document_request(message('Купи хлеб', 102), 'Купи хлеб')
    assert not await handler.route_document_request(message('PDF', 103, reply=message('Другой вопрос', 499)), 'PDF')
    assert not store.jobs(('queued',))
    assert PresentationChoices(store).pending(7, 7)


async def test_presentation_without_source_resumes_original_request(tmp_path, handler, monkeypatch):
    import d_brain.bot.handlers.text as text_module
    resume = AsyncMock()
    monkeypatch.setattr(text_module, 'handle_text', resume)
    request = 'Сделай презентацию про кошек на 3 слайда'
    assert await handler.route_document_request(message(request), request)
    assert not resume.called
    bot = Bot('123456:ABCdefFakeToken')
    assert await handler.route_document_request(message('PowerPoint', 102).as_(bot), 'PowerPoint')
    resumed = resume.call_args.args[0]
    assert resumed.text.startswith(request)
    assert output_format(resumed.text) == 'pptx'
    assert resumed.from_user.id == 7
    assert not DocumentStore(tmp_path).for_scope(7)
    await bot.session.close()


async def test_cancel_preserves_document_and_does_not_queue(tmp_path, handler):
    store, doc = document(tmp_path)
    await handler.route_document_request(message('Сделай презентацию'), 'Сделай презентацию')
    assert await handler.route_document_request(message('Отмена', 102), 'Отмена')
    assert not PresentationChoices(store).pending(7, 7)
    assert not store.latest_job(doc['id'])
    assert store.safe_path(doc['path']).exists()
