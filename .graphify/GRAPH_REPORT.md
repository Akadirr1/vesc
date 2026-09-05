# Graph Report - .  (2026-09-05)

## Corpus Check
- Corpus is ~28,790 words - fits in a single context window. You may not need a graph.

## Summary
- 846 nodes · 1929 edges · 44 communities detected
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output
- Edge kinds: calls: 995 · method: 471 · contains: 291 · rationale_for: 61 · uses: 58 · ON_BRANCH: 33 · PARENT_OF: 17 · MODIFIES: 2 · imports_from: 1


## Input Scope
- Requested: auto
- Resolved: committed (source: default-auto)
- Included files: 12 · Candidates: 20
- Excluded: 0 untracked · 24291 ignored · 0 sensitive · 0 missing committed
- Recommendation: Use --scope all or graphify.yaml inputs.corpus for a knowledge-base folder.

## Graph Freshness
- Built from Git commit: `0906f23`
- Compare this hash to `git rev-parse HEAD` before trusting freshness-sensitive graph output.
## God Nodes (most connected - your core abstractions)
1. `js()` - 72 edges
2. `an()` - 61 edges
3. `ns()` - 55 edges
4. `n()` - 39 edges
5. `no` - 34 edges
6. `s()` - 33 edges
7. `MavlinkDownlink` - 31 edges
8. `MavlinkUplink` - 30 edges
9. `o()` - 29 edges
10. `a()` - 29 edges

## Surprising Connections (you probably didn't know these)
- `BusHolder` --uses--> `MavlinkCanBus`  [INFERRED]
  backend/main.py → backend/mavcan.py
- `BusHolder` --uses--> `MavlinkDownlink`  [INFERRED]
  backend/main.py → backend/uplink.py
- `BusHolder` --uses--> `MavlinkUplink`  [INFERRED]
  backend/main.py → backend/uplink.py
- `Config` --uses--> `MavlinkCanBus`  [INFERRED]
  backend/main.py → backend/mavcan.py
