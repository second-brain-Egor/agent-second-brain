"""Замеры узлов VPN (deploy/vpn-nodes/vpn-nodes): отбор стран, разбор выхода, группы таблицы."""
import importlib.machinery
import importlib.util
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "deploy" / "vpn-nodes" / "vpn-nodes"
NAMES = ["нейросеть", "Telegram", "Google", "YouTube", "Cloudflare"]


@pytest.fixture
def nodes():
    loader = importlib.machinery.SourceFileLoader("vpn_nodes_under_test", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


def record(services, exits=None, error=None, node="🇳🇴 Осло, Норвегия", flag="NO"):
    return dict(run="r", time="t", node=node, flag=flag, services=services,
                exits=exits if exits is not None else [dict(ip="1.1.1.1", cc=flag)] * 3, error=error)


def full(code=200, ms=500):
    return {name: [[code, ms]] * 3 for name in NAMES}


def test_flag_country_and_selection(nodes):
    assert nodes.flag_country("🇳🇴 Осло, Норвегия, Extra") == "NO"
    assert nodes.flag_country("без флага") is None
    assert nodes.title("🇳🇴 Осло, Норвегия, Extra") == "🇳🇴 Осло, Норвегия"
    subscription = [SimpleNamespace(name=name) for name in
                    ("🇳🇴 Осло, Норвегия, Extra", "🇷🇺 Москва, Россия, Extra", "🇭🇰 Гонконг, Гонконг, Extra", "узел 4")]
    chosen, skipped = nodes.select(subscription)
    assert [node.name for node in chosen] == ["🇳🇴 Осло, Норвегия, Extra"]
    assert skipped == ["🇷🇺 Москва, Россия", "🇭🇰 Гонконг, Гонконг", "узел 4"]


def test_exit_prefers_cloudflare_then_ipinfo(nodes):
    trace = (200, b"fl=1\nip=203.0.113.5\nloc=NO\n")
    assert nodes.exit_of(trace, (0, b"")) == dict(ip="203.0.113.5", cc="NO")
    info = (200, b'{"ip": "198.51.100.7", "country": "FI"}')
    assert nodes.exit_of((0, b""), info) == dict(ip="198.51.100.7", cc="FI")
    assert nodes.exit_of((0, b""), (200, b"oops")) == dict(ip=None, cc=None)


def test_verdict_groups(nodes):
    assert nodes.verdict(record(full())) == "all"
    partial = full()
    partial["Telegram"] = [[0, 1400]] * 3
    assert nodes.verdict(record(partial)) == "partial"
    assert nodes.verdict(record(full(code=0), exits=[dict(ip=None, cc=None)] * 3)) == "dead"
    assert nodes.verdict(record({}, exits=[], error="пробный Xray не запустился")) == "dead"
    assert nodes.verdict(record({}, exits=[dict(ip="x", cc="RU")], error="выход из страны RU")) == "foreign"


def test_render_shows_progress_groups_and_mismatch(nodes):
    started = datetime(2026, 10, 9, 18, 10, tzinfo=nodes.TZ)
    oslo = record(full(), exits=[dict(ip="1.1.1.1", cc="NO"), dict(ip="2.2.2.2", cc="NO"), dict(ip="1.1.1.1", cc="NO")])
    stockholm = full()
    stockholm["Telegram"] = [[0, 1400]] * 3
    odd = record(stockholm, node="🇸🇪 Стокгольм, Швеция", flag="SE",
                 exits=[dict(ip="3.3.3.3", cc="DE")] * 3)
    text = nodes.render([odd, oslo], started=started, total=48, skipped=["🇷🇺 Москва, Россия"], names=NAMES)
    assert "проверено 2 из 48" in text
    assert "9 октября 2026" in text
    assert "| 🇳🇴 Осло, Норвегия | 🇳🇴 (2 адреса) | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0,50 |" in text
    assert "| 🇸🇪 Стокгольм, Швеция | ⚠️ 🇩🇪 | 3/3 | 0/3 |" in text
    assert text.index("✅ Прошли всё") < text.index("🟡 С перебоями")
    assert "Москва" in text
    done = nodes.render([oslo], started=started, total=1, skipped=[], names=NAMES,
                        finished=datetime(2026, 10, 9, 18, 31, tzinfo=nodes.TZ))
    assert "Завершён в 18:31, длился 21 мин" in done


def week_record(run, services, node="🇳🇴 Осло, Норвегия", flag="NO", ip="1.1.1.1"):
    return dict(run=run, time=run, node=node, flag=flag, services=services,
                exits=[dict(ip=ip, cc=flag)] * 3, error=None)


def test_week_summary_counts_states_gaps_and_missing(nodes):
    week = dict(start="2026-10-09T19:20", end="2026-10-16T19:20", sent=None)
    runs = ["2026-10-09T19:20", "2026-10-09T21:00", "2026-10-10T00:00", "2026-10-10T03:00"]
    flaky = full()
    flaky["Telegram"] = [[200, 900], [0, 10000], [200, 900]]
    down = full()
    down["нейросеть"] = [[0, 10000]] * 3
    records = [
        week_record("2026-10-09T18:09", full()),  # первый прогон до недели — не считается
        week_record(runs[0], full(ms=400)), week_record(runs[1], flaky),
        week_record(runs[2], down), week_record(runs[3], down, ip="2.2.2.2"),
        week_record(runs[0], full(ms=700), node="🇮🇹 Милан, Италия", flag="IT"),
        week_record(runs[2], full(ms=700), node="🇮🇹 Милан, Италия", flag="IT"),
    ]
    assert nodes.week_runs(records, week) == runs
    summaries = nodes.summarize([r for r in records if r["run"] in runs], runs, NAMES)
    oslo = next(s for s in summaries if s["node"].startswith("🇳🇴"))
    milan = next(s for s in summaries if s["node"].startswith("🇮🇹"))
    assert oslo["services"]["нейросеть"] == dict(ok=2, partial=0, down=2, longest=2, ms=450)
    assert oslo["services"]["Telegram"] == dict(ok=3, partial=1, down=0, longest=0, ms=500)
    assert oslo["ips"] == 2 and oslo["missing"] == 0
    # Узла не было в подписке в двух замерах: это «нет» и перерыв.
    assert milan["missing"] == 2
    assert milan["services"]["нейросеть"]["down"] == 2 and milan["services"]["нейросеть"]["longest"] == 1
    assert nodes.hours(2) == "2 подряд (~6 ч)" and nodes.hours(0) == "не было"

    text = nodes.render_week(summaries, runs, NAMES, week, final=True,
                             at=datetime(2026, 10, 16, 18, 5, tzinfo=nodes.TZ))
    assert "# Итоги недели замеров узлов VPN — 9–16 октября 2026" in text
    assert "✅ Неделя закончилась: 4 замера" in text
    assert "| 🇳🇴 Осло, Норвегия | 2 / 0 / 2 | 3 / 1 / 0 | 2 подряд (~6 ч) | не было | 0,45 | 🇳🇴, адресов: 2 |" in text
    for name in ("## Нейросеть", "## Telegram", "## Google", "## YouTube", "## Cloudflare"):
        assert name in text
    assert "Милан, Италия — 2" in text

    message = nodes.week_message(summaries, runs, NAMES, week, "Итоги недели 9–16 октября 2026.md",
                                 [__import__("re").compile("Осло")])
    assert "4 замера раз в 3 часа, узлов: 2" in message
    assert "🇳🇴 Осло — нейросеть 2/4, Telegram 3/4 (+1 с перебоями), перерыв до ~6 ч" in message
    assert "файл «Итоги недели 9–16 октября 2026»" in message
    assert len(message) < 4096


def test_week_ranking_puts_neural_and_telegram_first(nodes):
    good = dict(node="a", flag="NO", services={n: dict(ok=4 if n in ("нейросеть", "Telegram") else 0,
                                                        partial=0, down=0, longest=0, ms=900) for n in NAMES})
    fast = dict(node="b", flag="NO", services={n: dict(ok=3, partial=0, down=1, longest=1, ms=100) for n in NAMES})
    assert nodes.week_key(good) < nodes.week_key(fast)


def test_measurements_plural(nodes):
    assert [nodes.measurements(n) for n in (1, 3, 11, 21, 57)] == \
        ["1 замер", "3 замера", "11 замеров", "21 замер", "57 замеров"]
