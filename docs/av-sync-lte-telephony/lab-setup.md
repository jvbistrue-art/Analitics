# Лабораторный стенд (VoLTE + video over data)

## 1. Целевая архитектура теста

```text
┌───────────────────────────┐         ┌───────────────────────────┐
│ Sender A                  │         │ Receiver B                │
│                           │         │                           │
│ Stimulus / Camera+Mic ────┼──video──► LTE data / WebRTC ────────┼──► Display
│                           │         │                           │
│ Audio (same stimulus) ────┼──voice──► VoLTE / IMS (or emu) ─────┼──► Speaker
│                           │         │                           │
│                           │         │ Screen+audio recorder ────┼──► capture.mkv
└───────────────────────────┘         └───────────────────────────┘
                                              │
                                              ▼
                                      av_sync_measure
                                      → report.json
```

Измеряем **то, что видит и слышит человек на приёме**, а не только RAN/IMS timestamps.

## 2. Минимальный комплект

- 2 UE/клиента с поддержкой VoLTE.
- На B: запись экрана с системным/internal audio (OBS, scrcpy+audio route, встроенный recorder).
- На A: стимул в virtual cam/mic или экран+динамик перед камерой (хуже).
- SIM/оператор с рабочим IMS/VoLTE на обеих сторонах (или одна сторона VoLTE, вторая — PSTN/VoLTE gateway — зафиксировать в протоколе).

## 3. Как подтвердить, что голос — классическая LTE-телефония

До и после прогона проверить хотя бы 2 признака:

1. Индикатор **VoLTE / HD Voice** во время вызова (не Wi‑Fi Calling).
2. UE в LTE (не упал в 3G/2G CSFB).
3. По возможности: engineering menu / `*#*#4636#*#*` / IMS registration state / QCI=1 dedicated bearer.
4. Если есть доступ к ядру: SIP INVITE/CDR с признаком VoLTE/IMS.

Прогон без подтверждения маршрута считать невалидным для S3.

## 4. Эмуляция VoLTE-delay в офисе

Эмулируйте **только аудио-путь**.

### Вариант A — `tc netem` на voice gateway

```bash
sudo tc qdisc add dev eth0 root netem delay 250ms 20ms distribution normal
# снять:
sudo tc qdisc del dev eth0 root
```

| Профиль | delay | jitter | Пояснение |
|---|---|---|---|
| VoLTE-good | 150 ms | 10 ms | хороший LTE |
| VoLTE-typical | 250 ms | 20 ms | типовой mouth-to-ear вклад |
| VoLTE-stressed | 350 ms | 40 ms + 0.5% loss | плохой радио / PLC |

### Вариант B — audio delay insert в клиенте/шлюзе

Задерживать только PCM голоса на N ms, видео не трогать.

### Вариант C — virtual cable + delay plugin

Для калибровки метода измерения без радиосети.

## 5. Полевой стенд (реальный VoLTE)

Зафиксировать:

- оператор / APN / IMS domain (если известно);
- модель UE A/B и версию клиента;
- RSRP/RSRQ/SINR (хотя бы качественно: indoor/outdoor);
- кодек (AMR-WB предпочтителен для бипа);
- Wi‑Fi **выключен** на время S3, если цель — именно LTE telephony;
- был ли handover.

## 6. Запись на приёмнике

- Video: окно звонка, **30–60 fps**.
- Audio: захват **выхода** («what you hear»), 48 kHz.
- Не писать комнату вторым телефоном — появится акустическая задержка.

## 7. Калибровка recorder bias

1. Локально играть синхронный стимул.
2. Записать тем же рекордером.
3. Измерить offset → это `recorder_bias_ms`.
4. В полевых прогонах: `--bias-ms <значение>`.

```text
true_offset ≈ measured_offset - recorder_bias
```

## 8. Протокол стенда

```yaml
run_id: S3-volte-001
date_utc: 2026-08-03T12:00:00Z
scenario: S3
sender_client: "app 1.4.2 / Android 14 / Pixel"
receiver_client: "app 1.4.2 / Android 14"
video_path: "WebRTC over LTE data"
audio_path: "VoLTE IMS QCI1"
volte_confirmed: true
wifi_calling: false
csfb: false
audio_delay_emulated_ms: null
compensation: off
radio_notes: "RSRP ~ -95 dBm, indoor"
recorder: "OBS 30.1, 60fps, desktop audio"
recorder_bias_ms: 18
capture_file: receiver_capture.mkv
```

## 9. Безопасность

- Только тестовый стимул / согласованный скрипт.
- В git — анонимизированные отчёты, не сырые звонки пользователей.
