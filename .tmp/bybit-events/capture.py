import sys, json
sys.path.insert(0, '.')
from direct_web.network import ensure_direct_process, direct_env
ensure_direct_process()
from direct_web.browser import _profile_lock, PROFILE_DIR, USER_AGENT
from playwright.sync_api import sync_playwright

url = "https://www.bybitglobal.com/trade/usdt/DASHUSDT"
out = []
with _profile_lock():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(user_data_dir=PROFILE_DIR, headless=True, locale="ru-RU",
            timezone_id="Europe/Moscow", user_agent=USER_AGENT, env=direct_env(), viewport={"width":1600,"height":1000},
            args=["--no-first-run","--disable-dev-shm-usage","--disable-blink-features=AutomationControlled","--proxy-server=direct://","--proxy-bypass-list=*"])
        page = ctx.new_page()
        def on_resp(r):
            u = r.url
            if any(k in u for k in ("event", "calendar", "news", "mark")) and "kline/mark" not in u and "sa.gif" not in u:
                try:
                    body = r.text()
                except Exception as e:
                    body = f"<err {e}>"
                out.append({"url": u, "method": r.request.method, "post": r.request.post_data, "headers": {k:v for k,v in r.request.headers.items() if k.lower() not in ("cookie",)}, "status": r.status, "body": body})
        page.on("response", on_resp)
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(20000)
        ctx.close()
json.dump(out, open(".tmp/bybit-events/capture.json","w"), ensure_ascii=False, indent=1)
for o in out:
    print(o["method"], o["status"], o["url"][:200]); print("POST:", o["post"]); print("BODY:", o["body"][:1500]); print()
