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

## Информационная архитектура vault

Vault должен помогать двум сценариям одновременно:

1. Человек быстро находит нужный материал без знания внутренних названий файлов.
2. Агент получает стабильные metadata и понимает, какие источники использовать для конкретного типа задачи.

Главный принцип: папка отвечает за тип знания, а frontmatter отвечает за состояние, проект, владельца, связи и правила retrieval.

## Структура vault

Рекомендуемая структура для каждого проекта:

```text
vaults/
  project-slug/
    00-home/
      index.md
      glossary.md
      navigation.md
      project-map.md
    01-sessions/
      human/
      agents/
      meetings/
      extracted-decisions/
    02-tasks/
      board.md
      backlog/
      active/
      blocked/
      done/
      canceled/
    03-product/
      domain/
      requirements/
      user-stories/
      constraints/
    04-architecture/
      adr/
      rfc/
      diagrams/
      integrations/
    05-code/
      code-map.md
      modules/
      api/
      schemas/
      repositories/
      snippets/
    06-data/
      datasets/
      metrics/
      lineage/
      experiments/
    07-errors/
      error-catalog.md
      incidents/
      bugs/
      postmortems/
      fixes/
    08-operations/
      runbooks/
      deployments/
      environments/
      access/
    09-research/
      market/
      technical/
      alternatives/
    90-archive/
    99-inbox/
    _system/
      templates/
      schemas/
      scripts/
```

### Назначение папок

| Папка | Что хранить | Что не хранить |
| --- | --- | --- |
| `00-home/` | Главные карты, глоссарий, навигация, обзор проекта | Детальные обсуждения, сырые логи |
| `01-sessions/` | Сессии общения с человеком, агентные сессии, встречи, извлеченные выводы | Финальные решения без переноса в ADR/task |
| `02-tasks/` | Небольшая Jira: задачи, статусы, блокеры, acceptance criteria | Общие заметки без action item |
| `03-product/` | Домен, требования, user stories, ограничения | Архитектурные решения и кодовые детали |
| `04-architecture/` | ADR, RFC, диаграммы, интеграции | Временные обсуждения без решения |
| `05-code/` | Карта кода, описание модулей, API, схем, ссылки на repo/commit | Полные копии исходного кода без необходимости |
| `06-data/` | Датасеты, метрики, lineage, эксперименты | Секреты, персональные данные, сырые дампы без политики доступа |
| `07-errors/` | Ошибки, баги, инциденты, postmortem, исправления | Непроверенные сведения без источника |
| `08-operations/` | Runbooks, деплой, окружения, доступы без секретов | Пароли, токены, приватные ключи |
| `09-research/` | Исследования, альтернативы, внешние ссылки | Принятые решения без переноса в ADR |
| `90-archive/` | Устаревшие материалы | Активные требования и решения |
| `99-inbox/` | Временный входящий буфер | Постоянные документы |
| `_system/` | Шаблоны, схемы, служебные скрипты | Проектные знания для retrieval |

### Правила размещения файлов

Чтобы файлы не расползались по vault:

1. Любой новый файл сначала попадает в правильную доменную папку или в `99-inbox/`, если тип пока неясен.
2. В `99-inbox/` файл живет только до ближайшей разборки базы знаний. После этого его нужно переместить, удалить или заархивировать.
3. Сессия общения не считается финальным знанием. Из нее нужно извлекать задачи, решения, требования, ошибки и переносить их в соответствующие папки.
4. Решение не остается только в сессии или задаче. Если оно влияет на архитектуру или продукт, создается ADR или requirement.
5. Ошибка не остается только в задаче. Для повторяемых или важных ошибок создается запись в `07-errors/`.
6. Код не дублируется целиком в vault. В `05-code/` хранится карта кода, контракты, важные snippets, ссылки на файлы, commits и PR.
7. Архивные документы переносятся в `90-archive/` и получают `status: archived`.

### Навигация для человека

В каждом крупном разделе должен быть индекс:

```text
00-home/project-map.md
02-tasks/board.md
04-architecture/adr/index.md
05-code/code-map.md
07-errors/error-catalog.md
```

Индекс отвечает на вопросы:

- что здесь лежит;
- какие документы читать первыми;
- какие документы активны;
- какие документы устарели;
- с чем связан раздел.

