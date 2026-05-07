---
name: baryga-access
description: Используй этот скилл, когда нужно быстро зайти к Барыге, открыть `/root/trading/` и работать с основным торговым контуром без повторного поиска доступа
model: default
scope: project
depends_on: []
triggers:
  - зайти к Барыге
  - доступ к Барыге
  - Барыга
  - trading bot
  - /root/trading
---

# Доступ к Барыге

Используй проверенный вход:

```bash
ssh barriga
```

Если alias не работает, используй явный вход:

```bash
ssh -i /home/egor/.ssh/id_ed25519 root@185.23.35.88
```

После входа переходи сюда:

```bash
cd /root/trading
```

Если пользователь спрашивает только про факт входа, отвечай только результатом.

Папка с памяткой и правилом лежит здесь:
`/home/egor/agent-second-brain/Барыга`
