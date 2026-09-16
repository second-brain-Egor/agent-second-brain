"""Durable document registry. Full documents never enter conversational memory."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


class DocumentStore:
    def __init__(self, vault: Path):
        self.vault = Path(vault).resolve()
        self.state = self.vault / '.documents'
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY, scope TEXT NOT NULL, sha TEXT NOT NULL,
                    name TEXT NOT NULL, path TEXT NOT NULL, state TEXT NOT NULL,
                    instructions TEXT NOT NULL DEFAULT '', chat_id INTEGER NOT NULL,
                    msg_id INTEGER NOT NULL, created INTEGER NOT NULL,
                    UNIQUE(scope, sha));
                CREATE TABLE IF NOT EXISTS selection (
                    scope TEXT PRIMARY KEY, doc_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS uploads (
                    scope TEXT, msg_id INTEGER, doc_id TEXT,
                    PRIMARY KEY(scope,msg_id));
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, doc_id TEXT NOT NULL, request TEXT NOT NULL,
                    chat_id INTEGER NOT NULL, msg_id INTEGER NOT NULL,
                    state TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                    artifact TEXT, error TEXT, sent_id INTEGER, created INTEGER NOT NULL,
                    UNIQUE(doc_id, chat_id, msg_id));
            ''')

    @contextmanager
    def db(self):
        with sqlite3.connect(self.state / 'state.sqlite3', timeout=20) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA journal_mode=WAL')
            yield conn

    def safe_path(self, relative: str) -> Path:
        path = (self.vault / relative).resolve()
        path.relative_to(self.vault)
        return path

    def get(self, doc_id: str) -> dict:
        with self.db() as db:
            row = db.execute('SELECT * FROM documents WHERE id=?', (doc_id,)).fetchone()
            if not row:
                raise ValueError('Документ не найден')
            return dict(row)

    def update(self, doc_id: str, **values):
        if not set(values) <= {'state', 'path', 'instructions', 'msg_id'}:
            raise ValueError('Invalid fields')
        with self.db() as db:
            db.execute('UPDATE documents SET '+','.join(k+'=?' for k in values)+' WHERE id=?',
                       (*values.values(), doc_id))
        return self.get(doc_id)

    def receive(self, data: bytes, name: str, scope, chat_id: int, msg_id: int,
                instructions: str = '') -> tuple[dict, bool]:
        scope = str(scope)
        digest = hashlib.sha256(data).hexdigest()
        name = re.sub(r'[\\/\x00-\x1f]', '_', name).strip('. ')[:150] or 'document.pdf'
        # Reserve extraction/metadata filenames and stay below filesystem byte limits.
        if name.lower() in {'текст.txt', 'текст.tmp', 'текст.sha256', 'описание.md', 'результаты'}:
            name = 'оригинал-' + name
        suffix = Path(name).suffix[:15]
        name = Path(name).stem.encode('utf-8')[:180].decode('utf-8', errors='ignore') + suffix
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            seen = db.execute('SELECT doc_id FROM uploads WHERE scope=? AND msg_id=?',
                              (scope, msg_id)).fetchone()
            if seen:
                return self.get(seen['doc_id']), False
            row = db.execute('SELECT * FROM documents WHERE scope=? AND sha=?',
                             (scope, digest)).fetchone()
            if row:
                doc_id = row['id']
            else:
                doc_id = uuid4().hex[:16]
                folder = self.state / 'incoming' / doc_id
                folder.mkdir(parents=True)
                (folder / name).write_bytes(data)
                relative = (folder / name).relative_to(self.vault).as_posix()
                db.execute("INSERT INTO documents VALUES (?,?,?,?,?,'destination',?,?,?,unixepoch())",
                           (doc_id, scope, digest, name, relative, instructions, chat_id, msg_id))
            db.execute('INSERT INTO uploads VALUES (?,?,?)', (scope, msg_id, doc_id))
        if row and instructions:
            self.update(doc_id, instructions=instructions, msg_id=msg_id)
        self.select(scope, doc_id)
        return self.get(doc_id), True

    def select(self, scope, doc_id):
        with self.db() as db:
            db.execute('INSERT OR REPLACE INTO selection VALUES (?,?)', (str(scope), doc_id))

    def for_scope(self, scope) -> list[dict]:
        with self.db() as db:
            return [dict(r) for r in db.execute(
                'SELECT d.* FROM documents d LEFT JOIN selection s ON s.scope=d.scope '
                'WHERE d.scope=? ORDER BY (d.id=s.doc_id) DESC, d.created DESC, d.rowid DESC',
                (str(scope),))]

    def import_existing(self, path: Path, scope, chat_id: int, msg_id: int,
                        instructions: str = '') -> dict:
        path = self.safe_path(path.relative_to(self.vault).as_posix())
        doc, fresh = self.receive(path.read_bytes(), path.name, scope, chat_id, msg_id, instructions)
        staged = self.safe_path(doc['path'])
        if fresh and staged.is_relative_to(self.state/'incoming') and staged != path:
            doc = self.update(doc['id'], path=path.relative_to(self.vault).as_posix())
            staged.unlink(missing_ok=True)
            try:
                staged.parent.rmdir()
            except OSError:
                pass
        return doc

    def from_upload(self, scope, msg_id) -> dict | None:
        with self.db() as db:
            r = db.execute('SELECT doc_id FROM uploads WHERE scope=? AND msg_id=?',
                           (str(scope), msg_id)).fetchone()
        return self.get(r['doc_id']) if r else None

    def bind_message(self, doc: dict, message_id: int):
        if not isinstance(message_id, int):
            return
        with self.db() as db:
            db.execute('INSERT OR IGNORE INTO uploads VALUES (?,?,?)',
                       (doc['scope'], message_id, doc['id']))

    def place(self, doc_id: str, project: str | None = None) -> dict:
        doc = self.get(doc_id)
        if doc['state'] == 'ready':
            return doc
        if project is None:
            root = self.vault / ('PDF' if doc['name'].lower().endswith('.pdf') else 'Документы')
        else:
            project = project.strip().strip('«»"')
            if not project or project in {'.', '..'} or len(project) > 100 or re.search(r'[/\\\x00-\x1f]', project):
                raise ValueError('Укажи название проекта без слешей и служебных символов.')
            root = self.safe_path('projects/' + project) / 'Документы'
        stem = re.sub(r'[^\w .-]', '_', Path(doc['name']).stem).strip('. ')[:70] or 'документ'
        stem = stem.encode('utf-8')[:160].decode('utf-8', errors='ignore')
        folder = root / (stem + '-' + doc['id'])
        folder = self.safe_path(str(folder.relative_to(self.vault)))
        source = self.safe_path(doc['path'])
        destination = folder / doc['name']
        folder.mkdir(parents=True, exist_ok=True)
        if source.exists():
            shutil.move(str(source), str(destination))
        elif not destination.exists():
            raise FileNotFoundError('Оригинал документа не найден')
        # A crash after move but before the database commit is recoverable.
        (folder / '.document.json').write_text(json.dumps(
            {'id': doc_id, 'sha256': doc['sha'], 'original': doc['name']}, ensure_ascii=False), encoding='utf-8')
        (folder / 'Описание.md').write_text(
            f"# {doc['name']}\n\nОригинал: {doc['name']}\n\n"
            'Извлечённый текст: текст.txt\n\nГотовые материалы: Результаты/\n', encoding='utf-8')
        old_folder = source.parent
        if old_folder.is_relative_to(self.state / 'incoming') and old_folder.exists():
            try:
                old_folder.rmdir()
            except OSError:
                pass
        return self.update(doc_id, state='ready', path=destination.relative_to(self.vault).as_posix())

    def enqueue(self, doc_id: str, request: str, chat_id: int, msg_id: int) -> dict:
        if self.get(doc_id)['state'] != 'ready':
            raise ValueError('Сначала выбери папку документа')
        with self.db() as db:
            db.execute("INSERT OR IGNORE INTO jobs (id,doc_id,request,chat_id,msg_id,state,created) VALUES (?,?,?,?,?,'queued',unixepoch())",
                       (uuid4().hex[:16], doc_id, request, chat_id, msg_id))
            return dict(db.execute('SELECT * FROM jobs WHERE doc_id=? AND chat_id=? AND msg_id=?',
                                   (doc_id, chat_id, msg_id)).fetchone())

    def job(self, job_id: str) -> dict:
        with self.db() as db:
            return dict(db.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone())

    def latest_job(self, doc_id: str) -> dict | None:
        with self.db() as db:
            row = db.execute('SELECT * FROM jobs WHERE doc_id=? ORDER BY created DESC, rowid DESC LIMIT 1',
                             (doc_id,)).fetchone()
            return dict(row) if row else None

    def jobs(self, states: tuple[str, ...]) -> list[dict]:
        with self.db() as db:
            return [dict(r) for r in db.execute('SELECT * FROM jobs WHERE state IN ('+
                ','.join('?' for _ in states)+') ORDER BY created, rowid', states)]

    def set_job(self, job_id: str, **values):
        if not set(values) <= {'state', 'attempts', 'artifact', 'error', 'sent_id'}:
            raise ValueError('Invalid job fields')
        with self.db() as db:
            db.execute('UPDATE jobs SET '+','.join(k+'=?' for k in values)+' WHERE id=?',
                       (*values.values(), job_id))

    def claim(self, job_id: str, old: str, new: str) -> bool:
        with self.db() as db:
            return db.execute('UPDATE jobs SET state=? WHERE id=? AND state=?',
                              (new, job_id, old)).rowcount == 1

    def recover(self):
        with self.db() as db:
            # Telegram has no idempotency key: an interrupted send must not be replayed.
            db.execute("UPDATE jobs SET state='send_unknown' WHERE state='sending'")
            db.execute("UPDATE jobs SET state='queued' WHERE state IN ('extracting','generating') AND attempts<2")
            db.execute("UPDATE jobs SET state='failed', error='Обработка прервана при перезапуске после двух попыток' WHERE state IN ('extracting','generating') AND attempts>=2")

    def context(self, scope) -> str:
        documents = self.for_scope(scope)[:5]
        if not documents:
            return ''
        states = {'ready': 'сохранён', 'destination': 'ожидает выбора папки',
                  'project': 'ожидает названия проекта'}
        lines = ['=== ДОСТУПНЫЕ ДОКУМЕНТЫ ===']
        for doc in documents:
            lines.append(f"{doc['name']}: {doc['path']} ({states.get(doc['state'], doc['state'])})")
            job = self.latest_job(doc['id'])
            if job:
                job_states = {'queued': 'в очереди', 'extracting': 'чтение документа',
                    'generating': 'подготовка результата', 'ready': 'файл готов к отправке',
                    'sending': 'отправляется', 'sent': 'файл отправлен в чат',
                    'failed': 'ошибка обработки', 'error_reported': 'ошибка обработки',
                    'send_unknown': 'отправка не подтверждена',
                    'uncertain_reported': 'отправка не подтверждена'}
                lines.append('Задание: '+job_states.get(job['state'], job['state']))
                if job['artifact']:
                    lines.append('Результат: '+job['artifact'])
        lines.append('Полный текст хранится рядом с оригиналом в текст.txt после чтения. '
                     'Не переноси его в общую память. Для документов во входящих '
                     'сначала нужен выбор папки пользователем; не выбирай за него.')
        return '\n'.join(lines)


def render_file_entry(entry: dict) -> str:
    parts = [f"Документ: {entry.get('name') or Path(entry.get('path') or '').name}"]
    for key, label in [('path','Путь'), ('caption','Задание'), ('text_path','Полный текст'), ('summary','Описание')]:
        if entry.get(key):
            parts.append(f'{label}: {entry[key]}')
    if entry.get('text'):
        parts.append(str(entry['text'])[:3500])
    return '\n'.join(parts)
