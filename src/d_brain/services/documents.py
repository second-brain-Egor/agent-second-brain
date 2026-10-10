"""Durable document registry. Full documents never enter conversational memory."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from uuid import uuid4

SERVICE_DIR = '.служебное'
JOURNAL = 'Журнал документов.md'
# Егор, 10 октября 2026: фото без проекта больше не копятся во вложениях по датам. Как документы,
# они ждут во входящих, а помощник кладёт их в проект по теме или в общую папку «Фото».
PHOTOS = 'Фото'
PHOTO_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.gif'}
# Егор, 8 октября 2026: бот помнит проект, в котором идёт работа, и кладёт туда файлы и фото
# без вопросов. Проект давно не трогали — бот снова спрашивает, чтобы вчерашняя работа
# не забирала сегодняшние файлы.
ACTIVE_HOURS = 12


def service_dir(original: Path) -> Path:
    """Extracted text and metadata live in a hidden folder beside the original."""
    return original.parent / SERVICE_DIR / original.stem


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folder_key(name: str) -> str:
    """Voice gives «ирина работа.» for the folder «Ирина работа»."""
    return ' '.join(name.casefold().replace('ё', 'е').replace('«', ' ').replace('»', ' ')
                    .replace('"', ' ').split()).strip(' .,!')


def folder_label(path: str) -> str:
    """«проект «X», подпроект «Y»» for the folder of a vault-relative file path."""
    folder = Path(path).parent.parts
    if len(folder) >= 2 and folder[0] == 'projects':
        if len(folder) == 2:
            return f'корень проекта «{folder[1]}»'
        return f"проект «{folder[1]}», подпроект «{'/'.join(folder[2:])}»"
    return f"папку {'/'.join(folder)}"


def is_photo(name: str) -> bool:
    return Path(name).suffix.lower() in PHOTO_SUFFIXES


def general_folder(name: str, topic: str | None = None) -> str:
    """Common folder for a file outside projects: «Фото», «PDF» or «Документы», optionally by topic."""
    folder = PHOTOS if is_photo(name) else 'PDF' if name.lower().endswith('.pdf') else 'Документы'
    return folder + ('/' + clean_folder_name(topic, 'темы') if topic else '')


def note_placement(store: 'DocumentStore', doc: dict, when: datetime) -> Path | None:
    """A placed file gets a line in the daily note and, if the project keeps one, its document journal."""
    from d_brain.services.storage import VaultStorage
    VaultStorage(store.vault).append_to_daily(
        f"Документ: {doc['name']}\nПапка: {Path(doc['path']).parent.as_posix()}", when, '[file]')
    return store.journal(doc, when)


def clean_folder_name(name: str, what: str = 'проекта') -> str:
    name = name.strip().strip('«»"').strip(' .,!')
    if not name or name in {'.', '..'} or len(name) > 100 or re.search(r'[/\\\x00-\x1f]', name):
        raise ValueError(f'Укажи название {what} без слешей и служебных символов.')
    return name


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
                CREATE TABLE IF NOT EXISTS subproject_choice (
                    doc_id TEXT PRIMARY KEY, project TEXT NOT NULL, options TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS project_choice (
                    doc_id TEXT PRIMARY KEY, options TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS active_project (
                    scope TEXT PRIMARY KEY, project TEXT NOT NULL,
                    subproject TEXT NOT NULL DEFAULT '', updated INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS placements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL, path TEXT NOT NULL,
                    kind TEXT NOT NULL, created INTEGER NOT NULL, checked INTEGER NOT NULL DEFAULT 0);
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

    def project_name(self, name: str) -> str:
        """Existing project folder for a typed or spoken name; otherwise the cleaned name."""
        name = clean_folder_name(name)
        projects = self.vault / 'projects'
        if projects.is_dir():
            for folder in projects.iterdir():
                if folder.is_dir() and folder_key(folder.name) == folder_key(name):
                    return folder.name
        return name

    def subprojects(self, project: str) -> list[str]:
        root = self.safe_path('projects/' + clean_folder_name(project))
        if not root.is_dir():
            return []
        return sorted((p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith('.')),
                      key=folder_key)

    def ask_subproject(self, doc_id: str, project: str) -> dict:
        """Remember the project and the exact list of subprojects shown as buttons."""
        project = self.project_name(project)
        options = self.subprojects(project)
        with self.db() as db:
            db.execute('INSERT OR REPLACE INTO subproject_choice VALUES (?,?,?)',
                       (doc_id, project, json.dumps(options, ensure_ascii=False)))
            db.execute("UPDATE documents SET state='subproject' WHERE id=?", (doc_id,))
        return {'project': project, 'options': options, 'exists': (self.vault/'projects'/project).is_dir()}

    def subproject_choice(self, doc_id: str) -> dict | None:
        with self.db() as db:
            row = db.execute('SELECT * FROM subproject_choice WHERE doc_id=?', (doc_id,)).fetchone()
        return {'project': row['project'], 'options': json.loads(row['options'])} if row else None

    def projects(self) -> list[str]:
        """Project folders, the most recently touched first."""
        root = self.vault / 'projects'
        if not root.is_dir():
            return []

        def touched(folder: Path) -> float:
            stamps = [folder.stat().st_mtime]
            stamps += [p.stat().st_mtime for p in folder.iterdir() if not p.name.startswith('.')]
            return max(stamps)
        folders = [p for p in root.iterdir() if p.is_dir() and not p.name.startswith(('.', '_'))]
        return [p.name for p in sorted(folders, key=lambda p: (-touched(p), folder_key(p.name)))]

    def offer_projects(self, doc_id: str, options: list[str]) -> list[str]:
        """Remember the exact project list shown as buttons for this document."""
        with self.db() as db:
            db.execute('INSERT OR REPLACE INTO project_choice VALUES (?,?)',
                       (doc_id, json.dumps(options, ensure_ascii=False)))
        return options

    def offered_projects(self, doc_id: str) -> list[str]:
        with self.db() as db:
            row = db.execute('SELECT options FROM project_choice WHERE doc_id=?', (doc_id,)).fetchone()
        return json.loads(row['options']) if row else []

    def existing_project(self, name: str) -> str | None:
        """Folder name of an existing project for a typed or spoken name."""
        try:
            name = self.project_name(name)
        except ValueError:
            return None
        return name if (self.vault / 'projects' / name).is_dir() else None

    def active_project(self, scope, stale: bool = False) -> dict | None:
        """The project we are working in; None once untouched for ACTIVE_HOURS (unless stale=True)."""
        with self.db() as db:
            row = db.execute("SELECT *, unixepoch() - updated AS age FROM active_project WHERE scope=?",
                             (str(scope),)).fetchone()
        if not row or not (self.vault / 'projects' / row['project']).is_dir():
            return None
        if not stale and row['age'] > ACTIVE_HOURS * 3600:
            return None
        return {'project': row['project'], 'subproject': row['subproject'] or None}

    def set_active(self, scope, project: str, subproject: str | None = None) -> dict:
        project = self.project_name(project)
        subproject = clean_folder_name(subproject, 'подпроекта') if subproject else ''
        with self.db() as db:
            db.execute('INSERT OR REPLACE INTO active_project VALUES (?,?,?,unixepoch())',
                       (str(scope), project, subproject))
        return {'project': project, 'subproject': subproject or None}

    def clear_active(self, scope):
        with self.db() as db:
            db.execute('DELETE FROM active_project WHERE scope=?', (str(scope),))

    def touch_active(self, scope):
        with self.db() as db:
            db.execute('UPDATE active_project SET updated=unixepoch() WHERE scope=?', (str(scope),))

    def active_folder(self, scope) -> Path | None:
        active = self.active_project(scope)
        if not active:
            return None
        folder = 'projects/' + active['project'] + ('/' + active['subproject'] if active['subproject'] else '')
        return self.safe_path(folder)

    def record_placement(self, scope, path: str, kind: str):
        """The bot put a file into the current project itself; the assistant checks the place later."""
        with self.db() as db:
            db.execute('INSERT INTO placements (scope,path,kind,created) VALUES (?,?,?,unixepoch())',
                       (str(scope), path, kind))

    def unchecked(self, scope) -> list[dict]:
        with self.db() as db:
            return [dict(r) for r in db.execute(
                'SELECT * FROM placements WHERE scope=? AND checked=0 ORDER BY id', (str(scope),))]

    def mark_checked(self, ids: list[int]):
        if not ids:
            return
        with self.db() as db:
            db.execute('UPDATE placements SET checked=1 WHERE id IN (' + ','.join('?' for _ in ids) + ')', ids)

    def move(self, relative: str, project: str | None, subproject: str | None = None,
             topic: str | None = None) -> str:
        """Move a placed file (with its service folder) to another project/subproject or a common folder."""
        source = self.safe_path(relative)
        if not source.is_file():
            raise FileNotFoundError(relative)
        if project:
            folder = 'projects/' + self.project_name(project)
            if subproject:
                folder += '/' + clean_folder_name(subproject, 'подпроекта')
        else:
            folder = general_folder(source.name, topic)
        root = self.safe_path(folder)
        destination = root / source.name
        number = 1
        while destination.exists() and destination != source:
            number += 1
            destination = root / f'{source.stem} ({number}){source.suffix}'
        destination = self.safe_path(destination.relative_to(self.vault).as_posix())
        if destination == source:
            return relative
        root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        old_meta, new_meta = service_dir(source), service_dir(destination)
        if old_meta.is_dir() and not new_meta.exists():
            new_meta.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_meta), str(new_meta))
            try:
                old_meta.parent.rmdir()
            except OSError:
                pass
        moved = destination.relative_to(self.vault).as_posix()
        with self.db() as db:
            db.execute('UPDATE documents SET path=? WHERE path=?', (moved, relative))
            db.execute('UPDATE placements SET path=? WHERE path=?', (moved, relative))
        self.relink(relative, moved)
        return moved

    def relink(self, old: str, new: str) -> list[str]:
        """Point embeds and links in notes (the photo in the daily note first of all) at the new place."""
        changed = []
        for folder, subfolders, files in os.walk(self.vault):
            subfolders[:] = [name for name in subfolders if not name.startswith('.')]  # .git, .documents…
            for name in files:
                if not name.endswith('.md'):
                    continue
                note = Path(folder) / name
                try:
                    text = note.read_text(encoding='utf-8')
                except (OSError, UnicodeDecodeError):
                    continue
                if old in text:
                    note.write_text(text.replace(old, new), encoding='utf-8')
                    changed.append(note.relative_to(self.vault).as_posix())
        return changed

    def place(self, doc_id: str, project: str | None = None, subproject: str | None = None,
              topic: str | None = None) -> dict:
        doc = self.get(doc_id)
        if doc['state'] == 'ready':
            return doc
        if project is None:
            root = self.safe_path(general_folder(doc['name'], topic))
        else:
            # Егор, 8 октября 2026: файл ложится прямо в папку проекта (или выбранного подпроекта),
            # без подпапки «Документы» и отдельной папки на каждый файл; служебное — в .служебное/.
            folder = 'projects/' + clean_folder_name(project)
            if subproject:
                folder += '/' + clean_folder_name(subproject, 'подпроекта')
            root = self.safe_path(folder)
        source = self.safe_path(doc['path'])
        name = Path(doc['name'])
        destination = self.safe_path((root / name).relative_to(self.vault).as_posix())
        number = 1
        # Same content already in the folder is reused; a different file keeps both names.
        while destination.exists() and not (destination.is_file() and sha256_file(destination) == doc['sha']):
            number += 1
            destination = self.safe_path((root / f'{name.stem} ({number}){name.suffix}').relative_to(self.vault).as_posix())
        root.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if source != destination:
                source.unlink(missing_ok=True)
        elif source.exists():
            shutil.move(str(source), str(destination))
        else:
            raise FileNotFoundError('Оригинал документа не найден')
        # A crash after move but before the database commit is recoverable.
        meta = service_dir(destination)
        meta.mkdir(parents=True, exist_ok=True)
        (meta / '.document.json').write_text(json.dumps(
            {'id': doc_id, 'sha256': doc['sha'], 'original': doc['name']}, ensure_ascii=False), encoding='utf-8')
        old_folder = source.parent
        if old_folder.is_relative_to(self.state / 'incoming') and old_folder.exists():
            try:
                old_folder.rmdir()
            except OSError:
                pass
        with self.db() as db:
            db.execute('DELETE FROM subproject_choice WHERE doc_id=?', (doc_id,))
            db.execute('DELETE FROM project_choice WHERE doc_id=?', (doc_id,))
        placed = destination.relative_to(self.vault).as_posix()
        if is_photo(doc['name']):
            self.relink(doc['path'], placed)  # the daily note already embeds the photo from incoming
        return self.update(doc_id, state='ready', path=placed)

    def journal(self, doc: dict, when: datetime, action: str | None = None) -> Path | None:
        """Add a line to «Записи» of the project's document journal, if the project keeps one."""
        parts = Path(doc['path']).parts
        if len(parts) < 3 or parts[0] != 'projects':
            return None
        journal = self.safe_path(f'projects/{parts[1]}/{JOURNAL}')
        if not journal.is_file():
            return None
        where = '/'.join(parts[2:-1])
        what = f'{action} «{parts[-1]}»' if action else f'бот получил «{parts[-1]}» и положил'
        line = (f"- {when:%Y-%m-%d %H:%M} — {what} "
                + (f"в подпроект «{where}»." if where else 'в корень проекта.'))
        text = journal.read_text(encoding='utf-8')
        start = text.find('\n## Записи')
        end = text.find('\n## ', start + 1) if start >= 0 else -1
        if end < 0:
            text = text.rstrip('\n') + '\n' + line + '\n'
        else:
            text = text[:end].rstrip('\n') + '\n' + line + '\n' + text[end:]
        journal.write_text(text, encoding='utf-8')
        return journal

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
            db.execute("UPDATE jobs SET state='failed', error='Обработка прервана перезапуском. Документ и задание сохранены; автоповтор отключён.' WHERE state IN ('extracting','generating')")

    def project_context(self, scope) -> str:
        """Current project and files the bot placed there itself, for the assistant's prompt."""
        active = self.active_project(scope)
        tool = f'uv run python scripts/project_context.py --scope {scope}'
        if active:
            where = active['project'] + (f" / {active['subproject']}" if active['subproject'] else ' (корень)')
            lines = ['=== ТЕКУЩИЙ ПРОЕКТ ===', f'Работаем в проекте: {where}. Новые документы и фото '
                     'бот без вопросов кладёт сюда.']
        else:
            lines = ['=== ТЕКУЩИЙ ПРОЕКТ ===', 'Проект не выбран: новые файлы и фото ждут во входящих. '
                     'Бот ни о чём не спрашивает, место выбираешь ты по разговору.']
        lines.append('Если разговор однозначно перешёл к другому проекту или подпроекту, переключи его сам '
                     f'(`{tool} set "Проект" ["Подпроект"]`) и скажи об этом одной строкой; при реальном '
                     f'сомнении переспроси. «Выйди из проекта» — `{tool} clear`. Список проектов — '
                     f'`{tool} list`.')
        placed = self.unchecked(scope)
        if placed:
            lines.append('=== НОВЫЕ ФАЙЛЫ: ПРОВЕРЬ МЕСТО ===')
            lines += [f"- {p['path']}" for p in placed[-20:]]
            lines.append('Бот положил их в текущий проект сам. Сверь каждый с проектом по содержимому и '
                         'разговору. Сомнений нет — ничего об этом не пиши. Есть сомнение или файл явно не '
                         'отсюда — спроси, куда положить, и предложи вариант; переноси только после ответа: '
                         f'`{tool} move "<путь от vault>" "Проект" ["Подпроект"]` (без проекта — в общую '
                         'папку, тема — `--topic "Тема"`).')
        return '\n'.join(lines)

    def context(self, scope) -> str:
        project = self.project_context(scope)
        documents = self.for_scope(scope)[:5]
        if not documents:
            return project
        states = {'ready': 'сохранён', 'destination': 'во входящих, место не выбрано',
                  'project': 'ожидает названия проекта', 'subproject': 'ожидает выбора подпроекта',
                  'subproject_new': 'ожидает названия нового подпроекта'}
        lines = ['=== ДОСТУПНЫЕ ДОКУМЕНТЫ ===']
        for doc in documents:
            lines.append(f"{doc['name']}: {doc['path']} ({states.get(doc['state'], doc['state'])})")
            job = self.latest_job(doc['id'])
            if job:
                job_states = {'queued': 'в очереди', 'extracting': 'чтение документа',
                    'generating': 'подготовка результата', 'ready': 'файл готов к отправке',
                    'sending': 'отправляется', 'sent': 'файл отправлен в чат',
                    'stopped': 'остановлено', 'failed': 'ошибка обработки', 'error_reported': 'ошибка обработки',
                    'send_unknown': 'отправка не подтверждена',
                    'uncertain_reported': 'отправка не подтверждена'}
                lines.append('Задание: '+job_states.get(job['state'], job['state']))
                if job['artifact'] and (self.vault/job['artifact']).exists():
                    lines.append('Результат: '+job['artifact'])
        lines.append(f'Полный текст после чтения хранится рядом с оригиналом в {SERVICE_DIR}/<имя файла>/текст.txt. '
                     'Не переноси его в общую память.')
        # Егор, 9 октября 2026: место для присланного файла выбирает помощник по разговору, не бот.
        tool = f"uv run python scripts/project_context.py --scope {scope}"
        waiting = sum(doc['state'] == 'destination' for doc in self.for_scope(scope)[5:])
        if waiting:
            lines.append(f'Ещё во входящих, место не выбрано: {waiting}.')
        lines.append('Файл или фото во входящих: реши по разговору и содержимому, к чему он относится. Ясно — '
                     f'положи сам: `{tool} place "<путь от vault>" "Проект" ["Подпроект"]`; без проекта — в '
                     'общую папку (фото в Фото, PDF в PDF, остальное в Документы), тему внутри неё задай '
                     '`--topic "Тема"`, чтобы не копилась свалка. Скажи одной строкой куда. Служебный файл, '
                     'который нужен для настройки (ключ, куки, конфиг), подключи по назначению. Спрашивай, '
                     'только если файл из другой области и место не понять.')
        # Document tasks are done in the chat itself (handlers/document.py: AUTOMATIC_JOBS).
        lines.append('Готовый файл клади в папку проекта и отправляй в чат: uv run python '
                     f"scripts/send_telegram_file.py \"<путь от vault>\" --chat-id {documents[0]['chat_id']}")
        return project + '\n' + '\n'.join(lines)


def render_file_entry(entry: dict) -> str:
    parts = [f"Документ: {entry.get('name') or Path(entry.get('path') or '').name}"]
    for key, label in [('path','Путь'), ('caption','Задание'), ('text_path','Полный текст'), ('summary','Описание')]:
        if entry.get(key):
            parts.append(f'{label}: {entry[key]}')
    if entry.get('text'):
        parts.append(str(entry['text'])[:3500])
    return '\n'.join(parts)
