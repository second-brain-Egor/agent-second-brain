---
type: note
last_accessed: 2026-04-16
relevance: 0.94
tier: active
---
# Операционный статус second brain bot

Дата: 2026-04-16

- После wiki-апгрейда по мотивам подхода Карпати у vault появился отдельный вход через индекс знаний и health-check связности
- Рабочая проверка подтвердила две критичные правки: рекурсивную индексацию project `README.md` в RAG и раздельные узлы `README.md` в графе
- Для Telegram polling допустим только один потребитель `getUpdates`; параллельный второй клиент даёт `TelegramConflictError`
- После перезапуска новых конфликтов polling не видно; устойчивый ориентир на будущее — держать один активный экземпляр бота на одном токене

Связано:
- [[memory/facts]]
- [[memory/change-log]]
- [[projects/server-backup-and-migration/README]]
