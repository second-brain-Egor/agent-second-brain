#!/usr/bin/env python3
"""Проверка опубликованных предложений SSH → Москва, без оформления заказов."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from avia_monitor_bg import parse_search_html  # noqa: E402
from avia_monitor_history import close_past_observations, update_history  # noqa: E402
from avia_monitor_notify import notify  # noqa: E402
from d_brain.bot.request_jobs import STOP  # noqa: E402

PROJECT = ROOT / "vault/projects/Авиаперелет"
STATE_PATH = PROJECT / "Состояние мониторинга.json"
HISTORY_PATH = PROJECT / "История мониторинга.jsonl"
SESSION_PATH = ROOT / "vault/.sessions/6144231826.jsonl"
CAIRO = ZoneInfo("Africa/Cairo")
WINDOW_DAYS = 21
INTERVAL = 300
BASE_PARAMS = {
    "action": "biletnew", "ac": "1", "chc": "0", "infc": "0",
    "search": "true",
}
ACCESS_DENIED = re.compile(
    r"HTTP 4(?!08)\d\d|проверк[ау] посетителя|доступ.{0,40}ограничен|"
    r"captcha|access denied|forbidden", re.I,
)
TERMINAL = {"stopped", "expired", "access_denied", "delivery_error", "parse_error"}
READY_ROOT = ('#avia:has([class*="AviaSearch-module__searchButton--"]'
              ':not([disabled]):not([data-loading="true"]))'
              ':not(:has([aria-busy="true"], [role="progressbar"], [data-loading="true"]))')
READY_SELECTOR = (READY_ROOT + ' .avia-info__title, ' + READY_ROOT
                  + ' [class*="FlightCard-module__card--"]')


def now() -> str:
    return datetime.now(ZoneInfo("Europe/Moscow")).isoformat()


def monitoring_dates(at: datetime | None = None) -> list[str]:
    first = (at or datetime.now(CAIRO)).astimezone(CAIRO).date()
    return [(first + timedelta(days=offset)).isoformat() for offset in range(WINDOW_DAYS)]


def save(path: Path, value: dict) -> None:
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False,
    ) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def log_event(kind: str, **data) -> None:
    with HISTORY_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at": now(), "event": kind, **data},
                                ensure_ascii=False) + "\n")


def load_state() -> dict:
    legacy = None
    if STATE_PATH.exists():
        value = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if value.get("schema") == 2 and value.get("rolling_window_days") == WINDOW_DAYS:
            return value
        if value.get("schema") != 1:
            raise RuntimeError("Не совпадают параметры сохранённого мониторинга.")
        legacy = value
    value = {
        "schema": 2, "rolling_window_days": WINDOW_DAYS,
        "origin": "SSH", "destination": "MOW", "mode": "observation",
        "passengers_for_search": {"adults": 1, "children": 0, "infants": 0},
        "passenger_count_confirmed": False, "booking_enabled": False,
        "interval_seconds": INTERVAL, "created_at": now(), "status": "prepared",
        "session_offset": SESSION_PATH.stat().st_size if SESSION_PATH.exists() else 0,
        "offers": {}, "pending": [], "consecutive_errors": 0,
        "date_results": {}, "flights": {}, "date_coverage": {},
        "sources": ["biblio_globus"], "notification_kinds": ["new", "reappeared", "disappeared"],
    }
    if legacy is not None:
        value["legacy_single_date"] = legacy
        value["migrated_at"] = now()
        # A user's stop or an explicit refusal must survive migration.
        if legacy.get("status") in TERMINAL - {"expired"}:
            value["status"] = legacy["status"]
            value["pending"] = legacy.get("pending", [])
            value["last_error"] = legacy.get("last_error")
        log_event("window_reconfigured", rolling_window_days=WINDOW_DAYS,
                  previous_date=legacy.get("date"), booking_enabled=False)
    return value


class Stopped(Exception):
    pass


class AccessDenied(Exception):
    pass


class StopReader:
    """Читает только новые сообщения; стоп не ждёт завершения веб-запроса."""

    def __init__(self, state: dict, path: Path | None = None):
        self.state = state
        self.path = SESSION_PATH if path is None else path
        self.offset = state.get("session_offset", 0)
        self.interrupted = False
        self.user_stop = False

    def check(self):
        if self.interrupted:
            raise Stopped
        if not self.path.exists():
            return
        if self.path.stat().st_size < self.offset:
            self.offset = 0
        with self.path.open("rb") as stream:
            stream.seek(self.offset)
            while line := stream.readline():
                if not line.endswith(b"\n"):
                    break
                self.offset = stream.tell()
                self.state["session_offset"] = self.offset
                try:
                    entry = json.loads(line)
                except (ValueError, UnicodeDecodeError):
                    continue
                if entry.get("type") not in {"text", "voice", "command"}:
                    continue
                text = str(entry.get("text", "")).strip()
                if STOP.fullmatch(text) or re.match(
                    r"^(?:стоп|стой|остановись)(?:[!?,.;]|\s+(?:пожалуйста|не\s+продолжай))",
                    text, re.I,
                ):
                    self.user_stop = True
                    raise Stopped

    def wait(self, seconds: float):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.check()
            time.sleep(min(1, max(0, deadline - time.monotonic())))


def search_url(exclusive: bool = False, *, date_str: str | None = None) -> str:
    params = dict(BASE_PARAMS)
    departure = datetime.fromisoformat(date_str or monitoring_dates()[0])
    params["params"] = f"0{departure:%d%m%Y}_SSH_MOW"
    if exclusive:
        params["un"] = "1"
    return "https://www.bgoperator.ru/price.shtml?" + urlencode(params)


def fetch_search(exclusive: bool, stop: StopReader, *, date_str: str | None = None) -> dict:
    date_str = date_str or monitoring_dates()[0]
    # Использует тот же постоянный профиль и маршрут, что штатное чтение сайтов.
    # Никаких переключений IP, HTTP-fallback, авторизаций или обхода проверки.
    command = [sys.executable, str(ROOT / "scripts/web_fetch.py"),
               search_url(exclusive, date_str=date_str), "--html", "--max-chars", "500000",
               "--wait-selector", READY_SELECTOR]
    with tempfile.TemporaryFile("w+b") as stdout, tempfile.TemporaryFile("w+b") as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr,
                                   start_new_session=True)
        started = time.monotonic()
        try:
            while process.poll() is None:
                stop.check()
                if time.monotonic() - started > 100:
                    raise TimeoutError("Проверка сайта не завершилась за 100 секунд.")
                time.sleep(0.5)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        stdout.seek(0)
        stderr.seek(0)
        html = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8", errors="replace")
    if process.returncode:
        if ACCESS_DENIED.search(error):
            code = re.search(r"HTTP \d{3}", error)
            if code:
                raise AccessDenied(f"Библио-Глобус отклонил запрос: {code[0]}.")
            raise AccessDenied("Библио-Глобус запросил проверку посетителя или ограничил доступ.")
        raise RuntimeError("Не удалось получить ответ сайта: сбой соединения или ожидания.")
    result = parse_search_html(html, expected_date=date_str)
    if result["exclusive"] != exclusive:
        raise ValueError("Сайт не применил запрошенный фильтр поиска.")
    return result


def merge_offers(results: list[dict]) -> dict:
    merged = {}
    for result in results:
        if not result.get("completed"):
            raise ValueError("Поиск не завершён.")
        for original in result["offers"]:
            offer = dict(original)
            if not offer.get("direct"):
                continue
            offer["exclusive"] = result["exclusive"]
            previous = merged.get(offer["id"])
            if previous is None:
                merged[offer["id"]] = offer
            else:
                winner = offer if offer["price_rub"] < previous["price_rub"] else previous
                winner["exclusive"] = previous["exclusive"] or offer["exclusive"]
                merged[offer["id"]] = winner
    return merged


def offer_events(previous: dict, current: dict) -> list[dict]:
    events = []
    for key, offer in current.items():
        old = previous.get(key)
        if old is None:
            events.append({"kind": "new", "offer": offer})
        elif offer["price_rub"] < old["price_rub"]:
            events.append({"kind": "price_drop", "offer": offer,
                           "old_price_rub": old["price_rub"]})
        elif offer.get("exclusive") and not old.get("exclusive"):
            events.append({"kind": "exclusive", "offer": offer})
    return events


def money(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " ₽"


def event_message(event: dict) -> str:
    if "flight_id" in event:
        offer = event["offer"]
        departure = datetime.fromisoformat(offer["departure"])
        labels = {
            "new": "Появился рейс, которого не было в предыдущих проверках",
            "reappeared": "Рейс снова появился в продаже",
            "disappeared": "Рейс исчез из продажи у Библио-Глобуса",
        }
        bounds = event["bounds"]
        after = datetime.fromisoformat(bounds["after"]) if bounds.get("after") else None
        by = datetime.fromisoformat(bounds["by"])
        window = f"между {after:%d.%m %H:%M} и {by:%d.%m %H:%M} МСК" if after else f"{by:%d.%m %H:%M} МСК"
        lead = max(0, event["lead_hours"])
        days, hours = divmod(int(lead), 24)
        lines = [
            f"✈️ {labels[event['kind']]}\n",
            f"Шарм-эль-Шейх → Москва · {offer['carrier']}, {offer['flight']}",
            f"Вылет {departure:%d.%m в %H:%M} по времени Шарма.",
            f"Обнаружено {window}; до вылета {days} дн. {hours} ч.",
        ]
        if event["kind"] != "disappeared":
            lines.append(f"{money(offer['price_rub'])} за одного взрослого; багаж: {offer['baggage']}.")
        else:
            interval = event["interval"]
            lower = interval["duration_seconds_min"] / 3600
            upper = interval["duration_seconds_max"]
            duration = (f"от {lower:.1f} до {upper / 3600:.1f} ч."
                        if upper is not None else f"не менее {lower:.1f} ч.; начало неизвестно")
            lines.append(f"Окно наличия в продаже: {duration} (между проверками возможны пропуски).")
        lines.append("\nЭто наблюдение выдачи продавца. Бронирование отключено на время проверки.")
        return "\n".join(lines)
    offer = event["offer"]
    departure = datetime.fromisoformat(offer["departure"])
    arrival = datetime.fromisoformat(offer["arrival"])
    heading = "✈️ Появился прямой билет Шарм-эль-Шейх → Москва"
    if event["kind"] == "price_drop":
        heading = "✈️ Подешевел прямой билет Шарм-эль-Шейх → Москва"
    elif event["kind"] == "exclusive":
        heading = "✈️ Билет появился в разделе «Только эксклюзив» Библио-Глобуса"
    price = money(offer["price_rub"])
    if event.get("old_price_rub"):
        price = f"{money(event['old_price_rub'])} → {price}"
    return (
        f"{heading}\n\n"
        f"{offer['carrier']}, {offer['flight']}\n"
        f"Вылет {departure:%d.%m в %H:%M}; прилёт {arrival:%d.%m в %H:%M}. "
        "Время местное.\n"
        f"{price} за одного взрослого. Багаж: {offer['baggage']}.\n\n"
        "Наличие подтверждено выдачей продавца; до оформления может измениться. "
        "Бронь не оформлена: автоматическое удержание места пока не подключено."
    )


def queue_notice(state: dict, text: str, kind: str, *, url: str | None = None) -> None:
    event_id = hashlib.sha256((now() + text).encode()).hexdigest()[:24]
    state["pending"].append({"id": event_id, "text": text, "kind": kind, "url": url})


def deliver_pending(state: dict, stop: StopReader) -> None:
    while state["pending"]:
        stop.check()
        event = state["pending"][0]
        path = ROOT / "vault/.session" / f"avia-notice-{event['id']}.json"
        try:
            receipt = notify(event["text"], state_path=path, url=event.get("url"))
        except RuntimeError as exc:
            state.update(status="delivery_error", last_error=str(exc), updated_at=now())
            save(STATE_PATH, state)
            log_event("delivery_error", event_id=event["id"], reason=str(exc))
            raise
        log_event("notification_sent", event_id=event["id"], receipt=receipt)
        state["pending"].pop(0)
        save(STATE_PATH, state)


def cycle(state: dict, stop: StopReader, *, baseline: bool = False) -> None:
    stop.check()
    started = time.time()
    dates = monitoring_dates()
    state.update(window_start=dates[0], window_end=dates[-1],
                 scan_started_at=now(), status="scanning")
    ended = close_past_observations(state, now())
    if ended:
        log_event("observations_ended", events=ended)
    save(STATE_PATH, state)
    failures = []
    successes = 0
    for date_str in dates:
        stop.check()
        try:
            # Общая выдача охватывает все предложения, фильтр не ограничиваем.
            result = fetch_search(False, stop, date_str=date_str)
            if not result.get("completed"):
                raise ValueError("Поиск не завершён.")
        except (AccessDenied, ValueError):
            raise
        except (RuntimeError, TimeoutError) as exc:
            failures.append(date_str)
            date_state = state["date_results"].setdefault(date_str, {})
            date_state.update(last_attempt_at=now(), last_error=str(exc))
            save(STATE_PATH, state)
            log_event("date_connection_error", date=date_str, reason=str(exc))
            continue
        checked_at = now()
        current = merge_offers([result])
        events = update_history(state, date_str, list(current.values()), checked_at)
        state["date_results"][date_str] = {
            "last_success_at": checked_at, "last_attempt_at": checked_at,
            "offers": current, "url": search_url(False, date_str=date_str),
        }
        successes += 1
        state.update(updated_at=checked_at, last_success_at=checked_at)
        state.setdefault("baseline_at", checked_at)
        for event in events:
            if event["kind"] in state["notification_kinds"]:
                queue_notice(state, event_message(event), event["kind"],
                             url=search_url(False, date_str=date_str))
        save(STATE_PATH, state)
        log_event("date_checked", date=date_str, checked_at=checked_at,
                  offers=list(current.values()), events=events,
                  baseline=state["date_coverage"][date_str]["successful_checks"] == 1)
    state.update(
        offers={key: offer for day in dates
                for key, offer in state["date_results"].get(day, {}).get("offers", {}).items()},
        status="connection_error" if failures else "running", updated_at=now(),
        next_check_at=max(time.time(), started + state["interval_seconds"]),
        consecutive_errors=state.get("consecutive_errors", 0) + 1 if failures else 0,
        scan_completed_at=now(), scan_seconds=round(time.time() - started, 2),
        scan_successful_dates=successes, scan_failed_dates=failures,
    )
    if failures:
        state["last_error"] = "Не получен ответ для дат: " + ", ".join(failures)
        if state["consecutive_errors"] == 3:
            queue_notice(state, "В трёх обходах мониторинга подряд есть пропуски из-за "
                         "сбоев соединения. Для этих дат наличие неизвестно; "
                         "это не считается исчезновением рейсов.", "connection_error")
    else:
        state.pop("last_error", None)
        state["last_complete_scan_at"] = now()
    save(STATE_PATH, state)
    write_report(state)
    log_event("scan_completed", dates=dates, successful_dates=successes,
              failed_dates=failures, scan_seconds=state["scan_seconds"])


def write_report(state: dict) -> None:
    lines = [
        "# Наблюдения за рейсами Шарм-эль-Шейх → Москва", "",
        f"Обновлено: {state.get('updated_at', '—')}",
        f"Скользящее окно: {state.get('window_start', '—')} — {state.get('window_end', '—')} (21 дата).",
        "Источник: общая выдача Библио-Глобуса, прямые рейсы, один взрослый.",
        "Целевой интервал повторного обхода — 5 минут от начала обхода; фактические интервалы сохраняются по каждой дате.",
        "Первый успешный снимок каждой даты — исходный набор, не доказанное позднее открытие продаж.",
        "Ошибки чтения и выход за окно наблюдения не считаются исчезновением. Бронирование отключено.", "",
        f"Последний обход: успешно {state.get('scan_successful_dates', 0)} из 21 дат; "
        f"длительность {state.get('scan_seconds', '—')} с.", "",
        "| Дата вылета | Рейс | Вылет, Шарм | Первое наблюдение, МСК | Последнее наличие, МСК | Состояние |",
        "|---|---|---|---|---|---|",
    ]
    for record in sorted(state.get("flights", {}).values(),
                         key=lambda r: (r["offer"]["departure"], r["offer"]["flight"])):
        offer = record["offer"]
        departure = datetime.fromisoformat(offer["departure"])
        first = datetime.fromisoformat(record["first_seen_at"])
        last = datetime.fromisoformat(record["last_seen_at"])
        in_window = state.get("window_start", "") <= record["date"] <= state.get("window_end", "")
        departed = departure <= datetime.fromisoformat(state["updated_at"])
        active = record.get("present") and in_window and not departed
        if not in_window or departed:
            status = "наблюдение завершено"
        elif active:
            status = "был в последней успешной выдаче"
        else:
            status = "нет в последней успешной выдаче"
        lines.append(f"| {departure:%d.%m.%Y} | {offer['flight']} | {departure:%H:%M} | "
                     f"{first:%d.%m %H:%M} | {last:%d.%m %H:%M} | {status} |")
    lines.extend(["", "## Интервалы наличия", "",
                  "Точные границы появления и исчезновения находятся между двумя успешными проверками. "
                  "Полные снимки, события и погрешности времени сохранены в «История мониторинга.jsonl» и «Состояние мониторинга.json»."])
    labels = {"baseline": "исходный набор; начало неизвестно", "new": "новое появление", "reappeared": "возврат"}
    for record in sorted(state.get("flights", {}).values(), key=lambda r: (r["date"], r["flight"])):
        for interval in record["availability_intervals"]:
            first = datetime.fromisoformat(interval["first_present_at"])
            last = datetime.fromisoformat(interval["last_present_at"])
            departure = datetime.fromisoformat(record["offer"]["departure"])
            lead = (departure - first).total_seconds() / 3600
            lower = interval["duration_seconds_min"] / 3600
            upper = interval["duration_seconds_max"]
            duration = (f"от {lower:.2f} до {upper / 3600:.2f} ч." if upper is not None
                        else f"не менее {lower:.2f} ч., верхняя граница неизвестна")
            lines.extend(["", f"- {record['date']}, {record['flight']}: {labels[interval['opened_kind']]}; "
                          f"первое наличие {first:%d.%m %H:%M} МСК, до вылета {lead:.2f} ч. "
                          f"Последнее наличие {last:%d.%m %H:%M} МСК. Наблюдаемая длительность: {duration}."])
    report = PROJECT / "Наблюдения за рейсами.md"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=PROJECT, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write("\n".join(lines) + "\n")
    temporary.replace(report)


def run(*, once: bool = False, baseline: bool = False) -> int:
    state = load_state()
    if state["status"] in TERMINAL:
        if not once and state["status"] in {"access_denied", "parse_error"}:
            try:
                deliver_pending(state, StopReader(state))
            except (RuntimeError, Stopped):
                return 2
        print(json.dumps({"status": state["status"], "last_error": state.get("last_error")},
                         ensure_ascii=False))
        return 0
    stop = StopReader(state)
    signal.signal(signal.SIGTERM, lambda *_: setattr(stop, "interrupted", True))
    signal.signal(signal.SIGINT, lambda *_: setattr(stop, "interrupted", True))
    state.update(process_id=os.getpid(), service_started_at=now(), updated_at=now())
    if state["status"] in {"prepared", "suspended"}:
        state["status"] = "running" if state.get("baseline_at") else "starting"
    save(STATE_PATH, state)
    try:
        while True:
            stop.check()
            if not once:
                deliver_pending(state, stop)
            if not once and state.get("next_check_at", 0) > time.time():
                save(STATE_PATH, state)
                stop.wait(state["next_check_at"] - time.time())
                continue
            try:
                cycle(state, stop, baseline=baseline)
            except AccessDenied as exc:
                state.update(status="access_denied", last_error=str(exc), updated_at=now())
                queue_notice(state, f"Мониторинг авиабилетов остановлен. {exc} "
                             "Автоматических повторов не будет.", "access_denied")
                save(STATE_PATH, state)
                log_event("access_denied", reason=str(exc))
                if not once:
                    deliver_pending(state, stop)
                return 2
            except ValueError as exc:
                state.update(status="parse_error", last_error=str(exc), updated_at=now())
                queue_notice(state, "Мониторинг авиабилетов остановлен: больше не удаётся "
                             "надёжно прочитать выдачу Библио-Глобуса. "
                             "Отсутствие ответа не считается отсутствием билетов.", "parse_error")
                save(STATE_PATH, state)
                log_event("parse_error", reason=str(exc))
                if not once:
                    deliver_pending(state, stop)
                return 2
            except (RuntimeError, TimeoutError) as exc:
                state["consecutive_errors"] += 1
                state.update(status="connection_error", last_error=str(exc), updated_at=now(),
                             next_check_at=time.time() + state["interval_seconds"])
                if state["consecutive_errors"] == 3:
                    queue_notice(state, "Три проверки авиабилетов подряд не получили ответ "
                                 "Библио-Глобуса. Наличие сейчас неизвестно; повторю "
                                 "обычную проверку через пять минут.", "connection_error")
                save(STATE_PATH, state)
                log_event("connection_error", reason=str(exc),
                          count=state["consecutive_errors"])
                if once:
                    return 1
            if not once:
                deliver_pending(state, stop)
            if once:
                print(json.dumps({"status": state["status"], "offers": len(state["offers"]),
                                  "sources": state.get("sources", [])}, ensure_ascii=False))
                return 1 if state["status"] == "connection_error" else 0
    except Stopped:
        state.update(status="stopped" if stop.user_stop else "suspended", updated_at=now())
        save(STATE_PATH, state)
        log_event(state["status"])
        return 0
    except RuntimeError:
        return 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "run", "status"])
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    if args.baseline and args.action != "check":
        parser.error("--baseline допускается только для разовой начальной проверки")
    if args.action == "status":
        value = load_state()
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    lock_path = ROOT / "tmp/avia-monitor.lock"
    with lock_path.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Проверка мониторинга уже выполняется.", file=sys.stderr)
            return 1
        return run(once=args.action == "check", baseline=args.baseline)


if __name__ == "__main__":
    raise SystemExit(main())
