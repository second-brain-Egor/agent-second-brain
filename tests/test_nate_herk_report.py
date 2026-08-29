import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "nate_herk_report.py"
SPEC = importlib.util.spec_from_file_location("nate_herk_report", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
extract = MODULE.extract


def test_canonical_sections():
    values, missing = extract("""# Карточка ролика: Тест
## Тема
Автоматизация отчётов.
## Краткое содержание
Показан надёжный генератор.
## Основной вывод
Формат нужно проверять.
""")
    assert not missing
    assert values["theme"] == "Автоматизация отчётов."
    assert values["conclusion"] == "Формат нужно проверять."


def test_legacy_brief_is_compatible():
    values, missing = extract("""# Карточка ролика: Старый формат
## Кратко
Автор показывает планировщик встреч. Главный вывод ролика: AI ускоряет разработку.
## Основные идеи и тезисы
- Первая идея.
""")
    assert not missing
    assert values["theme"] == "Автор показывает планировщик встреч."
    assert values["conclusion"] == "Главный вывод ролика: AI ускоряет разработку."


def test_missing_conclusion_is_rejected():
    _, missing = extract("""# Карточка ролика: Неполная
## Тема
Тема.
## Краткое содержание
Только описание.
""")
    assert missing == ["conclusion"]
