#!/usr/bin/env bash
# Автоматика выгрузки Forumhouse: качает сама, останавливается по месту на диске,
# продолжает когда место освободилось.
#
# Зачем: harvest живёт на barriga под root и завершается, доделав проход. Планировщика
# у него не было — 18 августа оркестратор прибили SIGTERM, и с тех пор загрузку гоняли
# руками. Этот скрипт закрывает и это, и переполнение диска: раньше безнадзорная
# загрузка забивала 38 ГБ.
#
# Логика одного запуска (cron, каждые 5 минут):
#   загрузка идёт  + мало места или памяти -> SIGTERM (прогресс сохранён), письмо Егору
#   загрузки нет   + место вернулось       -> продолжить (без пересмотра списка тем)
#   загрузки нет   + прошли сутки          -> запустить с --refresh-audit (искать новые темы)
#
# SIGTERM безопасен: scrape.py переводит его в KeyboardInterrupt, отрабатывают finally,
# а файл темы пишется после каждой страницы (emit_progress) — теряется максимум страница.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
LOG_DIR="$PROJECT_DIR/logs"
STATE_FILE="${FORUMHOUSE_GUARD_STATE_FILE:-$LOG_DIR/forumhouse-guard.state.json}"
RECEIPT_FILE="$LOG_DIR/forumhouse-notifications.jsonl"

REMOTE_HOST="${FORUMHOUSE_REMOTE_HOST:-barriga}"
REMOTE_DIR="${FORUMHOUSE_REMOTE_DIR:-/root/forum-harvest}"
FORUM_ID="${FORUMHOUSE_FORUM_ID:-91}"

# Порог остановки — 4 ГиБ, как просил Егор. Порог продолжения выше, чтобы загрузка
# не дёргалась «стоп-старт» вокруг одной и той же цифры.
STOP_FREE_BYTES="${FORUMHOUSE_STOP_FREE_BYTES:-4294967296}"
RESUME_FREE_BYTES="${FORUMHOUSE_RESUME_FREE_BYTES:-6442450944}"
# Память: на сервере 3.9 ГБ и Chromium с ботом рядом. Ниже этого браузер начнёт
# уходить в swap и тормозить всё остальное.
MIN_AVAIL_MEM_MB="${FORUMHOUSE_MIN_AVAIL_MEM_MB:-400}"
# Как часто пересматривать форум на новые темы, когда работа доделана.
REFRESH_EVERY_HOURS="${FORUMHOUSE_REFRESH_EVERY_HOURS:-24}"
# Сколько ждать чистого выхода после SIGTERM.
STOP_WAIT_SECONDS="${FORUMHOUSE_STOP_WAIT_SECONDS:-180}"

mkdir -p "$LOG_DIR"
exec 204>"$LOG_DIR/forumhouse-guard.lock"
flock -n 204 || exit 0

if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

CHAT_ID="${ADMIN_USER_IDS:-${ALLOWED_USER_IDS:-}}"
CHAT_ID="${CHAT_ID//[\[\]\" ]/}"
CHAT_ID="${CHAT_ID%%,*}"

say() { printf '[%s] %s\n' "$(TZ=Europe/Moscow date '+%F %T MSK')" "$1"; }

notify() {
    [ "${FORUMHOUSE_GUARD_NO_NOTIFY:-0}" != "1" ] || return 0
    [ -n "${TELEGRAM_BOT_TOKEN:-}" ] || { say "ERROR: TELEGRAM_BOT_TOKEN не задан"; return 0; }
    [ -n "$CHAT_ID" ] || { say "ERROR: chat id не задан"; return 0; }
    # Отправка обрывается при DPI-фильтрации TLS, поэтому три попытки.
    local attempt
    for attempt in 1 2 3; do
        if printf '%s' "$1" | "$PROJECT_DIR/.venv/bin/python" \
            "$PROJECT_DIR/scripts/send_telegram_message.py" \
            --token "$TELEGRAM_BOT_TOKEN" --chat-id "$CHAT_ID" \
            --receipt-file "$RECEIPT_FILE" >/dev/null 2>&1; then
            return 0
        fi
        say "попытка $attempt отправки не удалась"
        sleep 10
    done
    say "ERROR: уведомление не доставлено за 3 попытки"
}

