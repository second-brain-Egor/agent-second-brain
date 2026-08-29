---
type: note
description: >
last_accessed: 2026-03-27
relevance: 0.1
tier: archive
name: video-processor
model: default
scope: global
depends_on: []
triggers: 
---

# Video Processor

## YouTube — полный pipeline

### Зависимости
- `yt-dlp` — установлен в `/home/egor/.local/bin/yt-dlp`
- JS runtime: `node` (v22, установлен). Если не работает — указать `--js-runtimes node`
- PATH: `export PATH="$HOME/.local/bin:$PATH"`

### 1. Получить субтитры (основной способ)

```bash
# Автосубтитры (русские или английские)
yt-dlp --write-auto-sub --sub-lang ru,en --skip-download --sub-format vtt \
  -o "/tmp/yt-%(id)s" "URL"

# Ручные субтитры (если есть — точнее авто)
yt-dlp --write-sub --sub-lang ru,en --skip-download --sub-format vtt \
  -o "/tmp/yt-%(id)s" "URL"

# Комбо: сначала ручные, fallback на авто
yt-dlp --write-sub --write-auto-sub --sub-lang ru,en --skip-download --sub-format vtt \
  -o "/tmp/yt-%(id)s" "URL"
```

После скачивания: прочитать .vtt файл, убрать таймкоды, получить чистый текст.

### 2. Метаданные видео

```bash
# JSON с названием, описанием, длительностью, каналом
yt-dlp -j --no-warnings "URL"
```

### 3. Список видео канала

```bash
# Последние 30 видео канала (flat — без скачивания)
yt-dlp --flat-playlist -j --playlist-items 1-30 \
  "https://www.youtube.com/@ChannelHandle/videos"
```

### 4. Если субтитров нет — скачать аудио

```bash
yt-dlp -x --audio-format mp3 -o "/tmp/yt-%(id)s.%(ext)s" "URL"
```
Затем транскрибировать через Deepgram (см. ниже).

### Troubleshooting
- YouTube блокирует → `pip install -U yt-dlp` (обновить)
- Ошибка JS runtime → `--js-runtimes node`
- Rate limiting → `--no-warnings --quiet`, пауза 1-2 сек между запросами
- Не качать видео → всегда `--skip-download` для субтитров

## MP4/кружочки — ffmpeg + Deepgram

```bash
# Извлечь аудио
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 /tmp/audio.wav

# Транскрибировать
curl -X POST "https://api.deepgram.com/v1/listen?language=ru&model=nova-3" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: audio/wav" \
  --data-binary @/tmp/audio.wav
```

## Workflow: анализ YouTube-ролика

1. Получить метаданные (`yt-dlp -j`) — название, описание
2. Скачать субтитры (VTT) — `--write-sub --write-auto-sub`
3. Очистить VTT от таймкодов → чистый текст
4. Прочитать текст, сделать краткое содержание
5. Если есть ссылки в описании — извлечь и показать
6. Сохранить результат в vault (daily/ или thoughts/)

## Правила
- YouTube → сначала субтитры, если нет — скачать аудио → Deepgram
- MP4/MOV → ffmpeg → Deepgram
- Кружочки Telegram → скачать через Bot API → ffmpeg → Deepgram
- Результат → сохранить в vault/daily/ или vault/thoughts/
- Всегда очищать /tmp после обработки
