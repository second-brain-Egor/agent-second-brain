import re, sys, json
from pathlib import Path
vault = Path('vault')
files = sorted(p for p in (vault/'attachments').rglob('*') if p.is_file() and p.name != '.gitkeep')
mds = [p for p in vault.rglob('*.md') if '.git' not in p.parts and 'attachments' not in p.parts]
mds += [p for p in vault.rglob('*.jsonl')]
texts = {}
for p in mds:
    try: texts[p] = p.read_text(encoding='utf-8')
    except Exception: pass
out = {}
for f in files:
    rel = f.relative_to(vault).as_posix()
    refs = []
    for p, t in texts.items():
        if rel in t:
            refs.append(p.relative_to(vault).as_posix())
    # context from daily note
    ctx = ''
    for p in refs:
        if p.startswith('daily/'):
            t = texts[vault/p]; i = t.find(rel)
            ctx = t[max(0,i-200): i+700].replace('\n',' ')
            break
    out[rel] = {'refs': refs, 'ctx': ctx}
json.dump(out, open('tmp/photo-sort/refs.json','w'), ensure_ascii=False, indent=1)
for k,v in out.items():
    print('=====', k); print('REFS:', v['refs']); print(v['ctx'][:900])
