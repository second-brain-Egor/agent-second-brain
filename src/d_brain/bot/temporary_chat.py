"""Intercept temporary messages before the durable inbox and all normal handlers."""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile
from pathlib import Path

from d_brain.bot.formatters import prepare_telegram_response
from d_brain.bot.keyboards import CHAT_BUTTON, WORK_BUTTON, get_main_keyboard
from d_brain.bot.request_jobs import STATUS, STOP
from d_brain.bot.typing_indicator import keep_typing
from d_brain.config import get_settings
from d_brain.services.execution import Execution, ExecutionStopped, execution_context
from d_brain.services.temporary_chat import TOGGLE_LABELS, enabled, set_enabled
from d_brain.services.temporary_reply import reply

logger = logging.getLogger(__name__)
# These controls carry no conversation content. They retain their usual behavior.
CONTROLS = {CHAT_BUTTON, WORK_BUTTON, "✨ Запрос", "🤖 Модель", "🧠 Claude",
            "❓ Помощь", "⚙️ Обработать", "/process", "/weekly",
            "/help", "/start", "/chat", "/voice"}


class TemporaryChat:
    def __init__(self, settings, jobs):
        self.settings = settings
        self.jobs = jobs
        self.history = []
        self.images = []
        self.tasks = {}
        self.albums = {}
        self.lock = asyncio.Lock()
        self.generation = 0
        self.ingress_lock = asyncio.Lock()
        # A killed process cannot run finally blocks. Reap only its owned RAM files.
        if settings.temporary_chat_user_id:
            for path in Path('/dev/shm').glob(f'dbrain-private-{os.getuid()}-*'):
                try:
                    pid = int(path.name.split('-')[3])
                    if not Path(f'/proc/{pid}').exists() and path.stat().st_uid == os.getuid():
                        shutil.rmtree(path)
                except (ValueError, OSError):
                    continue

    def owns(self, message):
        return (message.chat.type == "private" and message.from_user is not None
                and message.from_user.id == self.settings.temporary_chat_user_id)

    async def __call__(self, handler, event, data):
        message = event.message
        if message is None or not self.owns(message):
            return await handler(event, data)
        async with self.ingress_lock:
            return await self.dispatch(handler, event, data)

    async def dispatch(self, handler, event, data):
        message = event.message
        text = message.text or ""
        command = text.split(maxsplit=1)[0].split("@")[0] if text else ""
        # Restored ordinary updates retain the storage mode chosen at receipt.
        if data.get("restored_inbox_key"):
            return await handler(event, data)
        if text in TOGGLE_LABELS or command == "/temporary":
            new_mode = not enabled(self.settings)
            try:
                set_enabled(self.settings, new_mode)
            except OSError:
                await message.answer("Не удалось переключить чат. Режим не изменён.")
                return
            self.generation += 1
            await self.stop()
            self.history.clear()
            self.images.clear()
            # Clear only the pending /do or silent state, retaining other preferences.
            if data.get("state"):
                await data["state"].set_state(None)
            await message.answer(
                "🕶 Временный чат включён. Переписка не сохраняется и не попадает в обработку."
                if new_mode else
                "💬 Обычный чат включён. Временный контекст очищен; новые сообщения сохраняются.",
                reply_markup=get_main_keyboard(message.from_user.id))
            return
        if not enabled(self.settings):
            return await handler(event, data)
        if text in CONTROLS or (command in CONTROLS and text.strip() == command):
            return await handler(event, data)
        if STOP.fullmatch(text.strip()):
            await self.stop()
            await self.jobs.stop_scope(message.from_user.id)
            await message.answer("Остановил.")
            return
        if STATUS.fullmatch(text.strip()):
            await message.answer("Временный запрос выполняется." if self.tasks
                                 else "Активных временных запросов нет.")
            return
        if command == "/silent":
            await message.answer("Во временном чате сохранение выключено. Для тихого режима сначала включи обычный чат.")
            return
        if command == "/restart":
            # Normal handler records only the command name, no chat content.
            return await handler(event, data)
        group = message.media_group_id
        if group and group in self.albums:
            self.albums[group].append(message)
            return
        batch = [message]
        if group:
            self.albums[group] = batch
        execution = Execution(self.settings.vault_path.parent, scope=message.from_user.id,
                              origin="temporary", persistent=False)
        task = asyncio.create_task(self.run(batch, data["bot"], execution, self.generation))
        self.tasks[task] = execution
        task.add_done_callback(self.tasks.pop)
        return None

    async def stop(self):
        current = asyncio.current_task()
        tasks = [task for task in self.tasks if task is not current]
        for task in tasks:
            self.tasks[task].stop()
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.albums.clear()

    async def close(self):
        await self.stop()
        self.history.clear()
        self.images.clear()

    async def thread(self, function, *args):
        # Let cancellation terminate the process before disposing of its RAM files.
        worker = asyncio.create_task(asyncio.to_thread(function, *args))
        try:
            return await asyncio.shield(worker)
        except asyncio.CancelledError:
            try:
                await worker
            except BaseException:
                pass
            raise

    async def run(self, batch, bot, execution, generation):
        message = batch[0]
        group = message.media_group_id
        with execution_context(execution):
            try:
                # Voice controls must be recognized even while an earlier model is running.
                transcript = None
                if message.voice:
                    from d_brain.bot.handlers.voice import _transcribe_voice
                    transcript = await _transcribe_voice(message, bot)
                    if not transcript:
                        await message.answer("Не удалось распознать голосовое.")
                        return
                    if STOP.fullmatch(transcript.strip()):
                        await self.stop()
                        await self.jobs.stop_scope(message.from_user.id)
                        await message.answer("Остановил.")
                        return
                if group:
                    # Telegram sends albums as separate updates. Wait until arrivals settle.
                    while True:
                        count = len(batch)
                        await asyncio.sleep(0.8)
                        if len(batch) == count:
                            break
                    self.albums.pop(group, None)
                async with self.lock:
                    execution.check()
                    if generation != self.generation:
                        return
                    execution.update(state="running")
                    # No fallback to disk: failure to create RAM workspace fails closed.
                    with tempfile.TemporaryDirectory(prefix=f"dbrain-private-{os.getuid()}-{os.getpid()}-", dir="/dev/shm") as directory:
                        workspace = Path(directory)
                        parts, images = [], []
                        for item in batch:
                            text = transcript if item.voice else (item.text or item.caption or "")
                            parts.append(text or "[Вложение без подписи]")
                            await self.attachment(item, bot, workspace, parts, images)
                        self.images.extend((Path(path).read_bytes(), Path(path).suffix) for path in images)
                        images = []
                        for index, (content, suffix) in enumerate(self.images):
                            path = workspace / f"контекст-{index}{suffix}"
                            path.write_bytes(content)
                            images.append(str(path))
                        entry = {"role": "user", "text": "\n\n".join(parts)}
                        self.history.append(entry)
                        async with keep_typing(message.chat):
                            answer = await self.thread(reply, get_settings(), workspace,
                                                       list(self.history), images)
                        execution.check()
                        if generation != self.generation:
                            return
                        for chunk in prepare_telegram_response(answer):
                            try:
                                await message.answer(chunk)
                            except Exception:
                                await message.answer(chunk, parse_mode=None)
                        self.history.append({"role": "assistant", "text": answer})
                        execution.update(state="completed")
            except (asyncio.CancelledError, ExecutionStopped):
                execution.stop()
            except Exception as exc:
                execution.update(state="error")
                # No traceback/error text: either may contain private input or model output.
                logger.error("Temporary request failed (%s)", type(exc).__name__)
                try:
                    await message.answer("Не удалось завершить временный запрос. Переписка не сохранена.")
                except Exception:
                    logger.error("Temporary error response could not be delivered")
            finally:
                if group:
                    self.albums.pop(group, None)

    async def attachment(self, message, bot, workspace, parts, images):
        media = (message.photo[-1] if message.photo else
                 message.document or message.video or message.video_note or message.audio)
        if media is None:
            return
        directory = workspace / str(message.message_id)
        directory.mkdir()
        suffix = Path(getattr(media, "file_name", "") or "").suffix.lower()
        suffix = suffix if len(suffix) < 12 else ""
        path = directory / ("вложение" + (suffix or (".jpg" if message.photo else ".mp4")))
        await bot.download(media, destination=path)
        if message.photo or suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            images.append(str(path))
        elif message.video or message.video_note or message.audio:
            # Provide representative frames and audio transcription without permanent copies.
            from d_brain.services.document_extract import run
            from d_brain.services.transcription import DeepgramTranscriber
            if not message.audio:
                await self.thread(run, ["ffmpeg", "-v", "error", "-i", str(path),
                                       "-vf", "fps=1/5,scale=960:-2", "-frames:v", "12",
                                       str(directory / "кадр-%02d.jpg")])
                images.extend(str(frame) for frame in sorted(directory.glob("кадр-*.jpg")))
                parts.append("Видео: выборка до 12 кадров с интервалом 5 секунд; это не все кадры.")
            audio_path = directory / "audio.wav"
            try:
                await self.thread(run, ["ffmpeg", "-v", "error", "-i", str(path),
                                       "-vn", "-ac", "1", "-ar", "16000", str(audio_path)])
            except Exception:
                parts.append("Звук вложения не удалось извлечь.")
            else:
                transcript = await DeepgramTranscriber(get_settings().deepgram_api_key).transcribe(audio_path.read_bytes())
                parts.append(transcript)
        else:
            from d_brain.services.document_extract import DocumentReadError, extract_text
            try:
                extracted = await self.thread(extract_text, path, None, workspace)
                parts.append(extracted.read_text())
            except DocumentReadError:
                parts.append("Формат вложения не удалось прочитать. Сообщи это пользователю без предположений о содержимом.")
