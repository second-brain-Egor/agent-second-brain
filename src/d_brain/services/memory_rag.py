"""
RAG-память: ежедневно извлекает факты из vault → SQLite FTS5.
При запросе — полнотекстовый поиск вместо чтения всего файла.
Semantic search через sentence-transformers — в бэклоге.
"""

import os
import re
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = os.path.join(os.environ.get("PROJECT_DIR", "."), "vault", ".data", "memory.db")


def _get_db_path() -> str:
    """Get database path, trying multiple strategies."""
    # Try PROJECT_DIR env var
    project_dir = os.environ.get("PROJECT_DIR")
    if project_dir:
        return os.path.join(project_dir, "vault", ".data", "memory.db")
    # Try relative to this file
    this_dir = Path(__file__).resolve().parent
    vault_data = this_dir.parent.parent.parent / "vault" / ".data"
    vault_data.mkdir(parents=True, exist_ok=True)
    return str(vault_data / "memory.db")


def _init_db(conn: sqlite3.Connection) -> None:
    """Initialize database tables."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY,
            source TEXT,
            content TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
            content, source, content=facts, content_rowid=id
        )
    """)
    conn.commit()


def _extract_facts(text: str) -> list[str]:
    """Extract facts from markdown text (each non-empty paragraph = one fact)."""
    # Remove frontmatter
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    # Remove headings that are just structural
    text = re.sub(r"^#+\s*$", "", text, flags=re.MULTILINE)
    # Split by double newline (paragraphs) or list items
    paragraphs = re.split(r"\n\n+", text)
    facts = []
    for p in paragraphs:
        p = p.strip()
        if len(p) > 20 and not p.startswith("#"):  # Skip short lines and headings
            facts.append(p)
    return facts


def index_daily(vault_path: str | None = None) -> int:
    """Index vault markdown files into SQLite FTS5.

    Args:
        vault_path: Path to vault directory

    Returns:
        Number of facts indexed
    """
    db_path = _get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if vault_path is None:
        vault_path = str(Path(db_path).parent.parent)

    vault = Path(vault_path)
    conn = sqlite3.connect(db_path)
    _init_db(conn)

    # Clear existing data (full reindex)
    conn.execute("DELETE FROM facts")
    conn.execute("DELETE FROM facts_fts")

    count = 0
    for subdir in ["daily", "thoughts", "memory"]:
        dir_path = vault / subdir
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob("*.md"):
            try:
                text = md_file.read_text(errors="ignore")
                facts = _extract_facts(text)
                source = f"{subdir}/{md_file.name}"
                today = date.today().isoformat()
                for fact in facts:
                    conn.execute(
                        "INSERT INTO facts (source, content, created_at) VALUES (?, ?, ?)",
                        (source, fact, today),
                    )
                    count += 1
            except Exception:
                continue

    # Rebuild FTS index
    conn.execute("INSERT INTO facts_fts(facts_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()
    return count


def search_memory(query: str, limit: int = 5) -> str:
    """Search memory using FTS5.

    Args:
        query: Search query
        limit: Max results

    Returns:
        Formatted string with relevant facts
    """
    db_path = _get_db_path()
    if not os.path.exists(db_path):
        return ""

    try:
        conn = sqlite3.connect(db_path)
        # Sanitize query for FTS5 (remove special chars)
        safe_query = re.sub(r"[^\w\s]", " ", query)
        safe_query = " ".join(safe_query.split())
        if not safe_query:
            return ""

        rows = conn.execute(
            "SELECT content, source FROM facts_fts WHERE facts_fts MATCH ? ORDER BY rank LIMIT ?",
            (safe_query, limit),
        ).fetchall()
        conn.close()

        if not rows:
            return ""
        return "\n".join(f"- {row[0][:200]} (из {row[1]})" for row in rows)
    except Exception:
        return ""
