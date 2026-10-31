"""История наблюдаемого наличия рейсов; без сети, часов и файловых операций.

``update_history`` изменяет переданный JSON-совместимый state и возвращает
события одного *полного успешного* снимка даты. При ошибке запроса, частичной
выдаче и отсутствии опроса функцию не вызывают: такие периоды не означают
исчезновение билетов. Первое наблюдение каждой даты является исходным снимком.

Интервалы описывают результаты дискретных проверок: между проверками возможны
необнаруженные изменения. baseline имеет неизвестную левую границу; departed
закрывает наблюдение при вылете и не доказывает исчезновение из продажи.
"""

from __future__ import annotations

import re
from copy import deepcopy
from datetime import UTC, date, datetime
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

CAIRO = ZoneInfo("Africa/Cairo")


def _timestamp(value: str, *, local_departure: bool = False) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        if not local_departure:
            raise ValueError("Время проверки должно содержать часовой пояс.")
        parsed = parsed.replace(tzinfo=CAIRO)
    return parsed


def _seconds(later: str, earlier: str) -> float:
    # Вычитание в UTC сохраняет фактическую длительность при переходе Cairo DST.
    return (_timestamp(later).astimezone(UTC)
            - _timestamp(earlier).astimezone(UTC)).total_seconds()


def _route(offer: dict) -> tuple[str, str]:
    origin, destination = offer.get("origin"), offer.get("destination")
    if not origin or not destination:
        parameters = parse_qs(urlsplit(offer.get("booking_url", "")).query)
        groups = re.findall(r"\(([^()]*)\)", parameters.get("par", [""])[0])
        if groups and "~" not in groups[0]:
            pieces = groups[0].split(".")
            if len(pieces) == 4:
                origin = origin or pieces[2]
                destination = destination or pieces[3]
    # Совместимость со старыми снимками, в которых маршрут задавался поиском.
    return str(origin or "SSH").upper(), str(destination or "MOW").upper()


def flight_id(offer: dict, date_str: str) -> str:
    """Один номер, дата и маршрут; тариф, багаж, цена и время не входят в ключ."""
    number = re.sub(r"[\s-]+", "", str(offer.get("flight", "")).upper())
    if not number:
        raise ValueError("Для истории необходим номер рейса.")
    origin, destination = _route(offer)
    return "|".join((date_str, origin, destination, number))


def _groups(offers: list[dict], date_str: str, checked_at: str) -> dict[str, dict]:
    grouped: dict[str, dict] = {}
    for original in offers:
        if original.get("direct") is False:
            continue
        offer = deepcopy(original)
        departure = _timestamp(
            offer["departure"], local_departure=True,
        ).astimezone(CAIRO)
        if departure.date().isoformat() != date_str:
            raise ValueError("Дата рейса отличается от даты успешного снимка.")
        offer["departure"] = departure.isoformat()
        if _seconds(checked_at, offer["departure"]) >= 0:
            continue
        key = flight_id(offer, date_str)
        previous = grouped.get(key)
        if previous is None or offer.get("price_rub", float("inf")) < previous.get(
            "price_rub", float("inf"),
        ):
            grouped[key] = offer
    return grouped


def _bounds(after: str | None, by: str) -> dict:
    return {"after": after, "by": by}


def _update_duration(interval: dict) -> None:
    observed = _seconds(interval["last_present_at"], interval["first_present_at"])
    interval["observed_duration_seconds"] = observed
    interval["duration_seconds_min"] = observed
    beginning = interval["previous_absent_at"]
    end = interval["first_absent_at"] or interval.get("censored_at")
    interval["duration_seconds_max"] = (
        _seconds(end, beginning) if beginning and end else None
    )


def _open_interval(kind: str, checked_at: str, absent_before: str | None) -> dict:
    interval = {
        "opened_kind": kind,
        "previous_absent_at": absent_before,
        "first_present_at": checked_at,
        "last_present_at": checked_at,
        "first_absent_at": None,
        "start_bounds": _bounds(absent_before, checked_at),
        "end_bounds": None,
        "closed_by": None,
        "censored_at": None,
        "left_censored": absent_before is None,
        "opening_uncertainty_seconds": (
            _seconds(checked_at, absent_before) if absent_before else None
        ),
        "closing_uncertainty_seconds": None,
    }
    _update_duration(interval)
    return interval


def _event(kind: str, record: dict, checked_at: str, bounds: dict) -> dict:
    departure = record["offer"]["departure"]
    lead_hours = _seconds(departure, checked_at) / 3600
    # t_change ∈ (after, by] => lead ∈ [departure-by, departure-after).
    event = {
        "kind": kind,
        "checked_at": checked_at,
        "flight_id": record["id"],
        "date": record["date"],
        "offer": deepcopy(record["offer"]),
        "bounds": bounds,
        "departure_cairo": departure,
        "lead_hours": lead_hours,
        "lead_days": lead_hours / 24,
        "lead_hours_min": _seconds(departure, bounds["by"]) / 3600,
        "lead_hours_max": (
            _seconds(departure, bounds["after"]) / 3600 if bounds["after"] else None
        ),
        "sale_end_proven": kind == "disappeared",
        "interval": deepcopy(record["availability_intervals"][-1]),
    }
    return event


