# av_sync_measure

Инструмент для измерения рассинхрона голоса и видео по маркерам **flash + beep**.

Методика: [docs/av-sync-space-telephony](../../docs/av-sync-space-telephony/README.md).

## Зависимости

- Python 3.10+
- `numpy`
- `ffmpeg` / `ffprobe` в `PATH`

## Быстрый старт

### 1. Сгенерировать стимул

```bash
python3 -m tools.av_sync_measure generate \
  --output /tmp/stimulus.mp4 \
  --duration 30 \
  --period 4 \
  --also-delayed 500
```

Получите:

- `/tmp/stimulus.mp4` — синхронные вспышки и бипы;
- `/tmp/stimulus_audio_delay_500ms.mp4` — имитация «голос через спутник» (аудио +500 ms).

### 2. Прогнать стимул через ваш звонок

- A: играет стимул в камеру/микрофон (или virtual cam/mic).
- B: пишет экран + системный звук → `receiver_capture.mkv`.

### 3. Измерить offset

```bash
python3 -m tools.av_sync_measure measure \
  --input /tmp/stimulus_audio_delay_500ms.mp4 \
  --bias-ms 0 \
  --threshold-profile baseline \
  --report /tmp/report.json
```

В отчёте смотрите:

- `median_offset_ms` — основной показатель (`>0` => голос позже видео);
- `std_offset_ms` — стабильность;
- `match_rate` — качество детекции маркеров;
- `verdict` — по выбранному профилю порогов.

## Профили порогов

| Профиль | Смысл |
|---|---|
| `baseline` | только измерение (`MEASURED_ONLY`) |
| `itu_like` | комфортный lip-sync (−45…+125 ms, std≤40) |
| `sat_compensated` | практичный после компенсации (\|median\|≤100, std≤60) |

## Калибровка recorder bias

Локально проиграйте синхронный стимул и запишите тем же рекордером. Если инструмент показал `+18 ms`, дальше всегда передавайте `--bias-ms 18`.
