import concurrent.futures
import datetime as dt
import json
from pathlib import Path
import subprocess

out = Path('.tmp/dash-corridors-2026-09-07')
first = json.loads((out / 'history-first.json').read_text())
step = 200 * 86400000
now = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
starts = range(first[-1][0] + 86400000, now, step)

def fetch(start):
    url = f'https://api.binance.com/api/v3/klines?symbol=DASHUSDT&interval=1d&limit=200&startTime={start}'
    proc = subprocess.run(['uv', 'run', 'python', 'scripts/web_fetch.py', url, '--max-chars', '50000'], capture_output=True, text=True, timeout=90, check=True)
    rows = json.loads(proc.stdout)
    assert isinstance(rows, list) and rows and isinstance(rows[0], list), rows
    (out / f'daily-{start}.json').write_text(proc.stdout)
    print(f'{dt.datetime.fromtimestamp(start / 1000, dt.timezone.utc).date()}: {len(rows)}', flush=True)
    return rows

rows = list(first)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for part in pool.map(fetch, starts):
        rows.extend(part)
rows = sorted({r[0]: r for r in rows}.values())
(out / 'daily-history.json').write_text(json.dumps(rows))
print(f'Total daily candles: {len(rows)}', flush=True)
