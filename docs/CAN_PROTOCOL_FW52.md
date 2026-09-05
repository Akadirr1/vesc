# VESC CAN Protokolü — FW 5.2 Kaynak Doğrulamalı Referans

Bu doküman, dashboard'un parse ettiği her baytın VESC firmware kaynağındaki
karşılığını gösterir. **Hiçbir alan hafızadan/tahminden yazılmamıştır** —
tamamı `vedderb/bldc` reposunun **`5.02` tag'inden** (commit `3f67013`,
"Rebuild firmwares and disabled test version flag") doğrulanmıştır.

Doğrulama yöntemi:

```bash
git clone --depth 1 --branch 5.02 https://github.com/vedderb/bldc
# İncelenen dosyalar: comm_can.c, commands.c, datatypes.h, buffer.c,
# mc_interface.c, appconf/appconf_default.h
```

Hedef donanım: 4 × Flipsky Mini VESC 6.7 Pro (VESC ID 0–3), FW 5.2,
motorlar sensorless DEGZ Ultra (motor NTC'si yok), bus'a ArduPilot SLCAN
passthrough ile erişim.

---

## 1. Çerçeve yapısı

Tüm VESC CAN trafiği **extended (29-bit) ID** kullanır:

```
arbitration_id = (command_id << 8) | controller_id      // comm_can.c: decode_msg()
payload        = big-endian                              // buffer.c append/get
```

`decode_msg()` içinde `id = eid & 0xFF`, `cmd = eid >> 8` (comm_can.c:1132+).
`buffer_append_float16/32` sadece `value * scale`'in int16/int32'ye çevrimidir
(buffer.c:48–54) — yani "float16" IEEE half değil, ölçekli tamsayıdır.

## 2. Broadcast edilen STATUS frame'leri (FW 5.2'de gerçekten var olanlar)

FW 5.2'de **yalnızca STATUS 1–5 vardır**. Gönderen kod: `comm_can.c`
`send_status1..5()` (satır 1605–1660), alan kaynakları `mc_interface_*`
fonksiyonlarıdır. Alıcı (decode) tarafı aynı dosyada satır 1478–1550'dedir ve
ölçekler iki tarafta birebir aynıdır.

### CAN_PACKET_STATUS (cmd **9**) — comm_can.c:1605

| Bayt | Alan | Tip | Ölçek | Firmware kaynağı |
|---|---|---|---|---|
| 0–3 | ERPM | int32 | ×1 | `mc_interface_get_rpm()` |
| 4–5 | Motor akımı (toplam, filtreli) | int16 | ÷10 → A | `mc_interface_get_tot_current_filtered()` |
| 6–7 | Duty cycle | int16 | ÷1000 → oran | `mc_interface_get_duty_cycle_now()` |

### CAN_PACKET_STATUS_2 (cmd **14**) — comm_can.c:1623

| Bayt | Alan | Tip | Ölçek |
|---|---|---|---|
| 0–3 | Ah harcanan | int32 | ÷10 000 |
| 4–7 | Ah şarj edilen (rejen) | int32 | ÷10 000 |

### CAN_PACKET_STATUS_3 (cmd **15**) — comm_can.c:1632

| Bayt | Alan | Tip | Ölçek |
|---|---|---|---|
| 0–3 | Wh harcanan | int32 | ÷10 000 |
| 4–7 | Wh şarj edilen | int32 | ÷10 000 |

### CAN_PACKET_STATUS_4 (cmd **16**) — comm_can.c:1641

| Bayt | Alan | Tip | Ölçek | Firmware kaynağı |
|---|---|---|---|---|
| 0–1 | FET sıcaklığı | int16 | ÷10 → °C | `mc_interface_temp_fet_filtered()` |
| 2–3 | Motor sıcaklığı | int16 | ÷10 → °C | `mc_interface_temp_motor_filtered()` (bkz. §6) |
| 4–5 | Giriş (batarya) akımı | int16 | ÷10 → A | `mc_interface_get_tot_current_in_filtered()` |
| 6–7 | PID pozisyonu | int16 | ÷50 → derece | `mc_interface_get_pid_pos_now()` |

### CAN_PACKET_STATUS_5 (cmd **27**) — comm_can.c:1652

| Bayt | Alan | Tip | Ölçek |
|---|---|---|---|
| 0–3 | Tachometer | int32 | ×1 |
| 4–5 | Giriş voltajı | int16 | ÷10 → V |
| 6–7 | **Rezerve** (`buffer_append_int16(buffer, 0)` — "Reserved for now") | int16 | — |

> Frame 8 bayttır ama son 2 bayt her zaman 0'dır; dashboard ilk 6 baytı okur.

### Gönderim koşulu ve hızı

`cancom_status_thread` (comm_can.c:1055+): `send_can_status` moduna göre
kademeli gönderir. Modlar (datatypes.h:693–701):

```
CAN_STATUS_DISABLED, CAN_STATUS_1, CAN_STATUS_1_2, CAN_STATUS_1_2_3,
CAN_STATUS_1_2_3_4, CAN_STATUS_1_2_3_4_5        ← FW 5.2'deki en geniş mod
```

Hız: `send_can_status_rate_hz`, varsayılan **50 Hz**
(appconf/appconf_default.h:45–46, `sleep = CH_CFG_ST_FREQUENCY / rate_hz`).
Tüm status'lar aynı tick'te gönderilir → mod 1_2_3_4_5'te VESC başına 5 frame
× 50 Hz. 4 VESC için ≈ 1000 frame/s ≈ %26 bus yükü @ 500 kbit/s (ext frame
~130 bit). Bus yükünü düşürmek gerekirse VESC Tool'dan rate'i 20 Hz'e çekmek
yeterlidir; dashboard 10 Hz push'ladığı için veri kaybı hissedilmez.

## 3. FW 5.2'de OLMAYANLAR (ve eski spec'in hatası)

`datatypes.h` 5.02 `CAN_PACKET_ID` enum'unda (satır 931–977) **STATUS_6
yoktur**. Sayım şöyledir:

```
9  CAN_PACKET_STATUS          27 CAN_PACKET_STATUS_5
14 CAN_PACKET_STATUS_2        28 CAN_PACKET_POLL_TS5700N8501_STATUS  ← STATUS_6 DEĞİL
15 CAN_PACKET_STATUS_3        58 CAN_PACKET_STATUS_6                 ← yalnız FW 6.00+
16 CAN_PACKET_STATUS_4
```

- **cmd 28**, her iki firmware'de de `POLL_TS5700N8501_STATUS`'tur (TS5700N8501
  SPI enkoder sorgusu). İlk implementasyonun "cmd 28 = STATUS_6 (ADC/PPM)"
  varsayımı **hiçbir firmware sürümünde doğru olmamıştır**; STATUS_6 FW 6.00'da
  **58** olarak eklendi (master `datatypes.h` ile doğrulandı). Dashboard artık
  varsayılan `--fw 5.2` profilinde cmd 28'i parse etmez; `--fw 6.0` verilirse
  cmd 58'i STATUS_6 olarak parse eder.
- Dolayısıyla FW 5.2'de **ADC1-3 ve PPM broadcast ile okunamaz** (istenirse
  `COMM_GET_DECODED_ADC`/`COMM_GET_DECODED_PPM` poll'u ile alınabilir; UI'da
  gösterilmediği için implement edilmedi).
