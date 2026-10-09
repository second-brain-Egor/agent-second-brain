import sys, json, re
sys.path.insert(0, '.')
from direct_web.network import ensure_direct_process, direct_env
ensure_direct_process()
from direct_web.browser import _profile_lock, PROFILE_DIR, USER_AGENT
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "https://www.bybit.com/trade/usdt/DASHUSDT"
reqs = []
with _profile_lock():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(user_data_dir=PROFILE_DIR, headless=True, locale="ru-RU",
            timezone_id="Europe/Moscow", user_agent=USER_AGENT, env=direct_env(), viewport={"width":1600,"height":1000},
            args=["--no-first-run","--disable-dev-shm-usage","--disable-blink-features=AutomationControlled","--proxy-server=direct://","--proxy-bypass-list=*"])
        page = ctx.new_page()
        def on_resp(r):
            u = r.url
            if r.request.resource_type in ("xhr","fetch"):
                reqs.append((r.status, u))
        page.on("response", on_resp)
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(25000)
        page.screenshot(path=".tmp/bybit-events/shot.png")
        ctx.close()
for s,u in reqs:
    print(s, u[:250])
