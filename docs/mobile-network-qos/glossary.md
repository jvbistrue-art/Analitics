# Глоссарий сокращений

| Сокращение | Раскрытие | Краткая справка |
|---|---|---|
| 5GC | 5G Core | Пакетное ядро 5G. |
| 5QI | 5G QoS Identifier | Класс QoS в 5G: priority, delay, loss, GBR/non-GBR. |
| AF | Application Function | Приложение, которое может запросить QoS через PCF/NEF. |
| AMBR | Aggregate Maximum Bit Rate | Суммарный лимит скорости UE/APN/session. |
| AMF | Access and Mobility Management Function | Регистрация UE, access control, mobility в 5G. |
| APN | Access Point Name | Имя сети данных в LTE: internet, ims, enterprise. |
| ARP | Allocation and Retention Priority | Приоритет допуска/удержания и pre-emption bearer/flow. |
| BGP | Border Gateway Protocol | Междоменная маршрутизация к internet/peering. |
| BSS | Business Support System | Коммерческие системы: тарифы, CRM, product catalog. |
| BWP | Bandwidth Part | Часть полосы 5G NR с отдельной numerology. |
| CA | Carrier Aggregation | Агрегация несущих для скорости и разгрузки. |
| CDN | Content Delivery Network | Кэширование контента ближе к пользователю. |
| CGNAT | Carrier-Grade NAT | Массовый NAT абонентов. |
| CHF | Charging Function | Charging в 5G. |
| CQI | Channel Quality Indicator | Индикатор качества канала от UE. |
| CSI-RS | Channel State Information Reference Signal | 5G-сигналы измерения канала/beam. |
| Dedicated bearer | Dedicated EPS bearer | Дополнительный LTE bearer для отдельного сервиса с собственным QCI/ARP/GBR. |
| Default bearer | Default EPS bearer | Базовый LTE bearer для APN, обычно переносит обычный internet data. |
| DNN | Data Network Name | 5G-аналог APN по роли подключения к сети данных. |
| DPI | Deep Packet Inspection | Классификация приложений и traffic policy. |
| DRB | Data Radio Bearer | Радиоканал пользовательских данных. |
| DSCP | Differentiated Services Code Point | IP-маркировка QoS. |
| EBI | EPS Bearer Identity | Идентификатор EPS bearer, по которому UE и EPC различают bearers. |
| E-RAB | E-UTRAN Radio Access Bearer | Связка EPS bearer с LTE radio bearer и S1 bearer до EPC. |
| eICIC | enhanced Inter-Cell Interference Coordination | Координация интерференции LTE HetNet. |
| eMBB | enhanced Mobile Broadband | 5G-сценарий массового broadband. |
| eNodeB | evolved NodeB | Базовая станция LTE. |
| EPC | Evolved Packet Core | Пакетное ядро LTE. |
| EPS | Evolved Packet System | LTE-система целиком: UE, RAN, EPC. |
| EPS bearer | Evolved Packet System bearer | LTE-логический канал от UE до P-GW с одним QoS-профилем. |
| FAR | Forwarding Action Rule | UPF-правило действия пересылки. |
| GBR | Guaranteed Bit Rate | Гарантированная скорость bearer/flow. |
| GFBR | Guaranteed Flow Bit Rate | Гарантированная скорость QoS Flow в 5G. |
| Gold-status | Commercial priority tier | Коммерческий premium-статус, который должен быть преобразован в QoS policy: AMBR, QCI/5QI, ARP, scheduler weight или GBR/GFBR. |
| gNB | gNodeB | Базовая станция 5G. |
| GTP-U | GPRS Tunneling Protocol - User Plane | Туннель пользовательских данных в EPC/5GC. |
| HARQ | Hybrid Automatic Repeat Request | Быстрые повторы ошибочных радиоблоков. |
| HSS | Home Subscriber Server | LTE-база подписок. |
| ICIC | Inter-Cell Interference Coordination | Координация межсотовой интерференции. |
| IMS | IP Multimedia Subsystem | Платформа VoLTE/VoNR и мультимедиа. |
| KPI | Key Performance Indicator | Метрика качества/эксплуатации сети. |
| LBO | Local Breakout | Локальный выход трафика ближе к пользователю. |
| LLQ | Low Latency Queue | Приоритетная очередь для низкой задержки. |
| MAC | Medium Access Control | Радиопланировщик и HARQ-уровень. |
| MBR | Maximum Bit Rate | Максимальная скорость bearer. |
| MEC | Multi-access Edge Computing | Edge-приложения рядом с RAN. |
| MFBR | Maximum Flow Bit Rate | Максимальная скорость QoS Flow в 5G. |
| MIMO | Multiple Input Multiple Output | Несколько антенн для скорости/качества. |
| MME | Mobility Management Entity | LTE control plane для attach/bearers/mobility. |
| MCS | Modulation and Coding Scheme | Модуляция/кодирование радиопередачи. |
| MLB | Mobility Load Balancing | Балансировка нагрузки через mobility. |
| MPLS TC | MPLS Traffic Class | QoS-маркировка в MPLS. |
| NEF | Network Exposure Function | API exposure для внешних приложений в 5G. |
| NR | New Radio | Радиоинтерфейс 5G. |
| NSSF | Network Slice Selection Function | Выбор network slice в 5G. |
| OCS/OFCS | Online/Offline Charging System | Charging и квоты LTE. |
| OSS | Operations Support System | Системы эксплуатации и управления сетью. |
| Packet filter | Packet filter | Правило сопоставления IP-пакета по адресу, порту, протоколу или precedence. |
| PCC | Policy and Charging Control | Policy + charging архитектура. |
| PCEF | Policy and Charging Enforcement Function | Enforcement-функция на P-GW. |
| PCF | Policy Control Function | Policy decision в 5G. |
| PCRF | Policy and Charging Rules Function | Policy decision в LTE. |
| PDCP | Packet Data Convergence Protocol | Шифрование, compression, reordering. |
| PDN Connection | Packet Data Network Connection | LTE-подключение UE к APN; внутри него есть default и dedicated bearers. |
| PDR | Packet Detection Rule | UPF-правило распознавания пакета. |
| PDU Session | Protocol Data Unit Session | 5G-сессия UE к DNN. |
| P-GW | Packet Data Network Gateway | LTE IP anchor и выход к APN. |
| PRB | Physical Resource Block | Единица радио ресурса LTE/NR. |
| QCI | QoS Class Identifier | Класс QoS в LTE. |
| QER | QoS Enforcement Rule | UPF-правило QoS enforcement. |
| QFI | QoS Flow Identifier | Идентификатор QoS Flow в 5G. |
| QoS Flow | Quality of Service Flow | Минимальная 5G-единица QoS внутри PDU Session. |
| QoS Rule | Quality of Service Rule | 5G-правило UE для привязки uplink-пакетов к QFI. |
| QoS | Quality of Service | Набор механизмов качества: delay, loss, priority, bitrate. |
| RAN | Radio Access Network | Радиосеть от UE до core. |
| RLC | Radio Link Control | Буферы, сегментация и повторы. |
| RRC | Radio Resource Control | Управление радио соединением. |
| RRM | Radio Resource Management | Управление radio resources, interference, mobility. |
| RTP | Real-time Transport Protocol | Медиа-поток голоса/видео. |
| SDAP | Service Data Adaptation Protocol | Маппинг QoS Flow в DRB в 5G. |
| SDF | Service Data Flow | Сервисный поток для PCC. |
| S-GW | Serving Gateway | LTE user-plane anchor. |
| Scheduler weight | Vendor-specific scheduling weight | Вес radio scheduler для распределения PRB/slots между классами и UE при перегрузке. |
| SGi | Интерфейс P-GW к external data network | LTE-граница в IP-сеть. |
| SMF | Session Management Function | 5G session control и UPF programming. |
| S-NSSAI | Single Network Slice Selection Assistance Information | Идентификатор network slice. |
| SSB | Synchronization Signal Block | 5G синхронизация и beam discovery. |
| SPID | Subscriber Profile ID | Идентификатор профиля абонента, который в некоторых реализациях помогает RAN применять subscriber-based handling. |
| TFT | Traffic Flow Template | LTE-фильтр для binding потока к bearer. |
| UDM/UDR | Unified Data Management / Repository | 5G подписка и данные политики. |
| UE | User Equipment | Смартфон, CPE, modem. |
| ULCL | Uplink Classifier | UPF-функция разветвления uplink. |
| UPF | User Plane Function | 5G user-plane forwarding и enforcement. |
| URLLC | Ultra-Reliable Low-Latency Communications | Сценарий сверхнадежной низкой задержки. |
| URR | Usage Reporting Rule | UPF-правило usage reporting. |
| URSP | UE Route Selection Policy | Политика UE для выбора DNN/slice по приложению. |
| VoLTE | Voice over LTE | Голос через IMS в LTE. |
| VoNR | Voice over New Radio | Голос через IMS в 5G NR. |
| WRED | Weighted Random Early Detection | Управление очередью при congestion. |
