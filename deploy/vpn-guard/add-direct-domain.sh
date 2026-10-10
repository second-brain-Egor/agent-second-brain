#!/bin/sh
# Пускает домен мимо VPN-выхода: добавляет его в правило Xray «transparent → direct»,
# где уже стоит forumhouse.ru. Соединение по-прежнему перехватывается, но Xray узнаёт домен
# по TLS и отправляет его напрямую с российского адреса сервера.
#
#   sudo systemd-run --wait --collect --pipe --unit=add-direct-domain \
#       sh deploy/vpn-guard/add-direct-domain.sh deepgram.com
#
# Порядок: снимок «последнего рабочего» → страховочный таймер → новый конфиг → перезапуск Xray →
# проверки. Любая проверка не прошла — сразу vpn-rollback. Не снял таймер — откатит он.
set -eu
export TZ=Europe/Moscow

DOMAIN="${1:?укажи домен, например deepgram.com}"
CONF=/usr/local/etc/xray/config.json
GOOD=/var/lib/vpn-guard/last-good
LOG=/var/log/vpn-guard.log
STAMP=$(date +%Y%m%d-%H%M%S)
TMP=/run/vpn-guard/direct-$STAMP.json

log() { printf '%s | add-direct-domain | %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG" >&2; }
fail() { log "ПРОВЕРКА НЕ ПРОШЛА: $* — откатываю"; /usr/local/sbin/vpn-rollback || true; exit 1; }
code() { "$@" 2>/dev/null || true; }
as_egor() { setpriv --reuid=1000 --regid=1000 --clear-groups "$@"; }

[ "$(id -u)" = 0 ] || { echo "нужны права root" >&2; exit 1; }

# Откатываться должно быть к текущему рабочему конфигу.
if ! cmp -s "$CONF" "$GOOD/config.json"; then
    /usr/local/sbin/vpn-guard snapshot || { log "снимок не обновился — ничего не меняю"; exit 2; }
fi

# Страж не должен проверять или менять узел, пока идёт правка.
exec 9>/run/vpn-guard.lock
flock -w 120 9 || { log "страж занят дольше 2 минут — ничего не меняю"; exit 3; }

mkdir -p /run/vpn-guard
status=0
python3 - "$CONF" "$TMP" "domain:$DOMAIN" <<'PY' || status=$?
import json, sys
src, dst, entry = sys.argv[1:]
config = json.load(open(src, encoding='utf-8'))
rules = config['routing']['rules']
rule = next(r for r in rules
            if r.get('inboundTag') == ['transparent'] and r.get('outboundTag') == 'direct' and r.get('domain'))
if entry in rule['domain']:
    sys.exit(10)
rule['domain'].append(entry)
json.dump(config, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
PY
[ "$status" = 10 ] && { log "$DOMAIN уже идёт напрямую — ничего не меняю"; exit 0; }
[ "$status" = 0 ] || { log "не удалось собрать конфиг"; exit 4; }
chown root:nogroup "$TMP"; chmod 640 "$TMP"
/usr/local/bin/xray run -test -config "$TMP" >/dev/null 2>&1 || { log "новый конфиг не проходит xray -test"; exit 5; }

/usr/local/sbin/vpn-safety arm 240 >/dev/null || { log "не взвёлся страховочный таймер"; exit 6; }
cp -p "$CONF" "$CONF.bak-$STAMP-direct-$DOMAIN"
install -m 640 -o root -g nogroup "$TMP" "$CONF"
rm -f "$TMP"
log "добавил $DOMAIN в прямой маршрут, перезапускаю Xray (таймер отката 240 с)"
systemctl restart xray
for _ in 1 2 3 4 5 6 7 8 9 10; do
    ss -Htln 'sport = :12345' | grep -q . && ss -Htln 'sport = :10808' | grep -q . && break
    sleep 1
done

[ "$(systemctl is-active xray)" = active ] || fail "Xray не запустился"

# Нейросеть: обычный пользователь → заворот → узел выхода.
ok=0
for _ in 1 2 3; do
    c=$(code as_egor curl -s -m 15 -o /dev/null -w '%{http_code}' https://api.anthropic.com/)
    [ "$c" != 000 ] && { ok=1; break; }
    sleep 2
done
[ "$ok" = 1 ] || fail "api.anthropic.com через заворот не отвечает"

# Страна выхода для прочего трафика — по-прежнему не RU.
country=
for _ in 1 2 3 4 5; do
    country=$(code as_egor curl -s -m 10 https://www.cloudflare.com/cdn-cgi/trace | sed -n 's/^loc=//p')
    [ -n "$country" ] && break
    sleep 2
done
[ -n "$country" ] || log "предупреждение: cloudflare trace не ответил за 5 попыток (выход нестабилен)"
[ "$country" != RU ] || fail "обычный трафик вышел напрямую (RU)"

# Telegram: обычный пользователь → заворот → узел выхода (так ходит бот).
c=$(code as_egor curl -s -m 10 -o /dev/null -w '%{http_code}' https://api.telegram.org/)
[ "$c" != 000 ] || fail "Telegram через заворот не отвечает"

# Сам домен: 8 запросов подряд должны пройти все.
good=0
for _ in 1 2 3 4 5 6 7 8; do
    c=$(code as_egor curl -s -m 10 -o /dev/null -w '%{http_code}' "https://api.$DOMAIN/")
    [ "$c" != 000 ] && good=$((good + 1))
done
[ "$good" = 8 ] || fail "api.$DOMAIN ответил $good из 8"

/usr/local/sbin/vpn-safety disarm >/dev/null
log "проверки прошли: Anthropic отвечает, выход ${country:-не определён}, Telegram отвечает, api.$DOMAIN 8/8; таймер снят"

# Снимок обновляем уже без блокировки: vpn-guard snapshot берёт её сам.
exec 9>&-
for _ in 1 2 3 4 5; do
    /usr/local/sbin/vpn-guard snapshot && exit 0
    sleep 3
done
log "предупреждение: снимок не обновлён (выход не ответил) — страж обновит его при следующей исправной проверке"
exit 0
