# Changelog

All notable changes to Crypto Trading Lab are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/),
and the project intends to follow
[Semantic Versioning](https://semver.org/) once it reaches 1.0
(current version: `0.0.0.dev0`).

Entries before this file existed live only in `git log --oneline`; the
list below starts at the repository review that created it. For the
per-chapter state of the specification, see [`ROADMAP.md`](ROADMAP.md).

## [Unreleased]

### Fixed

- **A quadratic backtest introduced by the chapter 33.6 candle view.** The
  engine now hands strategies a growing view of the past instead of the whole
  sequence, which invalidated the length-keyed indicator caches in
  `RSIStrategy` and `RuleStrategy` on every candle: a 2 000-candle run went
  from ~0.02 s to 16 s for RSI and 12 s for a rule. Both now use streaming
  indicators. New `EMAStream`, `RSIStream`, `ATRStream` and `ROCStream` join
  `SMAStream`; `tests/indicators/test_streams.py` compares every stream
  against its batch formula value by value, including the warm-up `None`s, so
  a stream cannot drift from the documented formula and silently change
  results. Measured after the fix: 5 000 candles in 0.09 s (RSI) and 0.35 s
  (rule), linear in the number of candles. One test in
  `tests/backtesting/test_strategies_33.py` called `on_candle` out of order —
  the old recompute tolerated it, the streaming contract (which the SMA
  strategies always had) does not — and now feeds the candles in order.

### Added

- **Chapter 33.1 (identity) closed — a strategy is named in one place.** New
  `strategy_identity.py` holds one frozen `StrategyIdentity` per built-in
  strategy with the nine facts the chapter asks for: name, identifier,
  version, author, description, category, beginner explanation, known
  weaknesses and risk warnings. The registry now reads name/version/author/
  description/category from it, which retires the
  `strategy_id.replace("_", " ").title()` guess that produced "Ma Crossover"
  and the hand-typed descriptions that lived only inside
  `_load_builtin_strategies`. `StrategyMetadata.category` is exported and
  imported through JSON. Weaknesses and risk warnings are separate fields on
  purpose: one is where the strategy is fragile, the other is what that does
  to an account, and a single merged list would let a strategy declare the
  mild version of each. Visible in `list-strategies` (category), in
  `list-strategies --explain ID` (identity block before the guide) and in the
  Backtesting Lab report.

- **Chapter 33.9 (beginner documentation) closed — every strategy answers
  the ten questions.** New `strategy_guide.py` holds one frozen
  `StrategyGuide` per built-in strategy, and `render()` turns it into the text
  a beginner reads. Sizing and stops are module constants shared by all six,
  because they belong to the engine: six paraphrases of the same paragraph
  would be six chances to disagree. Three surfaces read the same records — the
  CLI (`list-strategies --explain [ID]`, no id meaning all of them), the
  Backtesting Lab report (a "What this strategy is trying to do" section
  printed before the money, so the reader knows what the number describes) and
  `docs/en/beginners/strategy-guides.md`. A custom rule gets the engine's
  sizing paragraph and the one stop rule that matters (stops are checked on
  candle closes, so a wick passes through unseen), and a strategy registered
  later without a guide prints "no beginner guide is written for this yet"
  instead of silently omitting the section.
  `test_every_builtin_strategy_has_a_guide` compares the guide set against the
  registry, so that gap cannot reach a user unnoticed.

- **Chapter 33.8 (research warnings) — the caveats that travel with the
  number.** New `research_warnings.py` holds the chapter's seven statements
  as constants, because a warning paraphrased differently on every screen is
  a warning nobody can test. `warnings_for_run()` returns the ones that apply
  to a run: chance and "profit is not quality" always; overfitting when the
  strategy declares three or more parameters or the run was optimized on the
  same data; the filter warning when filters exist; the out-of-sample warning
  unless the run was evaluated out of sample; the complexity warning when the
  chapter 35 record is missing. The CLI prints them under "Before you trust
  this result", and the Backtesting Lab appends the same canonical text to its
  "Please read before trusting this" block — the hand-written duplicates in
  the GUI were removed so the two surfaces cannot drift. 6 of 7 boxes ticked;
  the seventh ("favour simpler strategies when performance is comparable")
  stays open because `prefer_simpler` still has no screen that compares two
  strategies.

- **Chapter 33.6 (mandatory architecture) closed — the flow is enforced, not
  described.** `run_backtest()` now builds a `RiskManager` per run and
  evaluates every order it would create, including exits: a refusal means no
  order that candle, the signal is still recorded, and
  `BacktestResult.risk_rejections` / `risk_rejection_reasons` say what
  happened. With no limits configured the engine uses
  `RiskManager.permissive()` — the gate is in the path, it just has nothing
  to refuse, because a backtest must not invent a risk appetite nobody
  stated — and `config_metadata["risk_gate"]` records which of the two ran.
  New `tests/test_architecture_boundaries.py` parses the strategy-surface
  modules with `ast` and refuses any import of an exchange, credentials, the
  network or (outside the executor) the risk manager; the scan is itself
  tested against a violating file. `RiskLimits` is frozen and a fresh manager
  is built per run, so a counter cannot leak between runs. Documented in
  `docs/en/developers/architecture-boundaries.md`; 5 boxes ticked in chapter
  33.6.
  **Fixed while enforcing it:** the engine passed the *whole* candle sequence
  to `on_candle` and trusted each strategy to slice it, while its own
  docstring claimed the strategy saw `candles[:i+1]`. It now passes a
  `_VisibleCandles` view (O(1); a slice per candle would be O(N²)) whose
  length, iteration and indices stop at the current candle, raising an
  `IndexError` that distinguishes *hidden* from *absent*.

- **Chapter 33.7 (strategy validation) closed — the gate before the run.**
  New `strategy_validation.py`: `validate_for_run()` returns
  `StrategyValidation` (a tuple of `ValidationIssue`s, each with a severity
  and a stable code) and refuses the run when an error is present.
  **Errors and warnings are different things on purpose**: an error means
  the run cannot mean anything (a warm-up longer than the sample, so no
  candle will ever be enough), a warning means it can but the user should
  know (the warm-up eats most of the sample). The checks cover
  configuration, parameters (chapter 33.4 schema), required indicators,
  timeframe grammar and consistency, warm-up, market compatibility, and
  impossible or contradictory rules — identical entry and exit, conditions
  between two constants, and bounds that cannot both hold. None of them
  calls `on_candle`, so the strategy's streaming state is untouched.
  Wired into `run_backtest` (errors become an `ApplicationError` listing
  every reason, warnings are kept on `BacktestRun.validation` and printed by
  the CLI) and into `run_live_paper_session` (no sample yet, so only the
  sample-independent checks). Documented in
  `docs/en/developers/strategy-validation.md`; 8 boxes ticked in chapter
  33.7. Fixed in the same change: `ParameterSpec(kind="int")` used to accept
  the string and fail later inside `coerce()` with a misleading message; the
  kind is now coerced at the declaration.

- **Chapter 33.5 (signal generation) closed — the decision, written down.**
  New `signals.py`: `SignalType` is the chapter's vocabulary (`enter_long`,
  `exit_long`, `enter_short`, `exit_short`, `hold`, `no_signal`) and `Signal`
  is a frozen record carrying timestamp (naive is rejected), strategy id and
  version, market, timeframe, type, the indicator values the decision was
  taken on, and the chapter 33.4 parameter signature. `run_backtest()` now
  writes one record per candle into `BacktestResult.signals`, so the two
  things the old `None` threw away are kept: **hold vs no signal** (in a
  position and silent is not the same as flat and silent) and **the decision
  vs what the engine could act on** (`actionable` is false for a BUY while
  already long, since the MVP engine is long-only spot). Every built-in
  strategy gained `indicator_values()` and a `ClassVar` `identifier` equal to
  its registry id — `Strategy.name` is a sentence that changes with the
  parameters, so it cannot be the identifier — and a registry test keeps the
  two from drifting apart. `enter_short`/`exit_short` exist in the vocabulary
  but nothing emits them, so their roadmap boxes stay open on purpose.
  Documented in `docs/en/developers/signal-records.md`; 12 boxes ticked in
  chapter 33.5.

