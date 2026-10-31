"""Parse a rendered public Biblio-Globus flight search without making requests.

Only a completed search for SSH -> Moscow is accepted. A search form, a partial
render, or an error must never be recorded as an empty availability result.
Booking links are returned as data and are never opened by this module.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from html.parser import HTMLParser
from urllib.parse import parse_qs, urljoin, urlsplit
from zoneinfo import ZoneInfo

BASE_URL = "https://www.bgoperator.ru"
MOSCOW_AIRPORTS = {"MOW", "SVO", "VKO", "DME", "ZIA"}
EMPTY_RESULT = "По заданным параметрам не найдены перелёты"
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


@dataclass
class _Node:
    tag: str
    attrs: dict[str, str | None] = field(default_factory=dict)
    children: list[_Node | str] = field(default_factory=list)

    def nodes(self):
        for child in self.children:
            if isinstance(child, _Node):
                yield child
                yield from child.nodes()

    def text(self) -> str:
        if self.tag in {"script", "style"}:
            return ""
        parts = [c.text() if isinstance(c, _Node) else c for c in self.children]
        return " ".join(" ".join(parts).split())

    def has_class(self, prefix: str) -> bool:
        classes = (self.attrs.get("class") or "").split()
        return any(c.startswith(prefix) for c in classes)

    def by_class(self, prefix: str) -> list[_Node]:
        return [node for node in self.nodes() if node.has_class(prefix)]


class _TreeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _one(nodes: list[_Node], description: str) -> _Node:
    if len(nodes) != 1:
        raise ValueError(f"Не удалось проверить {description}")
    return nodes[0]


def _verify_form(avia: _Node, expected_date: str) -> None:
    search = _one(avia.by_class("AviaSearch-module__search--"), "форму поиска")
    codes = [n.text() for n in search.by_class("AviaSearch-module__code--")]
    if codes != ["SSH", "MOW"]:
        raise ValueError("В форме поиска другой или неподтверждённый маршрут")
    dates = _one(search.by_class("AviaSearch-module__dates--"), "даты поиска")
    hidden = [n.attrs.get("value", "") for n in dates.nodes()
              if n.tag == "input" and n.attrs.get("type") == "hidden"]
    if hidden != [expected_date, ""]:
        raise ValueError("В форме поиска другая дата или задан обратный перелёт")
    button = _one(search.by_class("AviaSearch-module__searchButton--"), "кнопку поиска")
    if "disabled" in button.attrs or button.attrs.get("data-loading") == "true":
        raise ValueError("Поиск ещё выполняется")


def _exclusive_filter(avia: _Node) -> bool:
    labels = [n for n in avia.nodes() if n.tag == "label"
              and n.text() == "Только эксклюзив"]
    label = _one(labels, "фильтр эксклюзивных предложений")
    control_id = label.attrs.get("for")
    if not control_id:
        raise ValueError("Фильтр эксклюзивных предложений не связан с переключателем")
    controls = [n for n in avia.nodes() if n.tag == "input"
                and n.attrs.get("id") == control_id
                and n.attrs.get("type") == "checkbox"]
    control = _one(controls, "состояние фильтра эксклюзивных предложений")
    return "checked" in control.attrs


def _parse_offer(card: _Node, expected_date: str) -> dict | None:
    links = [n for n in card.nodes() if n.tag == "a"
             and parse_qs(urlsplit(n.attrs.get("href") or "").query).get("action")
             == ["biletnewsorder"]]
    link = _one(links, "ссылку выбора билета")
    booking_url = urljoin(BASE_URL, link.attrs["href"] or "")
    parsed_url = urlsplit(booking_url)
    if parsed_url.scheme != "https" or parsed_url.hostname != "www.bgoperator.ru":
        raise ValueError("Неожиданный адрес выбора билета")
    parameters = parse_qs(parsed_url.query)
    par = parameters.get("par", [""])[0]
    # The site's order link carries route, fare and local segment timestamps.
    # Inspect this parsed attribute only; never search arbitrary page text.
    groups = re.findall(r"\(([^()]*)\)", par)
    if len(groups) != 3:
        raise ValueError("Не удалось прочитать маршрут и тариф билета")
    segments = groups[0].split("~")
    price = _one(card.by_class("FlightCard-module__price--"), "цену билета").text()
    digits = price.removesuffix("₽").replace(" ", "").replace("\u00a0", "")
    if not price.endswith("₽") or not digits.isdigit() or int(digits) <= 0:
        raise ValueError("Цена билета не подтверждена в рублях")
    carrier = _one(card.by_class("FlightCard-module__airlines--"), "перевозчика").text()
    if not carrier:
        raise ValueError("Не указан перевозчик")
    if len(segments) != 1:
        return None
    pieces = segments[0].split(".")
    if len(pieces) != 4:
        raise ValueError("Не удалось прочитать прямой рейс")
    flight_token, stamps, origin, destination = pieces
    if origin != "SSH" or destination not in MOSCOW_AIRPORTS:
        raise ValueError("Маршрут карточки отличается от запроса")
    if not re.fullmatch(r"O[A-Z0-9][A-Z0-9]{2}\d{1,5}", flight_token):
        raise ValueError("Номер рейса не подтверждён")
    if not re.fullmatch(r"\d{20}", stamps):
        raise ValueError("Не удалось прочитать время рейса")
    departure = datetime.strptime(stamps[:10], "%y%m%d%H%M")
    arrival = datetime.strptime(stamps[10:], "%y%m%d%H%M")
    if departure.date().isoformat() != expected_date:
        raise ValueError("Дата карточки отличается от запроса")
    departure = departure.replace(tzinfo=ZoneInfo("Africa/Cairo"))
    arrival = arrival.replace(tzinfo=ZoneInfo("Europe/Moscow"))
    if arrival <= departure:
        raise ValueError("Некорректное время прилёта")
    summary = _one(card.by_class("FlightCard-module__summary--"), "описание тарифа")
    baggage = next((n.text() for n in summary.nodes() if n.tag == "li"
                    and (n.text().startswith("Багаж") or n.text() == "Без багажа")),
                   "не указан")
    identity = "biblio_globus|" + groups[0] + "|" + groups[2]
    return {
        "id": "bg:" + hashlib.sha256(identity.encode()).hexdigest()[:24],
        "flight": flight_token[2:],
        "origin": origin,
        "destination": destination,
        "carrier": carrier,
        "departure": departure.isoformat(timespec="minutes"),
        "arrival": arrival.isoformat(timespec="minutes"),
        "price_rub": int(digits),
        "baggage": baggage,
        "booking_url": booking_url,
        "direct": True,
    }


def parse_search_html(html: str, *, expected_date: str = "2026-11-21") -> dict:
    """Return observed direct offers, or raise if completion cannot be verified."""
    date.fromisoformat(expected_date)
    parser = _TreeParser()
    parser.feed(html)
    parser.close()
    avia = _one([n for n in parser.root.nodes() if n.attrs.get("id") == "avia"],
                "раздел поиска авиабилетов")
    _verify_form(avia, expected_date)
    exclusive = _exclusive_filter(avia)
    for node in avia.nodes():
        classes = (node.attrs.get("class") or "").lower()
        if (node.attrs.get("aria-busy") == "true"
                or node.attrs.get("role") == "progressbar"
                or node.attrs.get("data-loading") == "true"
                or any(word in classes for word in ("loader", "skeleton", "loading"))):
            raise ValueError("Выдача ещё загружается")
    listing = _one(avia.by_class("avia-price-page__list"), "выдачу поиска")
    cards = listing.by_class("FlightCard-module__card--")
    titles = listing.by_class("avia-info__title")
    if any(n.text() != EMPTY_RESULT for n in titles):
        raise ValueError("Источник вернул сообщение вместо выдачи")
    empty = [n for n in titles if n.text() == EMPTY_RESULT]
    if bool(cards) == bool(empty):
        raise ValueError("Завершение поиска не подтверждено")
    offers = []
    for card in cards:
        offer = _parse_offer(card, expected_date)
        if offer is not None:
            offers.append(offer)
    return {
        "source": "biblio_globus",
        "query": {
            "origin": "SSH", "destination": "MOW", "date": expected_date,
            "verified_route": True, "verified_date": True,
        },
        "exclusive": exclusive,
        "offers": offers,
        "completed": True,
    }
