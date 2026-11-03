# Contributing with a small context window

**Short answer: a 300,000-token context window is far more than this project
needs.** The numbers below are measured from the repository, not estimated
from the task. What actually decides whether a contributing agent succeeds
here is not the size of its window but whether it works in small, verified
steps — which is what `AGENTS.md` rule 8 and
[`working-method.md`](working-method.md) already require.

## What each thing costs

Token counts are approximate, using the usual ≈4 characters per token for
English prose (code is a little denser).

| What you might load | Size | ≈ tokens |
|---|---|---|
| `AGENT-HANDOFF.md` (state + continuation point) | 388 lines, 22 KB | ~6,000 |
| `AGENTS.md` (the ground rules) | 73 lines, 4 KB | ~1,000 |
| One ROADMAP chapter — the **median** chapter | 46 lines | ~400 |
| The **largest** ROADMAP chapter (37, Backtesting) | 216 lines | ~2,000 |
| `ROADMAP.md` **in full** (all 80 chapters) | 5,134 lines, 172 KB | ~45,000 |
| `docs/en/developers/unwired-modules-audit.md` in full | 435 lines, 25 KB | ~6,000 |

**The startup path the README prescribes** — the handoff, the rules, and the
one ROADMAP chapter that owns the task — is roughly **7,000 tokens**. A
complete work cycle (startup + the source file + a test run + the doc edit)
stays in the low tens of thousands, about **a tenth of a 300,000-token
window**; seven copies of the whole `ROADMAP.md` would still fit.

So the window is not the constraint. The constraint is discipline.

## Never load these

| Do not | Why |
|---|---|
| Read anything under `external/` | It is **empty**. A fresh clone creates `external/` as eight placeholder directories with no files; the eight reference projects are 11 GB of git history and their study is **concluded** — the conclusions are in `reference-projects.md` (Parts A–H). Read that document, never the repositories, and never fetch one to answer a question it already answers. |
| Read a whole large source file | The biggest are `exchanges/ccxt/adapter.py` (1,011 lines), `paper_session.py` (913), `ui/backtesting/lab.py` (868), `exchanges/binance/adapter.py` (825). Use grep for the symbol, then read only that function with `offset`/`limit`. |
| Read `ROADMAP.md` from top to bottom | 45 K tokens to find one chapter. Jump to the chapter that owns the task. |
| Read a whole test log | The suite prints 4 warnings and a long summary. Use `tail`, and read the **exit code**. |
| Re-derive the project state | `AGENT-HANDOFF.md` §5 is the continuation point on purpose. Read it instead of reconstructing history from `git log`. |

## The loop that keeps it small

1. Read `AGENT-HANDOFF.md` §1 and §5, then `AGENTS.md`.
2. Pick **one** unchecked box in the ROADMAP chapter that owns the task and
   read only that chapter.
3. `grep` the symbol you need; read only that function, not the file.
4. Run the narrow test while iterating
   (`pytest tests/path/test_x.py::test_name -q`), and the **full** suite once
   before you finish — checking the exit code, not only the count.
5. Update the documentation in the same change, and tick the ROADMAP box only
   when the requirement is implemented **and** tested.

A useful property of this repository: the test suite is **offline by design**
("a test that reaches the network is a bug"). Verification is therefore
cheap, deterministic and repeatable, which matters much more to a smaller or
less capable model than raw window size does. Measured on 2026-10-28 —
pointing every proxy at a dead port changes nothing:

```bash
http_proxy=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 \
ALL_PROXY=http://127.0.0.1:9 QT_QPA_PLATFORM=offscreen \
python3 -m pytest tests/ -q
# → 864 passed, 2 skipped, exit code 0
```

The two skips are intentional guards in `tests/exchanges/contract.py`
("adapter under test has trading enabled"), not missing dependencies. Run
exactly this if you want to convince yourself that your agent cannot be
quietly depending on the network.

## Write state into the repository, not into the conversation

A fresh session has no memory of the previous one, whatever its window. That
is why `AGENT-HANDOFF.md` exists: it carries the state, the verified numbers
and the ordered backlog across sessions. When you finish a session, leave
that file accurate — it is the single thing the next agent, human or not,
will read first.

## An honest caveat

A large context window and a capable model are not the same thing.
300,000 tokens is comfortably enough for any single item on this project's
backlog; whether the work comes out correct depends on the model following
the rules, running the commands, and reporting what it actually observed. If
the model is on the smaller side, prefer the tasks that are easiest to
verify — offline, deterministic, with tests already in place — and let it
hand back a bounded result rather than a broad refactor.

## A good first task for a smaller model

`AGENT-HANDOFF.md` §5.2: the chapter 22 CLI and chapter 56.5 (execution
realism in the backtest engine) are finished, so start from the next open
item instead — give the chapter-35 complexity-growth warning a CLI caller
(`compare-strategy-versions` in `strategy_comparison.py`) or one Debian
packaging task (chapter 82). Both are bounded and entirely offline. Pick a
single command or a single table, and the existing test suite tells you
whether it still works.
