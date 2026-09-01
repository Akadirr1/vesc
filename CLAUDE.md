# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`vesc` is a VESC CAN telemetry dashboard: a Python 3.11+ FastAPI backend (`backend/main.py`) that reads VESC status frames from an SLCAN adapter (ArduPilot SLCAN passthrough on a Cube Orange) and pushes state to a single-page dark-theme UI (`backend/static/index.html`, vanilla JS + vendored Chart.js, no build step) over a WebSocket at 10 Hz.

Architecture (all in `backend/main.py`): a CAN reader thread (or `--mock` generator thread) parses VESC status frames (extended ID = `(command_id << 8) | vesc_id`, big-endian) into a lock-protected `TelemetryState`; an asyncio broadcaster task snapshots it at 10 Hz and fans out to `/ws` clients. VESC IDs 0–3; everything else on the bus is ignored. The frame layouts are verified against the VESC firmware source at tag 5.02 and documented with source citations in `docs/CAN_PROTOCOL_FW52.md` — consult it before changing any parser, and never re-introduce "STATUS_6 = command 28" (28 is an encoder poll on every firmware; STATUS_6 is command 58, FW 6.00+, behind `--fw 6.0`). Fault codes are not broadcast: a poller thread requests them at ~1 Hz per VESC via `PROCESS_SHORT_BUFFER` + `COMM_GET_VALUES_SELECTIVE` (fault-only mask). A motor temp ≤ −50 °C means no motor NTC (sensorless motors) and is reported as null. `npm`/`package.json` exist only for the graphify tooling below.

## Commands

```bash
pip install -r requirements.txt     # Python deps (python-can, FastAPI, uvicorn)
python backend/main.py --mock       # run the dashboard with fake data (no hardware)
python backend/main.py              # real SLCAN bus (auto-detects /dev/tty.usbmodem*)
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
