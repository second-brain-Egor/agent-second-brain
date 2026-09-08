import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from zoneinfo import ZoneInfo

p = Path('.tmp/dash-corridors-2026-09-07')
raw = pd.read_csv(p / 'bars-5m.csv').sort_values(['exchange', 'bucket', 'first_ms'])
for _, group in raw.groupby(['exchange', 'bucket']):
    if len(group) > 1:
        assert (group.first_ms.iloc[1:].to_numpy() >= group.last_ms.iloc[:-1].to_numpy()).all()
d = raw.groupby(['exchange', 'bucket'], as_index=False).agg(
    open=('open', 'first'), high=('high', 'max'), low=('low', 'min'), close=('close', 'last'),
    qty=('qty', 'sum'), usd=('usd', 'sum'), trades=('trades', 'sum'),
    first_ms=('first_ms', 'min'), last_ms=('last_ms', 'max'))
d['t'] = pd.to_datetime(d.bucket, unit='ms', utc=True).dt.tz_convert('Europe/Moscow')
d = d.set_index('t').sort_index()
end = pd.to_datetime(d[d.exchange == 'binance'].last_ms.max(), unit='ms', utc=True).tz_convert('Europe/Moscow').floor('5min')
d = d[d.index < end]
b = d[d.exchange == 'binance']
d.to_csv(p / 'bars-5m-clean.csv')
windows = {}
for name, start in [('48h', end - pd.Timedelta(hours=48)), ('overnight', pd.Timestamp('2026-09-06 21:00', tz='Europe/Moscow'))]:
    g = b[b.index >= start]
    windows[name] = dict(start=str(start), end_exclusive=str(end), bars=len(g),
        missing_bars=int((end-start).total_seconds()/300)-len(g), low=float(g.low.min()), high=float(g.high.max()),
        vwap=float(g.usd.sum()/g.qty.sum()), close=float(g.close.iloc[-1]),
        core_66_5_71_5_pct=float(g.close.between(66.5,71.5).mean()*100),
        core_69_71_7_pct=float(g.close.between(69,71.7).mean()*100))
coverage = dict(start=str(b.index.min()), end_exclusive=str(end), bars=len(b),
    missing_5m_bins=len(pd.date_range(b.index.min(), end, freq='5min', inclusive='left').difference(b.index)),
    populated_moscow_days=int(b.index.normalize().nunique()),
    largest_bar_interval=str(b.index.to_series().diff().max()))
comparison = {}
for ex in d.exchange.unique():
    g=d[(d.exchange==ex)&(d.index>=end-pd.Timedelta(hours=48))]
    comparison[ex]=dict(bars=len(g),low=float(g.low.min()),high=float(g.high.max()),vwap=float(g.usd.sum()/g.qty.sum()))
result=dict(coverage=coverage,windows=windows,exchanges_48h=comparison)
(p/'statistics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,1,figsize=(12,8),gridspec_kw={'height_ratios':[1,1.35]},layout='constrained')
fig.suptitle('DASH/USDT: новый диапазон после роста',fontsize=19,fontweight='bold',ha='left',x=.07)
overview=b[b.index>=pd.Timestamp('2026-08-19',tz='Europe/Moscow')].resample('1h').agg(close=('close','last'),low=('low','min'),high=('high','max'))
axes[0].fill_between(overview.index,overview.low,overview.high,color='#cad6e7',alpha=.6)
axes[0].plot(overview.index,overview.close,color='#354f78',linewidth=1.3)
axes[0].set_title('19 августа — 7 сентября · часовые свечи',loc='left',fontsize=11)
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%d.%m',tz=ZoneInfo('Europe/Moscow')))
axes[0].set_ylabel('USDT')
axes[0].grid(axis='y',alpha=.15)
g=b[b.index>=end-pd.Timedelta(hours=48)]
ax=axes[1]
ax.axhspan(66.5,71.5,color='#42a895',alpha=.17,label='Основная область: 66,5–71,5')
ax.fill_between(g.index,g.low,g.high,color='#8495ad',alpha=.4,label='Минимумы и максимумы 5 минут')
ax.plot(g.index,g.close,color='#243c5c',linewidth=1,label='Цена закрытия 5 минут')
ax.axhline(windows['48h']['vwap'],color='#278574',linewidth=1.2,linestyle='--',label='Средняя по объёму: 69,78')
ax.axhline(64.74,color='#b55e52',linestyle=':',linewidth=1)
ax.axhline(78.75,color='#b55e52',linestyle=':',linewidth=1)
ax.annotate('78,75',xy=(g.high.idxmax(),78.75),xytext=(8,4),textcoords='offset points',color='#965146')
ax.annotate('64,74',xy=(g.low.idxmin(),64.74),xytext=(8,-15),textcoords='offset points',color='#965146')
ax.set_title('Последние 48 часов · около 90% закрытий внутри зелёной области',loc='left',fontsize=11)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M',tz=ZoneInfo('Europe/Moscow')))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=8,tz=ZoneInfo('Europe/Moscow')))
ax.set_ylabel('USDT');ax.grid(axis='y',alpha=.15);ax.set_ylim(63.5,80.3)
ax.legend(loc='upper left',fontsize=9,frameon=False)
fig.supxlabel('Время московское. Срез 7 сентября 2026, 07:25. Источник: сделки Binance Futures.\nГраницы описывают наблюдавшееся движение и не гарантируют будущих разворотов.',fontsize=9,color='#5d6670')
fig.savefig(p/'dash-corridors.png',dpi=150)
