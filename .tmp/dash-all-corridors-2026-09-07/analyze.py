"""Descriptive DASH price ranges; no prediction or trading actions."""
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SRC = Path('.tmp/dash-corridors-2026-09-07')
OUT = Path('.tmp/dash-all-corridors-2026-09-07')
TZ = 'Europe/Moscow'
now = pd.Timestamp(json.loads((SRC / 'futures-latest-5m-fetch.json').read_text())['started_utc'])
raw = pd.read_csv(SRC / 'bars-5m-clean.csv')
b = raw[raw.exchange == 'binance'].copy()
b.index = pd.to_datetime(b.t, utc=True).dt.tz_convert(TZ)
rows = json.loads((SRC / 'futures-latest-5m.json').read_text())
new = pd.DataFrame(rows, columns=['bucket', 'open', 'high', 'low', 'close', 'qty', 'end', 'usd', 'trades', 'taker_qty', 'taker_usd', 'ignore'])
new = new[new.end < now.timestamp() * 1000].copy()
new.index = pd.to_datetime(new.bucket, unit='ms', utc=True).dt.tz_convert(TZ)
for c in ['open', 'high', 'low', 'close', 'qty', 'usd']:
    new[c] = new[c].astype(float)
# Prefer official completed candles in the overlapping refresh interval.
b = pd.concat([b[~b.index.isin(new.index)], new]).sort_index()
assert b.index.is_unique and b.index.is_monotonic_increasing
end = b.index[-1] + pd.Timedelta(minutes=5)
b[['open', 'high', 'low', 'close', 'qty', 'usd']].to_csv(OUT / 'binance-5m.csv')

def ts(s):
    return pd.Timestamp(s, tz=TZ)

def stats(start, stop, lo=None, hi=None):
    g = b[(b.index >= ts(start)) & (b.index < ts(stop))]
    assert len(g)
    # Boundary touches must alternate across the inner 20% edge zones.
    crosses, previous = 0, None
    if lo is not None:
        for _, contiguous in g.groupby(g.index.to_series().diff().gt(pd.Timedelta(minutes=5)).cumsum()):
            previous = None
            for value in contiguous.close:
                side = 'L' if value <= lo + .2 * (hi-lo) else ('H' if value >= hi - .2 * (hi-lo) else None)
                if side is not None:
                    if previous is not None and previous != side:
                        crosses += 1
                    previous = side
    return dict(start=start, stop_exclusive=stop, bars=len(g),
                coverage_pct=100*len(g)/((ts(stop)-ts(start)).total_seconds()/300),
                q05=float(g.close.quantile(.05)), q95=float(g.close.quantile(.95)),
                low=float(g.low.min()), high=float(g.high.max()),
                within_pct=None if lo is None else float(100*g.close.between(lo, hi).mean()),
                alternating_edge_visits=None if lo is None else crosses)

# Selected, explicitly dated consolidation episodes, assessed retrospectively.
# These are descriptive choices, not an automatic proof of support/resistance.
groups = [
    ('29,5–32',29.5,32,[('2026-07-28','2026-08-20')]),
    ('32–33,5',32,33.5,[('2026-06-28','2026-07-02'),('2026-07-24','2026-07-28')]),
    ('33–35,5',33,35.5,[('2026-07-08','2026-07-24')]),
    ('34–38,5',34,38.5,[('2026-04-19','2026-05-04'),('2026-06-07','2026-06-25'),('2026-07-03','2026-07-08')]),
    ('37,5–41',37.5,41,[('2026-05-28','2026-06-04'),('2026-08-26','2026-08-30')]),
    ('40–43,5',40,43.5,[('2026-05-16','2026-05-20'),('2026-08-23','2026-08-26'),('2026-08-30','2026-08-31'),('2026-09-02','2026-09-03 19:00')]),
    ('43–47,5',43,47.5,[('2026-05-11','2026-05-16'),('2026-05-23','2026-05-28')]),
    ('45–49,5',45,49.5,[('2026-05-04 12:00','2026-05-06')]),
    ('47,5–53',47.5,53,[('2026-05-07','2026-05-11'),('2026-05-21','2026-05-23')]),
    ('66,5–71,5',66.5,71.5,[('2026-09-05 07:25',end.strftime('%Y-%m-%d %H:%M'))]),
]
result=[]
for label,lo,hi,windows in groups:
    episodes=[stats(a,z,lo,hi) for a,z in windows]
    n=sum(x['bars'] for x in episodes)
    result.append(dict(range=label,lo=lo,hi=hi,episodes=episodes,
                       within_pct=sum(x['within_pct']*x['bars'] for x in episodes)/n))
