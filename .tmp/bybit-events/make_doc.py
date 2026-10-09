import json, datetime as dt, re, statistics as st
from collections import defaultdict
MSK=dt.timezone(dt.timedelta(hours=3))
L=json.load(open(".tmp/bybit-events/events.json")); R={int(k):v for k,v in json.load(open(".tmp/bybit-events/reaction.json")).items()}
g=defaultdict(dict)
for x in L: g[int(x["eventTime"])][x["enTitle"]]=x
ORDER=["Fed Interest Rate Decision","Non Farm Payrolls","Unemployment Rate","Inflation Rate YoY","Inflation Rate MoM","Core Inflation Rate YoY","Core Inflation Rate MoM","PPI MoM","Core PCE Price Index MoM","GDP Growth Rate QoQ Adv","GDP Growth Rate QoQ 2nd Est","GDP Growth Rate QoQ Final"]
SHORT={"Fed Interest Rate Decision":"⚡ Ставка ФРС","Non Farm Payrolls":"⚡ NFP","Unemployment Rate":"Безработица","Inflation Rate YoY":"CPI г/г","Inflation Rate MoM":"CPI м/м","Core Inflation Rate YoY":"Базовый CPI г/г","Core Inflation Rate MoM":"Базовый CPI м/м","PPI MoM":"PPI м/м","Core PCE Price Index MoM":"⚡ Базовый PCE м/м","GDP Growth Rate QoQ Adv":"ВВП кв/кв, 1-я оценка","GDP Growth Rate QoQ 2nd Est":"ВВП кв/кв, 2-я оценка","GDP Growth Rate QoQ Final":"ВВП кв/кв, окончательная"}
MON=["","янв","фев","мар","апр","мая","июн","июл","авг","сен","окт","ноя","дек"]
def d(t): x=dt.datetime.fromtimestamp(t/1000,MSK); return f"{x.day} {MON[x.month]} {x.year}", x.strftime("%H:%M")
def v(s):
    s=(s or "").strip()
    if not s: return "—"
    s=s.replace("-","−").replace(".",",")
    return re.sub(r"K$"," тыс.",s)
def p(x):
    if abs(x)<0.05: return "0,0%"
    return f"{x:+.1f}%".replace(".",",").replace("-","−")
def p0(x): return f"{x:.1f}%".replace(".",",")
now=int(dt.datetime(2026,10,8,23,0,tzinfo=MSK).timestamp()*1000)
past=[t for t in sorted(g) if t<now]; future=[t for t in sorted(g) if t>=now]
# stats
base=1.23
ev=[R[t]["range"] for t in past if R.get(t)]
kept=sum(1 for t in past if R.get(t) and abs(R[t]["close"])>=0.5*R[t]["range"])
def med(keys):
    a=[R[t]["range"] for t in past if R.get(t) and any(k in g[t] for k in keys)]
    return p0(st.median(a)), p0(max(a)), len(a)
out=[]
w=out.append
w("""---
type: reference
description: Метки американской статистики на графике DASHUSDT в Bybit — что означают, когда выходят и как DASH двигался в час после каждой с апреля 2025.
related: "[[projects/dash-trading/README|Торговля DASH]]"
created: 2026-10-08
last_accessed: 2026-10-08
relevance: 0.9
tier: active
---

# Метки событий на графике Bybit

Внизу графика DASHUSDT Bybit ставит метки выхода американской статистики: инфляция, рынок труда, ставка ФРС, ВВП. Список меток у Bybit один на все монеты, к DASH он не привязан. Bybit отдаёт метки с 4 апреля 2025 года и заранее расписывает их до 23 декабря 2026 года. Выгрузка сделана 8 октября 2026 года, всё время московское.

⚡ — так Bybit сам помечает события сильного влияния.

## Какие метки бывают

Время выхода: 15:30 по Москве, а с ноября до середины марта, когда в США зимнее время, — 16:30. Решение ФРС выходит в 21:00, зимой в 22:00.

«Учебное правило» — как рынок обычно трактует цифру. «Совпало» — в скольких случаях DASH через час после метки ушёл туда, куда указывает правило. Считались только случаи, где факт отличался от прогноза.

| Метка на графике | Что это | Когда выходит | Учебное правило для крипты | DASH за час после метки |
|---|---|---|---|---|
""")
rows=[
 (["Fed Interest Rate Decision"],"⚡ Fed Interest Rate Decision","Решение ФРС по базовой ставке","8 раз в год, 21:00 / 22:00. Через 30 минут — пресс-конференция председателя ФРС, часто второй всплеск","Снижение или мягкий тон — рост, повышение или жёсткий тон — падение. Важнее не само решение, а отличие от ожиданий","Bybit пишет верхнюю границу диапазона ставки. 16 сен 2026 ФРС подняла ставку до 3,75–4%, рынок это повышение ждал, а DASH за час вырос на 5,2%"),
 (["Non Farm Payrolls"],"⚡ Non Farm Payrolls (NFP)","Сколько рабочих мест создано в США за месяц вне сельского хозяйства","Обычно первая пятница месяца","Меньше прогноза — ФРС скорее снизит ставку — крипте плюс. Больше прогноза — минус","Совпало 9 из 17 — как монетка"),
 (["Unemployment Rate"],"Unemployment Rate","Уровень безработицы в США","Вместе с NFP","Выше прогноза — крипте плюс, ниже — минус","Совпало 6 из 11"),
 (["Inflation Rate YoY","Inflation Rate MoM","Core Inflation Rate YoY","Core Inflation Rate MoM"],"Inflation Rate YoY / MoM, Core Inflation Rate YoY / MoM","Потребительская инфляция CPI за год и за месяц. «Core» — базовая, без еды и энергии","Четыре метки разом, около середины месяца","Ниже прогноза — крипте плюс, выше — минус","По общей за год совпало 7 из 9, по базовой за месяц 8 из 11"),
 (["PPI MoM"],"PPI MoM","Цены производителей за месяц, ранний сигнал для потребительской инфляции","Обычно через день-два после CPI","Ниже прогноза — плюс, выше — минус","Совпало 9 из 14"),
 (["Core PCE Price Index MoM"],"⚡ Core PCE Price Index MoM","Базовый индекс цен личных расходов, главный показатель инфляции для ФРС","Конец месяца, часто вместе с ВВП","Ниже прогноза — плюс, выше — минус","Совпало 4 из 5"),
 (["GDP Growth Rate QoQ Adv","GDP Growth Rate QoQ 2nd Est","GDP Growth Rate QoQ Final"],"GDP Growth Rate QoQ Adv / 2nd Est / Final","Рост ВВП США за квартал: первая, вторая и окончательная оценки","По одной оценке в месяц, конец месяца","Неоднозначно: сильная экономика хороша для рынка, но отдаляет снижение ставки","Направление не считал: правило неоднозначное"),
]
for keys,label,what,when,rule,res in rows:
    m,mx,n=med(keys)
    w(f"| {label} | {what} | {when} | {rule} | Обычный размах {m}, максимум {mx} ({n} раз). {res} |\n")
