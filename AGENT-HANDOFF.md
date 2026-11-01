# AGENT-HANDOFF.md — Continuation Guide

**Purpose:** everything a new AI Agent needs to continue this project from
its current state: what exists, what is verified, and where development
left off. The historical migration notes are kept in §3–§4 because they
still explain *why* the working rules exist.

A new AI Agent must read this file **before** doing anything else, then
`AGENTS.md`, then `ROADMAP.md`.

---

## 1. Project state (last updated 2026-10-31)

- **Repository:** `https://github.com/wachin/crypto-trading-lab`
  (branch `main`)
- **State verified at commit:** the commit that carries this file.
- **Tests:** 1158 passed, 2 skipped, **exit code 0** —
  `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q`
  (The exit code matters: the suite used to segfault while the interpreter
  shut down, so it printed "passed" and still failed the build. See §5.)
- **CI:** `tests` is **green on `main`**, but **not yet at 1158**: the last
  observed green run reports 990/2 on `ubuntu-24.04` with pip and carries
  **no annotations**. The chapter 35, 33.4, 33.5, 33.6, 33.7 and 33.8 changes add 151
  tests in total (990 → 1158) and have only been
  measured locally (Windows, Python 3.12). The history is at
  [actions/workflows/tests.yml](https://github.com/wachin/crypto-trading-lab/actions/workflows/tests.yml).
  The first green run was `38777456963` (2026-10-15); the suite had never
  passed before it. Do not let a push go red without reading the log.
- **Verified platforms:** Debian 13 (system packages, Python 3.13.5) and
  **Windows 10** (pip/PyPI, Python 3.14.7, 2026-10-01 — clean install, the
  window opens, identical numbers, `ccxt` reaches the network). The Windows
  path was re-measured on 2026-10-31 with **Python 3.12**: 1158/2, after two
  platform assumptions in the suite were fixed (see §5.2 item 10).
- **macOS — deferred by the maintainer's decision, not a pending task.** It
  comes last, once the program works on Linux and Windows. Do not spend a
  session on it and do not treat a macOS failure as a blocker. The steps are
  prepared in `README.md` and `docs/en/developers/venv-setup.md`; the
  manual `cross-platform` workflow can measure it when its turn arrives.
- **Source:** 115 Python files under `src/crypto_trading_lab/`
- **Tests:** 64 test modules under `tests/`
- **Documentation:** `docs/en/beginners/` and
  `docs/en/developers/` (virtualenv guide in `venv-setup.md`, audit in
  `unwired-modules-audit.md`)
- **Verification kit:** the `Experiments/` kit was deleted on 2026-10-16
  (commit `b296785`); `requirements-all.txt` at the repository root and the
  manual `cross-platform` workflow now carry what it did.
- **Specification:** `ROADMAP.md` — 83 chapters in 17 parts
- **Git submodules:** 8 *optional* reference projects under `external/`.
  **A fresh clone creates `external/` as eight empty placeholder directories
  (git does that for submodules); they hold no files and you do not need to
  populate them** — the application builds and tests without them (both CI
  workflows pass `submodules: false`). **All eight are studied**: chapter 25
  is `[x]` and the conclusions are in `reference-projects.md` Parts A–H. Read
  that document; go to a repository only to re-verify a specific claim, and
  fetch that one alone (`git submodule update --init external/<name>`). Never
  `--recursive` by reflex: it downloads 12 GB, 8.5 GB of it `ccxt`. If you do
  fetch them and want the space back, the tested procedure is in that
  document under "Disk cost, and what can now be removed".
- **Current phase:** the scientific engine is mature. The 2026-09/10 review
  fixed the documentation-vs-code drift and cleared all 16 unwired modules
  found in the audit; the last one, `strategy_registry`, was wired into the
  Lab and the CLI on 2026-10-07 and then re-reviewed, which exposed three
  further defects in it (see `unwired-modules-audit.md` item 16). The
  frontier now is the **scientific loop** (see `ROADMAP.md` §Delivery sequencing): finish the end-to-end pipeline on real-ish data before any packaging. Packaging (chapters 81/82/83) is **deferred** until the loop runs.
  Chapter 22 (the CLI) was completed on 2026-10-26: every subcommand now
  calls the shared use-case layer in `application.py`, so the CLI and the
  GUI cannot diverge (§5.2 item 1). Chapter 56.5 was completed on
  2026-10-28: the chapter 56 execution model now feeds the backtest engine
  and the robustness report, not only paper trading (§5.2 item 2). Chapter
  63.2 (drift reporting) was completed on 2026-10-28 as well (§5.2 item 3):
  expected ranges, drift over time, likely causes and a
  healthy/suspicious/degraded verdict. Chapters 26.2/27 were completed the
  same day (§5.2 item 4): the Binance WebSocket client is a real feed and
  `paper-live` runs a bounded session over it.
  Chapter 35 (strategy complexity) advanced on 2026-10-31 (§5.2 item 11):
  every strategy version now records its parameters, rules, indicators,
  filters, conditions, grid size and model size, and qualification shows
  them instead of a boolean. Chapter 33.4 (parameters) closed the same day
  (§5.2 item 12): parameters are a declared, validated contract and the run
  records which values produced it. Chapter 33.5 (signals) closed the same
  day (§5.2 item 13): every decision is now a frozen `Signal` record with the
  strategy id and version, market, timeframe, type, the indicator values it
  was taken on and the parameter signature — and hold is no longer the same
  value as no signal. Chapter 33.7 (validation) closed the same day (§5.2
  item 14): a strategy is checked against the data before a run, errors
  refuse it and warnings travel with the result. Chapter 33.6 (the mandatory
  architecture) closed the same day (§5.2 item 15): every order now passes
  through the risk manager, and the strategy/exchange boundary is checked by
  an import scan instead of being asserted in prose. Chapter 33.8 (research
  warnings) advanced the same day (§5.2 item 16): the seven statements now
  live in one module and both the CLI and the GUI print the same text.
  **Real trading remains disabled by default.**

### What changed on 2026-09-19 (direction correction + Fase A/B)

The previous session had drifted: commits announced features that were
only unused imports or canned text. Those were fixed and backed by real,
tested code:

- `MainWindow._open_notebook` used to crash (`ExperimentManager` has no
  `list_experiments`); the manager now really has it, with persistence,
  statuses, tags, search and comparison.
- The research assistant no longer ignores the question and returns
  canned text: it is an honest, offline methodology assistant with an
  injectable model backend and persisted conversations.
- `run_optimization` passed arguments in the wrong order and swallowed
  the error, reporting “0 combinations tested”; fixed and tested.
- `RobustnessReport.summary()` raised `ValueError` (invalid f-string);
  fixed with a regression test.
- `strategy_builder.py` imported a non-existent `IndicatorFactory`, so
  the module could not be imported; fixed.
- New: historical-data download + validation + versioned datasets
  (`market_data/historical.py`, `persistence/datasets.py`), a research
  workflow service (`research.py`), the Research Wizard, validity
  dashboard, Research Notebook UI and strategy-builder UI, all i18n.
- Round 1 also found and fixed: the Learning Center crashed on lesson
  click (`Qt.AlignHCenter`) and on the quiz (`QHBoxBoxLayout`, always
  returned False, progress never loaded); and the strategy-builder
  module was unimportable while its launcher opened the dialog twice.
- New in round 1: a 48-lesson curriculum in three levels
  (`education/curriculum.py`), a rewritten Learning Center with a working
  quiz and persisted progress, executable rule strategies
  (`rule_strategy.py`) wired into the Backtesting Lab, and paper trading
  with a mandatory risk gate and a trading journal (`paper_session.py`,
  `ui/paper/paper_trading.py`).

### Contributor infrastructure

The repository is now prepared for outside contributors who work with AI
agents:

- `CONTRIBUTING.md` — setup, workflow, definition of done, the
  non-negotiable rules, a ready-to-paste agent prompt and a list of good
  first contributions.
- `.github/workflows/tests.yml` — runs the offline suite on Debian
  packages (no pip, no venv) for every push and pull request.
- `.github/PULL_REQUEST_TEMPLATE.md` and `.github/ISSUE_TEMPLATE/` —
  they require the real test output and the owning ROADMAP chapter.
- `Makefile` — `make test`, `make run`, `make banner`, `make translations`.
- `tools/make_banner_gif.py` — regenerates the README contributor banner
  (deterministic; needs Pillow/NumPy only to regenerate the asset).
- `assets/contributing-agents.gif` — the animated banner (76 KB).

### Implemented modules (all with passing tests)

| Module | Path | Roadmap chapter |
|---|---|---|
| Domain models (Decimal, UTC) | `src/crypto_trading_lab/domain/models.py` | 7 |
| Exchange adapters + Mock + CCXT | `src/crypto_trading_lab/exchanges/` | 26-27, 30 (partial) |
| Credential store (keyring/memory) | `src/crypto_trading_lab/security/credentials.py` | 9 |
| Logging + redaction + audit | `src/crypto_trading_lab/infrastructure/logging_setup.py` | 10 |
| SQLite persistence + candle repo | `src/crypto_trading_lab/persistence/` | 8 |
| XDG configuration | `src/crypto_trading_lab/configuration/xdg.py` | 71.1 |
| i18n (en default, es) | `src/crypto_trading_lab/i18n/` | 20 |
| Main window + Learning Center | `src/crypto_trading_lab/ui/` | 71.1, 23 |
| Charts (PyQtGraph backend) | `src/crypto_trading_lab/ui/charts/` | 32, 4.2 |
| CSV import + validation | `src/crypto_trading_lab/market_data/importer.py` | 28 |
| Indicators (SMA/EMA/RSI/BB/ATR/ROC) | `src/crypto_trading_lab/indicators/library.py` | 31 |
| Backtesting engine (fees, slippage, spread, next-open) | `src/crypto_trading_lab/backtesting/engine.py` | 37, 33 |
| Performance metrics (returns, trades, risk, activity, benchmark, validity) | `src/crypto_trading_lab/backtesting/metrics.py` | 40 |
| Risk manager (position limits, loss limits, operational limits) | `src/crypto_trading_lab/risk_manager.py` | 58 |
| Emergency kill switch | `src/crypto_trading_lab/kill_switch.py` | 59 |
| Safety gates (pre-trade protection layer) | `src/crypto_trading_lab/safety_gates.py` | 67 |
| Strategy failure detection (early warning system) | `src/crypto_trading_lab/monitoring/failure_detection.py` | 64 |
| Risk of ruin and position sizing | `src/crypto_trading_lab/backtesting/robustness.py` | 60 |
| Strategy qualification (multi-criterion evaluation) | `src/crypto_trading_lab/qualification.py` | 66 |
| Robustness report (Monte Carlo, perturbation, cost sweep, OOS degradation) | `src/crypto_trading_lab/backtesting/robustness.py` | 44 |
| Statistical edge analysis (distributions, autocorrelation, bootstrap, PSR) | `src/crypto_trading_lab/backtesting/statistical_analysis.py` | 43 |
| Ensemble methods (voting, averaging, weighted combination) | `src/crypto_trading_lab/ensembles.py` | 50 |
| Portfolio construction (correlation, portfolio returns, portfolio metrics) | `src/crypto_trading_lab/portfolio.py` | 51 |
| AFML techniques (triple-barrier labeling, purged CV, sample uniqueness) | `src/crypto_trading_lab/machine_learning/` | 49 |
| Regime analysis (trending/ranging, volatility, concentration warning) | `src/crypto_trading_lab/market_data/regimes.py` | 46 |
| Feature engineering (returns, volatility, momentum, RSI, EMA, z-score) | `src/crypto_trading_lab/market_data/features.py` | 47 |
| Experiment manager (research tracking, reproducibility) | `src/crypto_trading_lab/machine_learning/experiment_manager.py` | 52 |
| Live vs backtest drift analysis | `src/crypto_trading_lab/monitoring/` | 63 |
| Real trading support (activation flow, safety protections) | `src/crypto_trading_lab/trading.py` | 68 |
| Robustness (seeded Monte Carlo, perturbation, cost sweeps) | `src/crypto_trading_lab/backtesting/robustness.py` | 44 (partial) |
| Chronological data splitting (train/validation/test) | `src/crypto_trading_lab/market_data/splitting.py` | 38 |
| Walk-forward analysis (rolling windows, per-window selection) | `src/crypto_trading_lab/backtesting/walk_forward.py` | 45 |
| AFML technique specifications | `docs/en/developers/afml-techniques.md` | 49, 47.4, 48 |
| Historical data download + validation + dataset identity | `src/crypto_trading_lab/market_data/historical.py` | 26.2, 28, 29, 53 |
| Dataset repository (versioned, checksummed) | `src/crypto_trading_lab/persistence/datasets.py` | 29, 53 |
| Download-and-store service | `src/crypto_trading_lab/market_data/dataset_service.py` | 28, 29 |
| End-to-end research workflow + validity checklist | `src/crypto_trading_lab/research.py` | 37-45, 53, 66 |
| Historical-data screen | `src/crypto_trading_lab/ui/data/historical_data.py` | 26.2, 28, 29 |
| Research Wizard | `src/crypto_trading_lab/ui/research/wizard.py` | 37-45, 66 |
| Research-validity dashboard | `src/crypto_trading_lab/ui/research/validity.py` | 43, 72 |
| Research Notebook / experiment manager UI | `src/crypto_trading_lab/ui/research/notebook.py` | 52-54 |
| Offline research assistant (injectable model backend) | `src/crypto_trading_lab/ui/research/assistant.py` | 55 |

### Domain-model naming and the chapter 7/26/30 reconciliation

- `Symbol` is the validated trading-pair type (`BASE/QUOTE`): where chapter 7
  lists "TradingPair", the implementation is `Symbol`.
- Domain models implemented: `Market`, `Ticker`, `Candle`, `Balance`,
  `OrderRequest`, `Fill`, `OrderResult` (`domain/models.py`), plus
  `BacktestConfig`, `CostModel`, `TradeRecord`, `BacktestResult`
  (`backtesting/engine.py`). All money, price, quantity, fee and balance
  fields are `Decimal`; timestamps are UTC and naive ones are rejected.
- Domain models still to add (chapter 7): Exchange, Asset, Trade, OrderBook,
  OrderBookLevel, Position, Portfolio, Order, Fee, StrategySignal,
  RiskDecision, Backtest, PaperAccount, PerformanceMetrics, DatasetVersion,
  Experiment, StrategyVersion, QualificationReport.
- Chapter 30 is only partly done: `Market` carries `min_quantity`,
  `min_notional`, `price_precision`, `quantity_precision` and maker/taker fees,
  and `ExchangeAdapter.validate_order_request` performs the shared pre-flight
  checks. Still pending: true tick-size/step-size rules, rate limits, time
  synchronisation, and the remaining pre-trade steps (risk limits, data
  freshness, duplicate prevention, idempotency identifiers, beginner-readable
  rejections).
- Chapters 26.2 and 26.3 are partial: only the Binance endpoint configuration
  exists (centralised, spot-only, tested). There is no WebSocket layer, no
  reconnection logic and no Coinbase support.

### Development environment

- Python 3.13.5, Debian 13 (trixie), PyQt6 (system), pyqtgraph 0.13.7
  (system, installed via `python3-pyqtgraph`), SQLAlchemy 2.0.40,
  platformdirs 4.3.7, pytest 8.3.5, Qt tools `pylupdate6`/`lrelease`/
  `linguist` — **all from Debian packages, no venv needed**
- **A local `.venv/` (gitignored) exists for the PyPI path.** It was built on
  2026-10-26 from `requirements-all.txt` and measured in
  `docs/en/developers/venv-setup.md` §8 (PyYAML 6.0.3, PyQt6 6.11.0,
  pytest 9.1.1, same 807/2 result). The Debian packages stay the supported
  default; use the venv only to reproduce the pip path.

### One reference you will not have

The previous developer held the book's *exhibit compilation* as a local PDF.
It is git-ignored, was deliberately deleted and is **not part of the
repository**. This is not a blocker: every technique that depended on it is
already specified in `docs/en/developers/afml-techniques.md`, with the
exhibit numbers, the equations and the primary-paper citations in its §5.
Work from that specification; do not try to obtain the PDF.

## About the book — Marcos López de Prado, *Advances in Financial Machine Learning* (Wiley, 2018)

Credit appears (and must be preserved) in:

- `docs/en/developers/reference-projects.md` — header and throughout
- `ROADMAP.md` — the "Vision and mission" section cites the book as
  the project's methodological reference
- `README.md` — "The method follows *Advances in Financial Machine
  Learning* (Marcos López de Prado)."

**Rule for the new repository:** the book is cited by bibliographic
reference only. Techniques from the book are implemented from the public
MIT-licensed exercise repository (`external/adv-financial-ml-marcos-
exercises`, already a submodule), from the book's own exhibit
compilation (a local reference copy, inventoried in
`reference-projects.md` A.9), and from the mathematical definitions
recorded in `docs/en/developers/afml-techniques.md`, always with
attribution. Never copy book text or code, and never commit the book —
printed text or exhibit compilation.

## 2. What to do if the Agent needs AFML material later

Part VIII of the ROADMAP (chapters 47-50) draws on the book. The new
repository's Agent must:

1. Read `docs/en/developers/afml-techniques.md` first — it holds the
   project's own specification of every AFML technique: purpose,
   mandatory parameters, algorithm outline, required tests, exhibit
   pointers and open questions.
2. Use `docs/en/developers/reference-projects.md` — Part A maps every
   relevant technique to roadmap sections with adoption guidance; A.9
   inventories the book's exhibit compilation (a local reference copy).
3. Use the MIT-licensed exercises submodule for reference code. For the
   snippets and equations the submodule lacks (sample weights, fractional
   differentiation, bet sizing, structural breaks, entropy, the PSR/DSR
   formulas, CPCV), use the specification in `afml-techniques.md` — it
   carries the exhibit numbers and equations, and the compilation itself
   is not available to you (see §1).
4. Implement from the recorded definitions, cite the book in
   docstrings/docs: *"Technique from López de Prado (2018),
   Advances in Financial Machine Learning, ch. N"*
5. Resolve every *open question* in `afml-techniques.md` before coding
   the affected technique. The two that were open (PBO/CSCV, ch. 49.6;
   the Deflated Sharpe Ratio, ch. 49.5) are now specified from their
   public primary papers, as the roadmap allows ("additional research",
   Ch. 49); only the DSR paper's Appendix 3 (effective number of
   independent trials) remains, with a conservative fallback. Never
   guess.
