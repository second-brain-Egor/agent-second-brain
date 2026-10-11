"""Заголовки навыков, агентов и правил целы.

10 октября 2026 ночная обработка памяти записала в них поля обычных карточек
(`type: note`, `relevance`, `tier`…) и затёрла `name` и `description`; Claude перестал
находить навыки по описанию, а заметили это только через /doctor.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
MEMORY_CARD_FIELDS = {"type", "last_accessed", "relevance", "tier"}

SKILLS = sorted([*VAULT.glob(".claude/skills/*/SKILL.md"), *ROOT.glob("Скиллы/*/SKILL.md"),
                 *VAULT.glob("projects/*/.skills/*/SKILL.md")])
AGENTS = sorted([*VAULT.glob(".claude/agents/*.md"), *VAULT.glob("projects/*/.agents/*.md")])
RULES = sorted(VAULT.glob(".claude/rules/*.md"))


def frontmatter(path: Path) -> dict[str, str] | None:
    """Ключи верхнего уровня заголовка; None, если заголовка нет или он не закрыт."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    fields: dict[str, str] = {}
    key = None
    for line in match.group(1).splitlines():
        top = re.match(r"([A-Za-z_][\w-]*):\s*(.*)$", line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            fields[key] = value.strip("\"'") if value not in {">", "|", ">-", "|-"} else ""
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields


def name(path: Path) -> str:
    return str(path.relative_to(ROOT))


def test_files_found():
    assert SKILLS and AGENTS and RULES


@pytest.mark.parametrize("path", SKILLS, ids=name)
def test_skill_header(path):
    fields = frontmatter(path)
    assert fields is not None, "нет заголовка --- в начале файла"
    assert fields.get("name") == path.parent.name, "name не совпадает с папкой навыка"
    assert 20 <= len(fields.get("description", "")) <= 1024, "description пустой или длиннее 1024 знаков"
    assert not MEMORY_CARD_FIELDS & fields.keys(), "в заголовке поля карточки памяти"


@pytest.mark.parametrize("path", AGENTS, ids=name)
def test_agent_header(path):
    fields = frontmatter(path)
    assert fields is not None, "нет заголовка --- в начале файла"
    assert fields.get("name") == path.stem, "name не совпадает с именем файла агента"
    assert len(fields.get("description", "")) >= 20, "description пустой"
    assert not MEMORY_CARD_FIELDS & fields.keys(), "в заголовке поля карточки памяти"


@pytest.mark.parametrize("path", RULES, ids=name)
def test_rule_header(path):
    if not path.read_text(encoding="utf-8").startswith("---"):
        return
    fields = frontmatter(path)
    assert fields is not None, "заголовок не закрыт"
    assert not MEMORY_CARD_FIELDS & fields.keys(), "в заголовке поля карточки памяти"
