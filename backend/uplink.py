"""MAVLink uplink / downlink for the sea deployment (v2).

Vessel side (--mavlink-out): the companion computer that reads the CAN bus
also talks MAVLink to the Cube (e.g. TELEM2). ArduPilot forwards broadcast
messages (target system 0) from one link to every other learned route
(libraries/GCS_MAVLink/MAVLink_routing.cpp, check_and_forward), so what we
send on TELEM2 reaches the shore GCS over the telemetry radio.

Sent at --uplink-rate (default 1 Hz):
  * ESC_TELEMETRY_1_TO_4 (ardupilotmega, id 11030) — the GCS shows ESC
    temperature / voltage / current / rpm natively. Unsigned fields: sign of
    current and rpm is lost here (fine for a no-regen, forward-only vessel).
  * TUNNEL (common, id 385, payload_type VESC_TUNNEL_TYPE) — a compact
    binary snapshot with everything ESC_TELEMETRY lacks: signed ERPM,
    duty, input current, Wh, fault codes, online / sensor flags.
  * HEARTBEAT at 1 Hz so routers and the GCS list this component.

Bandwidth: ~56 B (ESC_TELEMETRY) + ~100 B (TUNNEL) + ~20 B (HEARTBEAT) per
second ≈ 1.4 kbit/s — about 2.5 % of a 57.6 kbit/s radio.

Shore side (--mavlink-in): decode those messages back into a
TelemetryState so the very same web UI works unchanged.
"""

import logging
import os
import struct
import threading
import time

os.environ.setdefault("MAVLINK20", "1")  # TUNNEL (id 385) needs MAVLink 2

log = logging.getLogger("vesc-dash.uplink")

# MAV_TUNNEL_PAYLOAD_TYPE: 0 = unknown, 200-219 vendor reserved. 'VC' in ASCII.
VESC_TUNNEL_TYPE = 0x5643
TUNNEL_VERSION = 1
TUNNEL_MAX_PAYLOAD = 128
ESC_TELEMETRY_STALE_S = 3.0  # use ESC_TELEMETRY only if no TUNNEL for this long

# Record layout (big-endian, 20 bytes per VESC):
#   B id | B flags | B fault | b duty % | h motor current cA | h input current cA
#   H v_in cV | i erpm | H Ah used (mAh) | H Wh used (0.1 Wh) | b FET °C | b motor °C
_HDR = struct.Struct(">BHB")            # version, seq, record count
_REC = struct.Struct(">BBBbhhHiHHbb")
FLAG_ONLINE = 1
FLAG_MOTOR_TEMP_SENSOR = 2
FLAG_HAS_FAULT = 4
TEMP_NONE = 127        # motor temp: no sensor
TEMP_UNKNOWN = -128    # value never received


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def _num(d: dict, key: str, scale: float, lo: int, hi: int, default: float = 0.0) -> int:
    v = d.get(key)
    return _clamp(round((default if v is None else v) * scale), lo, hi)


def pack_tunnel(vescs: dict, seq: int) -> bytes:
    """`vescs` is the "vescs" dict of a TelemetryState.snapshot()."""
    recs = []
    for vid_s, d in sorted(vescs.items(), key=lambda kv: int(kv[0])):
        flags = FLAG_ONLINE if d.get("online") else 0
        if d.get("motor_temp_sensor") is not False:
            flags |= FLAG_MOTOR_TEMP_SENSOR
        if "fault" in d:
            flags |= FLAG_HAS_FAULT
        tf = d.get("temp_fet")
        tm = d.get("temp_motor")
        recs.append(_REC.pack(
            int(vid_s), flags, _clamp(d.get("fault", 0), 0, 255),
            _num(d, "duty", 100, -100, 100),
            _num(d, "current_motor", 100, -32768, 32767),
            _num(d, "current_in", 100, -32768, 32767),
            _num(d, "v_in", 100, 0, 65535),
            _clamp(int(d.get("erpm") or 0), -2**31, 2**31 - 1),
            _num(d, "ah_used", 1000, 0, 65535),
            _num(d, "wh_used", 10, 0, 65535),
            TEMP_UNKNOWN if tf is None else _clamp(round(tf), -127, 127),
            TEMP_NONE if tm is None else _clamp(round(tm), -128, 126),
        ))
    payload = _HDR.pack(TUNNEL_VERSION, seq & 0xFFFF, len(recs)) + b"".join(recs)
    if len(payload) > TUNNEL_MAX_PAYLOAD:
        raise ValueError(f"tunnel payload {len(payload)} B > {TUNNEL_MAX_PAYLOAD}")
    return payload