6. Never copy book text or code into the repository and never commit the
   book (printed text or exhibit compilation).

## 3. AGENTS.md at the repository root

The repository carries an `AGENTS.md` at its root so any
AI Agent (opencode, Codex, etc.) automatically loads the ground
rules. Keep it in sync with §4 of this file (the working rules) and with
the AFML book rule (§1).

## 4. Working rules (canonical)

These rules are canonical. Every Agent working here inherits them:

1. **Read `ROADMAP.md` first**; treat it as the specification. Never
   silently simplify or omit its requirements.
2. **MANDATORY STOP RULE for dependencies** (chapter 4.0 and
   `AGENTS.md` rule 2): if a new dependency is needed, STOP, notify the
   developer with package name, source (Debian/PyPI), reason, and exact
   command. Debian package → developer runs `apt install`. PyPI-only →
   the developer creates a venv (`.venv`), the Agent never installs or
   creates environments itself. The four required runtime dependencies
   come from Debian system packages; the optional extras (`ccxt`,
   `pypdf`, `keyring`, `aiohttp`, `websockets`) are PyPI-only.
3. **No real credentials**, no `eval()`/`exec()`, real trading stays
   disabled, strategies never bypass the risk manager.
4. **Vision and mission** (see ROADMAP.md intro): survive → validate
   → earn. Never risk money needed to live. Honest metrics only;
   never promise profits. The developer's economic situation makes
   capital protection a survival requirement, not ideology.