- `Config` --uses--> `MavlinkDownlink`  [INFERRED]
  backend/main.py → backend/uplink.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (7): an(), jn, ke(), Mn(), onClick(), u(), wn()

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (7): Ae(), d(), Ie(), js(), Xs(), Y(), ze()

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (17): addBox(), afterDraw(), afterUpdate(), b(), ba, f(), gs(), ki() (+9 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (16): Be(), ca(), Do(), eo(), fa(), ga(), ha, ia() (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (13): En, Fo(), _generate(), _getTimestampsForTable(), Gn(), In(), l(), lt() (+5 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (14): Bt(), Ft(), Gt(), It(), jt(), kt(), mt(), qt() (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (12): beforeLayout(), buildLookupTable(), destroy(), initOffsets(), je(), Jo(), ln(), qo() (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (14): bn(), cn(), dn(), fe(), ks(), mi(), nn(), o() (+6 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (4): addElements(), qs(), tn, w()

### Community 9 - "Community 9"
Cohesion: 0.13
Nodes (18): can_reader(), handle_frame(), mock_generator(), Parse one extended frame; returns True if it was an accepted VESC frame.      Th, Parse one extended frame; returns True if it was an accepted VESC frame.      Th, Parse one extended frame; returns True if it was an accepted VESC frame.      Th, Parse one extended frame; returns True if it was an accepted VESC frame.      Th, Parse one extended frame; returns True if it was an accepted VESC frame.      Th (+10 more)

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (2): As(), ns()

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (16): _clamp(), _num(), open_connection(), pack_esc_telemetry(), pack_tunnel(), MAVLink uplink / downlink for the sea deployment (v2).  Vessel side (--mavlink-o, Field lists for ESC_TELEMETRY_1_TO_4 (first four VESC ids).     rpm is the mecha, spec: 'udpout:host:port' | 'udpin:host:port' | 'tcp:host:port' |     '/dev/ttyXX (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.29
Nodes (19): claude/graphifyy-claude-setup-msp1t3, claude/ui-standstill-noise, claude/v2-usbcan-mavlink-uplink, main, 0906f23 Add MAVLink CAN forwarding transport (works while armed), 0a104b1 Add VESC CAN telemetry dashboard (FastAPI + WebSocket + Chart.js), 0b6ee5f Add graphify knowledge graph artifacts for the dashboard code, 40097c9 Ignore graphify local lifecycle files (+11 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (12): ct(), e(), ei(), fs(), ge(), ms(), pe(), we() (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (13): choose_port_interactive(), Config, _i16(), _i32(), main(), parse_args(), _parse_status(), _parse_status_2() (+5 more)

### Community 15 - "Community 15"
Cohesion: 0.15
Nodes (13): ai(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), da(), ea(), getRange(), hi() (+5 more)

### Community 16 - "Community 16"
Cohesion: 0.20
Nodes (2): Cs, os()

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (10): broadcaster(), fault_poller(), lifespan(), Asks each VESC for its fault code roughly once a second (staggered).     Faults, Asks each online VESC for its fault code roughly once a second     (staggered)., Asks each online VESC for its fault code roughly once a second     (staggered)., Asks each online VESC for its fault code roughly once a second     (staggered)., Asks each online VESC for its fault code roughly once a second     (staggered). (+2 more)

### Community 18 - "Community 18"
Cohesion: 0.19
Nodes (11): Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, TelemetryState (+3 more)

### Community 19 - "Community 19"
Cohesion: 0.24
Nodes (12): dataset(), getCenterPoint(), _i(), index(), inRange(), ji(), nearest(), Re() (+4 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (10): buildTicks(), Fn(), go(), init(), parse(), parseArrayData(), parseObjectData(), parsePrimitiveData() (+2 more)

### Community 21 - "Community 21"
Cohesion: 0.20
Nodes (5): MavlinkCanBus, CAN access through ArduPilot's MAVLink CAN forwarding (MAV_CMD_CAN_FORWARD).  Wh, Transmit a frame on the bus via CAN_FRAME (bus 0-based, EFF in bit 31)., python-can-like bus (recv / send / shutdown) over MAVLink CAN forwarding.      D, Next CAN frame as a can.Message, or None on timeout / non-frame traffic.

### Community 22 - "Community 22"
Cohesion: 0.20
Nodes (8): es(), generateLabels(), is(), pt(), Qi(), ss(), ts(), update()

### Community 23 - "Community 23"
Cohesion: 0.25
Nodes (8): ao(), ho(), Hs, inXRange(), inYRange(), lo(), oo(), ro()

### Community 24 - "Community 24"
Cohesion: 0.18
Nodes (3): at(), rt(), zs()

### Community 25 - "Community 25"
Cohesion: 0.25
Nodes (3): _calculateBarValuePixels(), getPixelForValue(), updateElements()

### Community 26 - "Community 26"
Cohesion: 0.20
Nodes (3): H(), mo(), xo

### Community 27 - "Community 27"
Cohesion: 0.31
Nodes (3): ce(), de, he()

### Community 28 - "Community 28"
Cohesion: 0.22
Nodes (9): find_ports(), Pick the serial port for (re)connecting. Called from the reader thread,     so i, Pick the serial port for (re)connecting. Called from the reader thread,     so i, Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube, Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube, Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube, Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube, Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.28
Nodes (6): a(), aa(), afterDatasetsUpdate(), determineDataLimits(), Di(), oa()

### Community 30 - "Community 30"
Cohesion: 0.31
Nodes (7): _calculateBarIndexPixels(), getLabelAndValue(), _getRuler(), _getStackCount(), _getStackIndex(), _getStacks(), resolveDataElementOptions()

### Community 31 - "Community 31"
Cohesion: 0.22
Nodes (1): rs

### Community 32 - "Community 32"
Cohesion: 0.25
Nodes (6): BusHolder, Shares the live can.Bus between the reader thread (owner) and the     fault poll, Shares the live can.Bus between the reader thread (owner) and the     fault poll, Shares the live can.Bus between the reader thread (owner) and the     fault poll, Shares the live can.Bus between the reader thread (owner) and the     fault poll, Shares the live can.Bus between the reader thread (owner) and the     fault poll

### Community 33 - "Community 33"
Cohesion: 0.25
Nodes (3): bo, et(), getValueForPixel()

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (8): draw(), Ee(), getMaxOverflow(), kn(), Le(), qn(), size(), uo()

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (7): build_fault_poll_frame(), (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (6): gi(), m(), pi(), r(), ri(), v()

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (1): initialize()

### Community 39 - "Community 39"
Cohesion: 0.33
Nodes (2): j(), ko

### Community 40 - "Community 40"
Cohesion: 0.40
Nodes (1): Ci()

### Community 41 - "Community 41"
Cohesion: 0.50
Nodes (3): Bi(), Fi(), zi()

### Community 42 - "Community 42"
Cohesion: 0.50
Nodes (2): dt(), pa()

### Community 43 - "Community 43"
Cohesion: 0.67
Nodes (1): g()

### Community 44 - "Community 44"
Cohesion: 0.67
Nodes (1): ls

## Knowledge Gaps
- **39 isolated node(s):** `CAN access through ArduPilot's MAVLink CAN forwarding (MAV_CMD_CAN_FORWARD).  Wh`, `python-can-like bus (recv / send / shutdown) over MAVLink CAN forwarding.      D`, `Next CAN frame as a can.Message, or None on timeout / non-frame traffic.`, `Transmit a frame on the bus via CAN_FRAME (bus 0-based, EFF in bit 31).`, `MAVLink uplink / downlink for the sea deployment (v2).  Vessel side (--mavlink-o` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (2 nodes): `As()`, `ns()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `Cs`, `os()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `rs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `initialize()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `j()`, `ko`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Ci()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (2 nodes): `dt()`, `pa()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `g()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `ls`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `js()` connect `Community 1` to `Community 6`, `Community 13`, `Community 2`, `Community 3`, `Community 40`, `Community 33`, `Community 20`, `Community 22`, `Community 25`, `Community 29`, `Community 26`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `ns()` connect `Community 10` to `Community 6`, `Community 24`, `Community 25`, `Community 7`, `Community 4`, `Community 40`, `Community 37`, `Community 30`, `Community 43`, `Community 38`, `Community 20`, `Community 22`, `Community 0`, `Community 16`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `an()` connect `Community 0` to `Community 6`, `Community 3`, `Community 7`, `Community 1`, `Community 40`, `Community 22`, `Community 15`, `Community 10`, `Community 19`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **What connects `CAN access through ArduPilot's MAVLink CAN forwarding (MAV_CMD_CAN_FORWARD).  Wh`, `python-can-like bus (recv / send / shutdown) over MAVLink CAN forwarding.      D`, `Next CAN frame as a can.Message, or None on timeout / non-frame traffic.` to the rest of the system?**
  _39 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06018018018018018 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05472636815920398 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.06327683615819209 - nodes in this community are weakly interconnected._