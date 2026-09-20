#!/usr/bin/env python3
"""Two-way synchronization of reviewed shared files; never delete either side."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def plan_sync(left: Path, right: Path, baseline: dict[str, str]):
    changes = []
    conflicts = []
    for name, previous in sorted(baseline.items()):
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"Недопустимый путь: {name}")
        a, b = left / rel, right / rel
        for path, root in [(a, left), (b, right)]:
            if not path.resolve().is_relative_to(root.resolve()):
                raise ValueError(f"Путь выходит за пределы экземпляра: {name}")
        ah, bh = digest(a), digest(b)
        if ah == bh:
            continue
        if ah is None:
            changes.append((b, a))
        elif bh is None:
            changes.append((a, b))
        elif ah == previous:
            changes.append((b, a))
        elif bh == previous:
            changes.append((a, b))
        else:
            conflicts.append(name)
    return changes, conflicts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", type=Path, default=Path("/home/egor/agent-second-brain"))
    parser.add_argument("--right", type=Path, default=Path("/home/irina/agent-second-brain"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    manifest = "assistant-sync-manifest.json"
    left_manifest = json.loads((args.left / manifest).read_text())
    right_manifest = json.loads((args.right / manifest).read_text())
    if left_manifest != right_manifest:
        raise SystemExit("Реестры расходятся: сначала требуется ручная сверка.")
    changes, conflicts = plan_sync(args.left, args.right, left_manifest["files"])
    if conflicts:
        print("Изменения с обеих сторон требуют объединения; ничего не записано:")
        print("\n".join(conflicts))
        return 2
    for src, dst in changes:
        print(f"{src} → {dst}")
    if not args.apply:
        print(f"Проверка: {len(changes)} переносов, удалений нет. Для применения: --apply")
        return 0
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    for src, dst in changes:
        root = args.left if dst.is_relative_to(args.left) else args.right
        owner = root.stat()
        if dst.exists():
            backup = root / "logs" / "assistant-sync-backups" / stamp / dst.relative_to(root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup)
        missing = []
        parent = dst.parent
        while not parent.exists():
            missing.append(parent)
            parent = parent.parent
        dst.parent.mkdir(parents=True, exist_ok=True)
        for parent in reversed(missing):
            if os.geteuid() == 0:
                os.chown(parent, owner.st_uid, owner.st_gid)
        tmp = dst.with_name(dst.name + ".sync-tmp")
        shutil.copy2(src, tmp)
        if os.geteuid() == 0:
            os.chown(tmp, owner.st_uid, owner.st_gid)
        tmp.replace(dst)
    for name in left_manifest["files"]:
        current = digest(args.left / name)
        if current is not None:
            left_manifest["files"][name] = current
    for root in [args.left, args.right]:
        (root / manifest).write_text(json.dumps(left_manifest, ensure_ascii=False, indent=2) + "\n")
    print("Синхронизация завершена. Службы автоматически не перезапускаются.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
