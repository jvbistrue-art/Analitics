# Учебник: Harness Engineering для самоулучшающихся AI-агентов

**Уровень:** средний  
**Источники:**
- [Stanford CS329A — Self-Improving AI Agents](https://www.youtube.com/playlist?list=PLangBM27OtEA) ([сайт курса](https://cs329a.stanford.edu/))
- [DAIR.AI Academy — Harness Engineering Paper Collection](https://academy.dair.ai/papers/collections/harness-engineering?view=latest)

**Как читать:** главы идут от базового цикла «сэмплинг → проверка → улучшение» к памяти, планированию, самомодификации harness и оценке. В конце каждой главы — три вопроса для самопроверки; краткие ответы — в приложении.

---

## Оглавление

1. [Что такое Harness Engineering](#глава-1-что-такое-harness-engineering)
2. [V0 harness: от сэмплинга к reasoning](#глава-2-v0-harness-от-сэмплинга-к-reasoning)
3. [Test-time compute: масштабирование на инференсе](#глава-3-test-time-compute-масштабирование-на-инференсе)
4. [Верификация: как отличать хороший ответ](#глава-4-верификация-как-отличать-хороший-ответ)
5. [Инструменты, ReAct и обратная связь среды](#глава-5-инструменты-react-и-обратная-связь-среды)
6. [Память и управление контекстом](#глава-6-память-и-управление-контекстом)
7. [Планирование и многошаговое рассуждение](#глава-7-планирование-и-многошаговое-рассуждение)
8. [Самоулучшающиеся harnesses](#глава-8-самоулучшающиеся-harnesses)
9. [Оркестрация, multi-agent и deep research](#глава-9-оркестрация-multi-agent-и-deep-research)
10. [Оценка агентов и long-horizon задачи](#глава-10-оценка-агентов-и-long-horizon-задачи)
11. [Безопасность и устойчивость harness](#глава-11-безопасность-и-устойчивость-harness)
12. [Практический дизайн harness](#глава-12-практический-дизайн-harness)

---

## Глава 1. Что такое Harness Engineering

### 1.1. Модель — не вся система

В CS329A подчёркивается сдвиг: прирост качества агентов всё чаще приходит не из переобучения весов, а из **системы вокруг модели**. Эту систему называют **harness** (обвязка): цикл генерации, инструменты, память, верификаторы, оркестрация и среда.

Коллекция DAIR формулирует поле так: *research on the systems around model weights* — agent loops, context, tools, memory, orchestration, verification, environments, harness optimization.

Практический смысл: одна и та же LLM при разной обвязке может дать сильно разный результат. На одинаковых весах harness может поднять качество на порядки (в материалах YC/DAIR для ARC-AGI-3 приводят пример скачка порядка 30% → 95%+ при смене harness, без смены модели).

### 1.2. Агент vs «голая» LLM

| | LLM | Агент |
|---|---|---|
| Цель | завершить текст | достичь цели в среде |
| Действия | токены | токены + tool calls + состояние |
| Обратная связь | обычно нет | наблюдения, тесты, судьи |
| Улучшение | один проход | plan → act → observe → verify → correct |

Агент — это **цель + среда + петля обратной связи**. Harness — код и политики, которые эту петлю организуют.

### 1.3. Базовый цикл Harness Engineering

```
Цель
  → генерация кандидатов / плана
  → действие в среде (tools, код, поиск)
  → наблюдение
  → верификация / оценка
  → коррекция (retry, refine, память, обучение)
  → повтор
```

Усилить модель = улучшить первый шанс. Усилить harness = улучшить **весь цикл**.

### 1.4. Две эпохи обвязки (по DAIR)

1. **Static harnesses** — код обвязки фиксирован; растёт action space (поиск, tools, self-critique, память, sub-agents).
2. **Learning harnesses** — оптимизируются промпты, scaffolding, а затем и сам код harness (DSPy, GEPA, Darwin Gödel Machine, Meta-Harness, Continual Harness).

### Вопросы для проверки

1. Чем harness отличается от весов модели, и почему качество агента нельзя сводить к «какой LLM взяли»?
2. Перечислите шаги базового цикла plan → act → observe → verify → correct и для каждого приведите пример из coding-агента.
3. В чём разница между static harness и learning harness?

---

## Глава 2. V0 harness: от сэмплинга к reasoning

### 2.1. Минимальная обвязка

До «агентов» harness был простым:

1. цикл `while not EOS`;
2. sampling (например top-p);
3. среда, которая оценивает текст после разделителя.

Базовая точка отсчёта — GPT-2 / unsupervised multitask learners: нет tools, нет памяти, только генерация.

### 2.2. Первое место для инженерии — контекст

**Few-shot** (GPT-3): в контекст кладут примеры. Цикл не меняется, но accuracy растёт. Вывод DAIR: *context window — первое место, куда инженер может вложить усилия*. Все последующие техники — потомки этой идеи.

### 2.3. Chain-of-Thought как вмешательство в output space

CoT «размазывает» вычисление по токенам вместо ответа в один шаг. Это первое системное вмешательство в пространство вывода: harness начинает **бюджетировать токены**, а не только число вызовов модели.

Связь с CS329A: появление CoT и emergent capabilities у крупных моделей — фундамент для test-time scaling. Большая модель не просто «умнее», она делает рабочими стратегии вроде CoT и few-shot.

### 2.4. Post-training pipeline (кратко)

Современный chat/agent foundation обычно строится так:

1. pre-training (next-token);
2. SFT / instruction tuning;
3. RLHF / RLAIF;
4. затем — agent harness поверх aligned модели.

Прыжок ChatGPT относительно «сырого» GPT-3 во многом обязан alignment stack, а не только размеру. Harness Engineering продолжает эту линию **вне** весов: на инференсе и в runtime-политиках.

### Вопросы для проверки

1. Почему few-shot можно считать первой формой harness engineering, хотя код цикла sampling не менялся?
2. Как CoT меняет то, что harness должен планировать (бюджет токенов vs число вызовов)?
3. Какую роль играет post-training относительно последующей agent-обвязки?

---

## Глава 3. Test-time compute: масштабирование на инференсе

### 3.1. Идея «infinite monkeys»

Модель часто уже «содержит» правильный ответ, но не выдаёт его с первого сэмпла. Test-time compute поднимает покрытие за счёт:

- **parallel scaling** — K независимых сэмплов;
- **sequential scaling** — итеративное улучшение одной траектории;
- **search / branching** — дерево альтернатив.

CS329A ставит inference scaling рядом с pre-training как ось прогресса.

### 3.2. Coverage и power law

Если есть автоматический verifier, полезно смотреть **coverage**: доля задач, где хотя бы один из K сэмплов верен.

Эмпирически coverage часто следует степенному закону вида  
`C(K) ≈ 1 − A · K^(−B)`.  
Pass@k на одной задаче растёт экспоненциально от pass@1; агрегированный закон возникает из длинного хвоста трудных задач с низким pass@1.

Следствие для инженера: маленький open-model + большой K + хороший verifier иногда бьёт более крупную закрытую модель с K=1.

### 3.3. Generation–verification gap

Покрытие растёт с K, но дешёвые селекторы (majority vote) рано выходят на плато (~10–50 сэмплов): на сложных задачах правильный ответ редок, голосование за финальный ответ его не находит.

Иерархия селекторов (от слабого к сильному):

1. majority vote по финальному ответу;
2. reward model / LLM-as-judge по полному решению;
3. process supervision (пошаговые оценки);
4. идеальный oracle-verifier (unit tests, exact match, formal check).

Разрыв между «хотя бы один сэмпл верный» и «селектор его выбрал» — **generation–verification gap**. Без его сужения test-time compute тратится впустую.

### 3.4. Parallel vs sequential: когда что брать

| Режим | Сильные стороны | Слабые стороны |
|---|---|---|
| Parallel (best-of-N) | разнообразие гипотез | дорого; нужен хороший selector |
| Sequential (self-refine) | дешевле на локальных ошибках | застревает на неверной стратегии |
| Branching search | recovery от ранних ошибок | сложнее инженерить и бюджетировать |

Практическое правило: если ошибка локальная — sequential feedback; если нужен другой подход — parallel/search.

### Вопросы для проверки

1. Что такое coverage и чем оно отличается от pass@1 при majority voting?
2. Почему majority vote часто выходит на плато раньше, чем растёт coverage?
3. Когда self-refine выгоднее best-of-N по отношению «прирост качества / число API-вызовов»?

---

## Глава 4. Верификация: как отличать хороший ответ

### 4.1. Почему verification — узкое место

Тезис CS329A и DAIR: генерация часто опережает способность надёжно выбрать правильный ответ. Поэтому harness engineering почти всегда сводится к вопросу: **какой сигнал проверки дёшев и достаточно надёжен в вашей домене?**

### 4.2. Типы верификаторов

**Outcome Reward Model (ORM)** — оценка всего решения целиком.  
**Process Reward Model (PRM)** — оценка шагов рассуждения. PRM снижает false positives, когда неверная цепочка случайно даёт верный финал.

**Discriminative verifier** — отдельная модель/голова, скорящая решение.  
**Generative verifier / LLM-as-judge** — модель читает кандидатов и выбирает лучшего.  
**Environment verifier** — unit tests, компилятор, точное совпадение числа, formal proof checker.

На практике для кода иерархия надёжности обычно такая:

`execution tests > LLM judge > synthetic weak tests > self-critique`

### 4.3. Generator vs verifier sizing

Эмпирический паттерн: крупный generator + меньший verifier часто лучше, чем маленький generator + огромный verifier — генерация в среднем труднее проверки. Pareto-оптимальное распределение compute между ними — открытая инженерная задача.

### 4.4. Слабые верификаторы и их риски

Синтетические unit tests (LLM пишет тесты по docstring) — полезный weak verifier, но:

- тесты могут неверно интерпретировать требования;
- ground-truth решение может «падать» на плохих тестах;
- агент может подогнать код под слабые тесты (reward hacking).

Поэтому harness должен разделять: **filter signal** (для поиска/ранжирования) и **final acceptance** (для отчёта/деплоя).

### Вопросы для проверки

1. В чём практическая разница ORM и PRM на примере математической задачи с «удачно угаданным» финальным числом?
2. Почему для coding-агентов execution feedback считается золотым стандартом верификации?
3. Какие риски возникают, если synthetic unit tests одновременно и обучающий сигнал, и критерий приёмки?

---

## Глава 5. Инструменты, ReAct и обратная связь среды

### 5.1. Рост action space (static harness era)

DAIR описывает шесть лет одной и той же операции: **дать циклу новое разрешённое действие**, не меняя код harness:

- WebGPT — браузер как действие;
- Toolformer — вызов внешнего инструмента вместо вычисления «в весах»;
- ReAct — чередование thought / action / observation;
- Self-Refine — внутренняя критика без среды;
- Reflexion — вербализация reward среды в контекст;
- InterCode — интерактивный coding loop с execution feedback;
- multi-agent spawn — другой агент как tool;
- Voyager — библиотека навыков;
- MemGPT — CRUD над собственной памятью/контекстом;
- Recursive LMs — LLM-вызов как программируемый ресурс.

### 5.2. ReAct как форма современного цикла

```
Thought → Action(tool) → Observation → Thought → ...
```

Thought планирует; action обращается к среде; observation заземляет следующий шаг. На knowledge-intensive задачах это снижает галлюцинации относительно чистого CoT.

Важный современный нюанс из DAIR: модели всё чаще умеют ReAct «нативно», поэтому harness не обязан жёстко навязывать формат — важнее надёжные tools, observation formatting и stop/verify политики.

### 5.3. RLEF и execution feedback

**RLEF (Reinforcement Learning from Execution Feedback)** для кода:

1. сгенерировать код;
2. прогнать тесты;
3. использовать pass/fail (+ traceback) как сигнал для retry и/или обучения.

Это code-аналог math verifier: дешёвый, объективный, масштабируемый. Именно поэтому coding agents стали «лабораторией» harness engineering.

### 5.4. Три источника feedback

| Источник | Пример | Когда уместен |
|---|---|---|
| Среда | unit tests, API, симулятор | есть автоматическая проверка |
| Человек / preference | RLHF | субъективные критерии |
| Self-critique | Constitutional AI, Self-Refine | нет дешёвого oracle |

Harness выбирает не «лучший в абсолюте», а **самый надёжный дешёвый сигнал** для домена.

### Вопросы для проверки

1. Чем ReAct отличается от «сначала подумать CoT, потом один tool call»?
2. Почему Reflexion называют мостом к self-improving harnesses?
3. Сопоставьте Constitutional AI и RLEF: какой feedback у каждого и где каждый сильнее?

---

## Глава 6. Память и управление контекстом

### 6.1. Контекст — не бесконечный лог

Ранний harness только **дописывал** transcript. Это ломается на long-horizon задачах: шум растёт, инструкции размываются, стоимость токенов взрывается.

**MemGPT**-идея: дать модели операции create/read/update/delete над выделенной областью состояния — превратить transcript в **управляемое состояние**.

В актуальной DAIR-коллекции рядом стоят темы:

- multi-resolution / folding контекста;
- decision-time memory (utility, а не только relevance);
- write-time preserve / read-time resolve конфликтов;
- compaction, decay, reinforcement;
- hierarchical memory для структурированных данных.

### 6.2. Working memory vs long-term memory

Практическая двухслойная схема:

1. **Working memory** — текущий план, последние наблюдения, активные constraints.
2. **Long-term memory** — навыки, факты о пользователе/проекте, успешные/провальные эпизоды.

Retrieval должен учитывать **utility at decision time**, а не только semantic similarity. Иначе агент достаёт «похожее», но бесполезное для текущего шага.

### 6.3. Ловушки памяти

Исследования вроде *Memory Trap* показывают: агенты могут **переобобщать** из безобидных прошлых взаимодействий. Compaction handoff summaries может превращать краткое резюме в несанкционированную «политику».

Инженерные правила:

- разделять факты, гипотезы и инструкции;
- версионировать память;
- проверять retrieved items перед исполнением;
- не давать summary права молча менять system policy.

### 6.4. Skills как процедурная память

Voyager-паттерн: цепочка действий → проверка в среде → запись skill в библиотеку → поиск skill позже. Современные `SKILLS.md` / skill routers — прямой наследник этой идеи.

Хороший skill:

- имеет precondition и postcondition;
- проверен хотя бы одним verifier;
- версионируется и может быть откатан.

### Вопросы для проверки

1. Почему «просто длинный контекст» не заменяет memory management в long-horizon агентах?
2. Чем relevance retrieval отличается от utility-based memory selection?
3. Какие риски появляются, если handoff summary начинает трактоваться как новые инструкции?

---

## Глава 7. Планирование и многошаговое рассуждение

### 7.1. Почему одного ReAct мало

На длинных задачах ошибка на шаге `t` каскадом портит `t+1…T`. Нужны:

- декомпозиция;
- ветвление;
- backtracking;
- reflection по провалившимся веткам.

### 7.2. LATS / MCTS-style search

**Language Agent Tree Search (LATS)** объединяет LLM-политику с tree search:

- узлы = состояния;
- LLM предлагает действия и оценивает ценность;
- UCT балансирует exploration/exploitation;
- backpropagation обновляет оценки;
- reflection превращает провал в constraint для новых веток.

Это **branching test-time compute**: дороже flat best-of-N, но лучше восстанавливается после ранних ошибок.

### 7.3. Adaptive planning

Не всегда нужен полный план заранее:

- **ADaPT**-стиль: декомпозировать по необходимости;
- interleaved planning + parallel execution (где независимость подзадач позволяет);
- adaptive branching: шире искать на трудных узлах, глубже — когда verifier локально уверен.

### 7.4. Бюджет поиска

Инженерный checklist:

1. Есть ли node-level verifier/heuristic?
2. Какова цена expand vs resample sibling?
3. Можно ли кэшировать наблюдения tools?
4. Когда остановиться (pass, confidence, token budget, wall clock)?

Без stop-политики дерево поиска превращается в дорогой бесконечный цикл.

### Вопросы для проверки

1. Почему success probability без recovery roughly ведёт себя как `p^T` на T зависимых шагах?
2. Какую роль играет reflection в tree search агента?
3. Когда flat parallel sampling предпочтительнее LATS-подобного дерева?

---

## Глава 8. Самоулучшающиеся harnesses

### 8.1. От фиксированной обвязки к оптимизируемой

DAIR-секция *Let the harness learn* описывает эскалацию:

1. **DSPy** — поиск/компиляция промптов и пайплайнов по train set;
2. **GEPA** — reflective prompt evolution по failed traces (часто дешевле RL по числу rollouts);
3. **Darwin Gödel Machine** — эволюция кода scaffolding/агента через archive + бенчмарки;
4. **Meta-Harness** — harness, который пишет/переписывает harness вокруг фиксированной модели;
5. **Continual Harness** — онлайн-адаптация памяти, skills, prompts (и иногда весов) во время работы.

### 8.2. Train-time scaling как обратная сторона test-time

CS329A замыкает петлю:

```
модель → sample → verify → filter successes → SFT/RL → лучшая модель
```

Методы вроде STaR, rejection sampling + fine-tune, GRPO на verifiable rewards показывают: в доменах с дешёвым oracle меньшая модель + train-time compute может догонять более крупную.

Ограничение: verifiable-only training сильнее в math/code; перенос в субъективные домены не гарантирован.

### 8.3. Open-ended self-improvement

Работы вроде AI Scientist / AlphaEvolve / automated design of agentic systems расширяют цикл до:

- генерации новых задач/экспериментов;
- модификации собственных процедур;
- архивирования успешных вариантов.

Ключевой сдвиг относительно классической Gödel machine: вместо формального proof of improvement — **эмпирическая валидация** на бенчмарках/среде.

### 8.4. Опасности самомодификации

- reward hacking под слабый evaluator;
- collapse diversity (один стиль решений);
- необратимые плохие правки harness;
- «улучшение» на offline-метрике и деградация online.

Поэтому современные AHE-подходы (Agentic Harness Engineering) требуют: revertible components, structured experience, проверяемые predictions/contracts на каждое изменение.

### Вопросы для проверки

1. Чем DSPy-оптимизация промпта отличается от ручного prompt engineering?
2. Почему Meta-Harness может улучшать результат без изменения весов LLM?
3. Какие механизмы безопасности нужны, если агент редактирует собственный scaffolding?

---

## Глава 9. Оркестрация, multi-agent и deep research

### 9.1. Оркестрация как часть harness

Оркестрация решает: кого вызвать, с каким контекстом, когда остановиться, как слить результаты.

Типичные паттерны:

- **router** — выбрать tool/API/модель;
- **decompose → parallel workers → fuse**;
- **iterative refinement** — новый sub-query, пока не хватает фактов;
- **manager/worker** — руководитель держит цель, исполнители делают узкие шаги;
- **debate/critics** — повышение diversity и проверка.

Исследования вроде *Lost in Delegation* показывают: делегирование не бесплатно — теряется intent, растёт ошибка handoff.

### 9.2. Deep research agents

Продуктовый паттерн long-horizon research:

1. декомпозировать вопрос;
2. искать и читать много источников;
3. извлекать факты с цитатами/датами;
4. синтезировать отчёт;
5. при необходимости запускать следующий hop поиска.

Это ReAct + retrieval + synthesis на длинном горизонте. Верификация здесь сложнее QA: нужны citation integrity, temporal accuracy, отсутствие «сшитых» галлюцинаций.

### 9.3. AlphaCode-урок про масштаб

Industrial coding success часто выглядит как:

`огромный sampling → filter tests → cluster by behavior → submit`

То есть self-improvement «в проде» нередко = test-time compute + verification + selection, а не мистическая рекурсивная самопереписка.

### 9.4. Requirement integrity в handoffs

В multi-agent системах критичен контракт передачи задачи:

- что является requirement;
- что — гипотеза;
- что уже verified;
- какие tools/permissions у следующего агента.

Без этого «signed but not safe»: формально handoff есть, но цель уже искажена.

### Вопросы для проверки

1. Какие failure modes появляются при делегировании подзадач другому агенту?
2. Чем deep research verification отличается от math/code verification?
3. Почему clustering по поведению программ полезен после массового sampling в competitive coding?

---

## Глава 10. Оценка агентов и long-horizon задачи

### 10.1. Сдвиг бенчмарков

Одношаговые QA-сеты насыщаются. CS329A смещает фокус к:

- **длине успешно выполняемой задачи** (METR-style time horizon);
- **экономической ценности** (GDPval и аналоги);
- live / long-horizon agent benchmarks (research synthesis, software tasks).

DAIR отдельно подчёркивает: harness progress виден, когда растёт горизонт задач, а не только single-turn score.

### 10.2. Compounding errors

Если каждый шаг независим с вероятностью успеха `p`, то для T зависимых шагов без recovery:

`P(success) ≈ p^T`

Даже `p=0.9` на 20 шагах даёт ~12%. Поэтому метрики агента обязаны включать recovery: replanning, verify, backtrack.

### 10.3. Многомерная оценка

Оценивайте не только correctness:

- tokens / latency / $ cost;
- tool-use quality;
- robustness к шуму среды;
- compliance / safety;
- human preference на final artifact.

Harness A может быть чуть хуже по accuracy, но в 5× дешевле и стабильнее — и выиграть в продукте.

### 10.4. Как измерять self-improvement

Смотрите динамику:

- pass@1 до/после refine loop;
- качество across episodes (continual harness);
- ablation: убрать memory / verifier / search и измерить дельту;
- cost-success Pareto, а не один score.

### Вопросы для проверки

1. Почему saturated single-shot benchmark плохо измеряет прогресс harness engineering?
2. Как оценить, помогает ли ваш recovery-механизм против compounding errors?
3. Что такое cost-success Pareto для сравнения двух harness на одной модели?

---

## Глава 11. Безопасность и устойчивость harness

### 11.1. Harness меняет поведение даже при фиксированных весах

Работы в духе *The Harness Is the Model* показывают: scaffolding влияет на compliance и safety unevenly across models. Значит security review нельзя ограничивать «какой checkpoint».

### 11.2. Tool-using атаки и injection

Классический риск: содержимое tool observation (веб-страница, файл, email) содержит инструкции, которые агент исполняет как system intent.

Защитные паттерны:

- разделять **target admission** и **sanitization** (идея вроде SPILLWAY);
- чёткие trust boundaries для tool outputs;
- allowlists действий / human approval на side effects;
- не смешивать untrusted text с policy без маркировки.

### 11.3. Memory poisoning и policy drift

Агент может записать в память вредоносный «факт» или вредное обобщение. Дальше retrieval усиливает атаку.

Защита:

- authenticate/trust-rank источников памяти;
- accept changes / reject attacks политики на write;
- audit log memory mutations;
- periodic policy re-anchoring к immutable system constitution.

### 11.4. Verification под атакой

Слабый judge можно обмануть риторикой. Поэтому для high-stakes действий:

- требуйте environment-grounded checks;
- разделяйте draft и privileged execution;
- используйте dual control (generator ≠ final approver).

### Вопросы для проверки

1. Почему prompt injection через tool observation опаснее обычного user jailbreak в chat?
2. Какие практики снижают риск memory poisoning?
3. Почему LLM-as-judge недостаточен как единственный gate перед irreversible action?

---

## Глава 12. Практический дизайн harness

### 12.1. Каркас дизайна на одну страницу

1. **Goal schema** — что считать успехом.
2. **Action space** — какие tools реально нужны.
3. **Observation contract** — как среда отвечает и как это парсится.
4. **Verifier stack** — oracle / weak / judge, и что из них final gate.
5. **Control loop** — parallel, sequential, tree, или hybrid.
6. **Memory policy** — что писать, что забывать, что нельзя менять.
7. **Stop & escalation** — budget, human-in-the-loop, fallback.
8. **Eval harness** — те же метрики, что и product success.

### 12.2. Минимальный coding-agent harness

```text
input: issue + repo snapshot
loop:
  plan patch
  edit files
  run tests / linters
  if fail: reflect with traceback → retry
  if pass: create summary + optional review judge
stop: tests green or budget exhausted
memory: store successful fix patterns as skills
```

Здесь сила почти целиком в execution verifier + bounded retry, а не в «магическом промпте».

### 12.3. Минимальный research-agent harness

```text
decompose question
for each subq:
  search → read → extract claims with citations
conflict-check claims
synthesize report
verify: citation exists, dates coherent, unanswered gaps listed
```

Без citation/conflict checks research harness имитирует уверенность, а не качество.

### 12.4. Когда улучшать harness, а когда модель

| Симптом | Скорее harness | Скорее модель/training |
|---|---|---|
| Есть правильные сэмплы, плохой выбор | selector/verifier | — |
| Ломается на длинных задачах | memory, planning, recovery | иногда long-context training |
| Нет сигнала проверки | environment design | reward model research |
| Стабильно не умеет доменный skill | skills + SFT/RL на verified traces | да, данные/RL |
| Дорого на простых запросах | router/cascades | distillation |

### 12.5. Чеклист перед продакшеном

- [ ] Есть ли oracle или хотя бы calibrated weak verifier?
- [ ] Есть ли stop conditions и cost caps?
- [ ] Отделяете ли untrusted observations от instructions?
- [ ] Логируете ли trajectories для eval и harness diffs?
- [ ] Есть ли ablation: loop / memory / tools по отдельности?
- [ ] Измеряете ли horizon и cost, а не только pass@1?

### Вопросы для проверки

1. Спроектируйте verifier stack для агента, который правит SQL-миграции в продакшен-БД.
2. Какие stop conditions вы зададите deep research агенту на 30-минутный бюджет?
3. Как по ablation понять, что узкое место — память, а не generator?

---

## Приложение A. Краткие ответы на вопросы глав

### Глава 1
1. Harness — runtime-система вокруг весов (цикл, tools, memory, verify). Одна модель в разных harness даёт разное качество.  
2. Plan patch → edit → run tests → observe failures → verify pass/fail → correct and retry.  
3. Static: фиксированный код, растёт action space. Learning: оптимизируются промпты/scaffolding/код harness.

### Глава 2
1. Меняется содержимое контекста (примеры), а это уже инженерное вмешательство в систему вокруг sampling loop.  
2. Harness должен выделять токены на промежуточные рассуждения, а не ждать ответ в один шаг.  
3. Post-training делает модель управляемой/полезной; harness затем организует её поведение в среде.

### Глава 3
1. Coverage — «хотя бы один из K верен»; majority pass@1 — «селектор выбрал верное».  
2. На трудных задачах правильный ответ редок, голосование по финалу его не ловит.  
3. Когда ошибки локальны и критика их чинит; иначе нужнее разнообразие независимых сэмплов.

### Глава 4
1. ORM может принять неверную цепочку с верным финалом; PRM штрафует плохие шаги.  
2. Тесты дают объективный, дешёвый, автоматический сигнал.  
3. Reward hacking и ложная уверенность: код подгоняется под плохие тесты.

### Глава 5
1. ReAct чередует рассуждение и действия многократно с наблюдениями между ними.  
2. Оно записывает сигнал среды обратно в контекст как опыт — семя self-improvement.  
3. Constitutional AI — self-critique по принципам; RLEF — внешний execution signal. Первый — для субъективных/safety целей, второй — для кода/формальных доменов.

### Глава 6
1. Растёт шум, стоимость и drift инструкций; нужен managed state.  
2. Relevance = похожесть; utility = полезность для текущего решения.  
3. Summary может незаметно стать новой политикой и сломать compliance.

### Глава 7
1. Ошибки перемножаются по зависимым шагам без восстановления.  
2. Превращает провал ветки в знания/constraints для следующих expand.  
3. Когда есть сильный final verifier и ошибки не сильно каскадные / пространство гипотез плоское.

### Глава 8
1. DSPy автоматически ищет промпт/пайплайн по метрике на данных.  
2. Он переписывает retrieval/memory/prompt assembly вокруг фиксированной LLM.  
3. Revertible diffs, eval contracts, archive/rollback, запрет необратимых side effects без проверки.

### Глава 9
1. Потеря intent, неполные requirements, error amplification, unsafe privilege inheritance.  
2. Нужны citation/temporal/conflict checks, а не только exact match.  
3. Разные программы с одним поведением избыточны; кластеры повышают diversity submitted решений.

### Глава 10
1. Он не видит рост горизонта работы и recovery на длинных задачах.  
2. Сравнить success vs T с/без replanning-verify-backtrack при той же per-step модели.  
3. Кривая качества против стоимости; доминирующие точки на Pareto front.

### Глава 11
1. Observation часто имеет высокий trust и попадает в цикл действий с side effects.  
2. Trust-rank источников, write policies, audit, re-anchor к immutable constitution.  
3. Judge обманывается формой текста; irreversible actions требуют grounded checks/approval.

### Глава 12
1. Пример: dry-run + schema checks + shadowed query tests + human approval; LLM judge только advisory.  
2. Max iterations/sources/tokens, min citation coverage, escalation если gaps остаются.  
3. Если отключение memory резко роняет long-horizon метрики при почти том же short-task pass@1.

---

## Приложение B. Карта источников по главам

| Глава | CS329A | DAIR Harness Collection |
|---|---|---|
| 1 | Course overview, agents vs LLMs | Intro: systems around weights |
| 2 | Pretraining, CoT, post-training | V0 harness: GPT-2/3, CoT |
| 3 | Test-time compute scaling | Inference budgets, sampling |
| 4 | Robust verification | Verifiers, judges, env checks |
| 5 | Tools/code feedback | WebGPT…ReAct…Reflexion…InterCode |
| 6 | Memory guest topics | MemGPT, memory papers 2026 |
| 7 | Planning / LATS | Search, branching, orchestration |
| 8 | RL, open-ended evolution | DSPy→GEPA→DGM→Meta/Continual |
| 9 | Deep research, SE agents | Multi-agent, research harnesses |
| 10 | Agentic evaluations | Long-task measurement papers |
| 11 | Safety themes across course | Security/resilience harness papers |
| 12 | Homeworks as design practice | Prime Agent / OpenJarvis lessons |

---

## Приложение C. Что читать дальше

1. Плейлист CS329A: https://www.youtube.com/playlist?list=PLangBM27OtEA  
2. Сайт курса: https://cs329a.stanford.edu/  
3. Коллекция DAIR Harness Engineering: https://academy.dair.ai/papers/collections/harness-engineering  
4. Базовые paper anchors: ReAct, Reflexion, MemGPT, DSPy, LATS, Measuring Long Tasks  
5. Современные системы-ориентиры коллекции: Prime Agent, OpenJarvis, Meta-Harness, Continual Harness

---

*Учебник подготовлен как конспект среднего уровня по публичным материалам курса CS329A и paper collection DAIR.AI Academy. Это педагогическая компиляция, а не официальный конспект Stanford или DAIR.*