- **Chapter 33.4 (parameters) closed — a contract instead of a bag of
  kwargs.** New `strategy_parameters.py`: `ParameterSpec` (name, kind,
  default, bounds, allowed values, description, rule text), `ParameterSchema`
  (the specs one version declares plus `CombinationRule`s for checks no
  single parameter can express) and `ParameterSet` (validated, frozen, with
  a `signature()`). `StrategyRegistry.create_instance()` and
  `parameter_set()` validate through the schema, so every entry point is
  covered: values are coerced (`"20"` → `20`, `True` is rejected as a
  number), bounds and combinations are enforced (`fast < slow`,
  `oversold < overbought`) and a misspelt parameter raises instead of being
  swallowed. `application.py` stopped re-implementing those checks by hand.
  What ran is recorded: `ma_crossover@1.0.0(fast=5, slow=20)` goes into
  `BacktestConfig.strategy_parameters`, lands in the result metadata and the
  CLI prints it. `run_backtest()` snapshots the strategy's dataclass fields
  and raises if a strategy rewrites them mid-run, so a parameter cannot move
  silently even by the strategy's own hand. Documented in
  `docs/en/developers/strategy-parameters.md`; 11 boxes ticked in chapter
  33.4, with the two limits (combination rules do not survive JSON; a stored
  schema without a default falls back to the strategy's own checks) written
  in the chapter and the doc.

- **Chapter 35 (strategy complexity) advanced — the record, and where it is
  shown.** `complexity_control.py` now separates two questions it used to
  blur: the code-level maintainability analyzer (cyclomatic complexity,
  Halstead volume) and `StrategyComplexity`, which records per strategy
  *version* exactly what chapter 35 asks for — parameters, rules,
  indicators, filters, conditions, the size of the parameter grid and the
  size of any machine-learning model. The registry stores the record with
  each registration and recomputes the parameter count, the grid and the
  version when `update_metadata()` changes them; declarative rules derive
  theirs from the rule itself (`strategy_complexity_from_rule`); the
  Backtesting Lab prints it under "What this strategy version declares";
  and `qualification.evaluate_complexity` now accepts the metrics and puts
  `score=…` plus the breakdown into the review instead of a bare boolean.
  The two decision rules — `prefer_simpler` (comparable evidence → the
  lower score wins) and `complexity_growth_warning` (growth without better
  evidence) — are implemented, tested and documented in
  `docs/en/developers/strategy-complexity.md`, but **no screen calls them
  yet** (nothing compares two strategies side by side), so those two
  roadmap boxes stay open and the honest state is written in
  `ROADMAP.md` chapter 35. Unknown bounds are reported as unknown: a
  parameter with no range counts as one setting, and a rule's grid is `1`.

- **Chapter 29 (data quality management) closed.** `market_data/quality.py`
  now flags delisted assets (`DELISTED_ASSET`), detects structural liquidity
  changes (`LIQUIDITY_CHANGE`), records an explicit survivorship-bias note
  when composing datasets, and exposes `DatasetProvenance` so every research
  result records the exact dataset id, version and checksum. The optional
  research bar types (29.1) gained volume and dollar bars (`build_volume_bars`
  / `build_dollar_bars`); imbalance bars stay unsupported because candle
  aggregates lack trade-level pressure. `BacktestResult` now carries
  `dataset_id` / `dataset_version` / `dataset_checksum`, wired through
  `run_backtest_file`.

- **Chapters 62/63 (live monitoring / drift) advanced.** `live_vs_backtest.py`
  now models the full monitored state (`MonitoredState`: portfolio value,
  open/pending/executed orders, fees, slippage, drawdown, exposure,
  risk-manager decisions, connection state, data freshness, environment,
  kill-switch status, recent alerts) and derives beginner-readable alerts
  (`monitoring_alerts`) that surface an unarmed kill switch, a lost
  connection, or drawdown past 20%. Drift analysis gained the two remaining
  63.1 dimensions — `latency_drift` (expected vs actual fill latency) and
  `volatility_drift` (return volatility of the two equity curves, also a
  `volatility` key in `calculate_drift_metrics`) — plus `drift_education()`
  (63.3), which explains in plain language why backtest/paper/live never
  match exactly and which gaps are normal versus warning signs. Neither
  monitoring nor drift assessment ever touches the risk manager.

- **Chapter 33 initial strategies completed (items 2/3/4).** Added three educational strategies to `backtesting/engine.py` and registered them in `strategy_registry.py` (ids `rsi`, `breakout`, `bollinger`): `RSIStrategy` (Wilder RSI crossing the oversold/overbought levels, with optional volume and trend SMA filters and a post-exit cooldown), `RollingHighLowBreakoutStrategy` (buys a close above the rolling `period`-bar high, exits on a break below the rolling low), and `BollingerBandsMeanReversionStrategy` (buys a close crossing into the lower band, sells on recovery to the middle band). All follow the chapter-33 architecture: they emit `OrderSide` signals consumed by the engine, never touch the exchange, the risk manager, or credentials. `NullStrategy` (item 6) is also now marked done. New tests in `tests/backtesting/test_strategies_33.py` (13 cases); full suite passes.

- **A weekly check of the external URLs.** The offline link checker stops at
  the repository edge on purpose, so nothing noticed when an outside
  reference rotted. `tools/check_external_links.py` visits every `http(s)://` URL
  in the Markdown — skipping fenced blocks, inline code and `example.*` hosts,
  because two of the URLs here are meant to be unreachable — and classifies
  what came back. It runs in its own workflow, weekly and on demand, never
  on a push: a third-party outage must not turn a commit red, and the test
  job's offline determinism is a documented property. Its first live run
  showed that HEAD is not trustworthy — `www.workbuddy.ai` answered 404 to
  HEAD and 200 to GET for the same path — so a doubtful HEAD is now
  confirmed with a one-byte GET before a link is called broken. 38 URLs: 36
  ok, 2 accepted through `tools/external_links_allowlist.txt` (SSRN answers
  403 to every non-browser client, a browser User-Agent included); a 404 is
  never excused. 30 tests, none of which reach the network.
- **A checker for the references written inside docstrings.** The suite
  never reads prose and the Markdown link checker never opens a
  docstring, so a rename could leave Sphinx roles (`:class:`, `:func:`)
  and `docs/...md` paths pointing at nothing — the failure mode
  `check_doc_links.py` exists for, one layer in.
  `tools/check_docstring_refs.py`
  resolves both against the AST (no imports, so no optional dependency is
  needed), prints how many references it checked, and fails when it finds
  none, because a scanner that matches nothing is also broken. All 33
  roles and 71 Markdown paths in the package currently resolve. Wired
  into CI next to the link check.
- **Monthly candles can be downloaded and validated.** `1M` joins the
  downloader's vocabulary, and `validate_candles` checks it by calendar
  month instead of by a fixed step: February is 28 days and August is 31,
  so the old arithmetic called one an overlap and the other a gap.
  `CALENDAR_INTERVALS` names the intervals that need the calendar path,
  and the 30-day entry in `TIMEFRAMES` is now arithmetic only (volume
  scaling, size estimates). This also fixed `DatasetValidation.ok`, which
  ignored `issues` entirely — an off-grid or overlapping series was
  reported as "ready for research" while its problems were printed
  nowhere, because the explanation only lists issues when `ok` is false.
- **The GUI timeframe dropdown offers the exchange's intervals.** The
  Historical Data screen listed the six intervals the downloader knew; it
  now lists all sixteen intervals Binance serves, fastest first (`1s` …
  `1M`), and the default stays `1h`. Offering `1s` also made a real
  footgun reachable: a 1-second
  download over the default five-year range is about 157 million candles,
  and the old guard only fired after walking two million of them page by
  page. A request now estimates its size first and raises
  `DownloadTooLarge` with a plain-language explanation before the first
  network call.
- **`paper-live` accepts every interval Binance streams, including `1s`.**
  The live path validated against the historical downloader's curated
  `TIMEFRAMES` table, so `--interval 1s` was refused even though the
  exchange serves it. The exchange's own vocabulary now lives in
  `BINANCE_INTERVALS` (`exchanges/binance/config.py`), and the downloader
  adopted it later the same day. Fixing the validation exposed a second, silent
  defect: the chapter-56 volume proxy read the same table, so an interval
  it did not know produced zero average daily volume, an empty synthetic
  book and a rejection of every order. `interval_seconds()` now derives the
  duration from the interval string, and a test pins a 1s session that
  fills instead of rejecting.
- **The live session says when a strategy never warmed up.** A short
  `paper-live` run can end before the strategy has seen enough candles to
  emit its first signal, and the empty journal then looked like a flat
  market. Strategies now declare `warmup_candles` (`ma_crossover` reports
  `slow + 1`, buy-and-hold 1, a strategy that does not declare one reports
  0 and gets no warning), `PaperSessionResult.warmup_candles` carries it,
  and a session that received fewer candles than that adds a sentence to
  its note explaining why nothing happened. The CLI prints a `Warm-up:`
  line next to `Candles received:`. The warning is an explanation only: it
  does not change the account, the journal or the risk gate.
- **A working Binance WebSocket feed, and paper trading over it (chapters
  26.2 and 27).** The client existed but could not do its job: `start()`
  blocked forever, so a caller could never stop it; the staleness check ran
  *after* a message arrived, which is the one case where staleness is not a
  problem; connection renewal logged a line and kept the dead socket open;
  duplicate detection keyed on the event time across all streams, so a kline
  and a trade in the same millisecond looked like duplicates; ticker streams
  were never dispatched; and an empty client spun the CPU. All of that is
  fixed: `start()` schedules the runner and returns, a watchdog detects
  silence on a timer, renewal really closes and reopens the socket,
  deduplication is per stream (klines key on the event time so forming and
  closed updates both survive), ticker messages reach their handlers, a
  broken handler no longer kills the feed, and `stop()` cancels the real
  tasks. `run_paper_session_live()` now runs a bounded session and returns a
  coherent result: it used to await the blocking `start()`, so the timeout
  never fired; it wrote the journal into the current working directory on
  every candle; and it reported a default `PaperSessionConfig` whatever the
  caller asked for. Signals are no longer evaluated while the feed is
  DEGRADED (chapter 27) — those candles are buffered and counted in the
  note. New `crypto-trading-lab paper-live` command. **Fixed on the way:**
  the risk manager added every order's notional to the current exposure, so
  a sell that closes a long was rejected for exceeding the exposure limit —
  the gate could block the order that reduces risk. Exposure is now computed
  from the position the order leaves behind. 26 new tests; baseline 782 →
  **807 passed, 2 skipped**. Chapter 27 is `[x]`; every connection state now
  links to a real section of `docs/en/user-guide/20-troubleshooting.md`, and
  a test fails if a link or its anchor stops resolving.


- **Drift reporting (chapter 63.2).** A paper session is now judged against
  what its backtest predicted, not just compared to it. `expected_ranges()`
  builds the band each metric should stay inside: the return band comes from
  resampling the backtest's own trades, anchored on the return the run
  actually realised (the bootstrap sees closed trades only, while the run
  also holds open positions); the drawdown band is anchored on the observed
  drawdown and widened by a 1.5x tolerance, because a trade-level bootstrap
  cannot see the drawdown that happens inside a trade and would otherwise
  report a band of zero for any profitable run. Every band states its
  `basis`. `drift_over_time()` splits both equity curves into equal slices,
  so a run that drifts away in its last third no longer hides behind an
  average. `assess_drift()` returns a `StrategyHealth` verdict — healthy,
  suspicious or degraded — using four per-metric verdicts that separate a
  normal tail (outside the band by less than half its width) from real
  degradation, and treats a result *better* than the band as a warning
  about the model rather than good news. Each dimension carries a list of
  likely causes to check. A backtest with fewer than two trades produces no
  band, and the run is reported as unvalidated rather than healthy. The
  Paper Trading screen renders the whole analysis after every session; the
  assessment never touches the risk manager. 12 new tests; baseline 770 →
  **782 passed, 2 skipped**. Documented in
  `docs/en/developers/live-vs-backtest-drift.md`.


- **Execution realism now feeds the backtest and the robustness report, not
  only paper trading (chapter 56.5).** `BacktestConfig` gained
  `execution_config` and `execution_seed`; when a configuration is set,
  fills come from the chapter 56 synthetic order book whose depth is the
  traded volume of the candles *before* the fill candle, so an order larger
  than the modelled liquidity is partially filled and an order with no
  depth is rejected instead of being assumed away. Every run records the
  model and the seed in `config_metadata`; the CLI names the model and
  reports rejections and partial fills. The cost-model path is numerically
  unchanged. In robustness, `sweep_costs` scales the execution model's own
  slippage assumptions when realism is on (it also stopped dropping
  `position_fraction` and `execution_config`), and `compare_execution_models`
  adds an `execution_impact` section — baseline versus realistic, with the
  delta in profit and return — to every `RobustnessReport`. The report
  states the direction caveat: the cost model applies a fixed adverse
  slippage while chapter 56 draws from a symmetric band, so the realistic
  arm can come out cheaper, and that is not evidence of safety. 15 new
  tests; baseline 755 → **770 passed, 2 skipped**. Chapter 56 is `[x]`.
  Documented in `docs/en/developers/cli.md` and
  `docs/en/developers/unwired-modules-audit.md`.

- **A working command-line interface (chapter 22), and the shared use-case
  layer behind it.** The five subcommands that printed one line and returned
  `0` now do real work: `database check` runs SQLite's
  `PRAGMA integrity_check` and prints the schema version plus every table's
  row count (a missing database is reported as missing, not "passed");
  `import-csv` validates the file with the chapter 28 parser and only then
  creates the database; `backtest` loads stored candles and runs the
  chapter 37 engine with the chapter 40 metrics from a JSON or YAML
  configuration; `glossary search` parses the beginner glossary; and
  `list-lessons` reads the curriculum. The new
  `src/crypto_trading_lab/application.py` holds the use cases, and
  `MainWindow.load_csv_file` now calls the same `import_csv_file` the CLI
  does, so the two front ends cannot drift apart. `doctor` gained the
  twelve checks chapter 22 lists — connectivity and clock drift behind
  `--network`, so the suite stays offline — and never reads a credential
  store. 47 new tests (`tests/test_cli.py`, `tests/test_application.py`);
  baseline 707 → **755 passed, 2 skipped**. Documented in
  `docs/en/developers/cli.md`. YAML configurations read through PyYAML:
  the Debian package now depends on `python3-yaml`, pip users get it from
  `requirements-all.txt` or the new `yaml` extra, and JSON needs nothing
  extra.

- **The console script actually dispatches now.** `[project.scripts]`
  pointed at the GUI function, so an installed `crypto-trading-lab` ignored
  every argument and opened a window — `crypto-trading-lab doctor` hung.
  It points at `crypto_trading_lab.__main__:main`, which runs the CLI when
  there are arguments, the GUI otherwise, and imports Qt only on the GUI
  path. Found while measuring a clean virtualenv; two subprocess tests in
  `tests/test_cli.py` keep it fixed.

- **`PyYAML` in the Debian package and in `requirements-all.txt`.**
  `debian/control` now depends on `python3-yaml` (runtime and build), and
  `requirements-all.txt` lists `PyYAML>=6.0` so a machine without Debian
  packages gets the YAML backtest path in one install. `pyproject.toml`
  gained a `yaml` extra for the same reason.

- **The dead `Experiments/` references are gone.** The kit was deleted on
  2026-10-16 but the README, the handoff and the virtualenv guide still
  linked to it, so `tools/check_doc_links.py` failed in CI. The three links
  now point at `requirements-all.txt` and the manual `cross-platform`
  workflow; the checker reports zero broken links.

- **A clean virtualenv is measured, not assumed.** Section 8 of
  `docs/en/developers/venv-setup.md` records a fresh
  `python3 -m venv .venv` built from `requirements-all.txt`: PyYAML 6.0.3,
  PyQt6 6.11.0, SQLAlchemy 2.1.6, pytest 9.1.1, **755 passed, 2 skipped**,
  exit 0 — the same numbers as the system Python.

- **`tools/check_doc_links.py`, and a CI step that runs it.** The test suite
  never reads the documentation, so nothing caught broken links: five had
  accumulated in the README, three pointing at an anchor that never existed
  and two broken by a heading rename. The checker validates both halves —
  that a linked file exists, and that a `#fragment` matches a heading in the
  target — using GitHub's slug algorithm, and it is worth noting why that
  algorithm is easy to get wrong: GitHub emits one hyphen per space and does
  not collapse runs, so `## Contributing — bring your AI agent` is
  `#contributing--bring-your-ai-agent`. A checker that collapses whitespace
  reported five false positives here and buried the three real failures.
  Stdlib only, offline, no dependency; it is also a line in the definition of
  done in `CONTRIBUTING.md`.

- **A "What you get out of it" section in the README's contribution
  pitch.** The pitch sold the *mechanics* — a written specification, small
  PRs, an offline suite — but never the *domain*: that a contributor
  implements purged cross-validation, the deflated Sharpe ratio and
  triple-barrier labelling against written definitions, with eight major
  reference projects already studied so they do not have to. It also states
  the credit terms plainly, which the README did not mention at all: no CLA,
  no copyright assignment, GPL-3.0, attribution kept in git and the
  CHANGELOG.
- **An honesty signal in "The rules that keep this repository honest".**
  The CHANGELOG records that the suite once printed "passed" and then
  segfaulted, that CI had never been able to pass, and that an audit found
  16 modules wired to nothing. Pointing at that is a stronger invitation
  than a claim of perfection, and it is checkable.

- **`reference-projects.md` Parts E–H, completing ROADMAP chapter 25.**
  The four remaining references under `external/` are now studied and
  documented to the same evidence standard as Parts A–D — every claim tied
  to a file path, with the searches behind each negative recorded:
  - **Part E — Freqtrade** (GPLv3, inspiration only). Signals-as-data
    enforced by construction, dry-run as a run mode rather than a fork, and
    a documented list of what it does *not* provide (no walk-forward, Monte
    Carlo, cross-validation, out-of-sample split, risk-based sizing, kill
    switch, strategy identity, or dataset identity in hyperopt records).
  - **Part F — Hummingbot** (Apache-2.0, adaptable). The thin-subclass
    connector base, a richer exchange-rule model than CCXT's, the
    client-order-tracker recovery machinery, and an order-book query that
    *reports* insufficient depth instead of extrapolating.
  - **Part G — Jesse** (MIT, adaptable). Its stationary-bootstrap rule
    significance test is the strongest statistical artifact in any
    reference and the one mechanism to adapt for 43.2.
  - **Part H — TA-Lib** (BSD-3-Clause, adaptable). A 201-function catalog
    with machine-readable naming, parameter ranges and a documented
    streaming API that answers chapter 31's open incremental-updates item.
- **Three advertised claims were corrected by per-feature verification**,
  which is exactly what chapter 25 demanded: Jesse's optimization is random
  search with Optuna used only as a trial store (not "Optuna-driven"), its
  significance test is a stationary bootstrap (not "random-entry variants"),
  and its indicator catalog is 174 modules (not "300+"). Hummingbot's own
  README also describes three directories that do not exist.
- **A cross-reference finding worth keeping**: none of the six trading
  frameworks studied enforces its own limits. Freqtrade's protections only
  lock new entries and are opt-in, Hummingbot's kill switch ships
  `KillSwitchDisabledMode()` by default, and Jesse's sizing helpers are
  optional calls a strategy can bypass. That is the gap chapters 58–59 exist
  to close, now recorded in chapter 25 itself.

- `tests/market_data/test_quality.py`: the Chapter 29 data-quality
  framework (`market_data/quality.py`) now has an offline test suite —
  validation, stale/frozen rules, volume anomalies, configuration and
  report serialization.
- `tests/ui/test_accessibility.py` now verifies that the tab order is
  actually applied, and that a cross-window call fails loudly.
- `CODE_OF_CONDUCT.md`, `CHANGELOG.md` and `.gitattributes` so a fork
  inherits community rules, a change history and consistent line
  endings.
- `invalid_count` is accepted by `create_quality_report()` and
  `validate_dataset_quality()`, so rejected raw rows are reported as an
  `INVALID_OHLCV` error instead of being dropped silently.
- Missing `__init__.py` files for `crypto_trading_lab.machine_learning`,
  `crypto_trading_lab.testing` and `crypto_trading_lab.monitoring`.
  Without them `setuptools.find_packages()` omitted those packages from
  a built distribution (27 → 30 packages discovered).
- The `integration` pytest marker is declared in `pyproject.toml`.
- `docs/en/developers/unwired-modules-audit.md`: a per-module audit of the
  16 modules that no product path imports, with an explicit
  delete / merge / wire disposition for each.
- The chapter-56 execution model is now wired into paper trading:
  `paper_session.run_paper_session` and `run_paper_session_live` call
  `simulate_market_order` for entries and exits. `PaperSessionConfig` and
  `LivePaperConfig` gained a `seed`, `execution_realism` gained
  `synthetic_order_book()` / `simulate_market_order()` and an injectable
  `random.Random`, and `tests/test_execution_realism.py` adds 15 tests.
- Chapter 53 reproducibility is now wired into research records:
  `ExperimentManager.create()` fills `code_hash` from the source and
  attaches a compact `environment` (Python, platform, git revision,
  dependency versions) to every `ExperimentRecord`, which round-trips
  through `update_status`, notes, tags and `save`/`load`.
  `reproducibility` gained `environment_summary()`,
  `capture_environment(include_packages=...)` and a cached dependency scan;
  `tests/test_reproducibility.py` adds 12 tests.
- Chapter 63 drift is now wired to the Paper Trading screen:
  `live_vs_backtest` gained `drift_report_from_results()` and
  `render_drift_report()`, and every paper session is compared with the
  same strategy's backtest at the same sizing. `BacktestConfig` gained
  `position_fraction` (default `1`, so existing backtests are unchanged);
  it is recorded in `metadata()` and `tests/test_live_vs_backtest.py` adds
  10 tests.
- Chapter 72 ethics now guards report generation: `reporting/ethics.py`
  holds `EthicsChecker` + `STANDARD_DISCLAIMERS`, and every HTML/CSV/JSON
  report carries the five mandatory disclaimers plus explicit
  **Assumptions** and **Limitations** sections. `audit_report_ethics()`
  raises `EthicsError` on a violation (missing disclaimer, profit-guarantee
  language) and attaches warnings for omissions;
  `tests/reporting/test_report_ethics.py` adds 11 tests.
- Chapter 60 position sizing is implemented and reachable:
  `robustness.kelly_fraction()`, `optimal_bet_size()` (half-Kelly by
  default, capped by `PositionSizingConfig`) and
  `position_size_from_trades()`, which derives the edge from the backtest's
  own trades and returns 0 **with a warning** when the sample is too small,
  degenerate or edgeless. `RiskOfRuinReport` gained
  `recommended_risk_per_trade` and `ResearchRun` carries it to the research
  output. `tests/backtesting/test_risk_of_ruin.py` adds 15 tests.
- `docs/en/developers/venv-setup.md`: the complete virtualenv guide —
  every dependency under its Debian **and** PyPI name, both venv routes
  (`--system-site-packages` over the Debian Qt stack, or fully isolated),
  run/test commands, troubleshooting, and how to decide whether `ccxt` is
  worth adopting. `pyproject.toml` gained the `pdf` extra, and
  `tools/evaluate_ccxt.py` is a read-only script that
  reports ccxt's coverage and whether the project's adapter accepts a real
  client. Section 7 of that guide records the **measured** evaluation: ccxt
  4.5.84, 104 exchanges, Binance and Coinbase both exposing the required
  surface, `fetch_candles()` returning normalised Decimal+UTC candles from
  **both** exchanges over the network, and the suite passing inside the venv
  (698 passed, 2 skipped). Verdict: ccxt is worth adopting for chapter 26.3
  because it is the only path to a second exchange.
- Cross-platform pip installation: the four runtime packages are now
  declared in `[project.dependencies]`, so a plain `pip install .` works on
  Linux, macOS and Windows instead of installing nothing; `keyring` moved to
  a `credentials` extra. The README gained per-platform tutorials (Linux,
  macOS, Windows) covering the PowerShell execution-policy error and its
  safe per-session fix, and clearly marking Windows/macOS as **not yet
  verified**. `.github/workflows/cross-platform.yml` runs the suite on
  Ubuntu, macOS and Windows — `workflow_dispatch` only, so it can never
  redden the default CI.
- `Experiments/`: a self-contained verification kit for machines without
  Debian packages. `requirements-all.txt` lists every dependency (including
  `ccxt`), `setup_windows.bat` and `run_verify.cmd` do the setup in `cmd.exe`
  so PowerShell's execution policy is never involved, `verify.py` runs twelve
  checks (imports, CSV import, backtest, paper trading, the offscreen Qt
  window, the ccxt adapter) with optional `--tests`, `--gui` and `--network`
  stages and writes `verify-report.md`, and `CHECKLIST.md` is a tick-box
  manual to fill in and return. A 400-candle sample dataset lets the whole
  pipeline be exercised with no network. The generated report is
  git-ignored.
- **Windows 10 verified (2026-10-01).** The kit was taken to a real
  Windows 10 machine (10.0.19045, AMD64) with Python **3.14.7** and
  every package installed from PyPI: the virtualenv and `pip install`
  worked, the PowerShell activation error appeared and the documented
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` cleared
  it, the application window opened, CSV import / backtest / paper
  trading produced numbers *identical* to Debian, and `ccxt` reached
  the network. The raw PowerShell transcript is kept in
  `Experiments/20261001-resultado-de-la-instalacion-en-Windows-10.txt`.
  The run also exposed the segmentation fault fixed below. macOS
  remains unverified.

### Changed
- **Chapter 66 (strategy qualification) is now [x].** All fourteen 66.1 criteria are evaluated where applicable (out-of-sample, drawdown, risk-adjusted, benchmark, sample size, parameter stability, robustness, walk-forward, paper trading, execution realism, data quality, complexity, statistical evidence, operational stability). Qualify produces Qualified / Conditionally Qualified / Not Qualified, lists the conditions or explains the failed criteria, stores the report (66.2) via save_qualification_report, and computes a re-qualification due date (66.3, default 90 days). Tests extended in tests/test_qualification.py.
- **Chapter 64 (strategy failure detection) is now [x].** Detection (64.1) covers all seven signals: return degradation, drawdown, execution (fill/win) degradation, volatility change, trade-distribution change, regime change and data-quality problems. The new recommendation engine (64.2) maps recorded alerts to Continue / Monitor / Reduce exposure / Pause / Retire with the reasons and the data plus thresholds shown, never guesses, never bypasses the risk manager, and a Retire can update the strategy registry through a callback. Chapter 64.3 education text is included. Tests extended in tests/monitoring/test_failure_detection.py.
- **Chapter 67 (safety gates) is now [x].** The gate layer gained an Environment model (the five environments from 67.2), all eleven pre-trade checks (environment, exchange, account, balances, market-data freshness, order parameters, market constraints, risk/position/exposure limits, kill-switch, connection), a non-bypassable evaluate_order that runs every gate on each order, and explicit-confirmation guards so importing a configuration or a UI action can never silently move into a riskier environment. Real Trading stays disabled unless explicitly enabled. Tests extended in tests/test_safety_gates.py.
- **ROADMAP packaging chapters were physically renumbered 15/16/18 → 81/82/83.** The scientific pipeline (LEARN → … → CONSIDER REAL TRADING) now owns chapters 1–80; packaging was appended as PART XVII (81 Python packaging, 82 Debian package, 83 AppImage) and tagged deferred until the loop runs. All prose cross-references in README, AGENTS, AGENT-HANDOFF, CONTRIBUTING, the developer docs, the exchange-adapter ADR and `conftest.py` were updated. The AFML *book* chapter references in `reference-projects.md` were deliberately left unchanged — they are bibliographic, not roadmap, chapters.
- **Three internal README links were pointing at an anchor that does not
  exist.** They said `#what-is-not-verified` while the heading is "What is
  verified, and what is not". Renaming the `## Quick start` heading also
  silently broke the two `#quick-start` links to it. Neither kind of breakage
  fails anything: the test suite never reads the README, and a link checker
  that only verifies that files exist will not look inside `#fragments`.
  Both were found by writing the anchor check, and the corrected checker
  algorithm is recorded here because it is easy to get wrong: GitHub emits
  **one hyphen per space and does not collapse runs**, so
  "Contributing — bring your AI agent" becomes
  `#contributing--bring-your-ai-agent`, not `#contributing-bring-your-ai-agent`.
- **The README's install instructions are now one section instead of two.**
  A "Start here — pick your platform" block had been added near the top with
  Debian, macOS and Windows commands, but it duplicated what the Quick start
  and "Install with pip" sections already said further down. It has been
  removed and its two genuinely unique pieces folded into the Quick start,
  which is the section that survives.
- **The Quick start's `apt` list was installing too little to reach the
  baseline it advertises.** It promised `707 passed, 2 skipped` but omitted
  `python3-pytestqt` and `python3-pypdf`. Without `pytest-qt` the five
  accessibility tests **error** rather than skip — verified by disabling the
  plugin: `2 passed, 5 errors`, exit 1 — and without `pypdf` the chapter-41
  export test skips, making the count 3. Both packages are now in the list,
  and the section explains why each one matters, since neither failure looks
  like a missing dependency. The same `dev`+`pdf` pairing is now stated for
  the pip route, where installing `".[dev]"` alone has the identical effect.
- **ROADMAP chapter 25 (reference projects) is closed: `[x]`, 13 boxes
  ticked, 0 open.** It had been `[ ]` with every box reading as undone even
  though four studies were already concluded and documented
  (`reference-projects.md` Parts A–D), so a reader would have concluded that
  nothing had been studied. The remaining four were finished on 2026-10-15
  (Parts E–H), and the chapter's closing requirement — document the
  conclusions — is now met.
- **`external/` is therefore removable.** The chapter's deliverable is the
  study and its written conclusions, not the vendored copies; nothing in
  `src/`, `tests/`, `pyproject.toml` or `Makefile` references `external/`,
  and both CI workflows pass `submodules: false`. The 12 GB release
  procedure is in `reference-projects.md` → "Disk cost, and what can now be
  removed"; it was tested end-to-end and is reversible.
- **The disk cost of `external/` is documented and measured**: not 930 MB but
  **12 GB** — 11 GB of git object store, 8.5 GB of it `ccxt`. The README and
  `CONTRIBUTING.md` had invited contributors to run
  `git submodule update --init --recursive`, which downloads all of it; they
  now state the real size and recommend fetching only the reference a task
  is about.
- **macOS verification is deferred to the end of development** by the
  maintainer's decision, after Linux and Windows. The `README.md` (agent
  prompt, good-first-contributions, "What is not verified"), the
  `Experiments/` kit, `AGENT-HANDOFF.md`, the virtualenv guide and the
  manual `cross-platform` workflow all say so now, so a contributing agent
  does not pick macOS up as the next task and does not read a red macOS job
  as a blocker.
