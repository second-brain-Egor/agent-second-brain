"""Очередь ответов чата: строго по порядку прихода, по свежей беседе, пачкой.

Место в очереди сообщение занимает сразу при получении (RequestJobs.__call__), а ждёт только
перед запросом к модели в режиме чата. Запись в журнал, «стоп» и /tasks не ждут никого.

Когда очередь дошла, беседа собирается заново, уже с ответами на все прежние сообщения.
Подряд идущие следом сообщения, которые уже ждут ответа, берутся в тот же запрос: на них идёт один
общий ответ, их собственные запросы к модели не запускаются, а вместо ответа уходит строка
«Ответил выше…». Если ответ не получился, ждавшие сообщения возвращаются в очередь.
Тяжёлая работа (`_run_agent`) очередь чата не держит.
"""
from __future__ import annotations

import threading
from datetime import datetime

from d_brain.services.execution import CURRENT_EXECUTION

ANSWERED_ABOVE = '☝️ Ответил выше, в сообщении от {stamp}'
POLL_SECONDS = 0.1  # как часто ждущий поток проверяет «стоп»; смену очереди он видит сразу


def stamp_now() -> str:
    """Время так же, как в журнале беседы: местное, ЧЧ:ММ."""
    return datetime.now().astimezone().strftime('%H:%M')


class Turn:
    """Место одного сообщения в очереди ответов своего чата."""

    def __init__(self, queue, scope, message_id):
        self.queue = queue
        self.scope = scope
        self.message_id = message_id
        self.text = None         # задан, пока сообщение дошло до запроса к модели
        self.stamp = ''
        self.finished = False
        self.covered_by = None   # Turn, чей общий ответ закроет и это сообщение
        self.batch = ()          # Turn'ы, взятые в ответ на этот запрос
        self.answered_at = None  # «ЧЧ:ММ»: ответ на этот запрос получен


class Grant:
    """Итог ожидания очереди.

    answered — сообщение уже закрыто чужим общим ответом, запрос к модели не нужен;
    stamp — время этого сообщения; queued — [(время, текст)] ждавших следом сообщений, которые
    отвечают вместе с этим. Выход из блока без commit возвращает их в очередь.
    """

    def __init__(self, turn=None, batch=(), answered=None):
        self.turn = turn
        self.batch = tuple(batch)
        self.stamp = turn.stamp if turn is not None else ''
        self.queued = tuple((other.stamp, other.text) for other in self.batch)
        self.answered = answered
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if self.turn is not None and self.batch and not self.committed:
            self.turn.queue.release(self.turn)
        return False

    def commit(self):
        """Ответ получен: взятые вместе с ним сообщения считаются закрытыми."""
        if self.turn is not None and not self.committed:
            self.committed = True
            self.turn.queue.commit(self.turn)


class ChatQueue:
    def __init__(self):
        self.cond = threading.Condition()
        self.turns = {}  # scope -> {message_id: Turn}; словарь хранит порядок прихода

    def register(self, scope, message_id) -> Turn:
        turn = Turn(self, str(scope), message_id)
        with self.cond:
            turns = self.turns.setdefault(turn.scope, {})
            replaced = turns.get(message_id)  # повторная доставка того же сообщения: место прежнее
            if replaced is not None:
                replaced.finished = True
                self._uncover(replaced)
            turns[message_id] = turn
            self.cond.notify_all()
        return turn

    def pending(self, scope) -> list:
        with self.cond:
            return list(self.turns.get(str(scope), {}))

    def finish(self, scope, message_id):
        """Сообщение отработало, остановлено или больше не держит очередь чата."""
        scope = str(scope)
        with self.cond:
            turns = self.turns.get(scope, {})
            turn = turns.pop(message_id, None)
            if not turns:
                self.turns.pop(scope, None)
            if turn is not None:
                turn.finished = True
                if turn.answered_at is None:
                    self._uncover(turn)
            self.cond.notify_all()

    def commit(self, turn):
        with self.cond:
            turn.answered_at = stamp_now()
            self.cond.notify_all()

    def release(self, turn):
        with self.cond:
            self._uncover(turn)
            self.cond.notify_all()

    def close(self):
        with self.cond:
            for turns in self.turns.values():
                for turn in turns.values():
                    turn.finished = True
                    turn.covered_by = None
            self.turns.clear()
            self.cond.notify_all()

    def acquire(self, turn, text, execution) -> Grant:
        """Блокирует поток ответа до очереди; «стоп» прерывает ожидание исключением."""
        with self.cond:
            turn.text, turn.stamp = text, stamp_now()
            grant = self._grant(turn)
        if grant is not None:
            return grant
        execution.update(waiting=True)
        try:
            with self.cond:
                while True:
                    execution.check()
                    grant = self._grant(turn)
                    if grant is not None:
                        return grant
                    self.cond.wait(POLL_SECONDS)
        except BaseException:
            turn.text = None
            raise
        finally:
            execution.update(waiting=False)

    # Ниже — под self.cond.

    def _grant(self, turn):
        leader = turn.covered_by
        if leader is not None:
            # Строка «Ответил выше» уходит после самого ответа, когда ведущий закончил отправку.
            if leader.finished and leader.answered_at is not None:
                return Grant(turn, answered=leader.answered_at)
            return None
        first = next(iter(self.turns.get(turn.scope, {}).values()), None)
        if first is turn:
            return Grant(turn, self._take_batch(turn))
        return None

    def _take_batch(self, turn):
        """Подряд идущие следом сообщения, уже дошедшие до запроса к модели. Порядок не нарушается:
        сообщение, которое ещё не готово (распознаётся голос, идёт другая работа), обрывает пачку."""
        batch, after = [], False
        for other in self.turns.get(turn.scope, {}).values():
            if other is turn:
                after = True
            elif after:
                if other.text is None or other.covered_by is not None:
                    break
                batch.append(other)
        for other in batch:
            other.covered_by = turn
        turn.batch = tuple(batch)
        return batch

    @staticmethod
    def _uncover(turn):
        for other in turn.batch:
            if other.covered_by is turn:
                other.covered_by = None
        turn.batch = ()


def wait_turn(text) -> Grant:
    """Из потока ответа: дождаться очереди. Без очереди (не сообщение чата) пускает сразу."""
    execution = CURRENT_EXECUTION.get()
    turn = getattr(execution, 'turn', None)
    if turn is None:
        return Grant()
    return turn.queue.acquire(turn, text, execution)


def leave_turn():
    """Тяжёлая работа очередь чата не держит: следующие сообщения идут дальше."""
    turn = getattr(CURRENT_EXECUTION.get(), 'turn', None)
    if turn is not None:
        turn.queue.finish(turn.scope, turn.message_id)