w(f"""
## Насколько DASH реагирует

- 📊 В обычный час цена DASH ходит примерно на {p0(base)} от минимума до максимума. Это медиана по 13 242 часовым свечам Bybit с апреля 2025 года.
- ⚡ В час после метки — {p0(st.median(ev))}, то есть примерно в полтора раза больше. Посчитано по {len(ev)} прошедшим меткам.
- 🎲 Направление по учебному правилу угадывается плохо. По инфляции правило чаще совпадает, по рынку труда и ставке ФРС совпадает примерно в половине случаев. Надёжно одно: в этот час цену болтает сильнее.
- ↗️ Движение после метки часто не возвращается: почти в половине случаев, {kept} из {len(ev)}, через час цена осталась дальше половины своего размаха от уровня до метки. Для стратегии возврата к средней это важно: выброс на статистике — не обычный выброс.

## Самые сильные движения

| Дата | Время | Метка | Рост за час | Падение за час | Итог через час |
|---|---|---|---|---|---|
""")
top=sorted((t for t in past if R.get(t)), key=lambda t:-R[t]["range"])[:10]
for t in top:
    a,b=d(t); r=R[t]
    w(f"| {a} | {b} | {', '.join(SHORT[k] for k in ORDER if k in g[t])} | {p(r['up'])} | {p(r['down'])} | {p(r['close'])} |\n")
w("""
## Ближайшие метки

Прогнозы Bybit заполняет ближе к дате выхода. «Было» — прошлое значение показателя. Даты по данным Bybit, их могут сдвинуть.

| Дата | Время | Метка | Было |
|---|---|---|---|
""")
for t in future:
    a,b=d(t)
    for k in ORDER:
        if k in g[t]: w(f"| {a} | {b} | {SHORT[k]} | {v(g[t][k]['previous'])} |\n")
w("""
## Все прошедшие метки

В скобках — прогноз и прошлое значение. Реакция DASH считается от цены закрытия пятиминутной свечи перед меткой: самый высокий и самый низкий уровень за следующие 60 минут и цена через час.

| Дата | Время | Что вышло: факт (прогноз; было) | Рост | Падение | Итог |
|---|---|---|---|---|---|
""")
for t in past:
    a,b=d(t); r=R.get(t)
    items="<br>".join(f"{SHORT[k]}: **{v(g[t][k]['actual'])}** ({v(g[t][k]['forecast'])}; {v(g[t][k]['previous'])})" for k in ORDER if k in g[t])
    rr=(p(r['up']),p(r['down']),p(r['close'])) if r else ("—","—","—")
    w(f"| {a} | {b} | {items} | {rr[0]} | {rr[1]} | {rr[2]} |\n")
w("""
## Откуда данные и как обновить

- Метки: запрос Bybit `POST https://www.bybitglobal.com/x-api/de/cht/market-index/trading-data/v1/calendar/kline-us-event` с телом `{"from": "<мс>", "to": "<мс>"}`. Этот запрос делает сам график Bybit. За один раз Bybit отдаёт не больше примерно 13 месяцев. Сайт bybit.com с нашего сервера в Швеции перекидывает на главную, поэтому запрос идёт через bybitglobal.com.
- Цены: пятиминутные и часовые свечи Bybit по бессрочному фьючерсу DASHUSDT, `https://api.bybit.com/v5/market/kline?category=linear&symbol=DASHUSDT`.
- Названия меток у Bybit по-русски переведены машинно и каждый раз по-разному, поэтому в таблицах свои названия, а в первой таблице — английские, как на графике.
- Ограничения: несколько показателей выходят в одну минуту, и реакция на них общая. В тот же час на цену могли влиять и другие новости. Совпадения направления посчитаны на малом числе случаев, это наблюдение, а не закономерность.
""")
open("vault/projects/dash-trading/Метки событий на графике Bybit.md","w").write("".join(out))
print(len(past),len(future),kept,len(ev))
