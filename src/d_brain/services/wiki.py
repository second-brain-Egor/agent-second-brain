"""Wiki index and health report generation for the vault."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

IGNORE_DIRS = {
    ".obsidian",
    "attachments",
    ".git",
    ".graph",
    ".claude",
    ".codex",
    ".trash",
    "__pycache__",
}

WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


@dataclass(slots=True)
class NoteInfo:
    path: str
    note_id: str
    title: str
    domain: str
    incoming: int = 0
    outgoing: int = 0

    @property
    def total_links(self) -> int:
        return self.incoming + self.outgoing


def _iter_markdown_files(vault_path: Path) -> list[Path]:
    return sorted(
        md_file
        for md_file in vault_path.rglob("*.md")
        if not any(part in IGNORE_DIRS or part.startswith(".") for part in md_file.relative_to(vault_path).parts)
    )


def _normalize_target(raw_link: str) -> str:
    target = raw_link.split("#", 1)[0].strip().strip("/")
    return target.removesuffix(".md")


def _read_title(md_file: Path) -> str:
    text = md_file.read_text(encoding="utf-8", errors="ignore")
    match = HEADING_RE.search(text)
    if match:
        return match.group(1).strip()
    if md_file.stem.lower() == "readme" and md_file.parent.name:
        return md_file.parent.name
    return md_file.stem


def _build_note_index(vault_path: Path) -> tuple[dict[str, NoteInfo], dict[str, str], dict[str, list[str]]]:
    notes: dict[str, NoteInfo] = {}
    path_index: dict[str, str] = {}
    stem_index: dict[str, list[str]] = defaultdict(list)

    for md_file in _iter_markdown_files(vault_path):
        rel_path = md_file.relative_to(vault_path)
        rel_path_str = rel_path.as_posix()
        note_id = rel_path_str.removesuffix(".md")
        title = _read_title(md_file)
        domain = rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
        notes[rel_path_str] = NoteInfo(
            path=rel_path_str,
            note_id=note_id,
            title=title,
            domain=domain,
        )
        path_index[note_id] = rel_path_str
        stem_index[md_file.stem].append(rel_path_str)

    return notes, path_index, stem_index


def _resolve_target(target: str, path_index: dict[str, str], stem_index: dict[str, list[str]]) -> str | None:
    normalized = _normalize_target(target)
    if not normalized:
        return None
    if normalized in path_index:
        return path_index[normalized]
    leaf = normalized.split("/")[-1]
    matches = stem_index.get(leaf, [])
    if len(matches) == 1:
        return matches[0]
    return None


def analyze_vault(vault_path: Path) -> dict[str, object]:
    notes, path_index, stem_index = _build_note_index(vault_path)
    links_from: dict[str, set[str]] = defaultdict(set)
    links_to: dict[str, set[str]] = defaultdict(set)
    unresolved_links: dict[str, set[str]] = defaultdict(set)

    for md_file in _iter_markdown_files(vault_path):
        source = md_file.relative_to(vault_path).as_posix()
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        for raw_target in WIKI_LINK_RE.findall(text):
            resolved = _resolve_target(raw_target, path_index, stem_index)
            if resolved:
                links_from[source].add(resolved)
                links_to[resolved].add(source)
            else:
                unresolved_links[source].add(_normalize_target(raw_target))

    orphans: list[str] = []
    weakly_connected: list[str] = []
    domain_stats: dict[str, dict[str, float]] = defaultdict(lambda: {"count": 0, "links": 0})

    for path, note in notes.items():
        note.incoming = len(links_to.get(path, set()))
        note.outgoing = len(links_from.get(path, set()))
        if note.incoming == 0 and note.outgoing == 0 and note.domain not in {"MOC", "root"}:
            orphans.append(path)
        elif note.total_links < 2:
            weakly_connected.append(path)

        domain_stats[note.domain]["count"] += 1
        domain_stats[note.domain]["links"] += note.total_links

    for stats in domain_stats.values():
        count = stats["count"]
        stats["avg_links"] = (stats["links"] / count) if count else 0.0

    most_connected = sorted(notes.values(), key=lambda note: note.total_links, reverse=True)[:10]

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "total_notes": len(notes),
        "total_links": sum(len(targets) for targets in links_from.values()),
        "orphan_count": len(orphans),
        "weakly_connected_count": len(weakly_connected),
        "orphans": sorted(orphans),
        "weakly_connected": sorted(weakly_connected),
        "unresolved_links": {path: sorted(targets) for path, targets in unresolved_links.items()},
        "domain_stats": {
            domain: {
                "count": int(stats["count"]),
                "links": int(stats["links"]),
                "avg_links": round(float(stats["avg_links"]), 2),
            }
            for domain, stats in sorted(domain_stats.items())
        },
        "most_connected": [
            {
                "path": note.path,
                "title": note.title,
                "count": note.total_links,
            }
            for note in most_connected
        ],
        "notes": {
            path: {
                "title": note.title,
                "domain": note.domain,
                "incoming": note.incoming,
                "outgoing": note.outgoing,
                "total_links": note.total_links,
            }
            for path, note in sorted(notes.items())
        },
    }


def _link(path: str, title: str) -> str:
    return f"[[{path}|{title}]]"


def _group_paths(paths: list[str]) -> dict[str, list[str]]:
    groups = {
        "memory": [],
        "goals": [],
        "moc": [],
        "projects": [],
        "learnings": [],
        "ideas": [],
        "reflections": [],
        "tasks": [],
        "references": [],
        "summaries": [],
        "daily": [],
        "other": [],
    }
    for path in paths:
        if path.startswith("memory/"):
            groups["memory"].append(path)
        elif path.startswith("goals/"):
            groups["goals"].append(path)
        elif path.startswith("MOC/"):
            groups["moc"].append(path)
        elif path.startswith("projects/"):
            groups["projects"].append(path)
        elif path.startswith("thoughts/learnings/"):
            groups["learnings"].append(path)
        elif path.startswith("thoughts/ideas/"):
            groups["ideas"].append(path)
        elif path.startswith("thoughts/reflections/"):
            groups["reflections"].append(path)
        elif path.startswith("thoughts/tasks/"):
            groups["tasks"].append(path)
        elif path.startswith("references/"):
            groups["references"].append(path)
        elif path.startswith("summaries/"):
            groups["summaries"].append(path)
        elif path.startswith("daily/"):
            groups["daily"].append(path)
        else:
            groups["other"].append(path)
    return groups


def _render_section(lines: list[str], title: str, paths: list[str], notes: dict[str, dict[str, object]], limit: int | None = None) -> None:
    if not paths:
        return
    lines.extend([f"## {title}", ""])
    selected = paths[:limit] if limit else paths
    for path in selected:
        note = notes[path]
        lines.append(f"- {_link(path, str(note['title']))}")
    lines.append("")


def build_index_markdown(stats: dict[str, object]) -> str:
    notes = stats["notes"]  # type: ignore[assignment]
    note_paths = sorted(notes.keys())  # type: ignore[union-attr]
    groups = _group_paths(note_paths)
    recent_daily = sorted(groups["daily"], reverse=True)[:7]
    recent_summaries = sorted(groups["summaries"], reverse=True)[:6]
    updated = datetime.now().date().isoformat()

    lines = [
        "---",
        "type: note",
        f"updated: {updated}",
        "relevance: 0.9",
        "tier: active",
        "---",
        "# Индекс знаний",
        "",
        "Канонический вход в vault: сначала карта разделов и опорные заметки, потом уже точечный поиск.",
        "",
        "## Срез",
        "",
        f"- Заметок: {stats['total_notes']}",
        f"- Связей: {stats['total_links']}",
        f"- Сирот: {stats['orphan_count']}",
        f"- Слабосвязанных: {stats['weakly_connected_count']}",
        "",
    ]

    _render_section(lines, "Память", groups["memory"], notes)
    _render_section(lines, "Горизонты и цели", groups["goals"], notes)
    _render_section(lines, "Карты разделов", groups["moc"], notes)
    _render_section(lines, "Проекты", groups["projects"], notes)
    _render_section(lines, "Новые записи дня", recent_daily, notes)
    _render_section(lines, "Недельные сводки", recent_summaries, notes)
    _render_section(lines, "Обучения и правила", groups["learnings"], notes)
    _render_section(lines, "Справочные материалы", groups["references"], notes)

    return "\n".join(lines).rstrip() + "\n"


def build_health_markdown(stats: dict[str, object]) -> str:
    notes = stats["notes"]  # type: ignore[assignment]
    updated = datetime.now().date().isoformat()
    orphan_paths = stats["orphans"]  # type: ignore[assignment]
    weak_paths = stats["weakly_connected"]  # type: ignore[assignment]
    unresolved = stats["unresolved_links"]  # type: ignore[assignment]

    lines = [
        "---",
        "type: note",
        f"updated: {updated}",
        "relevance: 0.86",
        "tier: warm",
        "---",
        "# Health Check Vault",
        "",
        "Снимок связности и навигации по базе знаний.",
        "",
        "## Обзор",
        "",
        f"- Заметок: {stats['total_notes']}",
        f"- Связей: {stats['total_links']}",
        f"- Сирот: {stats['orphan_count']}",
        f"- Слабосвязанных: {stats['weakly_connected_count']}",
        "",
        "## Домены",
        "",
        "| Домен | Заметок | Среднее число связей |",
        "|---|---:|---:|",
    ]

    for domain, domain_stats in stats["domain_stats"].items():  # type: ignore[union-attr]
        lines.append(
            f"| {domain} | {domain_stats['count']} | {domain_stats['avg_links']:.2f} |"
        )
    lines.append("")

    lines.extend(["## Самые связные заметки", ""])
    for item in stats["most_connected"]:  # type: ignore[union-attr]
        lines.append(f"- {_link(item['path'], item['title'])} — {item['count']} связей")
    lines.append("")

    if orphan_paths:
        lines.extend(["## Сироты", ""])
        for path in orphan_paths[:20]:
            lines.append(f"- {_link(path, str(notes[path]['title']))}")
        if len(orphan_paths) > 20:
            lines.append(f"- ... ещё {len(orphan_paths) - 20}")
        lines.append("")

    if weak_paths:
        lines.extend(["## Слабосвязанные", ""])
        for path in weak_paths[:20]:
            lines.append(f"- {_link(path, str(notes[path]['title']))}")
        if len(weak_paths) > 20:
            lines.append(f"- ... ещё {len(weak_paths) - 20}")
        lines.append("")

    if unresolved:
        lines.extend(["## Неразрешённые ссылки", ""])
        for path, targets in sorted(unresolved.items())[:20]:
            joined = ", ".join(targets[:5])
            suffix = " ..." if len(targets) > 5 else ""
            lines.append(f"- {_link(path, str(notes[path]['title']))}: {joined}{suffix}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def refresh_wiki(vault_path: str | Path) -> dict[str, object]:
    vault = Path(vault_path)
    moc_dir = vault / "MOC"
    reports_dir = vault / "reports"
    data_dir = vault / ".data"
    moc_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    index_path = moc_dir / "index.md"
    health_path = reports_dir / "vault-health.md"
    json_path = data_dir / "vault-health.json"

    initial_stats = analyze_vault(vault)
    index_path.write_text(build_index_markdown(initial_stats), encoding="utf-8")

    final_stats = analyze_vault(vault)
    index_path.write_text(build_index_markdown(final_stats), encoding="utf-8")
    health_path.write_text(build_health_markdown(final_stats), encoding="utf-8")
    json_path.write_text(json.dumps(final_stats, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "index_path": str(index_path),
        "health_path": str(health_path),
        "json_path": str(json_path),
        "stats": final_stats,
    }


def main() -> None:
    from d_brain.config import get_settings

    settings = get_settings()
    result = refresh_wiki(settings.vault_path)
    stats = result["stats"]
    print(
        "Wiki refreshed: "
        f"notes={stats['total_notes']} "
        f"links={stats['total_links']} "
        f"orphans={stats['orphan_count']}"
    )


if __name__ == "__main__":
    main()
