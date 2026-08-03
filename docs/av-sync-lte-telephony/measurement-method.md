# Метод измерения A/V offset

## 1. Идея

На источнике одновременно:

- **flash** — белая вспышка в видео;
- **beep** — короткий тон в голосовой канал (VoLTE).

На приёмнике:

```text
AV_offset_ms = t_beep_playout - t_flash_playout
```

## 2. Почему marker-метод подходит для VoLTE split-path

- Не требует общей NTP-шкалы A и B.
- VoLTE и WebRTC живут в разных стеках: RTP timestamps видео не склеить напрямую с IMS/VoLTE voice path без специального bridging.
- Измеряет реальный playout (включая jitter buffer, decoder, render, telephony DSP).
- Работает, даже если голос прошёл UE → IMS → PSTN/VoLTE peer.

## 3. Параметры стимула

| Параметр | Значение | Зачем |
|---|---|---|
| Период маркера | 3–5 s | разнести пары |
| Flash | 1–2 кадра | уверенный детект |
| Beep | 60–80 ms, 1000 Hz | переживает AMR-WB/NB лучше коротких кликов |
| Амплитуда | высокая, без клиппинга | против NS/AGC телефонии |
| Длина | 60–180 s | 15–50 маркеров |

```bash
python3 -m tools.av_sync_measure generate --output stimulus.mp4 --duration 90 --period 4
```

## 4. Прогон

1. Откалибровать recorder bias.
2. На A подать стимул в камеру + **в микрофон телефонии** (тот же mic, что берёт VoLTE).
3. На B писать экран видеозвонка + telephony speaker/earpiece output.
4. ≥60 с полезного сигнала.
5. До/после подтвердить VoLTE.

Важно: бип должен уйти именно в **телефонный** uplink, а не только в data-аудио приложения.

## 5. Разбор записи

```bash
python3 -m tools.av_sync_measure measure \
  --input receiver_capture.mkv \
  --bias-ms 18 \
  --search-window-ms 1000 \
  --threshold-profile baseline \
  --report report.json
```

Алгоритм:

1. ffmpeg → PCM WAV;
2. onsets бипов по огибающей;
3. вспышки по яркости кадров;
4. matching flash↔beep в окне поиска (для LTE обычно достаточно ±1000 ms; по умолчанию в инструменте ±2000 ms — тоже ок);
5. вычитание `--bias-ms`;
6. mean/median/p95/std + verdict.

## 6. Интерпретация

| Offset | Смысл | Частая причина |
|---|---|---|
| `+180 ms` | голос позже видео | VoLTE playout/jitter buffer > video render delay |
| `-40 ms` | голос чуть раньше | большой video jitter buffer / компенсация |
| скачок на handover | нестабильный sync | смена соты / rebuffer |

Для VoLTE знак чаще положительный, но это нужно **мерить**: data-видео с большим буфером может отставать сильнее голоса.

## 7. Точность

```text
± 0.5 video frame  (@60fps ≈ ±8–17 ms)
± onset detector   (несколько ms на чистом бипе)
± recorder bias    (убирается калибровкой)
```

Для LTE этого достаточно, чтобы решать, нужна ли компенсация и на сколько.

## 8. Альтернативы

- Хлопок в кадре — полевой smoke.
- Инструментизация клиента — онлайн offset; marker-метод остаётся ground truth.
- Высокоскоростная камера на экран+audio LED — избыточно для большинства прогонов.

## 9. Что делать с результатом в продукте

1. Если `|median_offset|` стабильно вне комфортной зоны — video delay buffer ≈ median (EMA).
2. Если большой `std` — сначала стабилизировать voice/video jitter, потом sync.
3. На handover переоценивать offset, не держать старый buffer вечно.