remote() { ssh -n -o BatchMode=yes -o ConnectTimeout=20 "$REMOTE_HOST" "$1"; }

# Ищем именно процесс скрейпера. Просто `pgrep -f scrape.py` не годится: под шаблон
# попадают оболочки и ssh, в чьей командной строке есть та же подстрока, — страж убил бы
# обёртку, доложил «остановлено», а загрузка продолжала бы забивать диск. Поэтому
# оставляем только процессы, у которых argv[0] — это питон.
PID_SNIPPET='for p in $(pgrep -f "scrape.py --forum FORUMID" 2>/dev/null); do
    [ -r "/proc/$p/cmdline" ] || continue
    first=$(tr "\\0" "\\n" < "/proc/$p/cmdline" 2>/dev/null | head -1)
    case "$first" in */python|*/python3|python|python3) echo "$p";; esac
done'
PID_SNIPPET="${PID_SNIPPET//FORUMID/$FORUM_ID}"

scraper_pids() { remote "$PID_SNIPPET"; }

read_state() {
    "$PROJECT_DIR/.venv/bin/python" - "$STATE_FILE" "$1" <<'PY'
import json, sys
from pathlib import Path
try:
    print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get(sys.argv[2], "") or "")
except Exception:
    print("")
PY
}

write_state() {
    "$PROJECT_DIR/.venv/bin/python" - "$STATE_FILE" "$1" "$2" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path
path = Path(sys.argv[1])
try:
    state = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    state = {}
state["reason"] = sys.argv[2]
if sys.argv[3]:
    state["last_start"] = sys.argv[3]
state["updated_at"] = datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
PY
}

human_gb() { awk -v b="$1" 'BEGIN { printf "%.1f", b / 1073741824 }'; }

# --- снимок состояния --------------------------------------------------------
SNAPSHOT="$(remote "
    free_bytes=\$(df --output=avail -B1 / | tail -1 | tr -d ' ')
    avail_mem=\$(awk '/MemAvailable/ { printf \"%d\", \$2 / 1024 }' /proc/meminfo)
    folder=\$(du -sb '$REMOTE_DIR/data/raw/forumhouse/$FORUM_ID' 2>/dev/null | cut -f1)
    printf '%s %s %s' \"\$free_bytes\" \"\$avail_mem\" \"\${folder:-0}\"
")" || { say "ERROR: barriga недоступна по ssh"; exit 1; }

read -r FREE_BYTES AVAIL_MEM FOLDER_BYTES <<<"$SNAPSHOT"
PID="$(scraper_pids | head -1)"
: "${FREE_BYTES:=0}" "${AVAIL_MEM:=0}" "${PID:=0}" "${FOLDER_BYTES:=0}"

say "диск $(human_gb "$FREE_BYTES") ГиБ свободно, память ${AVAIL_MEM} МБ, папка $(human_gb "$FOLDER_BYTES") ГиБ, pid=${PID}"

