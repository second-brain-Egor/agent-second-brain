"""Скользящий охват дат и независимость успешных снимков; без сети и отправок."""

import json
from datetime import datetime, timezone
from unittest.mock import Mock, call
from urllib.parse import parse_qs, urlsplit

import pytest

from scripts import avia_monitor as monitor


def offer(day: str, *, identity: str = "SU0431", price: int = 60000) -> dict:
    flight_id = f"SSH|SVO|{identity}|{day}"
    return {
        "id": f"fare:{flight_id}", "flight_id": flight_id,
        "flight": identity, "carrier": "Аэрофлот", "origin": "SSH",
        "destination": "SVO", "departure": f"{day}T12:00+02:00",
        "arrival": f"{day}T19:00+03:00", "price_rub": price,
        "baggage": "Без багажа", "booking_url": "https://www.bgoperator.ru/",
        "direct": True,
    }


def result(day: str, offers: list[dict]) -> dict:
    return {
        "source": "biblio_globus", "exclusive": False,
        "query": {"origin": "SSH", "destination": "MOW", "date": day,
                  "verified_route": True, "verified_date": True},
        "completed": True, "offers": offers,
    }


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(monitor, "PROJECT", tmp_path)
    monkeypatch.setattr(monitor, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(monitor, "HISTORY_PATH", tmp_path / "history.jsonl")
    monkeypatch.setattr(monitor, "SESSION_PATH", tmp_path / "session.jsonl")
    monkeypatch.setattr(monitor, "monitoring_dates", lambda *a: [])
    monkeypatch.setattr(monitor, "notify", Mock(side_effect=AssertionError("Отправка не ожидалась")))
    state = monitor.load_state()
    return state, monitor.StopReader(state, path=monitor.SESSION_PATH)


@pytest.mark.parametrize("at,first,last", [
    (datetime(2026, 10, 29, 22, 30, tzinfo=timezone.utc), "2026-10-30", "2026-11-19"),
    (datetime(2026, 11, 20, 22, 30, tzinfo=timezone.utc), "2026-11-21", "2026-12-11"),
])
def test_window_uses_cairo_local_day_and_includes_exactly_21_dates(at, first, last):
    days = monitor.monitoring_dates(at)
    assert len(days) == len(set(days)) == 21
    assert days[0] == first
    assert days[-1] == last


def test_search_url_encodes_the_requested_date_instead_of_legacy_november_21():
    query = parse_qs(urlsplit(monitor.search_url(date_str="2026-10-30")).query)
    assert query["params"] == ["030102026_SSH_MOW"]
    assert query["ac"] == ["1"]
    assert "un" not in query
    exclusive = parse_qs(urlsplit(monitor.search_url(True, date_str="2026-11-02")).query)
    assert exclusive["params"] == ["002112026_SSH_MOW"]
    assert exclusive["un"] == ["1"]


def test_new_state_has_no_single_date_baseline(isolated):
    state, _ = isolated
    assert state["schema"] == 2
    assert state["rolling_window_days"] == 21
    assert state["offers"] == {}
    assert state["date_results"] == {}
    assert state["date_coverage"] == {}
    assert state["booking_enabled"] is False


def test_legacy_offers_are_archived_without_becoming_a_window_baseline(isolated):
    legacy = {
        "schema": 1, "date": "2026-11-21", "status": "suspended",
        "offers": {"old": offer("2026-11-21")},
        "baseline_at": "2026-10-30T10:00:00+03:00", "pending": [],
    }
    monitor.STATE_PATH.write_text(json.dumps(legacy), encoding="utf-8")
    state = monitor.load_state()
    assert state["schema"] == 2
    assert state["legacy_single_date"] == legacy
    assert state["offers"] == {}
    assert state["date_results"] == {}
    assert state["date_coverage"] == {}
    assert not state.get("baseline_at")
    assert state["pending"] == []


@pytest.mark.parametrize("status", ["stopped", "access_denied", "parse_error"])
def test_legacy_terminal_stop_survives_window_migration(isolated, status):
    monitor.STATE_PATH.write_text(json.dumps({
        "schema": 1, "date": "2026-11-21", "status": status, "pending": [],
    }), encoding="utf-8")
    assert monitor.load_state()["status"] == status


def test_cycle_checks_each_date_once_using_general_search_and_no_booking(isolated, monkeypatch):
    state, stop = isolated
    days = ["2026-10-30", "2026-10-31", "2026-11-01"]
    monkeypatch.setattr(monitor, "monitoring_dates", lambda *a: days)
    reader = Mock(side_effect=[result(day, [offer(day)]) for day in days])
    monkeypatch.setattr(monitor, "fetch_search", reader)
    monitor.cycle(state, stop, baseline=True)
    assert reader.call_args_list == [call(False, stop, date_str=day) for day in days]
    assert set(state["date_results"]) == set(days)
    assert set(state["date_coverage"]) == set(days)
    assert len(state["offers"]) == 3
    assert state["pending"] == []
    assert state["booking_enabled"] is False
    saved = json.loads(monitor.STATE_PATH.read_text(encoding="utf-8"))
    assert set(saved["date_results"]) == set(days)


def test_connection_failure_keeps_its_last_good_snapshot_and_continues_other_dates(
    isolated, monkeypatch,
):
    state, stop = isolated
    days = ["2026-10-30", "2026-10-31"]
    first, second = [offer(day) for day in days]
    monkeypatch.setattr(monitor, "monitoring_dates", lambda *a: days)
    monkeypatch.setattr(monitor, "fetch_search", Mock(side_effect=[
        result(days[0], [first]), result(days[1], [second]),
    ]))
    monitor.cycle(state, stop, baseline=True)
    retained_coverage = json.loads(json.dumps(state["date_coverage"][days[0]]))
    reader = Mock(side_effect=[RuntimeError("Временный сбой соединения"), result(days[1], [])])
    monkeypatch.setattr(monitor, "fetch_search", reader)
    monitor.cycle(state, stop)
    assert reader.call_args_list == [call(False, stop, date_str=day) for day in days]
    assert first["id"] in state["offers"]
    assert second["id"] not in state["offers"]
    assert state["date_coverage"][days[0]] == retained_coverage
    saved = json.loads(monitor.STATE_PATH.read_text(encoding="utf-8"))
    assert first["id"] in saved["offers"]
    assert second["id"] not in saved["offers"]


@pytest.mark.parametrize("error_type", [monitor.AccessDenied, ValueError])
def test_refusal_or_unverifiable_response_stops_before_any_other_date(
    isolated, monkeypatch, error_type,
):
    state, stop = isolated
    days = ["2026-10-30", "2026-10-31", "2026-11-01"]
    monkeypatch.setattr(monitor, "monitoring_dates", lambda *a: days)
    reader = Mock(side_effect=error_type("Ответ нельзя использовать"))
    monkeypatch.setattr(monitor, "fetch_search", reader)
    with pytest.raises(error_type):
        monitor.cycle(state, stop)
    reader.assert_called_once_with(False, stop, date_str=days[0])
    assert not state["offers"]
    assert not state["date_coverage"]


def test_entering_far_date_gets_its_own_baseline_without_false_new_flight_notice(
    isolated, monkeypatch,
):
    state, stop = isolated
    first_day, added_day = "2026-10-30", "2026-11-20"
    monkeypatch.setattr(monitor, "monitoring_dates", lambda *a: [first_day])
    monkeypatch.setattr(monitor, "fetch_search", Mock(return_value=result(first_day, [])))
    monitor.cycle(state, stop, baseline=True)
    monkeypatch.setattr(monitor, "monitoring_dates", lambda *a: [first_day, added_day])
    monkeypatch.setattr(monitor, "fetch_search", Mock(side_effect=[
        result(first_day, []), result(added_day, [offer(added_day)]),
    ]))
    monitor.cycle(state, stop)
    assert added_day in state["date_results"]
    assert added_day in state["date_coverage"]
    assert state["pending"] == []