5. **Working method** (chapter 70): small changes, tests always run,
   results shown honestly, documentation evolves with code, English
   first (Spanish via Qt Linguist).
6. **Book rule** (§1 and §2 of this file): cite López de Prado by
   reference; never redistribute his text.
7. **Windows/portability**: code is Qt/stdlib/Debian-packages pure —
   keep it platform-neutral by construction, but Debian is the only
   officially supported target for now.

## 5. Where the project stands, and how to pick up work

### 5.1 The 2026-09/10 review (what changed, and why)

A repository review fixed one systematic problem: the documentation claimed
features the code did not ship. Concretely:

- **All 16 unwired modules were audited one by one.** The decisions and their
  evidence are in `docs/en/developers/unwired-modules-audit.md`: nine were
  deleted (dead, duplicated or non-functional), seven were merged or wired.
  The last of them, `strategy_registry.py`, was wired on 2026-10-07 by a
  contributing agent and then re-reviewed; the review found and fixed three
  more defects in it (a write to the current working directory on
  construction, a `_load()` that was never called, and a rule-7 regression
  in the new combo labels), plus a `strategy=None` path in the Lab.
- **The documented test baseline was wrong in twelve places** and had
  drifted between 229 and 698. It was `707 passed, 2 skipped` after that
  review, and the suite **exits 0**. The chapter 22 CLI work on 2026-10-26
  added 44 tests, so the current baseline is `807 passed, 2 skipped`.
