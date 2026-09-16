"""Presentation format choices, persisted separately from conversational memory."""
from __future__ import annotations

import re
from uuid import uuid4

from d_brain.services.documents import DocumentStore


POWERPOINT = r'(?:power\s*point|poyer\s*point|пау[эе]р\s*по[ий]нт|повер\s*по[ий]нт|pptx)'
PDF = r'(?:pdf|пдф|пэдээф)'
FORMAT = rf'(?:{POWERPOINT}|{PDF})'


def presentation_request(text: str) -> bool:
    return bool(re.search(r'презентац|с[лд]айд', text, re.I) and (re.search(
        r'сдела|созда|подготов|состав|собери|оформ|пришли|отправ|нуж[ен]|хочу|можешь|презентацию', text, re.I)
        or re.match(r'^(?:пожалуйста[, ]+)?(?:презентация|слайды)\b', text.strip(), re.I)))


def format_reply(text: str) -> str | None:
    value = text.strip().strip('.!').strip()
    match = re.fullmatch(rf'(?:(?:давай|лучше|нужен|нужна|хочу|выбираю|пришли|отправь)\s+)?'
                        rf'(?:(?:в\s+)?формате\s+|в\s+)?({FORMAT})'
                        rf'(?:\s*\(\.pptx\))?(?:,?\s+пожалуйста)?', value, re.I)
    if not match:
        return None
    return 'pdf' if re.fullmatch(PDF, match[1], re.I) else 'pptx'


def explicit_format(text: str) -> str | None:
    # A source named PDF is not a request to deliver the slides as PDF.
    reply = format_reply(text)
    if reply:
        return reply
    forced = re.search(r'Формат результата: (pptx|pdf)\.', text)
    if forced:
        return forced[1]
    matches = list(re.finditer(
        rf'\b(?:в\s+(?:формате\s+)?|формат(?:е|а)?\s*[:—-]?\s+|как\s+|'
        rf'(?:презентаци[юяи]|слайды)\s+)({FORMAT})\b', text, re.I))
    formats = {('pdf' if re.fullmatch(PDF, m[1], re.I) else 'pptx') for m in matches
               if not re.search(r'\bне\s*$', text[:m.start()], re.I)}
    # PowerPoint/.pptx unambiguously names the requested presentation application.
    if re.search(rf'\b{POWERPOINT}\b', text, re.I):
        formats.add('pptx')
    if re.search(rf'\b{PDF}\b\s*(?:или|и|/)\s*{POWERPOINT}\b|'
                 rf'\b{POWERPOINT}\b\s*(?:или|и|/)\s*{PDF}\b', text, re.I):
        return None
    return next(iter(formats)) if len(formats) == 1 else None


def with_format(request: str, fmt: str) -> str:
    if fmt not in {'pptx', 'pdf'}:
        raise ValueError('Неизвестный формат презентации')
    request = re.sub(r'\n\nФормат результата: (?:pptx|pdf)\..*$', '', request, flags=re.S)
    label = 'PowerPoint (.pptx)' if fmt == 'pptx' else 'PDF (.pdf)'
    return request + f'\n\nФормат результата: {fmt}. Подготовь и пришли файл {label}.'


class PresentationChoices:
    def __init__(self, store: DocumentStore):
        self.store = store
        with store.db() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS presentation_choices (
                id TEXT PRIMARY KEY, scope TEXT NOT NULL, chat_id INTEGER NOT NULL,
                msg_id INTEGER NOT NULL, doc_id TEXT, request TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'pending', format TEXT, prompt_id INTEGER,
                UNIQUE(scope, chat_id, msg_id))''')

    def create(self, scope, chat_id, msg_id, request, doc_id=None):
        with self.store.db() as db:
            db.execute('INSERT OR IGNORE INTO presentation_choices '
                       '(id,scope,chat_id,msg_id,doc_id,request) VALUES (?,?,?,?,?,?)',
                       (uuid4().hex[:16], str(scope), chat_id, msg_id, doc_id, request))
            return dict(db.execute('SELECT * FROM presentation_choices '
                                  'WHERE scope=? AND chat_id=? AND msg_id=?',
                                  (str(scope), chat_id, msg_id)).fetchone())

    def get(self, choice_id):
        with self.store.db() as db:
            row = db.execute('SELECT * FROM presentation_choices WHERE id=?', (choice_id,)).fetchone()
            return dict(row) if row else None

    def bind(self, choice_id, message_id):
        if isinstance(message_id, int):
            with self.store.db() as db:
                db.execute('UPDATE presentation_choices SET prompt_id=? WHERE id=?', (message_id, choice_id))

    def pending(self, scope, chat_id, reply_id=None):
        with self.store.db() as db:
            rows = db.execute("SELECT * FROM presentation_choices WHERE scope=? AND chat_id=? "
                              "AND state='pending' ORDER BY rowid DESC", (str(scope), chat_id)).fetchall()
            if reply_id is not None:
                rows = [r for r in rows if reply_id in {r['prompt_id'], r['msg_id']}]
            return dict(rows[0]) if rows else None

    def resolve(self, choice_id, fmt):
        with self.store.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute("SELECT * FROM presentation_choices WHERE id=? AND state='pending'",
                             (choice_id,)).fetchone()
            if not row:
                return False
            request = with_format(row['request'], fmt)
            if row['doc_id']:
                doc = db.execute('SELECT state FROM documents WHERE id=?', (row['doc_id'],)).fetchone()
                if not doc or doc['state'] != 'ready':
                    raise ValueError('Сначала выбери папку документа')
                db.execute("INSERT OR IGNORE INTO jobs (id,doc_id,request,chat_id,msg_id,state,created) "
                           "VALUES (?,?,?,?,?,'queued',unixepoch())",
                           (uuid4().hex[:16], row['doc_id'], request, row['chat_id'], row['msg_id']))
            db.execute("UPDATE presentation_choices SET state='selected', format=? WHERE id=?", (fmt, choice_id))
            return True

    def cancel(self, choice_id):
        with self.store.db() as db:
            db.execute("UPDATE presentation_choices SET state='cancelled' WHERE id=? AND state='pending'", (choice_id,))