- VESC Tool 5.2'de "Send Can Status" için `CAN_STATUS_1_2_3_4_5_6` diye bir
  seçenek yoktur; doğru ayar `CAN_STATUS_1_2_3_4_5`'tir.

## 4. Fault kodu sorgulama (dashboard'un eklediği poll)

Fault kodu hiçbir STATUS frame'inde yoktur; `COMM_GET_VALUES(_SELECTIVE)`
yanıtının parçasıdır. Dashboard bunu CAN üzerinden şöyle sorgular:

**İstek** — `CAN_PACKET_PROCESS_SHORT_BUFFER` (**8**), comm_can.c:1245–1268:

```
arbitration_id = (8 << 8) | hedef_vesc_id
data = [dash_id, 0x00, 50, 0x00, 0x00, 0x80, 0x00]
        │        │     │   └────────┴─────┴────── mask = 1<<15 (yalnız fault)
        │        │     └── COMM_GET_VALUES_SELECTIVE = 50 (datatypes.h:859,
        │        │         COMM_FW_VERSION=0'dan itibaren sayılır)
        │        └── 0 = "işle ve CAN'den yanıtla" (commands_process_packet →
        │            send_packet_wrapper, comm_can.c:1260–1263)
        └── yanıtın döneceği controller id (dashboard = 250)
```

