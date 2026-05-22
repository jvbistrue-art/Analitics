# Где хранится QoS-конфигурация и как ей управляют

## Карта ответственности

В мобильной сети нет единого файла, где хранится весь приоритет. Конфигурация распределена между commercial/product systems, subscriber database, policy control, packet core, RAN и IP-сетью.

```text
BSS/CRM/Product catalog
  -> subscriber/profile provisioning
  -> HSS/UDM + PCRF/PCF
  -> MME/SMF session setup
  -> P-GW/UPF enforcement
  -> eNodeB/gNB radio enforcement
  -> IP/MPLS/security/CDN edge
```

## Где лежит какая логика

| Уровень | LTE | 5G | Что хранит/делает |
|---|---|---|---|
| Product/BSS | CRM, product catalog | CRM, product catalog | Тариф, группа пользователя, enterprise SLA, услуга VoLTE/VoNR. |
| Subscriber DB | HSS | UDM/UDR | Подписка, доступные APN/DNN, AMBR, slice eligibility. |
| Policy decision | PCRF | PCF | PCC rules: QoS, charging, gating, service priority. |
| Session control | MME + P-GW | AMF + SMF | Создание bearer/PDU Session, доставка QoS в RAN и UPF. |
| User-plane enforcement | P-GW/PCEF | UPF | Shaping, gating, DSCP marking, charging reports. |
| Radio enforcement | eNodeB | gNB | Admission, scheduler, radio queue/DRB mapping, PRB allocation. |
| IP enforcement | SGi routers/FW/DPI | N6 routers/FW/DPI/MEC | DSCP/MPLS queues, CGNAT, firewall, DPI, peering/CDN. |

## Как управлять приоритетом группы пользователей

### 1. Определить группу и услугу

Примеры групп:

- обычные абоненты;
- gold/silver/bronze;
- premium data;
- enterprise APN/DNN;
- VoLTE/VoNR;
- public safety;
- IoT;
- low-latency gaming/MEC.

Группа должна быть отражена в BSS/CRM и provisioning, иначе network policy не узнает, что абонент имеет право на особый QoS.

### 2. Назначить service boundary

| Цель | LTE | 5G |
|---|---|---|
| Массовый интернет | APN `internet` | DNN `internet`, eMBB slice |
| Голос | APN/PDN `ims` | DNN `ims` |
| Enterprise | Corporate APN | Enterprise DNN + S-NSSAI |
| Low latency edge | Региональный APN/P-GW, если есть | MEC DNN + edge UPF + S-NSSAI |

### 3. Назначить QoS-класс

| Тип сервиса | LTE | 5G |
|---|---|---|
| Voice RTP | QCI 1, GBR | 5QI 1, GBR/GFBR |
| IMS signaling | QCI 5 | 5QI 5 |
| Critical enterprise | QCI 3/65/66 или vendor policy | Standard/custom 5QI + GFBR |
| Premium data | QCI 8 или operator-defined non-GBR QCI | 5QI 8 или custom non-GBR |
| Default internet | QCI 9 | 5QI 9 |

Один UE может иметь несколько QoS-классов одновременно: в LTE через несколько EPS bearers с разными QCI, в 5G через несколько QoS Flows с разными 5QI/QFI. Это позволяет одному устройству одновременно передавать VoLTE/VoNR, IMS signaling, enterprise traffic и ordinary internet с разными приоритетами. Подробности и схемы: [Несколько QoS-каналов на одном UE](ue-multiple-qos-channels.md).

Примечание: стандартный QCI 6 относится к GBR-видео и не должен описываться как обычный non-GBR premium internet без явного GBR SLA.

### 4. Настроить допуск и удержание

Для гарантии нужны:

- **GBR/GFBR** — целевой минимальный bitrate после успешного admission control и при достаточной емкости;
- **Admission Control** — не принимать больше гарантированных потоков, чем сеть выдержит;
- **ARP** — кто может быть допущен/удержан и кто может вытеснять при setup/retention;
- **scheduler weights/resource share** — как RAN делит PRB;
- **AMBR/MBR/MFBR** — чтобы ограничить excess traffic.

