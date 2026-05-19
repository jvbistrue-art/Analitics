# Процесс использования RAG в отдельных проектах

## Цель

Организовать знания проекта так, чтобы:

- исходные материалы хранились в человекочитаемом формате Obsidian Markdown;
- векторная база автоматически наполнялась из этих материалов;
- агенты понимали, когда обращаться к базе знаний, как фильтровать данные и как ссылаться на источники;
- каждый проект имел изолированное пространство знаний и не смешивал контекст с другими проектами.

## Базовая модель

Obsidian vault является источником истины. Векторная база является производным индексом, который можно пересоздать из vault в любой момент.

```text
project vault (.md files)
        |
        v
ingestion pipeline
        |
        +-- parse frontmatter
        +-- normalize markdown
        +-- split into chunks
        +-- calculate embeddings
        +-- upsert chunks with metadata
        v
project vector namespace / collection
        |
        v
agent retrieval policy
```

## Структура vault

Рекомендуемая структура для каждого проекта:

```text
vaults/
  project-slug/
    00-index.md
    01-domain/
    02-decisions/
    03-research/
    04-requirements/
    05-operations/
    90-archive/
```

- `00-index.md` - карта проекта: цели, важные ссылки, список ключевых документов.
- `01-domain/` - предметная область, термины, сущности, бизнес-правила.
- `02-decisions/` - архитектурные и продуктовые решения.
- `03-research/` - исследования, заметки по рынку, ссылки на внешние источники.
- `04-requirements/` - требования, user stories, ограничения.
- `05-operations/` - инструкции, runbooks, процессы эксплуатации.
- `90-archive/` - устаревшие материалы, которые не должны попадать в основной retrieval без явного запроса.

## Формат заметок

Каждая заметка должна иметь YAML frontmatter. Это позволяет агентам и ingestion pipeline фильтровать знания без эвристик.

```markdown
---
project: analytics-platform
type: decision
status: active
owner: product
created: 2026-05-19
updated: 2026-05-19
tags:
  - rag
  - agents
visibility: internal
retrieval:
  index: true
  priority: high
  audiences:
    - planning-agent
    - implementation-agent
---

# Решение: использовать Obsidian как источник истины

## Контекст

...

## Решение

...

## Последствия

...
```

Минимальные обязательные поля:

- `project` - стабильный идентификатор проекта.
- `type` - тип знания: `index`, `domain`, `decision`, `research`, `requirement`, `operation`, `archive`.
- `status` - `draft`, `active`, `deprecated`, `archived`.
- `updated` - дата последнего осмысленного обновления.
- `retrieval.index` - можно ли индексировать заметку.

## Типы знаний и поведение retrieval

| Type | Назначение | Когда использовать |
| --- | --- | --- |
| `index` | Карта проекта | В начале новой задачи, при выборе области поиска |
| `domain` | Термины и правила | При обсуждении предметной области и требований |
| `decision` | Принятые решения | При архитектурных вопросах и изменении поведения |
| `research` | Исследования | При анализе альтернатив и внешнего контекста |
| `requirement` | Требования | При реализации функциональности и проверке acceptance criteria |
| `operation` | Инструкции | При деплое, отладке, поддержке |
| `archive` | Устаревшие материалы | Только если агент явно ищет исторический контекст |

## Индексация

### 1. Discovery

Pipeline сканирует только vault конкретного проекта:

```text
vaults/{project-slug}/**/*.md
```

Файл пропускается, если:

- `retrieval.index: false`;
- `status: archived` и запрос не требует архивных данных;
- файл лежит в `90-archive/` и нет отдельного archive-index режима.

### 2. Parsing

Для каждого файла извлекаются:

- frontmatter;
- заголовки Markdown;
- wikilinks Obsidian (`[[note]]`, `[[note|label]]`);
- обычные ссылки;
- блоки кода;
- текстовые секции.

### 3. Chunking

Рекомендуемый подход:

- chunk строится вокруг заголовков, а не фиксированного количества символов;
- размер chunk: примерно 500-900 токенов;
- overlap: 80-150 токенов;
- каждый chunk наследует metadata файла;
- в metadata добавляются `heading_path`, `source_path`, `chunk_index`, `content_hash`.

Пример записи в векторной базе:

```json
{
  "id": "analytics-platform:02-decisions/rag-source-of-truth.md:0003",
  "namespace": "project:analytics-platform",
  "text": "## Решение\nObsidian vault является источником истины...",
  "metadata": {
    "project": "analytics-platform",
    "type": "decision",
    "status": "active",
    "priority": "high",
    "source_path": "02-decisions/rag-source-of-truth.md",
    "heading_path": ["Решение"],
    "updated": "2026-05-19",
    "content_hash": "sha256:..."
  }
}
```

### 4. Embeddings и upsert

Индексация должна быть идемпотентной:

- если `content_hash` не изменился, chunk не пересчитывается;
- если файл удален, все chunks с этим `source_path` удаляются из namespace проекта;
- если `status` стал `deprecated`, chunk остается доступным, но получает меньший retrieval score;
- если `status` стал `archived`, chunk исключается из обычного поиска.

### 5. Namespaces

Для изоляции проектов использовать отдельные namespaces или collections:

```text
project:{project-slug}
```

