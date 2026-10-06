#!/usr/bin/env python3
"""Перезапуск бота после ответа с проверкой и автоматическим откатом. Без нейросети.

Порядок: дождаться конца процесса ответа → дождаться записи о доставке ответа → дождаться,
пока бот закончит начатые задачи → перезапустить службу → убедиться, что бот снова принимает
сообщения и не падает. Если нет, вернуть файлы из резервных копий, убрать добавленную строку
из .env, перезапустить ещё раз и написать администратору.

Запускать от root отдельной службой (systemd-run), чтобы перезапуск не убил сам скрипт:
    systemd-run --unit=guarded-bot-restart --collect python3 scripts/guarded-bot-restart.py \
        --pid <pid ответа> --service d-brain-bot.service --project <каталог> \
        --revert <файл>=<копия> [--revert-env-line VPN_GUARD_ENABLED=1] [--failure-message 'Очередь не включилась']
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MARKERS = ('Voice message processed', 'Text message processed:')
TERMINAL = {'completed', 'error', 'stopped', 'limit', 'interrupted', 'superseded', 'delegated'}


def say(message):
    print(f'{datetime.now(ZoneInfo("Europe/Moscow")):%F %T} | {message}', flush=True)


def systemctl(*args, timeout=60):
    return subprocess.run(['systemctl', *args], capture_output=True, text=True, timeout=timeout)


def main_pid(service):
    return systemctl('show', service, '-p', 'MainPID', '--value').stdout.strip()


class Log:
    """Чтение только новых строк журнала бота."""

    def __init__(self, path):
        self.path = Path(path)
        self.offset = self.path.stat().st_size if self.path.exists() else 0

    def new(self):
        if not self.path.exists():
            return ''
        if self.path.stat().st_size < self.offset:
            self.offset = 0
        with self.path.open(errors='replace') as stream:
            stream.seek(self.offset)
            text = stream.read()
            self.offset = stream.tell()
        return text


def started(pid):
    try:
        return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]
    except (OSError, IndexError):
        return None


def wait_exit(pid, seconds):
    first = started(pid)
    end = time.monotonic() + seconds
    while first is not None and started(pid) == first:
        if time.monotonic() > end:
            return False
        time.sleep(0.25)
    return True


def wait_marker(log, seconds):
    seen = ''
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        seen += log.new()
        if any(marker in seen for marker in MARKERS):
            return True
        time.sleep(0.25)
    return False


def busy_tasks(project):
    """Незавершённые задачи бота этого проекта (их перезапуск оборвал бы)."""
    pending = []
    for path in (Path(project) / 'vault' / '.session' / 'tasks').glob('*.json'):
        try:
            entry = json.loads(path.read_text())
            cwd = (Path('/proc') / str(int(entry.get('owner_pid', 0))) / 'cwd').resolve(strict=True)
        except (OSError, ValueError):
            continue
        if cwd == Path(project).resolve() and entry.get('origin') == 'bot' and entry.get('state') not in TERMINAL:
            pending.append(path.stem)
    return pending


def wait_idle(project, seconds):
    end = time.monotonic() + seconds
    while busy_tasks(project):
        if time.monotonic() > end:
            return False
        time.sleep(0.5)
    return True


def healthy(service, log, before, seconds=60, settle=15):
    """Бот поднялся, начал приём сообщений и не падает."""
    seen = ''
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        seen += log.new()
        pid = main_pid(service)
        if 'Run polling for bot' in seen and systemctl('is-active', service).stdout.strip() == 'active' \
                and pid not in ('0', before):
            break
        time.sleep(0.5)
    else:
        return False, 'после перезапуска бот не начал принимать сообщения'
    time.sleep(settle)
    seen += log.new()
    if main_pid(service) != pid or systemctl('show', service, '-p', 'NRestarts', '--value').stdout.strip() not in ('', '0'):
        return False, 'бот перезапускается сам: он падает при старте'
    if 'Traceback' in seen:
        return False, 'в журнале бота после запуска есть ошибка (Traceback)'
    return True, ''


def notify(project, text, silent=False):
    """Отправляет сообщение администратору и записывает его в историю чата после подтверждённой доставки."""
    try:
        env = {}
        for line in (Path(project) / '.env').read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                key, _, value = line.partition('=')
                env[key.strip()] = value.strip().strip('"\'')
        chat = int(re.findall(r'\d+', env['ADMIN_USER_IDS'])[0])
        payload = {'chat_id': chat, 'text': text}
        if silent:
            payload['disable_notification'] = True
        request = urllib.request.Request(f'https://api.telegram.org/bot{env["TELEGRAM_BOT_TOKEN"]}/sendMessage',
                                         data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
        message_id = json.loads(urllib.request.urlopen(request, timeout=20).read())['result']['message_id']
    except Exception as error:  # токен в тексте ошибки не нужен
        say(f'уведомление не отправлено ({type(error).__name__})')
        return None
    entry = {'ts': datetime.now(ZoneInfo('Europe/Moscow')).isoformat(), 'type': 'assistant', 'text': text,
             'msg_id': message_id, 'chat_id': chat, 'chat_title': None, 'automatic': True,
             'source': 'guarded-bot-restart'}
    try:
        with (Path(project) / 'vault' / '.sessions' / f'{chat}.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except OSError as error:
        say(f'сообщение отправлено, но не записано в историю ({type(error).__name__})')
    say(f'уведомление отправлено (сообщение {message_id})')
    return message_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--service', required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--log-file', type=Path)
    parser.add_argument('--revert', action='append', default=[], metavar='ФАЙЛ=КОПИЯ')
    parser.add_argument('--revert-env-line', action='append', default=[])
    parser.add_argument('--no-notify', action='store_true')
    parser.add_argument('--success-message')
    parser.add_argument('--failure-message', default='Меню VPN не включилось',
                        help='что не включилось; после двоеточия добавляется причина')
    parser.add_argument('--wait-delivery', type=int, default=180)
    parser.add_argument('--wait-idle', type=int, default=1800)
    parser.add_argument('--health-timeout', type=int, default=60)
    parser.add_argument('--settle', type=int, default=15)
    args = parser.parse_args()
    project = args.project
    log = Log(args.log_file or project / 'logs' / 'bot.log')
    before = main_pid(args.service)

    say(f'жду завершения процесса ответа {args.pid}')
    if not wait_exit(args.pid, 1800):
        say('процесс ответа не завершился за 30 минут — перезапуск отменён')
        return 1
    if not wait_marker(log, args.wait_delivery):
        say('доставка ответа в журнале не подтверждена — перезапускаю всё равно, код нужно развернуть')
    if not wait_idle(project, args.wait_idle):
        say('бот остаётся занят задачами — перезапуск отменён')
        return 1

    log.new()
    say(f'перезапускаю {args.service}')
    systemctl('restart', args.service, timeout=90)
    ok, reason = healthy(args.service, log, before, args.health_timeout, args.settle)
    if ok:
        say('бот поднялся и принимает сообщения: развёртывание завершено')
        if args.success_message and not args.no_notify:
            notify(project, args.success_message)
        return 0

    say(f'НЕУДАЧА: {reason}. Возвращаю прежнее состояние')
    for pair in args.revert:
        target, _, backup = pair.partition('=')
        shutil.copy2(backup, target)
        say(f'возвращён файл {target}')
    env_path = project / '.env'
    if args.revert_env_line and env_path.exists():
        lines = [line for line in env_path.read_text().splitlines() if line.strip() not in args.revert_env_line]
        env_path.write_text('\n'.join(lines) + '\n')
        say('из .env убрана добавленная строка')
    before = main_pid(args.service)
    log.new()
    systemctl('restart', args.service, timeout=90)
    ok_after, reason_after = healthy(args.service, log, before, args.health_timeout, args.settle)
    say('после отката бот работает' if ok_after else f'ПОСЛЕ ОТКАТА бот тоже не поднялся: {reason_after}')
    if not args.no_notify:
        notify(project, f'⚠️ {args.failure_message}: ' + reason + '. Вернул прежний код бота, '
               + ('бот работает как раньше.' if ok_after else 'но бот не поднялся — нужен вход на сервер.'))
    return 2


if __name__ == '__main__':
    sys.exit(main())
