"""CAN access through ArduPilot's MAVLink CAN forwarding (MAV_CMD_CAN_FORWARD).

Why this exists: the Cube's SLCAN passthrough is switched off by ArduPilot
while the vehicle is armed (AP_SLCANIface.cpp, update_slcan_port). MAVLink
CAN forwarding has no arming check, so the dashboard can keep reading the
VESC bus through the autopilot's MAVLink port (USB SERIAL0, or a router such
as MAVProxy) during a mission. Verified against ArduPilot master 371990d
(libraries/AP_CANManager/AP_MAVLinkCAN.cpp) and mavlink/common.xml; the
DroneCAN GUI Tool "mavcan" driver was used as the reference client.
Source citations: docs/CAN_PROTOCOL_FW52.md §10.

Protocol facts this module relies on:
  * MAV_CMD_CAN_FORWARD (32000): param1 = bus, 1-based (CAN1 -> 1); 0 stops.
    ArduPilot drops the registration 5 s after the last request (checked
    every 100 frames), so the request is repeated every FORWARD_PERIOD_S.
  * Frames arrive as CAN_FRAME (386) on the requesting channel only, gated by
    HAVE_PAYLOAD_SPACE — silently dropped when the link is saturated (watch
    the fps warning). `id` is the raw AP_HAL::CANFrame id: bit 31 = extended
    (FlagEFF), 0x1FFFFFFF masks the 29-bit id. `data` is always 8 ints; `len`
    gives the real length. Frames the autopilot transmits itself (DroneCAN)
    are forwarded too — the VESC parser ignores them.
  * TX: a CAN_FRAME sent to the autopilot is transmitted on the bus. There the
    bus field is 0-BASED (asymmetric with the command), extended ids need
    bit 31 set and data must be padded to 8 bytes.
  * Only one forwarding client at a time: Mission Planner's DroneCAN screen
    uses the same mechanism and would take the stream over while open.
  * MAVLink 2 is required (message id > 255); open_connection() forces it.
"""

import logging
import threading
import time

from uplink import open_connection  # also sets MAVLINK20=1 before pymavlink loads

log = logging.getLogger("vesc-dash.mavcan")

MAV_CMD_CAN_FORWARD = 32000
FLAG_EFF = 0x80000000      # AP_HAL::CANFrame::FlagEFF
MASK_EXT_ID = 0x1FFFFFFF   # AP_HAL::CANFrame::MaskExtID
FORWARD_PERIOD_S = 1.0     # ArduPilot expires forwarding after 5 s; mavcan uses 1 s
MAV_RESULT_ACCEPTED = 0
REJECT_LOG_EVERY_S = 60.0  # probing recreates the bus every few seconds; do not spam
_last_reject_log = 0.0


class MavlinkCanBus:
    """python-can-like bus (recv / send / shutdown) over MAVLink CAN forwarding.

    Duck-types the parts of can.BusABC that run_bus() and fault_poller() use,
    so the rest of the dashboard does not care which transport is active.
    All writes on the pymavlink connection go through `self.lock`, which the
    telemetry uplink shares when started with --mavlink-out same.
    """

    def __init__(self, spec: str, bus_index: int, sysid: int, compid: int,
                 forward_period: float = FORWARD_PERIOD_S):
        import can  # python-can Message type only

        self._can = can
        self.conn = open_connection(spec, sysid, compid)
        self.lock = threading.Lock()
        self.bus_index = bus_index
        self.period = forward_period
        self._last_enable = 0.0
        self.frames_rx = 0
        self.acks = 0
        # Autopilot address, learned from the first message it sends us. Until
        # then 0/0 (processed locally, but ArduPilot also forwards broadcasts to
        # every other link — e.g. the telemetry radio — so we stop using it asap).
        self.target = (0, 0)
        self.note = None  # human-readable transport problem for the UI, or None

    def _keepalive(self, now: float) -> None:
        if now - self._last_enable < self.period:
            return
        # Before the autopilot's address is learned this goes out as 0/0, which
        # ArduPilot processes locally (MAVLink_routing.cpp) but also forwards.
        with self.lock:
            self.conn.mav.command_long_send(*self.target, MAV_CMD_CAN_FORWARD, 0,
                                            float(self.bus_index), 0, 0, 0, 0, 0, 0)
        self._last_enable = now

    def _learn_target(self, msg) -> None:
        if self.target == (0, 0):
            self.target = (msg.get_srcSystem(), msg.get_srcComponent())

    def recv(self, timeout: float = 0.5):
        """Next CAN frame as a can.Message, or None on timeout / non-frame traffic."""
        self._keepalive(time.time())
        msg = self.conn.recv_match(type=["CAN_FRAME", "CANFD_FRAME", "COMMAND_ACK"],
                                   blocking=True, timeout=timeout)
        if msg is None:
            return None
        mtype = msg.get_type()
        if mtype != "COMMAND_ACK" or msg.command == MAV_CMD_CAN_FORWARD:
            self._learn_target(msg)  # only from the autopilot's own CAN traffic / our ack
        if mtype == "COMMAND_ACK":
            if msg.command == MAV_CMD_CAN_FORWARD:
                self.acks += 1
                if msg.result == MAV_RESULT_ACCEPTED:
                    self.note = None
                else:
                    self.note = (f"MAV_CMD_CAN_FORWARD reddedildi (result={msg.result}) — "
                                 f"CAN_P{self.bus_index}_DRIVER=1 ve reboot?")
                    global _last_reject_log
                    now = time.time()
                    if now - _last_reject_log > REJECT_LOG_EVERY_S:
                        _last_reject_log = now
                        log.warning("ArduPilot %s", self.note)
            return None
        raw = int(msg.id)
        length = min(int(msg.len), len(msg.data))
        self.frames_rx += 1
        return self._can.Message(
            arbitration_id=raw & MASK_EXT_ID,
            is_extended_id=bool(raw & FLAG_EFF),
            is_fd=(mtype == "CANFD_FRAME"),
            dlc=length,
            data=bytes(msg.data[:length]),
        )

    def send(self, msg) -> None:
        """Transmit a frame on the bus via CAN_FRAME (bus 0-based, EFF in bit 31)."""
        data = bytes(msg.data)
        can_id = msg.arbitration_id | (FLAG_EFF if msg.is_extended_id else 0)
        padded = data[:8].ljust(8, b"\0")
        with self.lock:
            self.conn.mav.can_frame_send(*self.target, self.bus_index - 1, len(data[:8]), can_id, list(padded))

    def shutdown(self) -> None:
        try:
            with self.lock:  # param1 = 0: stop forwarding (best effort)
                self.conn.mav.command_long_send(*self.target, MAV_CMD_CAN_FORWARD, 0, 0, 0, 0, 0, 0, 0, 0)
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass
