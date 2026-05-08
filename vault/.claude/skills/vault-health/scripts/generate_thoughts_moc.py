#!/usr/bin/env python3
"""
Generate sub-MOC files for thoughts/* and summaries/.

Outputs:
  - MOC-ideas.md       — vault/thoughts/ideas/
  - MOC-learnings.md   — vault/thoughts/learnings/
  - MOC-reflections.md — vault/thoughts/reflections/
  - MOC-weekly.md      — vault/summaries/ (weekly summaries)

For each note: title (H1 or filename) + description from frontmatter (first 120 chars).

Usage:
  uv run vault/.claude/skills/vault-health/scripts/generate_thoughts_moc.py
"""

import re
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VAULT_PATH = SCRIPT_DIR.parents[3]
MOC_DIR = VAULT_PATH / "MOC"

# topic_key -> (subfolder, MOC filename, title)
TOPIC_MAP = [
    ("ideas",       VAULT_PATH / "thoughts" / "ideas",       "MOC-ideas.md",       "Идеи"),
    ("learnings",   VAULT_PATH / "thoughts" / "learnings",   "MOC-learnings.md",   "Уроки и паттерны"),
    ("reflections", VAULT_PATH / "thoughts" / "reflections", "MOC-reflections.md", "Рефлексии"),
    ("weekly",      VAULT_PATH / "summaries",                "MOC-weekly.md",      "Недельные дайджесты"),
]


def parse_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML frontmatter as simple key-value pairs."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm: dict[str, str] = {}
    current_key = None
    for raw in match.group(1).split("\n"):
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith(("  ", "\t")) and current_key:
            continue
        if ":" in line and not line.lstrip().startswith(("-", "#")):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and not value.startswith(("[", "{")):
                fm[key] = value
            current_key = key
    return fm


def extract_title(content: str, fallback: str) -> str:
    """First H1 heading, or fallback (filename)."""
    match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback


def build_entry(file: Path, vault_root: Path) -> str:
    """Format one MOC line: - [[path|Title]] — description"""
    try:
        content = file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    fm = parse_frontmatter(content)
    title = extract_title(content, file.stem)
    rel_path = file.relative_to(vault_root).with_suffix("").as_posix()
    desc = fm.get("description", "").strip()
    if desc:
        desc = desc.replace("\n", " ")
        if len(desc) > 120:
            desc = desc[:117] + "..."
    line = f"- [[{rel_path}|{title}]]"
    if desc:
        line += f" — {desc}"
    return line


def generate_topic_moc(topic_key: str, source_dir: Path, moc_filename: str, title: str) -> int:
    """Generate one sub-MOC. Returns number of entries written."""
    if not source_dir.exists():
        return 0

    files = sorted(
        [p for p in source_dir.rglob("*.md") if p.is_file() and not p.name.startswith(".")],
        key=lambda p: p.relative_to(source_dir).as_posix(),
    )

    lines = [
        "---",
        f"description: \"Map of Content: {title}, {len(files)} entries\"",
        "type: moc",
        f"last_accessed: {datetime.now().strftime('%Y-%m-%d')}",
        "relevance: 0.85",
        "tier: active",
        "---",
        "",
        f"# {title}",
        "",
        f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}. Файлов: {len(files)}.",
        "",
    ]

    if not files:
        lines.append("_Пока пусто._")
    else:
        for file in files:
            entry = build_entry(file, VAULT_PATH)
            if entry:
                lines.append(entry)

    out_path = MOC_DIR / moc_filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(files)


def main() -> None:
    print(f"Vault: {VAULT_PATH}")
    print(f"MOC dir: {MOC_DIR}")
    print()
    total = 0
    for topic_key, source_dir, moc_filename, title in TOPIC_MAP:
        count = generate_topic_moc(topic_key, source_dir, moc_filename, title)
        rel_source = source_dir.relative_to(VAULT_PATH).as_posix() if source_dir.exists() else f"{source_dir.relative_to(VAULT_PATH).as_posix()} (отсутствует)"
        print(f"  {moc_filename}: {count} entries from {rel_source}")
        total += count
    print()
    print(f"Total entries: {total}")


if __name__ == "__main__":
    main()
