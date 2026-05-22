# Приоритизация и качество в сети мобильного оператора

Этот комплект документов описывает путь трафика от устройства абонента до выхода в интернет/частную сеть и показывает, где в сети применяются политики качества.

## Как читать

1. Начните с нужной технологии: **LTE** или **5G**.
2. Внутри технологии идите по доменам:
   - **Radio/RAN** — радиосеть и базовая станция.
   - **Packet Core** — мобильное ядро и политика bearer/session.
   - **IP после P-GW/UPF** — транспорт, security edge, интернет/enterprise breakout.
3. Для каждого домена есть:
   - обзорная схема;
   - детальная схема;
   - список сокращений с расшифровкой и пояснением;
   - механизмы повышения качества для групп пользователей;
   - где хранится и как управляется конфигурация.

## Документы

### LTE

- [LTE Radio/RAN](lte-radio-ran.md)
- [LTE Packet Core/EPC](lte-packet-core.md)
- [LTE IP после P-GW](lte-ip-after-pgw.md)

### 5G

- [5G Radio/RAN](5g-radio-ran.md)
- [5G Packet Core](5g-packet-core.md)
- [5G IP после UPF](5g-ip-after-upf.md)

### Сквозные темы

- [Несколько QoS-каналов на одном UE](ue-multiple-qos-channels.md)
- [Gold-status в радио сети](gold-status.md)
- [Где хранится QoS-конфигурация и как ей управляют](policy-and-configuration.md)
- [Глоссарий сокращений](glossary.md)

## Главная end-to-end логика

```text
UE
  -> RAN scheduler/admission
  -> mobile packet core policy
  -> IP/MPLS and security edge
  -> Internet / IMS / enterprise / MEC
```

Качество для группы пользователей повышается не одной настройкой, а цепочкой:

```text
subscription/group policy
  -> APN/DNN/slice selection
  -> bearer/QoS Flow with QCI/5QI
  -> ARP and admission control
  -> RAN scheduler priority/resource reservation
  -> packet core shaping/gating/charging
  -> IP QoS, routing, peering, CDN/MEC
```

Коммерческие статусы вроде **gold/silver/bronze** должны быть сначала отражены в BSS/CRM и policy control, а затем превращены в технические параметры: AMBR, QCI/5QI, ARP, scheduler weight, dedicated bearer/QoS Flow или slice. Подробнее: [Gold-status в радио сети](gold-status.md).

На одном UE могут одновременно существовать несколько логических QoS-каналов: в LTE это несколько EPS bearers с разными QCI, в 5G — несколько QoS Flows с разными 5QI/QFI. Подробнее: [Несколько QoS-каналов на одном UE](ue-multiple-qos-channels.md).

## Ключевые различия LTE и 5G

| Область | LTE | 5G |
|---|---|---|
| Логическая сессия | EPS bearer | PDU Session |
| Класс QoS | QCI | 5QI |
| Поток сервиса | Dedicated/default bearer | QoS Flow с QFI |
| Policy control | PCRF/PCC | PCF |
| User-plane enforcement | P-GW/PCEF | UPF + QER/PDR/FAR |
| Сегментация сервисов | APN | DNN + S-NSSAI/slice |
| RAN mapping | EPS bearer -> DRB | QoS Flow -> DRB через SDAP |
| Edge breakout | через P-GW/SGi | через UPF/N6, включая MEC |

## Схемы

Все схемы имеют PlantUML-исходники и SVG-рендеры:

- исходники: [`diagrams/src`](diagrams/src)
- рендеры: [`diagrams/rendered`](diagrams/rendered)

Если нужно перерендерить:

```bash
java -jar /path/to/plantuml.jar -tsvg docs/mobile-network-qos/diagrams/src/*.puml -o ../rendered
```
