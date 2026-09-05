#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/egor/agent-second-brain"
NATE_DIR="$PROJECT_DIR/vault/projects/Nate Herk"
LOG_FILE="$NATE_DIR/logs/analysis-worker.log"
LOCK_FILE="$NATE_DIR/.analysis-worker.lock"

mkdir -p "$NATE_DIR/logs"
exec 9>"$LOCK_FILE"
flock -n 9 || exit 0
cd "$PROJECT_DIR"
FAILED=0
PROCESSED=0

while IFS= read -r folder; do
  [ -s "$folder/analysis.md" ] && continue
  PROCESSED=$((PROCESSED + 1))
  printf '%s START %s\n' "$(date -Is)" "$folder" >>"$LOG_FILE"

  prompt="Прочитай полностью vault/projects/Nate Herk/AGENTS.md, затем обработай только ролик в папке: ${folder#$PROJECT_DIR/}. Создай полноценный analysis.md строго по правилам проекта. Заголовок карточки переведи на русский, оставив точные названия моделей и сервисов. Обязательно используй точные отдельные заголовки второго уровня: «Тема», «Краткое содержание», «Основной вывод», а затем остальные разделы карточки. Эти три первых раздела напиши простыми русскими словами: тема — одно короткое предложение, содержание — не более двух коротких предложений, основной вывод — одно короткое предложение без отдельных подблоков. Английские слова заменяй русскими, кроме точных названий моделей и сервисов. Проверь ссылки на кадры. После этого аккуратно дополни vault/projects/Nate Herk/summary.md новыми знаниями без повторов. Не трогай другие карточки. Не отвечай пользователю и не отправляй сообщения: это фоновая обработка."

  if codex exec --skip-git-repo-check --color never --cd "$PROJECT_DIR" \
      --model gpt-5.6-sol --dangerously-bypass-approvals-and-sandbox \
      "$prompt" </dev/null >>"$LOG_FILE" 2>&1 \
      && [ -s "$folder/analysis.md" ]; then
    printf '%s DONE %s\n' "$(date -Is)" "$folder" >>"$LOG_FILE"
  else
    printf '%s FAILED %s\n' "$(date -Is)" "$folder" >>"$LOG_FILE"
    FAILED=$((FAILED + 1))
  fi
done < <(find "$NATE_DIR/videos" -mindepth 1 -maxdepth 1 -type d -print | sort)

printf '%s QUEUE_COMPLETE processed=%d failed=%d\n' \
  "$(date -Is)" "$PROCESSED" "$FAILED" >>"$LOG_FILE"

[ "$FAILED" -eq 0 ]
