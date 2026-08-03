# av_sync_measure

Инструмент для измерения рассинхрона голоса и видео по маркерам **flash + beep**.

Методика для split-path **видео по data + голос по классической LTE-телефонии (VoLTE)**:
[docs/av-sync-lte-telephony](../../docs/av-sync-lte-telephony/README.md).

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
  --also-delayed 250
```

Получите:

- `/tmp/stimulus.mp4` — синхронные вспышки и бипы;
- `/tmp/stimulus_audio_delay_250ms.mp4` — имитация более медленного голосового пути (например VoLTE-like +250 ms).

### 2. Прогнать стимул через ваш звонок

- A: стимул в камеру + в микрофон **телефонного** (VoLTE) канала.
- B: экран видеозвонка + звук telephony/speaker → `receiver_capture.mkv`.
- Подтвердить, что голос идёт по VoLTE, а не Wi‑Fi Calling / CSFB.

### 3. Измерить offset

```bash
python3 -m tools.av_sync_measure measure \
  --input /tmp/stimulus_audio_delay_250ms.mp4 \
  --bias-ms 0 \
  --search-window-ms 1000 \
  --threshold-profile baseline \
  --report /tmp/report.json
```

Смотрите `median_offset_ms` (`>0` => голос позже видео), `std_offset_ms`, `match_rate`, `verdict`.

## Профили порогов

| Профиль | Смысл |
|---|---|
| `baseline` | только измерение (`MEASURED_ONLY`) |
| `itu_like` | комфортный lip-sync (−45…+125 ms, std≤40) |
| `volte_compensated` | после компенсации (\|median\|≤100, std≤60) |

## Калибровка recorder bias

Локально проиграйте синхронный стимул тем же рекордером. Если получили `+18 ms`, дальше используйте `--bias-ms 18`.
