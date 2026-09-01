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

Birden fazla `usbmodem` portu varsa başlangıçta CLI'da seçim sorulur. USB
çekilirse backend otomatik yeniden bağlanmayı dener; durum üst barda görünür.

Diğer bayraklar: `--port /dev/tty.usbmodemXXXX` (portu elle seç),
`--bitrate 500000`, `--pole-pairs 7` (RPM = ERPM / pole_pairs),
`--fw 5.2|6.0` (firmware profili, varsayılan 5.2), `--no-poll-faults`
(fault sorgulamayı kapat), `--dash-id 250`, `--host`, `--http-port`.

## ArduPilot SLCAN kurulumu (Cube Orange)

Mission Planner / QGC ile şu parametreleri ayarlayıp yeniden başlatın:

| Parametre | Değer | Açıklama |
|---|---|---|
| `CAN_P1_DRIVER` | 1 | Birinci CAN arayüzünü etkinleştir (reboot ister) |
| `CAN_P1_BITRATE` | 500000 | VESC CAN baud'u ile aynı olmalı |
| `CAN_SLCAN_CPORT` | 1 | SLCAN'e yönlendirilecek CAN arayüzü (1 = birinci) |
| `CAN_SLCAN_SERNUM` | 0 | SLCAN'in çalışacağı seri port (0 = SERIAL0 / USB) |
| `CAN_SLCAN_TIMOUT` | 0 | 0 = zaman aşımı yok |

Not: Dashboard'u çalıştırmadan önce GCS'nin (Mission Planner/QGC) o USB
portuyla bağlantısını kesin — SLCAN akışı ile MAVLink aynı portu paylaşamaz.
macOS'ta port `/dev/tty.usbmodem*` olarak görünür.

## VESC tarafı ayarları (FW 5.2)

VESC Tool → App Settings → General:

- Her VESC'e benzersiz **VESC ID** verin: 0, 1, 2, 3
- **Send Can Status** = `CAN_STATUS_1_2_3_4_5` — FW 5.2'deki en geniş seçenek
  budur; STATUS_6 (ADC/PPM) FW 5.2'de **yoktur**, FW 6.00 ile gelmiştir
- **CAN Status Rate**: varsayılan 50 Hz (`send_can_status_rate_hz`)
- CAN baud: 500k (ArduPilot `CAN_P1_BITRATE` ile aynı)

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
