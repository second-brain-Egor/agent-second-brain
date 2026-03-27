---
name: video-processor
description: YouTube субтитры через yt-dlp. MP4/кружочки — ffmpeg + Deepgram + vision
model: default
scope: global
depends_on: []
triggers:
  - обработай видео
  - скачай субтитры
---

# Video Processor

## YouTube — субтитры через yt-dlp

```bash
# Скачать субтитры (предпочитать ручные, fallback на авто)
yt-dlp --write-sub --write-auto-sub --sub-lang ru,en --skip-download -o "/tmp/%(id)s" "URL"

# Или скачать аудио для транскрипции
yt-dlp -x --audio-format mp3 -o "/tmp/%(id)s.%(ext)s" "URL"
```

## MP4/кружочки — ffmpeg + Deepgram

```bash
# Извлечь аудио из видео
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 /tmp/audio.wav

# Транскрибировать через Deepgram API
curl -X POST "https://api.deepgram.com/v1/listen?language=ru&model=nova-2" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: audio/wav" \
  --data-binary @/tmp/audio.wav
```

## Правила
- YouTube → сначала субтитры, если нет — скачать аудио → Deepgram
- MP4/MOV → ffmpeg → Deepgram
- Кружочки Telegram → скачать через Bot API → ffmpeg → Deepgram
- Результат → сохранить в vault/daily/ или vault/thoughts/
