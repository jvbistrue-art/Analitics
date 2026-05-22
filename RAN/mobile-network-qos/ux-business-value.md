# Пользовательский опыт и бизнес-ценность QoS-подходов

Этот документ связывает технические механизмы QoS с тем, что реально видит пользователь, и с бизнес-ценностью для оператора.

## Сокращения и зачем нужны

| Сокращение | Полное имя | Краткая справка зачем нужно |
|---|---|---|
| QoS | Quality of Service | Управляет задержкой, потерями, приоритетом и скоростью разных классов трафика. |
| QoE | Quality of Experience | Пользовательское восприятие качества: слышимость, задержка, стабильность видео, скорость загрузки. |
| QCI | QoS Class Identifier | LTE-класс QoS, по которому RAN и core различают voice, signaling, data и GBR-сервисы. |
| 5QI | 5G QoS Identifier | 5G-класс QoS для QoS Flow; аналог QCI по назначению. |
| GBR | Guaranteed Bit Rate | LTE-целевой minimum bitrate после successful admission control и при достаточной radio capacity. |
| GFBR | Guaranteed Flow Bit Rate | 5G-целевой minimum bitrate для QoS Flow после successful admission control. |
| ARP | Allocation and Retention Priority | Управляет допуском, удержанием и pre-emption bearer/QoS Flow; не является per-packet scheduler priority. |
| AMBR | Aggregate Maximum Bit Rate | Суммарный лимит скорости UE/APN/session; повышает потолок, но не гарантирует ресурс при congestion. |
| MBR/MFBR | Maximum Bit Rate / Maximum Flow Bit Rate | Ограничивает максимальную скорость bearer/QoS Flow, защищая сеть от excess traffic. |
| APN | Access Point Name | LTE-граница сервиса: internet, IMS, enterprise, IoT. |
| DNN | Data Network Name | 5G-граница сервиса, аналог APN по роли подключения к data network. |
| S-NSSAI | Single Network Slice Selection Assistance Information | Идентификатор network slice, нужен для slice-specific policy и resource share. |
| DRB | Data Radio Bearer | Radio transport для пользовательских данных; именно его очереди обслуживает RAN scheduler. |
| QoS Flow | Quality of Service Flow | Минимальная 5G-единица QoS внутри PDU Session. |
| QFI | QoS Flow Identifier | Идентификатор QoS Flow, по которому UE/gNB/UPF различают 5G flows. |
| TFT | Traffic Flow Template | LTE packet filters, которые привязывают IP-поток к EPS bearer. |
| PDR/QER | Packet Detection Rule / QoS Enforcement Rule | UPF-правила для классификации пакетов и QoS enforcement в 5G. |
| DSCP | Differentiated Services Code Point | IP-маркировка QoS после P-GW/UPF. |
| MPLS TC | Multiprotocol Label Switching Traffic Class | QoS-маркировка в MPLS-транспортной сети. |
| DPI | Deep Packet Inspection | Классификация приложений для policy, shaping, charging и security. |
| MEC | Multi-access Edge Computing | Edge-размещение приложений рядом с RAN для снижения задержки. |
| CDN | Content Delivery Network | Кэширование контента ближе к пользователю для скорости и снижения backbone load. |

## Матрица подходов

