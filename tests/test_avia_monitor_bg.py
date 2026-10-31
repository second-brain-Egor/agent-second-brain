"""Search samples are reduced from BG's public response on 2026-10-30.

Keep real route, fare, price and DOM class values. Omit decorative SVGs,
carousels, CSS and the unrelated page header rather than depending on live web.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.avia_monitor_bg import parse_search_html


FORM = """
<div class="AviaSearch-module__search--WL03E">
  <div class="AviaSearch-module__fromTo--LKESU">
    <span class="AviaSearch-module__code--zVAGM">SSH</span>
    <input value="SHARM EL SHEIKH">
    <span class="AviaSearch-module__code--zVAGM">MOW</span>
    <input value="MOSCOW">
  </div>
  <div class="AviaSearch-module__dates--pwMIX">
    <label>Туда</label><button>21 ноября</button>
    <input type="hidden" value="2026-11-21">
    <label>Обратно</label><input type="hidden" value="">
  </div>
  <button class="AviaSearch-module__searchButton--vlh8W">Найти</button>
</div>
<input type="checkbox" id="exclusive" value="1">
<label for="exclusive">Только эксклюзив</label>
"""

CARDS = """
<div class="avia-price-page__list">
  <div class="FlightCard-module__card--cn_Lc">
    <div class="FlightCard-module__airlines--_14Hx">TURKISH AIRLINES</div>
    <div class="FlightCard-module__duration--pZw4W"><b>1 пересадка</b></div>
    <div class="FlightCard-module__summary--K9a8Y">
      <div class="FlightCard-module__price--UXlkE"><span>40 020</span> <span>₽</span></div>
      <ul><li>Багаж 1 шт.</li><li>ECOFLY</li></ul>
      <a href="/price.shtml?action=biletnewsorder&amp;par=1.40020.SAB.MA.1(OTTK699.26112104552611210850.SSH.IST~OTTK411.26112120302611220035.IST.VKO)(0)(A1_1_CL_TPCLO_1PC_MA)&amp;sc=b8ca65e7fc00b793ee5c7631f7b19502">Выбрать</a>
    </div>
  </div>
  <div class="FlightCard-module__card--cn_Lc">
    <div class="FlightCard-module__airlines--_14Hx">Аэрофлот</div>
    <div class="FlightCard-module__from--fdbII"><time><strong>22:35</strong>21 ноября 2026, сб</time><p>Шарм-эль-шейх, SSH</p></div>
    <div class="FlightCard-module__to--D1hVw"><time><strong>05:40<span>+1</span></strong>22 ноября 2026, вс</time><p>Москва, SVO</p></div>
    <div class="FlightCard-module__summary--K9a8Y">
      <div class="FlightCard-module__price--UXlkE"><span>64 404</span> <span>₽</span></div>
      <ul><li>Без багажа</li><li>Эконом Базовый</li><li>Класс перелёта: M</li></ul>
      <a href="/price.shtml?action=biletnewsorder&amp;par=1.64404.AFL.MA.1(OMSU0431.26112122352611220540.SSH.SVO)(MTAzMDE3OTMzNDQ2MjU3NzcwMzVfMF42NDQwNC4wMAoJCQkJCV4xMDMwMTc5MzM0NDYyNTc3NzAzNToxXkFEVF5BRFReNjQ0MDQuMA)(A1_1_NB_MNO_0PC_MA)&amp;sc=6170aca6bd0982a87eb0bcd8eb0ee14e">Выбрать</a>
    </div>
  </div>
  <div class="FlightCard-module__card--cn_Lc">
    <div class="FlightCard-module__airlines--_14Hx">Аэрофлот</div>
    <div class="FlightCard-module__from--fdbII"><time><strong>08:45</strong>21 ноября 2026, сб</time><p>Шарм-эль-шейх, SSH</p></div>
    <div class="FlightCard-module__to--D1hVw"><time><strong>15:45</strong>21 ноября 2026, сб</time><p>Москва, SVO</p></div>
    <div class="FlightCard-module__summary--K9a8Y">
      <div class="FlightCard-module__price--UXlkE"><span>71 089</span> <span>₽</span></div>
      <ul><li>Без багажа</li><li>Эконом Базовый</li><li>Класс перелёта: B</li></ul>
      <a href="/price.shtml?action=biletnewsorder&amp;par=1.71089.AFL.MA.1(OBSU0439.26112108452611211545.SSH.SVO)(MTAzMDE3OTMzNDQ2MjU3NzcwMzVfM143MTA4OS4wMAoJCQkJCV4xMDMwMTc5MzM0NDYyNTc3NzAzNToxXkFEVF5BRFReNzEwODkuMA)(A1_1_NB_BNO_0PC_MA)&amp;sc=a319322d8b5963b20f077a401bcc4969">Выбрать</a>
    </div>
  </div>
  <div class="FlightCard-module__card--cn_Lc">
    <div class="FlightCard-module__airlines--_14Hx">Аэрофлот</div>
    <div class="FlightCard-module__from--fdbII"><time><strong>07:15</strong>21 ноября 2026, сб</time><p>Шарм-эль-шейх, SSH</p></div>
    <div class="FlightCard-module__to--D1hVw"><time><strong>14:10</strong>21 ноября 2026, сб</time><p>Москва, SVO</p></div>
    <div class="FlightCard-module__summary--K9a8Y">
      <div class="FlightCard-module__price--UXlkE"><span>86 769</span> <span>₽</span></div>
      <ul><li>Без багажа</li><li>Эконом Базовый</li><li>Класс перелёта: D</li></ul>
      <a href="/price.shtml?action=biletnewsorder&amp;par=1.86769.AFL.MA.1(ODSU0429.26112107152611211410.SSH.SVO)(MTAzMDE3OTMzNDQ2MjU3NzcwMzVfNl44Njc2OS4wMAoJCQkJCV4xMDMwMTc5MzM0NDYyNTc3NzAzNToxXkFEVF5BRFReODY3NjkuMA)(A1_1_NB_DNO_0PC_MA)&amp;sc=dbd0742d8be73e4ce752df049a3a3c11">Выбрать</a>
    </div>
  </div>
