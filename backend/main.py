#!/usr/bin/env python3
"""VESC CAN telemetry dashboard.

Reads VESC CAN status frames over an SLCAN adapter (ArduPilot SLCAN
passthrough on a Cube Orange), keeps the latest telemetry per VESC in a
thread-safe dict and pushes it to browsers over a WebSocket at 10 Hz.

Frame layouts are verified against the VESC firmware source at tag 5.02
(vedderb/bldc: comm_can.c, commands.c, datatypes.h) — see
docs/CAN_PROTOCOL_FW52.md for the source-cited protocol reference.
FW 5.2 broadcasts STATUS 1-5 only; CAN_PACKET_STATUS_6 (ADC/PPM) exists
only from FW 6.00 on, as command id 58 (enable with --fw 6.0). Fault codes
are not broadcast on any firmware, so they are polled at 1 Hz per VESC via
CAN_PACKET_PROCESS_SHORT_BUFFER + COMM_GET_VALUES_SELECTIVE with a
fault-only mask — request and reply each fit in a single CAN frame.

Run:  python backend/main.py            (real bus, auto-detects /dev/tty.usbmodem*)
      python backend/main.py --mock     (fake data for UI development)
"""

import argparse
import asyncio
import glob
import json
import logging
import math
import random
import struct
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

log = logging.getLogger("vesc-dash")

STATIC_DIR = Path(__file__).resolve().parent / "static"

# SLCAN serial device search patterns. macOS exposes each USB CDC port twice;
# pyserial recommends the cu.* node (tty.* can block on open waiting for DCD),
# so cu.* is preferred and the tty.* twin is dropped. Linux as a fallback.
PORT_GLOBS = ("/dev/cu.usbmodem*", "/dev/tty.usbmodem*", "/dev/ttyACM*")

OFFLINE_AFTER_S = 2.0   # no frame for this long -> VESC counts as offline
PROBE_TIMEOUT_S = 3.0   # a candidate port must yield a VESC frame within this
STALE_FAULT_S = 5.0     # fault older than this (no poll reply) is flagged stale
STATUS_FRAMES_PER_TICK = 5  # FW 5.2 CAN_STATUS_1_2_3_4_5: 5 frames per rate tick


# ---------------------------------------------------------------------------
# Config / shared state
# ---------------------------------------------------------------------------

@dataclass
class Config:
    mock: bool = False
    port: str | None = None
    bitrate: int = 500_000
    pole_pairs: int = 7
    vesc_ids: tuple[int, ...] = (21, 22, 23, 24)  # the ESC ids on this bus (--vesc-ids)
    host: str = "127.0.0.1"
    http_port: int = 8000
    fw: str = "5.2"          # "5.2" or "6.0" — selects which status frames exist
    poll_faults: bool = True  # poll fault codes over CAN (real bus only)
    dash_id: int = 250        # our controller id on the VESC CAN protocol (must not collide with VESC ids)
    status_rate_hz: float = 50  # VESC "CAN Status Rate" — only used to estimate expected fps
    # v2: CAN access path and MAVLink sea link
    can_interface: str = "slcan"      # slcan (Cube SLCAN passthrough / serial adapter) | socketcan (USB-CAN, Linux)
                                      # | mavlink (ArduPilot MAV_CMD_CAN_FORWARD over the MAVLink port — works while armed)
    mav_can_bus: int = 1              # mavlink transport: autopilot CAN bus, 1-based (CAN1 -> 1)
    channel: str | None = None        # socketcan channel (default can0); for slcan same as --port
    mavlink_out: str | None = None    # vessel: push telemetry here (e.g. /dev/ttyAMA0:115200 -> Cube TELEM2)
    mavlink_in: str | None = None     # shore: rebuild state from here (e.g. udpin:0.0.0.0:14551)
    uplink_rate: float = 1.0          # Hz for ESC_TELEMETRY + TUNNEL
    esc_telemetry: bool = True        # also send GCS-native ESC_TELEMETRY_1_TO_4
    mav_sysid: int = 1                # same vehicle sysid as the autopilot
    mav_compid: int = 191             # MAV_COMP_ID_ONBOARD_COMPUTER
    offline_after_s: float = OFFLINE_AFTER_S

    def __post_init__(self) -> None:
        self.parsers = parsers_for_fw(self.fw)
        if self.can_interface == "socketcan" and self.channel is None:
            self.channel = "can0"

    def validate(self) -> list[str]:
        errors = []
        if self.pole_pairs < 1:
            errors.append("--pole-pairs en az 1 olmalı")
        if self.can_interface not in ("slcan", "socketcan", "mavlink"):
            errors.append("--can-interface slcan, socketcan ya da mavlink olmalı")
        if not 1 <= self.mav_can_bus <= 3:
            errors.append("--mav-can-bus 1-3 aralığında olmalı (CAN1 = 1)")
        if self.mavlink_out == "same" and self.can_interface != "mavlink":
            errors.append("--mavlink-out same yalnız --can-interface mavlink ile kullanılabilir")
        if self.mavlink_out == "same" and self.mock:
            errors.append("--mavlink-out same --mock ile kullanılamaz (paylaşılacak CAN bağlantısı yok)")
        if self.mav_compid == 1:
            errors.append("--mav-compid 1 otopilotun kendi id'si — ArduPilot paketleri loopback sayıp atar; 191 kullanın")
        if self.uplink_rate <= 0:
            errors.append("--uplink-rate pozitif olmalı")
        if self.mavlink_in and (self.mock or self.mavlink_out):
            errors.append("--mavlink-in (kara modu) --mock veya --mavlink-out ile birlikte kullanılamaz")
        if not 1 <= self.mav_sysid <= 255 or not 1 <= self.mav_compid <= 255:
            errors.append("--mav-sysid/--mav-compid 1-255 aralığında olmalı")
        if not self.vesc_ids or len(set(self.vesc_ids)) != len(self.vesc_ids) \
                or any(not 0 <= v <= 254 for v in self.vesc_ids):
            errors.append("--vesc-ids: 0-254 arası, tekrarsız, virgülle ayrılmış id listesi olmalı")
        if not 0 <= self.dash_id <= 254:
            errors.append("--dash-id 0-254 aralığında olmalı (255 = VESC broadcast)")
        elif self.dash_id in self.vesc_ids:
            errors.append(f"--dash-id {self.dash_id} bir VESC id'si ile çakışıyor")
        if self.status_rate_hz < 1:
            errors.append("--status-rate-hz en az 1 olmalı")
        if not 1 <= self.http_port <= 65535:
            errors.append("--http-port 1-65535 aralığında olmalı")
        return errors


