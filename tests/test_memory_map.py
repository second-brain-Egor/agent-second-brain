"""Память в запросе: карта главного целиком, свежие дописки; поиск видит facts.md, а не ролики."""
from pathlib import Path

from d_brain.services.memory_rag import _extract_facts, _iter_markdown_files
from d_brain.services.processor import AgentProcessor

ROOT = Path(__file__).resolve().parent.parent


def test_sections_right_under_heading_are_indexed_with_heading():
    facts = _extract_facts("---\ntype: note\n---\n# Факты\n\n## 2026-04-09 — Сбой WireGuard\n"
                           "- После скрипта пропал интернет на Windows\n- Ethernet получил адрес от роутера\n")
    assert facts == ["2026-04-09 — Сбой WireGuard: - После скрипта пропал интернет на Windows",
                     "2026-04-09 — Сбой WireGuard: - Ethernet получил адрес от роутера"]


def test_comment_in_code_block_is_not_a_heading():
    facts = _extract_facts("## Команды\n\n```bash\n# установка пакета\nuv sync --all-extras\n```\n")
    assert facts and all(fact.startswith("Команды: ") for fact in facts)


def test_video_materials_are_not_indexed(tmp_path):
    video = tmp_path / "projects" / "Канал" / "videos" / "001-ролик"
    video.mkdir(parents=True)
    (video / "comments.md").write_text("комментарии зрителей")
    (tmp_path / "projects" / "Канал" / "summary.md").write_text("сводка по каналу")
    assert _iter_markdown_files(tmp_path) == [tmp_path / "projects" / "Канал" / "summary.md"]


def test_memory_map_goes_whole_with_newest_sections(tmp_path):
    path = tmp_path / "soul.md"
    path.write_text("---\ntype: note\n---\n# Агент\n\n<!-- карта -->\n## Главное\n"
                    + "- правило карты\n" * 200 + "<!-- /карта -->\n\n## Старое\n- давний урок\n\n"
                    "## Уточнения 10 октября\n- свежий урок\n")
    context = AgentProcessor._memory_file_context(path)
    assert context.count("- правило карты") == 200  # больше прежних 2000 знаков, но целиком
    assert "свежий урок" in context and "давний урок" in context
    assert "<!--" not in context and "type: note" not in context


def test_old_tail_is_cut_to_the_newest(tmp_path, monkeypatch):
    import d_brain.services.processor as module
    monkeypatch.setattr(module, "_MEMORY_RECENT_LIMIT", 60)
    path = tmp_path / "user.md"
    path.write_text("<!-- карта -->\nкарта\n<!-- /карта -->\n## Старое\n" + "- давнее\n" * 30
                    + "## Новое\n- свежее предпочтение\n")
    context = AgentProcessor._memory_file_context(path)
    assert "свежее предпочтение" in context and "давнее" not in context


def test_file_without_map_keeps_old_behavior(tmp_path):
    path = tmp_path / "user.md"
    path.write_text("# Профиль\n" + "я" * 5000)
    assert len(AgentProcessor._memory_file_context(path)) == 2000


def test_real_maps_fit_the_limit():
    from d_brain.services.processor import _MEMORY_MAP_END, _MEMORY_MAP_LIMIT, _MEMORY_MAP_START
    for name in ("user.md", "soul.md"):
        text = (ROOT / "vault" / "memory" / name).read_text(encoding="utf-8")
        start, end = text.find(_MEMORY_MAP_START), text.find(_MEMORY_MAP_END)
        assert 0 <= start < end, f"{name}: нет карты"
        assert end - start < _MEMORY_MAP_LIMIT, f"{name}: карта не помещается в запрос"
    user = (ROOT / "vault" / "memory" / "user.md").read_text(encoding="utf-8")
    assert AgentProcessor._extract_markdown_section(user, "Работа")  # нужен рабочим группам
