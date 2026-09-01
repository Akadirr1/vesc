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
`--host`, `--http-port`.

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

## VESC tarafı ayarları

VESC Tool → App Settings → General:

- Her VESC'e benzersiz **VESC ID** verin: 0, 1, 2, 3
- **Send CAN Status** = `CAN_STATUS_1_2_3_4_5_6` (tüm status mesajları)
- **CAN Status Rate**: örn. 50 Hz
- CAN baud: 500k (ArduPilot `CAN_P1_BITRATE` ile aynı)

## Parse edilen CAN frame'leri

Extended (29-bit) ID = `(command_id << 8) | vesc_id`, payload big-endian.
STATUS 1–6 (cmd 9, 14, 15, 16, 27, 28): ERPM, akımlar, duty, Ah/Wh,
FET/motor sıcaklığı, tacho, giriş voltajı, ADC1-3, PPM. Bu 6 komut ve
ID 0–3 dışındaki tüm frame'ler sessizce yok sayılır.
