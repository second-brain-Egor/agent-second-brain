"""Durable incoming updates; only work that has not started is replayed."""
import sqlite3


class RequestInbox:
    def __init__(self, vault):
        path = vault / '.session' / 'request-inbox.sqlite3'
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS inbox (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE NOT NULL,
                scope TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL,
                transcript TEXT)''')
            db.execute("UPDATE inbox SET state='interrupted' WHERE state='running'")
        path.chmod(0o600)

    def connect(self):
        return sqlite3.connect(self.path)

    def accept(self, key, scope, payload):
        with self.connect() as db:
            return bool(db.execute(
                "INSERT OR IGNORE INTO inbox(key,scope,payload,state) VALUES(?,?,?,'queued')",
                (key, str(scope), payload)).rowcount)

    def set(self, key, state, transcript=None):
        with self.connect() as db:
            db.execute('UPDATE inbox SET state=?, transcript=COALESCE(?,transcript) WHERE key=?',
                       (state, transcript, key))

    def stop(self, scope):
        with self.connect() as db:
            db.execute("UPDATE inbox SET state='stopped' WHERE scope=? AND state IN ('queued','running')",
                       (str(scope),))

    def pending(self):
        with self.connect() as db:
            return db.execute("SELECT key,payload,transcript FROM inbox WHERE state='queued' ORDER BY seq").fetchall()
