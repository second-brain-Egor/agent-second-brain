"""Document intake and shared text/voice routing.

Since 9 October 2026 the bot asks nothing about a new file: it saves it and hands the batch of
attachments to the assistant (bot/uploads.py), who decides from the conversation. The old explicit
destination choice stays behind FOLDER_QUESTIONS.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from d_brain.bot import uploads
from d_brain.bot.chat_context import get_session_scope, is_work_chat
from d_brain.config import get_settings
from d_brain.services.documents import (
    DocumentStore, clean_folder_name, folder_key, folder_label, note_placement, service_dir,
)
from d_brain.services.presentations import (
    PresentationChoices, declined, explicit_format, format_reply, presentation_request, with_format,
)
from d_brain.services.session import SessionStore

router = Router(name='document')
logger = logging.getLogger(__name__)
QA_TRIGGERS = re.compile(r'\b(ответ\w*|обработ\w*|прочита\w*|разбер\w*|разобра\w*|заполн\w*|сдела\w*|подготов\w*|проанализ\w*|анализ\w*|состав\w*|сократ\w*|перевед\w*|перевести|выдел\w*|сравн\w*|объясн\w*|расскажи)\b', re.I)
DELIVERY_REQUEST = re.compile(r'^(?:пожалуйста[, ]+)?(?:пришли|отправь|дай|покажи)\b', re.I)
# Егор, 8 октября 2026: шаблонный генератор (заголовок и шесть пунктов на слайде) и вопрос
# о формате отключены. Задания по документам выполняет сам помощник в чате; здесь остаются
# только приём файла и выбор папки. Вернуть автоматику — True.
AUTOMATIC_JOBS = False
# Егор, 9 октября 2026: «канитель» с вопросом «Куда сохранить?» убрана. Бот сохраняет файл
# (в текущий проект или во входящие) и сразу отдаёт его помощнику с разговором; тот сам решает,
# куда положить и что сделать, а спрашивает, только если файл из другой области. Ответы про папку
# тоже разбирает помощник. Вернуть кнопки и вопросы бота — True.
FOLDER_QUESTIONS = False


def project_choice(text: str):
    return re.fullmatch(
        r'(?:(?:название\s+проекта(?:\s+для\s+документа)?\s*[:—-]?\s+)|'
        r'(?:(?:в\s+)?(?:папк[ау]\s+)?проект(?:а)?\s+))(.+)',
        text.strip(), re.I,
    )


# Егор, 8 октября 2026: проект — корневая папка, работа по задачам лежит в его подпапках.
# После названия проекта бот всегда спрашивает подпроект и называет, куда положил файл.
SUB_PREFIX = re.compile(r'^(?:(?:положи|сохрани|клади|перенеси|кинь|давай)\s+)?(?:во?\s+)?'
                        r'(?:(?:подпроект|подпапк\w*|папк\w*)\s+)?', re.I)
NEW_SUBPROJECT = re.compile(r'^(?:нов(?:ый|ая|ую|ое)|создай|создать|заведи|завести)\s+'
                            r'(?:подпроект|подпапк\w*|папк\w*)(?:\s+(?:(?:с\s+)?названием\s+)?(.+))?$', re.I)
NAME_PREFIX = re.compile(r'^(?:(?:назови|название)\s+(?:его\s+|её\s+|ее\s+)?)?'
                         r'(?:(?:подпроект|подпапк\w*|папк\w*)\s+)?', re.I)


def named_subproject(choice: dict, text: str) -> str | None:
    """Existing or explicitly new subproject; '' is the project root; None if the reply names nothing."""
    spoken = text.strip().strip(' .,!')
    by_key = {folder_key(name): name for name in choice['options']}
    for candidate in (spoken, SUB_PREFIX.sub('', spoken, count=1), NAME_PREFIX.sub('', spoken, count=1)):
        key = folder_key(candidate)
        if key in by_key:
            return by_key[key]
        if key.startswith(('корен', 'корн')) or key == folder_key(choice['project']):
            return ''
    new = NEW_SUBPROJECT.match(spoken)
    return new[1] if new and new[1] else None


def place_label(doc: dict) -> str:
    return folder_label(doc['path'])


def spoken_project(store: DocumentStore, text: str) -> str | None:
    """An existing project named in a reply: «Ирина работа», «в ирина работа.», «положи в дачу»."""
    spoken = text.strip().strip(' .,!')
    if len(spoken) > 80:
        return None
    for candidate in (spoken, SUB_PREFIX.sub('', spoken, count=1)):
        name = store.existing_project(candidate) if candidate else None
        if name:
            return name
    return None


async def ask_subproject(message: Message, store: DocumentStore, doc: dict, project: str):
    choice = store.ask_subproject(doc['id'], project)
    project, options = choice['project'], choice['options']
    rows = [[InlineKeyboardButton(text=f'📁 {name}', callback_data=f"docsub:{doc['id']}:{index}")]
            for index, name in enumerate(options)]
    rows.append([InlineKeyboardButton(text=f'В корень «{project}»', callback_data=f"docsub:{doc['id']}:root")])
    rows.append([InlineKeyboardButton(text='➕ Новый подпроект', callback_data=f"docsub:{doc['id']}:new")])
    if not choice['exists']:
        question = (f"📁 Проекта «{project}» пока нет, заведу новую папку. "
                    f"Положить «{doc['name']}» в её корень или сразу в подпроект?")
    elif options:
        question = f"📁 В какой подпроект «{project}» положить «{doc['name']}»?"
    else:
        question = (f"📁 В проекте «{project}» подпроектов пока нет. "
                    f"Положить «{doc['name']}» в корень или завести подпроект?")
    sent = await message.answer(question, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode=None)
    store.bind_message(doc, sent.message_id)


async def ask_new_subproject(message: Message, store: DocumentStore, doc: dict, project: str):
    store.update(doc['id'], state='subproject_new')
    sent = await message.answer(f'📁 Напиши название нового подпроекта в «{project}».', parse_mode=None)
    store.bind_message(doc, sent.message_id)


async def place_in_subproject(message: Message, store: DocumentStore, doc: dict,
                              project: str, subproject: str) -> bool:
    try:
        subproject = clean_folder_name(subproject, 'подпроекта') if subproject else None
    except ValueError as error:
        await message.answer(str(error), parse_mode=None)
        return True
    await after_placement(message, store, store.place(doc['id'], project, subproject), activate=True)
    return True


async def project_chosen(message: Message, store: DocumentStore, doc: dict, project: str):
    """A project without subprojects needs no second question: the file goes to its root."""
    existing = store.existing_project(project)
    if existing and not store.subprojects(existing):
        await after_placement(message, store, store.place(doc['id'], existing), activate=True)
        return
    await ask_subproject(message, store, doc, project)


def library_name(doc: dict) -> str:
    return 'PDF' if doc['name'].lower().endswith('.pdf') else 'Документы'


def destination_keyboard(doc: dict, projects: list[str], everything: bool = False):
    rows = [[InlineKeyboardButton(text=f'📁 {name}', callback_data=f"docproj:{doc['id']}:{index}")]
            for index, name in enumerate(projects)]
    last = [InlineKeyboardButton(text=f'В папку {library_name(doc)}', callback_data=f"docplace:{doc['id']}:library")]
    if not everything:
        last.insert(0, InlineKeyboardButton(text='📋 Все проекты', callback_data=f"docproj:{doc['id']}:all"))
    rows.append(last)
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def ask_destination(message: Message, doc: dict):
    # Егор, 8 октября 2026: названия проектов по памяти не набирать — последние проекты кнопками.
    store = DocumentStore(get_settings().vault_path)
    projects = store.projects()
    last = store.active_project(doc['scope'], stale=True)
    if last and last['project'] in projects:
        projects.remove(last['project'])
        projects.insert(0, last['project'])
    shown = store.offer_projects(doc['id'], projects[:5])
    sent = await message.answer(f"📄 Куда сохранить «{doc['name']}»? Выбери проект или общую папку "
                                f"{library_name(doc)}. Можно и написать название проекта.",
                                reply_markup=destination_keyboard(doc, shown), parse_mode=None)
    store.bind_message(doc, sent.message_id)


def record_document(store: DocumentStore, doc: dict):
    text_path = service_dir(store.safe_path(doc['path']))/'текст.txt'
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
    if not AUTOMATIC_JOBS:
        # The task from the caption or an earlier message goes to the assistant like typed text.
        from d_brain.bot.handlers.text import handle_text
        task = message.model_copy(update={'text': request, 'message_id': msg_id, 'caption': None,
                                          'document': None, 'reply_to_message': None, 'voice': None})
        await handle_text(task, state=None, bot=message.bot)
        return
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


async def after_placement(message: Message, store: DocumentStore, doc: dict, activate: bool = False):
    """activate: the user chose this project — it becomes the current one for the next files."""
    record_document(store, doc)
    journal = note_placement(store, doc, datetime.now())
    saved = (f"📂 Сохранил «{Path(doc['path']).name}» в {place_label(doc)}.\n"
             f"Путь: {doc['path']}" + ('\nЗапись добавил в журнал документов проекта.' if journal else ''))
    folder = Path(doc['path']).parent.parts
    if activate and len(folder) >= 2 and folder[0] == 'projects':
        before = store.active_project(doc['scope'])
        after = store.set_active(doc['scope'], folder[1], folder[2] if len(folder) > 2 else None)
        if after != before:
            saved += '\nСледующие файлы кладу сюда же, пока работаем в этом проекте.'
    if doc['instructions']:
        await message.answer(saved, parse_mode=None)
        await enqueue_or_ask(message, store, doc, doc['instructions'], doc['msg_id'])
    else:
        await message.answer(saved + '\n\nЧто сделать по документу?', parse_mode=None)


@router.message(lambda m: m.document is not None)
async def handle_document(message: Message, bot: Bot):
    if not message.document or not message.from_user:
        return
    settings = get_settings()
    scope = get_session_scope(message)
    if FOLDER_QUESTIONS or AUTOMATIC_JOBS or is_work_chat(message, settings):
        await _intake_with_questions(message, bot, settings, scope)
        return
    await uploads.collect(message, scope, lambda: _intake_for_assistant(message, bot, settings, scope))


async def _receive(message: Message, bot: Bot, settings, scope) -> tuple[DocumentStore, dict, bool]:
    file = await bot.get_file(message.document.file_id)
    if not file.file_path:
        raise ValueError('Telegram не вернул путь файла')
    stream = await bot.download_file(file.file_path)
    if stream is None:
        raise ValueError('Telegram вернул пустую загрузку')
    store = DocumentStore(settings.vault_path)
    doc, fresh = store.receive(stream.read(), message.document.file_name or 'document.pdf',
        scope, message.chat.id, message.message_id, message.caption or '')
    return store, doc, fresh


async def _intake_for_assistant(message: Message, bot: Bot, settings, scope) -> dict | None:
    """Save the file without questions; where it goes and what to do the assistant decides."""
    try:
        store, doc, fresh = await _receive(message, bot, settings, scope)
        if not fresh:
            return None
        active = store.active_project(scope)
        if doc['state'] == 'ready':
            where = 'такой же файл уже был сохранён раньше, лежит в ' + place_label(doc)
        elif active:
            # Working in a project: the file goes there; the assistant still checks the place.
            doc = store.place(doc['id'], active['project'], active['subproject'])
            store.record_placement(scope, doc['path'], 'document')
            store.touch_active(scope)
            note_placement(store, doc, datetime.now())
            where = 'бот положил в текущий проект: ' + place_label(doc)
        else:
            where = 'во входящих, место ещё не выбрано'
        record_document(store, doc)
        return {'kind': 'file', 'name': doc['name'], 'path': doc['path'], 'where': where,
                'caption': message.caption}
    except Exception:
        logger.exception('Document intake failed')
        await message.answer('Не удалось получить или сохранить файл. Отправь его ещё раз.', parse_mode=None)
        return None


async def _intake_with_questions(message: Message, bot: Bot, settings, scope):
    """Before 9 October 2026: the bot itself asks for the folder (FOLDER_QUESTIONS); work chats only save."""
    try:
        store, doc, fresh = await _receive(message, bot, settings, scope)
        if not fresh:
            return
        record_document(store, doc)
        if is_work_chat(message, settings):
            return
        if doc['state'] == 'ready':
            if message.caption:
                await enqueue_or_ask(message, store, doc, message.caption, message.message_id)
            else:
                await message.answer(f"Такой документ уже сохранён в {place_label(doc)}.\nПуть: {doc['path']}\n\nЧто сделать по нему?", parse_mode=None)
            return
        active = store.active_project(scope)
        if not active:
            await ask_destination(message, doc)
            return
        # Working in a project: no questions; the assistant checks the place on the next turn.
        doc = store.place(doc['id'], active['project'], active['subproject'])
        store.record_placement(scope, doc['path'], 'document')
        store.touch_active(scope)
        await after_placement(message, store, doc)
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
    # The button message belongs to the bot; the task must stay in the user's conversation.
    await after_placement(callback.message.model_copy(update={'from_user': callback.from_user}), store, doc)


@router.callback_query(F.data.startswith('docproj:'))
async def choose_project(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        return
    store = DocumentStore(get_settings().vault_path)
    _, doc_id, option = (callback.data or '').split(':')
    doc = store.get(doc_id)
    if doc['scope'] != str(callback.from_user.id) or doc['chat_id'] != callback.message.chat.id:
        await callback.answer('Этот документ относится к другому чату.')
        return
    await callback.answer()
    message = callback.message.model_copy(update={'from_user': callback.from_user})
    if doc['state'] == 'ready':
        await message.answer(f"Документ уже сохранён в {place_label(doc)}.\nПуть: {doc['path']}", parse_mode=None)
        return
    if option == 'all':
        shown = store.offer_projects(doc_id, store.projects())
        await callback.message.edit_reply_markup(reply_markup=destination_keyboard(doc, shown, everything=True))
        return
    offered = store.offered_projects(doc_id)
    if not option.isdigit() or int(option) >= len(offered):
        await message.answer('Этот вопрос устарел. Напиши название проекта.', parse_mode=None)
        return
    store.select(doc['scope'], doc_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await project_chosen(message, store, doc, offered[int(option)])


@router.callback_query(F.data.startswith('docsub:'))
async def choose_subproject(callback: CallbackQuery):
    if not callback.message or not callback.from_user:
        return
    store = DocumentStore(get_settings().vault_path)
    _, doc_id, option = (callback.data or '').split(':')
    doc = store.get(doc_id)
    if doc['scope'] != str(callback.from_user.id) or doc['chat_id'] != callback.message.chat.id:
        await callback.answer('Этот документ относится к другому чату.')
        return
    await callback.answer()
    message = callback.message.model_copy(update={'from_user': callback.from_user})
    if doc['state'] == 'ready':
        await message.answer(f"Документ уже сохранён в {place_label(doc)}.\nПуть: {doc['path']}", parse_mode=None)
        return
    choice = store.subproject_choice(doc_id)
    if not choice or doc['state'] not in {'subproject', 'subproject_new'}:
        await message.answer('Этот вопрос устарел. Напиши название проекта ещё раз.', parse_mode=None)
        return
    store.select(doc['scope'], doc_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    if option == 'new':
        await ask_new_subproject(message, store, doc, choice['project'])
        return
    if option == 'root':
        subproject = None
    elif option.isdigit() and int(option) < len(choice['options']):
        subproject = choice['options'][int(option)]
    else:
        return
    await after_placement(message, store, store.place(doc_id, choice['project'], subproject), activate=True)


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
    if not (AUTOMATIC_JOBS or FOLDER_QUESTIONS):
        # Folder answers and document tasks are the assistant's: the text goes to the conversation.
        return False
    store = DocumentStore(get_settings().vault_path)
    scope = get_session_scope(message)
    docs = store.for_scope(scope)
    choices = PresentationChoices(store)
    reply_id = message.reply_to_message.message_id if message.reply_to_message else None
    pending = choices.pending(scope, message.chat.id, reply_id) if AUTOMATIC_JOBS else None
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
    if declined(text):
        # "Delete the slides" must reach the assistant instead of starting a new document job.
        if pending:
            choices.cancel(pending['id'])
        return False
    reply_id = message.reply_to_message.message_id if message.reply_to_message else None
    doc = store.from_upload(scope, reply_id) if reply_id else None
    if reply_id and not doc:
        # Do not bind replies to unrelated messages to the latest document.
        doc = _legacy_document(store, scope, reply_id)
        reply = message.reply_to_message
        if (not doc and docs and docs[0]['state'] != 'ready' and reply.from_user
                and reply.from_user.is_bot and (reply.text or '').startswith(
                    ('В какой проект сохранить?', '📄 Куда сохранить', '📁 '))):
            doc = docs[0]
        if not doc:
            if AUTOMATIC_JOBS and presentation_request(text) and not explicit_format(text):
                await ask_presentation_format(message, store, text)
                return True
            return False
    if not doc:
        doc = docs[0] if docs else None
    if not doc and QA_TRIGGERS.search(text):
        doc = _legacy_document(store, scope)
    if not doc:
        if AUTOMATIC_JOBS and presentation_request(text) and not explicit_format(text):
            await ask_presentation_format(message, store, text)
            return True
        return False
    if reply_id:
        store.select(scope, doc['id'])
    reference = re.search(r'файл|документ|слайд|сдайд|презентац|\b(?:по нему|по ней|из него|в нём|в нем)\b', text, re.I)
    recent = SessionStore(store.vault).get_recent(scope, limit=8)
    previous_inputs = [e for e in recent[:-1] if e.get('type') in {'text','voice','file'}]
    immediate = bool(previous_inputs and previous_inputs[-1].get('type') == 'file')
    # The bare word "презентация" is not an order: "мы одинаково понимаем слово презентация?"
    # got a slide in reply on 8 October 2026. Slides need a verb (presentation_request).
    asks_for_work = bool(QA_TRIGGERS.search(text) or DELIVERY_REQUEST.search(text) or presentation_request(text))
    document_task = asks_for_work and bool(reference or immediate or reply_id)
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
        named = spoken_project(store, text) if doc['state'] in {'destination', 'project'} and not project else None
        if named:
            await project_chosen(message, store, doc, named)
            return True
        if re.fullmatch(r'(?:в\s+)?(?:папк[ау]\s+)?проект(?:а)?', lowered):
            store.update(doc['id'], state='project')
            sent = await message.answer('В какой проект сохранить? Напиши название проекта.', parse_mode=None)
            store.bind_message(doc, sent.message_id)
            return True
        waiting_name = doc['state'] in {'project', 'subproject', 'subproject_new'}
        if not project and waiting_name and (len(text)>100 or '?' in text or re.match(r'^(?:почему|как |что |в ч[её]м |когда |ты )', lowered)):
            return False
        choice = store.subproject_choice(doc['id']) if doc['state'] in {'subproject', 'subproject_new'} else None
        if choice and not project:
            new = NEW_SUBPROJECT.match(text.strip().strip(' .,!'))
            if new and not new[1]:
                await ask_new_subproject(message, store, doc, choice['project'])
                return True
            target = named_subproject(choice, text)
            if target is not None:
                return await place_in_subproject(message, store, doc, choice['project'], target)
        if project or waiting_name:
            # A natural-language task is not a project name.
            if asks_for_work and not project:
                if not document_task:
                    return False
                instructions = doc['instructions'] if DELIVERY_REQUEST.search(text) and doc['instructions'] else text
                store.update(doc['id'], instructions=instructions, msg_id=message.message_id)
                await message.answer('Задание сохранил. ' + ('Напиши название проекта для документа.'
                    if doc['state'] == 'project' else 'Выбери подпроект кнопкой выше или напиши его название.'),
                    parse_mode=None)
                return True
            if choice and not project:
                name = NAME_PREFIX.sub('', text.strip().strip(' .,!'), count=1)
                if doc['state'] == 'subproject_new':
                    return await place_in_subproject(message, store, doc, choice['project'], name)
                # A misheard voice reply must not create a folder: new subprojects need «новый».
                await message.answer(f"📁 В «{choice['project']}» нет подпроекта «{name}». Выбери кнопкой, "
                                     f"напиши «в корень» или «новый подпроект {name}».", parse_mode=None)
                return True
            try:
                await project_chosen(message, store, doc, project[1] if project else text)
            except ValueError as error:
                await message.answer(str(error), parse_mode=None)
            return True
        if document_task:
            instructions = doc['instructions'] if DELIVERY_REQUEST.search(text) and doc['instructions'] else text
            doc = store.update(doc['id'], instructions=instructions, msg_id=message.message_id)
            await ask_destination(message, doc)
            return True
        return False
    # Avoid treating every unrelated command as a document request.
    if document_task and AUTOMATIC_JOBS:
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
    if AUTOMATIC_JOBS and presentation_request(text) and not explicit_format(text):
        await ask_presentation_format(message, store, text)
        return True
    return False