## Рабочие области проекта

### Сессии общения

Сессия - это журнал взаимодействия с человеком, агентом или командой. Она нужна для трассировки контекста, но не должна становиться единственным источником истины.

Рекомендуемый путь:

```text
01-sessions/human/2026-05-19-rag-process.md
01-sessions/agents/2026-05-19-indexing-design.md
01-sessions/meetings/2026-05-19-sync.md
```

После сессии агент или человек должен извлечь:

- новые задачи -> `02-tasks/`;
- принятые решения -> `04-architecture/adr/` или `03-product/requirements/`;
- обнаруженные ошибки -> `07-errors/`;
- изменения в карте кода -> `05-code/code-map.md`;
- новые термины -> `00-home/glossary.md`.

### Задачи как небольшая Jira

`02-tasks/` хранит легковесный task tracker для синхронизации и контроля.

```text
02-tasks/
  board.md
  backlog/TASK-0001-add-rag-indexer.md
  active/TASK-0002-design-agent-policy.md
  blocked/TASK-0003-select-vector-db.md
  done/TASK-0004-create-vault-structure.md
```

Минимальный lifecycle:

```text
backlog -> active -> blocked -> done
                 \-> canceled
```

`board.md` содержит ссылки на задачи по статусам. Каждый task-файл содержит:

- problem statement;
- expected outcome;
- acceptance criteria;
- links to sessions, ADR, code, data, errors;
- owner;
- status;
- next action.

### ADR

ADR фиксирует решение, которое должно пережить сессию и задачу.

Рекомендуемый путь:

```text
04-architecture/adr/ADR-0001-use-obsidian-as-source-of-truth.md
```

ADR должен содержать:

- context;
- decision;
- alternatives;
- consequences;
- related tasks;
- related sessions;
- supersedes / superseded_by.

### Код

`05-code/` не заменяет репозиторий. Он описывает, как человеку и агенту ориентироваться в коде.

Хранить:

- карту репозиториев и модулей;
- владельцев модулей;
- публичные API и контракты;
- схемы данных;
- важные snippets с объяснением;
- ссылки на файлы, commits, PR и ADR.

Не хранить:

- полные копии репозитория;
- сгенерированные файлы;
- секреты;
- большие vendor-зависимости.

### Данные

`06-data/` описывает данные, на которые опирается проект:

- датасеты;
- источники данных;
- владельцев;
- freshness/SLA;
- lineage;
- метрики;
- эксперименты;
- ограничения доступа.

Если данные чувствительные, в vault хранится описание и ссылка на защищенное хранилище, а не сами данные.

### Ошибки и инциденты

`07-errors/` нужен, чтобы агент не решал одну и ту же проблему заново.

Рекомендуемая структура:

```text
07-errors/
  error-catalog.md
  bugs/BUG-0001-rag-index-duplicates.md
  incidents/INC-0001-vector-db-outage.md
  postmortems/PM-0001-indexing-regression.md
  fixes/FIX-0001-stable-content-hash.md
```

Запись об ошибке должна содержать:

- симптомы;
- affected area;
- root cause, если известен;
- workaround;
- permanent fix;
- related task;
- related ADR;
- verification;
- статус.

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
- `type` - тип знания: `index`, `session`, `task`, `domain`, `requirement`, `adr`, `decision`, `code`, `data`, `error`, `research`, `operation`, `archive`.
- `status` - `draft`, `active`, `deprecated`, `archived`.
- `updated` - дата последнего осмысленного обновления.
- `retrieval.index` - можно ли индексировать заметку.

## Типы знаний и поведение retrieval

