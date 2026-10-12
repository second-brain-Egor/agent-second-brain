import json, subprocess, concurrent.futures
from pathlib import Path
from datetime import datetime, timezone
V=Path('vault/projects/Nate Herk/videos/001-i-tried-100-github-repos-for-claude-these-6-are-the-best')
rows=[]
part=V.joinpath('description.md').read_text().split('The repos:\n',1)[1].split('\nMy Tools',1)[0]
for line in part.strip().splitlines():
    name,url=line.split(': ',1);rows.append((name,url))
def fetch(row):
    name,url=row
    p=subprocess.run(['/home/egor/.local/bin/uv','run','python','scripts/web_fetch.py',url,'--max-chars','25000'],text=True,capture_output=True,timeout=150)
    return {'name':name,'url':url,'exit_code':p.returncode,'text':p.stdout,'error':p.stderr,'checked_at':datetime.now(timezone.utc).isoformat()}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    for f in concurrent.futures.as_completed([ex.submit(fetch,row) for row in rows]):
        try: results.append(f.result())
        except Exception as exc: results.append({'error':str(exc)})
        V.joinpath('внешние-источники.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:v for k,v in results[-1].items() if k!='text'},ensure_ascii=False),flush=True)