local = [
    dict(range='69–71,7',lo=69,hi=71.7,**stats('2026-09-06 21:00','2026-09-07 08:00',69,71.7)),
    dict(range='67–69',lo=67,hi=69,**stats('2026-09-07 09:00',end.strftime('%Y-%m-%d %H:%M'),67,69)),
]
historical = json.loads((SRC / 'daily-history.json').read_text())
h = pd.DataFrame(historical,columns=['bucket','open','high','low','close','qty','end','usd','trades','a','z','c'])
h=h[h.end < now.timestamp()*1000].copy()
h.index=pd.to_datetime(h.bucket,unit='ms',utc=True)
for c in ['open','high','low','close']: h[c]=h[c].astype(float)
h.resample('MS').agg(low=('low','min'),close_q05=('close',lambda s:s.quantile(.05)),close_median=('close','median'),close_q95=('close',lambda s:s.quantile(.95)),high=('high','max')).to_csv(OUT/'historical-monthly-distributions.csv')
summary=dict(cutoff_moscow=str(end),last_close=float(b.close.iloc[-1]),ranges=result,local=local,
             historical_context=dict(start=str(h.index.min()),end=str(h.index.max()),bars=len(h),low=float(h.low.min()),high=float(h.high.max())))
(OUT/'statistics.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
for r in result:
    print(r['range'],round(r['within_pct'],1),[(x['start'],x['stop_exclusive'],round(x['within_pct'],1),x['alternating_edge_visits']) for x in r['episodes']])
print('LOCAL',local)
print('CUTOFF',str(end),'CLOSE',b.close.iloc[-1])

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,1,figsize=(14,10),layout='constrained',gridspec_kw={'height_ratios':[1.15,1]})
fig.suptitle('DASH/USDT · карта наблюдавшихся коридоров',fontsize=19,fontweight='bold',ha='left',x=.05)
overview=b.resample('1h').agg(close=('close','last'),low=('low','min'),high=('high','max'))
axs[0].fill_between(overview.index,overview.low,overview.high,color='#bac7db',alpha=.45)
axs[0].plot(overview.index,overview.close,color='#263b58',lw=.8)
colors=plt.get_cmap('tab10').colors
for idx,(label,lo,hi,windows) in enumerate(groups):
    for a,z in windows:
        x0,x1=mdates.date2num(ts(a)),mdates.date2num(ts(z))
        axs[0].add_patch(plt.Rectangle((x0,lo),x1-x0,hi-lo,facecolor=colors[idx],edgecolor=colors[idx],alpha=.2,lw=.8))
    axs[0].text(1.007,(lo+hi)/2,label,transform=axs[0].get_yaxis_transform(),color=colors[idx],va='center',fontsize=9)
axs[0].set_title('Апрель — сентябрь 2026 · цветные прямоугольники действуют только в отмеченные периоды',loc='left',fontsize=10)
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%d.%m',tz=ZoneInfo(TZ)))
axs[0].set_ylim(26,82)
recent=b[b.index>=ts('2026-09-04')]
ax=axs[1]
ax.fill_between(recent.index,recent.low,recent.high,color='#adbcd0',alpha=.5)
ax.plot(recent.index,recent.close,color='#263b58',lw=.9)
for label,lo,hi,start,stop,color in [
    ('Общий: 66,5–71,5',66.5,71.5,'2026-09-05 07:25',end.strftime('%Y-%m-%d %H:%M'),'#239980'),
    ('Ночной: 69–71,7',69,71.7,'2026-09-06 21:00','2026-09-07 08:00','#cb962b'),
    ('Дневной: 67–69',67,69,'2026-09-07 09:00',end.strftime('%Y-%m-%d %H:%M'),'#6167ce')]:
    a,z=mdates.date2num(ts(start)),mdates.date2num(ts(stop))
    ax.add_patch(plt.Rectangle((a,lo),z-a,hi-lo,facecolor=color,edgecolor=color,alpha=.27,label=label))
ax.axhline(78.75,color='#b36b62',ls=':',lw=1)
ax.text(.015,78.95,'78,75 — крайний выброс',transform=ax.get_yaxis_transform(),color='#9e5148',fontsize=9)
ax.annotate(f'{b.close.iloc[-1]:.2f}'.replace('.',','),(b.index[-1],b.close.iloc[-1]),xytext=(8,-12),textcoords='offset points',fontweight='bold')
ax.set_title('4–7 сентября · рост, широкий диапазон и смена локального коридора',loc='left',fontsize=10)
ax.legend(loc='lower right',frameon=False,fontsize=9)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12,tz=ZoneInfo(TZ)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M',tz=ZoneInfo(TZ)))
for ax in axs:
    ax.set_ylabel('USDT'); ax.grid(axis='y',alpha=.15)
fig.supxlabel(f'Срез: {end:%d.%m.%Y %H:%M} МСК. Binance Futures, завершённые свечи 5 минут.\nОкруглённые описательные диапазоны. Старые коридоры не означают действующих сейчас границ.',fontsize=9,color='#596371')
fig.savefig(OUT/'dash-all-corridors.png',dpi=160)
