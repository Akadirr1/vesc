# Graph Report - .  (2026-09-01)

## Corpus Check
- Corpus is ~24,565 words - fits in a single context window. You may not need a graph.

## Summary
- 774 nodes · 1762 edges · 36 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output
- Edge kinds: calls: 976 · method: 457 · contains: 282 · rationale_for: 21 · ON_BRANCH: 16 · PARENT_OF: 8 · MODIFIES: 2


## Input Scope
- Requested: auto
- Resolved: committed (source: default-auto)
- Included files: 10 · Candidates: 18
- Excluded: 1 untracked · 24284 ignored · 0 sensitive · 0 missing committed
- Recommendation: Use --scope all or graphify.yaml inputs.corpus for a knowledge-base folder.

## Graph Freshness
- Built from Git commit: `a71568b`
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
- `aa()` --calls--> `l()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 23 → community 5_
- `aa()` --calls--> `o()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 23 → community 8_
- `aa()` --calls--> `s()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 23 → community 4_
- `ao()` --calls--> `Re()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 18 → community 14_
- `at()` --calls--> `a()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 19 → community 23_

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (7): an(), jn, ke(), Mn(), onClick(), u(), wn()

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (7): Ae(), d(), Ie(), js(), Xs(), Y(), ze()

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (47): broadcaster(), build_fault_poll_frame(), BusHolder, can_reader(), choose_port_interactive(), Config, fault_poller(), find_ports() (+39 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (17): addBox(), afterDraw(), afterUpdate(), b(), ba, f(), gs(), ki() (+9 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (16): Be(), ca(), Do(), eo(), fa(), ga(), ha, ia() (+8 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (13): En, Fo(), _generate(), _getTimestampsForTable(), Gn(), In(), l(), lt() (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (14): Bt(), Ft(), Gt(), It(), jt(), kt(), mt(), qt() (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (12): beforeLayout(), buildLookupTable(), destroy(), initOffsets(), je(), Jo(), ln(), qo() (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (14): bn(), cn(), dn(), fe(), ks(), mi(), nn(), o() (+6 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (4): addElements(), qs(), tn, w()

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (2): As(), ns()

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (12): ct(), e(), ei(), fs(), ge(), ms(), pe(), we() (+4 more)

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (13): ai(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), da(), ea(), getRange(), hi() (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.20
Nodes (2): Cs, os()

### Community 14 - "Community 14"
Cohesion: 0.24
Nodes (12): dataset(), getCenterPoint(), _i(), index(), inRange(), ji(), nearest(), Re() (+4 more)

### Community 15 - "Community 15"
Cohesion: 0.15
Nodes (10): buildTicks(), Fn(), go(), init(), parse(), parseArrayData(), parseObjectData(), parsePrimitiveData() (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.44
Nodes (11): claude/graphifyy-claude-setup-msp1t3, claude/v2-usbcan-mavlink-uplink, main, 0a104b1 Add VESC CAN telemetry dashboard (FastAPI + WebSocket + Chart.js), 0b6ee5f Add graphify knowledge graph artifacts for the dashboard code, 40097c9 Ignore graphify local lifecycle files, 4f16a56 Harden serial/parse layer per FW 5.02 + ArduPilot source audit, 529351d Initial commit (+3 more)

### Community 17 - "Community 17"
Cohesion: 0.20
Nodes (8): es(), generateLabels(), is(), pt(), Qi(), ss(), ts(), update()

### Community 18 - "Community 18"
Cohesion: 0.25
Nodes (8): ao(), ho(), Hs, inXRange(), inYRange(), lo(), oo(), ro()

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (3): at(), rt(), zs()

### Community 20 - "Community 20"
Cohesion: 0.25
Nodes (3): _calculateBarValuePixels(), getPixelForValue(), updateElements()

### Community 21 - "Community 21"
Cohesion: 0.20
Nodes (3): H(), mo(), xo

### Community 22 - "Community 22"
Cohesion: 0.31
Nodes (3): ce(), de, he()

### Community 23 - "Community 23"
Cohesion: 0.28
Nodes (6): a(), aa(), afterDatasetsUpdate(), determineDataLimits(), Di(), oa()

### Community 24 - "Community 24"
Cohesion: 0.31
Nodes (7): _calculateBarIndexPixels(), getLabelAndValue(), _getRuler(), _getStackCount(), _getStackIndex(), _getStacks(), resolveDataElementOptions()

### Community 25 - "Community 25"
Cohesion: 0.22
Nodes (1): rs

### Community 26 - "Community 26"
Cohesion: 0.25
Nodes (3): bo, et(), getValueForPixel()

### Community 27 - "Community 27"
Cohesion: 0.25
Nodes (8): draw(), Ee(), getMaxOverflow(), kn(), Le(), qn(), size(), uo()

### Community 28 - "Community 28"
Cohesion: 0.29
Nodes (6): gi(), m(), pi(), r(), ri(), v()

### Community 29 - "Community 29"
Cohesion: 0.29
Nodes (1): initialize()

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (2): j(), ko

### Community 32 - "Community 32"
Cohesion: 0.40
Nodes (1): Ci()

### Community 33 - "Community 33"
Cohesion: 0.50
Nodes (3): Bi(), Fi(), zi()

### Community 34 - "Community 34"
Cohesion: 0.50
Nodes (2): dt(), pa()

### Community 35 - "Community 35"
Cohesion: 0.67
Nodes (1): g()

### Community 36 - "Community 36"
Cohesion: 0.67
Nodes (1): ls

## Knowledge Gaps
- **21 isolated node(s):** `Latest telemetry per VESC + bus status, shared between the CAN reader     thread`, `(arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can`, `Parse one extended frame; returns True if it was an accepted VESC frame.      Th`, `Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube`, `Shares the live can.Bus between the reader thread (owner) and the     fault poll` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (2 nodes): `As()`, `ns()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (2 nodes): `Cs`, `os()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `rs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `initialize()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `j()`, `ko`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Ci()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (2 nodes): `dt()`, `pa()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `g()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `ls`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `js()` connect `Community 1` to `Community 7`, `Community 11`, `Community 3`, `Community 4`, `Community 32`, `Community 26`, `Community 15`, `Community 17`, `Community 20`, `Community 23`, `Community 21`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `ns()` connect `Community 10` to `Community 7`, `Community 19`, `Community 20`, `Community 8`, `Community 5`, `Community 32`, `Community 29`, `Community 24`, `Community 35`, `Community 30`, `Community 15`, `Community 17`, `Community 0`, `Community 13`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `an()` connect `Community 0` to `Community 7`, `Community 4`, `Community 8`, `Community 1`, `Community 32`, `Community 17`, `Community 12`, `Community 10`, `Community 14`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **What connects `Latest telemetry per VESC + bus status, shared between the CAN reader     thread`, `(arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can`, `Parse one extended frame; returns True if it was an accepted VESC frame.      Th` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06018018018018018 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05472636815920398 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.05310734463276836 - nodes in this community are weakly interconnected._