- **The suite used to segfault while the interpreter shut down** (chapter 68
  imported Qt and re-initialised a `QObject`), so `make test` and CI failed
  while printing "passed". Fixed, with a regression test that forbids Qt in
  that module.
- **Chapter 56 execution realism is wired into paper trading**; chapter 63
  drift is shown in the Paper Trading screen; chapter 53 reproducibility now
  records the environment and the code hash; chapter 72 ethics guards report
  generation and the PDF export works; chapter 60 gained Kelly position
  sizing.
- **The CI was red for a real reason**: `ubuntu-24.04` ships SQLAlchemy 1.4
  and the code needs 2.0. `tests.yml` now installs with pip, and the manual
  `cross-platform` workflow runs Ubuntu, macOS and Windows.
- **The default CI is green for the first time.** Run
  [38772811163](https://github.com/wachin/crypto-trading-lab/actions/runs/38772811163)
  (commit `7eecb0c`) was the first pass; run
  [38777456963](https://github.com/wachin/crypto-trading-lab/actions/runs/38777456963)
  (commit `4926437`) repeats it with `707 passed, 2 skipped` in 45.8 s on
  `ubuntu-24.04`, SQLAlchemy 2.1.4 and pypdf installed — the same numbers as
  Debian. The two skips are the intentional "adapter under test has trading
  enabled" guards, not missing dependencies.
- **The workflow actions are on Node 24** (`actions/checkout@v5`,
  `actions/setup-python@v6`). GitHub had begun force-running the old
  `@v4`/`@v5` on Node 24 and annotating the run about the deprecation; the
  bump was verified by run 38777456963, which reports no annotations. Do not
  pin them back down.
- **Windows 10 is verified** (measured 2026-10-01; see README "What is
  verified"). **macOS is deferred to the end of development by the
  maintainer's decision** — see §1.

### 5.2 The backlog, in the order that makes sense

1. ~~**The CLI subcommands that only pretend to work.**~~ **DONE
   2026-10-26.** Chapter 22 is `[x]`. Every subcommand now calls
   `src/crypto_trading_lab/application.py` (the same use cases the GUI
   uses): `database check` runs SQLite's `PRAGMA integrity_check` and
   reports real row counts, `import-csv` validates before writing,
   `backtest` runs the engine and metric catalogue from a JSON/YAML
   configuration, `glossary search` parses the beginner glossary, and
   `list-lessons` reads the curriculum. `doctor` now performs all twelve
   chapter 22 checks (connectivity and clock drift behind `--network`).
   A missing database is reported as missing, and no command returns `0`
   for work it did not do. The installed console script also dispatches
   correctly now: it used to point at the GUI function, so
   `crypto-trading-lab doctor` opened a window and ignored its arguments.
   Tests: `tests/test_cli.py`, `tests/test_application.py`;
   documentation: `docs/en/developers/cli.md`. YAML configurations read
   through PyYAML: `debian/control` depends on `python3-yaml`, and
   `requirements-all.txt` plus the `yaml` extra cover pip installs.
2. ~~**Chapter 56.5** — feed the execution model into the **backtest
   engine** and robustness, not only paper trading.~~ **DONE 2026-10-28.**
   Chapter 56 is `[x]`. `BacktestConfig.execution_config` selects the model
   (and `execution_seed` makes it reproducible); with it set, the engine
   fills from a synthetic book whose depth is the traded volume *before*
   the fill candle, so oversized orders fill in part and orders with no
   depth are rejected instead of assumed away. `run_backtest` records the
   model and the seed in `config_metadata`, and the CLI names the model and
   reports rejections and partial fills. In robustness, `sweep_costs` now
   scales the model's own slippage assumptions (it used to drop the
   execution config and `position_fraction`), and `compare_execution_models`
   adds an `execution_impact` section to every `RobustnessReport`. Note the
   direction: the cost model applies a fixed adverse slippage while
   chapter 56 draws from a symmetric band, so the realistic arm can come
   out cheaper — the report says so instead of implying safety. The
   cost-model path is numerically unchanged. Tests:
   `tests/backtesting/test_execution_in_backtest.py`, plus 8 new cases in
   `tests/backtesting/test_robustness.py` and `tests/test_cli.py`.
3. ~~**Chapter 63.2** — drift over time, likely causes, and marking a
   strategy as degraded.~~ **DONE 2026-10-28.** `expected_ranges()` gives the
   band a live run should stay inside (trade bootstrap for return, anchored
   on the observed drawdown with a 1.5x tolerance for drawdown, because
   resampling trades cannot see intra-trade drawdown), `drift_over_time()`
   splits both equity curves into slices, and `assess_drift()` returns a
   `StrategyHealth` (healthy / suspicious / degraded) with the reasons, the
   causes and the evidence. The Paper Trading screen renders it. Chapter 63
   stays `[~]` for one reason that is *not* this item: "live behavior"
   needs live trading (chapter 68); 63.3 (education text) closed 2026-10-29. Tests: 12 new cases in `tests/test_live_vs_backtest.py`; documented
   in `docs/en/developers/live-vs-backtest-drift.md`.
4. ~~**Chapters 26.2/27** — a continuous Binance WebSocket feed.~~ **DONE
   2026-10-28.** The client had five real defects, all fixed: `start()`
   blocked forever; staleness was only checked after a message arrived;
   renewal logged a line and kept the dead socket; dedup keyed on event time
   across streams; tickers were never dispatched. `run_paper_session_live()`
   now runs a bounded session, writes nothing to the working directory, keeps
   the caller's config, and refuses to evaluate a signal while the feed is
   DEGRADED. `crypto-trading-lab paper-live` exposes it, and a session too
   short to warm the strategy up now says so (`warmup_candles` on the
   strategy, a `Warm-up:` line in the output and a sentence in the note)
   instead of leaving an empty journal looking like a flat market. The same
   day, `paper-live` and the Historical Data screen were opened to every
   interval Binance serves (`1s` included); `1M` needed a calendar-based
   validator, which `CALENDAR_INTERVALS` now selects. That work exposed a
   chapter 40 defect: annualization assumed 365 periods per year for every
   interval. `BacktestResult.interval` now records the interval and
   `MetricConfig.for_interval` derives the periods from it. The review
   that followed added the other half: `min_span_days` (30) gates
   Sharpe/Sortino validity on market time, not just row count, and
   `ExperimentRecord.metric_config` stores the assumptions with the
   metrics so a saved Sharpe stays readable at the interval it used. The
   two test-only helpers from that review are fixed as well:
   `probabilistic_sharpe_ratio` de-annualizes before meeting its
   per-candle sample size, and `compute_portfolio_metrics` takes
   `periods_per_year`, compounds, and measures drawdown on the curve.
   Chapter 27 is `[x]`
   (the troubleshooting links pointed at a file that did not exist; it now
   exists and a test resolves every link and anchor). Chapter 26 stays `[~]`
   for 26.1 "demonstrations" and 26.3 Coinbase, neither of which this task
   covered. **Next task: chapters 81/82/83 (packaging).**

   *Known limitation, stated so nobody is surprised:* the Paper Trading
   **screen** still replays a dataset. The live session is reachable from the
   CLI only; wiring it into the Qt screen needs a thread or an asyncio bridge
   and is deliberately left as its own task.
5. **Finish the scientific loop first — this is the priority.** `ROADMAP.md`
   now carries a §Delivery sequencing section that defines the one thing to
   ship before anything else: the end-to-end loop — learn → choose market →
   get data → form an idea → write a hypothesis → backtest → analyse →
   try to refute it → OOS / walk-forward → robustness → paper trading →
   qualification → testnet → evidence-of-edge gate → (only then) consider
   real trading. The loop stages still open are 33–35
   (strategies + builder; 33 initial strategies 2/3/4/6 done 2026-10-29, 33.1-33.9 still open), 37–38 (backtesting + splitting), 40–42
   (metrics/reports/benchmarks), 44–46 (robustness/walk-forward/regime), 57
   (paper-trading live wiring into the Qt screen). 62–63 are `[~]` as of
   2026-10-29: 62.1/62.2 (monitored state + alert rules), 63.1 (latency and
   volatility drift) and 63.3 (education) are done; only the live-behavior
   comparison items remain (they need live trading, chapter 68),
   Close these on real-ish data before
   any packaging. (Chapters 67, 64 and 66 - safety gates, failure detection and
   qualification - are [x] as of 2026-10-28.)
   Chapter 29 (data quality) is [~] as of 2026-10-29: delisted-asset,
   liquidity-change and survivorship-bias checks plus dataset provenance
   are done; imbalance bars (29.1) stay unsupported without trade-level
   data.
6. **Chapter 48 — machine learning** is part of the loop's refute/robustness
   stage but deliberately unbuilt; it needs a dependency decision first
   (chapter 4) before any code, so it follows the loop stages that need no new
   dependency.
7. **Translations** — the Spanish `.ts` still has untranslated strings that
   fall back to English. UI polish; can proceed in parallel, not blocking.
8. **Chapters 81/82/83 — packaging. DEFERRED until the loop runs.** Do not
   start packaging until the §Delivery sequencing loop is operational end to
   end. The Debian packaging is stale: `debian/rules` calls `setup.py install`
   and `debian/control` does not list pyqtgraph or platformdirs.
9. ~~**Chapter 25 — finish the reference-project study.**~~ **DONE
   2026-10-15.** All eight references are studied and documented in
   `reference-projects.md` Parts A–H; the chapter is `[x]` and its closing
   requirement is met. **This unblocks deleting `external/` (12 GB)** — the
   conclusions are the deliverable, not the vendored copies. Three of the
   four new Parts corrected claims their own projects advertise (see the
   chapter's notes), which is why the roadmap demanded per-feature
   verification.
10. ~~**The suite was red on Windows.**~~ **DONE 2026-10-31.** Not a chapter:
    a contributor following `README.md` §5.3 (Windows, PowerShell) got
    `2 failed, 988 passed` where the docs promised 990/2. Both failures were
    platform assumptions in the tests, not logic bugs: `markdown_files()`
    sorted `Path` objects and Windows compares paths case-insensitively, and
    two tests waited for real elapsed time by polling with 100 and 50
    `asyncio.sleep(0.01)` calls — on Windows the event-loop clock advances
    every 15.6 ms, so those sleeps can all return early and the loop finished
    before the timer had ticked. Both tests now wait on an event with a 5 s
    timeout, and the feed measures connection age with `time.monotonic()`.
    A third test (`test_stale_data_is_detected_without_waiting_for_a_message`)
    had the same defect and surfaced as flaky on the next run. README §5.3 now
    states the expected output and explains the two harmless Qt startup lines
    and that `QT_QPA_PLATFORM=offscreen` opens the GUI headless.
11. ~~**Chapter 35 — strategy complexity control.**~~ **DONE 2026-10-31**
    (advances item 5, the "form an idea" stage). `complexity_control.py` now
    holds two clearly separated things: the old code-level maintainability
    analyzer, and `StrategyComplexity` — the chapter 35 record of parameters,
    rules, indicators, filters, conditions, grid size and model size per
    strategy *version*. The registry stores it (and recomputes the parameter
    count, grid and version on `update_metadata`), declarative rules derive it
    from the rule itself, the Backtesting Lab prints it, and the chapter 66
    qualification criterion now carries `score=…` plus the breakdown instead
    of a bare boolean. The two decision rules (`prefer_simpler`,
    `complexity_growth_warning`) are implemented, tested and documented in
    `docs/en/developers/strategy-complexity.md`, but **nothing calls them
    yet** — no screen compares two strategies — so their roadmap boxes stay
    open. Chapter 35 is `[~]`, 9 of 12 boxes ticked.
    **Next task:** chapters 33.1–33.9 (strategy identity, market
    requirements, declared parameters, signal record) or 34 (the visual
    builder's remaining blocks: filters and arithmetic are rejected today).
12. ~~**Chapter 33.4 — parameters.**~~ **DONE 2026-10-31** (same stage as
    item 11). `strategy_parameters.py` declares the contract
    (`ParameterSpec`), the per-version schema with cross-parameter rules
    (`ParameterSchema`, `CombinationRule`) and the frozen validated values
    (`ParameterSet`, `signature()`). The registry validates in
    `create_instance()`/`parameter_set()`, so CLI, GUI and services share one
    gate; `application.py` no longer coerces parameters by hand; the
    backtest records `strategy_parameters` in its metadata and the CLI prints
    it; and `run_backtest()` raises if a strategy rewrites its own dataclass
    fields mid-run. Chapter 33.4 is fully `[x]`; chapter 33 overall is `[~]`
    with 33.1–33.3 and 33.5–33.9 still open. Docs:
    `docs/en/developers/strategy-parameters.md`.
    **Next task:** chapter 33.5 (explicit signal records: timestamp, strategy
    id and version, market, timeframe, type, indicator values, parameter
    signature) — it is the natural follow-up because `ParameterSet.signature()`
    is exactly the parameter-set identifier the signal must carry.
13. ~~**Chapter 33.5 — signal generation.**~~ **DONE 2026-10-31** (same stage
    as items 11 and 12). `signals.py` holds the chapter's vocabulary
    (`SignalType`) and a frozen `Signal` record; `run_backtest()` writes one
    per candle into `BacktestResult.signals`, stamped with the strategy id and
    version, the market and timeframe from the candle, the type, the indicator
    values the decision used (`indicator_values()` on every built-in) and the
    chapter 33.4 parameter signature. Two distinctions are now kept instead of
    collapsed: **hold vs no signal**, and **the decision vs what the engine
    could act on** (`actionable` is false for a BUY while already long).
    Built-ins also declare a `ClassVar` `identifier` equal to their registry id,
    because `Strategy.name` is a parameterised sentence and cannot be the
    identifier; a registry test keeps the two in sync.
    `enter_short`/`exit_short` exist in the vocabulary but **nothing emits
    them** (long-only spot), so those two boxes stay open on purpose. Chapter
    33.5 is 12 of 14 boxes; chapter 33 overall is `[~]` with 33.1–33.3 and
    33.6–33.9 still open. Docs: `docs/en/developers/signal-records.md`.
    **Next task:** chapter 33.6 (the mandatory signal → risk → order flow,
    enforced rather than described) — or 33.7 (strategy validation before a run:
    configuration, indicators, timeframe, warm-up, market compatibility), which
    is the natural neighbour of what was just built.
14. ~~**Chapter 33.7 — strategy validation.**~~ **DONE 2026-10-31** (same stage
    as items 11–13). `strategy_validation.py` is the gate before a run:
    `validate_for_run()` checks configuration, parameters (the chapter 33.4
    schema), required indicators, timeframe grammar and consistency, warm-up,
    market compatibility and impossible or contradictory rules, returning
    `ValidationIssue`s with a severity and a stable code. Errors refuse the
    run; warnings are kept on `BacktestRun.validation` and printed by the CLI.
    Nothing calls `on_candle`, so validation cannot disturb the strategy's
    streaming state. Wired into `run_backtest` (with the loaded candles) and
    into `run_live_paper_session` (no sample yet, so only the
    sample-independent checks). Chapter 33.7 is fully `[x]`; chapter 33
    overall is `[~]` at 37 of 86 boxes, with 33.1–33.3, 33.6, 33.8 and 33.9
    still open. Docs: `docs/en/developers/strategy-validation.md`.
    **Next task:** chapter 33.6 (enforce the signal → risk → order flow: no
    strategy reaches an exchange, the risk manager or credentials) — it is the
    last structural box in chapter 33 and can be checked by a boundary test
    over the strategy modules plus the engine's hand-off to `RiskManager`.
15. ~~**Chapter 33.6 — mandatory architecture.**~~ **DONE 2026-10-31** (same
    stage as items 11–14). `run_backtest()` builds a `RiskManager` per run and
    evaluates every order it would create (exits included); a refusal means no
    order that candle, the signal is still recorded, and
    `risk_rejections`/`risk_rejection_reasons` count what happened. With no
    limits configured the manager is `RiskManager.permissive()` — the gate is
    in the path with nothing to refuse — and `config_metadata["risk_gate"]`
    says which of the two ran. New `tests/test_architecture_boundaries.py`
    parses the strategy-surface modules with `ast` and refuses imports of an
    exchange, credentials, the network, or (outside the executor) the risk
    manager; the scan is tested against a violating file.
    **Fixed on the way:** `on_candle` received the whole candle sequence while
    the docstring claimed `candles[:i+1]`; it now gets a `_VisibleCandles` view
    (O(1), indices past the current candle raise `IndexError`). Chapter 33.6
    is fully `[x]`; chapter 33 is `[~]` at 42 of 86 boxes, with 33.1–33.3,
    33.8 and 33.9 open. Docs:
    `docs/en/developers/architecture-boundaries.md`.
    **Next task:** chapter 33.8 (the research warnings a user must see before
    trusting a result: chance, overfitting, filters that do not help, the
    out-of-sample rule) or 33.9 (per-strategy beginner documentation, which the
    beginner docs already partly cover and should be wired to each strategy).
16. ~~**Chapter 33.8 — research warnings.**~~ **6 of 7 done 2026-10-31** (same
    stage as items 11–15). `research_warnings.py` holds the chapter's seven
    statements as constants; `warnings_for_run()` returns the applicable ones
    (chance and "profit is not quality" always, overfitting at three or more
    parameters or after an optimization on the same data, the filter warning
    when filters exist, out-of-sample unless evaluated out of sample,
    complexity when the chapter 35 record is missing). The CLI prints them and
    the Backtesting Lab appends the same text, so the two surfaces cannot
    drift. **The seventh box stays open:** "favour simpler strategies when
    performance is comparable" needs a screen that compares two strategies,
    and `prefer_simpler` still has no caller — same honest state as chapter
    35. Chapter 33 is `[~]` at 48 of 86 boxes; 33.1–33.3 and 33.9 remain.
    **Next task:** chapter 33.9 (per-strategy beginner documentation: what it
    assumes, what it reads, what makes it enter and exit, when it hurts) —
    it is the last piece of chapter 33 that is not structural, and the
    beginner docs already cover the shared vocabulary.

Anything in `ROADMAP.md` marked `[ ]` or `[~]` is fair game. The roadmap is
the specification; this list is only the recommended order.

### 5.3 How to work here

- Read the chapter that owns the task before writing code.
- Run `make test` (or `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q`)
  and check the **exit code**, not only the printed count.
- One requirement per change; tick a ROADMAP box only when it is implemented
  **and** tested; update the documentation in the same change.
- Never install a dependency: stop and report it (see `AGENTS.md` rule 2).
- Real trading stays disabled. That rule has no exceptions.

## 6. Quick-start for the new Agent

```bash
# 1. (Optional) the 8 reference projects under external/ — not needed to
#    build, run or test the application, and 12 GB on disk. Fetch only the
#    one your task studies, e.g.:
git submodule update --init external/freqtrade

# 2. Verify the environment:
python3 --version            # ≥ 3.11 expected (3.13 on record)
python3 -c "import PyQt6, pyqtgraph, sqlalchemy, platformdirs; print('deps OK')"
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q   # 1158 passed, 2 skipped expected

# 3. Read in this order:
#    1. AGENT-HANDOFF.md (this file) — state and next steps
#    2. AGENTS.md — the non-negotiable rules
#    3. ROADMAP.md — the specification (find the chapter that owns your task)
#    4. CONTRIBUTING.md — workflow and definition of done
#    5. docs/en/developers/afml-techniques.md (when AFML is needed)
```

If the test count differs, stop and report it before changing anything.

---

*Handoff updated 2026-10-31. Baseline: 1158 passed, 2 skipped.*
