#!/bin/bash
set -e
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
USER=$(whoami)
UV_PATH=$(which uv)
SERVICE_FILE="/etc/systemd/system/d-brain-bot.service"

# Если сервис уже существует — проверить ExecStart
if [ -f "$SERVICE_FILE" ]; then
    CURRENT_EXEC=$(grep "ExecStart=" "$SERVICE_FILE" | head -1)
    NEW_EXEC="ExecStart=$UV_PATH run python -m d_brain"
    if echo "$CURRENT_EXEC" | grep -q "$UV_PATH"; then
        echo "Service already configured correctly, restarting..."
        sudo systemctl restart d-brain-bot
        sleep 3
        sudo systemctl status d-brain-bot --no-pager
        exit 0
    fi
    echo "Updating service (backup: ${SERVICE_FILE}.bak)..."
    sudo cp "$SERVICE_FILE" "${SERVICE_FILE}.bak"
fi

cat > /tmp/d-brain-bot.service << EOF
[Unit]
Description=d-brain Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$UV_PATH run python -m d_brain
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/d-brain-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable d-brain-bot
sudo systemctl restart d-brain-bot
sleep 3
sudo systemctl status d-brain-bot --no-pager
