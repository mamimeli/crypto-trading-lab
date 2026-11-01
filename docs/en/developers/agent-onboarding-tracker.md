# Agent Onboarding Tracker

Status of the files and infrastructure that let AI agents (and humans)
start productive work in this repository without guessing. This tracker
is the single place to check whether the agent-onboarding surface is
complete and current; the files themselves remain the source of truth
for their content.

Last verified: 2026-10-31 (baseline updated to 1015 by the chapter 35 work).

## Core agent files

| File | Status | Purpose |
|---|---|---|
| [`AGENTS.md`](../../../AGENTS.md) | [x] done | Non-negotiable ground rules for any AI agent working in this repo |
| [`CLAUDE.md`](../../../CLAUDE.md) | [x] done | Auto-loaded by Claude Code and other agent tools at session start; points to the authoritative files |
| [`AGENT-HANDOFF.md`](../../../AGENT-HANDOFF.md) | [x] done | Current project state and the exact continuation point |
| [`ROADMAP.md`](../../../ROADMAP.md) | [x] done | The per-chapter specification (source of truth for tasks) |
| [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) | [x] done | Workflow, quality bar, review process, agent guidance |

## Onboarding reading lists (all include AGENTS.md)

Each list below is checked when it includes `AGENTS.md` and stays in sync
with the current test baseline.

- [x] `README.md` — "Read these five files" table (AGENTS.md is row 2)
- [x] `CONTRIBUTING.md` — five-minute orientation table (row 2)
- [x] `CLAUDE.md` — reading list (item 2)
- [x] `docs/en/developers/README.md` — developer docs index (item 2)
- [x] `docs/en/developers/working-method.md` — Documentation files list

## Agent prompt

- [x] `README.md` § "Paste this to your agent" — a copy-paste system
      prompt encoding the ground rules for agents whose tools do not
      auto-load `CLAUDE.md`.

## Supporting infrastructure

- [x] `docs/en/developers/small-context-contributing.md` — measured
      token costs and what to never load for small context windows
- [x] PR template (`.github/PULL_REQUEST_TEMPLATE.md`) — includes a
      checklist that requires real test output
- [x] Issue templates — bug report and roadmap-chapter task
- [x] CI: `tests.yml` (suite), `links-external.yml` (weekly URL check),
      `cross-platform.yml` (manual platform verification)

## Test baseline sync

The test baseline quoted across the agent files must match reality.
When the count changes, update it everywhere (this is what the
"stale baseline" check below is for).

- [x] Current baseline: **1015 passed, 2 skipped** (measured 2026-10-31 on
      Windows, Python 3.12; the Debian CI run at this count has not been
      observed yet — the last green run was 990/2)
- [x] `AGENTS.md` references the current baseline
- [x] `AGENT-HANDOFF.md` references the current baseline
- [x] `README.md` badge and inline references use the current baseline
- [x] `CONTRIBUTING.md` references the current baseline
- [x] `docs/en/developers/working-method.md` references the current baseline

## How to update this tracker

When you add or change an agent-onboarding file:

1. Tick or add the relevant row above.
2. Update the "Last verified" date.
3. If the test baseline changed, update the sync section and every file
   it lists.
4. Run `python3 tools/check_doc_links.py` — the links in this file
   must resolve.
