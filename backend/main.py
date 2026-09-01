#!/usr/bin/env python3
"""VESC CAN telemetry dashboard.

Reads VESC CAN status frames over an SLCAN adapter (ArduPilot SLCAN
passthrough on a Cube Orange), keeps the latest telemetry per VESC in a
thread-safe dict and pushes it to browsers over a WebSocket at 10 Hz.

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
import sys
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

log = logging.getLogger("vesc-dash")

STATIC_DIR = Path(__file__).resolve().parent / "static"

# SLCAN serial device search patterns: macOS first (Cube Orange over USB),
# then Linux as a fallback.
PORT_GLOBS = ("/dev/tty.usbmodem*", "/dev/ttyACM*")

OFFLINE_AFTER_S = 2.0  # no frame for this long -> VESC counts as offline


# ---------------------------------------------------------------------------
# Config / shared state
# ---------------------------------------------------------------------------

@dataclass
class Config:
    mock: bool = False
    port: str | None = None
    bitrate: int = 500_000
    pole_pairs: int = 7
    vesc_ids: tuple[int, ...] = (0, 1, 2, 3)
    host: str = "127.0.0.1"
    http_port: int = 8000


class TelemetryState:
    """Latest telemetry per VESC + bus status, shared between the CAN reader
    thread and the asyncio broadcaster."""

    def __init__(self, vesc_ids: tuple[int, ...]):
        self._lock = threading.Lock()
        self.vescs: dict[int, dict] = {vid: {} for vid in vesc_ids}
        self.frames_total = 0
        self.bus_status = "starting"  # starting | connected | reconnecting | mock
        self.bus_port: str | None = None

    def update(self, vesc_id: int, fields: dict, frames: int = 1) -> None:
        now = time.time()
        with self._lock:
            d = self.vescs[vesc_id]
            d.update(fields)
            d["last_seen"] = now
            self.frames_total += frames

    def set_bus(self, status: str, port: str | None) -> None:
        with self._lock:
            self.bus_status = status
            self.bus_port = port

    def snapshot(self, pole_pairs: int, fps: float) -> dict:
        now = time.time()
        with self._lock:
            vescs = {}
            for vid, d in self.vescs.items():
                c = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()}
                last_seen = c.get("last_seen")
                age = (now - last_seen) if last_seen else None
                c["age"] = round(age, 2) if age is not None else None
                c["online"] = age is not None and age < OFFLINE_AFTER_S
                if "erpm" in c:
                    c["rpm"] = round(c["erpm"] / pole_pairs, 1)
                vescs[str(vid)] = c
            return {
                "t": round(now, 3),
                "bus": {
                    "status": self.bus_status,
                    "port": self.bus_port,
                    "fps": round(fps, 1),
                },
                "pole_pairs": pole_pairs,
                "vescs": vescs,
            }


CONFIG = Config()
STATE = TelemetryState(CONFIG.vesc_ids)


# ---------------------------------------------------------------------------
# VESC CAN frame parsing
# ---------------------------------------------------------------------------
# Extended (29-bit) arbitration ID: (command_id << 8) | vesc_id, big-endian payload.

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


def _parse_status_6(d: bytes) -> dict:  # CAN_PACKET_STATUS_6 (28)
    return {
        "adc1": _i16(d, 0) / 1000.0,
        "adc2": _i16(d, 2) / 1000.0,
        "adc3": _i16(d, 4) / 1000.0,
        "ppm": _i16(d, 6) / 1000.0,
    }


# command_id -> (parser, minimum payload length)
PARSERS = {
    9: (_parse_status, 8),
    14: (_parse_status_2, 8),
    15: (_parse_status_3, 8),
    16: (_parse_status_4, 8),
    27: (_parse_status_5, 6),
    28: (_parse_status_6, 8),
}


def handle_frame(arbitration_id: int, data: bytes, cfg: Config, state: TelemetryState) -> None:
    vesc_id = arbitration_id & 0xFF
    command_id = (arbitration_id >> 8) & 0xFF
    if vesc_id not in cfg.vesc_ids:
        return
    entry = PARSERS.get(command_id)
    if entry is None:
        return  # other bus traffic — ignore silently
    parser, min_len = entry
    if len(data) < min_len:
        return
    state.update(vesc_id, parser(data))


# ---------------------------------------------------------------------------
# SLCAN port discovery + reader thread
# ---------------------------------------------------------------------------

def find_ports() -> list[str]:
    ports: list[str] = []
    for pattern in PORT_GLOBS:
        ports.extend(sorted(glob.glob(pattern)))
    return ports


def choose_port_interactive(ports: list[str]) -> str:
    if not sys.stdin.isatty():
        log.warning("Birden fazla port var ama stdin tty değil; %s seçildi", ports[0])
        return ports[0]
    print("Birden fazla SLCAN portu bulundu:")
    for i, p in enumerate(ports):
        print(f"  [{i}] {p}")
    while True:
        raw = input(f"Port seç [0-{len(ports) - 1}]: ").strip()
        if raw.isdigit() and int(raw) < len(ports):
            return ports[int(raw)]
        print("Geçersiz seçim.")


def resolve_port(preferred: str | None) -> str | None:
    """Pick the serial port for (re)connecting. Called from the reader thread,
    so it never prompts: prefer the previously used port, otherwise take the
    only match, otherwise the first one."""
    ports = find_ports()
    if not ports:
        return None
    if preferred and preferred in ports:
        return preferred
    if len(ports) > 1:
        log.warning("Birden fazla port bulundu %s; %s kullanılıyor", ports, ports[0])
    return ports[0]


def can_reader(cfg: Config, state: TelemetryState, stop: threading.Event) -> None:
    import can  # imported here so --mock works without an adapter attached

    preferred = cfg.port
    while not stop.is_set():
        port = resolve_port(preferred)
        if port is None:
            state.set_bus("reconnecting", None)
            stop.wait(2.0)
            continue
        bus = None
        try:
            bus = can.Bus(interface="slcan", channel=port, bitrate=cfg.bitrate)
            preferred = port
            state.set_bus("connected", port)
            log.info("CAN bağlandı: %s @ %d bit/s", port, cfg.bitrate)
            while not stop.is_set():
                msg = bus.recv(timeout=1.0)
                if msg is None:
                    continue
                if not msg.is_extended_id or msg.is_error_frame or msg.is_remote_frame:
                    continue
                handle_frame(msg.arbitration_id, bytes(msg.data), cfg, state)
        except Exception as exc:  # USB pulled, serial error, open failure, ...
            log.warning("CAN bus hatası (%s) — yeniden bağlanılacak", exc)
            state.set_bus("reconnecting", port)
        finally:
            if bus is not None:
                try:
                    bus.shutdown()
                except Exception:
                    pass
        stop.wait(2.0)


# ---------------------------------------------------------------------------
# Mock data generator (--mock)
# ---------------------------------------------------------------------------

def mock_generator(cfg: Config, state: TelemetryState, stop: threading.Event) -> None:
    state.set_bus("mock", "mock")
    t0 = time.time()
    last = t0
    ah = {vid: 0.0 for vid in cfg.vesc_ids}
    wh = {vid: 0.0 for vid in cfg.vesc_ids}
    tacho = {vid: 0.0 for vid in cfg.vesc_ids}
    # Per-VESC temperature profiles so all three color bands show up:
    # (base °C, swing °C) — VESC 3 deliberately peaks above 80.
    temp_profile = {0: (48, 6), 1: (60, 9), 2: (54, 8), 3: (72, 16)}

    while not stop.is_set():
        now = time.time()
        dt, last = now - last, now
        t = now - t0
        for vid in cfg.vesc_ids:
            ph = vid * 1.7
            rpm = 2600 + 1800 * math.sin(t / 6 + ph) + random.uniform(-40, 40)
            erpm = rpm * cfg.pole_pairs
            duty = max(-0.95, min(0.95, rpm / 5200 + 0.02 * math.sin(t / 2 + ph)))
            i_mot = 12 + 9 * math.sin(t / 3.5 + ph * 2) + random.uniform(-0.8, 0.8)
            i_in = abs(i_mot * duty) + random.uniform(0.0, 0.3)
            v_in = 39.5 - 0.06 * i_in - 0.4 * math.sin(t / 40) + random.uniform(-0.05, 0.05)
            base, swing = temp_profile[vid]
            temp_fet = base + swing * math.sin(t / 25 + ph) + random.uniform(-0.3, 0.3)
            temp_motor = temp_fet + 6 + 3 * math.sin(t / 18 + ph)
            ah[vid] += i_in * dt / 3600.0
            wh[vid] += v_in * i_in * dt / 3600.0
            tacho[vid] += erpm / 60.0 * 6.0 * dt
            state.update(vid, {
                "erpm": int(erpm),
                "current_motor": i_mot,
                "duty": duty,
                "ah_used": ah[vid],
                "ah_charged": ah[vid] * 0.04,
                "wh_used": wh[vid],
                "wh_charged": wh[vid] * 0.04,
                "temp_fet": temp_fet,
                "temp_motor": temp_motor,
                "current_in": i_in,
                "pid_pos": (t * 10 + vid * 90) % 360,
                "tacho": int(tacho[vid]),
                "v_in": v_in,
                "adc1": 1.65 + 0.4 * math.sin(t / 7 + ph),
                "adc2": 1.65 + 0.4 * math.cos(t / 9 + ph),
                "adc3": 0.8 + 0.2 * math.sin(t / 5 + ph),
                "ppm": 0.5 + 0.45 * math.sin(t / 6 + ph),
            }, frames=6)  # emulates the 6 status frames per update
        stop.wait(0.1)


# ---------------------------------------------------------------------------
# FastAPI app: / (static UI), /ws (10 Hz state push)
# ---------------------------------------------------------------------------

ws_clients: set[WebSocket] = set()


async def broadcaster() -> None:
    prev_frames = STATE.frames_total
    prev_t = time.time()
    fps = 0.0
    while True:
        await asyncio.sleep(0.1)
        now = time.time()
        total = STATE.frames_total
        inst = (total - prev_frames) / max(now - prev_t, 1e-6)
        prev_frames, prev_t = total, now
        fps = 0.85 * fps + 0.15 * inst
        if not ws_clients:
            continue
        text = json.dumps(STATE.snapshot(CONFIG.pole_pairs, fps))
        for ws in list(ws_clients):
            try:
                await ws.send_text(text)
            except Exception:
                ws_clients.discard(ws)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = threading.Event()
    target = mock_generator if CONFIG.mock else can_reader
    reader = threading.Thread(target=target, args=(CONFIG, STATE, stop), daemon=True)
    reader.start()
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
    p.add_argument("--port", help="SLCAN seri portu (varsayılan: otomatik bul)")
    p.add_argument("--bitrate", type=int, default=500_000, help="CAN bitrate (varsayılan 500000)")
    p.add_argument("--pole-pairs", type=int, default=7,
                   help="motor kutup çifti sayısı, RPM = ERPM / pole_pairs (varsayılan 7)")
    p.add_argument("--host", default="127.0.0.1", help="HTTP host (varsayılan 127.0.0.1)")
    p.add_argument("--http-port", type=int, default=8000, help="HTTP port (varsayılan 8000)")
    a = p.parse_args()
    return Config(mock=a.mock, port=a.port, bitrate=a.bitrate,
                  pole_pairs=a.pole_pairs, host=a.host, http_port=a.http_port)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    global CONFIG
    CONFIG = parse_args()

    if not CONFIG.mock and CONFIG.port is None:
        ports = find_ports()
        if len(ports) > 1:
            CONFIG.port = choose_port_interactive(ports)
        elif len(ports) == 1:
            CONFIG.port = ports[0]
        else:
            log.warning("SLCAN portu bulunamadı (%s) — takılınca otomatik bağlanılacak",
                        " | ".join(PORT_GLOBS))

    log.info("Dashboard: http://localhost:%d  (%s)", CONFIG.http_port,
             "mock veri" if CONFIG.mock else f"port={CONFIG.port or 'aranıyor'}")
    uvicorn.run(app, host=CONFIG.host, port=CONFIG.http_port, log_level="warning")


if __name__ == "__main__":
    main()