### 5. Обеспечить end-to-end QoS

Проверить цепочку:

```text
Policy DB -> session setup -> RAN DRB/scheduler -> P-GW/UPF -> DSCP/MPLS -> Internet/CDN/MEC
```

Если один домен не настроен, качество ломается именно там:

- RAN без admission control не удержит GBR;
- packet core без PCC не создаст нужный bearer/QoS Flow;
- IP-сеть без DSCP/MPLS queues смешает critical и best effort;
- плохой peering/CDN даст задержку вне мобильной сети.

## Управление голосом и data

### Голос

```text
IMS subscription
  -> IMS registration
  -> PCRF/PCF policy
  -> QCI 5/5QI 5 signaling
  -> QCI 1/5QI 1 RTP
  -> RAN low-delay scheduling
  -> IMS low-latency IP class
```

Голос должен быть отделен от обычного data, иначе при перегрузке соты он будет конкурировать с bulk traffic.

### Data

```text
internet APN/DNN
  -> default bearer / QoS Flow
  -> QCI 9 / 5QI 9
  -> best effort scheduler
  -> CGNAT/DPI/CDN/peering
```

Для premium data обычно применяют не строгую гарантию, а higher weight, больший AMBR, лучший route/CDN и менее агрессивный shaping. Строгая гарантия требует GBR/GFBR и admission control.

### Gold-status

Gold-status является коммерческим профилем, поэтому его нужно явно связать с технической policy:

```text
gold entitlement
  -> subscriber profile
  -> PCRF/PCF policy group
  -> QCI/5QI, ARP, AMBR, optional GBR/GFBR
  -> RAN scheduler weight/resource share
  -> IP QoS/DSCP policy
```

Типовая модель:

| Уровень | Что настроить |
|---|---|
| BSS/CRM | Gold entitlement, срок действия, список абонентов или enterprise-группа. |
| HSS/UDM | Разрешенные APN/DNN, AMBR, S-NSSAI/URSP для 5G. |
| PCRF/PCF | Policy group: QCI/5QI, ARP, AMBR, charging, gating. |
| P-GW/UPF | Shaping, DSCP marking, routing, QER/PCEF enforcement. |
| eNodeB/gNB | QCI/5QI mapping, scheduler weight, admission thresholds, slice share. |
| IP/MPLS | DSCP/MPLS queues, peering/CDN/service chain. |

Gold-status без RAN scheduler mapping часто дает только больший скоростной лимит. Gold-status со scheduler weight дает преимущество при congestion, но строгая гарантия требует GBR/GFBR и admission control. Подробнее: [Gold-status в радио сети](gold-status.md).

## Операционный цикл изменения политики

1. Product/business описывает услугу и группу.
2. BSS/CRM создает entitlement.
3. Provisioning обновляет HSS/UDM и policy store PCRF/PCF.
4. Core team настраивает APN/DNN, P-GW/UPF, charging.
5. RAN team настраивает QCI/5QI mapping, scheduler, admission thresholds.
6. IP team настраивает DSCP/MPLS queues, security chain, peering/CDN.
7. NOC/engineering проверяют KPI: accessibility, retainability, latency, packet loss, throughput, PRB utilization, PDU/bearer success, VoLTE/VoNR MOS.

## Контрольные вопросы перед запуском QoS-услуги

- Как UE/приложение попадет в нужный APN/DNN/slice?
- Есть ли subscriber entitlement в HSS/UDM?
- Как PCRF/PCF распознает сервис?
- Нужен ли dedicated bearer/QoS Flow?
- Есть ли admission control для GBR/GFBR?
- Какой ARP и pre-emption policy?
- Как RAN scheduler маппит QCI/5QI в веса и очереди?
- Сохраняется ли DSCP после P-GW/UPF?
- Есть ли congestion на CGNAT/FW/DPI/IP/MPLS/peering?
- Какие KPI докажут, что качество реально улучшилось?

Сводная матрица влияния каждого подхода на пользовательский опыт и бизнес-ценность приведена в документе [Пользовательский опыт и бизнес-ценность QoS-подходов](ux-business-value.md).