def close_past_observations(state: dict, checked_at: str) -> list[dict]:
    """Закрыть наблюдения ушедших рейсов без фиктивного успешного снимка.

    Завершение по расписанию не является доказательством отсутствия билетов.
    Покрытие дат и время последней успешной проверки остаются прежними.
    """
    checked_at = _timestamp(checked_at).isoformat()
    events = []
    for record in state.get("flights", {}).values():
        departure = record["offer"]["departure"]
        if not record["present"] or _seconds(checked_at, departure) < 0:
            continue
        interval = record["availability_intervals"][-1]
        interval.update(closed_by="departed", censored_at=departure)
        _update_duration(interval)
        record.update(present=False, departed_at=departure)
        events.append(_event(
            "departed", record, checked_at,
            _bounds(interval["last_present_at"], departure),
        ))
    return events


def update_history(
    state: dict, date_str: str, offers: list[dict], checked_at: str,
) -> list[dict]:
    """Добавить успешный снимок даты и вернуть события, сохранив историю в state.

    Состояние хранится в ``flights`` и ``date_coverage`` и переживает обычное
    JSON-сохранение/загрузку без особого восстановления. Возвращаемые виды:
    ``baseline``, ``new``, ``reappeared``, ``disappeared``, ``departed``.
    Последний вид означает только завершение наблюдения при вылете.

    ``checked_at`` содержит часовой пояс. Время вылета приводится к Cairo;
    локальное время вылета без пояса также трактуется как Cairo. Все входные
    данные проверяются до изменения state. Повтор снимка с тем же временем
    безопасен; снимок раньше последнего успешного отклоняется.
    """
    date.fromisoformat(date_str)
    checked_at = _timestamp(checked_at).isoformat()
    grouped = _groups(offers, date_str, checked_at)
    previous_coverage = state.get("date_coverage", {}).get(date_str)
    previous_at = previous_coverage["last_success_at"] if previous_coverage else None
    if previous_at:
        difference = _seconds(checked_at, previous_at)
        if difference < 0:
            raise ValueError("Снимок старше последней успешной проверки этой даты.")
        if difference == 0:
            if set(previous_coverage["current_flight_ids"]) != set(grouped):
                raise ValueError("Разные снимки не могут иметь одно время проверки.")
            return []

    flights = state.setdefault("flights", {})
    coverage = state.setdefault("date_coverage", {})
    events = []
    for key, offer in grouped.items():
        record = flights.get(key)
        if record is None:
            kind = "baseline" if previous_coverage is None else "new"
            origin, destination = _route(offer)
            record = {
                "id": key, "date": date_str, "flight": offer["flight"],
                "origin": origin, "destination": destination,
                "first_seen_at": checked_at, "last_seen_at": checked_at,
                "first_observed_kind": kind,
                "first_seen_lead_hours": (
                    _seconds(offer["departure"], checked_at) / 3600
                ),
                "availability_intervals": [],
            }
            flights[key] = record
        else:
            kind = "reappeared" if not record["present"] else None
        record.update(offer=offer, departure_cairo=offer["departure"],
                      present=True, last_seen_at=checked_at, last_checked_at=checked_at)
        if kind:
            interval = _open_interval(kind, checked_at, previous_at)
            record["availability_intervals"].append(interval)
            events.append(_event(kind, record, checked_at, interval["start_bounds"]))
        else:
            interval = record["availability_intervals"][-1]
            interval["last_present_at"] = checked_at
            _update_duration(interval)

    for key, record in flights.items():
        if record["date"] != date_str or key in grouped:
            continue
        record["last_checked_at"] = checked_at
        if not record["present"]:
            continue
        interval = record["availability_intervals"][-1]
        departure = record["offer"]["departure"]
        if _seconds(checked_at, departure) >= 0:
            kind = "departed"
            interval["censored_at"] = departure
            bounds = _bounds(interval["last_present_at"], departure)
            record["departed_at"] = departure
        else:
            kind = "disappeared"
            interval["first_absent_at"] = checked_at
            bounds = _bounds(interval["last_present_at"], checked_at)
            interval["end_bounds"] = bounds
            interval["closing_uncertainty_seconds"] = _seconds(
                checked_at, interval["last_present_at"],
            )
        interval["closed_by"] = kind
        _update_duration(interval)
        record["present"] = False
        events.append(_event(kind, record, checked_at, bounds))

    coverage[date_str] = {
        "baseline_at": (previous_coverage or {}).get("baseline_at", checked_at),
        "last_success_at": checked_at,
        "successful_checks": (previous_coverage or {}).get("successful_checks", 0) + 1,
        "current_flight_ids": sorted(grouped),
    }
    return events
