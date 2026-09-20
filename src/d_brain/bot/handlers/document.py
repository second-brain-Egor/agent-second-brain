"""Document intake, explicit destination choice and shared text/voice routing."""
from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from d_brain.bot.chat_context import get_session_scope, is_work_chat
from d_brain.config import get_settings
from d_brain.services.documents import DocumentStore
from d_brain.services.presentations import (
    PresentationChoices, explicit_format, format_reply, presentation_request, with_format,
)
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name='document')
logger = logging.getLogger(__name__)
QA_TRIGGERS = re.compile(r'\b(ответ\w*|обработ\w*|прочита\w*|разбер\w*|разобра\w*|заполн\w*|сдела\w*|подготов\w*|проанализ\w*|анализ\w*|состав\w*|сократ\w*|перевед\w*|перевести|выдел\w*|сравн\w*|презентац\w*|слайд\w*|объясн\w*|расскажи)\b', re.I)
DELIVERY_REQUEST = re.compile(r'^(?:пожалуйста[, ]+)?(?:пришли|отправь|дай|покажи)\b', re.I)


def project_choice(text: str):
    return re.fullmatch(
        r'(?:(?:название\s+проекта(?:\s+для\s+документа)?\s*[:—-]?\s+)|'
        r'(?:(?:в\s+)?(?:папк[ау]\s+)?проект(?:а)?\s+))(.+)',
        text.strip(), re.I,
    )


def destination_keyboard(doc: dict):
    library = 'PDF' if doc['name'].lower().endswith('.pdf') else 'Документы'
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f'В папку {library}', callback_data=f"docplace:{doc['id']}:library"),
        InlineKeyboardButton(text='В папку проекта', callback_data=f"docplace:{doc['id']}:project")]])


async def ask_destination(message: Message, doc: dict):
    library = 'PDF' if doc['name'].lower().endswith('.pdf') else 'Документы'
    sent = await message.answer(f"📄 Куда сохранить «{doc['name']}» — в папку {library} или в папку проекта?",
                         reply_markup=destination_keyboard(doc), parse_mode=None)
    DocumentStore(get_settings().vault_path).bind_message(doc, sent.message_id)


def record_document(store: DocumentStore, doc: dict):
    text_path = store.safe_path(doc['path']).parent/'текст.txt'
    SessionStore(store.vault).append(doc['scope'], 'file', doc_id=doc['id'],
        path=doc['path'], name=doc['name'], caption=doc['instructions'],
        text_path=text_path.relative_to(store.vault).as_posix() if text_path.exists() else None,
        msg_id=doc['msg_id'], chat_id=doc['chat_id'])


async def ask_presentation_format(message: Message, store: DocumentStore, request: str,
                                  doc: dict | None = None, msg_id: int | None = None):
    choices = PresentationChoices(store)
    scope = doc['scope'] if doc else get_session_scope(message)
    choice = choices.create(scope, message.chat.id, msg_id or message.message_id,
                            request, doc['id'] if doc else None)
    if choice['state'] != 'pending':
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='PowerPoint (.pptx)', callback_data=f"presformat:{choice['id']}:pptx"),
        InlineKeyboardButton(text='PDF', callback_data=f"presformat:{choice['id']}:pdf"),
    ]])
    question = 'В каком формате подготовить презентацию — PowerPoint (.pptx) или PDF?'
    sent = await message.answer(question, reply_markup=keyboard, parse_mode=None)
    choices.bind(choice['id'], sent.message_id)
    SessionStore(store.vault).append(scope, 'assistant', text=question, chat_id=message.chat.id)


async def enqueue_or_ask(message: Message, store: DocumentStore, doc: dict,
                         request: str, msg_id: int):
    if presentation_request(request) and not explicit_format(request):
        await ask_presentation_format(message, store, request, doc, msg_id)
        return
    job = store.enqueue(doc['id'], request, message.chat.id, msg_id)
    await message.answer('Результат этого запроса уже отправлен.' if job['state'] == 'sent'
                         else 'Готовлю результат по документу.', parse_mode=None)


