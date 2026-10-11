#!/usr/bin/env python3
"""Прогон проверки поведения бота на типовых сообщениях (tests/behavior/cases.toml).

    uv run python scripts/behavior_check.py               # весь набор
    uv run python scripts/behavior_check.py math thanks   # только выбранные
    uv run python scripts/behavior_check.py --list

Тратит лимит текущей модели: по одному запросу на сообщение. Запускать вручную,
не по расписанию.
"""
from __future__ import annotations

import argparse
import re
import sys

from d_brain.config import get_settings
from d_brain.services import behavior_check
from d_brain.services.processor import AgentProcessor


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ids", nargs="*", help="id проверок; без них — весь набор")
    parser.add_argument("--list", action="store_true", help="показать набор и выйти")
    args = parser.parse_args()
    cases, _ = behavior_check.load_cases()
    if args.list:
        for case in cases:
            print(f"{case['id']:18} {case.get('title', '')}")
        return 0
    unknown = set(args.ids) - {case["id"] for case in cases}
    if unknown:
        print("Нет таких проверок: " + ", ".join(sorted(unknown)), file=sys.stderr)
        return 2
    settings = get_settings()
    summary = behavior_check.run_all(AgentProcessor(settings.vault_path, settings.todoist_api_key),
                                     args.ids or None)
    print(re.sub(r"</?[bi]>", "", behavior_check.telegram_report(summary)))
    print(f"\nОтветы целиком: {summary['path']}")
    return 0 if all(item["ok"] for item in summary["results"]) else 1


if __name__ == "__main__":
    sys.exit(main())
