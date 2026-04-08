# VPS Setup Guide

Run Agent Second Brain 24/7 on a virtual private server.

## Requirements

- VPS with Ubuntu 22.04+ (minimum 1GB RAM, recommended 2GB)
- Root or sudo access
- SSH client

## Recommended VPS Providers

| Provider | Price | Region |
|----------|-------|--------|
| Contabo | from $5/mo | Europe |
| Hetzner | from $4/mo | Europe |
| DigitalOcean | from $6/mo | Global |
| Vultr | from $5/mo | Global |

---

## Step 1: Connect to Server

After purchasing VPS, you'll get:
- IP address (e.g., `162.55.123.45`)
- Root password

Connect via SSH:

```bash
ssh root@162.55.123.45
```

Enter password (characters won't display — that's normal).

---

## Step 2: Create User

Never work as root. Create a regular user:

```bash
# Create user (replace "myuser" with your name)
adduser myuser

# Follow prompts:
# - Enter password (twice)
# - Other fields can be skipped (Enter)

# Grant sudo rights
usermod -aG sudo myuser

# Switch to new user
su - myuser
```

---

## Step 3: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Step 4: Install Base Tools

```bash
# Git
sudo apt install -y git

# Curl and wget
sudo apt install -y curl wget

# Build tools
sudo apt install -y build-essential

# Verify
git --version
```

---

## Step 5: Install Python 3.12

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Verify
python3.12 --version
```

---

## Step 6: Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Verify
uv --version
```

---

## Step 7: Install Node.js

Required for MCP servers (Todoist integration):

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version
npm --version
```

---

## Step 8: Prepare Codex CLI Access

```bash
codex login
codex login status
```

The bot uses local Codex CLI authorization. `codex login status` should show `Logged in using ChatGPT`.

---

## Step 9: Clone Project

```bash
cd ~
mkdir -p projects
cd projects

git clone https://github.com/smixs/agent-second-brain.git
cd agent-second-brain

ls -la
```

---

## Step 10: Install Dependencies

```bash
uv sync

# Verify
uv run python -c "import aiogram; print('aiogram OK')"
```

---

## Step 11: Get Tokens

### Telegram Bot Token

1. Open Telegram
2. Find `@BotFather`
3. Send `/newbot`
4. Enter bot name and username
5. Copy the token

### Your Telegram User ID

1. Find `@userinfobot` in Telegram
2. Send any message
3. Copy the ID number

### Deepgram API Key

1. Go to https://console.deepgram.com/
2. Sign up (free $200 credit)
3. Settings → API Keys
4. Create key and copy

### Todoist API Token (optional)

1. Go to https://todoist.com/
2. Settings → Integrations → Developer
3. Copy API token

---

## Step 12: Configure Environment

```bash
nano ~/projects/agent-second-brain/.env
```

Paste (replace with your values):

```bash
TELEGRAM_BOT_TOKEN=7123456789:AAHdN8J2K4m5N6o7P8q9R0s1T2u3V4w5X6y
DEEPGRAM_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
TODOIST_API_KEY=
CODEX_BIN=codex
CODEX_MODEL=gpt-5.4
VAULT_PATH=./vault
ALLOWED_USER_IDS=[123456789]
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Step 13: Clean Vault Examples

```bash
cd ~/projects/agent-second-brain

rm -rf vault/daily/*
rm -rf vault/thoughts/ideas/*
rm -rf vault/thoughts/projects/*
rm -rf vault/thoughts/learnings/*
rm -rf vault/thoughts/reflections/*
rm -rf vault/summaries/*
rm -rf vault/attachments/*
```

---

## Step 14: Customize Goals

Edit goals to match yours:

```bash
nano vault/goals/0-vision-3y.md    # 3-year vision
nano vault/goals/1-yearly-2026.md  # Yearly goals
nano vault/goals/2-monthly.md      # Monthly priorities
nano vault/goals/3-weekly.md       # Weekly focus
```

---

## Step 15: Test Run

```bash
cd ~/projects/agent-second-brain
uv run python -m d_brain
```

Should show:
```
INFO:aiogram.dispatcher:Start polling
INFO:aiogram.dispatcher:Run polling for bot @your_bot_name
```

Test in Telegram:
- Find your bot
- Send `/start`
- Send a voice message

Stop with `Ctrl+C`.

---

## Step 16: Setup Automation (cron)

```bash
cd ~/projects/agent-second-brain
/bin/bash scripts/install-cron.sh

# Check installed jobs
crontab -l
```

---

## Step 17: Git Configuration

```bash
cd ~/projects/agent-second-brain

git config user.email "your@email.com"
git config user.name "Your Name"
```

### Create your own repository

1. GitHub → "+" → "New repository"
2. Name: `my-second-brain`
3. Leave empty (no README)
4. Create

### Change remote

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/my-second-brain.git
git remote -v
git push -u origin main
```

If prompted for password, use Personal Access Token:
- GitHub → Settings → Developer settings → Personal access tokens

---

## Useful Commands

```bash
# Cron jobs
crontab -l

# Bot logs
tail -f ~/projects/agent-second-brain/logs/bot.log

# Daily processing logs
tail -f ~/projects/agent-second-brain/logs/process.log

# Weekly digest logs
tail -f ~/projects/agent-second-brain/logs/weekly.log

# Manual processing
cd ~/projects/agent-second-brain
./scripts/process.sh

# Update code
cd ~/projects/agent-second-brain
git pull
uv sync
/bin/bash scripts/install-cron.sh
```

---

## Troubleshooting

### Bot doesn't respond

```bash
crontab -l
tail -n 100 ~/projects/agent-second-brain/logs/bot.log
cat ~/projects/agent-second-brain/.env | grep TELEGRAM_BOT_TOKEN
/bin/bash ~/projects/agent-second-brain/scripts/install-cron.sh
```

### Voice not transcribing

```bash
cat ~/projects/agent-second-brain/.env | grep DEEPGRAM
sudo journalctl -u d-brain-bot | grep -i error
```

### Processing errors

```bash
codex login status
tail -n 100 ~/projects/agent-second-brain/logs/process.log
```

### Todoist not working

```bash
cat ~/projects/agent-second-brain/.env | grep TODOIST
mcp-cli call todoist find-tasks-by-date '{"startDate": "today"}'
```

### Permission errors

```bash
sudo chown -R myuser:myuser ~/projects/agent-second-brain
chmod -R 755 ~/projects/agent-second-brain
```

### Git push fails

```bash
git remote -v
git status
git config --global credential.helper store
git push
```

---

## Sync with Local Computer

See main [README](../README.md) for Obsidian sync options.

---

## Security Tips

- Use SSH keys instead of passwords
- Keep system updated: `sudo apt update && sudo apt upgrade`
- `.env` is in `.gitignore` — never commit tokens
- Consider setting up firewall: `sudo ufw enable`
