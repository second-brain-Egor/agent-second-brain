---
name: skill-builder
description: Создаёт новые навыки и суб-агентов по запросу пользователя
model: default
scope: global
depends_on: []
triggers:
  - создай навык
  - добавь навык
  - новый скилл
  - создай агента
  - новый агент
---

# Skill & Agent Builder

Создаёт навыки (skills) и суб-агентов (agents) по запросу пользователя.

## Разница между навыком и агентом

- **Навык (skill)** — инструкция, которую Claude выполняет в текущем контексте. Видит всю историю разговора. Пример: веб-поиск, генерация отчёта.
- **Суб-агент (agent)** — отдельный процесс со своим свежим контекстом и своей моделью. Не видит историю. Пример: research на Haiku (дешевле), перевод на Sonnet.

Если задача рутинная и дешёвая — предложи агента. Если нужен контекст разговора — предложи навык.

## Глобальные vs проектные

- **Глобальные** — нужны везде, живут в `vault/.claude/skills/` и `vault/.claude/agents/`
- **Проектные** — нужны только в одном проекте, живут в `vault/projects/{project-name}/.skills/` или `vault/projects/{project-name}/.agents/`

Спроси пользователя: «Этот навык для всех задач или только для проекта X?»

## Процесс создания навыка

1. Спросить: что навык должен делать? Глобальный или проектный? Какие инструменты/API?
2. Определить путь:
   - Глобальный: `vault/.claude/skills/{skill-name}/SKILL.md`
   - Проектный: `vault/projects/{project-name}/.skills/{skill-name}/SKILL.md`
3. Создать SKILL.md с YAML front matter (шаблон ниже)
4. Записать инструкции в markdown после YAML
5. Обновить CLAUDE.md — добавить в секцию Skills (для глобальных)
6. Если нужен API-ключ — добавить плейсхолдер в .env и сообщить пользователю
7. Протестировать: попросить пользователя вызвать навык

## Процесс создания суб-агента

1. Спросить: что агент должен делать? Какую модель использовать (sonnet/haiku)?
2. Определить путь:
   - Глобальный: `vault/.claude/agents/{agent-name}/AGENT.md`
   - Проектный: `vault/projects/{project-name}/.agents/{agent-name}/AGENT.md`
3. Создать AGENT.md с YAML front matter (шаблон ниже)
4. Обновить CLAUDE.md — добавить в секцию Субагенты (для глобальных)
5. Протестировать

## Шаблон YAML для навыка

```yaml
---
name: {skill-name}
description: {что делает}
model: default
scope: global | project
depends_on: []
triggers:
  - {фраза 1}
  - {фраза 2}
---
```

## Шаблон YAML для суб-агента

```yaml
---
name: {agent-name}
description: {что делает}
model: sonnet | haiku
scope: global | project
depends_on: []
triggers:
  - {фраза 1}
---
```

## Правила
- Один навык = одна папка = один SKILL.md
- Один агент = одна папка = один AGENT.md
- Имя папки = имя в kebab-case
- Не создавать дубли существующих
- Глобальные → обновить CLAUDE.md, проектные → обновить README проекта
- Агент ВСЕГДА имеет поле model (sonnet или haiku, НЕ default)
