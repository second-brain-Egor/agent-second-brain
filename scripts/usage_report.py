#!/usr/bin/env python3
"""Сводка расхода по моделям и уровням мышления из vault/.data/usage.jsonl.

    uv run python scripts/usage_report.py            # последние 7 дней
    uv run python scripts/usage_report.py --days 30
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "vault" / ".data" / "usage.jsonl"


def load(path: Path, since: datetime) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            if datetime.fromisoformat(row["time"]) >= since:
                rows.append(row)
        except (ValueError, KeyError, TypeError):
            continue
    return rows


def report(rows: list[dict], days: int) -> str:
    if not rows:
        return f"За {days} дн. записей о расходе нет."
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row.get("model") or "?", row.get("effort") or "?")].append(row)
    lines = [f"Расход за {days} дн.: {len(rows)} запросов", ""]
    for (model, effort), items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        def median(key: str) -> float:
            values = [item.get(key) or 0 for item in items]
            return statistics.median(values) if values else 0
        cost = [item["cost_usd"] for item in items if item.get("cost_usd") is not None]
        failed = sum(1 for item in items if not item.get("ok", True))
        lines.append(f"{model}, мышление {effort}: {len(items)} запросов")
        lines.append(f"  медиана: {median('seconds'):.0f} с, шагов {median('steps'):.0f}, "
                     f"вывод {median('output'):,.0f} токенов, из них мышление {median('thinking'):,.0f}"
                     .replace(",", " "))
        if cost:
            lines.append(f"  цена по прайсу API: медиана ${statistics.median(cost):.2f}, всего ${sum(cost):.2f}")
        if failed:
            lines.append(f"  с ошибкой: {failed}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--log", type=Path, default=LOG)
    args = parser.parse_args()
    since = datetime.now().astimezone() - timedelta(days=args.days)
    print(report(load(args.log, since), args.days))


if __name__ == "__main__":
    main()
