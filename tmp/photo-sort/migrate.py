"""Разовый перенос вложений по датам в проекты и общую папку «Фото» (Егор, 10 октября 2026)."""
import json, os, re, shutil, sys
from pathlib import Path

vault = Path('vault').resolve()
P = 'projects/'
plan = {
    P + 'server-backup-and-migration': ['2026-03-29/*'],
    'Фото/Компьютер и сеть': ['2026-04-08/img-224628.jpg', '2026-04-09/*', '2026-04-23/*',
                              '2026-06-17/img-181534.jpg', '2026-06-21/*', '2026-07-11/*'],
    P + 'second-brain-bot-operations': ['2026-04-08/img-231319.jpg', '2026-04-11/*', '2026-04-13/*',
                                        '2026-05-07/*', '2026-05-08/*', '2026-05-09/*', '2026-09-25/*'],
    P + 'shiporezny-stanok-selection': ['2026-04-14/*'],
    P + 'Рынок стройматериалы': ['2026-04-26/*'],
    'Фото/Цены и товары': ['2026-04-29/*', '2026-06-17/img-172109.jpg'],
    'Фото/Личное': ['2026-05-10/*', '2026-05-11/*'],
    P + 'timberframe': ['2026-05-14/*'],
    P + 'timberframe-workshop-setup': ['2026-09-06/*'],
    P + 'Подключение': ['2026-05-15/*', '2026-09-12/*'],
    P + 'dacha': ['2026-05-17/*', '2026-05-26/*', '2026-06-01/*', '2026-06-25/*', '2026-06-29/*',
                  '2026-06-30/*', '2026-07-03/*'],
    'Фото/Карты участков': ['2026-06-11/*'],
    'Фото/Трубная ферма': ['2026-08-21/*'],
    P + 'Сварочник': ['2026-10-07/*'],
}
att = vault / 'attachments'
moves = {}
for folder, patterns in plan.items():
    for pattern in patterns:
        for src in sorted(att.glob(pattern)):
            if not src.is_file():
                continue
            m = re.fullmatch(r'img-(\d\d)(\d\d)(\d\d)(?:-(\d+))?\.(\w+)', src.name)
            if m:
                day = src.parent.name
                name = f'фото {day} {m[1]}-{m[2]}-{m[3]}' + (f' ({m[4]})' if m[4] else '') + '.' + m[5]
            else:
                name = src.name
            old = src.relative_to(vault).as_posix()
            assert old not in moves, old
            moves[old] = f'{folder}/{name}'
left = [p.relative_to(vault).as_posix() for p in att.rglob('*') if p.is_file() and p.name != '.gitkeep'
        and p.relative_to(vault).as_posix() not in moves]
assert not left, left
assert len(set(moves.values())) == len(moves)
for new in moves.values():
    assert not (vault / new).exists(), new
print(len(moves), 'files')
if '--run' not in sys.argv:
    for a, b in moves.items():
        print(a, '->', b)
    raise SystemExit

# 1. Files
for old, new in moves.items():
    (vault / new).parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(vault / old), str(vault / new))

# 2. Links: notes and the conversation journal (not .git, not backups)
def text_files():
    for folder, subs, files in os.walk(vault):
        subs[:] = [s for s in subs if s not in ('.git', '.obsidian', '.trash')]
        for f in files:
            if f.endswith(('.md', '.jsonl')):
                yield Path(folder) / f

changed = {}
for path in text_files():
    for _ in range(5):
        try:
            before = path.stat().st_size
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            break
        new_text = text
        for old, new in moves.items():
            new_text = new_text.replace(old, new)
        if new_text == text:
            break
        tmp = path.with_name(path.name + '.relink-tmp')
        tmp.write_text(new_text, encoding='utf-8')
        shutil.copymode(path, tmp)
        if path.stat().st_size != before:  # бот дописал строку, пока меняли — заново
            tmp.unlink()
            continue
        os.replace(tmp, path)
        changed[path.relative_to(vault).as_posix()] = sum(text.count(o) for o in moves)
        break
for p, n in sorted(changed.items()):
    print(f'{n:3} {p}')

# 3. Empty date folders
for d in sorted(att.iterdir()):
    if d.is_dir() and not any(d.iterdir()):
        d.rmdir()
json.dump(moves, open('tmp/photo-sort/moves.json', 'w'), ensure_ascii=False, indent=1)
