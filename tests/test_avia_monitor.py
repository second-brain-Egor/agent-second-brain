"""События мониторинга и независимая остановка; без настоящей сети."""

import json
from unittest.mock import Mock

import pytest

from scripts import avia_monitor as monitor


def offer(*, price=60000, exclusive=False, identity="flight-1"):
    return {
        "id": identity, "flight": "SU0431" if identity == "flight-1" else "SU0433", "carrier": "Аэрофлот",
        "departure": "2026-11-21T22:35+02:00",
        "arrival": "2026-11-22T05:40+03:00", "price_rub": price,
        "baggage": "Без багажа", "booking_url": "https://www.bgoperator.ru/",
        "direct": True, "exclusive": exclusive,
    }


def result(offers, *, exclusive=False):
    return {"offers": offers, "exclusive": exclusive, "completed": True}


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(monitor, "PROJECT", tmp_path)
    monkeypatch.setattr(monitor, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(monitor, "HISTORY_PATH", tmp_path / "history.jsonl")
    monkeypatch.setattr(monitor, "SESSION_PATH", tmp_path / "session.jsonl")
    monkeypatch.setattr(monitor.signal, "signal", lambda *args: None)
    monkeypatch.setattr(monitor, "monitoring_dates", lambda *args: ["2026-11-21"])
    state = monitor.load_state()
    return state, monitor.StopReader(state, path=monitor.SESSION_PATH)


def test_merge_deduplicates_tariff_and_keeps_exclusive_with_lower_observed_price():
    merged = monitor.merge_offers([
        result([offer(price=65000)], exclusive=True), result([offer(price=60000)]),
    ])
    assert len(merged) == 1
    assert merged["flight-1"]["price_rub"] == 60000
    assert merged["flight-1"]["exclusive"] is True


def test_existing_flights_do_not_alert_on_price_increase_but_drop_and_new_do():
    old = {"flight-1": offer()}
    assert monitor.offer_events(old, {"flight-1": offer(price=61000)}) == []
    dropped = monitor.offer_events(old, {"flight-1": offer(price=59000)})
    assert dropped[0]["kind"] == "price_drop"
    assert dropped[0]["old_price_rub"] == 60000
    assert monitor.offer_events({}, old)[0]["kind"] == "new"
    assert monitor.offer_events(old, {"flight-1": offer(exclusive=True)})[0]["kind"] == "exclusive"


def test_baseline_is_read_only_and_next_new_offer_is_queued_once(isolated, monkeypatch):
    state, stop = isolated
    reads = iter([
        result([offer()]),
        result([offer(), offer(identity="flight-2")]),
        result([offer(), offer(identity="flight-2")]),
    ])
    monkeypatch.setattr(monitor, "fetch_search", lambda *args, **kwargs: next(reads))
    sender = Mock()
    monkeypatch.setattr(monitor, "notify", sender)
    monitor.cycle(state, stop, baseline=True)
    assert state["booking_enabled"] is False
    assert state["passenger_count_confirmed"] is False
    assert state["pending"] == []
    monitor.cycle(state, stop)
    assert len(state["pending"]) == 1
    assert "Бронирование отключено" in state["pending"][0]["text"]
    assert state["pending"][0]["url"] == monitor.search_url(False)
    monitor.cycle(state, stop)
    assert len(state["pending"]) == 1
    sender.assert_not_called()


def test_access_refusal_does_not_try_other_search_or_overwrite_last_good_data(isolated, monkeypatch):
    state, stop = isolated
    state["offers"] = {"flight-1": offer()}
    reader = Mock(side_effect=monitor.AccessDenied("Отказ"))
    monkeypatch.setattr(monitor, "fetch_search", reader)
    with pytest.raises(monitor.AccessDenied):
        monitor.cycle(state, stop)
    reader.assert_called_once_with(False, stop, date_str="2026-11-21")
    assert state["offers"] == {"flight-1": offer()}


def test_stop_reads_only_new_user_messages_and_handles_partial_writes(tmp_path):
    path = tmp_path / "session.jsonl"
    path.write_text(json.dumps({"type": "text", "text": "стоп"}) + "\n")
    state = {"session_offset": path.stat().st_size}
    reader = monitor.StopReader(state, path)
    with path.open("a") as stream:
        stream.write(json.dumps({"type": "assistant", "text": "стоп"}) + "\n")
        stream.write(json.dumps({"type": "voice", "text": "стоп"}))
    reader.check()
    assert not reader.user_stop
    with path.open("a") as stream:
        stream.write("\n")
    with pytest.raises(monitor.Stopped):
        reader.check()
    assert reader.user_stop


def test_unknown_delivery_is_terminal_and_pending_is_preserved(isolated, monkeypatch):
    state, stop = isolated
    monitor.queue_notice(state, "Появился билет", "new")
    sender = Mock(side_effect=RuntimeError("Результат неизвестен"))
    monkeypatch.setattr(monitor, "notify", sender)
    with pytest.raises(RuntimeError):
        monitor.deliver_pending(state, stop)
    assert state["status"] == "delivery_error"
    assert len(state["pending"]) == 1
    assert json.loads(monitor.STATE_PATH.read_text())["status"] == "delivery_error"


def test_pending_failure_notice_survives_restart_without_new_site_requests(isolated, monkeypatch):
    state, stop = isolated
    state["status"] = "access_denied"
    monitor.queue_notice(state, "Сайт отказал", "access_denied")
    monitor.save(monitor.STATE_PATH, state)
    sender = Mock(return_value={"message_id": 77})
    reader = Mock(side_effect=AssertionError("Нельзя снова опрашивать сайт"))
    monkeypatch.setattr(monitor, "notify", sender)
    monkeypatch.setattr(monitor, "fetch_search", reader)
    assert monitor.run() == 0
    sender.assert_called_once()
    reader.assert_not_called()
    assert not json.loads(monitor.STATE_PATH.read_text())["pending"]


def test_user_stop_is_not_resumed_on_next_start(isolated, monkeypatch):
    state, stop = isolated
    state["status"] = "stopped"
    monitor.save(monitor.STATE_PATH, state)
    reader = Mock()
    monkeypatch.setattr(monitor, "fetch_search", reader)
    assert monitor.run() == 0
    reader.assert_not_called()
