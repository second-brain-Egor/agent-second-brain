#!/usr/bin/env python3
"""Finish a bot deployment after its current CLI response; no model polling."""
import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pid', required=True, type=int)
    parser.add_argument('--service', required=True, choices=['d-brain-bot.service', 'd-brain-bot-irina.service'])
    parser.add_argument('--project', required=True, type=Path)
    args = parser.parse_args()
    journal = args.project / 'logs' / 'request-guardrails-restart.json'
    log = args.project / 'logs' / 'bot.log'
    offset = log.stat().st_size if log.exists() else 0
    state = dict(state='waiting_for_response', pid=args.pid, service=args.service)

    def record(**values):
        state.update(values, updated=datetime.now(timezone.utc).isoformat())
        temporary = journal.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n')
        temporary.replace(journal)

    def read_new():
        nonlocal offset
        if not log.exists():
            return ''
        if log.stat().st_size < offset:
            offset = 0
        with log.open() as stream:
            stream.seek(offset)
            text = stream.read()
            offset = stream.tell()
        return text

    def main_pid():
        return subprocess.check_output(['systemctl','show',args.service,'-p','MainPID','--value'],text=True).strip()

    def process_start():
        try:
            return Path(f'/proc/{args.pid}/stat').read_text().rsplit(')',1)[1].split()[19]
        except (OSError, IndexError):
            return None

    record(previous_pid=main_pid())
    initial_start = process_start()
    until = time.monotonic()+1800
    recent = ''
    while initial_start is not None and process_start() == initial_start:
        if time.monotonic() >= until:
            record(state='error', error='Текущий ответ не завершился; перезапуск не выполнялся.')
            return 1
        recent = read_new()
        time.sleep(.25)
    # Handler completion is logged after Telegram delivery, not just CLI exit.
    until = time.monotonic()+30
    while not any(marker in recent for marker in ('Voice message processed', 'Text message processed:')):
        if time.monotonic() >= until:
            record(state='error', error='Доставка текущего ответа не подтверждена; перезапуск не выполнялся.')
            return 1
        recent = read_new()
        time.sleep(.25)
    # Let queued messages finish before restarting the process that owns them.
    from d_brain.services.execution import TERMINAL
    tasks_directory = args.project / 'vault' / '.session' / 'tasks'
    until = time.monotonic()+1800
    while True:
        pending = []
        for path in tasks_directory.glob('*.json'):
            try:
                entry = json.loads(path.read_text())
            except (OSError, ValueError):
                record(state='error', error='Не удалось проверить очередь; перезапуск не выполнялся.')
                return 1
            try:
                owner_project = (Path('/proc') / str(int(entry.get('owner_pid', 0))) / 'cwd').resolve(strict=True)
            except (OSError, ValueError):
                continue
            if (owner_project == args.project.resolve()
                    and entry.get('origin') == 'bot'
                    and entry.get('state') not in TERMINAL):
                pending.append(path.stem)
        if not pending:
            break
        if time.monotonic() >= until:
            record(state='error', error='Очередь ещё занята; перезапуск не выполнялся.', pending=pending)
            return 1
        record(state='waiting_for_queue', pending=pending)
        time.sleep(.5)
    record(state='restarting', pending=[])
    read_new()
    subprocess.run(['systemctl','restart',args.service],check=True,timeout=45)
    until = time.monotonic()+45
    polling = False
    while time.monotonic() < until:
        polling = polling or 'Run polling for bot' in read_new()
        active = subprocess.run(['systemctl','is-active','--quiet',args.service]).returncode == 0
        pid = main_pid()
        if polling and active and pid != state['previous_pid'] and pid != '0':
            record(state='completed', current_pid=pid, polling=True)
            return 0
        time.sleep(.5)
    record(state='error', error='После перезапуска не подтверждён приём сообщений.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