- The documented test baseline was refreshed from the stale `702`/`704` to
  the measured **707 passed, 2 skipped** in the `README.md` badge and
  tutorials, `AGENTS.md`, `AGENT-HANDOFF.md`, `CONTRIBUTING.md`, the pull
  request template, `docs/en/developers/`, the `Makefile` and the
  `tests.yml` comment. `AGENTS.md` rule 2 no longer claims that no virtual
  environment has ever been needed, which had been false since the extras
  (`ccxt`, `pypdf`, `keyring`, `aiohttp`, `websockets`) were documented.
- **The GitHub Actions were moved to Node 24**: `actions/checkout@v4` → `@v5`
  and `actions/setup-python@v5` → `@v6`. GitHub had started force-running the
  old majors on Node 24 and annotating every run with the deprecation. Run
  [38777456963](https://github.com/wachin/crypto-trading-lab/actions/runs/38777456963)
  verifies the bump: `707 passed, 2 skipped` and no annotations.
- **The `tests` workflow now passes on `main`.** It had never been able to:
  run
  [38772811163](https://github.com/wachin/crypto-trading-lab/actions/runs/38772811163)
  was the first green build, and
  [38777456963](https://github.com/wachin/crypto-trading-lab/actions/runs/38777456963)
  repeats it, reporting the same counts as Debian (SQLAlchemy 2.1.4, pypdf
  installed, so the chapter-41 export test runs instead of skipping).

### Fixed
- **The suite was green on Debian and red on Windows (990 passed vs 988
  passed, 2 failed).** Two platform assumptions, both now removed — the
  second one hid in two tests.
  `tools/check_external_links.py` (and its sibling `check_doc_links.py`)
  sorted Markdown files by `Path`, and Windows compares paths
  case-insensitively, so the report listed `docs/guide.md` before
  `README.md` where Linux lists them the other way round; both now sort by
  the POSIX relative path, which reads the same everywhere.
  `test_renewal_really_closes_and_reconnects` waited for a connection
  renewal by polling 100 times with `asyncio.sleep(0.01)`, but the Windows
  event-loop clock advances only every 15.6 ms, so those sleeps can all
  return early and the loop finished before the 30 ms renewal interval had
  elapsed — the test now waits on an event the socket factory sets, with a
  5 s timeout, and still fails if renewal breaks (verified by running it
  with `renewal_interval=3600`).
  `test_stale_data_is_detected_without_waiting_for_a_message` had the same
  defect one run later (it passed, then failed, with no code change in
  between): it polled 50 times for the watchdog, and a polling loop that
  finishes before the timer has ticked asserts the opposite of what it
  means. It now waits on the "degraded" warning itself, same 5 s timeout.
  The feed also measured the connection age with `time.time()`, which an
  NTP correction can move backwards and so delay or skip a renewal; it now
  uses `time.monotonic()`.
- **`create_order` rejected every order it was given.** `_validate_order_request`
  accepted an optional `market`, but `create_order` never passed one, and
  the guard `if request.symbol != market.symbol if market else True:`
  parses as `(request.symbol != market.symbol) if market else True` — with
  `market=None` it is always true, so every order raised
  `AdapterInvalidOrder("symbol does not match market")`. `create_order` now
  resolves the market from `exchangeInfo` (fetched once, then cached on the
  adapter) and validates against it, so the tick-size, step-size,
  minimum-quantity and minimum-notional checks chapter 30 asks for actually
  run. Two more defects sat on the same path: a market order was rejected
  for having no price to compare the minimum order value against (it now
  leaves that check to the exchange), and step/tick precision was parsed
  with `int("0.00001000".split('.')[-1])`, which reads Binance's padded
  `0.00001000` as 1000 — `_decimal_places` normalizes the value first. The
  old behaviour failed closed, so no order was ever sent; chapter 68 was
  blocked on it.
- **A re-import could silently drop a candle of another interval.**
  `CandleRepository.save_candles(replace=False)` built its "already
  stored" set from the first candle's interval but keyed it by
  `open_time` alone, so a new 5m candle was skipped whenever a stored 1m
  candle shared its open_time: a mixed-interval batch reported 0 rows and
  wrote nothing. The skip now uses the full (market, interval,
  open_time) key — the same key as the table's unique constraint — and
  the docstring says what the returned count means. Both call sites pass
  `replace=True`, so no stored dataset was affected. The persistence
  suite now also covers the ordering of `list_datasets`/`latest`, UTC
  round-trips, empty batches, the auto-created exchange row and the
  legacy rows without a timezone suffix; the package is at 100% branch
  coverage from `tests/persistence/` alone.
- **The probabilistic Sharpe ratio mixed two frequencies.** It divided
  annualized return by annualized volatility and then fed that
  *annualized* ratio to `sqrt((1 + SR²/2) / T)` with `T` counted per
  candle — the "annualization trap" already recorded in
  `afml-techniques.md`. It now takes `periods_per_year` and de-annualizes
  the ratio first: a one-year daily run with a true per-period Sharpe of
  0.10 returns p ≈ 0.028 instead of p = 0.000. Nothing in the application
  called it yet, so no shipped number changed.
- **Portfolio metrics used a 252-day year and a return-space drawdown.**
  `compute_portfolio_metrics` assumed 252 equity-market trading days for
  every series (a daily crypto Sharpe was understated by sqrt(365/252)),
  annualized arithmetically from the sum of returns, and measured the
  drawdown on the returns themselves — a series of 1% returns reported a
  50% drawdown. It now takes `periods_per_year` (default 365), compounds
  the returns into an equity curve, annualizes geometrically and measures
  the drawdown on that curve. Test-only today.
- **A valid annualized Sharpe needs market time, not just rows.** With
  the periods per year derived from the interval, the same 30-observation
  series reports a Sharpe of 181 at 1m and 0.87 at 1M — both marked
  "valid", because the gate only counted observations. Thirty one-minute
  candles are half an hour. `MetricConfig.min_span_days` (30) now also
  gates Sharpe/Sortino validity, the warning says how many days the run
  covers, and the CLI marks the number the way the GUI already did
  ("descriptive only, not statistically supported") instead of printing
  it bare.
- **Stored metrics carry the assumptions they were computed under.**
  `ExperimentRecord.metric_config` holds the chapter 40.7 record
  (periodicity, annualization method, span rule), the exported report
  states it in its assumptions, and both survive a reload. Without it a
  saved Sharpe cannot be compared with one computed at another interval.
- **Annualized metrics no longer assume every candle is a day.**
  `MetricConfig.periods_per_year` defaulted to 365 and no call site ever
  overrode it, so an hourly run annualized after 365 candles — 15 days —
  and reported that as a yearly return (volatility understated by about
  4.9x, return by 24x). Monthly candles made it worse: a monthly run
  needed 30 years of candles before annualizing at all, and at 365 of
  them it labelled the 30-year total as one year's return. The run now
  records its interval (`BacktestResult.interval`), and
  `MetricConfig.for_interval` derives the periods per year from it —
  365 daily, 8,760 hourly, 12 monthly (counted by definition, not by
  dividing 365 by an approximate month). A run that does not record its
  interval keeps the daily default and says so in the report's warnings.
- **`StrategyRegistry` wrote to disk as a side effect of being built.**
  Its constructor created `data/strategy_registry/registry.json` under the
  *current working directory* — including the source tree — and did it for
  every registry, even one only used to list strategies. It also had a
  `_load()` that was never called, so the persistence was write-only: the
  file was written on every `register()` and never read back. The
  constructor no longer touches the filesystem, the load path runs, and
  built-in strategies keep the Python factories that JSON cannot carry;
  entries restored from JSON come back as metadata only and
  `get_factory()` says so. `StrategyRegistry(storage_path=...)` is
  unchanged for callers.
- **The Backtesting Lab could run a backtest with `None`.** The new
  registry lookup replaced the old `NullStrategy()` fallback, so an
  unregistered or metadata-only strategy id reached
  `run_backtest(candles, None, config)` and failed far from the cause. The
  widget now stops with a message naming the problem, and only offers
  strategies that can actually be instantiated.
- The strategy selector lost its translatable labels when it started
  reading the registry: it showed the raw registry names ("Ma Crossover")
  built at runtime, which `pylupdate6` cannot extract. The labels are
  literal `self.tr()` strings again, with the registry name only as a
  fallback for strategies registered by other code (chapter 36).
- **The CI had never been able to pass.** `tests.yml` ran on
  `ubuntu-24.04`, whose `python3-sqlalchemy` is **1.4**, while the code
  needs 2.0 (`DeclarativeBase`): every build died with an `ImportError`
  during collection. The workflow now installs with pip in a venv, the
  path the README documents, and `cross-platform.yml` additionally runs
  Ubuntu, macOS and Windows manually.
- The manual `cross-platform` workflow itself failed on all three
  systems on its first run because it wrote `VENV_PY` to `$GITHUB_ENV`
  and then used `$VENV_PY` **in the same step** (GITHUB_ENV only applies
  to later steps), so the command expanded to nothing and exited 127.
- Both workflows installed `".[dev]"`, so the chapter 41 PDF export test
  was skipped in CI (`could not import 'pypdf'`) and the CI baseline no
  longer matched the documented one. They install `".[dev,pdf]"` now,
  the same set the README documents.
- `tests/exchanges/test_binance_adapter.py` reached the real Binance
  endpoint to prove that trading is refused when it is enabled, which
  made the suite fail with `HTTP 451` on GitHub's runners. It patches
  `_make_signed_request` instead; the whole suite now passes with a bogus
  proxy, which is the offline guarantee the project claims.

- **The test suite segfaulted when the interpreter exited.** Every test
  passed (`698 passed, 2 skipped`) and then the process died with SIGSEGV,
  so the exit code was non-zero and `make test`/CI reported failure. Found by
  the Windows 10 verification run and reproduced on Linux; the cause was
  `trading.py`: chapter 68's safety logic imported `PyQt6.QtCore`, and
  `RealTradingManager.deactivate()` called `self.__init__()` on a `QObject`,
  which is undefined behaviour with sip. The suite now exits `0`
  (707 passed, 2 skipped).
- `trading.py` no longer depends on Qt at all: `RealTradingManager` is a
  plain class, the UI subscribes through the existing `add_observer` API,
  and a regression test asserts that importing the module pulls in no
  `PyQt6`. That keeps chapter 68 safety logic importable headless, as
  chapter 6.1 requires.
- State changes now actually notify: `set_state()` was never called by the
  activation, suspension or deactivation paths, so the main window's
  "REAL TRADING" indicator could never update. Those paths call
  `set_state()` now, and observers receive `(state, message)`.
- `venv-setup.md` now explains the two messages a `pip install` prints
  inside a `--system-site-packages` venv: `Not uninstalling X … outside
  environment` (pip correctly refusing to modify the Debian packages) and
  `ERROR: pip's dependency resolver … weasyprint … html5lib` (a conflict in
  a *system* package this project does not use; the install still succeeds
  and pip exits 0).
- The documented test baseline had been left at **683 passed, 2 skipped**
  in ten places (the README badge and body, `AGENTS.md`,
  `AGENT-HANDOFF.md`, `CONTRIBUTING.md`, `Makefile`, the pull-request
  template and the developer docs) after the chapter-60 turn: a previous
  update used the wrong search value and silently changed nothing. It is
  **698 passed, 2 skipped**.
- `README.md` no longer states the blanket "No virtualenv, no `pip install`,
  no network"; the Debian-first default is unchanged, and the PyPI-only
  path is documented separately in `venv-setup.md`. `CONTRIBUTING.md` and
  `debian-dependencies.md` say the same thing instead of "no virtualenv".
- `render_pdf()` was broken: it called `PdfWriter._addObject` /
  `_writeObject` / `.stream`, private names that pypdf 5 removed, so every
  PDF export raised `AttributeError`. It now builds the document with the
  current API, escapes PDF string delimiters that a strategy name could
  inject, and returns bytes.
- The ethics checker only matched the underscore spelling of
  "out_of_sample", so the normal English "out-of-sample" was reported as
  missing.
- `live_vs_backtest.calculate_regime_drift()` put the **live** return into
  the backtest bucket, so per-regime drift was always exactly zero. It also
  silently truncated mismatched inputs; it now raises.
- `calculate_drift_metrics()` iterated a `set`, so metric order and the
  report were non-deterministic, and a zero backtest baseline was reported
  as "no drift" instead of material.
- `analyze_execution_drift()` computed fill rates with float division,
  leaking binary floating point into a money-adjacent report.
- The drift bridge cannot mistake position sizing for drift: the backtest
  engine invested 100 % of cash while the paper session uses
  `position_fraction`, so returns now require matched sizing and a mismatch
  is reported as a `SIZING MISMATCH` warning rather than a fake drift.
- `reproducibility.compute_code_hash()` walked the **relative** path
  `"src"`, so running the app or the tests from any other directory hashed
  nothing and returned the SHA-256 of the empty string (`e3b0c442…`). It is
  now cwd-independent.
- `capture_environment()` stored the **values** of every `CRYPTO_*` /
  `TRADING_*` environment variable, so an API key present in the
  environment would have been written in clear text into
  `experiments.json`. Variables whose name looks like a credential are now
  recorded as `***` (chapter 9 / threat model).
- `reproducibility` no longer uses the deprecated `pkg_resources`; the
  dependency scan uses `importlib.metadata` and is cached per process
  (~520 ms per call before).
- Chapter 56's model was inert: `paper_session` imported
  `simulate_execution` and never called it, so an `execution_config` only
  changed one `impact_factor` term and partial fills came from an
  **unseeded** `random.random()`, making paper-trading runs
  non-reproducible. Seeds now make a session reproducible, and an order
  larger than the modelled liquidity is partially filled or rejected
  instead of being assumed away.
- `simulate_execution` computed its slippage price and then discarded it,
  returning the raw book-ladder average and reporting market impact in the
  `slippage_bps` field. The slippage model now sets the price and the
  reported slippage.
- `calculate_slippage` could return **favourable** slippage — the random
  term could push the total negative, so a buy filled below mid. Slippage
  is now clamped to be adverse, as slippage is by definition.
- `run_paper_session_live` divided the P/L of a partial exit incorrectly
  and always recorded `entry.slippage = 0` because it read `position`
  after zeroing it.

- `create_quality_report()` raised `TypeError` because it indexed the
  `DataQualityReport` returned by `validate_dataset_quality()`
  (`report[0]`).
- `DataQualityValidator` no longer mislabels missing, duplicate or
  invalid-row counts as `GRID_ALIGNMENT` warnings; only genuinely
  off-grid timestamps get that code.
- Keyboard tab order set by `MainWindow` had no effect: it was applied
  before the buttons shared a top-level window, which Qt silently
  ignores. The call now runs after `setCentralWidget()`, and
  `AccessibilityHelper.set_tab_order()` raises `ValueError` instead of
  pretending when widgets live in different windows.
- `machine_learning/strategies.py` was deleted (see Removed); earlier in
  this batch it had an unused `scipy` import, a `NameError` in
  `evaluate_ensemble()` (`report` → `performance`) and duplicate `__all__`.
- `features.py` no longer declares `compute_asset_correlations()` with a
  bare `except:` next to an `import scipy.stats` the project does not
  ship (see Removed).
- `setup.py` duplicated metadata from `pyproject.toml` and disagreed
  with it (different dependencies, missing packages). It is now a
  metadata-free shim, and the license is declared with the SPDX
  expression `GPL-3.0-only` instead of the deprecated TOML table.
- `pyproject.toml` package data now includes the Learning Center
  tutorial figures, so an installed copy can display them.
- `media-generation/README.md` and `generate_tutorial_images.py` no
  longer hard-code the maintainer's `/home/wachin/...` path.
- Documented test baseline corrected to **698 passed, 2 skipped**
  across `README.md`, `AGENTS.md`, `AGENT-HANDOFF.md`,
  `CONTRIBUTING.md`, `Makefile`, the pull-request template and the
  developer docs. It had drifted between 229, 415, 522, 599 and 611.
- `AGENTS.md` "Current position" no longer claims the project is at
  chapter 40; that chapter is implemented.
- `ROADMAP.md` header rewritten as an English specification preamble
  instead of an audit report about a file that is not in the repository.

### Removed

- **`hypothesis` and `typeguard` are no longer declared dependencies.** Both
  sat in the `dev` extra and neither was used: no test imported them, pytest
  was never configured to activate them, and the ROADMAP names neither.
  `typeguard` was dropped outright — chapter 4.7 assigns type checking to
  `mypy`, which is static, and a second runtime checker has no home here.
  `hypothesis` may return: the README invites property-based tests, and a
  financial engine has invariants worth fuzzing (drawdown never negative, a
  strategy never exceeding its exposure cap, an equity curve round-tripping
  through the ledger). The reasoning lives in `venv-setup.md` rather than in
  `pyproject.toml` alone, so whoever picks that work up finds it.
- **`GENESIS.md`.** It was the Phase 0 bootstrap instruction written when
  the repository was empty, and every deliverable it ordered now exists
  (the dependency research, the architecture proposal, the threat model,
  the seven ADRs and the first beginner guides), so it had become a second,
  partly contradictory onboarding list: the README told contributors to
  read four files while `AGENTS.md` told agents to also read `GENESIS.md`.
  Two rules in it existed nowhere else and moved into `AGENTS.md` first —
  *silence is not approval*, and *build only what the task needs, never
  empty stubs mirroring the planned architecture* — along with the project's
  one-sentence creed. `AGENTS.md` rule 2 no longer points at it.
- Obsolete root-level scratch files (translation scripts, an orphan
  JSON Schema and internal audit/plan notes). They are preserved
  locally under `.scratch/`, which is git-ignored.
- The archived `numba-vs-decimal` benchmark script, which imported the
  deleted `performance/numba_accel` module. The decision record it
  supported is kept in `docs/en/developers/benchmarks/README.md`.
- Dead chapter-51 portfolio code that had been pasted into
  `market_data/features.py` (`portfolio_backtest`,
  `compute_asset_correlations`, `compute_portfolio_metrics` and three
  unused warning constants). It duplicated the tested `portfolio.py`,
  was imported nowhere, and its correlation function needed `scipy` plus
  a bare `except:`.
- Nine unwired modules that no product path and no test imported
  (2,317 lines). Each was either a duplicate of a tested module, a
  re-statement of a markdown document, or non-functional; every decision
  and its evidence is recorded in
  `docs/en/developers/unwired-modules-audit.md`:
  `benchmarking.py` (42), `live_monitoring.py` (62, non-functional),
  `research_notebooks.py` (54), `capital_protection.py` (61),
  `working_method.py` (70), `development_phases.py` (69, raised
  `KeyError`), `infrastructure/performance.py` (13),
  `ui/charts/qt_websocket_client.py` (4.2) and
  `machine_learning/strategies.py` (48).
  `ROADMAP.md` §4.4 item 3 was corrected accordingly.
- `research_ethics.py` (chapter 72), after merging its checker into
  `reporting/ethics.py`. The unused `EvidenceLevel`, `EvidenceLabel`,
  `generate_evidence_label`, `format_evidence_label`,
  `WarningType` and `EthicalWarning` were dropped instead of carried over
  as dead weight; the evidence ladder already lives in
  `reporting/report.py` and `ui/research/validity.py`.
- `risk_of_ruin.py` (chapter 60), after merging its Kelly sizing into
  `backtesting/robustness.py`. Its closed-form ruin formulas
  (`risk_of_ruin_binomial`, `risk_of_ruin_diffusion`),
  `capital_depletion_path` and `sequential_risk_of_ruin` were **not**
  ported: they mix units, multiply a per-trade expectancy by 100/50 and
  present it as an "expected/median drawdown", or return 0/1 while claiming
  to be a probability. The Monte-Carlo estimate that already exists is more
  defensible.
- The whole `exchanges/coinbase/` package (chapter 26.3): the native
  adapter and its endpoint config. Nothing imported either; the WebSocket
  client was a placeholder, `stop()` was declared twice so the synchronous
  definition silently overrode the async one, and the REST path recorded
  circuit-breaker *successes before the request*, so the breaker could never
  open. `ROADMAP.md` §26.3 and `docs/en/developers/live-trading-roadmap.md`
  were corrected to state that Coinbase is **not implemented**; the sandbox
  warning the config carried is preserved in the roadmap text.