| Подход | Где применяется | Пользовательский опыт | Бизнес-ценность |
|---|---|---|---|
| **Default bearer / default QoS Flow** | LTE APN или 5G DNN для обычного internet | Пользователь получает базовый доступ в интернет; при перегрузке скорость может падать первой. | Простая массовая услуга с высокой емкостью и низкой стоимостью обслуживания. |
| **Dedicated bearer / отдельный QoS Flow** | LTE dedicated EPS bearer или 5G QoS Flow для конкретного сервиса | Голос, enterprise app или premium service не стоят в одной очереди с bulk download. | Можно продавать управляемые сервисы, SLA и дифференцировать тарифы. |
| **GBR/GFBR + admission control** | RAN и core для voice, critical enterprise, public safety | Сервис продолжает работать предсказуемо при congestion, если сессия принята и емкость доступна. | Поддержка SLA, B2B-контрактов, mission-critical услуг и voice quality. |
| **ARP/pre-emption** | Bearer/QoS Flow setup, retention и release | Важная сессия чаще устанавливается и сохраняется при нехватке ресурсов; менее важные сессии могут быть вытеснены. | Приоритизация emergency, public safety, enterprise VIP и регуляторных услуг. |
| **AMBR/MBR/MFBR** | HSS/UDM, PCRF/PCF, P-GW/UPF, UE/session limits | Пользователь получает тарифный потолок скорости; premium-тариф быстрее в свободной сети. | Монетизация тарифных уровней и контроль потребления емкости. |
| **Scheduler weight / premium QCI/5QI** | eNodeB/gNB scheduler profiles | При равных radio conditions gold/premium data получает большую долю PRB/slots при congestion. | Видимое отличие premium-тарифа без жесткого резервирования ресурса для всех. |
| **APN/DNN separation** | LTE APN, 5G DNN, P-GW/UPF routing | Enterprise, IMS, IoT и internet имеют разные маршруты, security и лимиты. | Упрощает продуктовую сегментацию, security policy и B2B-подключения. |
| **Network slicing через S-NSSAI** | 5G core, gNB, transport, UPF | Enterprise/public safety группа получает отдельные policy и resource share; массовый internet не мешает критичным сервисам в той же степени. | Продажа private/enterprise slices и изоляция сервисов на общей инфраструктуре. |
| **Несколько QoS-каналов на одном UE** | LTE EPS bearers с разными QCI или 5G QoS Flows с разными 5QI/QFI | Пользователь может одновременно говорить по VoLTE/VoNR и скачивать файл; голос остается стабильным, data замедляется. | Улучшение удержания клиентов, снижение жалоб на voice/data coexistence. |
| **IMS voice QoS** | IMS, PCRF/PCF, dedicated bearer/QoS Flow, RAN scheduler | Меньше обрывов, задержек и роботизации голоса при загруженной соте. | Voice KPI, regulatory quality, снижение churn и поддержка VoLTE/VoNR как базовой услуги. |
| **DPI/application-aware policy** | P-GW/UPF/service chain после классификации трафика | Видео может быть стабилизировано, P2P ограничен, gaming/VoIP может получить более мягкий путь, если policy разрешает. | Traffic optimization, fair usage, parental/security services, zero-rating/charging models. |
| **IP QoS через DSCP/MPLS TC** | SGi/N6, IP/MPLS backbone, transport network | Приоритет не теряется после P-GW/UPF: voice/enterprise пакеты не смешиваются полностью с best effort. | End-to-end SLA и защита инвестиций в mobile QoS за пределами RAN/core. |
| **MEC/local breakout** | Edge UPF/P-GW, MEC platform, regional routing | Ниже RTT для games, AR/VR, industrial apps и enterprise edge-сервисов. | Новые low-latency B2B/B2B2C продукты и разгрузка backbone. |
| **CDN/peering optimization** | IP backbone, CDN caches, BGP policy | Видео быстрее стартует, меньше buffering, выше стабильность массового контента. | Снижение transit cost, рост NPS для массового data и меньше нагрузки на core/backbone. |
| **RAN load balancing и radio optimization** | eNodeB/gNB, SON, mobility, ICIC/eICIC, beamforming | Пользователь чаще оказывается на менее загруженной соте/layer; выше SINR и throughput. | Больше полезной емкости из существующего spectrum, меньше CAPEX pressure. |
| **Gold-status policy** | BSS/CRM -> HSS/UDM -> PCRF/PCF -> RAN/IP | Premium-клиент получает более высокий потолок скорости и лучшую долю ресурса при congestion, но voice/critical traffic остается выше. | Дифференциация тарифов, VIP/enterprise удержание, дополнительная выручка без полной физической изоляции сети. |

## Примеры пользовательских сценариев

### 1. Голос + загрузка файла

```text
UE:
  VoLTE/VoNR voice -> QCI/5QI 1
  IMS signaling -> QCI/5QI 5
  file download -> QCI/5QI 9
```

**Пользовательский эффект:** разговор не "роботизируется" и не обрывается, даже если параллельно идет download.  
**Бизнес-ценность:** стабильные voice KPI, меньше обращений в поддержку, выполнение регуляторных требований.

### 2. Gold-пользователь в загруженной соте

```text
Gold data:
  higher AMBR
  QCI/5QI 8 или custom non-GBR
  higher scheduler weight
  ARP для лучшего admission/retention
```

**Пользовательский эффект:** при одинаковом SINR gold-клиент получает больше throughput, чем default data user.  
**Бизнес-ценность:** понятная премиальная услуга, которую можно продавать как тарифный tier.

### 3. Enterprise critical app

```text
enterprise DNN/APN
  -> dedicated bearer или QoS Flow
  -> GBR/GFBR after admission
  -> private route / edge UPF
  -> DSCP/MPLS assured forwarding
```

**Пользовательский эффект:** корпоративное приложение работает стабильнее при нагрузке сети.  
**Бизнес-ценность:** B2B SLA, private network upsell, снижение риска штрафов по контрактам.

### 4. Массовое видео

```text
default internet
  -> non-GBR data
  -> CDN/peering optimization
  -> optional DPI/video policy
```

**Пользовательский эффект:** быстрее стартует видео и меньше buffering без выделения GBR каждому пользователю.  
**Бизнес-ценность:** дешевле, чем гарантировать радиоресурс каждому видеопотоку; снижает transit и backbone load.

## Как оценивать результат

| Метрика | Что показывает |
|---|---|
| QoE/NPS | Реально ли пользователь видит улучшение. |
| Throughput per class | Получает ли premium/gold больше ресурса при равных radio conditions. |
| Latency/jitter/loss | Сохраняется ли качество voice, gaming и critical apps. |
| GBR/GFBR fulfillment | Выполняются ли гарантии после admission. |
| PRB utilization | Хватает ли radio capacity для выбранной policy. |
| Drop/discard per QCI/5QI | Кто деградирует первым при congestion. |
| Support tickets/churn | Снижается ли число жалоб и отток. |
| Revenue uplift | Окупается ли premium/enterprise QoS-продукт. |
