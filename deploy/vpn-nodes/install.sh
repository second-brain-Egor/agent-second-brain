#!/bin/sh
# Ставит программу замеров узлов VPN и её таймер (проект «Узлы VPN»). Неделю наблюдения не начинает:
# для этого — sudo vpn-nodes week. Нужен установленный страж (deploy/vpn-guard/install.sh).
# Запуск (на сервере): sudo sh deploy/vpn-nodes/install.sh. Безопасно запускать повторно.
set -eu
SRC="$(cd "$(dirname "$0")" && pwd)"
[ "$(id -u)" = 0 ] || { echo "Нужны права root: sudo sh $0" >&2; exit 1; }

install -d -m 700 /var/lib/vpn-nodes
install -m 755 -o root -g root "$SRC/vpn-nodes" /usr/local/sbin/vpn-nodes
install -m 644 "$SRC/vpn-nodes.service" /etc/systemd/system/vpn-nodes.service
install -m 644 "$SRC/vpn-nodes.timer" /etc/systemd/system/vpn-nodes.timer
systemctl daemon-reload
echo "vpn-nodes установлен; таймер включается командой: sudo vpn-nodes week"
