# Метрики и пороги

## 1. Основные метрики

| Метрика | Определение |
|---|---|
| `offset_i_ms` | `t_beep_i - t_flash_i` |
| `mean_offset_ms` | среднее |
| `median_offset_ms` | медиана (основной KPI) |
| `p95_offset_ms` | хвост |
| `std_offset_ms` | стабильность sync |
| `drift_ms_per_min` | уход за длинную сессию |
| `match_rate` | доля вспышек с найденным бипом |

## 2. Пороги восприятия

Ориентиры в духе ITU-R BT.1359 / lip-sync практики:

| Состояние | Ориентир |
|---|---|
| Комфортно | −45…+125 ms (звук относительно видео) |
| Заметно | вне комфортной зоны |
| Ломает UX | ≳ 200–300 ms |
| VoLTE split-path без компенсации | часто десятки–первые сотни ms — измерять baseline |

Для продукта с классической LTE-телефонией:

1. `baseline` — сначала просто измерить факт.
2. После компенсации — целевой бюджет, например `|median_offset| ≤ 100 ms`.

## 3. Профили в инструменте

### `itu_like`

PASS, если `-45 <= median <= 125` и `std <= 40`.

### `volte_compensated`

PASS, если `abs(median) <= 100` и `std <= 60`.

### `baseline`

Всегда `MEASURED_ONLY`.

```bash
--threshold-profile volte_compensated
```

## 4. Сопутствующие наблюдения

- VoLTE confirmed yes/no;
- RSRP/RSRQ / indoor-outdoor;
- handover during run;
- codec AMR-WB/NB;
- video FPS / freezes;
- AEC/NS/AGC on/off.

## 5. Минимум статистики

- ≥ **15** matched markers на короткий прогон;
- `match_rate >= 0.7`, иначе сначала чинить стимул/запись;
- для S5 — маркеры на всей длительности.
