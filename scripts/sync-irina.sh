#!/bin/bash
# Перенос КОДА бота из инстанса egor в инстанс irina + рестарт её сервиса.
# Переносится только код: src/, scripts/, pyproject.toml, uv.lock.
# НЕ трогаются её данные и личность: vault/, .env, CLAUDE.md, GLOBAL_RULES.md, Скиллы/.
#
# ВНИМАНИЕ (2026-06-11): копия Ирины отстала от egor на ~5 недель (54 файла,
# у неё нет claude_model.py и майских правок). Первый прогон — осознанно:
# после него проверить её бота (отправить сообщение) и хвост её logs/bot.log.
# Откат: бэкап её src/ кладётся рядом, см. вывод скрипта.
set -euo pipefail

SRC=/home/egor/agent-second-brain
DST=/home/irina/agent-second-brain
STAMP=$(date +%Y%m%d-%H%M%S)

[ -d "$DST/src" ] || { echo "Не найден $DST/src"; exit 1; }

echo "Бэкап её кода → $DST/src.bak-$STAMP"
sudo cp -a "$DST/src" "$DST/src.bak-$STAMP"

echo "Переношу src/ (зеркально), scripts/ (добавлением), pyproject, uv.lock…"
sudo rsync -a --delete --exclude "__pycache__" "$SRC/src/" "$DST/src/"
sudo rsync -a --exclude "__pycache__" "$SRC/scripts/" "$DST/scripts/"
sudo install -m 644 "$SRC/pyproject.toml" "$DST/pyproject.toml"
sudo install -m 644 "$SRC/uv.lock" "$DST/uv.lock"
sudo chown -R irina:irina "$DST/src" "$DST/scripts" "$DST/pyproject.toml" "$DST/uv.lock"

echo "uv sync (зависимости)…"
sudo -u irina bash -lc "cd $DST && uv sync >/dev/null" || echo "⚠️ uv sync не прошёл — проверь вручную"

echo "Рестарт d-brain-bot-irina…"
sudo systemctl restart d-brain-bot-irina
sleep 5
sudo systemctl is-active d-brain-bot-irina && echo "OK: сервис активен" || {
    echo "❌ Сервис не поднялся! Откат: sudo rm -rf $DST/src && sudo mv $DST/src.bak-$STAMP $DST/src && sudo systemctl restart d-brain-bot-irina"
    exit 1
}
echo "Готово. Проверь её бота сообщением и хвост: sudo tail -20 $DST/logs/bot.log"