async def resume_presentation(message: Message, store: DocumentStore, choice: dict, fmt: str):
    choices = PresentationChoices(store)
    if not choices.resolve(choice['id'], fmt):
        return
    request = with_format(choice['request'], fmt)
    if choice['doc_id']:
        # Choice and queued job were committed together before Telegram I/O.
        await message.answer('Готовлю презентацию в ' + ('PowerPoint (.pptx).' if fmt == 'pptx' else 'PDF.'),
                             parse_mode=None)
    else:
        # Resume the ordinary conversation with the original task and selected format.
        from d_brain.bot.handlers.text import handle_text
        resumed = message.model_copy(update={'text': request, 'message_id': choice['msg_id'],
                                              'reply_to_message': None, 'voice': None})
        await handle_text(resumed, state=None, bot=message.bot)


@router.callback_query(F.data.startswith('presformat:'))
async def choose_presentation_format(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        return
    parts = (callback.data or '').split(':')
    if len(parts) != 3 or parts[2] not in {'pptx', 'pdf'}:
        await callback.answer('Неизвестный формат.')
        return
    store = DocumentStore(get_settings().vault_path)
    choice = PresentationChoices(store).get(parts[1])
    if (not choice or choice['scope'] != str(callback.from_user.id)
            or choice['chat_id'] != callback.message.chat.id):
        await callback.answer('Этот запрос относится к другому чату.')
        return
    if choice['state'] != 'pending':
        await callback.answer('Формат уже выбран или запрос отменён.')
        return
    await callback.answer()
    message = callback.message.model_copy(update={'from_user': callback.from_user})
    await resume_presentation(message, store, choice, parts[2])
    await callback.message.edit_reply_markup(reply_markup=None)


async def after_placement(message: Message, store: DocumentStore, doc: dict):
    record_document(store, doc)
    VaultStorage(store.vault).append_to_daily(
        f"Документ: {doc['name']}\nПапка: {Path(doc['path']).parent.as_posix()}",
        datetime.now(), '[file]')
    if doc['instructions']:
        await message.answer(f"Сохранил в {Path(doc['path']).parent.as_posix()}.", parse_mode=None)
        await enqueue_or_ask(message, store, doc, doc['instructions'], doc['msg_id'])
    else:
        await message.answer(f"Сохранил в {Path(doc['path']).parent.as_posix()}.\n\nЧто сделать по документу?", parse_mode=None)


@router.message(lambda m: m.document is not None)
async def handle_document(message: Message, bot: Bot):
    if not message.document or not message.from_user:
        return
    settings = get_settings()
    scope = get_session_scope(message)
    try:
        file = await bot.get_file(message.document.file_id)
        if not file.file_path:
            raise ValueError('Telegram не вернул путь файла')
        stream = await bot.download_file(file.file_path)
        if stream is None:
            raise ValueError('Telegram вернул пустую загрузку')
        store = DocumentStore(settings.vault_path)
        doc, fresh = store.receive(stream.read(), message.document.file_name or 'document.pdf',
            scope, message.chat.id, message.message_id, message.caption or '')
        if not fresh:
            return
        record_document(store, doc)
        if is_work_chat(message, settings):
            return
        if doc['state'] == 'ready':
            if message.caption:
                await enqueue_or_ask(message, store, doc, message.caption, message.message_id)
            else:
                await message.answer(f"Документ уже сохранён в {Path(doc['path']).parent.as_posix()}.\n\nЧто сделать по нему?", parse_mode=None)
        else:
            await ask_destination(message, doc)
    except Exception:
        logger.exception('Document intake failed')
        await message.answer('Не удалось получить или сохранить файл. Отправь его ещё раз.', parse_mode=None)


@router.callback_query(F.data.startswith('docplace:'))
async def choose_destination(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        return
    store = DocumentStore(get_settings().vault_path)
    _, doc_id, choice = callback.data.split(':')
    doc = store.get(doc_id)
    if doc['scope'] != str(callback.from_user.id) or doc['chat_id'] != callback.message.chat.id:
        await callback.answer('Этот документ относится к другому чату.')
        return
    await callback.answer()
    if doc['state'] == 'ready':
        await callback.message.answer(f"Документ уже сохранён: {doc['path']}", parse_mode=None)
        return
    store.select(doc['scope'], doc_id)
    if choice == 'project':
        store.update(doc_id, state='project')
        sent = await callback.message.answer('В какой проект сохранить? Напиши название проекта.', parse_mode=None)
        store.bind_message(doc, sent.message_id)
        return
    if choice != 'library':
        return
    doc = store.place(doc_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await after_placement(callback.message, store, doc)


@router.callback_query(F.data.startswith('docretry:'))
async def retry_document(callback: CallbackQuery):
    store = DocumentStore(get_settings().vault_path)
    job = store.job(callback.data.split(':')[1])
    doc = store.get(job['doc_id'])
    if not callback.message or str(callback.from_user.id) != doc['scope'] or job['chat_id'] != callback.message.chat.id:
        await callback.answer('Это задание относится к другому чату.')
        return
    if job['state'] in {'send_unknown', 'uncertain_reported'}:
        store.set_job(job['id'], state='ready', error=None)
    elif job['state'] in {'failed', 'error_reported', 'stopped'}:
        store.set_job(job['id'], state='queued', attempts=0, error=None)
    else:
        await callback.answer('Задание уже выполняется или результат отправлен.')
        return
    await callback.answer('Повтор принят.')
    await callback.message.edit_reply_markup(reply_markup=None)


def _legacy_document(store: DocumentStore, scope, reply_id=None) -> dict | None:
    for entry in reversed(SessionStore(store.vault).get_recent(scope, limit=100)):
        if entry.get('type') != 'file' or not entry.get('path'):
            continue
        if reply_id and entry.get('msg_id') != reply_id:
            continue
        if entry.get('doc_id'):
            return store.get(entry['doc_id'])
        try:
            path = store.safe_path(entry['path'])
        except ValueError:
            continue
        if path.is_file():
            doc = store.import_existing(path, scope, entry['chat_id'],
                                        entry.get('msg_id', 0), entry.get('caption') or '')
            return doc
    return None


async def route_document_request(message: Message, text: str) -> bool:
    """Called after recording either typed text or a voice transcription."""
    store = DocumentStore(get_settings().vault_path)
    scope = get_session_scope(message)
    docs = store.for_scope(scope)
    choices = PresentationChoices(store)
    reply_id = message.reply_to_message.message_id if message.reply_to_message else None
    pending = choices.pending(scope, message.chat.id, reply_id)
    if pending and not reply_id and docs and docs[0]['state'] != 'ready':
        # A new upload's folder question takes priority over an older format question.
        pending = None
    if pending:
        fmt = format_reply(text)
        if fmt:
            await resume_presentation(message, store, pending, fmt)
            return True
        if text.strip().lower().strip('.!') in {'отмена', 'отмени', 'не сейчас'}:
            choices.cancel(pending['id'])
            await message.answer('Подготовку этой презентации отменил.', parse_mode=None)
            return True
    reply_id = message.reply_to_message.message_id if message.reply_to_message else None
    doc = store.from_upload(scope, reply_id) if reply_id else None
    if reply_id and not doc:
        # Do not bind replies to unrelated messages to the latest document.
        doc = _legacy_document(store, scope, reply_id)
        reply = message.reply_to_message
        if (not doc and docs and docs[0]['state'] != 'ready' and reply.from_user
                and reply.from_user.is_bot and (reply.text or '').startswith(
                    ('В какой проект сохранить?', '📄 Куда сохранить'))):
            doc = docs[0]
        if not doc:
            if presentation_request(text) and not explicit_format(text):
                await ask_presentation_format(message, store, text)
                return True
            return False
    if not doc:
        doc = docs[0] if docs else None
    if not doc and QA_TRIGGERS.search(text):
        doc = _legacy_document(store, scope)
    if not doc:
        if presentation_request(text) and not explicit_format(text):
            await ask_presentation_format(message, store, text)
            return True
        return False
    if reply_id:
        store.select(scope, doc['id'])
    reference = re.search(r'файл|документ|слайд|сдайд|презентац|\b(?:по нему|по ней|из него|в нём|в нем)\b', text, re.I)
    recent = SessionStore(store.vault).get_recent(scope, limit=8)
    previous_inputs = [e for e in recent[:-1] if e.get('type') in {'text','voice','file'}]
    immediate = bool(previous_inputs and previous_inputs[-1].get('type') == 'file')
    document_task = bool((QA_TRIGGERS.search(text) or DELIVERY_REQUEST.search(text))
                         and (reference or immediate or reply_id))
    lowered = text.strip().lower().strip('.!')
    if doc['state'] != 'ready':
        if lowered in {'отмена', 'отмени', 'не сейчас'}:
            store.update(doc['id'], instructions='')
            await message.answer('Обработку не запускаю. Документ сохранён во входящих до выбора папки.', parse_mode=None)
            return True
        if re.fullmatch(r'(?:в\s+)?(?:папк[ау]\s+)?(?:pdf|пдф|документы)', lowered):
            await after_placement(message, store, store.place(doc['id']))
            return True
        project = project_choice(text)
        if re.fullmatch(r'(?:в\s+)?(?:папк[ау]\s+)?проект(?:а)?', lowered):
            store.update(doc['id'], state='project')
            sent = await message.answer('В какой проект сохранить? Напиши название проекта.', parse_mode=None)
            store.bind_message(doc, sent.message_id)
            return True
        if not project and doc['state'] == 'project' and (len(text)>100 or '?' in text or re.match(r'^(?:почему|как |что |в ч[её]м |когда |ты )', lowered)):
            return False
        if project or doc['state'] == 'project':
            # A natural-language task is not a project name.
            if (QA_TRIGGERS.search(text) or DELIVERY_REQUEST.search(text)) and not project:
                if not document_task:
                    return False
                instructions = doc['instructions'] if DELIVERY_REQUEST.search(text) and doc['instructions'] else text
                store.update(doc['id'], instructions=instructions, msg_id=message.message_id)
                await message.answer('Задание сохранил. Напиши название проекта для документа.', parse_mode=None)
                return True
            try:
                placed = store.place(doc['id'], project[1] if project else text)
            except ValueError as error:
                await message.answer(str(error), parse_mode=None)
                return True
            await after_placement(message, store, placed)
            return True
        if document_task:
            instructions = doc['instructions'] if DELIVERY_REQUEST.search(text) and doc['instructions'] else text
            doc = store.update(doc['id'], instructions=instructions, msg_id=message.message_id)
            await ask_destination(message, doc)
            return True
        return False
    # Avoid treating every unrelated command as a document request.
    if document_task:
        if DELIVERY_REQUEST.search(text) and not explicit_format(text):
            job = store.latest_job(doc['id'])
            if job:
                responses = {
                    'sent': 'Готовый файл уже отправлен в этот чат.',
                    'failed': job['error'] or 'Обработка завершилась ошибкой.',
                    'stopped': 'Обработка остановлена. Документ и задание сохранены.',
                    'error_reported': job['error'] or 'Обработка завершилась ошибкой.',
                    'send_unknown': 'Файл готов. Для повторной отправки нажми кнопку под сообщением об ошибке.',
                    'uncertain_reported': 'Файл готов. Для повторной отправки нажми кнопку под сообщением об ошибке.',
                }
                await message.answer(responses.get(job['state'], 'Задание уже выполняется. Готовый файл пришлю сюда.'), parse_mode=None)
                return True
            text = doc['instructions'] or text
        if DELIVERY_REQUEST.search(text) and explicit_format(text):
            previous = store.latest_job(doc['id'])
            original = previous['request'] if previous else doc['instructions']
            if original:
                text = with_format(original, explicit_format(text))
        await enqueue_or_ask(message, store, doc, text, message.message_id)
        return True
    if presentation_request(text) and not explicit_format(text):
        await ask_presentation_format(message, store, text)
        return True
    return False