def unpack_tunnel(payload: bytes) -> dict[int, dict]:
    """Returns {vesc_id: fields}; fields use the same keys as TelemetryState,
    plus "online" (bool). Motor temp without sensor comes back as the
    firmware sentinel -100.0 so main.py's snapshot logic applies unchanged."""
    if len(payload) < _HDR.size:
        return {}
    version, _seq, n = _HDR.unpack_from(payload, 0)
    if version != TUNNEL_VERSION:
        return {}
    out: dict[int, dict] = {}
    off = _HDR.size
    for _ in range(n):
        if off + _REC.size > len(payload):
            break
        (vid, flags, fault, duty, i_mot, i_in, v_in, erpm,
         mah, dwh, tf, tm) = _REC.unpack_from(payload, off)
        off += _REC.size
        f = {
            "online": bool(flags & FLAG_ONLINE),
            "duty": duty / 100.0,
            "current_motor": i_mot / 100.0,
            "current_in": i_in / 100.0,
            "v_in": v_in / 100.0,
            "erpm": erpm,
            "ah_used": mah / 1000.0,
            "wh_used": dwh / 10.0,
            "temp_motor": -100.0 if tm == TEMP_NONE else float(tm),
        }
        if tf != TEMP_UNKNOWN:
            f["temp_fet"] = float(tf)
        if flags & FLAG_HAS_FAULT:
            f["fault"] = fault
        out[vid] = f
    return out


def pack_esc_telemetry(vescs: dict, vesc_ids, counters: dict) -> tuple:
    """Field lists for ESC_TELEMETRY_1_TO_4 (first four VESC ids).
    rpm is the mechanical RPM the GCS expects; current is |motor current|."""
    cols = {k: [] for k in ("temperature", "voltage", "current", "totalcurrent", "rpm", "count")}
    for vid in list(vesc_ids)[:4]:
        d = vescs.get(str(vid), {})
        cols["temperature"].append(_num(d, "temp_fet", 1, 0, 255))
        cols["voltage"].append(_num(d, "v_in", 100, 0, 65535))
        cols["current"].append(_clamp(round(abs(d.get("current_motor") or 0.0) * 100), 0, 65535))
        cols["totalcurrent"].append(_num(d, "ah_used", 1000, 0, 65535))
        cols["rpm"].append(_clamp(round(abs(d.get("rpm") or 0.0)), 0, 65535))
        cols["count"].append(counters.get(vid, 0) & 0xFFFF)
    for col in cols.values():
        col.extend([0] * (4 - len(col)))
    return (cols["temperature"], cols["voltage"], cols["current"],
            cols["totalcurrent"], cols["rpm"], cols["count"])


def open_connection(spec: str, sysid: int, compid: int):
    """spec: 'udpout:host:port' | 'udpin:host:port' | 'tcp:host:port' |
    '/dev/ttyXXX:baud' (serial). Imports pymavlink lazily so the CAN-only
    dashboard does not need it installed."""
    from pymavlink import mavutil

    baud = 115200
    device = spec
    if spec.startswith("/") or spec.upper().startswith("COM"):
        head, _, tail = spec.rpartition(":")
        if head and tail.isdigit():
            device, baud = head, int(tail)
    return mavutil.mavlink_connection(device, baud=baud, source_system=sysid,
                                      source_component=compid, dialect="ardupilotmega")


