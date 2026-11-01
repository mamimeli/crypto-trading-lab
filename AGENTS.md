# AGENTS.md — Crypto Trading Lab

Ground rules for any AI Agent working in this repository.
Read `AGENT-HANDOFF.md` first if you are starting a session in a
freshly migrated copy, then the `ROADMAP.md` chapter that owns your
task.

## Non-negotiable rules

1. **ROADMAP.md is the specification.** Do not replace, simplify,
   reinterpret, or silently omit its requirements. If something is
   unclear, say so explicitly instead of guessing. Mark completed
   items with `[x]` as you finish them.
2. **Dependency STOP rule.** If development needs a new dependency:
   STOP at that task. Do NOT install anything yourself (no apt, no
   pip, no venv creation). Notify the developer with: package name,
   Debian-or-PyPI source, reason, and the exact command to run.
   PyPI-only packages require the developer to create a venv
   (`.venv`) — the Agent uses it afterwards but never creates or
   installs into one. The supported Debian 13 setup uses system
   packages for the four required dependencies; the optional extras
   (`ccxt`, `pypdf`, `keyring`, `aiohttp`, `websockets`) and the
   macOS/Windows paths are PyPI-only and documented in `README.md`
   and `docs/en/developers/venv-setup.md`.
3. **Security posture.** No real credentials in code/tests; no
   `eval()`/`exec()`; real trading stays disabled by default and
   only activates through the chapter 68 flow; strategies never
   bypass the risk manager; secrets are redacted in every log.
4. **Vision and mission.** Survive → validate → earn. The program
   never promises profits and must tell the user the truth when no
   statistical edge exists. Capital protection outranks profit
   seeking: never encourage trading money needed to live. The sentence
   that states the whole project is: *"This program tries, with
   scientific honesty, to find and validate an edge — and it tells you
   the truth when there isn't one."* Nobody can promise which year the
   rain comes; some people do make a living from these markets, and
   they are the ones who measure and protect themselves from the bad
   years rather than the ones who hope.
5. **Honesty in reporting.** Only claim a test passed if you ran it.
   Show real command output. If a tool is missing, say so and give
   the command; never pretend success. Never mock a missing import or
   stub a missing component to make work appear to continue — stop and
   report the blocker instead.
6. **The AFML book rule.** *Advances in Financial Machine Learning*
   (Marcos López de Prado, Wiley 2018) is cited by bibliographic
   reference only. Record every technique mapping and definition in
   `docs/en/developers/reference-projects.md` and
   `docs/en/developers/afml-techniques.md`; cite the book as
   "López de Prado (2018), Advances in Financial Machine Learning,
   ch. N"; never copy book text, code, figures, or tables into the
   repository; never commit or redistribute the book itself — printed
   text or local exhibit compilation — which stays a local reference.
7. **Language.** English is the source language for code, docs, and
   UI strings; Spanish via Qt Linguist (`pylupdate6` → `.ts` →
   `lrelease` → `.qm`). Never hard-code visible strings outside
   `self.tr()`.
8. **Working method.** Small changes; run the full test suite
   (`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q`) after
   every iteration; update documentation in the same change;
   beginner-oriented explanations accompany user-facing features.
   Build only what the task needs: never scatter empty stubs or
   placeholder modules to mirror the planned architecture — that
   produces the documentation-vs-code drift this project already
   spent a review cleaning up.
9. **Silence is not approval.** Do not assume that because nobody
   answered, the work was accepted. Stop at the boundary you were
   given and wait for an explicit answer; if you must proceed on an
   assumption, state the assumption where the human will see it.
10. **Keep the agent-onboarding tracker current.** When you add,
    rename, or remove a file in the agent-onboarding surface
    (`AGENTS.md`, `CLAUDE.md`, `AGENT-HANDOFF.md`, the onboarding
    reading lists, the agent prompt in `README.md`), or when the test
    baseline changes, update
    `docs/en/developers/agent-onboarding-tracker.md` in the same
    change: tick or add the relevant row, update the "Last verified"
    date, and sync the baseline across every file the tracker lists.

## Environment facts (verify at session start)

- Debian 13, Python 3.13.5, PyQt6 + pyqtgraph + SQLAlchemy +
  platformdirs from system packages (no venv)
- Expected baseline: **1071 passed, 2 skipped**
- GUI tests run offscreen (`QT_QPA_PLATFORM=offscreen`)

## Current position

The scientific core is implemented and tested: domain models, market
data, indicators, the backtesting engine, performance metrics, the
research workflow, robustness analysis and paper trading over replayed
datasets. All 16 unwired modules the 2026-09/10 audit found are now
resolved, and chapter 22 (the CLI) is complete: every subcommand calls
the shared use cases in `src/crypto_trading_lab/application.py`, the same
functions the GUI uses. The immediate frontier is the **scientific loop**
— finishing the end-to-end pipeline (learn → choose market → get data →
idea → hypothesis → backtest → analyse → refute → OOS/walk-forward →
robustness → paper trading → qualification → testnet → evidence-of-edge
gate) on real-ish data. Per `ROADMAP.md` §Delivery sequencing, **packaging
(ch. 81/82/83) is deferred** until that loop runs. Real trading stays
disabled by default.

`ROADMAP.md` is the per-chapter source of truth for what remains; see
`AGENT-HANDOFF.md` §5 for the exact continuation point.
