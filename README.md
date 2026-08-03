# Analitics

Рабочий репозиторий аналитики, методик и внутренних инструментов.

## Материалы

- [Тестирование рассинхрона голоса и видео при классической LTE-телефонии (VoLTE)](docs/av-sync-lte-telephony/README.md)
- Инструмент измерения: [`tools/av_sync_measure`](tools/av_sync_measure/README.md)

## Быстрая проверка инструмента A/V sync

```bash
python3 -m unittest tests.test_av_sync_measure -v
```
