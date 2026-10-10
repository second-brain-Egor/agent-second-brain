#!/usr/bin/env python3
"""Текущий проект беседы: в него бот без вопросов кладёт новые документы и фото.

Запуск из корня проекта: uv run python scripts/project_context.py --scope <id> <команда>
  list                                   — проекты, недавние первыми, с подпроектами
  show                                   — текущий проект
  set "Проект" ["Подпроект"] [--create]  — перейти в проект (новую папку — только с --create)
  clear                                  — выйти из проекта: файлы снова с вопросом о папке
  move "<путь от vault>" ["Проект" ["Подпроект"]] — переложить файл; без проекта — во вложения
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from d_brain.config import get_settings
from d_brain.services.documents import DocumentStore, folder_label
from d_brain.services.session import SessionStore


def where(active: dict | None) -> str:
    if not active:
        return 'Проект не выбран.'
    return f"Текущий проект: {active['project']}" + (f" / {active['subproject']}" if active['subproject'] else '')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--scope', required=True, help='номер пользователя или chat_<id> группы')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    sub.add_parser('show')
    sub.add_parser('clear')
    choose = sub.add_parser('set')
    choose.add_argument('project')
    choose.add_argument('subproject', nargs='?')
    choose.add_argument('--create', action='store_true', help='создать папку, если её нет')
    move = sub.add_parser('move')
    move.add_argument('path')
    move.add_argument('project', nargs='?')
    move.add_argument('subproject', nargs='?')
    args = parser.parse_args()

    store = DocumentStore(get_settings().vault_path)
    if args.command == 'list':
        for name in store.projects():
            subprojects = store.subprojects(name)
            print(name + (f" — подпроекты: {', '.join(subprojects)}" if subprojects else ''))
        return 0
    if args.command == 'show':
        print(where(store.active_project(args.scope)))
        return 0
    if args.command == 'clear':
        store.clear_active(args.scope)
        print('Проект сброшен: новый документ бот снова спросит, куда положить.')
        return 0
    if args.command == 'set':
        project = store.existing_project(args.project)
        if not project and not args.create:
            print(f'Проекта «{args.project}» нет. Список: --scope … list; новый — с --create.', file=sys.stderr)
            return 1
        project = project or store.project_name(args.project)
        if args.subproject:
            known = {name.casefold(): name for name in store.subprojects(project)}
            subproject = known.get(args.subproject.strip().casefold())
            if not subproject and not args.create:
                print(f'В «{project}» нет подпроекта «{args.subproject}». Новый — с --create.', file=sys.stderr)
                return 1
            args.subproject = subproject or args.subproject
        active = store.set_active(args.scope, project, args.subproject)
        folder = store.active_folder(args.scope)
        folder.mkdir(parents=True, exist_ok=True)
        print(where(active))
        return 0
    moved = store.move(args.path, args.project, args.subproject)
    SessionStore(store.vault).append(args.scope, 'assistant', text=f'Переложил файл: {args.path} → {moved}')
    store.journal({'path': moved}, datetime.now(), action='помощник переложил')
    print(f'Переложил в {folder_label(moved)}: {moved}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
