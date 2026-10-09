import json, subprocess, datetime as dt, time, statistics as st
from collections import defaultdict
MSK=dt.timezone(dt.timedelta(hours=3))
L=json.load(open(".tmp/bybit-events/events.json"))
def api(params):
    q="&".join(f"{k}={v}" for k,v in params.items())
    out=subprocess.run(["env","-u","http_proxy","-u","https_proxy","curl","-s","--max-time","20",f"https://api.bybit.com/v5/market/kline?{q}"],capture_output=True,text=True).stdout
    for i in range(5):
        try:
            d=json.loads(out)
            if d.get("retCode")==0 and "list" in d.get("result",{}): return d
        except Exception: d=out[:200]
        time.sleep(2+i*2)
        out=subprocess.run(["env","-u","http_proxy","-u","https_proxy","curl","-s","--max-time","20",f"https://api.bybit.com/v5/market/kline?{q}"],capture_output=True,text=True).stdout
    raise SystemExit(f"API fail {q}: {d}")
groups=defaultdict(list)
for x in L: groups[int(x["eventTime"])].append(x)
now=int(time.time()*1000)
res={}
for t in sorted(groups):
    if t > now - 3600_000: continue
    r=api(dict(category="linear",symbol="DASHUSDT",interval=5,start=t-5*60_000,end=t+60*60_000,limit=20))
    k=sorted(r["result"]["list"], key=lambda c:int(c[0]))
    k=[c for c in k if t-5*60_000<=int(c[0])<t+60*60_000]
    if len(k)<10: res[t]=None; continue
    pre=float(k[0][4])  # close of candle before release
    after=[c for c in k if int(c[0])>=t]
    hi=max(float(c[2]) for c in after); lo=min(float(c[3]) for c in after); cl=float(after[-1][4])
    first=[c for c in after if int(c[0])<t+15*60_000]
    hi15=max(float(c[2]) for c in first); lo15=min(float(c[3]) for c in first)
    res[t]=dict(pre=pre,up=(hi/pre-1)*100,down=(lo/pre-1)*100,close=(cl/pre-1)*100,range=(hi-lo)/pre*100,range15=(hi15-lo15)/pre*100)
    time.sleep(0.12)
json.dump({str(k):v for k,v in res.items()}, open(".tmp/bybit-events/reaction.json","w"), indent=1)
# baseline: hourly candles over the same period
start=min(groups); rng=[]; s=start
while s<now:
    r=api(dict(category="linear",symbol="DASHUSDT",interval=60,start=s,end=min(s+999*3600_000,now),limit=1000))
    for c in r["result"]["list"]:
        o,h,l=float(c[1]),float(c[2]),float(c[3]); rng.append((h-l)/o*100)
    s+=1000*3600_000; time.sleep(0.12)
print("baseline hourly range median %.2f%%  p75 %.2f%%  n=%d"%(st.median(rng), sorted(rng)[int(len(rng)*.75)], len(rng)))
ev=[v["range"] for v in res.values() if v]; print("event 60m range median %.2f%% n=%d"%(st.median(ev),len(ev)))
bytype=defaultdict(list)
for t,v in res.items():
    if not v: continue
    for en in {x["enTitle"] for x in groups[t]}: bytype[en].append(v["range"])
for en,a in sorted(bytype.items(), key=lambda kv:-st.median(kv[1])): print("%-30s n=%2d median %.2f%% max %.2f%%"%(en,len(a),st.median(a),max(a)))
print("missing", [dt.datetime.fromtimestamp(t/1000,MSK).isoformat() for t,v in res.items() if v is None])
