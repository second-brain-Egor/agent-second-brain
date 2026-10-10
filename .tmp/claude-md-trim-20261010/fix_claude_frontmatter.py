"""Clean vault/.claude/**.md frontmatter damaged by memory-engine decay.

- drops the injected keys (type: note, last_accessed, relevance, tier);
- removes the frontmatter block when nothing else is left;
- puts back the headers whose multi-line values were lost.

Usage: fix_claude_frontmatter.py <vault/.claude dir> [--apply]
"""
import re
import sys
from pathlib import Path

JUNK = re.compile(r"^(type: note|last_accessed: .*|relevance: .*|tier: .*)$")

AGENT_TRIGGERS = {
    "goal-aligner": ["проверь выравнивание целей", "alignment check"],
    "inbox-processor": ["обработай входящие", "inbox processing"],
    "note-organizer": ["организуй заметки", "organize vault"],
    "weekly-digest": ["недельный дайджест", "weekly digest"],
}


def triggers(items):
    return "triggers:\n" + "".join(f"  - {i}\n" for i in items)


# Full replacement headers (text between the --- lines), keyed by path relative to .claude/
HEADERS = {
    "skills/agent-memory/SKILL.md": (
        "name: agent-memory\n"
        'description: "Memory system for markdown files with automatic decay, tiered search and creative recall. '
        "Use when: (1) setting up memory for a new agent, (2) diagnosing memory bloat or context problems. "
        'Triggers: memory management, organize vault, memory decay, forgetting curve."\n'
    ),
    "skills/dbrain-processor/SKILL.md": (
        "name: dbrain-processor\n"
        'description: "Обработка записей дня из Telegram (голос, текст, пересылки, фото): классификация, '
        "задачи в Todoist по целям, мысли в Obsidian с wiki-ссылками, HTML-отчёт. "
        'Запускается командой /process или из process-randomized.sh."\n'
    ),
    "skills/graph-builder/SKILL.md": (
        "name: graph-builder\n"
        'description: "Analyze and build knowledge graph links in Obsidian vault. Runs a deterministic script '
        'for analysis, then the agent adds semantic links to orphan files. Three domains: Personal, Business, Projects."\n'
        "allowed-tools: Bash(uv run:*), Bash(rg:*), Read, Edit\n"
        "depends_on: []\n"
    ),
    "skills/skill-builder/SKILL.md": (
        "name: skill-builder\n"
        "description: Создаёт новые навыки и суб-агентов по запросу пользователя\n"
        "model: default\nscope: global\ndepends_on: []\n"
        + triggers(["создай навык", "добавь навык", "новый скилл", "создай агента", "новый агент"])
    ),
    "skills/skill-conductor/SKILL.md": (
        "name: skill-conductor\n"
        "description: >\n"
        "  Create, edit, evaluate, and package agent skills. Use when building a new\n"
        "  skill from scratch, improving an existing skill, running evals to test a\n"
        "  skill, benchmarking skill performance, optimizing a skill's description\n"
        "  for better triggering, reviewing third-party skills for quality, or\n"
        "  packaging skills for distribution. Not for using skills or general coding\n"
        "  tasks.\n"
    ),
    "skills/video-processor/SKILL.md": (
        "name: video-processor\n"
        "description: >\n"
        "  Транскрибация и анализ YouTube-видео через yt-dlp + субтитры.\n"
        "  MP4/кружочки — ffmpeg + Deepgram. Используй когда нужно\n"
        "  понять содержание видео, скачать субтитры, проанализировать ролик.\n"
        "model: default\nscope: global\ndepends_on: []\n"
        + triggers(["обработай видео", "скачай субтитры", "посмотри видео", "что в этом ролике", "о чем видео"])
    ),
    "rules/communication-style.md": 'paths: "**/*"\n',
}


def split(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[4:end + 1], text[end + 5:]
    return None, text


def fix(rel, text):
    fm, body = split(text)
    if rel in HEADERS:
        return "---\n" + HEADERS[rel] + "---\n" + body
    if fm is None:
        return text
    lines = [l for l in fm.splitlines() if not JUNK.match(l)]
    agent = re.fullmatch(r"agents/(.+)\.md", rel)
    if agent and agent.group(1) in AGENT_TRIGGERS:
        lines = [l for l in lines if l.strip() != "triggers:"]
        lines += triggers(AGENT_TRIGGERS[agent.group(1)]).splitlines()
    if rel == "skills/web-search/SKILL.md":
        lines = [l for l in lines if l.strip() != "triggers:"]
        lines += triggers(["найди информацию", "поищи в интернете", "что такое"]).splitlines()
    if not any(l.strip() for l in lines):
        return body
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def main():
    root = Path(sys.argv[1])
    apply = "--apply" in sys.argv
    changed = 0
    for path in sorted(root.rglob("*.md")):
        if path.is_symlink() or any((root / p).is_symlink() for p in path.relative_to(root).parents):
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        new = fix(rel, text)
        if new != text:
            changed += 1
            print(("fixed " if apply else "would fix ") + rel)
            if apply:
                path.write_text(new, encoding="utf-8")
    missing = [r for r in HEADERS if not (root / r).exists()]
    print(f"{changed} files; missing targets: {missing}")


if __name__ == "__main__":
    main()
