# Вычислительный рой: Android + одноплатники для локальных LLM

## Вердикт

**Да, объединить можно** — но не как «один быстрый GPU-кластер», а как **гетерогенный edge-рой** с двумя разными режимами работы:

| Режим | Что даёт | Скорость | Когда уместен |
|-------|----------|----------|---------------|
| **A. Шардинг модели** (layer / tensor parallel) | Одна большая модель, которой не хватает RAM на одном устройстве | Медленно: каждый токен идёт по цепочке узлов | 7B–70B на рое телефонов/Pi, офлайн-чат |
| **B. Рой задач** (task / batch parallel) | Много независимых запросов / маленьких моделей | Линейно растёт с числом узлов | RAG, классификация, эмбеддинги, агентные воркеры |
| **C. Гибрид** | Оркестратор выбирает A или B | Зависит от маршрутизации | Продуктовый «рой» |

Практика 2024–2025 (DistAI, distributed-llama, llama.cpp RPC, CoLLM, JARVIS) подтверждает: **память складывается, FLOPS — почти нет**. Сеть (Wi‑Fi) — главный bottleneck.

---

## 1. Физика ограничений

### 1.1 Память vs скорость

- GGUF Q4_K_M ~0.5–0.6 байт/параметр → 7B ≈ 4–5 ГБ, 13B ≈ 8 ГБ, 70B ≈ 40 ГБ.
- Телефон 8 ГБ RAM реально отдаёт 3–5 ГБ под модель (система, UI, Doze).
- **Шардинг по слоям** (pipeline): activations (~KB–MB на токен) гоняются по сети → latency = Σ(compute_i + RTT_i).
- **Tensor parallel**: нужен быстрый sync (Ethernet/USB); Wi‑Fi убивает выигрыш.

### 1.2 Android-специфика

- Doze / App Standby / battery optimization гасят фоновый inference → нужен foreground service + WakeLock + WifiLock.
- SELinux / W^X: нативные бинарники только из `nativeLibraryDir`.
- Нет стабильного root/SSH на всех устройствах → discovery и агент должны быть приложением.
- Разный SoC (Adreno / Mali / Tensor / MediaTek) → единый backend: **llama.cpp** (CPU Neon/DotProd + опционально Vulkan).

### 1.3 Одноплатники (Pi 4/5, Orange Pi, RK3588…)

- Linux: проще оркестрация (systemd, Docker, SSH).
- Ethernet / USB gadget → лучше для tensor/layer parallel, чем Wi‑Fi телефонов.
- RK3588 / Pi 5 с NPU/GPU — кандидаты в «тяжёлые» узлы роя.

### 1.4 Сеть

| Связь | Ожидание для шардинга |
|-------|------------------------|
| Gigabit Ethernet | Рабочий tensor/layer parallel |
| USB 3 tethering | Приемлемо |
| 5 GHz Wi‑Fi LAN | Терпимо для layer parallel, плохо для tensor |
| 2.4 GHz / mesh | Только режим B (отдельные задачи) |

---

## 2. Существующий стек (не изобретать с нуля)

