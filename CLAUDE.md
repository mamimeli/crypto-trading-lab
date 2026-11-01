# CLAUDE.md

> This file is loaded automatically by Claude Code and other agent tools
> at session start. It points to the authoritative rules — it does not
> duplicate them, so there is one source of truth.

## Read these before touching anything (in order)

1. **`AGENT-HANDOFF.md`** — current state of the project and the exact
   continuation point.
2. **`AGENTS.md`** — the non-negotiable ground rules.
3. **`ROADMAP.md`** — **the specification.** Find the chapter that owns
   your task; do not start before reading it.
4. **`CONTRIBUTING.md`** — workflow, quality bar, and review process.

## Quick reference (read the full files above for the complete rules)

- **ROADMAP.md is the specification.** Never replace, simplify,
  reinterpret, or silently omit its requirements. If something is
  ambiguous, stop and say so instead of guessing.
- **Dependency STOP rule.** Do not run `apt`, `pip`, or create a venv
  yourself. If a dependency is needed, STOP and report: package name,
  source (Debian or PyPI), reason, and the exact command for the human.
- **Test after every change:**
  ```bash
  QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q
  ```
  Baseline: **1182 passed, 2 skipped**, exit code 0. Check the exit code,
  not only the printed count.
- **Safety.** No real credentials; no `eval()`/`exec()`; real trading
  stays disabled; strategies never bypass the risk manager; secrets are
  redacted in every log.
- **Honesty.** Only claim a test passed if you ran it. Show real command
  output. Never mock a missing import or stub a missing component.
- **English first.** Code, docs, and UI source strings are English.
  Spanish ships through Qt Linguist. Wrap every visible string in
  `self.tr()`.
- **Small changes.** One requirement per change. Update documentation in
  the same change. Tick a ROADMAP `[x]` only when the requirement is
  implemented AND tested.
- **Money is `Decimal`, time is UTC.** Never introduce `float` into a
  price, quantity, or balance path.
- **No look-ahead.** A strategy sees `candles[:i]` only; signals fill at
  the next candle's open.
- **Keep the agent-onboarding tracker current.** When you add, rename, or
  remove a file in the agent-onboarding surface, or when the test baseline
  changes, update `docs/en/developers/agent-onboarding-tracker.md` in the
  same change.

## Environment

- Debian 13, Python 3.13.5
- PyQt6 + pyqtgraph + SQLAlchemy + platformdirs from system packages
  (no venv for the default workflow)
- GUI tests run offscreen (`QT_QPA_PLATFORM=offscreen`)

## For smaller context windows

The prescribed startup reading costs ~7,000 tokens and no task needs all
of `ROADMAP.md` (one chapter averages 46 lines). See
`docs/en/developers/small-context-contributing.md`.