class TelemetryState:
    """Latest telemetry per VESC + bus status, shared between the CAN reader
    thread and the asyncio broadcaster."""

    def __init__(self, vesc_ids: tuple[int, ...], offline_after_s: float = OFFLINE_AFTER_S,
                 frames_per_tick: int = STATUS_FRAMES_PER_TICK):
        self._lock = threading.Lock()
        self.vescs: dict[int, dict] = {vid: {} for vid in vesc_ids}
        self.offline_after_s = offline_after_s
        self.frames_per_tick = frames_per_tick  # frames one VESC produces per status tick
        self.frames_total = 0
        self.last_frame_t: float | None = None  # last accepted VESC frame (any id)
        # VESC status frames seen from ids that are NOT in vesc_ids (misconfigured --vesc-ids)
        self.unknown_ids: dict[int, int] = {}
        self.transport = "slcan"  # slcan | socketcan | mavlink | mock | mavlink-in (for the UI label)
        self.bus_note: str | None = None  # transport-specific problem text (e.g. CAN_FORWARD rejected)
        self.bus_status = "starting"  # starting | probing | connected | reconnecting | mock
        self.bus_port: str | None = None

    def update(self, vesc_id: int, fields: dict, frames: int = 1) -> None:
        now = time.time()
        with self._lock:
            d = self.vescs[vesc_id]
            d.update(fields)
            d["last_seen"] = now
            if "fault" in fields:
                d["fault_seen"] = now
            self.frames_total += frames
            self.last_frame_t = now

    def note_unknown(self, vesc_id: int) -> None:
        with self._lock:
            self.unknown_ids[vesc_id] = self.unknown_ids.get(vesc_id, 0) + 1

    def set_bus(self, status: str, port: str | None) -> None:
        with self._lock:
            self.bus_status = status
            self.bus_port = port

    def set_note(self, note: str | None) -> None:
        with self._lock:
            self.bus_note = note

    def is_online(self, vesc_id: int) -> bool:
        with self._lock:
            last_seen = self.vescs[vesc_id].get("last_seen")
        return last_seen is not None and time.time() - last_seen < self.offline_after_s

    def snapshot(self, pole_pairs: int, fps: float, status_rate_hz: float) -> dict:
        now = time.time()
        with self._lock:
            vescs = {}
            n_online = 0
            for vid, d in self.vescs.items():
                c = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()}
                last_seen = c.get("last_seen")
                age = (now - last_seen) if last_seen else None
                c["age"] = round(age, 2) if age is not None else None
                c["online"] = age is not None and age < self.offline_after_s
                n_online += c["online"]
                if "fault_seen" in c:
                    c["fault_age"] = round(now - c.pop("fault_seen"), 1)
                if "erpm" in c:
                    c["rpm"] = round(c["erpm"] / pole_pairs, 1)
                # No motor NTC connected (e.g. sensorless thruster motors):
                # the firmware reads an open input as deeply negative and clamps
                # invalid values to -100 °C. Report "no sensor" instead.
                tm = c.get("temp_motor")
                if tm is not None and tm <= MOTOR_TEMP_SENSOR_MISSING_BELOW_C:
                    c["temp_motor"] = None
                    c["motor_temp_sensor"] = False
                if "fault" in c:
                    f = c["fault"]
                    c["fault_name"] = FAULT_CODES[f] if 0 <= f < len(FAULT_CODES) else f"CODE_{f}"
                vescs[str(vid)] = c
            frame_age = (now - self.last_frame_t) if self.last_frame_t else None
            return {
                "t": round(now, 3),
                "bus": {
                    "status": self.bus_status,
                    "port": self.bus_port,
                    "fps": round(fps, 1),
                    # expected CAN frame rate for the VESCs currently online
                    "fps_expected": round(n_online * self.frames_per_tick * status_rate_hz, 1),
                    "frame_age": round(frame_age, 1) if frame_age is not None else None,
                    "unknown_ids": sorted(self.unknown_ids),
                    "transport": self.transport,
                    "note": self.bus_note,
                },
                "vesc_ids": list(self.vescs.keys()),
                "pole_pairs": pole_pairs,
                "vescs": vescs,
            }


