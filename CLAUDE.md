# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`vesc` is a VESC CAN telemetry dashboard: a Python 3.11+ FastAPI backend (`backend/main.py`) that reads VESC status frames from an SLCAN adapter (ArduPilot SLCAN passthrough on a Cube Orange) and pushes state to a single-page dark-theme UI (`backend/static/index.html`, vanilla JS + vendored Chart.js, no build step) over a WebSocket at 10 Hz.

Architecture (all in `backend/main.py`): a CAN reader thread (or `--mock` generator thread) parses VESC status frames (extended ID = `(command_id << 8) | vesc_id`, big-endian) into a lock-protected `TelemetryState`; an asyncio broadcaster task snapshots it at 10 Hz and fans out to `/ws` clients. VESC ids come from `--vesc-ids` (default 21–24, the owner's ESCs); everything else on the bus is ignored, but status frames from unlisted ids are counted as `unknown_ids` and surfaced in the UI so a wrong id list is obvious. The frame layouts are verified against the VESC firmware source at tag 5.02 and documented with source citations in `docs/CAN_PROTOCOL_FW52.md` — consult it before changing any parser, and never re-introduce "STATUS_6 = command 28" (28 is an encoder poll on every firmware; STATUS_6 is command 58, FW 6.00+, behind `--fw 6.0`). Compare the command id as the full `arbitration_id >> 8`, never masked to 8 bits — the firmware does the same, and the bus also carries ArduPilot DroneCAN frames. Fault codes are not broadcast: a poller thread requests them at ~1 Hz per *online* VESC via `PROCESS_SHORT_BUFFER` + `COMM_GET_VALUES_SELECTIVE` (fault-only mask). A motor temp ≤ −50 °C means no motor NTC (sensorless motors) and is reported as null.

v2 (sea deployment): `--can-interface socketcan --channel can0` reads a USB-CAN adapter directly on the companion computer (no Cube passthrough); `backend/uplink.py` pushes `HEARTBEAT` + `ESC_TELEMETRY_1_TO_4` + a compact `TUNNEL` snapshot over MAVLink (`--mavlink-out`, ~1.4 kbit/s at 1 Hz) to the Cube's TELEM2, which ArduPilot routes to the shore GCS; on shore `--mavlink-in udpin:…` rebuilds `TelemetryState` from that stream so the same UI works. The TUNNEL payload layout is specified in `docs/CAN_PROTOCOL_FW52.md` §9 — bump `TUNNEL_VERSION` if you change it. `--can-interface mavlink` (`backend/mavcan.py`) reads the bus through ArduPilot's MAVLink CAN forwarding (`MAV_CMD_CAN_FORWARD`, 1 Hz keepalive, `CAN_FRAME` id masked with `0x1FFFFFFF`, TX bus 0-based) — the only persistent Cube path that keeps working while armed (per-boot `CAN_SLCAN_SERNUM` is the temporary alternative); facts and citations in §10. `--mavlink-out same` makes the uplink share that connection (writes serialised by `MavlinkCanBus.lock`).

Serial layer (v1 path): the Cube Orange exposes two USB CDC ports (SERIAL0 MAVLink, SERIAL6 SLCAN); `can_reader` probes candidates and keeps the first one that yields a VESC frame within 3 s (`run_bus`). Inside the recv loop, `ValueError/IndexError/KeyError` from python-can mean a corrupted SLCAN line and are skipped; only serial/CAN errors trigger reconnect. ArduPilot-side behaviour (SERNUM resets at boot, SERIALn_PROTOCOL=22 is the persistent path but auto-disables while armed, silent frame drops when the serial TX buffer fills) is documented in `docs/CAN_PROTOCOL_FW52.md` §8 — read that before touching connection logic or the README's SLCAN section. `npm`/`package.json` exist only for the graphify tooling below.

## Working discipline — graphify first, token budget second

The owner watches token usage closely. Follow these rules in every session:

1. **Orient with the graph, not with file reads.** For any "where/what/how" question about this codebase run `npx graphify summary --graph .graphify/graph.json` or `npx graphify query "<question>"` (pipe through `head -30`) before opening a file. Open a raw file only to edit it, and then only the line range you need (`Read` with `offset`/`limit`).
2. **Never re-read what is already in context.** After an `Edit`/`Write` the file state is known; do not `Read` it back to check.
3. **Cap command output.** Every Bash call that can print a lot goes through `head`/`tail`/`grep -n` with a line limit; never `cat` a whole file or dump a full log.
4. **Firmware and ArduPilot facts live in `docs/CAN_PROTOCOL_FW52.md`.** Cite from there instead of re-cloning or re-grepping `vedderb/bldc` / ArduPilot. If a new fact is needed, fetch a single raw file, extract with `grep -n`/`sed -n 'a,bp'`, and record the finding (file:line) in that document so it is never looked up twice.
5. **One pass per file.** Batch all edits to a file into one turn; run tests once after the batch, not after every edit.
6. **Keep the graph current.** After code changes run `npx graphify hook-rebuild` (AST only, no LLM) and commit the portable artifacts per the rules below.
7. **Report compactly.** Findings and plans go to the user as short structured text; put long-form research into `docs/`, not into chat.

## Commands

```bash
pip install -r requirements.txt     # Python deps (python-can, FastAPI, uvicorn)
python backend/main.py --mock       # run the dashboard with fake data (no hardware)
python backend/main.py              # real SLCAN bus (auto-detects /dev/tty.usbmodem*)
python backend/main.py --can-interface mavlink --port /dev/cu.usbmodemXXXX1 [--mavlink-out same]  # Cube MAVLink port, works armed
python backend/main.py --can-interface socketcan --channel can0 --mavlink-out /dev/ttyAMA0:115200   # vessel (v2)
python backend/main.py --mavlink-in udpin:0.0.0.0:14551                                            # shore (v2)
npm install                         # graphify tooling only
npx graphify --version              # verify the graphify CLI
```

The dashboard serves on http://localhost:8000. There are no lint or test scripts defined yet; when they are added, document them here. Chart.js is vendored at `backend/static/chart.umd.min.js` — the UI must keep working offline, so don't replace it with a CDN reference.

## Claude Code integration

This repository is set up with the graphify skill and hooks (project-scoped, committed to version control):

- `.claude/skills/graphify/SKILL.md` — the `/graphify` skill: builds a queryable knowledge graph of the codebase into `.graphify/`.
- `.claude/settings.json` — PreToolUse hooks that remind Claude to query the knowledge graph (once `.graphify/graph.json` exists) instead of grepping or reading raw files one by one.
- Run `/graphify .` to build or rebuild the graph once there is source code to index.

## graphify

This project has a graphify knowledge graph at .graphify/.

Rules:
- For codebase or architecture questions, when `.graphify/graph.json` exists, first run `graphify query "<question>"` (or `graphify path "<A>" "<B>"` / `graphify explain "<concept>"`); these return a scoped subgraph, usually much smaller than `GRAPH_REPORT.md` or raw grep output
- If .graphify/wiki/index.md exists, navigate it instead of reading raw files
- If .graphify/graph.json is missing but graphify-out/graph.json exists, run `graphify migrate-state --dry-run` first; if tracked legacy artifacts are reported, ask before using the recommended `git mv -f graphify-out .graphify` and commit message
- If .graphify/needs_update exists or .graphify/branch.json has stale=true, warn before relying on semantic results and run /graphify . --update when appropriate
- Before proposing or committing .graphify artifacts, run `graphify portable-check .graphify`; commit-safe graph artifacts must use repo-relative paths, and never commit .graphify/branch.json, .graphify/worktree.json, .graphify/needs_update, or .graphify/cache/. If a repo already tracks any of them, first add them to .gitignore, then propose `git rm --cached .graphify/branch.json .graphify/worktree.json .graphify/needs_update` and `git rm -r --cached .graphify/cache`; never mutate git state without asking
- Before deep graph traversal, prefer `graphify summary --graph .graphify/graph.json` for compact first-hop orientation
- For review impact on changed files, use `graphify review-delta --graph .graphify/graph.json` instead of generic traversal
- Read `.graphify/GRAPH_REPORT.md` only for broad architecture review or when `query` / `path` / `explain` do not surface enough context
- After modifying code files in this session, run `npx graphify hook-rebuild` to keep the graph current
