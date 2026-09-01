# vesc — VESC CAN Telemetri Dashboard'u

Aynı CAN bus üzerindeki 4 adet Flipsky Mini VESC 6.7 Pro'nun (VESC ID 0–3)
canlı telemetrisi: FastAPI + WebSocket backend, tek sayfalık koyu temalı web UI
(vanilla JS + Chart.js, build adımı yok). Bus'a Cube Orange üzerinden ArduPilot
SLCAN passthrough ile bağlanılır.

## Kurulum

Python 3.11+ gerekir.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
python backend/main.py            # gerçek bus: /dev/tty.usbmodem* otomatik bulunur
python backend/main.py --mock     # donanım yokken sahte veriyle UI geliştirme
```

Dashboard: http://localhost:8000

Cube Orange USB'de **iki** seri port çıkarır (SERIAL0 = MAVLink, SERIAL6 =
SLCAN); dashboard adayları sırayla dener ve 3 s içinde VESC frame'i veren
portu seçer (MAVLink portu SLCAN el sıkışmasını sessizce kabul ettiği için
"bağlı ama veri yok" tuzağına düşmez). USB çekilirse otomatik yeniden bağlanır;
durum üst barda görünür. Port açık ama frame gelmiyorsa pill sarı
"bağlı · frame yok" olur (bkz. SLCAN → armed notu).

Diğer bayraklar: `--port /dev/cu.usbmodemXXXX` (portu elle seç, probe yok),
`--bitrate 500000`, `--pole-pairs 7` (RPM = ERPM / pole_pairs),
`--fw 5.2|6.0` (firmware profili, varsayılan 5.2), `--no-poll-faults`
(fault sorgulamayı kapat), `--dash-id 250`, `--status-rate-hz 50` (VESC
Tool'daki CAN Status Rate; frame kaybı uyarısı için), `--host`, `--http-port`.

## ArduPilot SLCAN kurulumu (Cube Orange / Orange+)

Kalıcı ve GCS ile aynı anda çalışan yol: ikinci USB portunu (SERIAL6 = OTG2)
SLCAN'e ayırmak. Cube Orange/Orange+ hwdef'inde SERIAL6 zaten varsayılan
olarak SLCAN protokolündedir. Parametreler (ArduPilot kaynağından
doğrulandı: `AP_CANManager.cpp`, `AP_SLCANIface.cpp`, `hwdef/CubeOrange/hwdef.inc`):

| Parametre | Değer | Açıklama |
|---|---|---|
| `CAN_P1_DRIVER` | 1 | Birinci CAN arayüzünü etkinleştir (reboot ister) |
| `CAN_P1_BITRATE` | 500000 | VESC CAN baud'u ile aynı olmalı |
| `CAN_D1_PROTOCOL` | 1 (DroneCAN) | **Zorunlu.** Protokol "None" olursa arayüze driver bağlanmaz ve SLCAN'e frame akmaz. `CAN_D1_UC_NODE` 0–3 olmasın (varsayılan 10) |
| `CAN_SLCAN_CPORT` | 1 | SLCAN'e yönlendirilecek CAN arayüzü (1 = birinci) |
| `SERIAL6_PROTOCOL` | 22 (SLCAN) | Cube Orange'da fabrika varsayılanı; reboot'a dayanıklı |
| `CAN_SLCAN_TIMOUT` | 0 | 0 = zaman aşımı yok |

Bu kurulumda GCS SERIAL0'da (ilk `usbmodem`) bağlı kalabilir; dashboard
SERIAL6'yı (ikinci `usbmodem`) otomatik bulur.

**`CAN_SLCAN_SERNUM` kullanmayın (kalıcı değil):** bu parametre *geçici*dir —
ArduPilot her boot'ta `-1`'e sıfırlar (F9P güncellemesinde yaşanan "reboot'ta
hat eski haline döndü" sorununun sebebi budur).

**Armed uyarısı:** `SERIALn_PROTOCOL=22` ile açılan SLCAN, araç **armed**
olduğunda ArduPilot tarafından otomatik kapatılır, disarm'da geri açılır
(`update_slcan_port()`). Cube yalnızca CAN adaptörü olarak kullanılıyorsa
(hiç arm edilmiyorsa) akış süreklidir. Armed iken de telemetri gerekiyorsa
tek yol boot sonrası GCS'den `CAN_SLCAN_SERNUM=6` vermektir (bu yolda arming
kontrolü yoktur; her boot'ta tekrarlanır). Dashboard kesintiyi
"bağlı · frame yok" olarak gösterir.

**Bant genişliği:** ArduPilot SLCAN her frame'i timestamp'li 31 bayt olarak
yazar ve seri TX tamponu dolarsa frame'i **sessizce düşürür**. 4 VESC × 5
status × 50 Hz = 1000 frame/s (31 KB/s). Frame kaybı uyarısı görürseniz VESC
Tool'da CAN Status Rate'i 20–25 Hz'e çekin ve `--status-rate-hz` ile aynı
değeri verin.

macOS'ta portlar `/dev/cu.usbmodem*` olarak seçilir (`tty.*` ikizi atlanır).

## VESC tarafı ayarları (FW 5.2)

VESC Tool → App Settings → General:

- Her VESC'e benzersiz **VESC ID** verin: 0, 1, 2, 3
- **Send Can Status** = `CAN_STATUS_1_2_3_4_5` — FW 5.2'deki en geniş seçenek
  budur; STATUS_6 (ADC/PPM) FW 5.2'de **yoktur**, FW 6.00 ile gelmiştir
- **CAN Status Rate**: varsayılan 50 Hz (`send_can_status_rate_hz`)
- CAN baud: 500k (ArduPilot `CAN_P1_BITRATE` ile aynı)

## v2 — Denizde kurulum: USB-CAN adaptör + MAVLink telemetri hattı

Gemide CAN veri yolu artık Cube'dan **geçmez**: companion bilgisayar (Raspberry
Pi vb. Linux) VESC bus'ını kendi USB-CAN adaptörüyle okur; Cube yalnız radyo
köprüsüdür. Armed/disarmed farkı kalmaz.

```
VESC×4 ═CAN═ USB-CAN (candleLight) ─ companion ─UART→ Cube TELEM2 → TELEM1 radyo ~~~ kara: radyo → GCS → MAVLink mirror → dashboard
```

### Companion (gemi, Linux)

```bash
sudo ip link set can0 up type can bitrate 500000        # kalıcı için systemd-networkd / interfaces
python backend/main.py --can-interface socketcan --channel can0 \
    --mavlink-out /dev/ttyAMA0:115200 --host 0.0.0.0     # TELEM2'ye bağlı UART
