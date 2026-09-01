# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`vesc` is an early-stage Node.js project (Node.js >= 20 required). There is no application source code yet — the repository currently contains project scaffolding and the graphify knowledge-graph tooling described below.

## Commands

```bash
npm install                 # install dependencies (includes @sentropic/graphify)
npx graphify --version      # verify the graphify CLI
```

There are no build, lint, or test scripts defined yet. When they are added to `package.json`, document them here.

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
