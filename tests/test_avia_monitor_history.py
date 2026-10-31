"""Смысл истории: начало продаж, интервалы и честные границы наблюдения."""

import json
from copy import deepcopy

import pytest

from scripts.avia_monitor_history import (
    close_past_observations,
    flight_id,
    update_history,
)

DATE = "2026-11-02"


def offer(**changes):
    value = {
        "id": "tariff-1", "flight": "SU0431", "carrier": "Аэрофлот",
        "origin": "SSH", "destination": "SVO", "direct": True,
        "departure": "2026-11-02T12:00+02:00",
        "arrival": "2026-11-02T17:00+03:00", "price_rub": 60000,
        "baggage": "Без багажа", "booking_url": "https://www.bgoperator.ru/",
    }
    value.update(changes)
    return value


def at(hour, minute=0, *, day=30):
    return f"2026-10-{day:02d}T{hour:02d}:{minute:02d}:00+03:00"


def test_each_dates_first_success_is_baseline_even_after_other_dates_are_seen():
    state = {}
    events = update_history(state, DATE, [offer()], at(9))
    assert [event["kind"] for event in events] == ["baseline"]
    assert events[0]["bounds"] == {"after": None, "by": at(9)}
    assert events[0]["lead_hours_max"] is None
    assert events[0]["lead_hours"] == 76
    tomorrow = "2026-11-03"
    future = offer(departure="2026-11-03T12:00+02:00")
    assert update_history(state, tomorrow, [future], at(9, 5))[0]["kind"] == "baseline"
    assert len(state["flights"]) == 2


def test_empty_baseline_then_new_then_absence_retains_polling_bounds():
    state = {}
    assert update_history(state, DATE, [], at(9)) == []
    event = update_history(state, DATE, [offer()], at(9, 5))[0]
    assert event["kind"] == "new"
    assert event["bounds"] == {"after": at(9), "by": at(9, 5)}
    assert event["lead_hours_min"] == pytest.approx(76 - 5 / 60)
    assert event["lead_hours_max"] == 76
    assert update_history(state, DATE, [offer()], at(9, 25)) == []
    event = update_history(state, DATE, [], at(9, 40))[0]
    assert event["kind"] == "disappeared"
    assert event["bounds"] == {"after": at(9, 25), "by": at(9, 40)}
    interval = event["interval"]
    assert interval["duration_seconds_min"] == 20 * 60
    assert interval["duration_seconds_max"] == 40 * 60
    assert interval["opening_uncertainty_seconds"] == 5 * 60
    assert interval["closing_uncertainty_seconds"] == 15 * 60
    assert event["sale_end_proven"] is True


def test_reappearance_survives_json_restart_and_does_not_reset_initial_evidence():
    state = {}
    update_history(state, DATE, [], at(9))
    update_history(state, DATE, [offer()], at(9, 5))
    update_history(state, DATE, [], at(9, 10))
    state = json.loads(json.dumps(state))
    event = update_history(state, DATE, [offer()], at(9, 15))[0]
    assert event["kind"] == "reappeared"
    assert event["bounds"] == {"after": at(9, 10), "by": at(9, 15)}
    record = state["flights"][event["flight_id"]]
    assert record["first_seen_at"] == at(9, 5)
    assert record["first_observed_kind"] == "new"
    assert len(record["availability_intervals"]) == 2
    assert record["availability_intervals"][0]["first_absent_at"] == at(9, 10)


def test_fare_baggage_price_and_schedule_changes_do_not_create_new_flight():
    state = {}
    update_history(state, DATE, [offer()], at(9))
    changed = offer(id="another-tariff", baggage="20 кг", price_rub=50000,
                    departure="2026-11-02T13:00+02:00", flight="SU 0431")
    assert update_history(
        state, DATE, [changed, offer(price_rub=80000)], at(9, 5),
    ) == []
    assert len(state["flights"]) == 1
    record = next(iter(state["flights"].values()))
    assert record["offer"]["price_rub"] == 50000
    assert record["departure_cairo"] == "2026-11-02T13:00:00+02:00"
    assert len(record["availability_intervals"]) == 1


def test_same_number_different_route_is_a_different_flight():
    state = {}
    update_history(state, DATE, [offer()], at(9))
    events = update_history(state, DATE, [offer(), offer(destination="VKO")], at(9, 5))
    assert len(events) == 1
    assert events[0]["kind"] == "new"
    assert len(state["flights"]) == 2


def test_legacy_offer_route_can_be_read_from_order_link():
    value = offer(booking_url=(
        "https://www.bgoperator.ru/price.shtml?action=biletnewsorder&par="
        "(ORSU0431.26110212002611021700.SSH.VKO)(x)(fare)"
    ))
    del value["origin"], value["destination"]
    assert flight_id(value, DATE) == f"{DATE}|SSH|VKO|SU0431"