</div>
"""

EMPTY = """
<div class="avia-price-page__list"><div class="avia-info">
  <h3 class="avia-info__title">По заданным параметрам не найдены перелёты</h3>
  <button>Сбросить фильтры</button>
</div></div>
"""


def page(results=CARDS, *, form=FORM):
    return '<html><body><div id="avia">' + form + results + '</div></body></html>'


def test_real_sales_keep_three_direct_flights_and_filter_transfer():
    result = parse_search_html(page())
    assert result["completed"] is True
    assert result["exclusive"] is False
    assert result["query"] == {
        "origin": "SSH", "destination": "MOW", "date": "2026-11-21",
        "verified_route": True, "verified_date": True,
    }
    offers = result["offers"]
    assert [(o["flight"], o["price_rub"]) for o in offers] == [
        ("SU0431", 64404), ("SU0439", 71089), ("SU0429", 86769),
    ]
    assert all(o["direct"] for o in offers)
    assert offers[0]["departure"] == "2026-11-21T22:35+02:00"
    assert offers[0]["arrival"] == "2026-11-22T05:40+03:00"
    assert offers[0]["carrier"] == "Аэрофлот"
    assert offers[0]["baggage"] == "Без багажа"
    assert offers[0]["booking_url"].startswith("https://www.bgoperator.ru/")


def test_confirmed_empty_exclusive_search():
    exclusive_form = FORM.replace('id="exclusive"', 'id="exclusive" checked')
    result = parse_search_html(page(EMPTY, form=exclusive_form))
    assert result["completed"] is True
    assert result["exclusive"] is True
    assert result["offers"] == []


@pytest.mark.parametrize("results", [
    "", '<div class="avia-price-page__list"></div>',
    '<div class="avia-price-page__list"><div>Ошибка сервера</div></div>',
    '<div class="avia-price-page__list"><div class="Loader-module__block">Поиск</div></div>',
])
def test_main_form_loading_and_errors_are_not_empty_availability(results):
    with pytest.raises(ValueError):
        parse_search_html(page(results))


@pytest.mark.parametrize("original,replacement", [
    ('value="2026-11-21"', 'value="2026-11-20"'),
    ('>SSH</span>', '>HRG</span>'),
    ('>MOW</span>', '>LED</span>'),
])
def test_query_checked_independently_of_valid_cards(original, replacement):
    with pytest.raises(ValueError):
        parse_search_html(page(form=FORM.replace(original, replacement)))


def test_broken_or_inconsistent_card_is_not_recorded_as_no_offers():
    with pytest.raises(ValueError):
        parse_search_html(page(CARDS.replace("2611212235", "2611202235")))
    with pytest.raises(ValueError):
        parse_search_html(page(CARDS.replace("64 404", "нет цены")))


def test_tariff_identity_survives_new_quote_and_price_but_changes_with_fare():
    first = parse_search_html(page())["offers"][0]
    changed = CARDS.replace("64 404", "65 000").replace("1.64404", "1.65000")
    changed = changed.replace("6170aca6bd0982a87eb0bcd8eb0ee14e", "new_quote")
    changed = changed.replace("(MTAzMDE3OTMzNDQ2MjU3NzcwMzVfMF42", "(differentQuote")
    second = parse_search_html(page(changed))["offers"][0]
    assert first["id"] == second["id"]
    assert first["price_rub"] != second["price_rub"]
    another_fare = parse_search_html(page(CARDS.replace("MNO_0PC", "MFO_1PC")))["offers"][0]
    assert another_fare["id"] != first["id"]


def test_missing_baggage_is_explicitly_unknown():
    result = parse_search_html(page(CARDS.replace("<li>Без багажа</li>", "")))
    assert result["offers"][0]["baggage"] == "не указан"


def test_loading_overlay_prevents_treating_old_cards_as_complete():
    with pytest.raises(ValueError):
        parse_search_html(page(CARDS + '<div aria-busy="true">Поиск</div>'))


def test_empty_text_in_script_cannot_make_an_unloaded_form_complete():
    script = '<script>const message = "По заданным параметрам не найдены перелёты";</script>'
    with pytest.raises(ValueError):
        parse_search_html(page(script))