**Yanıt** — commands.c:306–367 mask'lı alanları sırayla paketler; yanıt ≤6 bayt
olduğundan `comm_can_send_buffer` (comm_can.c:301–311) **tek frame** ile döner:

```
arbitration_id = (8 << 8) | dash_id
data = [vesc_id, 0x01, 50, mask(4 bayt), fault_u8]   → tam 8 bayt
```

`commands.c:365–367`: `if (mask & (1<<15)) send_buffer[ind++] =
mc_interface_get_fault();`

Dashboard her VESC'i ~1 Hz'de sorgular (4 VESC → saniyede 4 istek + 4 yanıt,
bus yüküne etkisi ihmal edilebilir). `--no-poll-faults` ile kapatılır;
`--dash-id` çakışmayan bir id olmalıdır (varsayılan 250).

### Fault kodları (datatypes.h:111–136, `mc_fault_code`)

| # | Kod | # | Kod |
|---|---|---|---|
| 0 | NONE | 13 | ENCODER_SINCOS_ABOVE_MAX_AMPLITUDE |
| 1 | OVER_VOLTAGE | 14 | FLASH_CORRUPTION |
| 2 | UNDER_VOLTAGE | 15 | HIGH_OFFSET_CURRENT_SENSOR_1 |
| 3 | DRV | 16 | HIGH_OFFSET_CURRENT_SENSOR_2 |
| 4 | ABS_OVER_CURRENT | 17 | HIGH_OFFSET_CURRENT_SENSOR_3 |
| 5 | OVER_TEMP_FET | 18 | UNBALANCED_CURRENTS |
| 6 | OVER_TEMP_MOTOR | 19 | BRK |
| 7 | GATE_DRIVER_OVER_VOLTAGE | 20 | RESOLVER_LOT |
| 8 | GATE_DRIVER_UNDER_VOLTAGE | 21 | RESOLVER_DOS |
| 9 | MCU_UNDER_VOLTAGE | 22 | RESOLVER_LOS |
| 10 | BOOTING_FROM_WATCHDOG_RESET | 23 | FLASH_CORRUPTION_APP_CFG |
| 11 | ENCODER_SPI | 24 | FLASH_CORRUPTION_MC_CFG |
| 12 | ENCODER_SINCOS_BELOW_MIN_AMPLITUDE | 25 | ENCODER_NO_MAGNET |

## 5. FW 5.2'de CAN üzerinden okunabilecek TÜM parametreler

`COMM_GET_VALUES_SELECTIVE` mask tablosu (commands.c:306–390). Bunların hepsi
§4'teki mekanizmayla istenebilir; **≤6 bayt yanıtlar tek frame**, daha uzunları
`CAN_PACKET_FILL_RX_BUFFER`(5) + `CAN_PACKET_PROCESS_RX_BUFFER`(7) çok-frame
protokolü + CRC16 gerektirir (comm_can.c:312–340). Dashboard bilinçli olarak
yalnız fault'u poll eder — diğer değerli alanların tamamı zaten STATUS
broadcast'lerinde vardır:

