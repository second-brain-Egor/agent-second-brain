#!/bin/sh
# Устанавливает защиту сети сервера: страж выхода (Осло, Стокгольм, Оулу, запасной Вильнюс), откат и страховочный таймер.
# Запуск (на сервере): sudo sh deploy/vpn-guard/install.sh
# Безопасно запускать повторно. Скрипт правил перехвата заменяется только если отличается,
# с резервной копией рядом; сам Xray и правила он не перезапускает.
set -eu
SRC="$(cd "$(dirname "$0")" && pwd)"
[ "$(id -u)" = 0 ] || { echo "Нужны права root: sudo sh $0" >&2; exit 1; }

install -d -m 700 /var/lib/vpn-guard /var/lib/vpn-guard/last-good /etc/vpn-guard
touch /var/log/vpn-guard.log && chmod 640 /var/log/vpn-guard.log

for tool in vpn-rollback vpn-safety vpn-guard; do
    install -m 755 -o root -g root "$SRC/$tool" "/usr/local/sbin/$tool"
done

ROUTING=/usr/local/sbin/xray-transparent-routing
if ! cmp -s "$SRC/xray-transparent-routing" "$ROUTING"; then
    [ -e "$ROUTING" ] && cp -p "$ROUTING" "$ROUTING.bak-$(TZ=Europe/Moscow date +%Y%m%d-%H%M%S)-vpn-guard"
    install -m 755 -o root -g root "$SRC/xray-transparent-routing" "$ROUTING"
    echo "скрипт правил перехвата обновлён (изменения применятся при следующем перезапуске Xray)"
fi

install -m 644 "$SRC/vpn-guard.service" /etc/systemd/system/vpn-guard.service
install -m 644 "$SRC/vpn-guard.timer" /etc/systemd/system/vpn-guard.timer
systemctl daemon-reload
systemctl enable --now vpn-guard.timer

# Первый снимок «последнего рабочего» делаем только если выход отвечает.
[ -s /var/lib/vpn-guard/last-good/config.json ] || /usr/local/sbin/vpn-guard snapshot || \
    echo "снимок не создан: выход не отвечает, повтори после восстановления связи" >&2
echo "готово: vpn-guard.timer $(systemctl is-active vpn-guard.timer)"