# ---------------------------------------------------------------------------
# VESC CAN frame parsing
# ---------------------------------------------------------------------------
# Extended (29-bit) arbitration ID: (command_id << 8) | vesc_id, big-endian payload.
# Command ids and scales verified against vedderb/bldc tag 5.02 (comm_can.c,
# datatypes.h CAN_PACKET_ID enum). On FW 5.2 command 28 is
# CAN_PACKET_POLL_TS5700N8501_STATUS (encoder), NOT a status frame;
# CAN_PACKET_STATUS_6 only exists from FW 6.00 on, as command id 58.

CAN_PACKET_PROCESS_SHORT_BUFFER = 8
COMM_GET_VALUES_SELECTIVE = 50
GET_VALUES_MASK_FAULT = 1 << 15  # commands.c: fault code is bit 15 of the selective mask

# datatypes.h (tag 5.02): mc_fault_code, values 0-25
FAULT_CODES = (
    "NONE", "OVER_VOLTAGE", "UNDER_VOLTAGE", "DRV", "ABS_OVER_CURRENT",
    "OVER_TEMP_FET", "OVER_TEMP_MOTOR", "GATE_DRIVER_OVER_VOLTAGE",
    "GATE_DRIVER_UNDER_VOLTAGE", "MCU_UNDER_VOLTAGE",
    "BOOTING_FROM_WATCHDOG_RESET", "ENCODER_SPI",
    "ENCODER_SINCOS_BELOW_MIN_AMPLITUDE", "ENCODER_SINCOS_ABOVE_MAX_AMPLITUDE",
    "FLASH_CORRUPTION", "HIGH_OFFSET_CURRENT_SENSOR_1",
    "HIGH_OFFSET_CURRENT_SENSOR_2", "HIGH_OFFSET_CURRENT_SENSOR_3",
    "UNBALANCED_CURRENTS", "BRK", "RESOLVER_LOT", "RESOLVER_DOS",
    "RESOLVER_LOS", "FLASH_CORRUPTION_APP_CFG", "FLASH_CORRUPTION_MC_CFG",
    "ENCODER_NO_MAGNET",
)

# mc_interface.c clamps an invalid/absent motor NTC reading to -100 °C, and an
# open sensor input reads deeply negative — below this the sensor is missing.
MOTOR_TEMP_SENSOR_MISSING_BELOW_C = -50.0

def _i16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">h", data, offset)[0]


def _i32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">i", data, offset)[0]


def _parse_status(d: bytes) -> dict:  # CAN_PACKET_STATUS (9)
    return {
        "erpm": _i32(d, 0),
        "current_motor": _i16(d, 4) / 10.0,
        "duty": _i16(d, 6) / 1000.0,
    }


def _parse_status_2(d: bytes) -> dict:  # CAN_PACKET_STATUS_2 (14)
    return {
        "ah_used": _i32(d, 0) / 10000.0,
        "ah_charged": _i32(d, 4) / 10000.0,
    }


def _parse_status_3(d: bytes) -> dict:  # CAN_PACKET_STATUS_3 (15)
    return {
        "wh_used": _i32(d, 0) / 10000.0,
        "wh_charged": _i32(d, 4) / 10000.0,
    }


