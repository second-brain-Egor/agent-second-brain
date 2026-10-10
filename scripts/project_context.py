#!/usr/bin/env python3
"""Текущий проект беседы: в него бот без вопросов кладёт новые документы и фото.

Запуск из корня проекта: uv run python scripts/project_context.py --scope <id> <команда>
  list                                   — проекты, недавние первыми, с подпроектами
  show                                   — текущий проект
  set "Проект" ["Подпроект"] [--create]  — перейти в проект (новую папку — только с --create)
  clear                                  — выйти из проекта: файлы снова с вопросом о папке
  move "<путь от vault>" ["Проект" ["Подпроект"]] [--topic "Тема"] — переложить файл; без проекта —
                                         в общую папку (Фото, PDF или Документы), в ней — по теме
  place "<путь от vault>" ["Проект" ["Подпроект"]] [--topic "Тема"] [--create] — положить присланный
                                         файл или фото из входящих; без проекта — в общую папку по теме
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from d_brain.config import get_settings
from d_brain.services.documents import DocumentStore, folder_label, is_photo, note_placement
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
    move.add_argument('--topic', help='тема внутри общей папки, когда проекта нет')
    place = sub.add_parser('place')
    place.add_argument('path')
    place.add_argument('project', nargs='?')
    place.add_argument('subproject', nargs='?')
    place.add_argument('--topic', help='тема внутри общей папки, когда проекта нет')
    place.add_argument('--create', action='store_true', help='создать папку проекта или подпроекта, если её нет')
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
        # active_folder() is None until the folder exists, so build the path from the choice itself.
        folder = store.safe_path('projects/' + active['project']
                                 + ('/' + active['subproject'] if active['subproject'] else ''))
        folder.mkdir(parents=True, exist_ok=True)
        print(where(active))
        return 0
    if args.command == 'place':
        return place_incoming(store, args)
    moved = store.move(args.path, args.project, args.subproject, None if args.project else args.topic)
    SessionStore(store.vault).append(args.scope, 'assistant', text=f'Переложил файл: {args.path} → {moved}')
    store.journal({'path': moved}, datetime.now(), action='помощник переложил')
    print(f'Переложил в {folder_label(moved)}: {moved}')
    return 0


def place_incoming(store: DocumentStore, args) -> int:
    """Присланный файл, который бот оставил во входящих (Егор, 9 октября 2026: место выбирает помощник)."""
    doc = next((d for d in store.for_scope(args.scope) if args.path in (d['path'], d['id'])), None)
    if not doc:
        print(f'Среди присланных файлов этого чата нет «{args.path}».', file=sys.stderr)
        return 1
    if doc['state'] == 'ready':
        print(f"Файл уже лежит в {folder_label(doc['path'])}: {doc['path']}. Переложить — команда move.")
        return 0
    project, subproject = args.project, args.subproject
    if project:
        known = store.existing_project(project)
        if not known and not args.create:
            print(f'Проекта «{project}» нет. Список: --scope … list; новый — с --create.', file=sys.stderr)
            return 1
        project = known or store.project_name(project)
        if subproject:
            names = {name.casefold(): name for name in store.subprojects(project)}
            if subproject.strip().casefold() not in names and not args.create:
                print(f'В «{project}» нет подпроекта «{subproject}». Новый — с --create.', file=sys.stderr)
                return 1
            subproject = names.get(subproject.strip().casefold(), subproject)
    doc = store.place(doc['id'], project, subproject, None if project else args.topic)
    now = datetime.now()
    if is_photo(doc['name']):
        store.journal(doc, now)  # фото уже есть в дневнике дня, ссылку на него store.place поправил
    else:
        note_placement(store, doc, now)
    SessionStore(store.vault).append(args.scope, 'file', doc_id=doc['id'], path=doc['path'], name=doc['name'],
                                     caption=doc['instructions'], msg_id=doc['msg_id'], chat_id=doc['chat_id'])
    print(f"Положил в {folder_label(doc['path'])}: {doc['path']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