```

Cube tarafı: `SERIAL2_PROTOCOL = 2` (MAVLink2), `SERIAL2_BAUD = 115`.
`CAN_SLCAN_*` parametrelerine gerek yok. ArduPilot, companion'dan gelen
broadcast mesajları radyo bağlantısına iletir (`MAVLink_routing.cpp`,
`check_and_forward`: `broadcast_system` → öğrenilen tüm kanallar).

### Adaptör seçimi ve olası kayıplar

- **candleLight/gs_usb firmware'li adaptör** (CANable 2.0, MKS CANable, Innomaker
  vb.) → Linux çekirdek sürücüsü, `socketcan`. USB bulk aktarım 500 kbit/s'lik
  bus'ın tamamını (~4000 frame/s) taşır; **veri kaybı yoktur**, çekirdek kuyruğu
  python'un okuma temposundan bağımsızdır. ArduPilot SLCAN'deki sessiz düşürme,
  timestamp metni ve byte-byte parse yükü ortadan kalkar.
- **slcan firmware'li** adaptör de çalışır (`--can-interface slcan --port /dev/ttyACM0`)
  ama text protokol kalır; mümkünse candleLight flash'layın. macOS'ta gs_usb
  sürücüsü yok → Mac'te adaptör slcan modunda kullanılır.
- **Sonlandırma:** bus'ın iki ucunda 120 Ω olmalı. Adaptör bus'ın ortasına
  giriyorsa termination jumper'ını **kapatın**; üçüncü sonlandırma hata üretir.
- **İzolasyon:** izole olmayan adaptör companion toprağını VESC güç toprağına
  bağlar (36–48 V sistemde gürültü/toprak döngüsü). Galvanik izoleli model tercih.
- Adaptör bus'ta **aktif düğümdür** (ACK verir) — sorun değil; listen-only modda
  fault poll (TX) çalışmaz.
- USB gecikmesi ~1 ms; 10 Hz dashboard için anlamsız.

### Kara

GCS'nin MAVLink akışını yansıtın — Mission Planner: *MAVLink Mirror* (UDP) ya da
MAVProxy: `mavproxy.py --master=/dev/tty.usbserial-XXXX --out udp:127.0.0.1:14550 --out udp:127.0.0.1:14551` — sonra:

```bash
python backend/main.py --mavlink-in udpin:0.0.0.0:14551
```

Aynı arayüz açılır; VESC'ler 5 s veri gelmezse offline sayılır, fps ≈ online
VESC sayısı × uplink hızı. GCS ayrıca ESC 1–4 sıcaklık/voltaj/akım/RPM'i
kendi ekranında gösterir (`ESC_TELEMETRY_1_TO_4`).

### Bant genişliği (telemetriyi boğmaz)

| Mesaj | Boyut (MAVLink2) | Hız | Yük |
|---|---|---|---|
| `ESC_TELEMETRY_1_TO_4` (GCS için) | ~56 B | 1 Hz | 0.45 kbit/s |
| `TUNNEL` (dashboard için tam veri) | ~100 B | 1 Hz | 0.8 kbit/s |
| `HEARTBEAT` | ~21 B | 1 Hz | 0.17 kbit/s |
| **Toplam** | | | **≈1.4 kbit/s ≈ %2.5 @ 57.6 kbit/s** |

`--uplink-rate 0.5` ile yarıya iner; `--no-esc-telemetry` ile yalnız TUNNEL
kalır. ESC_TELEMETRY alanları unsigned'dır (akım/RPM işareti yok — rejen
kullanılmadığından sorun değil); TUNNEL tam alan setini taşır
(`docs/CAN_PROTOCOL_FW52.md` §9).

## Parse edilen CAN frame'leri (FW 5.2, kaynak doğrulamalı)

Extended (29-bit) ID = `(command_id << 8) | vesc_id`, payload big-endian.
Yerleşimler vedderb/bldc **5.02 tag'indeki kaynaktan** birebir doğrulandı —
tam referans ve satır numaraları için `docs/CAN_PROTOCOL_FW52.md`.

- STATUS 1–5 (cmd 9, 14, 15, 16, 27): ERPM, motor akımı, duty, Ah/Wh,
  FET/motor sıcaklığı, giriş akımı, PID pozisyonu, tacho, giriş voltajı
- **Fault kodu** status'larda yoktur; dashboard her VESC'i ~1 Hz'de
  `PROCESS_SHORT_BUFFER` + `COMM_GET_VALUES_SELECTIVE` (yalnız fault mask'ı)
  ile sorgular ve UI'da kırmızı rozetle gösterir
- Bu komutlar ve ID 0–3 dışındaki tüm frame'ler sessizce yok sayılır

**Sensorless motorlar (ör. DEGZ Ultra):** motor NTC'si bağlı olmadığından
firmware motor sıcaklığını geçersiz okur ve −100 °C'ye sabitler; dashboard
bunu algılayıp motor sıcaklığını "—" olarak gösterir. FET sıcaklığı gerçektir.
