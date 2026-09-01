# Graph Report - .  (2026-09-01)

## Corpus Check
- Corpus is ~23,170 words - fits in a single context window. You may not need a graph.

## Summary
- 764 nodes · 1742 edges · 40 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output
- Edge kinds: calls: 976 · method: 457 · contains: 282 · rationale_for: 14 · ON_BRANCH: 7 · PARENT_OF: 5 · MODIFIES: 1


## Input Scope
- Requested: auto
- Resolved: committed (source: default-auto)
- Included files: 10 · Candidates: 18
- Excluded: 0 untracked · 24282 ignored · 0 sensitive · 0 missing committed
- Recommendation: Use --scope all or graphify.yaml inputs.corpus for a knowledge-base folder.

## Graph Freshness
- Built from Git commit: `6574004`
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
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 24 → community 36_
- `aa()` --calls--> `o()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 24 → community 5_
- `aa()` --calls--> `s()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 24 → community 23_
- `ao()` --calls--> `Re()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 18 → community 15_
- `at()` --calls--> `a()`  [EXTRACTED]
  backend/static/chart.umd.min.js → backend/static/chart.umd.min.js  _Bridges community 19 → community 24_

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
Nodes (40): broadcaster(), build_fault_poll_frame(), BusHolder, can_reader(), choose_port_interactive(), Config, fault_poller(), find_ports() (+32 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (14): Bt(), Ft(), Gt(), It(), jt(), kt(), mt(), qt() (+6 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (15): As(), bn(), cn(), dn(), fe(), ks(), mi(), nn() (+7 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (10): En, Fo(), _generate(), _getTimestampsForTable(), In(), lt(), no, nt() (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (12): beforeLayout(), buildLookupTable(), destroy(), initOffsets(), je(), Jo(), ln(), qo() (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (4): addElements(), qs(), tn, w()

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (3): Do(), eo(), Oe()

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (1): ns()

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (12): ct(), e(), ei(), fs(), ge(), ms(), pe(), we() (+4 more)

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (13): ai(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), da(), ea(), getRange(), hi() (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.17
Nodes (3): Be(), n(), ne()

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (2): Cs, os()

### Community 15 - "Community 15"
Cohesion: 0.24
Nodes (12): dataset(), getCenterPoint(), _i(), index(), inRange(), ji(), nearest(), Re() (+4 more)

### Community 16 - "Community 16"
Cohesion: 0.17
Nodes (11): Fn(), gi(), m(), parseArrayData(), parseObjectData(), parsePrimitiveData(), pi(), r() (+3 more)

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
Cohesion: 0.25
Nodes (7): fa(), ga(), ia(), la(), ra(), s(), ta()

### Community 24 - "Community 24"
Cohesion: 0.28
Nodes (6): a(), aa(), afterDatasetsUpdate(), determineDataLimits(), Di(), oa()

### Community 25 - "Community 25"
Cohesion: 0.31
Nodes (7): _calculateBarIndexPixels(), getLabelAndValue(), _getRuler(), _getStackCount(), _getStackIndex(), _getStacks(), resolveDataElementOptions()

### Community 26 - "Community 26"
Cohesion: 0.22
Nodes (3): ca(), ha, sa()

### Community 27 - "Community 27"
Cohesion: 0.22
Nodes (1): rs

### Community 28 - "Community 28"
Cohesion: 0.43
Nodes (8): claude/graphifyy-claude-setup-msp1t3, main, 0a104b1 Add VESC CAN telemetry dashboard (FastAPI + WebSocket + Chart.js), 0b6ee5f Add graphify knowledge graph artifacts for the dashboard code, 40097c9 Ignore graphify local lifecycle files, 529351d Initial commit, 6574004 Verify CAN parsing against VESC FW 5.02 source; add fault polling, e0c859f Add graphify (@sentropic/graphify) with Claude Code setup and CLAUDE.md

### Community 29 - "Community 29"
Cohesion: 0.25
Nodes (3): bo, et(), getValueForPixel()

### Community 30 - "Community 30"
Cohesion: 0.25
Nodes (5): buildTicks(), go(), init(), parse(), po()

### Community 31 - "Community 31"
Cohesion: 0.25
Nodes (8): draw(), Ee(), getMaxOverflow(), kn(), Le(), qn(), size(), uo()

### Community 32 - "Community 32"
Cohesion: 0.29
Nodes (1): initialize()

### Community 34 - "Community 34"
Cohesion: 0.33
Nodes (2): j(), ko

### Community 35 - "Community 35"
Cohesion: 0.40
Nodes (1): Ci()

### Community 36 - "Community 36"
Cohesion: 0.50
Nodes (3): Gn(), l(), so()

### Community 37 - "Community 37"
Cohesion: 0.50
Nodes (3): Bi(), Fi(), zi()

### Community 38 - "Community 38"
Cohesion: 0.50
Nodes (2): dt(), pa()

### Community 39 - "Community 39"
Cohesion: 0.67
Nodes (1): g()

### Community 40 - "Community 40"
Cohesion: 0.67
Nodes (1): ls

## Knowledge Gaps
- **14 isolated node(s):** `Latest telemetry per VESC + bus status, shared between the CAN reader     thread`, `(arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can`, `Parse one extended frame; returns True if it was an accepted VESC frame.      Th`, `Candidate serial ports, cu.* preferred over its tty.* twin on macOS.     A Cube`, `Shares the live can.Bus between the reader thread (owner) and the     fault poll` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (1 nodes): `ns()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `Cs`, `os()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `rs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `initialize()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (2 nodes): `j()`, `ko`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Ci()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `dt()`, `pa()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `g()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `ls`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `js()` connect `Community 1` to `Community 7`, `Community 11`, `Community 2`, `Community 26`, `Community 35`, `Community 29`, `Community 30`, `Community 17`, `Community 20`, `Community 24`, `Community 21`, `Community 13`, `Community 23`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `ns()` connect `Community 10` to `Community 7`, `Community 19`, `Community 20`, `Community 5`, `Community 6`, `Community 35`, `Community 32`, `Community 25`, `Community 39`, `Community 33`, `Community 30`, `Community 17`, `Community 0`, `Community 14`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `an()` connect `Community 0` to `Community 7`, `Community 23`, `Community 5`, `Community 1`, `Community 35`, `Community 13`, `Community 17`, `Community 12`, `Community 10`, `Community 15`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **What connects `Latest telemetry per VESC + bus status, shared between the CAN reader     thread`, `(arbitration_id, data) asking `target_vesc_id` for its fault code.      comm_can`, `Parse one extended frame; returns True if it was an accepted VESC frame.      Th` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06018018018018018 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05472636815920398 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.06327683615819209 - nodes in this community are weakly interconnected._