def test_other_dates_and_unpolled_periods_are_not_absence_evidence():
    state = {}
    update_history(state, DATE, [offer()], at(9))
    original = deepcopy(state["flights"])
    # Неуспешный запрос не передают в update_history. Другую дату можно опросить.
    assert update_history(state, "2026-11-03", [], at(9, 5)) == []
    assert state["flights"] == original
    # После пропуска остаётся широкий, но честный интервал обнаружения.
    event = update_history(state, DATE, [], at(12))[0]
    assert event["bounds"] == {"after": at(9), "by": at(12)}
    assert event["interval"]["closing_uncertainty_seconds"] == 3 * 3600


def test_invalid_or_out_of_order_snapshot_does_not_mutate_state():
    state = {}
    update_history(state, DATE, [offer()], at(9))
    before = deepcopy(state)
    with pytest.raises(ValueError, match="Дата рейса"):
        update_history(
            state, DATE, [offer(), offer(departure="2026-11-03T12:00+02:00")], at(10),
        )
    assert state == before
    with pytest.raises(ValueError, match="старше"):
        update_history(state, DATE, [], at(8))
    assert state == before
    with pytest.raises(ValueError, match="часовой пояс"):
        update_history(state, DATE, [], "2026-10-30T10:00")
    assert state == before


def test_replaying_successful_snapshot_is_idempotent():
    state = {}
    update_history(state, DATE, [offer()], at(9))
    before = deepcopy(state)
    assert update_history(state, DATE, [offer()], at(9)) == []
    assert state == before
    with pytest.raises(ValueError, match="одно время"):
        update_history(state, DATE, [], at(9))
    assert state == before


def test_baseline_duration_remains_left_censored():
    state = {}
    update_history(state, DATE, [offer()], at(9))
    update_history(state, DATE, [offer()], at(10))
    event = update_history(state, DATE, [], at(11))[0]
    assert event["interval"]["duration_seconds_min"] == 3600
    assert event["interval"]["duration_seconds_max"] is None
    assert event["interval"]["left_censored"] is True


def test_already_departed_offers_are_ignored_even_in_initial_snapshot():
    state = {}
    past = offer(departure="2026-10-30T07:00+02:00")
    assert update_history(state, "2026-10-30", [past], at(10)) == []
    assert state["flights"] == {}


def test_after_departure_closes_observation_without_proven_disappearance():
    state = {}
    today = "2026-10-30"
    value = offer(departure="2026-10-30T12:00+02:00")
    update_history(state, today, [], at(9))
    update_history(state, today, [value], at(10))
    update_history(state, today, [value], at(12))
    # Вылет 12:00 Cairo = 13:00 Москва; запрос уже после вылета.
    event = update_history(state, today, [], at(14))[0]
    assert event["kind"] == "departed"
    assert event["sale_end_proven"] is False
    assert event["interval"]["first_absent_at"] is None
    assert event["interval"]["end_bounds"] is None
    assert event["interval"]["censored_at"] == "2026-10-30T12:00:00+02:00"
    assert event["bounds"]["by"] == "2026-10-30T12:00:00+02:00"
    assert update_history(state, today, [], at(15)) == []


def test_cairo_timezone_and_daylight_saving_are_actual_elapsed_hours():
    state = {}
    value = offer(departure="2026-10-30T01:00")
    events = update_history(state, "2026-10-30", [value], "2026-10-29T23:00+03:00")
    assert events[0]["departure_cairo"] == "2026-10-30T01:00:00+02:00"
    assert events[0]["lead_hours"] == 3


def test_returned_events_do_not_change_when_state_is_updated_later():
    state = {}
    event = update_history(state, DATE, [offer()], at(9))[0]
    before = deepcopy(event)
    update_history(state, DATE, [offer(price_rub=40000)], at(10))
    update_history(state, DATE, [], at(11))
    assert event == before


def test_close_past_observation_does_not_invent_a_successful_date_snapshot():
    state = {}
    today = "2026-10-30"
    value = offer(departure="2026-10-30T12:00+02:00")
    update_history(state, today, [value], at(10))
    coverage = deepcopy(state["date_coverage"])
    events = close_past_observations(state, "2026-10-31T09:00:00+03:00")
    assert len(events) == 1
    event = events[0]
    assert event["kind"] == "departed"
    assert event["sale_end_proven"] is False
    assert event["interval"]["first_absent_at"] is None
    assert event["interval"]["censored_at"] == "2026-10-30T12:00:00+02:00"
    record = state["flights"][event["flight_id"]]
    assert record["present"] is False
    assert record["last_checked_at"] == at(10)
    assert state["date_coverage"] == coverage


def test_close_past_observations_preserves_future_and_previously_closed_records():
    state = {}
    today = "2026-10-30"
    update_history(state, today, [offer(departure="2026-10-30T12:00+02:00")], at(10))
    update_history(state, DATE, [offer()], at(10))
    close_past_observations(state, at(14))
    before = deepcopy(state)
    assert close_past_observations(state, at(15)) == []
    assert state == before
    future = state["flights"][flight_id(offer(), DATE)]
    assert future["present"] is True
    assert future["availability_intervals"][-1]["closed_by"] is None