def _parse_status_4(d: bytes) -> dict:  # CAN_PACKET_STATUS_4 (16)
    return {
        "temp_fet": _i16(d, 0) / 10.0,
        "temp_motor": _i16(d, 2) / 10.0,
        "current_in": _i16(d, 4) / 10.0,
        "pid_pos": _i16(d, 6) / 50.0,
    }


def _parse_status_5(d: bytes) -> dict:  # CAN_PACKET_STATUS_5 (27)
    return {
        "tacho": _i32(d, 0),
        "v_in": _i16(d, 4) / 10.0,
    }


def _parse_status_6(d: bytes) -> dict:  # CAN_PACKET_STATUS_6 (58, FW 6.00+)
    return {
        "adc1": _i16(d, 0) / 1000.0,
        "adc2": _i16(d, 2) / 1000.0,
        "adc3": _i16(d, 4) / 1000.0,
        "ppm": _i16(d, 6) / 1000.0,
    }


# command_id -> (parser, minimum payload length)
PARSERS_FW52 = {
    9: (_parse_status, 8),
    14: (_parse_status_2, 8),
    15: (_parse_status_3, 8),
    16: (_parse_status_4, 8),
    27: (_parse_status_5, 6),  # 8 bytes on the wire; bytes 6-7 are reserved
}
PARSERS_FW60 = {**PARSERS_FW52, 58: (_parse_status_6, 8)}


def parsers_for_fw(fw: str) -> dict:
    return PARSERS_FW60 if fw.startswith("6") else PARSERS_FW52


CONFIG = Config()
STATE = TelemetryState(CONFIG.vesc_ids)


def build_fault_poll_frame(target_vesc_id: int, dash_id: int) -> tuple[int, bytes]:
    """(arbitration_id, data) asking `target_vesc_id` for its fault code.

    comm_can.c CAN_PACKET_PROCESS_SHORT_BUFFER: data = [reply_to_id,
    process_mode(0 = process and reply over CAN), COMM payload...]. The COMM
    payload is COMM_GET_VALUES_SELECTIVE + uint32 mask (fault only).
    """
    arb = (CAN_PACKET_PROCESS_SHORT_BUFFER << 8) | target_vesc_id
    data = bytes([dash_id, 0x00, COMM_GET_VALUES_SELECTIVE]) \
        + GET_VALUES_MASK_FAULT.to_bytes(4, "big")
    return arb, data


def handle_frame(arbitration_id: int, data: bytes, cfg: Config, state: TelemetryState) -> bool:
    """Parse one extended frame; returns True if it was an accepted VESC frame.

    The firmware compares the *whole* `eid >> 8` against CAN_PACKET_ID
    (comm_can.c decode_msg), so bits 16-28 must be zero. Masking to 8 bits
    would accept non-VESC traffic such as ArduPilot's DroneCAN frames.
    """
    vesc_id = arbitration_id & 0xFF
    command_id = arbitration_id >> 8

    # Reply to our fault poll: addressed to dash_id, sent via short buffer.
    # comm_can_send_buffer (<=6 byte payloads): data = [vesc_controller_id,
    # send_flag, COMM_GET_VALUES_SELECTIVE, mask(4), fault(1)] = 8 bytes.
    if command_id == CAN_PACKET_PROCESS_SHORT_BUFFER and vesc_id == cfg.dash_id:
        if len(data) >= 8 and data[2] == COMM_GET_VALUES_SELECTIVE:
            responder = data[0]
            mask = int.from_bytes(data[3:7], "big")
            if responder in cfg.vesc_ids and mask == GET_VALUES_MASK_FAULT:
                state.update(responder, {"fault": data[7]})
                return True
        return False

    if vesc_id not in cfg.vesc_ids:
        if command_id in cfg.parsers:  # a real VESC status frame from an id we were not told about
            state.note_unknown(vesc_id)
        return False
    entry = cfg.parsers.get(command_id)
    if entry is None:
        return False  # other bus traffic — ignore silently
    parser, min_len = entry
    if len(data) < min_len:
        return False
    state.update(vesc_id, parser(data))
    return True


# ---------------------------------------------------------------------------
# SLCAN port discovery + reader thread
# ---------------------------------------------------------------------------

def find_ports() -> list[str]:
    """Candidate serial ports, cu.* preferred over its tty.* twin on macOS.
    A Cube Orange exposes two USB CDC ports (SERIAL0 = MAVLink, SERIAL6 =
    SLCAN), so the list normally has two entries and must be probed."""
    ports: list[str] = []
    seen_devices: set[str] = set()
    for pattern in PORT_GLOBS:
        for p in sorted(glob.glob(pattern)):
            device = p.rsplit("/", 1)[-1].split(".", 1)[-1]  # "usbmodem1103" for cu./tty.
            if device in seen_devices:
                continue
            seen_devices.add(device)
            ports.append(p)
    return ports