# --- загрузка идёт: проверяем, не пора ли остановиться ------------------------
if [ "$PID" != "0" ]; then
    STOP_REASON=""
    if [ "$FREE_BYTES" -lt "$STOP_FREE_BYTES" ]; then
        STOP_REASON="мало места на диске"
    elif [ "$AVAIL_MEM" -lt "$MIN_AVAIL_MEM_MB" ]; then
        STOP_REASON="мало свободной памяти"
    fi
    [ -n "$STOP_REASON" ] || { say "всё в порядке, не вмешиваюсь"; exit 0; }

    say "останавливаю загрузку: $STOP_REASON"
    remote "kill -TERM $PID 2>/dev/null || true"
    waited=0
    while [ "$waited" -lt "$STOP_WAIT_SECONDS" ]; do
        sleep 10
        waited=$((waited + 10))
        [ -z "$(scraper_pids)" ] && break
    done
    LEFT="$(scraper_pids)"
    if [ -n "$LEFT" ]; then
        say "не вышел за ${STOP_WAIT_SECONDS}с, добиваю KILL"
        for p in $LEFT; do remote "kill -KILL $p 2>/dev/null || true"; done
    fi

    write_state "stopped_by_guard" ""
    notify "$(printf '📦 Загрузка Forumhouse остановлена: %s.\n\nСвободно на диске: %s ГиБ\nПапка раздела %s: %s ГиБ\n\nЗабери папку data/raw/forumhouse/%s и удали её с сервера. Загрузка продолжится сама, с того же места — прогресс сохранён.' \
        "$STOP_REASON" "$(human_gb "$FREE_BYTES")" "$FORUM_ID" "$(human_gb "$FOLDER_BYTES")" "$FORUM_ID")"
    say "остановлено, Егор оповещён"
    exit 0
fi

# --- загрузки нет: решаем, запускать ли --------------------------------------
if [ "$FREE_BYTES" -lt "$RESUME_FREE_BYTES" ]; then
    say "места мало ($(human_gb "$FREE_BYTES") ГиБ), жду выгрузки папки"
    exit 0
fi
if [ "$AVAIL_MEM" -lt "$MIN_AVAIL_MEM_MB" ]; then
    say "памяти мало (${AVAIL_MEM} МБ), не запускаю"
    exit 0
fi

REASON="$(read_state reason)"
LAST_START="$(read_state last_start)"
REFRESH_FLAG=""

if [ "$REASON" = "stopped_by_guard" ]; then
    # Продолжаем ровно с места остановки. Пересмотр списка тем тут не нужен —
    # это ещё полтора часа обхода указателя впустую.
    say "продолжаю после остановки по месту"
else
    FRESH_ENOUGH="$("$PROJECT_DIR/.venv/bin/python" - "$LAST_START" "$REFRESH_EVERY_HOURS" <<'PY'
import sys
from datetime import datetime, timedelta, timezone
try:
    stamp = datetime.fromisoformat(sys.argv[1])
    print("1" if datetime.now(timezone.utc) - stamp < timedelta(hours=float(sys.argv[2])) else "0")
except Exception:
    print("0")
PY
)"
    if [ "$FRESH_ENOUGH" = "1" ]; then
        say "проход уже делался недавно, новый не начинаю"
        exit 0
    fi
    # Суточный пересмотр форума — ищем появившиеся темы.
    REFRESH_FLAG="--refresh-audit"
    say "сутки прошли, запускаю с пересмотром списка тем"
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LAUNCHED="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
remote "cd '$REMOTE_DIR' && setsid nohup ./.venv/bin/python -u scrape.py --forum $FORUM_ID --resume $REFRESH_FLAG --headless > 'runtime/harvest-auto-$STAMP.out' 2>&1 < /dev/null & echo ok" >/dev/null

sleep 15
NEW_PID="$(scraper_pids | head -1)"
if [ -z "$NEW_PID" ]; then
    say "ERROR: загрузка не поднялась"
    remote "tail -5 '$REMOTE_DIR/runtime/harvest-auto-$STAMP.out' 2>/dev/null" || true
    notify "⚠️ Не смог запустить загрузку Forumhouse. Лог: runtime/harvest-auto-$STAMP.out"
    exit 1
fi

write_state "running" "$LAUNCHED"
say "загрузка запущена, pid=$NEW_PID"
if [ "$REASON" = "stopped_by_guard" ]; then
    notify "$(printf '▶️ Папка выгружена, загрузка Forumhouse продолжена с того же места.\n\nСвободно на диске: %s ГиБ' "$(human_gb "$FREE_BYTES")")"
fi
