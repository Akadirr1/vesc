# Graph Report - .  (2026-09-05)

## Corpus Check
- Corpus is ~26,181 words - fits in a single context window. You may not need a graph.

## Summary
- 810 nodes · 1846 edges · 43 communities detected
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output
- Edge kinds: calls: 989 · method: 463 · contains: 290 · rationale_for: 36 · ON_BRANCH: 31 · uses: 20 · PARENT_OF: 15 · MODIFIES: 2


## Input Scope
- Requested: auto
- Resolved: committed (source: default-auto)
- Included files: 11 · Candidates: 19
- Excluded: 0 untracked · 24286 ignored · 0 sensitive · 0 missing committed
- Recommendation: Use --scope all or graphify.yaml inputs.corpus for a knowledge-base folder.

## Graph Freshness
- Built from Git commit: `95d76af`
- Compare this hash to `git rev-parse HEAD` before trusting freshness-sensitive graph output.
## God Nodes (most connected - your core abstractions)
1. `js()` - 72 edges
2. `an()` - 61 edges
3. `ns()` - 55 edges
4. `n()` - 39 edges
5. `no` - 34 edges
6. `s()` - 33 edges
7. `o()` - 29 edges
8. `a()` - 29 edges
9. `va` - 29 edges
10. `l()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `BusHolder` --uses--> `MavlinkDownlink`  [INFERRED]
  backend/main.py → backend/uplink.py
- `Config` --uses--> `MavlinkDownlink`  [INFERRED]
  backend/main.py → backend/uplink.py
- `Config` --uses--> `MavlinkUplink`  [INFERRED]
  backend/main.py → backend/uplink.py
- `Latest telemetry per VESC + bus status, shared between the CAN reader     thread` --uses--> `MavlinkDownlink`  [INFERRED]
  backend/main.py → backend/uplink.py
- `Latest telemetry per VESC + bus status, shared between the CAN reader     thread` --uses--> `MavlinkUplink`  [INFERRED]
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
Cohesion: 0.16
Nodes (16): broadcaster(), choose_port_interactive(), Config, _i16(), _i32(), lifespan(), main(), parse_args() (+8 more)

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (2): As(), ns()

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (12): ct(), e(), ei(), fs(), ge(), ms(), pe(), we() (+4 more)

### Community 12 - "Community 12"
Cohesion: 0.34
Nodes (17): claude/graphifyy-claude-setup-msp1t3, claude/ui-standstill-noise, claude/v2-usbcan-mavlink-uplink, main, 0a104b1 Add VESC CAN telemetry dashboard (FastAPI + WebSocket + Chart.js), 0b6ee5f Add graphify knowledge graph artifacts for the dashboard code, 40097c9 Ignore graphify local lifecycle files, 4f16a56 Harden serial/parse layer per FW 5.02 + ArduPilot source audit (+9 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (13): ai(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), da(), ea(), getRange(), hi() (+5 more)

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (2): Cs, os()

### Community 15 - "Community 15"
Cohesion: 0.24
Nodes (12): dataset(), getCenterPoint(), _i(), index(), inRange(), ji(), nearest(), Re() (+4 more)

### Community 16 - "Community 16"
Cohesion: 0.15
Nodes (10): buildTicks(), Fn(), go(), init(), parse(), parseArrayData(), parseObjectData(), parsePrimitiveData() (+2 more)

### Community 17 - "Community 17"
Cohesion: 0.21
Nodes (10): can_reader(), handle_frame(), mock_generator(), Parse one extended frame; returns True if it was an accepted VESC frame.      Th, Parse one extended frame; returns True if it was an accepted VESC frame.      Th, Parse one extended frame; returns True if it was an accepted VESC frame.      Th, Open `port` and pump frames until the bus fails or `stop` is set.      Returns T, Open `port` and pump frames until the bus fails or `stop` is set.      Returns T (+2 more)

### Community 18 - "Community 18"
Cohesion: 0.20
Nodes (8): es(), generateLabels(), is(), pt(), Qi(), ss(), ts(), update()

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (8): ao(), ho(), Hs, inXRange(), inYRange(), lo(), oo(), ro()

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (3): at(), rt(), zs()

### Community 21 - "Community 21"
Cohesion: 0.25
Nodes (3): _calculateBarValuePixels(), getPixelForValue(), updateElements()

### Community 22 - "Community 22"
Cohesion: 0.20
Nodes (3): H(), mo(), xo

### Community 23 - "Community 23"
Cohesion: 0.31
Nodes (9): _clamp(), _num(), open_connection(), pack_esc_telemetry(), pack_tunnel(), MAVLink uplink / downlink for the sea deployment (v2).  Vessel side (--mavlink-o, Field lists for ESC_TELEMETRY_1_TO_4 (first four VESC ids).     rpm is the mecha, spec: 'udpout:host:port' | 'udpin:host:port' | 'tcp:host:port' |     '/dev/ttyXX (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.20
Nodes (10): build_fault_poll_frame(), fault_poller(), (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, (arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can, Asks each VESC for its fault code roughly once a second (staggered).     Faults, Asks each online VESC for its fault code roughly once a second     (staggered). (+2 more)

### Community 25 - "Community 25"
Cohesion: 0.22
Nodes (6): Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, Latest telemetry per VESC + bus status, shared between the CAN reader     thread, TelemetryState

### Community 26 - "Community 26"
Cohesion: 0.22
Nodes (7): BusHolder, Shares the live can.Bus between the reader thread (owner) and the     fault poll, Shares the live can.Bus between the reader thread (owner) and the     fault poll, Shares the live can.Bus between the reader thread (owner) and the     fault poll, Shares the live can.Bus between the reader thread (owner) and the     fault poll, MavlinkUplink, Vessel side: periodically push the current snapshot over MAVLink.

### Community 27 - "Community 27"
Cohesion: 0.31
Nodes (3): ce(), de, he()

### Community 28 - "Community 28"
Cohesion: 0.28
Nodes (6): a(), aa(), afterDatasetsUpdate(), determineDataLimits(), Di(), oa()

### Community 29 - "Community 29"
Cohesion: 0.31
Nodes (7): _calculateBarIndexPixels(), getLabelAndValue(), _getRuler(), _getStackCount(), _getStackIndex(), _getStacks(), resolveDataElementOptions()

### Community 30 - "Community 30"
Cohesion: 0.22
Nodes (1): rs

### Community 31 - "Community 31"
Cohesion: 0.25
Nodes (3): bo, et(), getValueForPixel()

### Community 32 - "Community 32"
Cohesion: 0.25
Nodes (8): draw(), Ee(), getMaxOverflow(), kn(), Le(), qn(), size(), uo()

### Community 33 - "Community 33"
Cohesion: 0.29
Nodes (5): MavlinkDownlink, Shore side: rebuild the telemetry state from the MAVLink stream., Lossy fallback when only ESC_TELEMETRY_1_TO_4 arrives (e.g. another         send, Returns {vesc_id: fields}; fields use the same keys as TelemetryState,     plus, unpack_tunnel()

### Community 34 - "Community 34"
Cohesion: 0.29
Nodes (7): find_ports(), Pick the serial port for (re)connecting. Called from the reader thread,     so i, Pick the serial port for (re)connecting. Called from the reader thread,     so i, Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube, Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube, Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube, resolve_port()

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (6): gi(), m(), pi(), r(), ri(), v()

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (1): initialize()

### Community 38 - "Community 38"
Cohesion: 0.33
Nodes (2): j(), ko

### Community 39 - "Community 39"
Cohesion: 0.40
Nodes (1): Ci()

### Community 40 - "Community 40"
Cohesion: 0.50
Nodes (3): Bi(), Fi(), zi()

### Community 41 - "Community 41"
Cohesion: 0.50
Nodes (2): dt(), pa()

### Community 42 - "Community 42"
Cohesion: 0.67
Nodes (1): g()

### Community 43 - "Community 43"
Cohesion: 0.67
Nodes (1): ls

## Knowledge Gaps
- **29 isolated node(s):** `MAVLink uplink / downlink for the sea deployment (v2).  Vessel side (--mavlink-o`, ``vescs` is the "vescs" dict of a TelemetryState.snapshot().`, `Returns {vesc_id: fields}; fields use the same keys as TelemetryState,     plus`, `Field lists for ESC_TELEMETRY_1_TO_4 (first four VESC ids).     rpm is the mecha`, `spec: 'udpout:host:port' | 'udpin:host:port' | 'tcp:host:port' |     '/dev/ttyXX` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (2 nodes): `As()`, `ns()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `Cs`, `os()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `rs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `initialize()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `j()`, `ko`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Ci()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `dt()`, `pa()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `g()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `ls`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `js()` connect `Community 1` to `Community 6`, `Community 11`, `Community 2`, `Community 3`, `Community 39`, `Community 31`, `Community 16`, `Community 18`, `Community 21`, `Community 28`, `Community 22`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Why does `ns()` connect `Community 10` to `Community 6`, `Community 20`, `Community 21`, `Community 7`, `Community 4`, `Community 39`, `Community 36`, `Community 29`, `Community 42`, `Community 37`, `Community 16`, `Community 18`, `Community 0`, `Community 14`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `an()` connect `Community 0` to `Community 6`, `Community 3`, `Community 7`, `Community 1`, `Community 39`, `Community 18`, `Community 13`, `Community 10`, `Community 15`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **What connects `MAVLink uplink / downlink for the sea deployment (v2).  Vessel side (--mavlink-o`, ``vescs` is the "vescs" dict of a TelemetryState.snapshot().`, `Returns {vesc_id: fields}; fields use the same keys as TelemetryState,     plus` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06018018018018018 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05472636815920398 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.06327683615819209 - nodes in this community are weakly interconnected._