| Type | Назначение | Когда использовать |
| --- | --- | --- |
| `index` | Карта проекта и навигация | В начале новой задачи, при выборе области поиска |
| `session` | Сессия общения, встречи, агентные логи | Для восстановления контекста и поиска исходного обсуждения |
| `task` | Легковесная Jira-задача | При планировании, синхронизации статуса, проверке acceptance criteria |
| `domain` | Термины и бизнес-правила | При обсуждении предметной области и требований |
| `requirement` | Требования и ограничения | При реализации функциональности и проверке поведения |
| `adr` | Архитектурное решение | При выборе технического подхода и проверке уже принятых решений |
| `decision` | Продуктовое или процессное решение | Когда решение не является архитектурным ADR |
| `code` | Карта кода, API, схемы, snippets | При реализации, ревью, поиске владельцев и контрактов |
| `data` | Датасеты, метрики, lineage, эксперименты | При аналитике, ML/RAG, проверке источников данных |
| `error` | Ошибки, баги, инциденты, fixes | При отладке и поиске известных проблем |
| `research` | Исследования и альтернативы | При анализе вариантов и внешнего контекста |
| `operation` | Инструкции и runbooks | При деплое, поддержке, доступах и эксплуатации |
| `archive` | Устаревшие материалы | Только если агент явно ищет исторический контекст |

## Шаблоны ключевых документов

Шаблоны лучше хранить в `_system/templates/` и копировать при создании новых файлов. Это делает документы однотипными и облегчает поиск.

### Session

```markdown
---
project: analytics-platform
type: session
status: active
created: 2026-05-19
updated: 2026-05-19
participants:
  - human
  - agent
related_tasks: []
related_adr: []
retrieval:
  index: true
  priority: normal
---

# Сессия: тема

## Цель

## Обсуждение

## Решения для извлечения

## Задачи для создания

## Ошибки / риски

## Ссылки
```

### Task

```markdown
---
project: analytics-platform
type: task
status: active
owner: product
created: 2026-05-19
updated: 2026-05-19
task_id: TASK-0001
priority: medium
related_sessions: []
related_adr: []
related_code: []
related_errors: []
retrieval:
  index: true
  priority: high
---

# TASK-0001: краткое название

## Problem

## Expected outcome

## Acceptance criteria

- [ ] ...

## Current status

## Next action

## Links
```

### ADR

```markdown
---
project: analytics-platform
type: adr
status: active
created: 2026-05-19
updated: 2026-05-19
adr_id: ADR-0001
supersedes: []
superseded_by: []
related_tasks: []
retrieval:
  index: true
  priority: high
---

# ADR-0001: решение

## Context

## Decision

## Alternatives

## Consequences

## Links
```

### Error / Incident

```markdown
---
project: analytics-platform
type: error
status: active
created: 2026-05-19
updated: 2026-05-19
error_id: BUG-0001
severity: medium
affected_area: rag-indexing
related_tasks: []
related_code: []
related_adr: []
retrieval:
  index: true
  priority: high
---

# BUG-0001: краткое название

## Symptoms

## Root cause

## Workaround

## Permanent fix

## Verification

## Links
```

## Связи между документами

Для человека и агента важны не только папки, но и граф связей. В каждом документе рекомендуется использовать два слоя связей:

1. Obsidian wikilinks в тексте: `[[ADR-0001-use-obsidian-as-source-of-truth]]`.
2. Структурные поля во frontmatter: `related_tasks`, `related_adr`, `related_code`, `related_errors`, `related_sessions`.

Минимальный граф проекта:

```text
session -> task -> ADR / requirement -> code / data -> error / operation
```

Если агент работает с задачей, он должен подтянуть связанные ADR, code notes, data notes и известные ошибки перед тем, как предлагать реализацию.

## Индексация

### 1. Discovery

Pipeline сканирует только vault конкретного проекта:

```text
vaults/{project-slug}/**/*.md
```

Файл пропускается, если:

- `retrieval.index: false`;
- `status: archived` и запрос не требует архивных данных;
- файл лежит в `90-archive/` и нет отдельного archive-index режима;
- файл лежит в `_system/`, потому что шаблоны и схемы не являются проектным знанием;
- файл лежит в `99-inbox/` и не прошел разборку, если для проекта включена строгая индексация только curated notes.

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
- нужно понять статус задачи или синхронизироваться с легковесной Jira в `02-tasks/`;
- нужно восстановить контекст прошлой сессии общения;
- нужно понять структуру кода, владельцев модулей, API или схемы;
- нужно проверить данные, метрики, lineage или эксперименты;
- нужно найти известную ошибку, incident, workaround или permanent fix;
- есть риск принять решение по памяти без актуального источника;
- агент видит ссылку на Obsidian note, task id, ADR id, error id, requirement id или project slug.

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
