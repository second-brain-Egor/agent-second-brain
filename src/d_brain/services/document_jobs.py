"""Restartable background jobs; sending is never retried ambiguously."""
from __future__ import annotations

import asyncio
import logging
import subprocess
from datetime import datetime

from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from d_brain.services.documents import DocumentStore
from d_brain.services.document_extract import DocumentReadError, extract_text
from d_brain.services.document_output import DocumentOutputError, build_prompt, create_artifact, parse_content
from d_brain.services.session import SessionStore

logger = logging.getLogger(__name__)


def transient_error(error: Exception) -> bool:
    from d_brain.services.execution import ExecutionLimit
    if isinstance(error, ExecutionLimit):
        return False
    if isinstance(error, (TimeoutError, subprocess.TimeoutExpired, ConnectionError, DocumentOutputError)):
        return True
    return isinstance(error, RuntimeError) and any(word in str(error).lower() for word in (
        'timeout', 'timed out', '429', '502', '503', '504', 'connection', 'network',
        'temporar', 'rate limit', 'overloaded', 'empty response', 'stream disconnected'))


def user_error(error: Exception, stage: str = 'model') -> str:
    if stage == 'delivery':
        return 'Файл готов, но отправка не подтверждена. Повторить отправку можно кнопкой ниже.'
    from d_brain.services.execution import ExecutionLimit
    if isinstance(error, ExecutionLimit):
        return "Достигнут предел выполнения. Запрос и промежуточный журнал сохранены; автоповтор отключён."
    if isinstance(error, (TimeoutError, subprocess.TimeoutExpired)):
        return 'Превышено время обработки. ' + (
            'Документ и задание сохранены.' if stage == 'document' else 'Запрос сохранён.')
    if isinstance(error, DocumentReadError):
        return f'Не удалось прочитать документ: {error}'
    if isinstance(error, DocumentOutputError):
        return f'Не удалось подготовить корректный файл: {error}'
    return 'Не удалось получить ответ от выбранной модели. ' + (
        'Документ и задание сохранены.' if stage == 'document' else 'Запрос сохранён.')


def process_job(store: DocumentStore, job: dict, processor) -> None:
    from d_brain.services.execution import CURRENT_EXECUTION
    execution = CURRENT_EXECUTION.get()
    if execution:
        execution.check()
    doc = store.get(job['doc_id'])
    original = store.safe_path(doc['path'])
    for attempt in range(job['attempts'], 2):
        if execution:
            execution.check()
        store.set_job(job['id'], attempts=attempt+1, state='extracting', error=None)
        try:
            text_path = extract_text(original)
            if execution:
                execution.check()
            SessionStore(store.vault).append(doc['scope'], 'file', name=doc['name'],
                path=doc['path'], text_path=text_path.relative_to(store.vault).as_posix(),
                caption=job['request'], doc_id=doc['id'], chat_id=job['chat_id'])
            store.set_job(job['id'], state='generating')
            prompt = build_prompt(text_path.read_text(encoding='utf-8'), job['request'], original)
            answer = processor._run_backend_exec(prompt, read_only=True, timeout_sec=None, mode='agent')
            if execution:
                execution.check()
            content = parse_content(answer, job['request'])
            artifact = create_artifact(content, job['request'], original.parent/'Результаты'/job['id'])
            if execution:
                execution.check()
            store.set_job(job['id'], state='ready', artifact=artifact.relative_to(store.vault).as_posix())
            return
        except Exception as error:
            logger.warning('Document job %s attempt %s failed: %s', job['id'], attempt+1, type(error).__name__)
            if attempt == 0 and transient_error(error):
                continue
            store.set_job(job['id'], state='failed', error=user_error(error, 'document'))
            return


async def deliver_job(store: DocumentStore, job: dict, bot) -> None:
    if not store.claim(job['id'], 'ready', 'sending'):
        return
    try:
        artifact = store.safe_path(job['artifact'])
        result = await bot.send_document(chat_id=job['chat_id'], document=FSInputFile(artifact),
            caption='Готово. Файл сохранён вместе с исходным документом.', parse_mode=None)
    except Exception as error:
        logger.warning('Document delivery %s failed: %s', job['id'], type(error).__name__)
        # Request could already have reached Telegram: never resend automatically.
        store.set_job(job['id'], state='send_unknown', error=user_error(error, 'delivery'))
        return
    store.set_job(job['id'], state='sent', sent_id=result.message_id)
    doc = store.get(job['doc_id'])
    store.bind_message(doc, result.message_id)
    SessionStore(store.vault).append(doc['scope'], 'assistant',
        text='Готовый файл: '+job['artifact'], path=job['artifact'], chat_id=job['chat_id'])


async def document_worker(bot, settings, request_jobs=None) -> None:
    from d_brain.services.processor import AgentProcessor
    store = DocumentStore(settings.vault_path)
    store.recover()
    while True:
        try:
            for job in store.jobs(('queued', 'ready', 'failed', 'send_unknown')):
                if job['state'] == 'queued' and store.claim(job['id'], 'queued', 'extracting'):
                    processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
                    if request_jobs is not None:
                        await request_jobs.run_document(store, job, processor)
                    else:
                        await asyncio.to_thread(process_job, store, job, processor)
                    job = store.job(job['id'])
                if job['state'] == 'ready':
                    await deliver_job(store, job, bot)
                    job = store.job(job['id'])
                if job['state'] in ('failed', 'send_unknown'):
                    uncertain = job['state'] == 'send_unknown'
                    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                        text='Повторить отправку' if uncertain else 'Повторить обработку',
                        callback_data=f"docretry:{job['id']}")]])
                    # Claim notification before I/O; avoids repeated unsolicited notices.
                    if store.claim(job['id'], job['state'], 'uncertain_reported' if uncertain else 'error_reported'):
                        await bot.send_message(job['chat_id'], job['error'] or
                            'Отправка могла прерваться при перезапуске. Автоматический повтор отключён, чтобы не прислать копию.',
                            reply_markup=markup, parse_mode=None)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception('Document worker iteration failed')
        await asyncio.sleep(2)
