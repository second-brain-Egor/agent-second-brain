import json, subprocess, datetime as dt, time
URL="https://www.bybitglobal.com/x-api/de/cht/market-index/trading-data/v1/calendar/kline-us-event"
def get(a,b,lang):
    cmd=["env","-u","http_proxy","-u","https_proxy","-u","HTTP_PROXY","-u","HTTPS_PROXY","curl","-s","--max-time","30","-X","POST",
         "-H","Content-Type: application/json","-H",f"lang: {lang}","-H",f"accept-language: {lang}","-H","platform: pc",
         "-A","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36",
         "-H","Origin: https://www.bybitglobal.com","-H","Referer: https://www.bybitglobal.com/ru-RU/trade/usdt/DASHUSDT",
         "-d",json.dumps({"from":str(a),"to":str(b)}),URL]
    return json.loads(subprocess.run(cmd,capture_output=True,text=True).stdout)
DAY=86400000
start=int(dt.datetime(2018,1,1,tzinfo=dt.timezone.utc).timestamp()*1000)
end=int(dt.datetime(2027,12,31,tzinfo=dt.timezone.utc).timestamp()*1000)
ev={}
a=start
while a<end:
    b=min(a+360*DAY,end)
    r=get(a,b,"ru-RU")
    if r.get("ret_code")!=0: print("ERR",a,r); break
    for x in r["result"]["list"]: ev[x["eventId"]]=x
    print(dt.datetime.utcfromtimestamp(a/1000).date(), len(r["result"]["list"]))
    a=b; time.sleep(0.5)
L=sorted(ev.values(), key=lambda x:int(x["eventTime"]))
json.dump(L, open(".tmp/bybit-events/events.json","w"), ensure_ascii=False, indent=1)
print("total", len(L))