class MavlinkUplink(threading.Thread):
    """Vessel side: periodically push the current snapshot over MAVLink."""

    def __init__(self, cfg, state, stop: threading.Event):
        super().__init__(daemon=True, name="mavlink-uplink")
        self.cfg, self.state, self.stop = cfg, state, stop

    def run(self) -> None:
        from pymavlink import mavutil

        mav = mavutil.mavlink
        period = 1.0 / self.cfg.uplink_rate
        seq = 0
        counters = {vid: 0 for vid in self.cfg.vesc_ids}
        while not self.stop.is_set():
            conn = None
            try:
                conn = open_connection(self.cfg.mavlink_out, self.cfg.mav_sysid, self.cfg.mav_compid)
                log.info("MAVLink uplink: %s @ %.2f Hz (sysid %d, compid %d)",
                         self.cfg.mavlink_out, self.cfg.uplink_rate, self.cfg.mav_sysid, self.cfg.mav_compid)
                next_hb = 0.0
                while not self.stop.is_set():
                    t0 = time.time()
                    snap = self.state.snapshot(self.cfg.pole_pairs, 0.0, self.cfg.status_rate_hz)
                    vescs = snap["vescs"]
                    if t0 >= next_hb:
                        conn.mav.heartbeat_send(mav.MAV_TYPE_ONBOARD_CONTROLLER, mav.MAV_AUTOPILOT_INVALID,
                                                0, 0, mav.MAV_STATE_ACTIVE)
                        next_hb = t0 + 1.0
                    for vid in self.cfg.vesc_ids:
                        if vescs.get(str(vid), {}).get("online"):
                            counters[vid] += 1
                    if self.cfg.esc_telemetry:
                        conn.mav.esc_telemetry_1_to_4_send(*pack_esc_telemetry(vescs, self.cfg.vesc_ids, counters))
                    payload = pack_tunnel(vescs, seq)
                    seq += 1
                    conn.mav.tunnel_send(0, 0, VESC_TUNNEL_TYPE, len(payload),
                                         list(payload.ljust(TUNNEL_MAX_PAYLOAD, b"\0")))
                    self.stop.wait(max(0.0, period - (time.time() - t0)))
            except Exception as exc:
                log.warning("MAVLink uplink hatası (%s) — 2 s sonra tekrar", exc)
                self.stop.wait(2.0)
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass


class MavlinkDownlink(threading.Thread):
    """Shore side: rebuild the telemetry state from the MAVLink stream."""

    def __init__(self, cfg, state, stop: threading.Event):
        super().__init__(daemon=True, name="mavlink-downlink")
        self.cfg, self.state, self.stop = cfg, state, stop

    def run(self) -> None:
        last_tunnel = 0.0
        while not self.stop.is_set():
            conn = None
            try:
                conn = open_connection(self.cfg.mavlink_in, self.cfg.mav_sysid, self.cfg.mav_compid)
                self.state.set_bus("mavlink", self.cfg.mavlink_in)
                log.info("MAVLink downlink dinleniyor: %s", self.cfg.mavlink_in)
                while not self.stop.is_set():
                    msg = conn.recv_match(type=["TUNNEL", "ESC_TELEMETRY_1_TO_4"], blocking=True, timeout=1.0)
                    if msg is None:
                        continue
                    now = time.time()
                    if msg.get_type() == "TUNNEL":
                        if msg.payload_type != VESC_TUNNEL_TYPE:
                            continue
                        last_tunnel = now
                        for vid, f in unpack_tunnel(bytes(msg.payload[:msg.payload_length])).items():
                            if vid in self.cfg.vesc_ids and f.pop("online"):
                                self.state.update(vid, f)
                    elif now - last_tunnel > ESC_TELEMETRY_STALE_S:
                        self._apply_esc_telemetry(msg)
            except Exception as exc:
                log.warning("MAVLink downlink hatası (%s) — 2 s sonra tekrar", exc)
                self.state.set_bus("reconnecting", self.cfg.mavlink_in)
                self.stop.wait(2.0)
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

    def _apply_esc_telemetry(self, msg) -> None:
        """Lossy fallback when only ESC_TELEMETRY_1_TO_4 arrives (e.g. another
        sender). voltage == 0 is treated as 'no data for this slot'."""
        for i, vid in enumerate(list(self.cfg.vesc_ids)[:4]):
            if msg.voltage[i] == 0:
                continue
            self.state.update(vid, {
                "temp_fet": float(msg.temperature[i]),
                "v_in": msg.voltage[i] / 100.0,
                "current_motor": msg.current[i] / 100.0,
                "ah_used": msg.totalcurrent[i] / 1000.0,
                "erpm": msg.rpm[i] * self.cfg.pole_pairs,
            })