class BusHolder:
    """Shares the live can.Bus between the reader thread (owner) and the
    fault poller thread (sender). `bus` is None while disconnected."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.bus = None

    def set(self, bus) -> None:
        with self.lock:
            self.bus = bus

    def get(self):
        with self.lock:
            return self.bus


BUS_HOLDER = BusHolder()


def run_bus(cfg: Config, state: TelemetryState, stop: threading.Event,
            port: str, probing: bool) -> bool:
    """Open `port` and pump frames until the bus fails or `stop` is set.

    Returns True if the port ever produced a VESC frame. While `probing`, a
    port that stays silent for PROBE_TIMEOUT_S is abandoned (returns False)
    so the caller can try the next candidate — a Cube Orange's MAVLink port
    accepts the SLCAN handshake silently and would otherwise look "connected".
    """
    import can  # imported here so --mock works without an adapter attached

    bus = None
    got_frames = False
    try:
        if cfg.can_interface == "socketcan":
            # USB-CAN adapter (candleLight/gs_usb) on Linux. Bitrate is set on
            # the interface: ip link set can0 up type can bitrate 500000
            bus = can.Bus(interface="socketcan", channel=port)
        elif cfg.can_interface == "mavlink":
            # ArduPilot MAVLink CAN forwarding: not affected by arming. `port` is a
            # pymavlink spec (/dev/cu.usbmodemXXXX[:baud], udpin:..., udpout:...).
            from mavcan import MavlinkCanBus
            bus = MavlinkCanBus(port, cfg.mav_can_bus, cfg.mav_sysid, cfg.mav_compid)
        else:
            # ArduPilot streams before "O" and python-can's default 2 s settle
            # delay only matters for Arduino adapters; flush the partial line
            # that is almost certainly sitting in the input buffer.
            bus = can.Bus(interface="slcan", channel=port, bitrate=cfg.bitrate, sleep_after_open=0.3)
            try:
                bus.flush()
            except Exception:
                pass
        BUS_HOLDER.set(bus)
        state.set_bus("probing" if probing else "connected", port)
        t_open = time.time()
        last_note = None
        while not stop.is_set():
            try:
                msg = bus.recv(timeout=0.5)
            except (ValueError, IndexError, KeyError):
                continue  # corrupted/partial SLCAN line — not a bus failure
            note = getattr(bus, "note", None)  # mavlink transport: CAN_FORWARD rejected etc.
            if note != last_note:
                state.set_note(note)
                last_note = note
            if (msg is not None and msg.is_extended_id
                    and not msg.is_error_frame and not msg.is_remote_frame
                    and handle_frame(msg.arbitration_id, bytes(msg.data), cfg, state)
                    and not got_frames):
                got_frames = True
                state.set_bus("connected", port)
                log.info("CAN bağlandı: %s @ %d bit/s (VESC frame'leri geliyor)", port, cfg.bitrate)
            if probing and not got_frames and time.time() - t_open > PROBE_TIMEOUT_S:
                unk = sorted(state.unknown_ids)
                if unk:
                    log.warning("%s: hatta VESC status frame'leri var ama id'ler listede yok: %s — "
                                "--vesc-ids %s ile başlatın (şu an: %s)", port, unk,
                                ",".join(map(str, unk)), ",".join(map(str, cfg.vesc_ids)))
                else:
                    log.info("%s: %.0f s içinde VESC frame'i yok — sonraki port deneniyor", port, PROBE_TIMEOUT_S)
                return False
    except Exception as exc:  # USB pulled, serial error, open failure, ...
        log.warning("CAN bus hatası (%s: %s) — yeniden bağlanılacak", port, exc)
        state.set_bus("reconnecting", port)
    finally:
        BUS_HOLDER.set(None)
        state.set_note(None)
        if bus is not None:
            try:
                bus.shutdown()
            except Exception:
                pass
    return got_frames


def can_reader(cfg: Config, state: TelemetryState, stop: threading.Event) -> None:
    if cfg.can_interface == "socketcan":
        while not stop.is_set():  # fixed channel: no probing, just reconnect
            run_bus(cfg, state, stop, cfg.channel, probing=False)
            stop.wait(2.0)
        return
    preferred = cfg.port
    while not stop.is_set():
        ports = [cfg.port] if cfg.port else find_ports()
        if preferred in ports:  # last known-good port first
            ports.remove(preferred)
            ports.insert(0, preferred)
        if not ports:
            state.set_bus("reconnecting", None)
            stop.wait(2.0)
            continue
        for port in ports:
            if stop.is_set():
                break
            # With a single candidate (or an explicit --port) there is nothing
            # else to try, so stay on it and let the UI show "no frames".
            if run_bus(cfg, state, stop, port, probing=len(ports) > 1):
                preferred = port
                break
        stop.wait(2.0)


def fault_poller(cfg: Config, state: TelemetryState, stop: threading.Event) -> None:
    """Asks each online VESC for its fault code roughly once a second
    (staggered). Faults are not part of the STATUS broadcasts on any firmware,
    so this is the only way to see e.g. ABS_OVER_CURRENT remotely. Offline
    VESCs are skipped: an unacknowledged frame would sit in ArduPilot's CAN
    TX queue and bump its error counters for nothing."""
    import can

    targets = list(cfg.vesc_ids)
    i = 0
    while not stop.is_set():
        stop.wait(1.0 / max(len(targets), 1))
        bus = BUS_HOLDER.get()
        vid = targets[i % len(targets)]
        i += 1
        if bus is None or not state.is_online(vid):
            continue
        arb, data = build_fault_poll_frame(vid, cfg.dash_id)
        try:
            bus.send(can.Message(arbitration_id=arb, data=data, is_extended_id=True))
        except Exception:
            pass  # bus is going away; the reader thread handles reconnection


# ---------------------------------------------------------------------------
# Mock data generator (--mock)
# ---------------------------------------------------------------------------

def mock_generator(cfg: Config, state: TelemetryState, stop: threading.Event) -> None:
    state.set_bus("mock", "mock")
    cfg.status_rate_hz = 10  # the generator ticks at 10 Hz; keeps fps_expected honest
    t0 = time.time()
    last = t0
    ah = {vid: 0.0 for vid in cfg.vesc_ids}
    wh = {vid: 0.0 for vid in cfg.vesc_ids}
    tacho = {vid: 0.0 for vid in cfg.vesc_ids}
    # Per-VESC temperature profiles so all three color bands show up:
    # (base °C, swing °C) — VESC 3 deliberately peaks above 80.
    temp_profiles = [(48, 6), (60, 9), (54, 8), (72, 16)]  # by position, not by id

    while not stop.is_set():
        now = time.time()
        dt, last = now - last, now
        t = now - t0
        for i, vid in enumerate(cfg.vesc_ids):
            ph = i * 1.7
            rpm = 2600 + 1800 * math.sin(t / 6 + ph) + random.uniform(-40, 40)
            erpm = rpm * cfg.pole_pairs
            duty = max(-0.95, min(0.95, rpm / 5200 + 0.02 * math.sin(t / 2 + ph)))
            i_mot = 12 + 9 * math.sin(t / 3.5 + ph * 2) + random.uniform(-0.8, 0.8)
            i_in = abs(i_mot * duty) + random.uniform(0.0, 0.3)
            v_in = 39.5 - 0.06 * i_in - 0.4 * math.sin(t / 40) + random.uniform(-0.05, 0.05)
            base, swing = temp_profiles[i % len(temp_profiles)]
            temp_fet = base + swing * math.sin(t / 25 + ph) + random.uniform(-0.3, 0.3)
            ah[vid] += i_in * dt / 3600.0
            wh[vid] += v_in * i_in * dt / 3600.0
            tacho[vid] += erpm / 60.0 * 6.0 * dt
            # Sensorless motors without an NTC: firmware reports the clamped
            # -100 °C sentinel, exactly like the real bus would.
            fields = {
                "erpm": int(erpm),
                "current_motor": i_mot,
                "duty": duty,
                "ah_used": ah[vid],
                "ah_charged": ah[vid] * 0.04,
                "wh_used": wh[vid],
                "wh_charged": wh[vid] * 0.04,
                "temp_fet": temp_fet,
                "temp_motor": -100.0,
                "current_in": i_in,
                "pid_pos": (t * 10 + i * 90) % 360,
                "tacho": int(tacho[vid]),
                "v_in": v_in,
                # VESC 1 raises ABS_OVER_CURRENT for 6 s out of every 40 s.
                "fault": 4 if (i == 1 and t % 40 < 6) else 0,
            }
            if cfg.fw.startswith("6"):  # STATUS_6 exists only on FW 6.00+
                fields.update({
                    "adc1": 1.65 + 0.4 * math.sin(t / 7 + ph),
                    "adc2": 1.65 + 0.4 * math.cos(t / 9 + ph),
                    "adc3": 0.8 + 0.2 * math.sin(t / 5 + ph),
                    "ppm": 0.5 + 0.45 * math.sin(t / 6 + ph),
                })
            state.update(vid, fields, frames=5)  # STATUS 1-5 per update
        stop.wait(0.1)


# ---------------------------------------------------------------------------
# FastAPI app: / (static UI), /ws (10 Hz state push)
# ---------------------------------------------------------------------------

ws_clients: set[WebSocket] = set()


async def _send_snapshot(ws: WebSocket, text: str) -> None:
    try:
        await asyncio.wait_for(ws.send_text(text), timeout=0.5)
    except Exception:  # slow or gone — drop it so it cannot stall the others
        ws_clients.discard(ws)


async def broadcaster() -> None:
    prev_frames = STATE.frames_total
    prev_t = time.time()
    fps = 0.0
    while True:
        await asyncio.sleep(0.1)
        try:
            now = time.time()
            total = STATE.frames_total
            inst = (total - prev_frames) / max(now - prev_t, 1e-6)
            prev_frames, prev_t = total, now
            fps = 0.85 * fps + 0.15 * inst
            if not ws_clients:
                continue
            text = json.dumps(STATE.snapshot(CONFIG.pole_pairs, fps, CONFIG.status_rate_hz))
            await asyncio.gather(*(_send_snapshot(ws, text) for ws in list(ws_clients)))
        except asyncio.CancelledError:
            raise
        except Exception:  # never let one bad tick kill the push loop
            log.exception("broadcaster tick failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = threading.Event()
    if CONFIG.mavlink_in:  # shore: no CAN at all, state comes over the radio
        from uplink import MavlinkDownlink
        MavlinkDownlink(CONFIG, STATE, stop).start()
    else:
        target = mock_generator if CONFIG.mock else can_reader
        threading.Thread(target=target, args=(CONFIG, STATE, stop), daemon=True).start()
        if not CONFIG.mock and CONFIG.poll_faults:
            threading.Thread(target=fault_poller, args=(CONFIG, STATE, stop), daemon=True).start()
        if CONFIG.mavlink_out:  # vessel: push snapshots toward the GCS
            from uplink import MavlinkUplink
            shared = (lambda: BUS_HOLDER.get()) if CONFIG.mavlink_out == "same" else None
            MavlinkUplink(CONFIG, STATE, stop, shared=shared).start()
    task = asyncio.create_task(broadcaster())
    yield
    stop.set()
    task.cancel()


app = FastAPI(title="VESC CAN Telemetry", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    ws_clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # only to detect disconnect; input is ignored
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(ws)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> Config:
    p = argparse.ArgumentParser(description="VESC CAN telemetry dashboard")
    p.add_argument("--mock", action="store_true",
                   help="gerçek CAN yerine 4 VESC için sahte veri üret")
    p.add_argument("--port", help="slcan: seri port; mavlink: pymavlink bağlantısı (/dev/cu.usbmodemXXXX[:baud], "
                                  "udpin:host:port, udpout:host:port). Varsayılan: usbmodem/ttyACM portlarını sırayla dene")
    p.add_argument("--bitrate", type=int, default=500_000, help="CAN bitrate (varsayılan 500000)")
    p.add_argument("--vesc-ids", default="21,22,23,24",
                   help="bus'taki VESC id'leri, virgülle (varsayılan 21,22,23,24)")
    p.add_argument("--pole-pairs", type=int, default=7,
                   help="motor kutup çifti sayısı, RPM = ERPM / pole_pairs (varsayılan 7)")
    p.add_argument("--fw", choices=("5.2", "6.0"), default="5.2",
                   help="VESC firmware sürümü: 5.2 = STATUS 1-5; 6.0 STATUS_6'yı (cmd 58, ADC/PPM) ekler")
    p.add_argument("--no-poll-faults", action="store_true",
                   help="fault kodu sorgulamayı kapat (varsayılan: her VESC ~1 Hz sorgulanır)")
    p.add_argument("--dash-id", type=int, default=250,
                   help="dashboard'un VESC CAN protokolündeki controller id'si (varsayılan 250)")
    p.add_argument("--status-rate-hz", type=float, default=50,
                   help="VESC Tool'daki CAN Status Rate; beklenen fps ve frame kaybı uyarısı için (varsayılan 50)")
    g = p.add_argument_group("v2 — USB-CAN adaptör ve MAVLink deniz hattı")
    g.add_argument("--can-interface", choices=("slcan", "socketcan", "mavlink"), default="slcan",
                   help="slcan: Cube SLCAN passthrough / seri adaptör; socketcan: Linux'ta USB-CAN (candleLight); "
                        "mavlink: Cube'un MAVLink portundan CAN forwarding (armed iken de çalışır)")
    g.add_argument("--mav-can-bus", type=int, default=1, help="mavlink transport: otopilot CAN bus numarası, 1 = CAN1 (varsayılan)")
    g.add_argument("--channel", help="socketcan arayüzü (varsayılan can0)")
    g.add_argument("--mavlink-out", metavar="CONN",
                   help="gemi: telemetriyi bu MAVLink bağlantısına bas, örn. /dev/ttyAMA0:115200 (Cube TELEM2), "
                        "udpout:host:port, ya da 'same' (--can-interface mavlink bağlantısını paylaş)")
    g.add_argument("--mavlink-in", metavar="CONN",
                   help="kara: state'i bu MAVLink akışından kur, örn. udpin:0.0.0.0:14551 (GCS mirror) — CAN kullanılmaz")
    g.add_argument("--uplink-rate", type=float, default=1.0, help="MAVLink gönderim hızı Hz (varsayılan 1)")
    g.add_argument("--no-esc-telemetry", action="store_true",
                   help="GCS'ye ESC_TELEMETRY_1_TO_4 gönderme (yalnız TUNNEL)")
    g.add_argument("--mav-sysid", type=int, default=1, help="MAVLink system id (otopilotla aynı, varsayılan 1)")
    g.add_argument("--mav-compid", type=int, default=191, help="MAVLink component id (varsayılan 191 = onboard computer)")
    g.add_argument("--offline-after", type=float, default=None,
                   help="bu kadar saniye veri gelmeyen VESC offline sayılır (CAN: 2, MAVLink kara: 5)")
    p.add_argument("--host", default="127.0.0.1", help="HTTP host (varsayılan 127.0.0.1)")
    p.add_argument("--http-port", type=int, default=8000, help="HTTP port (varsayılan 8000)")
    a = p.parse_args()
    try:
        vesc_ids = tuple(int(x) for x in a.vesc_ids.split(",") if x.strip())
    except ValueError:
        p.error("--vesc-ids sayı listesi olmalı, örn. 21,22,23,24")
    offline = a.offline_after if a.offline_after is not None else (5.0 if a.mavlink_in else OFFLINE_AFTER_S)
    cfg = Config(mock=a.mock, port=a.port, bitrate=a.bitrate, vesc_ids=vesc_ids,
                 pole_pairs=a.pole_pairs, host=a.host, http_port=a.http_port,
                 fw=a.fw, poll_faults=not a.no_poll_faults, dash_id=a.dash_id,
                 status_rate_hz=a.status_rate_hz, can_interface=a.can_interface, mav_can_bus=a.mav_can_bus,
                 channel=a.channel or a.port, mavlink_out=a.mavlink_out, mavlink_in=a.mavlink_in,
                 uplink_rate=a.uplink_rate, esc_telemetry=not a.no_esc_telemetry,
                 mav_sysid=a.mav_sysid, mav_compid=a.mav_compid, offline_after_s=offline)
    errors = cfg.validate()
    if errors:
        p.error("; ".join(errors))
    return cfg


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    global CONFIG, STATE
    CONFIG = parse_args()
    if CONFIG.mavlink_in:
        # One TUNNEL record per VESC per uplink tick replaces 5 CAN frames per status tick.
        CONFIG.status_rate_hz = CONFIG.uplink_rate
        STATE = TelemetryState(CONFIG.vesc_ids, CONFIG.offline_after_s, frames_per_tick=1)
        source = f"MAVLink kara modu: {CONFIG.mavlink_in}"
    else:
        STATE = TelemetryState(CONFIG.vesc_ids, CONFIG.offline_after_s)
        if CONFIG.mock:
            source = "mock veri"
        elif CONFIG.can_interface == "socketcan":
            source = f"socketcan {CONFIG.channel}"
        elif CONFIG.can_interface == "mavlink":
            source = f"MAVLink CAN forward bus {CONFIG.mav_can_bus} via {CONFIG.port or 'otomatik port'}"
        else:
            ports = find_ports()
            if CONFIG.port:
                source = f"slcan {CONFIG.port}"
            elif ports:
                source = "slcan otomatik (adaylar: " + ", ".join(ports) + ")"
            else:
                source = "slcan — port bulunamadı, takılınca bağlanılacak"
        if CONFIG.mavlink_out:
            source += f" → MAVLink {CONFIG.mavlink_out} @ {CONFIG.uplink_rate:g} Hz"

    STATE.transport = "mavlink-in" if CONFIG.mavlink_in else ("mock" if CONFIG.mock else CONFIG.can_interface)
    log.info("VESC id'leri: %s (pole_pairs=%d)", ",".join(map(str, CONFIG.vesc_ids)), CONFIG.pole_pairs)
    log.info("Dashboard: http://localhost:%d  (%s)", CONFIG.http_port, source)
    uvicorn.run(app, host=CONFIG.host, port=CONFIG.http_port, log_level="warning")


if __name__ == "__main__":
    main()
