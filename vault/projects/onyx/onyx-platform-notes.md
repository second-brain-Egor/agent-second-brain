---
type: note
source: https://github.com/onyx-dot-app/onyx
created: 2026-05-04
last_accessed: 2026-05-05
relevance: 0.95
tier: active
---

# Onyx — заметки по платформе

Onyx — не отдельная LLM-модель, а open-source платформа поверх языковых моделей. Это слой приложения: чат, поиск по внутренним данным, RAG, агенты, действия, веб-поиск, выполнение кода, генерация файлов и интеграции.

## Что умеет

- Чат с разными LLM-провайдерами: OpenAI, Anthropic, Gemini, Azure OpenAI, Amazon Bedrock, Ollama, LiteLLM, vLLM, LM Studio, OpenRouter и OpenAI-совместимые API.
- RAG и поиск по внутренним данным через коннекторы, загрузку файлов или ingestion API.
- Кастомные агенты с инструкциями, привязанными источниками знаний и действиями.
- Actions через встроенные инструменты, OpenAPI и MCP.
- Веб-поиск, Deep Research, Code Execution, Image Generation, Voice Mode.
- Самостоятельное развёртывание через Docker Compose, Kubernetes, Helm/Terraform и облака.

## Архитектура

Основные компоненты:

- Frontend: Next.js.
- Backend: Python FastAPI.
- Background workers: фоновые задачи загрузки и индексации.
- Postgres: пользователи, настройки, история, системное состояние.
- Search/vector index: в актуальной документации фигурирует OpenSearch, в части security-документации ещё встречается Vespa.
- Redis: кэш и сессии в Standard-режиме.
- MinIO/S3: файловое хранилище.
- Nginx: reverse proxy.

Есть два режима:

- Onyx Lite — лёгкий чат/агенты/проекты/загрузка файлов без коннекторов и полноценного RAG.
- Onyx Standard — полный стек с коннекторами, индексацией, RAG, workers, search/vector index, Redis и файловым хранилищем.

## Ресурсы

Для Standard-деплоя документация ориентирует примерно на:

- минимум: 4 vCPU, 10 GB RAM;
- предпочтительно: 8+ vCPU, 16+ GB RAM;
- диск: 32 GB плюс запас под индексированные данные.

Для 10 GB текстового контента пример из документации выходит уже примерно на 9 CPU и 35 GB RAM из-за индекса. Для личной базы знаний это значит: Lite можно пробовать легко, Standard под большой vault/архивы лучше ставить на отдельный достаточно мощный сервер.

## Безопасность

Self-hosted-режим держит данные внутри своей инфраструктуры, но внешние LLM, веб-поиск и Actions будут получать данные только если их настроить. Анонимная телеметрия включена по умолчанию, её можно отключить.

Доступы к документам и полноценный RBAC в основном относятся к Enterprise Edition. В Community/Self-hosted есть базовая аутентификация и поддержка SSO через OAuth/OIDC/SAML, но тонкая модель доступа к документам ограничена.

## Подходит ли для второго мозга

Подходит как тяжёлая оболочка для базы знаний: чат, поиск, RAG, агенты, коннекторы, API, MCP. Особенно интересно для отдельной корпоративной базы или для большого архива документов.

Для текущего Telegram second-brain bot это не прямая замена. Onyx может стать отдельным поисково-агентным слоем рядом с ботом, но тащить его внутрь текущего контура нерационально: много инфраструктуры, отдельная модель данных, отдельная авторизация, отдельный индекс.

Наиболее разумный вариант: сначала пробный self-hosted Standard-деплой на отдельном сервере, затем загрузка части vault и Forumhouse/документов через File/Web/API-коннекторы, после этого оценка качества поиска против текущего RAG.

## Источники

- https://docs.onyx.app/
- https://docs.onyx.app/llms.txt
- https://docs.onyx.app/deployment/getting_started/quickstart
- https://docs.onyx.app/deployment/getting_started/resourcing
- https://docs.onyx.app/deployment/local/docker
- https://docs.onyx.app/overview/core_features/internal_search
- https://docs.onyx.app/overview/core_features/agents
- https://docs.onyx.app/overview/core_features/actions
- https://docs.onyx.app/overview/core_features/connectors
- https://docs.onyx.app/security/architecture/system_description
- https://docs.onyx.app/security/architecture/data_storage
- https://docs.onyx.app/security/architecture/access_controls
- https://docs.onyx.app/security/self_hosted/data_processing
- https://github.com/onyx-dot-app/onyx