| Bit | Alan | Tip | Ölçek | STATUS'ta var mı? |
|---|---|---|---|---|
| 0 | temp_fet | int16 | ÷10 | ✓ S4 |
| 1 | temp_motor | int16 | ÷10 | ✓ S4 |
| 2 | avg_motor_current | int32 | ÷100 | ✓ S1 (filtreli) |
| 3 | avg_input_current | int32 | ÷100 | ✓ S4 (filtreli) |
| 4 | avg_id (FOC d-akımı) | int32 | ÷100 | ✗ |
| 5 | avg_iq (FOC q-akımı) | int32 | ÷100 | ✗ |
| 6 | duty | int16 | ÷1000 | ✓ S1 |
| 7 | rpm (ERPM) | int32 | ×1 | ✓ S1 |
| 8 | v_in | int16 | ÷10 | ✓ S5 |
| 9–12 | Ah / Ah_chg / Wh / Wh_chg | int32 | ÷10 000 | ✓ S2/S3 |
| 13 | tachometer | int32 | ×1 | ✓ S5 |
| 14 | tachometer_abs | int32 | ×1 | ✗ |
| **15** | **fault_code** | uint8 | — | **✗ → dashboard poll'lar** |
| 16 | pid_pos | int32 | ÷1 000 000 | ✓ S4 (÷50 çözünürlükle) |
| 17 | controller_id | uint8 | — | (ID zaten frame'de) |
| 18 | NTC mos1/mos2/mos3 | 3×int16 | ÷10 | ✗ |
| 19 | avg_vd | int32 | ÷1000 | ✗ |
| 20 | avg_vq | int32 | ÷1000 | ✗ |

STATUS'ta olmayıp poll'a değebilecekler yalnız id/iq/vd/vq (FOC teşhisi) ve
mos1-3 ayrı NTC'leridir; ihtiyaç olursa çok-frame RX assembler eklenerek tek
mask'la alınabilir.

## 6. Sensorless DEGZ Ultra motorların etkisi

- **Motor sıcaklığı sahtedir.** Motor NTC'si bağlı değilken `TEMP_SENSOR_NTC_10K_25C`
  formülü açık devreyi derin negatif okur; firmware geçersiz değerleri
  **-100 °C'ye sabitler** (mc_interface.c:1909–1914: "If the reading is messed
  up ... temp_motor = -100.0"). Dashboard ≤ −50 °C okumaları "sensör yok"
  sayar ve motor sıcaklığını "—" gösterir. `FAULT_CODE_OVER_TEMP_MOTOR`
  negatif değerlerle tetiklenmez, güvenlik sorunu yoktur.
- **FET sıcaklığı gerçektir** (kart üstü NTC, `NTC_TEMP(ADC_IND_TEMP_MOS)`).
- **pid_pos** yalnız pozisyon kontrol modunda anlamlıdır; duty/akım kontrolünde
  gösterge değeri yoktur (dashboard UI'da göstermez, backend yine de parse eder).
- Hall/enkoder yokluğu diğer telemetri alanlarını etkilemez; ERPM sensorless
  gözlemciden gelir ve geçerlidir. Düşük ERPM'de (openloop bölgesi) kısa süreli
  sıçramalar normaldir.

## 7. Dashboard alanı → kaynak eşlemesi (özet)

| UI alanı | Kaynak | Gerçeklik |
|---|---|---|
| RPM (= ERPM ÷ pole_pairs) | S1 | ✓ birebir (pole_pairs=7 DEGZ Ultra için config) |
| Duty % | S1 | ✓ |
| Motor akımı | S1 | ✓ (filtreli toplam motor akımı) |
| Giriş akımı | S4 | ✓ (filtreli batarya akımı) |
| FET sıcaklığı | S4 | ✓ |
| Motor sıcaklığı | S4 | sensorless'ta yok → "—" |
| Voltaj | S5 | ✓ |
| Ah / Wh | S2 / S3 | ✓ |
| Fault rozeti | GET_VALUES_SELECTIVE bit 15 poll | ✓ |
| Σ giriş gücü | S5.v_in × S4.current_in toplamı | ✓ (türetilmiş) |

### İşaret ve filtre semantiği (mcpwm_foc.c 5.02)

- **Motor akımı (S1)** = `SIGN(vq · iq_filter) · i_abs_filter` (:1169). İşaret
  **güç yönü**dür: + motorlama, − rejeneratif fren. Dönüş yönünü **vermez**;
  ters itki de + okunur. Yön için ERPM'nin işaretine bakın.
- **Giriş akımı (S4)** = `i_bus`, adına rağmen **filtresizdir** (:1275 "TODO:
  Calculate filtered current?"). 10 Hz örneklemede titremesi normaldir; − = bataryaya şarj.
- **Ah/Wh (S2/S3)** VESC açılışından itibaren sayaçtır; VESC güç çevriminde sıfırlanır.

### FW 5.03 ile fark

`release_5_03` ile diff alındı: `CAN_PACKET_ID` ilk 46 girişi ve STATUS 1–5
gönderim kodu aynıdır (yalnız S5 voltajı `mc_interface_get_input_voltage_filtered()`
olur, ölçek aynı). Bu doküman 5.02 ve 5.03 için geçerlidir.

## 8. SLCAN / ArduPilot katmanı (kaynak: ArduPilot master)

Dashboard'un parser'ı doğru olsa da veri ArduPilot'tan geçer; şu davranışlar
doğrulandı ve koda yansıtıldı:

| Bulgu | Kaynak | Dashboard'daki karşılığı |
|---|---|---|
| Firmware `cmd = eid >> 8`'in tamamını karşılaştırır (21 bit), `&0xFF` yapmaz | bldc `comm_can.c:1141` | Parser da maskesiz karşılaştırır; bits 16–28 dolu frame'ler (DroneCAN) yok sayılır. Aynı sebeple DroneCAN frame'leri VESC'lere komut olamaz |
| SLCAN passthrough için arayüze bir protokol driver'ı bağlı olmalı; `CAN_D1_PROTOCOL=None` → `default: continue` → `receive()` hiç çağrılmaz | `AP_CANManager.cpp` init | README: `CAN_D1_PROTOCOL=1` zorunlu |
| `CAN_SLCAN_SERNUM` her boot'ta −1'e sıfırlanır (`reset_params()`); kalıcı yol `SERIALn_PROTOCOL=22` | `AP_SLCANIface.cpp` params + `update_slcan_port()` | README: SERIAL6_PROTOCOL=22 |
| Cube Orange/Orange+: `SERIAL_ORDER OTG1 … OTG2` → SERIAL6 = ikinci USB; `HAL_OTG2_PROTOCOL SerialProtocol_SLCAN` | `hwdef/CubeOrange/hwdef.inc:32,35` | Port probe: iki `usbmodem`'den frame vereni seç |
| SERIALn yoluyla açılan SLCAN **armed** olunca kapanır, disarm'da açılır; SERNUM yolunda arming kontrolü yok | `update_slcan_port()` | UI "bağlı · frame yok" uyarısı + README notu |
| Her frame'e koşulsuz 4 hex timestamp eklenir (`T`+id8+dlc+data+ts4+`\r` = 31 bayt); `txspace` yetmezse `reportFrame` 0 döner → **sessiz frame kaybı** | `reportFrame()` | `--status-rate-hz` ile beklenen fps; %70 altı sarı uyarı; README 20–25 Hz önerisi |
| `S`/`O`/`C`/`Z` komutları sadece "OK" döner; frame akışı `O`'ya bağlı değildir; TX'e `Z\r` ack'ı yazılır | `AP_SLCANIface.cpp:350–360, 329` | python-can bu satırları yok sayar; bağlanınca `flush()` |
| Hex çıktısı büyük harf; satır ortasından açılınca `D`/`B` ile başlayan fragment python-can'in CAN-FD dallarında `IndexError/ValueError` fırlatır (`slcan.py:298–322`, try yok) | `nibble2hex`, python-can 4.6.1 | `recv` etrafında `(ValueError, IndexError, KeyError)` → satır atlanır; yalnız seri/CAN hataları reconnect tetikler |
| python-can `sleep_after_open` varsayılanı 2 s (Arduino adaptörleri için) | `slcan.py:150` | 0.3 s |

Poll istekleri ArduPilot'ta `push_Frame → rx_queue_` ile CAN'e aktarılır; TX
mailbox'ı 8 denemede boşalmazsa frame düşer (`receive()` kuyruğu). Bu yüzden
yalnız **online** VESC'ler sorgulanır — ACK'lenmeyecek frame ArduPilot'un hata
sayaçlarını boşuna artırır.

## 9. v2 — MAVLink deniz hattı (companion → Cube → radyo → kara)

Companion `MAV_COMP_ID_ONBOARD_COMPUTER` (191) olarak, otopilotla aynı sysid
ile Cube'un TELEM2'sine yazar. ArduPilot `MAVLink_routing.cpp`
`check_and_forward()`: `broadcast_system` (target_system 0) mesajlar öğrenilen
tüm rotalara (GCS'nin görüldüğü radyo kanalı dahil) iletilir — doğrulandı.

### Gönderilen mesajlar (`backend/uplink.py`, `--uplink-rate`, varsayılan 1 Hz)

| Mesaj | Kaynak alan → MAVLink alanı | Not |
|---|---|---|
| `HEARTBEAT` (0) | type ONBOARD_CONTROLLER, autopilot INVALID | 1 Hz, router/GCS bileşeni görsün |
| `ESC_TELEMETRY_1_TO_4` (ardupilotmega 11030) | temp_fet → temperature °C (u8); v_in → voltage cV (u16); \|current_motor\| → current cA (u16); ah_used → totalcurrent mAh (u16, 65.5 Ah'de sarar); \|rpm\| (mekanik) → rpm (u16); online tick sayacı → count | GCS-native; işaretler kaybolur |
| `TUNNEL` (common 385), `payload_type = 0x5643` | aşağıdaki ikili paket | dashboard için tam veri |

### TUNNEL payload (big-endian, sürüm 1, 4 + 20·N bayt)

Başlık `>BHB`: version=1, seq (u16), N (kayıt sayısı). Kayıt `>BBBbhhHiHHbb`:

| Alan | Tip | Ölçek | Sentinel |
|---|---|---|---|
| vesc_id | u8 | | |
| flags | u8 | bit0 online, bit1 motor NTC var, bit2 fault bilgisi var | |
| fault | u8 | mc_fault_code | |
| duty | i8 | % | |
| current_motor | i16 | cA (işaretli) | |
| current_in | i16 | cA (işaretli) | |
| v_in | u16 | cV | |
| erpm | i32 | ×1 (işaretli) | |
| ah_used | u16 | mAh | |
| wh_used | u16 | 0.1 Wh | |
| temp_fet | i8 | °C | −128 = hiç alınmadı |
| temp_motor | i8 | °C | 127 = sensör yok → karada −100 sentinel'e çevrilir |

Kara tarafı (`--mavlink-in`) TUNNEL kayıtlarını `TelemetryState.update()` ile
işler; `online` biti 0 olan VESC güncellenmez (5 s sonra offline). TUNNEL 3 s
gelmezse `ESC_TELEMETRY_1_TO_4` kayıplı yedek olarak kullanılır (`voltage == 0`
= veri yok). Offline eşiği `--offline-after` (kara varsayılanı 5 s);
`fps_expected` = online VESC × 1 × uplink hızı.

### Kaynak doğrulamaları

- `ESC_TELEMETRY_1_TO_4` alan tipleri: `message_definitions/v1.0/ardupilotmega.xml`
  (id 11030: u8[4] temperature degC, u16[4] voltage cV, u16[4] current cA,
  u16[4] totalcurrent mAh, u16[4] rpm, u16[4] count).
- Broadcast yönlendirme: `libraries/GCS_MAVLink/MAVLink_routing.cpp:182–225`.
- pymavlink 2.4.x: TUNNEL MAVLink2 gerektirir → `MAVLINK20=1`; `recv_match(type=[...])` list ister.

## 10. MAVLink CAN forwarding (Cube üzerinden armed'de de çalışan CAN erişimi)

Kaynak: ArduPilot master `371990d` — `libraries/AP_CANManager/AP_MAVLinkCAN.cpp`
(GCS_Common.cpp yalnız dispatch eder), `libraries/AP_HAL/CANIface.h`,
`libraries/AP_HAL_ChibiOS/CANFDIface.cpp`; mavlink `common.xml`; referans istemci
pydronecan `dronecan/driver/mavcan.py`. Uygulama: `backend/mavcan.py`.

| Bulgu | Kaynak | Dashboard'daki karşılığı |
|---|---|---|
| `MAV_CMD_CAN_FORWARD` (32000) `param1` **1-tabanlı** bus (`bus = int8_t(param1)-1`), 0 = durdur; kapalı arayüz → `MAV_RESULT_FAILED` | `AP_MAVLinkCAN.cpp:65-83` | `--mav-can-bus 1`; ACK≠0 logda uyarı |
| Son istekten 5 s sonra forwarding kapanır; kontrol her 100 frame'de | `AP_MAVLinkCAN.cpp` `last_callback_enable_ms`, `frame_counter++ == 100` | 1 Hz keepalive (`FORWARD_PERIOD_S`), mavcan ile aynı |
| **Arming kontrolü yok**; tek gereksinim `hal.can[bus]` init (`CAN_Px_DRIVER≠0`); callback'ler protokol driver'ının `receive()/send()` çağrılarından tetiklenir → `CAN_Dx_PROTOCOL=0` ile RX akmaz | `AP_MAVLinkCAN.cpp`, `AP_HAL/CANIface.cpp:59-104`, `AP_CANManager.cpp:139-170` | README: `CAN_D1_PROTOCOL=1` |
| `CAN_FRAME` yalnız **isteyen kanala**; tek istemci struct'ı — yeni istek eskisini ezer | `can_forward.chan/system_id/component_id` | MP DroneCAN ekranı akışı çalar (README) |
| RX **ve** otopilotun kendi TX frame'leri iletilir (`IsForwardedFrame` değilse) | `CanIface.cpp:374`, `CANFDIface.cpp:435` | Parser DroneCAN frame'lerini yok sayar |
| Gönderim yalnız `HAVE_PAYLOAD_SPACE(chan, CAN_FRAME)` ise; kuyruk/rate limit yok → **sessiz düşürme** (`out_of_space_to_send_count`, log `MAV.times_full`) | `AP_MAVLinkCAN.cpp` callback | fps uyarısı; status rate önerisi |
| `id` = `AP_HAL::CANFrame::id` ham: `FlagEFF=1<<31`, `FlagRTR=1<<30`, `FlagERR=1<<29`, `MaskExtID=0x1FFFFFFF` | `CANIface.h:30-34`, RX'te EFF set: `CANFDIface.cpp:768-769` | `id & 0x1FFFFFFF`, extended = bit31 |
| Ters yol: GCS→`CAN_FRAME`(386) bus'a yazılır; burada `bus` **0-tabanlı**, extended için bit31 şart, 20'lik kuyruk, 2 ms deadline; forwarding açık olmak zorunda değil | `_handle_can_frame` | `MavlinkCanBus.send()`: `bus_index-1`, `id | FlagEFF`, 8 bayta doldur |
| `target_system 0 / component 0` yerel işlenir | `MAVLink_routing.cpp:182-187` | Komut ve TX frame'ler 0/0 ile gönderilir; otopilot sysid öğrenmeye gerek yok |
| SLCAN ile aynı arayüzde birlikte çalışır; SLCAN armed'de kapanır, forwarding kapanmaz | `AP_SLCANIface.cpp:439-446` | Cube yolu için önerilen transport |
| MAVLink 2 zorunlu (id 386 > 255); kanal MAVLink2 paket görünce MAVLink2'ye geçer, `SERIALn_PROTOCOL=2` önerilir | pymavlink `mavlink_helpers`, GCS_MAVLink | `MAVLINK20=1` (`uplink.open_connection`) |
| `CAN_FILTER_MODIFY`(388): id bits 8..23'e göre filtre; VESC ext id'de bu = komut id (id<128 için) ama `dash_id≥128` yanıtları "service" dalına düşer (`id>>16`=0) | `common.xml`, `AP_MAVLinkCAN.cpp` | Kullanılmıyor (fault yanıtlarını keserdi); ileride opsiyon |

`common.xml`: `CAN_FRAME` = target_system u8, target_component u8, bus u8, len u8,
id u32, data u8[8] (wire sırası id önce); pymavlink `can_frame_send(target_system,
target_component, bus, len, id, data[8])`, `data` **tam 8 eleman** ister; alınan
`msg.data` her zaman 8 int (MAVLink2 sıfır kırpması decode'da geri doldurulur).

Referans istemci (mavcan.py): sysid 250 / compid 189, komutu **1 s'de bir** yeniler,
`is_extended = id & (1<<31)`, `canid = id & 0x1FFFFFFF`, `data[:len]`, TX'te
`bus` 0-tabanlı, `id |= 1<<31`, 8 bayta doldurma — dashboard aynı kuralları uygular.
