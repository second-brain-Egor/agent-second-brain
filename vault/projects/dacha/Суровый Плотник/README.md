---
type: project
description: "Суровый Плотник — project"
related: 
last_accessed: 2026-05-01
relevance: 0.47
tier: cold
---
# Суровый Плотник

Источник: https://youtube.com/@suroviplotnik

Папка для выгрузки и последующего разбора канала по каркасному строительству.

Общий скрипт выгрузки лежит отдельно:

`vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py`

## Что складывать сюда

- `videos/` — отдельные папки по роликам.
- `logs/` — журналы запусков.
- `summary.md` — общая сводка по всем выгруженным роликам.

## Схема по каждому ролику

- `metadata.json` — технические метаданные yt-dlp.
- `metadata.md` — краткая карточка: название, ссылка, канал, дата, длительность.
- `description.md` — описание ролика.
- `comments.json` — комментарии, если YouTube отдаст их через yt-dlp.
- `subtitles/` — субтитры VTT.
- `transcript.md` — очищенный текст субтитров.
- `frames/` — кадры из видео, если включить их извлечение.

## Запуск

Пробная выгрузка последних 5 роликов:

```bash
python3 "vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py" --url "https://youtube.com/@suroviplotnik" --output "vault/projects/dacha/Суровый Плотник" --limit 5
```

Только метаданные, описания, субтитры и комментарии:

```bash
python3 "vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py" --url "https://youtube.com/@suroviplotnik" --output "vault/projects/dacha/Суровый Плотник" --limit 30
```

С кадрами:

```bash
python3 "vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py" --url "https://youtube.com/@suroviplotnik" --output "vault/projects/dacha/Суровый Плотник" --limit 5 --frames
```
