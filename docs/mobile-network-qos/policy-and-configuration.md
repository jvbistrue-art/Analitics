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
| Radio enforcement | eNodeB | gNB | Admission, scheduler, DRB mapping, PRB allocation. |
| IP enforcement | SGi routers/FW/DPI | N6 routers/FW/DPI/MEC | DSCP/MPLS queues, CGNAT, firewall, DPI, peering/CDN. |

## Как управлять приоритетом группы пользователей

### 1. Определить группу и услугу

Примеры групп:

- обычные абоненты;
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
| Premium data | QCI 6/8 non-GBR | 5QI 8 или custom non-GBR |
| Default internet | QCI 9 | 5QI 9 |

### 4. Настроить допуск и удержание

Для гарантии нужны:

- **GBR/GFBR** — минимальный bitrate;
- **Admission Control** — не принимать больше гарантированных потоков, чем сеть выдержит;
- **ARP** — кто может вытеснять и кто может быть вытеснен;
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