| Проект | Роль |
|--------|------|
| [llama.cpp](https://github.com/ggerganov/llama.cpp) + **RPC backend** | Базовый runtime шардинга |
| [DistAI](https://github.com/alex8819/DistAi) | Android + Pi/PC, mDNS, auto layer split, OpenAI API |
| [llama-cpp-android-node](https://github.com/adil-adysh/llama-cpp-android-node) | Телефон как RPC worker (Vulkan/CPU) |
| [distributed-llama](https://github.com/b4rtaz/distributed-llama) | Tensor parallel на 2^n узлов (Linux/macOS/Win, Pi) |
| CoLLM / JARVIS (research) | Идеи load-balancing и fault recovery на Pi |

**Рекомендация:** не писать свой tensor engine. Писать **оркестратор роя** поверх llama.cpp RPC / DistAI-паттернов + свой control plane.

---

## 3. Целевая архитектура ПО «рой»

```
┌─────────────────────────────────────────────────────────┐
│  Control Plane (координатор, Linux SBC или PC)          │
│  - registry узлов (capabilities, RAM, battery, RTT)     │
│  - scheduler (режим A / B / C)                          │
│  - model catalog + shard planner                        │
│  - OpenAI-compatible gateway                            │
│  - health / rebalance / drain                           │
└────────────────────┬────────────────────────────────────┘
                     │ gRPC / QUIC / WebSocket
     ┌───────────────┼───────────────────┐
     ▼               ▼                   ▼
┌─────────┐    ┌──────────┐        ┌──────────┐
│ Android │    │ Android  │  ...   │  SBC     │
│ Worker  │    │ Worker   │        │ Worker   │
│ llama   │    │ llama    │        │ llama    │
│ RPC svc │    │ RPC svc  │        │ RPC/svc  │
└─────────┘    └──────────┘        └──────────┘
```

### 3.1 Компоненты

1. **Worker Agent**
   - Android APK + Linux daemon.
   - Регистрирует: arch, RAM free, threads, GPU/Vulkan, battery, thermal, IP.
   - Поднимает `rpc-server` / локальный `llama-server`.
   - Heartbeat, graceful leave при низком заряде/перегреве.

2. **Discovery**
   - LAN: mDNS/DNS-SD (`_llm-swarm._tcp`).
   - Опционально: координатор с фиксированным IP + QR/токен для join.

3. **Scheduler**
   - **Mode B (по умолчанию для Wi‑Fi роя):** очередь задач → sticky/least-loaded worker с моделью в RAM.
   - **Mode A:** при запросе большой модели — собрать shard-set по суммарной RAM и минимальному диаметру сети; зафиксировать pipeline до конца сессии.
   - **Preempt:** телефоны с battery < threshold выходят из шарда, слои переезжают.

4. **Model Store**
   - Координатор держит GGUF; воркеры качают только нужные shards/слои (или полный файл для mode B).
   - Dedup по content-hash; приоритет Ethernet-узлам как seed.

5. **API**
   - `POST /v1/chat/completions`, embeddings, models list.
   - Заголовок/поле `x-swarm-mode: auto|shard|replica`.

6. **Observability**
   - tok/s, queue lag, per-node temp/battery, network hop latency.
   - Простая TUI/web dashboard.

### 3.2 Минимальный MVP (порядок работ)

1. Linux coordinator + Linux workers (Pi) — mode B, одна малая модель на узел.
2. Android worker APK (foreground RPC) — join в тот же registry.
3. OpenAI gateway + простой chat UI.
4. Mode A: llama.cpp RPC pipeline planner (авторазбиение слоёв).
5. Thermal/battery policies + rebalance.
6. (Опционально) tensor parallel только для Ethernet-подгруппы SBC.

---

## 4. Реалистичные сценарии использования

**Хорошо подходит**
- Локальный чат 7B–13B, размазанный по 3–8 телефонам (медленно, но «влезает»).
- Парallel RAG: эмбеддинги + rerank на десятках узлов.
- Ночной batch: суммаризация корпусов документов.
- Edge-агенты: каждый телефон — воркер tool-calling с маленькой моделью.

**Плохо подходит**
- Интерактивный 70B на Wi‑Fi с низкой latency.
- Обучение / fine-tune (нужен другой стек и энергия).
- Ожидание «N телефонов = N× скорость одной карты».

### Грубая оценка (order of magnitude)

- 1× Pi 5, 7B Q4: ~2–8 tok/s (зависит от квантизации/потоков).
- Pipeline 4 телефона, 13B: часто **<1–3 tok/s**, зато модель живёт.
- Mode B, 20 устройств × 3B: ~20 независимых потоков по 5–15 tok/s каждый.

---

## 5. Риски и решения

| Риск | Митигация |
|------|-----------|
| Устройство ушло в Doze | Foreground service, исключение из battery opt |
| Телефон сел / перегрелся | Drain + replan shards |
| Wi‑Fi jitter | Mode B по умолчанию; Mode A только при RTT < порога |
| Гетерогенность SoC | Единый GGUF + llama.cpp; capability scoring |
| Безопасность роя | mTLS / join token; модели только из доверенного store |
| Юр./этика чужих устройств | Только свои устройства; явный opt-in агент |

---

## 6. Предлагаемое имя и репозиторная раскладка

Рабочее имя: **Hive** / **SwarmLLM** / **EdgeHive**.

```
/
  docs/                 # этот дизайн
  coordinator/          # Go или Rust: registry, scheduler, gateway
  worker-linux/         # daemon + install scripts для SBC
  worker-android/       # Kotlin APK, llama.cpp JNI/RPC
  proto/                # gRPC schema
  web-ui/               # минимальный chat + node map
  deploy/               # docker-compose для координатора
```

Стек координатора: **Go** (простые бинарники на Pi) или **Rust**.  
Inference: не трогать — только обвязка вокруг **llama.cpp**.

---

## 7. Решение «делать своё ПО?»

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| Форк/обвязка DistAI + android-node | Быстрый MVP | Android-centric UX, мало mode B |
| Свой control plane + llama.cpp RPC | Рой как продукт, гибрид A/B | Больше кода оркестрации |
| Только distributed-llama на Ethernet SBC | Макс. скорость шардинга | Телефоны почти вне игры |

**Оптимум:** свой тонкий control plane (режим B + планировщик) + готовый llama.cpp RPC для режима A. Не конкурировать с ggml по ядрам.

---

## 8. Следующий шаг

1. Инвентаризация железа: модель, RAM, Wi‑Fi/Eth, Android version / OS.
2. Пилот: 1 координатор + 2–3 Pi в mode B.
3. Подключить 1–2 Android как RPC nodes.
4. Замерить tok/s и RTT → решить, нужен ли Mode A в v1.
