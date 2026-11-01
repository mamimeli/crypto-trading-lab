# Working Method (Chapter 70)

## How we build Crypto Trading Lab

This project follows a disciplined, small-step method to ensure quality and honesty.

### 1. Small changes

Every change is kept as small as possible. Small changes are easier to review, test, and revert if necessary.

* Never combine unrelated fixes in one commit.
* Write a clear commit message explaining *why* the change was made.

### 2. Tests always run

Before any commit, the full test suite must pass.

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q
```

The baseline is **1141 passed, 2 skipped**. If tests fail, fix them before proceeding.

### 3. Results shown honestly

* Never claim a test passed without running it.
* Never claim a strategy has a statistical edge without Chapter 43 evidence.
* Never promise profits. Report observed results.

### 4. Documentation evolves with code

Documentation is not an afterthought. When you change code, update:

* Docstrings
* `docs/en/developers/`
* `docs/en/beginners/`

### 5. English first, Spanish via i18n

All source code and documentation is written in English. Spanish translations are handled via Qt Linguist:

```bash
pylupdate6 *.py -ts locale/es.ts
lrelease locale/es.ts
```

### 6. Honest metrics

When reporting results:

* Distinguish between "observed result" and "statistical evidence"
* Never show backtest profits as guaranteed future performance
* Always label risk metrics with their assumptions

## Checklist for every change

1. [ ] Write code
2. [ ] Write/Update tests
3. [ ] Run full test suite (must pass)
4. [ ] Update documentation
5. [ ] Commit with clear message
6. [ ] Push

## Evidence levels

| Level | Meaning | Example |
|-------|---------|---------|
| Observed result | What happened in one historical run | Backtest return |
| Statistical evidence | Result distinguishes from noise | PSR < 0.05 |
| Research hypothesis | Idea being tested | "SMA crossover works in trending markets" |
| Validated evidence | Survived OOS, robustness, qualification | Chapter 66 qualified strategy |

## Rules we never break

1. No real credentials in code
2. No `eval()` or `exec()`
3. Real trading disabled by default
4. Strategies never bypass risk manager
5. Secrets are redacted in logs

## Documentation files

* `CLAUDE.md` - Auto-loaded by agent tools at session start; entry point
* `ROADMAP.md` - Project specification
* `AGENTS.md` - Non-negotiable ground rules
* `AGENT-HANDOFF.md` - State for new developers
* `CONTRIBUTING.md` - Workflow, review process, quality bar
* `docs/en/developers/` - Technical documentation
* `docs/en/beginners/` - User guides

## History

* Last updated: 2026-10-29
* Version: 1.1.0