Общие знания можно вынести отдельно:

```text
shared:company
shared:engineering
```

Агент сначала ищет в `project:{project-slug}`. Shared namespaces подключаются только если задача явно требует общих стандартов, политик или практик.

## Правила для агентов

Агент должен использовать RAG, если задача содержит хотя бы один из признаков:

- требуется знание проекта, которого нет в текущем контексте диалога;
- нужно проверить термин, бизнес-правило, ограничение, принятое решение;
- пользователь просит опираться на проектную документацию;
- задача затрагивает требования, архитектуру, интеграции, эксплуатацию;
- есть риск принять решение по памяти без актуального источника;
- агент видит ссылку на Obsidian note, decision id, requirement id или project slug.

Агент может не использовать RAG, если:

- задача полностью локальная и решается по открытому файлу или текущему diff;
- пользователь просит только переформулировать уже предоставленный текст;
- запрос не относится к конкретному проекту.

## Retrieval policy

Базовый алгоритм:

1. Определить `project-slug`.
2. Прочитать `00-index.md` через vector search или прямой доступ, если он уже известен.
3. Выполнить semantic search в `project:{project-slug}`.
4. Применить metadata-фильтры:
   - `status in ["active", "draft"]` по умолчанию;
   - `type` по смыслу задачи;
   - `retrieval.audiences` при наличии специализированного агента.
5. Сделать rerank найденных chunks.
6. Вернуть ответ со ссылками на `source_path` и `heading_path`.
7. Если confidence низкий, запросить дополнительные источники или явно сказать, что база знаний не содержит достаточного ответа.

## Scoring

При ранжировании учитывать не только similarity:

```text
final_score =
  semantic_similarity
  + type_boost
  + priority_boost
  + recency_boost
  - deprecated_penalty
  - archive_penalty
```

Пример boosts:

- `retrieval.priority: high` -> плюс к score;
- `type: decision` для архитектурного вопроса -> плюс к score;
- `status: deprecated` -> существенный штраф;
- `90-archive/` -> исключить, если archive mode не включен.

## Контракт ответа агента

Когда агент использовал RAG, он должен:

- кратко указать, что опирался на базу знаний проекта;
- перечислить ключевые источники;
- отделить факты из базы знаний от собственных выводов;
- не выдавать выводы без источников как проектные факты.

Пример:

```text
Опираюсь на проектную базу знаний:
- 02-decisions/rag-source-of-truth.md > Решение
- 04-requirements/agent-retrieval.md > Acceptance criteria

Факты из базы:
...

Вывод:
...
```

## Синхронизация

### Локальный режим

Подходит для разработки и небольших проектов:

```text
obsidian save
  -> file watcher
  -> incremental ingestion
  -> vector upsert
```

### CI режим

Подходит для командной работы:

```text
pull request with vault changes
  -> validation
  -> ingestion dry run
  -> merge
  -> production indexing
```

### Scheduled режим

Подходит для внешних источников и регулярного обновления:

```text
nightly job
  -> scan changed files
  -> reindex changed chunks
  -> report stale / invalid notes
```

## Валидация качества базы знаний

Перед индексацией проверять:

- наличие обязательного frontmatter;
- корректность `project`, `type`, `status`;
- отсутствие пустых заметок;
- отсутствие слишком больших секций без заголовков;
- валидность wikilinks;
- отсутствие секретов и приватных токенов;
- наличие `updated` после существенного изменения.

Для контроля качества полезны отчеты:

- заметки без входящих ссылок;
- заметки без исходящих ссылок;
- deprecated documents, которые все еще часто извлекаются;
- chunks с низким retrieval score;
- запросы агентов, где ответ не нашел источников.

## Минимальный MVP

1. Завести `vaults/{project-slug}` и базовую структуру папок.
2. Договориться о frontmatter schema.
3. Реализовать ingestion:
   - Markdown parser;
   - chunking по заголовкам;
   - embeddings;
   - upsert в namespace проекта.
4. Добавить agent instruction:
   - когда использовать RAG;
   - как фильтровать по project namespace;
   - как цитировать источники.
5. Добавить validation command для vault.
6. Протестировать на 10-20 реальных заметках проекта.

## Открытые решения

Перед реализацией нужно выбрать:

- векторную БД: Qdrant, Chroma, pgvector, Pinecone или другой вариант;
- embedding model;
- способ хранения vault: Git repo, отдельный repo, synced folder;
- runtime для ingestion: CLI, background worker, CI job;
- способ доступа агента к retrieval: MCP tool, HTTP API, локальный CLI;
- формат auth и разграничение доступа между проектами.

## Рекомендуемая целевая архитектура

Для агентного workflow удобна такая схема:

```text
Obsidian vault in Git
        |
        v
ingestion CLI / CI job
        |
        v
Qdrant or pgvector namespaces per project
        |
        v
retrieval service exposed as MCP tool
        |
        v
agents with explicit RAG policy
```

MCP tool для агентов должен иметь минимум три операции:

- `search_project_knowledge(project, query, filters)` - semantic search по проекту;
- `get_project_note(project, source_path)` - получить полную заметку;
- `list_project_sources(project, filters)` - посмотреть доступные источники.

Так агент не получает прямой доступ к базе данных и работает через стабильный контракт.
