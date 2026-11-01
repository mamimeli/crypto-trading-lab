# ROADMAP — the specification

Crypto Trading Lab is built specification-first: this file is the
contract every contribution is measured against. It is organised as 83
chapters grouped into 17 parts. Read the chapter that owns your task
before writing code, and tick a checkbox only when the requirement is
**implemented and tested**.

> **Status legend**
> - `[x]` — implemented and tested; the chapter has no open subtask and no explicit "pending" note.
> - `[~]` — partially implemented, or a `[ ]` subtask remains, or the chapter carries an explicit "pending" note.
> - `[ ]` — not implemented.
>
> `[~]` does **not** mean the chapter is wrong; it means it is not closed
> yet. See `CONTRIBUTING.md` §4 for the ground rules.
>
> In the overview table, **Open** counts both `[ ]` and `[~]` items: a
> partially-done item is still open work. As of 2026-10-28 no `[~]`
> subtask remains, so every open item is a plain `[ ]`.

> **Honesty rule:** a chapter is never marked `[x]` because a header once
> said so — the checkbox tracks evidence, not intention. When a
> requirement is ambiguous, stop and say so instead of guessing.

## Delivery sequencing — finish the loop before packaging


This roadmap is organised **by topic** (the sixteen parts), but the work is
**delivered as one working scientific loop**. The priority order is the loop
below, not the chapter numbers. Packaging (chapters 81, 82, 83) is explicitly
deferred until the loop runs end to end on real-ish data — shipping an
installer for a program whose core loop does not yet close would hide the real
work behind a package.

> **Priority rule:** finish the loop first. A chapter numbered lower than a
> packaging chapter is not necessarily earlier to build; the loop order below
> is the authority for *what to do next*. Packaging stays `[ ]` until the loop
> is operational.

The loop, in order:

```
              CRYPTO TRADING LAB

                    ↓
              LEARN
                    ↓
             CHOOSE MARKET
                    ↓
              GET DATA
                    ↓
            FORM AN IDEA
                    ↓
          WRITE A HYPOTHESIS
                    ↓
              BACKTEST
                    ↓
              ANALYSE
                    ↓
           TRY TO REFUTE IT
                    ↓
          OOS / WALK-FORWARD
                    ↓
             ROBUSTNESS
                    ↓
            PAPER TRADING
                    ↓
            QUALIFICATION
                    ↓
               TESTNET
                    ↓
        ┌──────────────────┐
        │ Is there evidence │
        │ of an edge?       │
        └──────────────────┘
                  ↓
            ONLY IF THERE IS
                  ↓
        CONSIDER REAL TRADING
```

How the loop maps to the chapters (the loop is the priority; the chapter
numbers are just the spec's identifiers — see the Status overview by chapter
for the exact `[x]` / `[~]` / `[ ]` of each):

| Loop stage | Primary chapters |
|---|---|
| Learn | 1, 2, 23, 24, 80 |
| Choose market | 3, 30, 33 |
| Get data | 26, 28, 29, 73 |
| Form an idea | 33, 34, 35 |
| Write a hypothesis | 43, 53, 74 |
| Backtest | 37, 38 |
| Analyse | 40, 41, 42 |
| Try to refute it | 43, 44 |
| OOS / walk-forward | 38, 45 |
| Robustness | 44, 46, 47 |
| Paper trading | 57, 79 |
| Qualification | 65, 66 |
| Testnet | 68 |
| Evidence-of-edge gate | 43, 74 |
| Consider real trading | 67, 68 |

**Deferred until the loop runs:** chapters 81 (Python packaging), 82 (Debian
package) and 83 (AppImage). They are intentionally left `[ ]`; do not start
them until every stage above is operational on real-ish data. The recommended
task order is in `AGENT-HANDOFF.md` §5.2.

## Status overview by chapter

| Ch. | Status | `[x]` inside | Open inside | Explicit pending note | Topic |
|---:|:---:|---:|---:|:---:|---|
| 1 | [ ] | 0 | 33 | No | Project purpose and scientific principles |
| 2 | [ ] | 0 | 26 | No | Terminology and conventions |
| 3 | [~] | 2 | 17 | No | Supported platforms and technologies |
| 4 | [~] | 6 | 86 | No | Debian dependency priority |
| 5 | [ ] | 0 | 31 | No | Mandatory project principles |
| 6 | [~] | 1 | 137 | No | Architecture |
| 7 | [~] | 19 | 20 | No | Domain models |
| 8 | [~] | 9 | 35 | No | Database |
| 9 | [~] | 10 | 11 | No | Credential security |
| 10 | [~] | 22 | 3 | No | Logging and auditing |
| 11 | [ ] | 0 | 20 | No | Threat model and security documentation |
| 12 | [ ] | 0 | 13 | No | Background processing |
| 13 | [~] | 1 | 14 | No | Performance |
| 14 | [~] | 4 | 53 | No | Tests |
| 17 | [~] | 1 | 61 | No | Debian dependency documentation |
| 19 | [~] | 15 | 137 | No | Documentation |
| 20 | [~] | 20 | 38 | No | Multilingual support and Qt Linguist |
| 21 | [~] | 2 | 70 | Sí | Main interface, themes, and accessibility |
| 22 | [x] | 23 | 0 | No | Complementary CLI |
| 23 | [~] | 5 | 32 | No | Built-in Learning Center |
| 24 | [~] | 54 | 0 | Sí | Glossary |
| 25 | [x] | 13 | 0 | No | Reference projects |
| 26 | [~] | 36 | 6 | No | Market-data sources and exchange adapters |
| 27 | [x] | 22 | 0 | No | Connection state management |
| 28 | [~] | 19 | 1 | No | Data import |
| 29 | [~] | 22 | 1 | Imbalance bars (29.1) need trade-level data; not supported | Data quality management |
| 30 | [~] | 14 | 11 | No | Market precision and exchange rules |
| 31 | [~] | 23 | 6 | No | Technical indicators |
| 32 | [~] | 18 | 16 | No | Financial charts |
| 33 | [~] | 29 | 57 | No | Strategies |
| 34 | [ ] | 0 | 24 | No | Visual strategy builder |
| 35 | [~] | 9 | 3 | Yes | Strategy complexity control |
| 36 | [~] | 4 | 15 | No | Strategy registry |
| 37 | [~] | 55 | 66 | No | Backtesting |
| 38 | [~] | 21 | 24 | Sí | Data splitting |
| 39 | [ ] | 0 | 57 | No | Parameter optimization |
| 40 | [~] | 71 | 4 | Sí | Performance metrics |
| 41 | [~] | 26 | 2 | Sí | Reports |
| 42 | [~] | 15 | 4 | Sí | Benchmarking |
| 43 | [~] | 31 | 7 | No | Statistical edge and evidence |
| 44 | [~] | 32 | 19 | Sí | Robustness and sensitivity analysis |
| 45 | [~] | 16 | 8 | Sí | Walk-forward analysis |
| 46 | [~] | 13 | 9 | No | Market regime analysis |
| 47 | [~] | 16 | 9 | No | Feature engineering |
| 48 | [ ] | 0 | 34 | No | Machine learning |
| 49 | [~] | 13 | 40 | No | Advanced financial machine learning (AFML) |
| 50 | [~] | 4 | 6 | No | Ensembles |
| 51 | [~] | 6 | 11 | No | Portfolio construction and correlations |
| 52 | [~] | 16 | 14 | No | Research experiment manager |
| 53 | [~] | 5 | 14 | No | Reproducibility |
| 54 | [ ] | 0 | 9 | No | Research notebooks |
| 55 | [ ] | 0 | 20 | No | AI research assistant |
| 56 | [x] | 23 | 0 | No | Execution realism |
| 57 | [~] | 5 | 55 | Sí | Paper trading |
| 58 | [~] | 0 | 74 | Sí | Risk manager |
| 59 | [~] | 0 | 39 | Sí | Emergency kill switch |
| 60 | [~] | 15 | 1 | No | Risk of ruin and capital depletion |
| 61 | [~] | 2 | 16 | No | Capital protection |
| 62 | [~] | 18 | 2 | Sí | Live monitoring |
| 63 | [~] | 33 | 8 | No | Live vs backtest drift |
| 64 | [x] | 16 | 0 | No | Strategy failure detection |
| 65 | [~] | 2 | 8 | No | Strategy promotion pipeline |
| 66 | [x] | 20 | 0 | No | Strategy qualification |
| 67 | [x] | 21 | 0 | No | Safety gates |
| 68 | [x] | 54 | 0 | No | Real trading |
| 69 | [~] | 22 | 59 | No | Development phases |
| 70 | [~] | 2 | 24 | No | Working method |
| 71 | [~] | 67 | 20 | No | First concrete task and expected result |
| 72 | [~] | 14 | 14 | No | Research ethics and honest reporting |
| 73 | [~] | 11 | 1 | Sí | Historical data acquisition and dataset identity |
| 74 | [x] | 9 | 0 | No | Research workflow and validity dashboard |
| 75 | [x] | 7 | 0 | No | Observable experiment lifecycle |
| 76 | [x] | 5 | 0 | No | Integrated research notebook |
| 77 | [x] | 10 | 0 | No | Honest assistant and strategy rule builder |
| 78 | [x] | 4 | 0 | No | Complexity and multiple-testing awareness |
| 79 | [x] | 11 | 0 | No | Paper trading over real market data and trading journal |
| 80 | [x] | 7 | 0 | No | Learning Center as a real course |
| 81 | [ ] | 0 | 16 | No | Python packaging |
| 82 | [ ] | 0 | 43 | No | Debian package |
| 83 | [ ] | 0 | 17 | No | AppImage |

---

# PART I — FOUNDATION

---

## [ ] 1. Project purpose and scientific principles

Crypto Trading Lab is a **research instrument**, not a market-prediction machine.

The scientific and technical objective is to allow the user to:

- [ ] formulate trading hypotheses;
- [ ] develop strategies;
- [ ] test them on historical data;
- [ ] avoid look-ahead bias and data leakage;
- [ ] separate training, validation, and out-of-sample data correctly;
- [ ] optimize parameters in a controlled way;
- [ ] analyze risk and performance;
- [ ] check robustness;
- [ ] study different market regimes;
- [ ] compare against benchmarks;
- [ ] perform paper trading;
- [ ] eventually evaluate a strategy for real trading under strict safety controls.

The application must favor reproducible and statistically responsible research, **with the explicit goal of finding and validating real edges that can generate real profits** — while never promising that such an edge will be found, and always telling the user the truth when it is not.

### 1.1 What the application is and is not

- [ ] Not a tool that "predicts the market".
- [ ] Not a guarantee of profit — and it must never claim to be one.
- [ ] A serious research instrument whose honest purpose is to find, validate, and help harvest a genuine edge.
- [ ] Not a substitute for financial advice.
- [ ] Not a place where a profitable backtest is treated as evidence of future advantage.

### 1.2 Evidence hierarchy

The interface must distinguish between:

```text
Observed result
Statistical evidence
Research hypothesis
Validated evidence
```

- [ ] "Observed result" = what happened in one historical test.
- [ ] "Statistical evidence" = whether the result is distinguishable from noise (see Chapter 43).
- [ ] "Research hypothesis" = the idea being investigated, never presented as a proven fact.
- [ ] "Validated evidence" = evidence that survived out-of-sample, robustness, and qualification checks (see Chapters 38, 44, and 66).

- [ ] The application must never present an observed backtest result as validated evidence by default.

### 1.3 Educational duty

- [ ] Every complex financial concept must be accompanied by a plain-language explanation.
- [ ] Every financial metric must include an explanation a complete beginner can understand.
- [ ] Every warning must be understandable to a complete beginner.

### 1.4 Realistic expectations

The application must teach realistic expectations grounded in real-world evidence:

- [ ] Explain that a large majority of retail crypto traders lose money (studies commonly report that roughly 70–95% of retail traders lose money, and that most day traders stop within their first two years).
- [ ] Explain that most of those who lose share the same mistakes: no validated edge, no risk control, risking money they need to live. This program exists precisely to be the opposite of that majority.
- [ ] Explain that a profitable backtest does not imply a profitable future (see Chapters 43–45).
- [ ] Explain that trading is not a reliable source of income — the reliable strategy is survival first, edge second.
- [ ] Explain that fees, spread, and slippage reduce net returns and compound over time.
- [ ] Explain that the safest financial decision for most people is not to trade money they cannot afford to lose.
- [ ] Never encourage the user to trade with essential funds, borrowed money, or emergency savings.
- [ ] Include these lessons in the Learning Center (see Chapter 23) and in the beginner documentation (see Chapter 19.2).

---

## [ ] 2. Terminology and conventions

These definitions are canonical for the whole document. Use them consistently in code, UI, documentation, and reports.

### 2.1 Costs

- [ ] **Trading fees**: the umbrella term for all costs applied to an order (commission, spread, slippage, and, where applicable, funding/borrowing costs).
- [ ] **Commission**: the exchange fee charged per order. A component of trading fees.
- [ ] **Spread**: the difference between the best bid and the best ask.
- [ ] **Slippage**: the difference between the expected execution price and the actual fill price.
- [ ] **Funding/borrowing costs**: apply only if leveraged or futures products are ever supported. Not applicable to the spot-only MVP.

### 2.2 Order rules

- [ ] **Minimum order quantity**: the smallest quantity of an asset that may be ordered.
- [ ] **Minimum order value/notional**: the smallest quote-currency value an order may have. Distinct from minimum order quantity.
- [ ] **Tick size**: the minimum price increment.
- [ ] **Step size**: the minimum quantity increment.

### 2.3 Entities and flow

- [ ] **Signal**: the output of a strategy ("enter long", "exit long", "hold"). A signal is not an order.
- [ ] **Order**: a request to execute a trade. Created only after a signal passes the risk manager.
- [ ] **Fill**: the executed portion of an order.
- [ ] **Strategy**: defines *when* a signal is generated. Never communicates with an exchange.
- [ ] **Execution**: handles orders, fills, latency, slippage, liquidity, exchange, positions, and balances.
- [ ] **Risk**: enforces limits, exposure, drawdown, position size, losses, restrictions, and emergency stop.

### 2.4 Data

- [ ] **Dataset**: a stored, versioned collection of market data used for research.
- [ ] **Data source**: the origin of data (exchange, CSV file, provider).
- [ ] **Backtest**: a deterministic historical simulation of strategy + execution + risk rules.
- [ ] **Paper trading**: simulated trading on real-time or replayed market data with simulated money.
- [ ] **Historical replay**: a paper-trading mode that replays stored historical data.

### 2.5 Validation periods

- [ ] **Training (strategy-development) period**: data used to develop rules and select initial parameters.
- [ ] **Validation period**: data used to compare candidates and refine hypotheses.
- [ ] **Out-of-sample (test) period**: data reserved for final historical evaluation.

### 2.6 Conventions

- [ ] All internal timestamps use UTC. Local timezone is used only for presentation.
- [ ] Monetary values, prices, quantities, commissions, and balances use `Decimal`, never `float`.
- [ ] The document uses "trading fees", "minimum order quantity", "minimum order value", "signal", "order", "backtest", "paper trading", "dataset", and "data source" as defined above.

---

## [~] 3. Supported platforms and technologies

### 3.1 Supported platforms

The application must be developed primarily for:

- [ ] Debian 12 Bookworm;
- [ ] Debian 13;
- [ ] MX Linux;
- [ ] AV Linux MXe;
- [ ] Ubuntu;
- [ ] Ubuntu-based distributions;
- [ ] other Debian-based GNU/Linux distributions.

### 3.2 Main technologies

Main technologies:

- [ ] Python 3;
- [ ] PyQt6;
- [x] SQLite;
- [x] Qt Linguist;
- [ ] Qt translation tools;
- [ ] `pyproject.toml`;
- [ ] pytest;
- [ ] Debian `.deb` packaging;
- [ ] an architecture prepared for AppImage distribution.

- [ ] The AppImage packaging process must remain separate from the official Debian package.
- [ ] The project must be Free Software and use a Debian-compatible license, preferably:

```text
GPL-3.0-or-later
```

- [ ] Do not use proprietary components or services that require mandatory payment.

---

## [~] 4. Debian dependency priority

Prioritize dependencies available in the official Debian 12 repositories before adding dependencies from PyPI.

### 4.0 MANDATORY STOP RULE for dependencies

The AI Agent must apply this rule without exception:

- [ ] If at any point the development requires installing a new dependency, the Agent must **STOP** development immediately at that task.
- [ ] The Agent must **NOT** install anything by itself: no `apt install`, no `pip install`, no `pip --user`, no downloading of packages or wheels.
- [ ] Instead, the Agent must **notify the developer** with:
  1. the exact package name;
  2. whether it comes from the Debian repositories or from PyPI;
  3. the reason it is needed;
  4. the exact command the developer must run.
- [ ] If the package exists in the Debian repositories, the developer installs it with `apt`; the Agent then verifies the import works and continues.
- [ ] If the package exists only on PyPI, the developer must create and activate a virtual environment (`python3 -m venv .venv`), and only then may the Agent use it inside that venv. The Agent must never create, activate, or install into a venv on its own.
- [x] The four **required** runtime dependencies are available as Debian packages, so the supported Debian 13 setup needs no venv. The **optional extras are PyPI-only** — `ccxt`, `pypdf`, `keyring`, `aiohttp`, `websockets` — and do require the venv procedure above; they are documented in `docs/en/developers/venv-setup.md` and declared as extras in `pyproject.toml`. The Agent must warn the developer before any of them becomes necessary.
- [ ] The Agent must not proceed past a missing dependency, must not mock a missing import to pretend work continues, and must record the blocker in the final report until the developer resolves it.

Before choosing any dependency:

1. [ ] confirm whether it exists in Debian 12;
2. [ ] confirm its exact Debian package name;
3. [ ] verify its version;
4. [ ] verify its license;
5. [ ] determine whether it is suitable for runtime, development, packaging, or optional use;
6. [ ] avoid adding a PyPI dependency when the Python standard library, Qt, or an official Debian package already solves the problem adequately.

### 4.1 Graphical interface

Evaluate and use the following Debian packages where appropriate:

- [ ] `python3-pyqt6`
- [ ] `python3-pyqt6.qtcharts`
- [x] `python3-pyqt6.qtwebsockets`
- [ ] `python3-pyqt6.qtsvg`
- [ ] `python3-pyqt6.qtdesigner`
- [ ] `pyqt6-dev-tools`
- [ ] `python3-superqt`

### 4.2 Charting libraries

Research and evaluate:

- [ ] `python3-pyqtgraph`
- [ ] `python3-pyqt6.qtcharts`
- [ ] `python3-matplotlib`

- [x] Create an internal chart abstraction so that the chart backend can be replaced without modifying the financial domain or strategy logic.

Initial preference:

- [ ] PyQtGraph for real-time charts, candlesticks, volume, and fast updates;
- [ ] Matplotlib for static reports, statistical charts, and exported graphics;
- [ ] Qt Charts where it is suitable and does not create performance limitations.

- [ ] Do not use Qt WebEngine for the main charts unless there is a documented technical justification.

### 4.3 Data processing and analysis

Evaluate:

- [ ] `python3-numpy`
- [ ] `python3-pandas`
- [ ] `python3-scipy`
- [ ] `python3-statsmodels`
- [ ] `python3-sklearn`
- [ ] `python3-numba`

Use:

- [ ] NumPy for numerical arrays and vectorized calculations;
- [ ] pandas for time series, tables, imports, exports, and analysis;
- [ ] SciPy when advanced statistical or numerical functions are required;
- [ ] statsmodels when statistically justified;
- [ ] scikit-learn only for optional research experiments;
- [x] Numba only as an optional performance optimization. (Framework ready; requires `apt install python3-numba` or `pip install numba`)

- [ ] Machine learning must not be a mandatory part of the initial application.
- [ ] Do not describe machine learning as a method that can predict the market with certainty.
- [ ] Machine learning details are defined in Chapter 48.

### 4.4 Networking

Evaluate:

- [ ] `python3-aiohttp`
- [ ] `python3-websockets`
- [ ] `python3-requests`
- [ ] `python3-requests-cache`
- [ ] `python3-ratelimiter`

Analyze whether the application should use:

- [ ] 1. `aiohttp` for REST and WebSocket communication;
- [ ] 2. `websockets` for WebSocket connections;
- [ ] 3. `QNetworkAccessManager` and `QWebSocket` for Qt-native networking. (An unwired attempt lived in `ui/charts/qt_websocket_client.py`; it duplicated the tested `exchanges/binance/websocket_client.py` and was removed on 2026-09-27 — see `docs/en/developers/unwired-modules-audit.md`.)

- [ ] Create interfaces that remain independent of the specific transport implementation.
- [ ] Never block the Qt main thread.

### 4.5 Persistence and validation

Evaluate:

- [ ] `python3-sqlalchemy`
- [ ] `python3-pydantic`
- [ ] `python3-dateutil`
- [ ] `python3-platformdirs`
- [ ] `python3-yaml`
- [ ] `python3-jsonschema`

- [ ] SQLite must be the default database.
- [ ] Do not make PostgreSQL a requirement for the desktop application.
- [ ] PostgreSQL may be considered as a future optional backend, but it must not be part of the MVP runtime requirements.

### 4.6 Security

Evaluate:

- [ ] `python3-keyring`
- [ ] `python3-cryptography`

API keys and secrets must never be stored:

- [ ] in plain text;
- [ ] inside the Git repository;
- [ ] in `.json` files;
- [ ] in `.yaml` files;
- [ ] in `.toml` files;
- [ ] in `.ini` files;
- [ ] in debug logs;
- [ ] in error reports;
- [ ] in SQLite without proper protection.

- [ ] Use the operating system credential store through `keyring`.

The application must also work without credentials for:

- [ ] public market data;
- [ ] imported CSV data;
- [ ] offline demonstrations;
- [x] backtesting;
- [x] paper trading;
- [ ] educational exercises.

### 4.7 Testing and code quality

Evaluate:

- [ ] `python3-pytest`
- [ ] `python3-pytest-asyncio`
- [ ] `python3-pytest-cov`
- [ ] `python3-requests-mock`
- [ ] `python3-freezegun`
- [ ] `python3-flake8`
- [ ] `python3-mypy`
- [ ] `python3-bandit`
- [ ] `python3-black`
- [ ] `python3-isort`

Classify each dependency as one of the following:

- [ ] required runtime dependency;
- [ ] recommended runtime dependency;
- [ ] optional dependency;
- [ ] development-only dependency;
- [ ] packaging-only dependency;
- [ ] available only from PyPI;
- [ ] unnecessary because the standard library or Qt is sufficient.

- [ ] Do not add external dependencies unnecessarily.

---

## [ ] 5. Mandatory project principles

The application must comply with the following rules:

- [ ] 1. Paper trading must be the default mode.
- [ ] 2. Real trading must be disabled in the initial build.
- [ ] 3. Futures must not be implemented in the MVP.
- [ ] 4. Margin trading must not be implemented in the MVP.
- [ ] 5. Leverage must not be implemented in the MVP.
- [ ] 6. The MVP must support spot markets only.
- [ ] 7. Martingale strategies must not be implemented.
- [ ] 8. The application must never double position size automatically after a loss.
- [ ] 9. The application must never promise profits.
- [ ] 10. The application must never request API withdrawal permissions.
- [ ] 11. The application must reject or warn about API keys with withdrawal permissions.
- [ ] 12. Strategies must never bypass the central risk manager.
- [ ] 13. Every order must pass through validation before being submitted.
- [ ] 14. The application must operate fully without API keys.
- [ ] 15. Automated tests must never use real funds.
- [ ] 16. The application must not implement market manipulation.
- [ ] 17. The application must not implement spoofing.
- [ ] 18. The application must not implement wash trading.
- [ ] 19. The application must not implement front-running.
- [ ] 20. The application must not abuse exchange APIs.
- [ ] 21. User strategy rules must not execute arbitrary Python code.
- [ ] 22. Do not use `eval()`.
- [ ] 23. Do not use `exec()`.
- [ ] 24. Do not dynamically import untrusted strategy code.
- [ ] 25. Educational explanations must accompany complex financial concepts.
- [ ] 26. Every financial metric must include a plain-language explanation.
- [ ] 27. Every warning must be understandable to a complete beginner.
- [ ] 28. The application must never encourage trading with money the user cannot afford to lose.
- [ ] 29. The application must warn when the user indicates financial hardship or an inability to absorb losses.
- [ ] 30. The application must never suggest borrowing money to trade.
- [ ] 31. The application must not present trading as a solution to financial problems.

---

## [~] 6. Architecture

Use a modular, maintainable, testable architecture.

- [ ] Propose a Clean Architecture or Hexagonal Architecture adapted to a PyQt6 desktop application.

Clearly separate:

- [ ] financial domain;
- [ ] application use cases;
- [ ] market-data providers;
- [ ] exchange adapters;
- [ ] strategy engine;
- [ ] backtesting engine;
- [ ] paper-trading engine;
- [ ] execution engine;
- [ ] order management;
- [ ] risk management;
- [ ] portfolio management;
- [ ] persistence;
- [ ] PyQt6 interface;
- [x] configuration;
- [ ] security;
- [ ] reporting;
- [ ] internationalization;
- [ ] beginner education;
- [ ] user documentation.

### 6.1 Research / Execution / Risk separation

This is a mandatory architectural rule (see also Chapter 2):

- [ ] **Research** owns: hypotheses, experiments, statistics, datasets, features, optimization, validation, robustness, machine learning, strategy comparison, regime analysis, reproducibility.
- [ ] **Execution** owns: signals, orders, fills, latency, slippage, liquidity, exchange, positions, balances.
- [ ] **Risk** owns: limits, exposure, drawdown, position size, losses, restrictions, emergency stop.

- [ ] Research components must not submit orders.
- [ ] Execution components must not modify risk limits.
- [ ] Risk components must not design strategies.
- [ ] The backtesting engine must not be expanded into a general research toolbox; research methods live in their own chapters (Chapters 43–51).

### 6.2 Suggested structure

- [ ] `crypto-trading-lab/`
  - [ ] `pyproject.toml`
  - [ ] `README.md`
  - [ ] `LICENSE`
  - [ ] `CHANGELOG.md`
  - [ ] `CONTRIBUTING.md`
  - [ ] `SECURITY.md`
  - [ ] `CODE_OF_CONDUCT.md`
  - [ ] `src/`
    - [ ] `crypto_trading_lab/`
      - [ ] `__init__.py`
      - [ ] `__main__.py`
      - [ ] `application.py`
      - [ ] `domain/`
        - [ ] `entities/`
        - [ ] `value_objects/`
        - [ ] `services/`
        - [ ] `exceptions/`
        - [ ] `protocols/`
      - [ ] `use_cases/`
      - [ ] `market_data/`
        - [ ] `providers/`
        - [ ] `normalization/`
        - [ ] `aggregation/`
        - [ ] `cache/`
      - [ ] `exchanges/`
        - [ ] `base/`
        - [ ] `binance/`
        - [ ] `coinbase/`
        - [ ] `mock/`
      - [ ] `indicators/`
      - [ ] `strategies/`
      - [ ] `backtesting/`
      - [ ] `research/`
        - [ ] `statistics/`
        - [ ] `robustness/`
        - [ ] `walk_forward/`
        - [ ] `regimes/`
        - [ ] `features/`
        - [ ] `machine_learning/`
        - [ ] `ensembles/`
        - [ ] `portfolio/`
        - [ ] `benchmarking/`
        - [ ] `experiments/`
        - [ ] `notebooks/`
      - [ ] `paper_trading/`
      - [ ] `execution/`
      - [ ] `risk/`
      - [ ] `portfolio/`
      - [ ] `analytics/`
      - [ ] `persistence/`
        - [ ] `database/`
        - [ ] `repositories/`
        - [ ] `migrations/`
      - [ ] `security/`
      - [ ] `configuration/`
      - [ ] `reporting/`
      - [ ] `education/`
        - [ ] `lessons/`
        - [ ] `glossary/`
        - [ ] `tutorials/`
        - [ ] `quizzes/`
        - [ ] `examples/`
      - [ ] `infrastructure/`
      - [ ] `ui/`
        - [ ] `main_window/`
        - [ ] `dashboards/`
        - [ ] `charts/`
        - [ ] `dialogs/`
        - [ ] `models/`
        - [ ] `delegates/`
        - [ ] `workers/`
        - [ ] `education/`
        - [ ] `resources/`
        - [ ] `generated/`
      - [ ] `i18n/`
        - [ ] `en/`
        - [ ] `es/`
        - [ ] `translations/`
        - [ ] `README.md`
  - [ ] `tests/`
    - [ ] `unit/`
    - [ ] `integration/`
    - [ ] `gui/`
    - [ ] `contract/`
    - [ ] `regression/`
    - [ ] `security/`
    - [ ] `education/`
    - [ ] `fixtures/`
  - [ ] `docs/`
    - [ ] `en/`
      - [ ] `beginners/`
      - [ ] `user-guide/`
      - [ ] `developers/`
      - [ ] `reference/`
    - [ ] `es/`
      - [ ] `beginners/`
      - [ ] `user-guide/`
      - [ ] `developers/`
      - [ ] `reference/`
  - [ ] `examples/`
  - [ ] `scripts/`
  - [ ] `data/`
    - [ ] `samples/`
  - [ ] `debian/`
  - [ ] `packaging/`
    - [ ] `appimage/`
  - [ ] `.github/`
    - [ ] `workflows/`

- [ ] The `ui/generated` directory may contain files generated from Qt Designer.
- [ ] Do not place business logic inside generated interface files.

---

## [~] 7. Domain models

Implement explicit, strongly validated models for:

- [ ] Exchange;
- [x] Market;
- [x] TradingPair;
- [ ] Asset;
- [x] Candle;
- [ ] Trade;
- [ ] OrderBook;
- [ ] OrderBookLevel;
- [x] Ticker;
- [x] Balance;
- [ ] Position;
- [ ] Portfolio;
- [ ] Order;
- [x] OrderRequest;
- [x] OrderResult;
- [x] Fill;
- [ ] Fee;
- [ ] Strategy;
- [ ] StrategySignal;
- [ ] RiskDecision;
- [ ] Backtest;
- [x] BacktestResult;
- [ ] PaperAccount;
- [ ] PerformanceMetrics;
- [ ] DatasetVersion;
- [ ] Experiment;
- [ ] StrategyVersion;
- [ ] QualificationReport.

Use:

- [x] `Decimal` for money;
- [x] `Decimal` for prices;
- [x] `Decimal` for quantities;
- [x] `Decimal` for commissions;
- [x] `Decimal` for balances;
- [x] normalized timestamps;
- [x] UTC internally;
- [ ] the local timezone only for presentation;
- [x] dataclasses or Pydantic models where appropriate.

- [x] Do not use `float` for critical monetary calculations.
- [x] Every exchange adapter must normalize exchange-specific data into common domain models.

---

## [~] 8. Database

Use SQLite with SQLAlchemy.

The database must store:

- [ ] configured exchanges;
- [ ] markets;
- [x] candles;
- [ ] trades;
- [ ] optional order-book snapshots;
- [ ] strategies;
- [ ] strategy parameters;
- [ ] strategy versions;
- [ ] dataset versions;
- [ ] backtest runs;
- [ ] experiments (see Chapter 52);
- [ ] simulated orders;
- [ ] fills;
- [ ] fees;
- [ ] simulated balances;
- [ ] positions;
- [ ] performance metrics;
- [ ] qualification reports (see Chapter 66);
- [ ] alerts;
- [ ] audit records;
- [ ] non-secret configuration;
- [ ] educational progress;
- [ ] completed lessons;
- [ ] glossary bookmarks;
- [ ] beginner tutorial progress.

- [x] Do not store API keys in SQLite.

Enable where appropriate:

- [x] foreign keys;
- [x] indexes;
- [x] transactions;
- [x] WAL mode;
- [x] migrations;
- [ ] backups;
- [ ] integrity checks.

- [ ] Design a retention policy to prevent uncontrolled database growth.

Include import and export support for:

- [ ] CSV;
- [ ] JSON;
- [ ] optional Parquet if an acceptable Debian dependency exists.

Exports must include:

- [x] exchange;
- [x] trading pair;
- [ ] interval;
- [ ] time range;
- [ ] timezone;
- [ ] format;
- [ ] schema version.

---

## [~] 9. Credential security

Create an abstract `CredentialStore`.

Initial implementations:

- [x] system keyring;
- [x] in-memory storage for tests;
- [x] mock implementation for unit tests.

The application must:

- [ ] hide keys on screen;
- [ ] allow secure pasting;
- [ ] never log pasted secrets;
- [ ] never copy secrets automatically to the clipboard;
- [ ] clear sensitive fields;
- [ ] never log authentication headers;
- [ ] redact secrets from exceptions;
- [ ] block withdrawal permissions;
- [ ] warn about excessive permissions;
- [ ] allow credential deletion;
- [ ] display the last-use date without showing the secret.

Add a logging filter that redacts:

- [x] API keys;
- [x] tokens;
- [x] signatures;
- [x] JWTs;
- [x] secrets;
- [x] sensitive parameters;
- [x] authorization headers.

---

## [~] 10. Logging and auditing

Use Python's standard `logging` module.

Separate logs for:

- [x] application;
- [x] networking;
- [x] trading;
- [x] auditing;
- [x] errors.

Features:

- [x] rotation;
- [x] configurable levels;
- [x] human-readable format;
- [x] optional JSON format;
- [x] correlation IDs;
- [x] secret redaction;
- [ ] support export;
- [ ] size limits;
- [ ] retention policy.

The audit log must record:

- [x] mode changes;
- [x] risk-setting changes;
- [x] strategy creation;
- [x] backtest start and completion;
- [x] experiment start and completion;
- [x] kill-switch activation;
- [x] real-trading attempts;
- [x] order creation and cancellation;
- [x] credential changes;
- [x] critical errors.

- [x] Do not log secret values.

---

## [ ] 11. Threat model and security documentation

- [ ] Create a threat model covering:

- [ ] API key theft;
- [ ] secrets appearing in logs;
- [ ] compromised dependencies;
- [ ] malicious strategy files;
- [ ] malformed CSV files;
- [ ] manipulated API responses;
- [ ] stale market data;
- [ ] incorrect local clock;
- [ ] replayed messages;
- [ ] duplicate orders;
- [ ] uncontrolled storage growth;
- [ ] GUI freezes;
- [ ] incomplete database updates;
- [ ] corrupted configuration;
- [ ] excessive API permissions;
- [ ] accidental real-trading activation;
- [ ] misleading educational content;
- [ ] users confusing simulation with real profitability.

- [ ] Document mitigations for each threat.

---

## [ ] 12. Background processing

Do not block the GUI.

Use a consistent approach involving:

- [ ] `QThreadPool`;
- [ ] `QRunnable`;
- [ ] worker objects moved to `QThread`;
- [ ] signals and slots;
- [ ] carefully integrated asyncio;
- [ ] separate processes for CPU-intensive work when necessary.

- [ ] Do not mix multiple concurrency models without a clear abstraction.

Backtesting, optimization, robustness, and walk-forward jobs must:

- [ ] report progress;
- [ ] support cancellation;
- [ ] terminate cleanly;
- [ ] save safe partial results;
- [ ] notify errors.

- [ ] Do not update widgets directly from worker threads.

---

## [~] 13. Performance

Design for:

- [ ] hundreds of thousands of stored candles;
- [ ] charts with limited visible windows;
- [ ] batch insertion;
- [ ] indexed queries;
- [ ] vectorized processing;
- [ ] controlled caching;
- [ ] task cancellation;
- [ ] moderate memory usage.

- [ ] First build a correct and testable implementation.
- [ ] Optimize only after measuring.

Include benchmarks for:

- [ ] CSV loading;
- [ ] indicator calculation;
- [x] backtesting.
- [ ] SQLite insertion;
- [ ] chart updates.

---

## [~] 14. Tests

Write tests from the beginning.

### 14.1 Unit tests

Test:

- [ ] monetary models;
- [ ] normalization;
- [ ] indicators;
- [ ] strategy rules;
- [ ] risk rules;
- [ ] position sizing;
- [x] commissions;
- [x] slippage;
- [x] metrics. (computed from backtest)
- [ ] `Decimal` precision;
- [ ] educational text availability;
- [ ] translation-key availability.

### 14.2 Integration tests

Test:

- [ ] SQLite;
- [ ] repositories;
- [ ] migrations;
- [ ] CSV imports;
- [ ] mock providers;
- [ ] simulated HTTP clients;
- [ ] simulated WebSockets;
- [ ] credential-store abstractions.

### 14.3 Contract tests

- [ ] Every exchange adapter must pass a common contract-test suite.

### 14.4 GUI tests

Test:

- [ ] table models;
- [ ] validators;
- [ ] critical dialogs;
- [ ] language switching;
- [ ] English startup;
- [ ] Spanish translation loading;
- [ ] settings;
- [ ] kill switch;
- [ ] mode activation;
- [ ] Learning Center navigation;
- [ ] glossary search;
- [ ] tutorial progress.

- [ ] Do not make real network calls in normal automated tests.

### 14.5 Financial regression tests

- [ ] Include small frozen datasets and expected results to prevent silent changes in:

- [ ] trades;
- [ ] balances;
- [x] metrics. (computed from backtest)
- [ ] equity curves;
- [ ] drawdowns.

### 14.6 Statistical tests

- [ ] Add tests for the statistical research components (see Chapters 38 and 43–46):

- [ ] split reproducibility;
- [ ] walk-forward window boundaries;
- [ ] Monte Carlo seeds and scenario counts;
- [ ] sensitivity sweeps;
- [ ] significance calculations on synthetic data with known properties.

### 14.7 Security tests

Verify that:

- [ ] secrets do not appear in logs;
- [ ] secrets are not stored in SQLite;
- [ ] secrets do not appear in exported files;
- [ ] real trading remains disabled;
- [ ] strategies cannot bypass the risk manager.

### 14.8 Documentation tests

Verify:

- [ ] required beginner guides exist;
- [ ] internal documentation links are valid;
- [ ] code examples are syntactically correct;
- [ ] English documentation is present;
- [ ] Spanish documentation structure mirrors the English structure where translated;
- [ ] glossary terms referenced by the interface exist.

---

## [~] 17. Debian dependency documentation

Create:

- [ ] `docs/en/developers/debian-dependencies.md`

Include a table containing:

- [ ] purpose;
- [ ] Python import;
- [ ] Debian package;
- [ ] Debian 12 version;
- [ ] required or optional;
- [ ] runtime or build dependency;
- [ ] alternative;
- [ ] reason for selection;
- [ ] Debian 13 availability;
- [ ] PyPI equivalent.

Evaluate at least:

- [ ] `python3-pyqt6`
- [ ] `python3-pyqt6.qtcharts`
- [x] `python3-pyqt6.qtwebsockets`
- [ ] `python3-pyqt6.qtsvg`
- [ ] `python3-pyqt6.qtdesigner`
- [ ] `pyqt6-dev-tools`
- [ ] `python3-pyqtgraph`
- [ ] `python3-superqt`
- [ ] `python3-numpy`
- [ ] `python3-pandas`
- [ ] `python3-scipy`
- [ ] `python3-matplotlib`
- [ ] `python3-statsmodels`
- [ ] `python3-sklearn`
- [ ] `python3-numba`
- [ ] `python3-aiohttp`
- [ ] `python3-websockets`
- [ ] `python3-requests`
- [ ] `python3-requests-cache`
- [ ] `python3-ratelimiter`
- [ ] `python3-sqlalchemy`
- [ ] `python3-pydantic`
- [ ] `python3-dateutil`
- [ ] `python3-platformdirs`
- [ ] `python3-yaml`
- [ ] `python3-jsonschema`
- [ ] `python3-keyring`
- [ ] `python3-cryptography`
- [ ] `python3-apscheduler`
- [ ] `python3-pytest`
- [ ] `python3-pytest-asyncio`
- [ ] `python3-pytest-cov`
- [ ] `python3-requests-mock`
- [ ] `python3-freezegun`
- [ ] `python3-flake8`
- [ ] `python3-mypy`
- [ ] `python3-bandit`
- [ ] `python3-black`
- [ ] `python3-isort`
- [ ] `python3-build`
- [ ] `python3-setuptools`
- [ ] `python3-wheel`
- [ ] `python3-debian`
- [ ] `dh-python`
- [ ] `debhelper-compat`
- [ ] `devscripts`
- [ ] `lintian`
- [ ] `sbuild`

- [ ] Do not assume every package must be installed.

- [ ] Create a Spanish translation later at `docs/es/developers/dependencias-debian.md`

- [ ] English documentation must be completed first.

---

## [~] 19. Documentation

- [ ] Documentation is a core feature of the project, not an optional final task.
- [ ] Create and maintain documentation continuously as the application evolves.
- [ ] English documentation must be written first.
- [ ] Spanish translations must follow after the English documentation is stable.

### 19.1 Main project documentation

Create:

- [ ] `README.md`
- [ ] `INSTALL.md`
- [ ] `USER_GUIDE.md`
- [ ] `DEVELOPER_GUIDE.md`
- [ ] `ARCHITECTURE.md`
- [ ] `SECURITY.md`
- [ ] `CONTRIBUTING.md`
- [ ] `CHANGELOG.md`
- [ ] `ROADMAP.md`

Also create:

- [ ] `docs/en/developers/debian-packaging.md`
- [ ] `docs/en/developers/debian-dependencies.md`
- [ ] `docs/en/developers/exchange-adapters.md`
- [ ] `docs/en/developers/backtesting-methodology.md`
- [ ] `docs/en/developers/risk-management.md`
- [ ] `docs/en/developers/data-formats.md`
- [ ] `docs/en/developers/i18n.md`
- [ ] `docs/en/developers/threat-model.md`

### 19.2 “For Dummies” beginner documentation

- [x] Create a complete beginner-friendly documentation series in English. (started: start-here + glossary; series continues)

The writing style must be similar to a good “For Dummies” guide:

- [x] welcoming;
- [x] patient;
- [x] non-judgmental;
- [x] clear;
- [x] practical;
- [x] step-by-step;
- [x] free from unnecessary jargon;
- [x] full of simple examples;
- [x] full of warnings before risky actions;
- [x] suitable for readers who know nothing about cryptocurrency;
- [x] suitable for readers who know nothing about trading;
- [x] suitable for readers who know nothing about technical analysis;
- [x] suitable for readers who have never used an exchange;
- [x] suitable for readers who have never used a backtesting program.

- [ ] Do not assume prior knowledge.

Whenever a technical word is introduced:

- [ ] 1. define it immediately;
- [ ] 2. provide a simple example;
- [ ] 3. explain why it matters;
- [ ] 4. link it to the glossary;
- [ ] 5. mention common misunderstandings.

Create this documentation structure:

- [ ] `docs/en/beginners/00-start-here.md`
- [ ] `docs/en/beginners/01-what-is-money.md`
- [ ] `docs/en/beginners/02-what-is-digital-money.md`
- [ ] `docs/en/beginners/03-what-is-cryptocurrency.md`
- [ ] `docs/en/beginners/04-what-is-bitcoin.md`
- [ ] `docs/en/beginners/05-what-is-a-blockchain.md`
- [ ] `docs/en/beginners/06-wallets-explained.md`
- [ ] `docs/en/beginners/07-private-keys-and-seed-phrases.md`
- [ ] `docs/en/beginners/08-what-is-an-exchange.md`
- [ ] `docs/en/beginners/09-centralized-and-decentralized-exchanges.md`
- [ ] `docs/en/beginners/10-spot-markets.md`
- [ ] `docs/en/beginners/11-trading-pairs.md`
- [ ] `docs/en/beginners/12-bid-ask-and-spread.md`
- [ ] `docs/en/beginners/13-order-books.md`
- [ ] `docs/en/beginners/14-market-orders.md`
- [ ] `docs/en/beginners/15-limit-orders.md`
- [ ] `docs/en/beginners/16-fees.md`
- [ ] `docs/en/beginners/17-slippage.md`
- [ ] `docs/en/beginners/18-liquidity.md`
- [ ] `docs/en/beginners/19-volatility.md`
- [ ] `docs/en/beginners/20-candlestick-charts.md`
- [ ] `docs/en/beginners/21-ohlcv-data.md`
- [ ] `docs/en/beginners/22-timeframes.md`
- [ ] `docs/en/beginners/23-support-and-resistance.md`
- [ ] `docs/en/beginners/24-trends.md`
- [ ] `docs/en/beginners/25-technical-indicators.md`
- [ ] `docs/en/beginners/26-moving-averages.md`
- [ ] `docs/en/beginners/27-rsi.md`
- [ ] `docs/en/beginners/28-macd.md`
- [ ] `docs/en/beginners/29-bollinger-bands.md`
- [ ] `docs/en/beginners/30-atr-and-volatility.md`
- [ ] `docs/en/beginners/31-what-is-a-trading-strategy.md`
- [ ] `docs/en/beginners/32-risk-management.md`
- [ ] `docs/en/beginners/33-position-sizing.md`
- [ ] `docs/en/beginners/34-stop-loss.md`
- [ ] `docs/en/beginners/35-take-profit.md`
- [ ] `docs/en/beginners/36-drawdown.md`
- [ ] `docs/en/beginners/37-paper-trading.md`
- [ ] `docs/en/beginners/38-backtesting.md`
- [ ] `docs/en/beginners/39-look-ahead-bias.md`
- [ ] `docs/en/beginners/40-overfitting.md`
- [ ] `docs/en/beginners/41-training-validation-and-testing.md`
- [ ] `docs/en/beginners/42-why-backtests-can-lie.md`
- [ ] `docs/en/beginners/43-why-paper-trading-is-different.md`
- [ ] `docs/en/beginners/44-api-keys.md`
- [ ] `docs/en/beginners/45-api-key-security.md`
- [ ] `docs/en/beginners/46-common-scams.md`
- [ ] `docs/en/beginners/47-emotional-trading.md`
- [ ] `docs/en/beginners/48-common-beginner-mistakes.md`
- [ ] `docs/en/beginners/49-when-not-to-trade.md`
- [ ] `docs/en/beginners/50-learning-roadmap.md`
- [ ] `docs/en/beginners/51-why-most-traders-lose-money.md`
- [ ] `docs/en/beginners/52-trading-is-not-an-income.md`
- [ ] `docs/en/beginners/glossary.md`

### 19.3 Program usage guide

- [ ] Create a complete beginner user guide:

- [ ] `docs/en/user-guide/00-welcome.md`
- [ ] `docs/en/user-guide/01-installing-on-debian.md`
- [ ] `docs/en/user-guide/02-first-launch.md`
- [ ] `docs/en/user-guide/03-interface-tour.md`
- [ ] `docs/en/user-guide/04-changing-the-language.md`
- [ ] `docs/en/user-guide/05-using-the-learning-center.md`
- [ ] `docs/en/user-guide/06-importing-csv-data.md`
- [ ] `docs/en/user-guide/07-opening-a-market-chart.md`
- [ ] `docs/en/user-guide/08-reading-a-candlestick-chart.md`
- [ ] `docs/en/user-guide/09-adding-an-indicator.md`
- [ ] `docs/en/user-guide/10-creating-a-simple-strategy.md`
- [ ] `docs/en/user-guide/11-running-your-first-backtest.md`
- [ ] `docs/en/user-guide/12-understanding-backtest-results.md`
- [ ] `docs/en/user-guide/13-starting-paper-trading.md`
- [ ] `docs/en/user-guide/14-placing-a-simulated-order.md`
- [ ] `docs/en/user-guide/15-reading-your-portfolio.md`
- [ ] `docs/en/user-guide/16-using-risk-profiles.md`
- [ ] `docs/en/user-guide/17-using-the-kill-switch.md`
- [ ] `docs/en/user-guide/18-exporting-a-report.md`
- [ ] `docs/en/user-guide/19-backing-up-your-data.md`
- [ ] `docs/en/user-guide/20-troubleshooting.md`
- [ ] `docs/en/user-guide/21-safe-next-steps.md`

Each guide must contain:

- [ ] objective;
- [ ] prerequisites;
- [ ] numbered steps;
- [ ] expected result;
- [ ] screenshots or screenshot placeholders;
- [ ] common mistakes;
- [ ] troubleshooting;
- [ ] safety notes;
- [ ] glossary links;
- [ ] a short knowledge check.

### 19.4 Spanish documentation

- [ ] After the English documentation is created and reviewed, create Spanish translations under `docs/es/`.
- [ ] The Spanish structure should mirror the English structure where practical.
- [ ] Do not automatically translate technical content without review.
- [ ] Use clear, neutral Spanish suitable for Latin American users.
- [ ] Maintain terminology consistently.

### 19.5 Documentation rules

Documentation must:

- [ ] evolve with each feature;
- [ ] be updated in the same change as the feature;
- [ ] never describe nonexistent features as completed;
- [ ] clearly label planned or experimental features;
- [ ] clearly distinguish paper trading from real trading;
- [ ] clearly distinguish education from financial advice;
- [ ] include version information where useful;
- [ ] include links between related topics;
- [ ] avoid unexplained abbreviations.

The README must clearly explain:

- [ ] that the application does not guarantee profits;
- [ ] that simulation is the default mode;
- [ ] that real trading is disabled initially;
- [ ] how to install Debian dependencies;
- [ ] how to run the application;
- [ ] how to run tests;
- [ ] how to build the `.deb`;
- [ ] how to contribute;
- [ ] where beginners should start learning.

---

## [~] 20. Multilingual support and Qt Linguist

The application must be multilingual from the beginning.

### 20.1 Language order

The language implementation order must be:

- [x] 1. English as the primary and default language;
- [x] 2. Spanish as the second supported language;
- [ ] 3. additional languages may be added later.

- [x] The application must start in English on first launch unless the user has previously selected another language.
- [ ] The user must be able to change the language from the interface.
- [ ] The application should support either:
  - [ ] immediate language switching at runtime; or
  - [ ] language switching after restart if runtime switching creates excessive complexity.

- [ ] The chosen behavior must be documented.

### 20.2 Qt translation system

Use:

- [x] `QTranslator`;
- [x] `.ts` translation source files;
- [x] `.qm` compiled translation files;
- [ ] Qt Linguist;
- [x] `pylupdate6`;
- [x] `lrelease`;
- [x] `self.tr()` or the correct PyQt6 translation mechanism.

Suggested translation files:

- [x] `src/crypto_trading_lab/i18n/translations/crypto_trading_lab_en.ts`
- [x] `src/crypto_trading_lab/i18n/translations/crypto_trading_lab_es.ts`

- [x] English is the source and default application language.
- [ ] Spanish must be maintained as a complete translation.
- [ ] Do not use Spanish source strings and translate them into English.
- [ ] Do not hard-code visible strings outside the translation system.
- [ ] Do not concatenate sentence fragments that are difficult to translate.

Translate:

- [x] menus;
- [x] buttons;
- [x] labels;
- [ ] dialogs;
- [ ] warnings;
- [ ] errors;
- [ ] metric names;
- [ ] strategy descriptions;
- [ ] report text;
- [ ] units;
- [x] connection states;
- [x] risk messages;
- [ ] educational lessons;
- [ ] glossary terms;
- [ ] tutorials;
- [ ] onboarding screens;
- [ ] help text;
- [x] accessibility labels.

Document commands such as:

- [x] `pylupdate6`
- [ ] `linguist`
- [x] `lrelease`

- [ ] Do not use absolute paths.

### 20.3 Translation workflow

- [ ] Create `docs/en/developers/translation-workflow.md` covering:
  - [ ] how source strings are marked;
  - [ ] how `.ts` files are updated;
  - [ ] how Qt Linguist is used;
  - [ ] how translations are reviewed;
  - [ ] how `.qm` files are generated;
  - [ ] how missing translations are detected;
  - [ ] how plural forms are handled;
  - [ ] how translator comments are added;
  - [ ] how screenshots are used for translation context.

- [ ] Create the Spanish equivalent:
  - [ ] `docs/es/developers/flujo-de-traduccion.md`

- [ ] Add automated checks for untranslated critical strings.

---

## [~] 21. Main interface, themes, and accessibility

### 21.1 Main interface

Design a professional, clear, responsive interface.

#### Sidebar

Include:

- [ ] Overview;
- [ ] Markets;
- [ ] Charts;
- [ ] Strategies;
- [ ] Backtesting;
- [ ] Research Lab;
- [ ] Paper Trading;
- [ ] Portfolio;
- [ ] Orders;
- [ ] Risk;
- [ ] Reports;
- [ ] Learning Center;
- [ ] Glossary;
- [ ] Tutorials;
- [ ] Logs;
- [ ] Settings;
- [ ] Help.

#### Top toolbar

Include:

- [x] exchange.
- [ ] environment;
- [x] trading pair.
- [ ] interval;
- [ ] connection status;
- [ ] last-data time;
- [ ] current mode;
- [ ] kill-switch status;
- [ ] selected language.

#### Status bar

Include:

- [ ] connectivity;
- [ ] latency;
- [ ] active tasks;
- [ ] pending data;
- [ ] database status;
- [ ] risk warnings;
- [ ] educational hints.

Use:

- [ ] `QMainWindow`;
- [ ] `QDockWidget` where appropriate;
- [ ] `QAbstractTableModel`;
- [ ] proxy models for filtering and sorting;
- [ ] delegates for editing;
- [ ] `QSettings` only for non-sensitive preferences;
- [ ] clear dialogs;
- [ ] keyboard accessibility.

Avoid:

- [ ] overloaded interfaces;
- [ ] using color as the only status indicator;
- [ ] unnecessary modal dialogs;
- [ ] rebuilding entire tables for every update.

### 21.2 Themes and appearance

Include:

- [ ] system theme;
- [ ] light theme;
- [ ] dark theme;
- [ ] interface scaling;
- [ ] saved window state;
- [ ] support for small screens;
- [ ] bundled SVG icons;
- [ ] good behavior under XFCE;
- [ ] good behavior under Fluxbox;
- [ ] good behavior under KDE;
- [ ] good behavior under GNOME;
- [ ] good behavior under LXQt.

- [ ] Do not depend on one desktop theme.
- [ ] Verify contrast and readability.
- [ ] Do not download icons at runtime.

### 21.3 Accessibility

Include:

- [ ] full keyboard navigation;
- [ ] accessible labels;
- [ ] logical tab order;
- [ ] tooltips;
- [ ] messages that do not depend only on color;
- [ ] interface scaling;
- [ ] reasonable screen-reader support;
- [ ] configurable shortcuts;
- [ ] reduced-animation support;
- [ ] readable beginner documentation;
- [ ] clear heading structures;
- [ ] descriptive link text.

---

## [x] 22. Complementary CLI

Implemented 2026-10-26. Every subcommand calls
`src/crypto_trading_lab/application.py`, the same use-case layer the GUI
uses; `tests/test_cli.py` and `tests/test_application.py` cover the real
behaviour and the honest failures.

- [x] Add a basic CLI without duplicating business logic:

- [x] `crypto-trading-lab --version`
- [x] `crypto-trading-lab doctor`
- [x] `crypto-trading-lab database check`
- [x] `crypto-trading-lab import-csv file.csv`
- [x] `crypto-trading-lab backtest strategy.yaml` (YAML needs the optional
  `python3-yaml` package; the same configuration as `.json` needs nothing
  beyond the standard library)
- [x] `crypto-trading-lab list-strategies`
- [x] `crypto-trading-lab list-lessons`
- [x] `crypto-trading-lab glossary search "slippage"`

- [x] The CLI must reuse the same use cases as the GUI.
  (`application.import_csv_file` is called by both `cli.py` and
  `MainWindow.load_csv_file`; the backtest calls the same `run_backtest`
  and `compute_performance` the Lab uses.)

The `doctor` command must check:

- [x] Python version;
- [x] required modules;
- [x] database;
- [x] permissions;
- [x] keyring;
- [x] public connectivity; (`doctor --network`; offline by default so the
  command stays deterministic and the suite never touches the network)
- [x] system clock; (`doctor --network` compares against a public clock)
- [x] Qt resources;
- [x] translations;
- [x] XDG paths;
- [x] English documentation. (`docs/en/developers/`)
- [x] Spanish translation availability.

- [x] It must never display secrets. (No credential store is read; a test
  monkeypatches `KeyringCredentialStore.load`/`list` to fail if doctor
  ever calls them.)

---

## [~] 23. Built-in Learning Center

- [x] Create a Learning Center inside the application.

It must include:

- [x] beginner lessons;
- [x] glossary;
- [ ] tutorials;
- [ ] examples;
- [ ] simple quizzes;
- [ ] progress tracking;
- [ ] bookmarks;
- [ ] links to relevant application screens.

The Learning Center should allow a user to:

- [ ] read a lesson;
- [ ] open the related chart or tool;
- [ ] try an example using simulated data;
- [ ] answer a short quiz;
- [ ] mark the lesson as completed;
- [ ] continue from the last lesson.

Initial learning path:

- [ ] 1. What is cryptocurrency?
- [ ] 2. What is a market?
- [ ] 3. What is a trading pair?
- [ ] 4. What is a candlestick?
- [ ] 5. What is volume?
- [ ] 6. What is a market order?
- [ ] 7. What is a limit order?
- [ ] 8. What are fees?
- [ ] 9. What is risk?
- [ ] 10. What is paper trading?
- [ ] 11. What is backtesting?
- [ ] 12. Build your first simple strategy.
- [ ] 13. Run your first backtest.
- [ ] 14. Understand a loss.
- [ ] 15. Understand drawdown.
- [ ] 16. Learn why profits are never guaranteed.
- [ ] 17. Why most traders lose money.
- [ ] 18. Trading is not a reliable income.
- [ ] 19. When not to trade.
- [ ] 20. Protecting the money you need for living.

- [x] The Learning Center must work offline.
- [x] Do not require an internet connection for core educational content.

---

## [~] 24. Glossary

- [x] Create an English glossary first, followed by Spanish. (English initial version done; Spanish pending)

The glossary must include terms such as:

- [x] asset;
- [x] cryptocurrency;
- [x] Bitcoin;
- [x] altcoin;
- [x] blockchain;
- [x] wallet;
- [x] private key;
- [x] seed phrase;
- [x] exchange.
- [x] trading pair.
- [x] base asset;
- [x] quote asset;
- [x] bid;
- [x] ask;
- [x] spread;
- [x] liquidity;
- [x] volatility;
- [x] order book;
- [x] market order;
- [x] limit order;
- [x] stop-loss;
- [x] take-profit;
- [x] commission;
- [x] fee;
- [x] slippage;
- [x] candle;
- [x] OHLCV;
- [x] timeframe;
- [x] indicator;
- [x] strategy;
- [x] signal;
- [x] position;
- [x] portfolio;
- [x] drawdown;
- [x] backtest;
- [x] paper trading.
- [x] overfitting;
- [x] look-ahead bias;
- [x] API;
- [x] API key;
- [x] WebSocket;
- [x] REST;
- [x] rate limit;
- [x] dataset;
- [x] out-of-sample;
- [x] walk-forward;
- [x] robustness;
- [x] benchmark.

Every glossary entry must include:

- [x] a short definition;
- [x] a plain-language explanation;
- [x] an example;
- [x] related terms;
- [x] a warning when appropriate.

---

## [x] 25. Reference projects

The repositories under `external/` are **technical and architectural references**.

- [x] They should be consulted to study concepts, gather ideas, or, if possible, adapt the code for use. **Done — all eight studied; conclusions in `reference-projects.md` Parts A–H.**
- [x] If a feature in a reference project is assumed, verify it in that project's documentation first; never assume a feature exists because the project name suggests it. **Done — every Part separates verified findings from negatives found by search, and each states the searches it ran.**

Technical references:

- [x] **Backtrader** (`external/backtrader`): study event-driven backtesting design, analyzers (Sharpe, drawdown, trade analysis, SQN, VWR, Calmar), broker simulation, and feed handling. Use as inspiration for Chapter 37, not as a runtime dependency. **Done — `reference-projects.md` Part B.**
- [x] **CCXT** (`external/ccxt`): study the unified exchange API design, market metadata normalization (precision, limits), REST/WebSocket abstraction, and the many exchange quirks handled. Use as inspiration for Chapter 26 exchange adapters; verify Debian/PyPI packaging before use. **Done — Part D; PyPI-only, verified live (104 exchanges), `ccxt` is an optional extra.**
- [x] **Freqtrade** (`external/freqtrade`): study strategy/execution separation, dry-run (paper) mode, hyperopt (parameter optimization), persistence, and its cautious default posture. Inspect for Chapters 33, 39, and 57. **Done — Part E. GPLv3, so inspiration only. Signals-not-orders enforced by construction; dry-run is a run mode, not a fork. Verified gaps it does not fill: no walk-forward, no Monte Carlo, no cross-validation, no out-of-sample split, no risk-based sizing, no kill switch, no strategy id/version, no dataset identity in hyperopt records, no partial fills.**
- [x] **Hummingbot** (`external/hummingbot`): study execution and order-management design, market-making/arbitrage logic, and connector architecture. Inspect for Chapters 56 and 26. **Done — Part F. Apache-2.0, adaptation permitted. Borrow the thin-subclass connector base, the `TradingRule` field set, the client-order-tracker recovery machinery and the "insufficient depth is reported" query; do not adopt its candle-only backtester. Its kill switch ships disabled by default — ours must not.**
- [x] **Jesse** (`external/jesse`): study its research loop: backtest, optimization, Monte Carlo simulation, rule significance testing, and machine-learning pipeline. Inspect for Chapters 43–50; note that Jesse's feature set must be verified per feature. **Done — Part G. MIT, adaptation permitted. Per-feature verification changed three advertised claims: optimization is random search with Optuna used only as a trial store (not Optuna-driven), the "random-entry variants" significance test is actually a stationary bootstrap, and the catalog is 174 indicators, not "300+". Its stationary-bootstrap significance test is the strongest statistical artifact in any reference and is the one mechanism worth adapting for 43.2.**
- [x] **TA-Lib** (`external/ta-lib`): study the indicator catalog and naming. It is a C library; check whether the Python wrapper is available as a Debian package before use. Indicator requirements remain defined by Chapter 31. **Done — Part H. The checkout is the C core only (no Python wrapper source); no `python3-talib`/`libta-lib` in Debian 13 sources, so the working default is study-only. The 201-function catalog is a naming and metadata reference, not a backlog — Chapter 31 says not to add dozens of indicators without tests.**
- [x] **VectorBT** (`external/vectorbt`): study vectorized backtesting, walk-forward optimization, and portfolio analytics concepts. Inspect for Chapters 37 and 45; verify Debian/PyPI packaging. **Done — Part C.**
- [x] **Advances in Financial Machine Learning — exercises** (`external/adv-financial-ml-marcos-exercises`): study the exercise solutions and the book's own snippets: event-based bars, triple-barrier labeling, sample weighting, purged/embargoed cross-validation, feature importance, and parallelization. Reference for Chapters 29, 38, and 43–50; the code is MIT-licensed and may be adapted with attribution after review and testing. **Done — Part A, with the A.8 adoption checklist.**
- [x] **Advances in Financial Machine Learning** (Marcos López de Prado, Wiley, 2018) — the printed reference behind the exercise repository. Conceptual authority for Chapters 43–50, especially the False Strategy theorem, the Deflated Sharpe Ratio, the Probability of Backtest Overfitting, and combinatorial purged cross-validation. Verify every technique against the exercise repository before implementing it. **Study complete — every technique mapped in `afml-techniques.md`, whose entries carry no blocking open questions, and the exhibit compilation is inventoried in A.9. The "verify before implementing" clause is a standing rule that applies at implementation time (see `AGENTS.md` rule 6), not an open deliverable of this chapter.**

- [x] Document the conclusions of this study in `docs/en/developers/reference-projects.md`. **Parts A–H.**
- [x] When studying each reference project, explicitly note which mechanisms protect capital (risk limits, position sizing, kill switches, dry-run modes, conservative defaults) and which mechanisms only optimize historical performance. Only the former may be adopted for capital-protection features; the latter belong to research chapters (Chapters 39, 44–45). **Every Part carries that section. Recurring finding: none of the six trading frameworks enforces its own limits — Freqtrade's protections only lock entries and are opt-in, Hummingbot's kill switch ships disabled, and Jesse's helpers are optional library calls a strategy can bypass. That is the gap Chapters 58–59 exist to close.**

# PART II — MARKET DATA

---

## [~] 26. Market-data sources and exchange adapters

Create an `ExchangeAdapter` interface or equivalent.

It must define separate operations for:

- [x] retrieving markets;
- [x] retrieving tickers;
- [x] retrieving historical candles;
- [x] subscribing to tickers;
- [x] subscribing to candles;
- [x] subscribing to trades;
- [x] subscribing to the order book;
- [x] retrieving balances;
- [x] retrieving orders;
- [x] creating an order;
- [x] cancelling an order;
- [x] receiving order updates;
- [x] checking API permissions.

### 26.1 MockExchange

Implement a fully local provider for:

- [x] automated tests;
- [ ] demonstrations;
- [x] paper trading.
- [x] historical replay;
- [x] simulated failures;
- [x] simulated disconnections;
- [x] simulated latency;
- [x] simulated slippage;
- [x] partially filled orders;
- [x] rejected orders;
- [x] rate-limit simulations.

### 26.2 Binance Spot Testnet

Add initial support for Binance Spot Testnet using current official documentation.

- [x] Endpoints must be configurable.
- [x] Do not scatter endpoint strings throughout the codebase.

Include:

- [x] REST;
- [x] WebSocket;
- [x] automatic reconnection;
- [x] ping/pong handling;
- [x] connection renewal;
- [x] rate-limit management;
- [x] time synchronization;
- [x] out-of-order message detection;
- [x] duplicate message tolerance;
- [x] secure logging.

- [x] Do not implement Binance Futures.

*Wiring note (2026-10-28).* The client is a real feed, not a placeholder:
`start()` schedules the runner and returns, the watchdog detects silence
without waiting for a message, connection renewal closes and reopens the
socket, and duplicate/out-of-order detection is per stream. `run_paper_session_live()`
runs a bounded session over it with the chapter-58 risk gate, and
`crypto-trading-lab paper-live` exposes it from the CLI. A session never
evaluates a signal while the feed is DEGRADED (chapter 27).

### 26.3 Coinbase

**Not implemented.** The native read-only adapter was removed on
2026-09-27: nothing imported it, its WebSocket client was a placeholder
(`start()` never connected, `stop()` was declared twice so the synchronous
one silently overrode the async one) and its REST path recorded
circuit-breaker *successes before the request*, so the breaker could never
open. Coinbase can be reached through the optional CCXT adapter, which is a
PyPI-only dependency; on 2026-09-27 that path was verified live to return
normalised (Decimal + UTC) Binance **and** Coinbase candles through
`CcxtExchangeAdapter.fetch_candles()`, but it is not exposed in the UI. See
`docs/en/developers/venv-setup.md` §7 and
`docs/en/developers/unwired-modules-audit.md`. Preserve this
warning for whenever it is rebuilt: the Coinbase sandbox may return static
or predefined data and must not be treated as a realistic profitability
simulation.

Initially add:

- [ ] public market data;
- [ ] an architecture prepared for Advanced Trade (the `ExchangeAdapter` port already exists — chapter 6.2);
- [ ] clearly labeled experimental support.

- [ ] Document that the sandbox may return static or predefined data and must not be treated as a realistic profitability simulation.
- [ ] Do not mix Coinbase-specific models with the central domain.

---

## [x] 27. Connection state management

Create a connection state machine with:

- [x] DISCONNECTED
- [x] CONNECTING
- [x] AUTHENTICATING
- [x] SUBSCRIBING
- [x] CONNECTED
- [x] DEGRADED
- [x] RECONNECTING
- [x] RATE_LIMITED
- [x] ERROR
- [x] STOPPED

Implement:

- [x] exponential backoff with jitter;
- [x] a maximum number of consecutive retries;
- [x] a circuit breaker;
- [x] stale-data detection;
- [x] subscription recovery;
- [x] reconciliation after reconnection;
- [x] visible warnings when data is outdated.

- [x] Never generate buy or sell signals from stale data.

Every connection state must have:

- [x] a technical description;
- [x] a beginner-friendly explanation;
- [x] a visible status label;
- [x] a troubleshooting link. (Every state links to its own section of `docs/en/user-guide/20-troubleshooting.md`; a test resolves each link and its anchor, so a renamed heading fails the suite instead of the user.)

---

## [~] 28. Data import

Allow candle import from CSV.

Provide a wizard for mapping:

- [x] timestamp;
- [x] open;
- [x] high;
- [x] low;
- [x] close;
- [x] volume;
- [x] symbol;
- [x] interval.

Validate:

- [x] duplicate timestamps;
- [x] unordered timestamps;
- [x] irregular intervals;
- [x] negative values;
- [x] high below low;
- [x] open outside the high-low range;
- [x] close outside the high-low range;
- [x] missing values;
- [x] unknown timezone;
- [x] unrecognized columns.

- [x] Display a summary before importing.
- [ ] Include a beginner explanation of OHLCV columns.

---

## [ ] 29. Data quality management

Market data quality is a research prerequisite, not an afterthought.

The system must support:

- [x] dataset identity and versioning (dataset ID, dataset version, source, exchange, pair, interval, time range);
- [x] dataset checksums for reproducibility (see Chapter 53);
- [x] validation on import and on storage (see Chapter 28);
- [x] detection of gaps and missing candles;
- [x] detection of duplicate candles;
- [x] detection of out-of-order timestamps;
- [x] detection of invalid OHLCV values;
- [x] detection of stale or frozen data;
- [x] detection of suspicious volume anomalies where data allows;
- [x] handling of delisted assets where historical data is available;
- [x] handling of changes in market liquidity where historical data is available;
- [x] explicit handling of survivorship bias when composing datasets;
- [x] a visible data-quality report per dataset;
- [x] warnings when a dataset is incomplete for the requested analysis.

- [x] Every research result must record the exact dataset version and checksum used (see Chapters 38, 52, and 53).
- [x] The application must never silently fill missing candles in a way that could affect research conclusions; any filling policy must be explicit, documented, and recorded.

### 29.1 Advanced bar types (research)

Beyond time-based candles, the system may support event-based bars for research (see 49.1):

- [x] volume bars (a new bar after a fixed amount of volume);
- [x] dollar bars (a new bar after a fixed traded value);
- [ ] imbalance bars where the data source provides trade-level data;
- [x] every bar type must be a first-class dataset with its own ID, version, and checksum;
- [x] bar construction must record its thresholds and parameters;
- [x] event-based bars must be clearly distinguishable from time candles in the UI and the database;
- [x] missing-data policies for event-based bars must be explicit (their cadence is irregular by design and must not be treated as gaps in a time series).

---

# PART III — MARKET MODEL

---

## [~] 30. Market precision and exchange rules

Every exchange adapter must retrieve and respect:

- [x] minimum quantity;
- [x] minimum order value/notional;
- [ ] tick size;
- [ ] step size;
- [x] price precision;
- [x] quantity precision;
- [x] supported order states;
- [x] supported order types;
- [x] known fees;
- [ ] rate limits;
- [x] timestamp formats;
- [ ] time synchronization requirements.

Before creating an order:

- [x] 1. normalize the price;
- [x] 2. normalize the quantity;
- [ ] 3. apply tick-size rules;
- [ ] 4. apply step-size rules;
- [x] 5. verify minimum notional value;
- [x] 6. estimate fees;
- [x] 7. verify available balance;
- [ ] 8. verify risk limits;
- [ ] 9. verify market-data freshness;
- [x] 10. verify connection state;
- [ ] 11. prevent duplicate orders;
- [ ] 12. create an idempotency identifier;
- [ ] 13. produce a beginner-readable explanation of any rejection.

---

## [~] 31. Technical indicators

Initially implement:

- [x] SMA;
- [x] EMA;
- [x] RSI;
- [x] MACD;
- [x] Bollinger Bands;
- [x] ATR;
- [x] ROC;
- [ ] historical volatility;
- [ ] average volume;
- [ ] rolling highs and lows;
- [x] drawdown.

Every indicator must:

- [x] use a common interface;
- [x] validate parameters;
- [x] document its formula;
- [x] describe its warm-up period;
- [x] handle missing values;
- [x] avoid look-ahead bias;
- [x] support batch calculation;
- [ ] support incremental updates where practical;
- [x] include tests using small datasets with manually verifiable results.

- [ ] Do not add dozens of indicators without tests.

Every indicator must also include beginner documentation:

- [x] what it measures;
- [x] what its name means;
- [ ] a plain-language explanation;
- [x] common parameter values;
- [x] typical misuse;
- [x] limitations;
- [x] a visual example;
- [x] a warning that it does not guarantee future price movements.

---

## [~] 32. Financial charts

Implement charts for:

- [x] OHLC candlesticks;
- [x] volume.
- [ ] price lines;
- [x] moving averages;
- [ ] bands;
- [ ] RSI;
- [ ] MACD;
- [ ] entry points;
- [ ] exit points;
- [ ] stop-loss levels;
- [ ] take-profit levels;
- [ ] equity curves;
- [ ] drawdowns;
- [ ] return distributions.

Requirements:

- [x] zoom;
- [x] panning;
- [x] crosshair;
- [x] OHLC information under the cursor;
- [ ] interval selection;
- [x] auto-scaling;
- [ ] optional logarithmic scale;
- [ ] incremental updates;
- [x] do not rebuild the entire chart on every tick;
- [x] limit the number of visible points;
- [x] separate chart data from visual representation;
- [x] handle missing time intervals correctly.

- [ ] Do not update widgets directly from worker threads.
- [ ] Workers must emit Qt signals containing immutable data or safe copies.

Each chart must include an optional beginner explanation panel describing:

- [x] what the chart shows;
- [x] how to read it;
- [x] what beginners often misunderstand;
- [x] what the chart cannot predict;
- [x] a simple example;
- [x] a glossary link.

# PART IV — STRATEGIES AND SIGNALS

---

## [~] 33. Strategies

Strategies must use explicit, testable, versioned, and declarative rules.

The purpose of a strategy is to define **when a trading signal should be generated**. A strategy must not be responsible for exchange communication, order execution, credential handling, or direct risk-limit modification.

Initial strategies:

* [x] 1. Moving-average crossover.
* [x] 2. RSI with configurable filters.
* [x] 3. Rolling high/low breakout.
* [x] 4. Bollinger Bands mean reversion as an educational example.
* [x] 5. Buy-and-hold benchmark.
* [x] 6. Null strategy that never trades.

Each strategy must declare:

### 33.1 Identity

* [ ] Name.
* [ ] Unique identifier.
* [ ] Version.
* [ ] Author or source.
* [ ] Description.
* [ ] Strategy category.
* [ ] Beginner-oriented explanation.
* [ ] Known weaknesses.
* [ ] Risk warnings.

### 33.2 Market requirements

* [ ] Compatible markets.
* [ ] Supported asset types.
* [ ] Required timeframe.
* [ ] Required market-data fields.
* [ ] Required indicators.
* [ ] Warm-up period.
* [ ] Minimum amount of historical data required.

### 33.3 Trading rules

* [ ] Entry conditions.
* [ ] Exit conditions.
* [ ] Invalidation conditions.
* [ ] Stop-loss rules.
* [ ] Take-profit rules.
* [ ] Trailing-stop rules where applicable.
* [ ] Cooldown rules.
* [ ] Time-based restrictions where applicable.
* [ ] Position-sizing rules (subject to the risk manager; see Chapter 58).

### 33.4 Parameters

Every configurable parameter must define:

* [x] Name.
* [x] Type.
* [x] Default value.
* [x] Minimum value.
* [x] Maximum value.
* [x] Allowed values where applicable.
* [x] Description.
* [x] Validation rules.
* [x] Parameters must be versioned with the strategy.
* [x] Invalid parameter combinations must be rejected before execution.
* [x] Strategy parameters must never silently change during a backtest or live session.

**Implemented 2026-10-31.** `strategy_parameters.py` holds the contract:
`ParameterSpec` (name, kind, default, bounds, allowed values, description,
rule text), `ParameterSchema` (the specs one version declares, plus
`CombinationRule`s for checks no single parameter can express) and
`ParameterSet` (validated, frozen, with a `signature()`).

`StrategyRegistry.create_instance()` and `parameter_set()` validate through
the schema, so every entry point — CLI, GUI, application services — is
covered: values are coerced (`"20"` → `20`, `True` is rejected as a number),
bounds and combinations are enforced (`fast < slow`, `oversold <
overbought`), and a misspelt parameter raises instead of being swallowed.
The application layer stopped re-implementing those checks by hand.

The values that ran are recorded: `ParameterSet.signature()` →
`ma_crossover@1.0.0(fast=5, slow=20)` goes into
`BacktestConfig.strategy_parameters`, lands in
`BacktestResult.config_metadata`, and the CLI prints it. The set is frozen,
and `run_backtest()` snapshots the strategy's dataclass fields before the
loop and raises if they changed, so a parameter cannot move silently even by
the strategy's own hand (internal streaming state is not a dataclass field
and is not confused with a parameter).

Two limits, stated so they are not mistaken for gaps: combination rules are
callables and do not survive the JSON round trip (an imported strategy is
validated parameter by parameter until its owner registers it again), and a
stored schema with no `default` keeps `parameter_schema=None` rather than
refusing to load the registry. Documented in
`docs/en/developers/strategy-parameters.md`.

### 33.5 Signal generation

Strategies must generate explicit signals such as:

* [x] Enter long.
* [x] Exit long.
* [ ] Enter short where supported.
* [ ] Exit short where supported.
* [x] Hold.
* [x] No signal.

Signals must include:

* [x] Timestamp.
* [x] Strategy identifier.
* [x] Strategy version.
* [x] Market.
* [x] Timeframe.
* [x] Signal type.
* [x] Relevant indicator values.
* [x] Strategy parameters or parameter-set identifier.

**Implemented 2026-10-31.** `signals.py` holds the vocabulary
(`SignalType`) and the record (`Signal`, frozen). The engine now writes one
record per candle into `BacktestResult.signals`, stamped with the strategy
id and version, the market and timeframe taken from the candle, the type,
the indicator values the decision was taken on, and the chapter 33.4
parameter signature (`ma_crossover@1.0.0(fast=5, slow=20)`) — the
parameter-set identifier, not a second copy of the values.

Two distinctions the record keeps instead of collapsing them:
**hold vs no signal** (`None` from a strategy in a position is *hold*;
`None` flat is *no signal*), and **the decision vs what the engine could
act on** (`actionable` is false for a BUY while already long, because the
MVP engine is long-only spot). Indicator values come from each strategy's
`indicator_values()`, so a record can be re-read without re-running the
strategy.

`enter_short`/`exit_short` stay **unticked on purpose**: the names exist in
the vocabulary and are rejected by `Signal` if mistyped, but no strategy can
emit them because the engine has no short side yet. Adding the enum member
is not the feature the chapter asks for ("where supported"); the box opens
the day a short-capable engine does. Documented in
`docs/en/developers/signal-records.md`.

### 33.6 Mandatory architecture

The execution flow must be:

```text
Market Data
    ↓
Strategy
    ↓
Signal
    ↓
Portfolio / Risk Manager
    ↓
Approved Order Request
    ↓
Execution Engine
    ↓
Broker / Exchange
```

* [ ] Strategies generate signals but do not create exchange orders directly.
* [ ] No strategy may communicate directly with an exchange API.
* [ ] No strategy may bypass the `RiskManager`.
* [ ] No strategy may modify global risk limits.
* [ ] No strategy may access API credentials directly.

### 33.7 Strategy validation

Before a strategy can be backtested or paper-traded:

* [ ] Validate its configuration.
* [ ] Validate its required indicators.
* [ ] Validate its timeframe.
* [ ] Validate its warm-up period.
* [ ] Validate its market compatibility.
* [ ] Validate all parameters.
* [ ] Detect impossible or contradictory rules.
* [ ] Report warnings before execution.

### 33.8 Strategy research warnings

The application must warn users that:

* [ ] A strategy can perform well historically by chance.
* [ ] More parameters increase the risk of overfitting.
* [ ] Adding filters does not necessarily improve a strategy.
* [ ] A higher historical profit does not necessarily mean a better strategy.
* [ ] A strategy must be evaluated on data that was not used to design or optimize it.
* [ ] Strategy complexity should be recorded (see Chapter 35).
* [ ] The system should favor simpler strategies when performance is otherwise comparable.

### 33.9 Beginner documentation

Every strategy must explain:

* [ ] What the strategy attempts to do.
* [ ] What market behavior it assumes.
* [ ] What indicators it uses.
* [ ] What causes an entry.
* [ ] What causes an exit.
* [ ] How position sizing works.
* [ ] How stop-loss and take-profit work.
* [ ] What market conditions may favor it.
* [ ] What market conditions may hurt it.
* [ ] Why historical profitability does not guarantee future profitability.

---

## [ ] 34. Visual strategy builder

Create a basic no-code strategy builder using blocks or forms for:

- [ ] indicator;
- [ ] operator;
- [ ] value;
- [ ] crossover;
- [ ] AND condition;
- [ ] OR condition;
- [ ] entry;
- [ ] exit;
- [ ] stop-loss;
- [ ] take-profit;
- [ ] time filter;
- [ ] volatility filter;
- [ ] cooldown.

- [ ] Do not use `eval()`.
- [ ] Convert rules into a validated expression tree.

Allow users to:

- [ ] save;
- [ ] duplicate;
- [ ] export;
- [ ] import;
- [ ] validate;
- [ ] view a natural-language explanation;
- [ ] view a beginner-friendly explanation;
- [ ] view warnings about possible overfitting.

- [ ] Use a versioned schema for strategy files.

---

## [~] 35. Strategy complexity control

The system must consider strategy complexity explicitly.

- [x] Record for every strategy version:
  - [x] number of parameters;
  - [x] number of rules;
  - [x] number of indicators;
  - [x] number of filters;
  - [x] number of conditions;
  - [x] optimization complexity;
  - [x] model complexity where machine learning is used (see Chapter 48).

- [ ] A strategy with many parameters, indicators, and filters must not be considered automatically superior to a simpler one.
- [ ] When two strategies provide comparable evidence, the simpler strategy must be favored.
- [x] Complexity metrics must be displayed in strategy reports and qualification reviews (see Chapter 66).
- [ ] The application must warn when complexity grows without a corresponding evidence improvement.

**Honest state (2026-10-31).** `complexity_control.StrategyComplexity`
records the seven items per version: the registry stores them with each
registration and recomputes the parameter count, the grid and the version
when `update_metadata()` changes them; declarative rules derive them from
the rule itself. The record is shown in the Backtesting Lab report
("What this strategy version declares") and in the chapter 66 qualification
criterion, which now carries `score=…` and the breakdown instead of a bare
boolean.

The two decision rules exist, are tested and are documented in
`docs/en/developers/strategy-complexity.md` — `prefer_simpler()` (comparable
evidence → lower complexity wins) and `complexity_growth_warning()` (growth
without better evidence) — but **no screen calls them yet**: the application
still has no view that compares two strategies side by side (the registry
comparison of chapter 36 is open). They are therefore left unticked: the
rule is written down and exercised by tests, not yet part of a user's
decision.

Two deliberate limits, stated so nobody mistakes them for bugs. A parameter
with no declared bounds counts as one setting rather than a guessed range,
and the rule language declares no bounds at all, so a rule's
`optimization_complexity` is `1` — unknown is reported as unknown. And the
`score` weights are a stated convention (4·parameters + 2·indicators +
2·filters + rules + conditions + order of magnitude of the grid), not a
measurement of quality.

---

## [~] 36. Strategy registry

The system must maintain a central registry of strategies and their evidence.

Each strategy must be able to record:

- [x] strategy ID;
- [x] name;
- [x] version;
- [ ] code/configuration;
- [x] parameters;
- [ ] datasets used;
- [ ] results (from backtest metrics);
- [ ] benchmarks;
- [ ] validations;
- [ ] robustness tests;
- [ ] experiment history (see Chapter 52);
- [ ] status;
- [ ] qualification report reference (see Chapter 66);
- [ ] complexity metrics (see Chapter 35).

**Honest state (2026-10-07).** `StrategyRegistry` now stores the ID, name,
version and parameter schema of each strategy, and the Backtesting Lab and
the CLI read it instead of hard-coding a list. Nothing else on the list
above is stored: `ExperimentRecord` carries a free-text strategy name and
version but no registry ID, so no result, dataset, benchmark, validation or
robustness report is actually linked to a strategy yet. Only the four boxes
ticked above are backed by code today.

Suggested statuses:

```text
Draft
Research
Backtested
Validated
Paper Trading
Qualified
Rejected
Retired
Live
```

- [ ] Status transitions must follow the promotion pipeline (see Chapter 65).
- [ ] A strategy must never skip from `Backtested` directly to `Live`.
- [ ] Every status change must be audited with timestamp and reason.
- [ ] The registry must support searching, filtering, and comparing strategies.
- [ ] The registry must clearly distinguish a strategy's current status from its historical statuses.

---

# PART V — BACKTESTING AND VALIDATION

---

## [~] 37. Backtesting

The backtesting engine must be deterministic, reproducible, realistic, and explicitly protected against look-ahead bias and other forms of historical-data leakage.

A backtest must simulate the complete sequence from market data to signal, risk decision, order creation, execution, position update, and portfolio valuation.

### 37.1 Capital and trading costs

The engine must support:

* [x] Initial capital.
* [x] Commissions.
* [x] Trading fees.
* [x] Spread.
* [x] Slippage.
* [ ] Funding costs where applicable (not applicable to the spot-only MVP).
* [ ] Borrowing costs where applicable.
* [x] Configurable trading costs.
* [ ] Cost changes over time where historical fee data is available.

The report must show:

* [x] Total commissions and fees.
* [x] Estimated spread cost.
* [x] Estimated slippage cost.
* [ ] Other applicable trading costs.
* [x] Performance before costs.
* [x] Performance after costs.

### 37.2 Market and exchange constraints

The engine must model, where applicable:

* [ ] Available liquidity.
* [ ] Maximum position size.
* [x] Minimum order quantity.
* [x] Minimum order value/notional.
* [ ] Tick size.
* [x] Step size.
* [ ] Price precision.
* [x] Quantity precision.
* [ ] Exchange-specific trading constraints.
* [ ] Market-specific restrictions.

The backtest must never assume that an arbitrary quantity or price can be submitted to an exchange.

### 37.3 Order types

The engine must support, at minimum:

* [x] Market orders.
* [ ] Limit orders.
* [ ] Stop orders.
* [ ] Stop-loss.
* [ ] Take-profit.
* [ ] Trailing stop.
* [ ] Partial fills.
* [ ] Rejected orders.
* [ ] Order cancellation where applicable.

### 37.4 Execution simulation

The engine must explicitly model the difference between:

```text
Signal generated
        ↓
Order requested
        ↓
Order accepted/rejected
        ↓
Order executed
        ↓
Position updated
```

It must support:

* [ ] Simulated execution latency.
* [x] Conservative slippage assumptions.
* [x] Spread.
* [ ] Available liquidity.
* [ ] Partial execution.
* [ ] Rejected orders.
* [ ] Delayed execution.
* [ ] Order cancellation.
* [ ] Different execution models.

Implement at least two execution models:

* [x] 1. Execution at the opening price of the next candle.
* [ ] 2. A documented conservative intrabar execution model.

The selected execution model must be recorded in every backtest.

- [ ] Advanced execution realism (fills, latency, liquidity models) is specified in Chapter 56 and must remain a separate component.

### 37.5 Intrabar ambiguity

When historical data does not provide enough information to determine the exact sequence of events inside a candle:

* [ ] Never invent an execution sequence.
* [ ] Use a configurable conservative policy.
* [ ] Document the policy.
* [ ] Record the policy in the backtest metadata.
* [ ] Clearly identify ambiguous executions in the report.

When a candle reaches both stop-loss and take-profit during the same interval:

* [ ] Apply the configured conservative policy.
* [ ] Record which policy was used.
* [ ] Never assume an execution order that cannot be established from the available data.

### 37.6 Historical data handling

The engine must correctly handle:

* [ ] Missing data.
* [ ] Missing candles.
* [ ] Incomplete candles.
* [ ] Duplicate candles.
* [ ] Out-of-order timestamps.
* [ ] Invalid OHLCV values.
* [ ] Zero or invalid volume where applicable.
* [ ] Chronological data ordering.
* [ ] Warm-up periods.
* [ ] Dataset boundaries.
* [ ] Delisted assets where historical data is available.
* [ ] Changes in market liquidity where historical data is available.

All internal timestamps must use a clearly defined convention, preferably UTC.

- [ ] Data-quality policies are specified in Chapter 29 and must be shared with the backtest engine.

### 37.7 Bias and leakage prevention

The engine must explicitly prevent:

* [ ] Look-ahead bias.
* [ ] Data leakage.
* [ ] Survivorship bias where applicable.
* [ ] Future information entering historical signals.
* [ ] Future candles being used to calculate historical indicators.
* [ ] Using a known closing price to execute at that same close without an explicit model.
* [ ] Assuming all orders execute instantly.
* [ ] Ignoring commissions, fees, spread, slippage, or liquidity constraints.

> **The backtesting engine must never use information that was unavailable at the exact moment when the simulated trading decision was made.**

### 37.8 Determinism and reproducibility

A backtest must produce the same result when executed again with the same:

* [ ] Dataset version.
* [ ] Strategy version.
* [ ] Strategy parameters.
* [ ] Initial capital.
* [ ] Fee configuration.
* [ ] Spread configuration.
* [ ] Slippage configuration.
* [ ] Execution model.
* [ ] Software configuration.
* [ ] Random seed when randomness is used.

Every backtest must record enough metadata to reproduce the experiment (see Chapter 53).

### 37.9 Backtest results

Every backtest must record:

* [x] Initial capital.
* [x] Final equity.
* [x] Net profit/loss.
* [x] Total return.
* [x] Number of trades.
* [x] Win rate.
* [x] Average winning trade.
* [x] Average losing trade.
* [x] Profit factor.
* [x] Maximum drawdown.
* [x] Maximum drawdown duration.
* [x] Sharpe ratio where statistically appropriate.
* [x] Sortino ratio where statistically appropriate.
* [x] Buy-and-hold performance (see Chapter 42).
* [x] Total commissions/fees.
* [x] Estimated slippage.
* [x] Execution model.
* [x] Dataset period.
* [x] Dataset version.
* [x] Strategy version.
* [x] Strategy parameters.

- [x] Metric definitions and statistical validity rules are specified in Chapter 40.

### 37.10 Beginner-oriented explanation

Every backtest result must explain:

* [x] What was tested.
* [x] Which asset and timeframe were tested.
* [x] Which strategy and parameters were used.
* [x] Which historical period was used.
* [x] What assumptions were made.
* [x] Which execution model was used.
* [x] What commissions and fees mean.
* [x] What spread and slippage mean.
* [x] Why liquidity affects execution.
* [x] Why historical results can be misleading.
* [x] Why backtesting cannot guarantee future profitability.
* [x] Why real trading results may differ.
* [x] Whether the result is in-sample, validation, or out-of-sample.

- [x] A profitable backtest must never be presented as proof that a strategy will be profitable in the future.

---

## [~] 38. Data splitting

Financial time-series data must be divided chronologically.

The system must support at least:

* [x] Training (strategy-development) period.
* [x] Validation period.
* [x] Out-of-sample test period.

The default data flow must be:

```text
Historical Data
      ↓
Training (Strategy Development)
      ↓
Validation
      ↓
Out-of-Sample Test
```

### 38.1 Chronological integrity

* [x] Never randomly shuffle financial time-series data for strategy evaluation. (splitting is deterministic; shuffled input is rejected)
* [x] Preserve temporal ordering.
* [x] Prevent future observations from entering earlier periods.
* [x] Respect dataset boundaries.
* [x] Respect indicator warm-up periods. (borrowed warm-up prefixes, excluded from the recorded boundaries)
* [x] Record the exact timestamp boundaries of every split.

### 38.2 Training (strategy-development) period

This period may be used for:

* [ ] Strategy development.
* [ ] Indicator selection.
* [ ] Rule development.
* [ ] Initial parameter selection.
* [ ] Hypothesis generation.

It must not be presented as independent evidence of future performance.

### 38.3 Validation period

The validation period may be used for:

* [ ] Comparing candidate strategies.
* [ ] Selecting among limited parameter sets.
* [ ] Detecting obvious overfitting.
* [ ] Refining a research hypothesis.

Repeated use of the validation set must be recorded because it can gradually become part of the optimization process.

### 38.4 Out-of-sample test period

The out-of-sample period must:

* [ ] Remain isolated from strategy development as much as possible.
* [ ] Not be used repeatedly for parameter selection.
* [ ] Be used as the final historical evaluation of a strategy version.
* [ ] Be clearly identified in reports.

### 38.5 Data leakage protection

The system must detect or warn about:

* [x] Indicators calculated using future data. (engine guarantee: signals at close i fill at open i+1, ch. 37)
* [x] Features containing future observations. (same construction)
* [ ] Optimization using the test period. — pending: optimization is chapter 39; the evaluation log is the guardrail in place.
* [x] Repeated evaluation of the test period. (`DatasetSplit.record_evaluation` warns from the second use)
* [x] Using future market information. (same construction as above)
* [x] Randomized time-series splitting. (never shuffles; shuffled input is rejected)
* [x] Incorrect warm-up handling. (borrowed prefixes excluded from recorded boundaries)

### 38.6 Optimization separation

When a strategy has been optimized:

* [ ] The optimization period must be recorded.
* [ ] The validation period must be recorded.
* [ ] The out-of-sample period must be recorded.
* [ ] The application must warn if the same period is used for both optimization and final evaluation.

- [ ] Rolling-window validation (walk-forward) is a distinct concept and is specified in Chapter 45.

### 38.7 Beginner explanation

The application must explain:

* [x] Why historical data is divided.
* [x] Why testing on the same data used for optimization is misleading.
* [x] What out-of-sample means.
* [x] Why repeatedly checking the test period can cause overfitting.
* [x] Why chronological order matters.
* [x] Why good out-of-sample performance is stronger evidence than in-sample performance.

The system must clearly distinguish:

> **“The strategy worked on historical data used to design it”**

from:

> **“The strategy continued to work on data that was not used to design it.”**

### 38.8 Purged and embargoed cross-validation (research)

Standard K-Fold cross-validation is invalid for financial time series when labels overlap in time (e.g., multi-bar holding periods) or when features are serially dependent.

The system may support, as a research capability (see 49.4):

- [ ] purged cross-validation: remove training observations whose label windows overlap validation-label windows;
- [ ] embargo: additionally delete a documented buffer after each validation block before resuming training;
- [ ] the embargo length must be an explicit, recorded parameter, never implicit;
- [ ] warn whenever labels span multiple bars and plain K-Fold or plain walk-forward splits are requested, because leakage is likely;
- [ ] explain in beginner terms why a trade that is still open at a boundary leaks information across it.

---

## [ ] 39. Parameter optimization

Parameter optimization is a research tool, not a guarantee of better future performance.

Initially include:

* [ ] Limited grid search.
* [ ] Limited random search.

Do not include unrestricted automatic optimization in the MVP.

### 39.1 Optimization inputs

Every optimization experiment must record:

* [ ] Strategy version.
* [ ] Parameter ranges.
* [ ] Parameter combinations.
* [ ] Dataset version.
* [ ] Optimization period.
* [ ] Validation period.
* [ ] Out-of-sample period.
* [ ] Initial capital.
* [ ] Fee configuration.
* [ ] Slippage configuration.
* [ ] Execution model.
* [ ] Random seed where applicable.

### 39.2 Safety limits

The optimizer must enforce:

* [ ] Maximum number of combinations.
* [ ] Maximum execution time where practical.
* [ ] Maximum memory usage where practical.
* [ ] Cancel button.
* [ ] Progress indicator.
* [ ] Background execution.
* [ ] Safe cancellation.
* [ ] Persisted results.

### 39.3 Optimization objective

The optimizer must not select a strategy solely because it has the highest net profit.

Supported objectives may include:

* [ ] Net profit.
* [ ] Total return.
* [ ] Maximum drawdown.
* [ ] Profit factor.
* [ ] Sharpe ratio where appropriate.
* [ ] Sortino ratio where appropriate.
* [ ] Calmar ratio where appropriate.
* [ ] Risk-adjusted return.
* [ ] Composite score.

The objective and ranking method must always be visible.

### 39.4 Overfitting protection

The optimizer must:

* [ ] Warn about excessive parameter combinations.
* [ ] Warn when parameter ranges are excessively broad.
* [ ] Penalize unnecessary complexity where appropriate (see Chapter 35).
* [ ] Compare in-sample and validation performance.
* [ ] Require out-of-sample evaluation before a strategy can be considered robust.
* [ ] Show performance degradation between datasets.
* [ ] Identify unstable parameter regions where practical.

### 39.5 Parameter stability

The system should identify whether:

* [ ] A broad region of parameters produces similar results.
* [ ] Performance depends on one extremely specific parameter combination.
* [ ] Small parameter changes cause large performance changes.
* [ ] The optimized result is substantially better than neighboring configurations.

A strategy whose performance exists only at one highly specific parameter combination must receive an overfitting warning.

### 39.6 Optimization results

Each experiment must preserve:

* [ ] Parameter set.
* [ ] Performance metrics.
* [ ] Dataset.
* [ ] Execution assumptions.
* [ ] Ranking objective.
* [ ] Optimization timestamp.
* [ ] Software version.
* [ ] Experiment identifier.

- [ ] Experiments must be recorded in the research experiment manager (see Chapter 52).

### 39.7 Beginner explanation

The application must explain:

* [ ] What parameter optimization is.
* [ ] Why optimization can help.
* [ ] Why optimization can also overfit historical data.
* [ ] Why the best historical parameter set is not necessarily the best future parameter set.
* [ ] Why out-of-sample testing is necessary.
* [ ] Why simpler parameter sets may be preferable.

> **Optimization searches historical possibilities. It does not predict which parameter values will be optimal in the future.**

# PART VI — PERFORMANCE, REPORTING, AND BENCHMARKING

---

## [~] 40. Performance metrics

The application must calculate performance metrics consistently, transparently, and with appropriate statistical safeguards.

No single metric must be presented as proof that a strategy is good, safe, or profitable in the future.

### 40.1 Return and profit metrics

Calculate where applicable:

* [x] Initial capital.
* [x] Final equity.
* [x] Net profit/loss.
* [x] Gross profit.
* [x] Gross loss.
* [x] Total return.
* [x] Annualized return.
* [x] Buy-and-hold return. (supplied as the benchmark run, see 40.5)
* [x] Excess return relative to benchmark.

### 40.2 Trade statistics

Calculate:

* [x] Number of trades.
* [x] Winning trades.
* [x] Losing trades.
* [x] Win rate.
* [x] Average winning trade.
* [x] Average losing trade.
* [x] Largest winning trade.
* [x] Largest losing trade.
* [x] Average trade.
* [x] Median trade where appropriate.
* [x] Profit factor.
* [x] Expectancy.
* [x] Average holding time.
* [x] Maximum consecutive wins.
* [x] Maximum consecutive losses.

### 40.3 Risk metrics

Calculate where statistically appropriate:

* [x] Maximum drawdown.
* [x] Maximum drawdown duration.
* [x] Average drawdown.
* [x] Volatility.
* [x] Downside volatility.
* [x] Sharpe ratio.
* [x] Sortino ratio.
* [x] Calmar ratio.
* [x] Risk-adjusted return.
* [x] Market exposure.
* [x] Long exposure.
* [ ] Short exposure where applicable. — pending: the chapter 37 engine
  is long-only spot by construction; there are no shorts to measure.

### 40.4 Trading activity

Calculate:

* [x] Turnover.
* [x] Number of orders.
* [ ] Number of rejected orders. — pending: the engine always fills
  or skips; rejections only exist once a paper-trading layer (ch. 57)
  can produce them.
* [ ] Number of partially filled orders. — pending: the engine fills
  all-or-nothing; partial fills require a more detailed fill model.
* [x] Commissions.
* [x] Trading fees.
* [x] Estimated spread cost.
* [x] Estimated slippage.
* [ ] Funding costs where applicable. — pending: spot trading has no
  funding; requires futures/margin support.

### 40.5 Benchmark comparison

- [x] Every applicable strategy evaluation must compare against a benchmark (see Chapter 42). — implemented via the `benchmark` argument of `compute_performance` (chapter 42 owns the benchmark *selection* policy).

The report must clearly distinguish:

* [x] Absolute performance.
* [x] Benchmark performance.
* [x] Difference from benchmark.

### 40.6 Statistical validity

The application must avoid displaying misleading metrics when there is insufficient data.

For example:

* [x] Do not present annualized metrics for inappropriate periods.
* [x] Do not present Sharpe or Sortino as reliable conclusions with insufficient observations.
* [x] Identify metrics affected by small sample sizes.
* [x] Display warnings when the number of trades is very small.
* [x] Distinguish descriptive statistics from statistically supported conclusions (see Chapter 43).

### 40.7 Metric configuration

Every metric must record:

* [x] Periodicity.
* [x] Annualization method where applicable.
* [x] Assumed risk-free rate where applicable.
* [x] Return calculation method.
* [x] Missing-data treatment.
* [x] Treatment of zero returns.
* [x] Relevant assumptions.

### 40.8 Documentation

Every metric must provide:

* [x] Technical definition.
* [x] Beginner-friendly definition.
* [x] Worked example.
* [x] Warning about misuse.
* [x] Explanation of whether higher or lower values are generally preferred.
* [x] Limitations.
* [x] Required assumptions.

Every report must explain:

> **No single metric proves that a strategy is good.**

Performance must be interpreted together with:

* [x] Risk.
* [x] Drawdown.
* [x] Trading costs.
* [x] Number of trades.
* [x] Market conditions.
* [x] Out-of-sample performance.
* [x] Robustness tests.

---

## [~] 41. Reports

Generate backtesting, paper-trading, research, and qualification reports in:

- [x] HTML;
- [x] CSV;
- [x] JSON;
- [ ] optional PDF. — pending: would require a new dependency; stdlib
  only so far. (Paper-trading/research/qualification reports will reuse
  `reporting.report` once chapters 52 and 57 exist.)

Reports must include:

- [x] strategy;
- [x] version;
- [x] parameters;
- [x] dataset checksum or identifier;
- [x] time range;
- [x] exchange;
- [x] trading pair;
- [x] interval;
- [x] initial capital;
- [x] fees;
- [x] slippage;
- [x] execution model;
- [x] metrics;
- [x] trades;
- [x] equity curve;
- [x] drawdown;
- [x] benchmark;
- [x] warnings;
- [x] Crypto Trading Lab version;
- [x] generation date.

- [x] Reports must not claim future profitability.
- [x] Include an optional beginner summary that explains the results in plain language.
- [x] Reports must clearly label the evidence level of any conclusion (observed result, statistical evidence, hypothesis, validated evidence; see Chapters 1 and 43). — backtest reports are labelled "observed result" (single in-sample run; descriptive only).
- [ ] Research and qualification reports must cite the experiment identifier (see Chapter 52). — pending: the experiment manager (ch. 52) does not exist yet.

---

## [~] 42. Benchmarking

The system must compare strategies against:

- [x] buy-and-hold;
- [x] simple benchmarks; (null strategy available)
- [ ] eventually other strategies. — `compare_reports()` accepts any
  strategy's report; the Lab UI offers buy-and-hold and null so far.

- [x] Do not assume that an active strategy is good simply because it makes money. (plain-language verdict in the comparison view)

Every comparison must ask:

> **Does the strategy offer enough improvement over a passive alternative, considering risk, costs, and complexity?**

### 42.1 Benchmark requirements

- [x] Same evaluation period for strategy and benchmark. (both are run on the same candles)
- [x] Same initial capital for strategy and benchmark. (shared `BacktestConfig`)
- [x] Comparable cost assumptions where appropriate. (shared `CostModel`)
- [x] Comparative performance metrics.
- [x] Relative performance.
- [x] Buy-and-hold must be the default benchmark for every strategy backtest.
- [x] The chosen benchmark must be recorded in every report. (chapter 41 report fields)
- [x] Benchmark selection must be visible and changeable by the user. (Backtesting Lab benchmark selector)
- [x] The application must warn when a benchmark is inappropriate for the strategy's market or timeframe. (identical-strategy benchmarks are flagged; other mismatches are impossible because both runs always share the same dataset)

### 42.2 Benchmark comparison views

- [ ] Equity curve comparison. — textual differences implemented
  (`compare_reports`); graphical overlay views pending.
- [ ] Drawdown comparison. — textual max-drawdown difference
  implemented; graphical underwater overlay pending.
- [x] Risk-adjusted comparison where appropriate. (Sharpe/Sortino
  differences, suppressed when statistically invalid)
- [x] Cost-adjusted comparison. (gross excess return + cost drag)
- [x] A plain-language summary of whether the active strategy beat the passive alternative.

- [ ] Benchmarking results feed the strategy qualification process (see Chapter 66). — pending: the qualification pipeline does not exist yet.

---

# PART VII — STATISTICAL RESEARCH AND ROBUSTNESS

---

## [~] 43. Statistical edge and evidence

The roadmap must incorporate a fundamental concept:

> **A historically profitable strategy does not necessarily have a real statistical edge.**

The system must allow investigating:

- [x] mathematical expectation;
- [x] distribution of returns;
- [ ] distribution of trades;
- [x] variability;
- [x] confidence;
- [x] uncertainty;
- [x] stability;
- [x] statistical significance where appropriate;
- [x] sample size;
- [x] temporal dependence;
- [x] autocorrelation;
- [x] bootstrap;
- [ ] sensitivity analysis;
- [x] comparison against benchmarks (see Chapter 42).

### 43.1 Evidence levels

The interface must distinguish:

```text
Observed result
Statistical evidence
Research hypothesis
Validated evidence
```

- [x] A single backtest result is an observed result, never validated evidence.
- [x] Statistical evidence requires explicit, documented methods and sufficient sample sizes.
- [x] A research hypothesis must always be labeled as such.
- [ ] Validated evidence requires out-of-sample, robustness, walk-forward, and qualification checks (see Chapters 44–46 and 66).
- [x] Account for the number of trials actually performed when interpreting a result: the more configurations tested, the more likely a good historical result is pure chance (the multiple-testing problem, related to the False Strategy theorem).
- [x] Support deflated performance evaluation as a research capability (see 49.5): correct Sharpe-ratio-type estimates for the number of trials, non-normal returns, and sample length before comparing strategies.
- [x] Where statistically justifiable, offer probabilistic statements about metrics (e.g., probabilistic Sharpe Ratio) instead of single-point values; label them as model-based estimates with their assumptions.

### 43.2 Statistical significance

- [x] Significance tests must only be applied when their assumptions are valid.
- [x] The application must warn when sample sizes are too small for a given test.
- [x] The application must warn about multiple-testing problems when many strategies or parameters are compared.
- [x] Never promise “significance” when the statistical assumptions are not satisfied.
- [x] Report effect size and uncertainty alongside any p-value where appropriate.
- [x] Prefer confidence intervals or bootstrap ranges over binary “significant / not significant” verdicts where practical.

### 43.3 Correlation and dependence

- [x] Check for autocorrelation in returns.
- [ ] Check for dependence between trades.
- [ ] Check for overlapping trade effects.
- [ ] Document the implications of dependence for statistical conclusions.

### 43.4 Distribution analysis

- [x] Plot and summarize return and trade distributions.
- [x] Compare observed distributions with appropriate reference distributions only when justified.
- [x] Do not assume normality without checking.
- [x] Explain heavy tails and skewness in plain language.

### 43.5 Interface and honesty

- [x] Every statistical analysis must include its assumptions and limitations.
- [ ] The interface must not present statistical tools as “proof of profitability”.
- [x] Statistical analyses are research features, not trading-signal generators.

---

## [~] 44. Robustness and sensitivity analysis

Robustness answers:

> **Does the result still exist when we change the conditions?**

Optimization (Chapter 39) finds configurations that worked on given data; robustness checks whether the result persists under changed conditions. Do not mix both responsibilities.

### 44.1 Robustness methods

The system must support:

- [x] parameter perturbation; (`perturb_sma_crossover`)
- [x] Monte Carlo simulation (see 44.4); (`monte_carlo_trades`)
- [x] bootstrap; (trade-level bootstrap inside the Monte Carlo runner)
- [ ] randomized execution; — pending (needs a fill-uncertainty model)
- [x] slippage variation; (`sweep_costs`)
- [x] fee variation; (`sweep_costs`)
- [ ] market variation; — pending (dataset variations)
- [x] out-of-sample degradation analysis; (`out_of_sample_degradation`)
- [x] sensitivity analysis.

### 44.2 Parameter perturbation

- [x] Perturb each parameter within a documented neighborhood. (±20% grid, explicated in the code)
- [x] Show how metrics change when parameters move away from the optimized values.
- [x] Identify parameter regions where performance collapses. (`collapsed` flag at <50% of the reference return)
- [x] Compare perturbed results against the optimized result. (`delta_vs_reference`)

### 44.3 Sensitivity analysis

- [x] Vary one factor at a time where appropriate. (cost multiplier sweep)
- [ ] Vary combinations of factors where practical. — pending
- [x] Sweep trading-cost assumptions (fees, slippage, spread). (`sweep_costs`)
- [ ] Sweep execution assumptions (latency, fill rate). — pending (needs randomized execution, 44.6)
- [ ] Sweep dataset variations (time ranges, markets) where appropriate. — pending
- [x] Present results as ranges or heatmaps, not single numbers. (sweeps return scenario rows, never a single point)

### 44.4 Monte Carlo simulation

Monte Carlo must clearly explain **what is being simulated**.

Supported modes may include:

- [x] reshuffling of trade sequences where statistically justifiable; (resampling with replacement)
- [x] bootstrap resampling of trades;
- [x] variation of results under alternative trade sequences;
- [ ] randomized slippage and fees; — pending (needs randomized execution, 44.6)
- [ ] execution uncertainty; — pending (44.6)
- [x] drawdown distributions; (p50/p95 of per-scenario max drawdown)
- [x] risk-of-ruin estimates (see Chapter 60). (fraction of scenarios hitting 50% capital)

Requirements:

- [x] The scenario definition must be explicit and documented. (`MonteCarloConfig`)
- [x] The random seed must be recorded. (`MonteCarloReport.seed`, deterministic)
- [x] The number of scenarios must be recorded.
- [x] The distribution of outcomes must be shown, not only the average. (percentile reports)
- [x] Confidence ranges must be labeled as estimates under the stated assumptions.
- [x] Warn when reshuffling destroys the temporal structure of the data and therefore may not be statistically justifiable.
- [x] Never present Monte Carlo as a prediction of the future. (both warnings are mandatory in every report)

### 44.5 Bootstrap

- [x] Support bootstrap resampling where statistically appropriate. (with-replacement trade resampling)
- [ ] Support block bootstrap for dependent data; document the block scheme and block length. — pending
- [ ] Report bootstrap confidence intervals with their assumptions. — percentiles land via 44.4's Monte Carlo report; formal CIs pending
- [ ] Warn when independence assumptions are violated. — pending

### 44.6 Randomized execution

- [ ] Support randomized execution simulations to test execution sensitivity. — pending
- [ ] Record the random seed and distribution used. — pending
- [ ] Compare execution-sensitive metrics across scenarios. — pending

### 44.7 Out-of-sample degradation

- [x] Compare in-sample, validation, and out-of-sample performance. (`out_of_sample_degradation`)
- [x] Quantify performance degradation between periods. (degradation = 1 − oos/train)
- [x] Flag strategies whose out-of-sample performance collapses.

### 44.8 Backtest overfitting probability (research)

The system may support estimation of the probability that a selected configuration is overfit (see 49.6):

- [ ] combinatorial cross-validation on the same data used for selection, comparing in-sample against symmetric out-of-sample performance;
- [ ] the probability of backtest overfitting (PBO) must always be reported together with the number of trials and the selection method;
- [ ] a high PBO must visibly degrade the evidence level of the result (see Chapter 43.1);
- [ ] explain in beginner terms: "how often would random pickers among these candidates have looked this good?";
- [ ] never present PBO as an exact probability of future failure — it is an estimate under stated assumptions.

### 44.9 Robustness report

- [x] Produce a robustness report summarizing all tests. (`compute_robustness_report`)
- [x] Include assumptions, seeds, and scenario counts.
- [ ] Feed results into strategy qualification (see Chapter 66). — pending

---

## [~] 45. Walk-forward analysis

Walk-forward must be clearly separated from a simple training/validation/test split (Chapter 38).

It must allow:

```text
Train
   ↓
Validate
   ↓
Forward Test
   ↓
Move Window
   ↓
Train
   ↓
Validate
   ↓
Forward Test
```

### 45.1 Requirements

- [x] Define rolling training windows.
- [ ] Define validation windows. — the current walker selects parameters
  on the training window and tests on the forward window; a separate
  validation stage inside each window is pending.
- [x] Define forward test windows.
- [x] Define the window step size.
- [x] Record every window. (`WindowResult` per window)
- [x] Prevent information from later windows entering earlier windows. (engine no-look-ahead + forward-only window generation)
- [x] Respect indicator warm-up periods at each window boundary. (borrow-only warm-up prefixes, boundaries stay exact)
- [x] Aggregate results across walk-forward periods. (compounded unit-stake aggregate, method documented)
- [x] Allow inspection of each individual period.
- [x] Show the distribution of per-window results, not only the aggregate. (`test_returns` per-window distribution)
- [x] Report the number of windows and their time coverage. (window count + exact boundaries per window)
- [x] Record the exact parameters selected per window.
- [x] Flag windows where the strategy degraded materially. (`degraded` flag, documented threshold)

### 45.2 Reproducibility

- [x] Record dataset version, strategy version, window configuration, and seed. (`WalkForwardReport` metadata; no randomness is used — recorded as such)
- [x] Re-running walk-forward with identical inputs must produce identical results. (tested determinism)

### 45.3 Combinatorial purged cross-validation (research)

Walk-forward uses one chronological path through history. As an optional research capability, the system may support combinatorial purged cross-validation (CPCV, see 49.4):

- [ ] generate multiple train/test combinations over the same historical period instead of a single path;
- [ ] apply purging and embargo (see 38.8) at every boundary;
- [ ] report the distribution of results across paths, not only the mean;
- [ ] record the combination scheme and the number of paths;
- [ ] explain that CPCV produces many more backtest paths from the same data, which raises re-use concerns that must be disclosed;
- [ ] CPCV complements, but does not replace, walk-forward and a final untouched out-of-sample period (Chapter 38.4).

### 45.4 Interpretation

- [x] Never present aggregate walk-forward results as proof of future profitability. (every report carries `WALK_FORWARD_NOTE`)
- [x] Explain that walk-forward reduces, but does not eliminate, overfitting risk.
- [ ] Feed walk-forward results into strategy qualification (see Chapter 66). — pending: qualification pipeline does not exist yet.

---

## [~] 46. Market regime analysis

Regime analysis studies different market conditions. It must not assume that regimes can be identified perfectly.

The system must support the analysis of:

- [x] trending; (`detect_trending_ranging`)
- [x] ranging; (`detect_trending_ranging`)
- [x] high volatility; (`detect_volatility_regime`)
- [x] low volatility; (`detect_volatility_regime`)
- [ ] high liquidity;
- [ ] low liquidity;
- [ ] bull/bear conditions where appropriate.

### 46.1 Regime detection as a model

- [x] Treat regime detection as a hypothesis/model subject to error. (`REGIME_DETECTION_WARNING`)
- [x] Never present a detected regime as a ground-truth label.
- [x] Document the detection method and its parameters. (`RegimeLabels.method`)
- [ ] Report regime classifications with confidence or uncertainty where practical.

### 46.2 Regime-conditional analysis

- [x] Compute performance metrics per regime where appropriate. (`compute_regime_performance`)
- [ ] Compare strategy behavior across regimes.
- [x] Detect whether a strategy depends on one specific regime.
- [x] Warn when a strategy's historical performance is concentrated in a single regime. (`check_regime_concentration`)
- [ ] Evaluate benchmarks within each regime (see Chapter 42).

### 46.3 Regime changes

- [ ] Detect and visualize regime changes over time.
- [ ] Explain that regime changes can invalidate historical results.
- [ ] Support the comparison of out-of-sample behavior against the dominant regimes of the training period.

### 46.4 Beginner explanation

- [x] Explain what market regimes are in plain language.
- [x] Explain why a strategy that works in one regime may fail in another.
- [x] Explain why regime detection is uncertain.

# PART VIII — FEATURE ENGINEERING, MACHINE LEARNING, AFML, AND ENSEMBLES

---

## [~] 47. Feature engineering

Feature engineering is a research activity that supports machine learning and statistical studies. It is not part of the backtesting engine.

### 47.1 Feature catalog

- [x] Maintain a catalog of features with (`FEATURE_CATALOG`):
  - [x] name;
  - [x] formula/definition;
  - [x] source data;
  - [x] parameters;
  - [x] version;
  - [x] warm-up period;
  - [x] intended interpretation;
  - [x] known limitations.

### 47.2 Feature validation

- [x] Every feature must be computed without look-ahead bias. (all features validated)
- [x] Every feature must be computable at the exact time it is used.
- [x] Features must handle missing data explicitly.
- [x] Feature computation must be reproducible (same input → same output).

### 47.3 Feature leakage prevention

- [x] Never use future information in a feature.
- [ ] Normalize/scale features only on training data (Chapter 48.3)
- [ ] Detect and warn about features containing future observations.
- [ ] Detect and warn about redundant or nearly duplicate features.

### 47.4 Advanced feature families (research)

As optional research capabilities (see Chapter 49), the feature catalog may include:

- [ ] fractionally differentiated series: retain memory while achieving stationarity; the differentiation order `d` must be a recorded, documented parameter;
- [ ] structural-break features (for example CUSUM-style tests) with their parameters documented;
- [ ] information-content features (for example Shannon entropy of return signs or quantized returns) with the quantization scheme documented;
- [ ] every advanced feature must pass the same validation, leakage, and documentation rules as any other feature (47.2–47.3);
- [ ] explain in beginner terms why over-differentiated series lose predictive memory.

### 47.5 Feature documentation

- [x] Document the economic or statistical rationale of each feature. (`FeatureMetadata.interpretation`)
 - [x] Document when and why a feature may break. (`FeatureMetadata.limitations`)
- [ ] Provide a beginner-friendly explanation of feature importance results (see Chapter 48; methods and pitfalls in 49.7).

---

## [ ] 48. Machine learning

Machine learning is a research tool, not a magical predictive machine.

- [ ] ML must not be presented as a way to predict the market with certainty.
- [ ] ML is an optional research capability; it must not be required for the MVP.
- [ ] Favor simple models when they provide comparable evidence to complex ones (see Chapter 35).

### 48.1 Scope

- [ ] Feature engineering (Chapter 47).
- [ ] Labels/targets.
- [ ] Leakage prevention.
- [ ] Time-series validation.
- [ ] Walk-forward validation (Chapter 45).
- [ ] Model versioning.
- [ ] Reproducibility.
- [ ] Hyperparameter control.
- [ ] Overfitting detection.
- [ ] Feature importance.
- [ ] Model degradation tracking.
- [ ] Out-of-sample testing.

### 48.2 Labels and targets

- [ ] Labels must be defined explicitly and documented.
- [ ] Labels must not use future information.
- [ ] Label definitions must be versioned.

### 48.3 Validation discipline

- [ ] Use time-series-aware validation, never random shuffling.
- [ ] Use walk-forward validation where appropriate (Chapter 45).
- [ ] Never tune hyperparameters on the out-of-sample period.
- [ ] Record all hyperparameters, seeds, and data splits.

### 48.4 Overfitting control

- [ ] Compare training, validation, and out-of-sample performance.
- [ ] Warn when the gap between training and out-of-sample performance is large.
- [ ] Warn when performance depends on a specific random seed.
- [ ] Prefer simpler models when evidence is comparable.

### 48.5 Model management

- [ ] Every model must be versioned.
- [ ] Every model must record its training dataset version, features, labels, hyperparameters, and software versions.
- [ ] Models must be reproducible from recorded metadata.
- [ ] Track model degradation over time (see Chapter 64).

### 48.6 Interpretation

- [ ] Report feature importance where appropriate.
- [ ] Present importance with uncertainty and caveats.
- [ ] Do not treat feature importance as causal evidence.
- [ ] A model output is a research signal candidate, never an order by itself (see Chapter 33.6).

### 48.7 Advanced ML research capabilities

Advanced, leakage-aware ML techniques are specified in their own chapter (Chapter 49): triple-barrier labeling, sample weighting, meta-labeling, purged cross-validation, and feature-importance methods. Those capabilities are optional research extensions, not MVP requirements, and must follow the same validation discipline as this chapter.

---

## [~] 49. Advanced financial machine learning (AFML)

This chapter consolidates the advanced research techniques from *Advances in Financial Machine Learning* (Marcos López de Prado, Wiley, 2018) that the platform may implement. Reference implementations and exercise solutions are available under `external/adv-financial-ml-marcos-exercises`.

These techniques are **research-tier capabilities**: none of them is required for the MVP, none of them may generate orders by itself, and every one of them must obey the evidence rules of Chapter 43 and the leakage rules of Chapters 38 and 48.

- [x] Every technique in this chapter must be verified against the exercise repository (and, where necessary, additional research) before implementation; never implement from memory of the book alone.
- [x] Every technique must record its parameters, versions, seeds, and dataset identity like any other research artifact (Chapters 52–53).
- [ ] The UI must label these features as advanced research tools with their assumptions and limitations visible.

### 49.1 Event-based bars and monetary sampling

Canonical specification for the bar types introduced in 29.1:

- [ ] volume bars: sample after a fixed traded volume;
- [ ] dollar bars: sample after a fixed traded value;
- [ ] imbalance bars: sample after a directional-imbalance threshold, only where trade-level data is available;
- [ ] document why event-based bars often stabilize variance compared with fixed-time candles;
- [ ] bar thresholds and parameters must be recorded and versioned;
- [ ] study the exercises' reference implementation of bars before implementing.

### 49.2 Triple-barrier labeling

Labels must describe the trading decision, not just the next price change.

- [x] define two horizontal barriers: take-profit and stop-loss. (`TripleBarrierConfig`)
- [x] define a vertical (time) barrier: the maximum holding period. (`TripleBarrierConfig`)
- [x] the label is which barrier is touched first. (`TripleBarrierLabel.barrier_hit`)
- [x] barrier distances and the time barrier are explicit, documented parameters. (`TripleBarrierConfig`)
- [ ] barrier evaluation must respect intrabar ambiguity rules (see 37.5) and must state whether the high/low path or close-only paths are used;
- [x] labels are computed without look-ahead. (all features validated)
- [ ] explain in beginner terms what the three barriers mean.

### 49.3 Sample weighting and uniqueness

Consecutive overlapping positions make observations non-independent and must not be treated as equal:

- [x] compute average uniqueness of each labeled observation based on overlap. (`compute_label_uniqueness`)
- [ ] weight observations by uniqueness and by return magnitude where appropriate.
- [x] record the weighting scheme as part of the model/experiment metadata.
- [ ] warn when many labels share the same time intervals because effective sample size is then much smaller than the nominal count.

### 49.4 Purged K-Fold cross-validation and embargo (canonical)

This subsection owns the canonical requirements; 38.8 and 45.3 reference it.

- [x] implement purging. (`create_purged_splits`)
- [x] implement embargo. (`PurgedKFoldConfig.embargo_pct`)
- [x] embargo length is an explicit parameter, recorded with the experiment.
- [ ] provide combinatorial split generation for CPCV (used by 45.3);
- [ ] warn when applied to labels that do not overlap but features are highly serially dependent;
- [ ] never present a purged-CV score as a substitute for a true untouched out-of-sample test.

### 49.5 Probabilistic and deflated Sharpe ratios

Support rigorous evaluation of Sharpe-ratio-type metrics as research capabilities:

- [x] probabilistic Sharpe ratio (PSR). (`probabilistic_sharpe_ratio`)
- [ ] deflated Sharpe ratio (DSR)
- [ ] the number of trials must be recorded wherever DSR is computed — an experiment that cannot count its trials cannot claim a deflated estimate;
- [ ] both estimates must be labeled as model-based with their assumptions (non-normality, independence) visible;
- [ ] feed both into the evidence levels of Chapter 43.1 and into strategy qualification (Chapter 66).

### 49.6 Probability of backtest overfitting (PBO)

Canonical specification for 44.8:

- [ ] implement combinatorially symmetric cross-validation (CSCV) to estimate PBO for a set of candidate configurations;
- [ ] report PBO next to any optimization or selection result that used multiple trials (see Chapter 39);
- [ ] a high PBO must be displayed as a prominent warning and must lower the evidence level of the result;
- [ ] document the rank-logit/combinatorial method actually implemented;
- [ ] never present PBO as an exact prediction — it is an estimate under stated assumptions.

### 49.7 Feature-importance methods

Complement Chapter 48.6 with techniques that respect temporal dependence:

- [ ] mean-decrease accuracy via purged/embargoed cross-validation (not plain K-Fold);
- [ ] mean-decrease impurity for tree ensembles, reported with the same caveats;
- [ ] document that clustered features (highly correlated groups) distort single-feature importance and report clustered importance where practical;
- [ ] never interpret importance as causal evidence;
- [ ] explain in beginner terms what feature importance can and cannot say.

### 49.8 Meta-labeling

Meta-labeling is a research capability that filters an existing primary signal instead of generating one:

- [ ] the primary strategy produces the directional signal exactly as specified in Chapter 33.6;
- [ ] a secondary model predicts whether the primary signal is likely to succeed, using features that contain no future information;
- [ ] labels for the secondary model must come from triple-barrier outcomes (49.2), not from arbitrary future returns;
- [ ] evaluate the primary strategy alone, the filtered version alone, and the filter's marginal contribution;
- [ ] meta-labeling must never bypass the signal → order separation of 33.6, and its output is still only a research signal candidate;
- [ ] bet sizing derived from model probabilities is a research study that must satisfy the risk limits of Chapter 58 before it can ever inform anything operational.

### 49.9 Research code references

- [ ] Map each implemented technique to its exercise-repository reference and record the mapping in `docs/en/developers/reference-projects.md`;
- [ ] review any adapted code for correctness against the book's definitions before merging;
- [ ] the printed book is the conceptual authority for disputes between implementations; it must be cited in documentation but never redistributed.

### 49.10 Implementation guardrails

- [ ] These capabilities must not be required by any other MVP chapter; chapters that reference them must mark the dependency as research-tier.
- [ ] A failure or unavailability of these features must never block backtesting, optimization, paper trading, or risk management.
- [ ] All advanced features must be clearly separated in the UI from beginner workflows.

---

## [~] 50. Ensembles

- [x] Support combining multiple strategies or models into ensembles. (`combine_signals_majORITY`, `combine_signals_average`, `combine_signals_weighted`)

### 50.1 Ensemble design

- [x] Document the combination method. (`CombinationMethod`)
- [ ] Document the diversity rationale of the members.
- [x] Record each member's version and parameters. (`StrategySignal`)
- [ ] Evaluate each member independently before evaluating the ensemble.
- [x] Compare the ensemble against its best member and against benchmarks.
- [ ] Warn when the ensemble adds complexity without improving evidence (see Chapter 35).

### 50.2 Ensemble validation

- [ ] Validate the ensemble with the same discipline as individual strategies (out-of-sample, walk-forward, robustness).
- [ ] Check that the ensemble does not concentrate risk in one regime (see Chapter 46).
- [ ] Never present ensemble performance as proof of future profitability.

---

# PART IX — PORTFOLIO

---

## [~] 51. Portfolio construction and correlations

### 51.1 Multi-asset support

- [ ] Support evaluating strategies across multiple assets.
- [ ] Support portfolio-level backtesting where appropriate.
- [ ] Track portfolio value, positions, and balances across assets.

### 51.2 Correlations

- [x] Calculate correlation between strategy returns. (`compute_correlation`)
- [x] Calculate correlation between assets.
- [x] Warn when correlations are unstable over time. (`warn_instability`)
- [ ] Explain that correlations can change in different market regimes.
- [ ] Do not present correlation as causation.

### 51.3 Portfolio metrics

- [x] Portfolio return. (`PortfolioMetrics`)
- [x] Portfolio drawdown.
- [x] Portfolio volatility. (`compute_portfolio_metrics`)
- [ ] Risk contributions per asset or strategy where appropriate.
- [ ] Diversification effect where appropriate.
- [ ] Combined exposure.

### 51.4 Position sizing at portfolio level

- [ ] Portfolio-level position sizing must pass through the risk manager (see Chapter 58).
- [ ] The portfolio must never bypass risk limits per asset or per strategy.
- [ ] Record all portfolio construction assumptions.

---

# PART X — RESEARCH INFRASTRUCTURE

---

## [~] 52. Research experiment manager

The system must maintain a clear entity for experiments.

Each experiment must record:

- [x] experiment ID. (`ExperimentRecord.experiment_id`)
- [x] hypothesis. (`ExperimentRecord.hypothesis`)
- [x] strategy version. (`ExperimentRecord.strategy_version`)
- [x] dataset version. (`ExperimentRecord.dataset_version`)
- [x] parameters;
- [x] metrics. (computed from backtest)
- [x] execution assumptions. (`ExperimentRecord.execution_assumptions`)
- [x] software version. (`ExperimentRecord.software_version`)
- [x] random seed. (`ExperimentRecord.random_seed`)
- [x] timestamp. (`ExperimentRecord.timestamp`)
- [x] results. (from backtest metrics)
- [x] notes. (`ExperimentRecord.notes`)
- [x] conclusion. (`ExperimentRecord.conclusion`)

### 52.1 Experiment lifecycle

- [x] Draft. (`ExperimentStatus.DRAFT`)
- [x] Running. (`ExperimentStatus.RUNNING`)
- [x] Completed. (`ExperimentStatus.COMPLETED`)
- [ ] Failed.
- [ ] Cancelled.
- [ ] Archived.

### 52.2 Reproducibility

- [ ] An experiment must be reproducible from its recorded metadata (see Chapter 53).
- [ ] Re-running an experiment with identical inputs must produce identical results.
- [ ] The experiment manager must link to the strategy registry (see Chapter 36).
- [ ] The experiment manager must link to the dataset versions used.
- [ ] Experiments must be searchable and filterable.

### 52.3 Research automation

- [ ] Support batch/bulk experiment runs where appropriate.
- [ ] Support queued research jobs with progress and cancellation.
- [ ] Support comparing experiments side by side.
- [ ] Support exporting experiment histories.
- [ ] Support tagging experiments (e.g., by hypothesis, strategy, regime).
- [ ] Automated experiments must never trigger orders; they are research-only.

---

## [~] 53. Reproducibility

Reproducibility is a core research requirement, not an optional feature.

### 53.1 Backtest reproducibility

Every backtest must store:

- [ ] application version;
- [x] strategy version. (`ExperimentRecord.strategy_version`)
- [x] parameters;
- [ ] dataset checksum;
- [ ] commission configuration;
- [ ] slippage model;
- [ ] execution model;
- [x] random seed. (`ExperimentRecord.random_seed`)
- [ ] time range;
- [ ] schema version;
- [x] environment information. (`ExperimentRecord.environment`, captured automatically by `ExperimentManager.create()` since 2026-09-27.)

- [ ] Repeating a backtest with identical data and configuration must produce identical results.

### 53.2 Research reproducibility

- [x] Every experiment must record the environment (Python version, dependency versions, platform). (`capture_environment()` → `environment_summary()` on every record; secret-looking environment variables are redacted.)
- [ ] Every result must reference its experiment ID (see Chapter 52).
- [ ] Every dataset must have a checksum (see Chapter 29).
- [ ] Every machine-learning model must record training data, features, labels, hyperparameters, and seed (see Chapter 48).

### 53.3 Reproducibility verification

- [ ] Provide a command or workflow to re-run a recorded experiment.
- [ ] Provide a way to compare a re-run result with the original result.
- [ ] Document known sources of non-determinism and how they are controlled.

---

## [ ] 54. Research notebooks

- [ ] Provide research notebooks for exploratory analysis where practical.

### 54.1 Notebook requirements

- [ ] Notebooks must run against the application's stored datasets and domain models.
- [ ] Notebooks must not bypass the risk manager or execution engine.
- [ ] Notebooks are research tools; they must not submit orders.
- [ ] Notebooks must record their runtime environment for reproducibility (see Chapter 52).
- [ ] Notebooks must be able to reference experiments from the experiment manager (see Chapter 52).

### 54.2 Notebook safety

- [ ] Do not expose credentials to notebooks.
- [ ] Do not allow notebooks to modify risk settings.
- [ ] Clearly label notebook results as research artifacts, not trading signals.

---

## [ ] 55. AI research assistant

The AI assistant must be presented as:

> **An assistant for research and analysis, not an AI that knows which trade to make.**

It may help with:

- [ ] explaining results;
- [ ] generating hypotheses;
- [ ] comparing experiments;
- [ ] detecting inconsistencies;
- [ ] analyzing documentation;
- [ ] suggesting experiments;
- [ ] generating reports.

### 55.1 Hard restrictions

The AI research assistant must:

- [ ] not execute real operations automatically by default;
- [ ] not modify strategies silently;
- [ ] not bypass the `RiskManager`;
- [ ] not have direct access to credentials;
- [ ] not present predictions as certainties;
- [ ] not present a backtest as proof of future profitability;
- [ ] require explicit user confirmation for any action beyond analysis;
- [ ] record its suggestions in the audit log (see Chapter 10);
- [ ] clearly label generated content as assistant-generated where appropriate.

### 55.2 Educational role

- [ ] The assistant must explain concepts in plain language.
- [ ] The assistant must point out when evidence is insufficient.
- [ ] The assistant must not invent statistics or metric values.
- [ ] Any metric it reports must come from recorded experiments.

---

# PART XI — EXECUTION AND PAPER TRADING

---

## [x] 56. Execution realism

Execution realism models how orders behave in real markets. It must remain separate from strategy logic and from the risk manager.

### 56.1 Execution components

- [x] Fills.
- [x] Latency.
- [x] Slippage.
- [x] Liquidity.
- [x] Partial fills.
- [x] Rejections.
- [x] Order cancellations.
- [x] Exchange rules (see Chapter 30).
- [x] Fee models.
- [x] Order-book depth where data is available.

### 56.2 Execution models

- [x] At least two documented execution models must be available to backtests, paper trading, and simulations (see Chapter 37.4).
- [x] The selected execution model must be recorded in every run.
- [x] Execution models must be configurable and comparable.

### 56.3 Latency and slippage

- [x] Simulated execution latency.
- [x] Conservative slippage assumptions.
- [x] Slippage variation across scenarios (see Chapter 44).
- [x] Document that real latency and slippage depend on market conditions.

### 56.4 Liquidity

- [x] Model available liquidity where data is available.
- [x] Never assume unlimited liquidity.
- [x] Warn when simulated order size exceeds plausible liquidity.

### 56.5 Execution realism report

- [x] Reports must state which execution model was used.
- [x] Reports must quantify the impact of execution assumptions on results where practical.
- [x] Execution realism feeds backtest (Chapter 37), paper trading (Chapter 57), and robustness (Chapter 44) results. *(Paper trading wired 2026-09-27: `paper_session.py` calls `simulate_market_order`. Backtest and robustness wired 2026-10-28: `BacktestConfig.execution_config` selects the model, the engine fills from the synthetic book, and `compare_execution_models` quantifies the difference inside every robustness report. See `docs/en/developers/cli.md` and `docs/en/developers/unwired-modules-audit.md`.)*

---

## [~] 57. Paper trading

Paper trading must use real-time or replayed market data while using simulated money.

The purpose is to test the complete trading workflow without risking real capital.

### 57.1 Account simulation

The paper account must model:

- [ ] Initial balance.
- [x] Balances by asset.
- [x] Positions.
- [x] Portfolio value.
- [x] Unrealized profit/loss.
- [x] Realized profit/loss.
- [ ] Fees.
- [ ] Slippage.
- [ ] Spread.
- [ ] Complete account history.

### 57.2 Order simulation

Support:

- [ ] Market orders.
- [ ] Limit orders.
- [ ] Stop orders where applicable.
- [ ] Stop-loss.
- [ ] Take-profit.
- [ ] Trailing stops where applicable.
- [ ] Partially filled orders.
- [ ] Rejected orders.
- [ ] Cancellations.
- [ ] Simulated latency.
- [ ] Liquidity constraints where data is available.

### 57.3 Execution consistency

Paper trading should use the same major components used by backtesting and future live trading:

```text
Market Data
    ↓
Strategy
    ↓
Signal
    ↓
Risk Manager
    ↓
Order Request
    ↓
Execution Simulator
    ↓
Paper Account
```

- [ ] Do not create a separate simplified trading logic that behaves fundamentally differently from the backtesting engine.
- [ ] Reuse common domain and execution components where practical (see Chapter 56).

### 57.4 Modes

Include:

- [ ] Real-time paper trading.
- [ ] Historical replay.
- [ ] Configurable playback speed.
- [ ] Pause.
- [ ] Resume.
- [ ] Step-by-step advancement.
- [ ] Account reset.
- [ ] Snapshot creation.
- [ ] Session recording.

### 57.5 Comparison

The application should allow comparison between:

- [ ] Backtest.
- [ ] Paper trading.
- [ ] Buy-and-hold.
- [ ] Expected execution assumptions.
- [ ] Actual simulated execution.

### 57.6 Monitoring

Display:

- [ ] Current portfolio value.
- [ ] Open positions.
- [ ] Pending orders.
- [ ] Executed orders.
- [ ] Fees.
- [ ] Slippage.
- [ ] Drawdown.
- [ ] Exposure.
- [ ] Risk-manager decisions.
- [ ] Connection state.
- [ ] Data freshness.

### 57.7 Evidence limitations

- [ ] Do not present paper trading as proof of future profitability.
- [ ] Explain that paper trading cannot perfectly reproduce real liquidity.
- [ ] Explain that simulated fills may differ from real fills.
- [ ] Explain that real markets can change between simulation and deployment.

### 57.8 Beginner tutorial

Explain:

- [ ] What paper trading is.
- [ ] Why it is useful.
- [ ] What it can test.
- [ ] What it cannot reproduce perfectly.
- [ ] Why it should precede real-money trading.
- [ ] How to reset the simulated account.
- [ ] How to interpret gains and losses.
- [ ] Why a paper profit is not guaranteed to become a real profit.

---

# PART XII — RISK AND CAPITAL PROTECTION

---

## [~] 58. Risk manager

Create a central `RiskManager` service.

The `RiskManager` must operate independently from individual strategies and must be able to reject or modify proposed orders before execution.

### 58.1 Position and exposure limits

Configurable rules:

* [ ] Maximum risk per trade.
* [ ] Maximum position size.
* [ ] Maximum percentage of portfolio in one asset.
* [ ] Maximum total exposure.
* [ ] Maximum long exposure where applicable.
* [ ] Maximum short exposure where applicable.
* [ ] Maximum leverage where applicable.

### 58.2 Loss limits

Support:

* [ ] Maximum daily loss.
* [ ] Maximum weekly loss.
* [ ] Maximum drawdown.
* [ ] Maximum consecutive losses.
* [ ] Cooldown after losses.

### 58.3 Operational limits

Support:

* [ ] Maximum trades per day.
* [ ] Maximum open orders.
* [ ] Maximum order frequency.
* [ ] Maximum position changes.
* [ ] Duplicate-order protection.

### 58.4 Market-condition protections

Block or restrict trading on:

* [ ] Stale market data.
* [ ] Data-feed failure.
* [ ] Exchange disconnection.
* [ ] Excessive volatility.
* [ ] Excessive spread.
* [ ] Insufficient liquidity.
* [ ] Time-synchronization errors.
* [ ] Inconsistent balances.
* [ ] Invalid market metadata.

### 58.5 System-state protections

The `RiskManager` must be able to reject orders when:

* [ ] The emergency kill switch is active (see Chapter 58).
* [ ] The selected trading environment is invalid.
* [ ] Required credentials are unavailable.
* [ ] Account state cannot be verified.
* [ ] Market data is considered unsafe.
* [ ] The execution engine reports an unsafe state.

### 58.6 Profiles

Include:

* [ ] Conservative.
* [ ] Moderate.
* [ ] Custom.

* [ ] Do not include an “Aggressive” profile in the first version.

### 58.7 Decision result

The `RiskManager` must return a structured result containing:

* [ ] Approved.
* [ ] Rejected.
* [ ] Modified.
* [ ] Reason.
* [ ] Triggered rule.
* [ ] Permitted size.
* [ ] Timestamp.
* [ ] Audit identifier.
* [ ] Beginner-friendly explanation.

### 58.8 Strategy isolation

* [ ] A strategy must never bypass the `RiskManager`.
* [ ] A strategy must never disable a risk rule.
* [ ] A strategy must never modify global risk limits.
* [ ] Imported strategies must inherit the active risk configuration.
* [ ] Real trading must always pass through the same central risk layer.

### 58.9 Risk calculations

Where applicable, the risk manager should consider:

* [ ] Account equity.
* [ ] Available balance.
* [ ] Current exposure.
* [ ] Existing positions.
* [ ] Pending orders.
* [ ] Stop-loss distance.
* [ ] Estimated execution price.
* [ ] Fees.
* [ ] Slippage.
* [ ] Market liquidity.

### 58.10 Auditability

Every risk decision must be recorded with:

* [ ] Timestamp.
* [ ] Strategy.
* [ ] Signal.
* [ ] Proposed order.
* [ ] Account state used.
* [ ] Risk rules evaluated.
* [ ] Final decision.
* [ ] Reason.
* [ ] Risk-manager version.

### 58.11 Education

Every risk rule must include beginner documentation explaining:

* [ ] What the rule does.
* [ ] Why it exists.
* [ ] What problem it attempts to prevent.
* [ ] What happens when it is triggered.
* [ ] Its limitations.

---

## [~] 59. Emergency kill switch

Implement a visible, accessible, and clearly identifiable emergency kill switch.

The kill switch must be designed as a **capital-protection mechanism**, not merely as a user-interface feature.

### 59.1 When activated

* [ ] No new orders may be created.
* [ ] Automatic strategies must stop generating executable orders.
* [ ] Pending internal trading tasks must be cancelled where safely possible.
* [ ] New order requests must be rejected by the central risk/execution layer.
* [ ] The application must clearly display the emergency state.
* [ ] The event must be logged.
* [ ] An audit identifier must be created.
* [ ] The activation timestamp must be recorded.

### 59.2 Exchange orders

The kill switch must distinguish between:

```text
Local application state
        and
Orders already accepted by the exchange
```

Therefore:

* [ ] Open exchange orders must not be cancelled automatically by default.
* [ ] Automatic cancellation may be implemented as an explicit configurable policy.
* [ ] Any automatic cancellation policy must require additional confirmation during configuration.
* [ ] The application must clearly inform the user whether exchange orders remain active.

### 59.3 Activation sources

Support:

* [ ] GUI button.
* [ ] Configurable keyboard shortcut.
* [ ] Programmatic activation by the risk system.
* [ ] Automatic activation when configured critical safety conditions are triggered.

### 59.4 Recovery

To deactivate the kill switch:

* [ ] Require explicit user action.
* [ ] Display the reason for activation.
* [ ] Display current account and market state.
* [ ] Revalidate connectivity.
* [ ] Revalidate balances.
* [ ] Revalidate market-data freshness.
* [ ] Revalidate risk limits.
* [ ] Require confirmation before resuming automated trading.

### 59.5 Logging

Record:

* [ ] Activation timestamp.
* [ ] Deactivation timestamp.
* [ ] Activation source.
* [ ] Reason.
* [ ] Active strategy.
* [ ] Account/environment.
* [ ] Open positions.
* [ ] Pending orders known by the application.
* [ ] Result of any cancellation attempt.

### 59.6 Beginner explanation

Explain:

* [ ] What the kill switch does.
* [ ] When it should be used.
* [ ] What it does not do.
* [ ] Why exchange orders may remain active.
* [ ] Why the user must verify the account after an emergency.
* [ ] Why stopping new orders is not necessarily the same as closing positions.

---

## [~] 60. Risk of ruin and capital depletion

The system must differentiate:

- [x] maximum historical drawdown; (`RiskOfRuinReport.historical_max_drawdown`, `metrics.risk.max_drawdown`.)
- [x] expected drawdown; (`RiskOfRuinReport.expected_max_drawdown`, the Monte Carlo p95.)
- [x] probability of ruin; (`RiskOfRuinReport.probability_of_ruin`; `research.py` feeds `monte_carlo.risk_of_ruin` into qualification.)
- [x] capital depletion; (Modelled as the `ruin_threshold_fraction` at which trading stops.)
- [x] position sizing. (`robustness.position_size_from_trades()` → `ResearchRun.recommended_risk_per_trade`, Kelly scaled and capped.)

### 60.1 Definitions

- [x] **Maximum historical drawdown**: the largest peak-to-trough decline observed in the analyzed period.
- [x] **Expected drawdown**: an estimate of drawdown under stated assumptions.
- [x] **Probability of ruin**: an estimate of the probability that capital falls below a defined threshold.
- [x] **Capital depletion**: the point at which trading cannot continue because capital is exhausted or restricted.
- [x] **Position sizing**: the rule that determines how much capital a trade risks.

### 60.2 Estimation discipline

- [x] Never present a risk-of-ruin estimate as mathematical certainty if its assumptions are not valid. (Every report carries its `assumptions` and warnings.)
- [x] Document all assumptions (distribution, independence, costs, sample size). (`RiskOfRuinReport.assumptions`; the sizing warning names the sample size.)
- [ ] Prefer ranges or scenario distributions over single numbers. *(Monte Carlo already reports distributions for ruin and drawdown, but the position-size recommendation is still one point; a size-versus-ruin curve is pending.)*
- [x] Use Monte Carlo and bootstrap methods where appropriate (see Chapter 44).
- [x] Warn when estimates depend on unrealistically favorable assumptions. (Sizing warns on too few trades, no edge, and suspiciously large edges.)
- [x] Risk-of-ruin estimates are research/risk-analysis outputs; they must never be the only basis for an order. (The sizing warning says "a research ceiling, not advice", and orders still pass the risk manager.)

---

## [~] 61. Capital protection

The system must adopt the principle:

> **Capital preservation takes priority over strategy execution.**

A strategy must never be able to ignore:

- [ ] risk limits;
- [ ] kill switch;
- [ ] exposure limits;
- [ ] account restrictions;
- [ ] safety gates.

### 61.1 Enforcement

- [ ] The risk manager enforces capital-protection rules for every environment (see Chapter 58).
- [ ] The kill switch remains available in every environment (see Chapter 58).
- [x] Safety gates verify capital-protection conditions before real orders. (`SafetyGates`)
- [x] Safety gates are non-bypassable. (`SAFETY_GATES_WARNING`)
- [ ] Capital-protection rule changes require explicit user action and are audited.

### 61.2 Education

- [ ] Explain why capital preservation comes first.
- [ ] Explain that drawdowns are harder to recover from as they grow.
- [ ] Explain the relationship between position sizing, drawdown, and risk of ruin (see Chapter 60).

### 61.3 Protection of essential funds

- [ ] Before enabling real trading, the user must confirm that they are not using essential funds (money needed for living expenses, rent, food, or emergencies).
- [ ] The application must warn when a user's stated risk capacity suggests financial hardship.
- [ ] The application must recommend paper trading only for users who cannot afford losses.
- [ ] The application must never offer credit, leverage, or margin as a "solution" (see Chapter 5).
- [ ] The application must provide clear guidance on how to stop trading and walk away.

# PART XIII — MONITORING AND STRATEGY LIFECYCLE

---

## [~] 62. Live monitoring

Live monitoring covers paper trading, testnet, and real trading sessions.

### 62.1 Monitored state

Display:

- [x] current portfolio value;
- [x] open positions;
- [x] pending orders;
- [x] executed orders;
- [x] fees;
- [x] slippage.
- [x] drawdown;
- [x] exposure;
- [x] risk-manager decisions;
- [x] connection state;
- [x] data freshness;
- [x] environment indicator (always visible);
- [x] kill-switch status;
- [x] recent alerts.

### 62.2 Monitoring rules

- [x] The environment (backtest, paper, testnet, real) must be visible at all times.
- [x] Alerts must be understandable to a beginner.
- [x] Alerts must not depend only on color.
- [x] Monitoring must never bypass the risk manager.

### 62.3 Historical comparisons

- [ ] Compare live behavior against backtest expectations where appropriate (see Chapter 63).
- [ ] Compare live behavior against paper-trading behavior.

---

## [~] 63. Live vs backtest drift

The system must explain and quantify differences between:

- [x] backtest expectations. (tracked in backtest results)
- [x] paper-trading behavior. (tracked via paper trading)
- [ ] live behavior.

### 63.1 Drift dimensions

Analyze:

- [x] return drift. (computed from backtest vs paper by `drift_report_from_results`; the comparison requires equal position sizing and emits a `SIZING MISMATCH` warning instead of passing a sizing artefact off as drift)
- [x] drawdown drift. (computed from backtest vs paper)
- [x] slippage drift. (computed from model vs actual)
- [x] fill-rate drift. (computed from expected vs actual)
- [x] latency drift; (computed by `latency_drift` between expected and actual fill latency)
- [x] volatility drift; (computed by `volatility_drift` from the two equity curves; also a `volatility` key in `calculate_drift_metrics`)
- [ ] market-regime changes (see Chapter 46).

### 63.2 Drift reporting

- [x] Compare realized metrics against expected ranges from the backtest. (`expected_ranges()`: a trade bootstrap for the return band, anchored on the realised return; the drawdown band is anchored on the observed drawdown because a trade-level bootstrap cannot see intra-trade drawdown. Every band carries its `basis`.)
- [x] Show drift over time, not only as a single value. (`drift_over_time()` splits both equity curves into equal slices and reports the drift of each.)
- [x] Explain likely causes for each drift dimension. (`LIKELY_CAUSES` names a mechanism per metric; shown only for degraded and outside-expected verdicts.)
- [x] Distinguish expected variability from meaningful degradation. (Four verdicts: `within_expected`, `expected_tail`, `outside_expected`, `degraded`; a miss beyond half the band width is degradation, inside it is a tail. A run with fewer than two backtest trades is `suspicious`/unvalidated, never healthy.)
- [x] The system must be able to mark a strategy as degraded or suspicious (see Chapter 64). (`assess_drift()` returns `StrategyHealth` — healthy / suspicious / degraded — with the reasons and the evidence, rendered by the Paper Trading screen. It never touches the risk manager.)

### 63.3 Education

- [x] Explain why backtest, paper, and live results will never match exactly. (covered by `drift_education()`)
- [x] Explain which differences are normal and which are warning signs. (covered by `drift_education()`)

---

## [x] 64. Strategy failure detection

The system must detect when a strategy stops behaving as it did historically.

### 64.1 Detection signals

Consider:

- [x] performance degradation;
- [x] drawdown increase;
- [x] trade-distribution changes;
- [x] volatility changes;
- [x] execution degradation;
- [x] regime changes;
- [x] data-quality problems.

### 64.2 Recommendations

The system must be able to recommend:

```text
Continue
Monitor
Reduce exposure
Pause
Retire
```

- [x] Every recommendation must show the reason.
- [x] Never hide the reason behind a recommendation.
- [x] Recommendations must be based on recorded evidence, not guesses.
- [x] Recommendations must never bypass the risk manager.
- [x] A “Retire” recommendation must update the strategy registry status (see Chapter 36).
- [x] Recommendations must include the data and thresholds used.

### 64.3 Education

- [x] Explain why strategies degrade over time.
- [x] Explain that past performance does not guarantee continued performance.
- [x] Explain the difference between normal variability and genuine failure.

---

## [~] 65. Strategy promotion pipeline

A strategy must progress through explicit stages. It must never jump directly from `Backtest → Real Trading`.

The progression is:

```text
Idea
 ↓
Prototype
 ↓
Backtest
 ↓
Validation
 ↓
Out-of-Sample
 ↓
Robustness
 ↓
Walk-Forward
 ↓
Paper Trading
 ↓
Qualification
 ↓
Safety Gates
 ↓
Small Live Deployment
 ↓
Monitoring
```

### 65.1 Stage requirements

- [x] Each stage requires the completion of the previous stage.
- [x] Each stage transition must be recorded with timestamp and evidence reference.
- [ ] The strategy registry must reflect the current stage (see Chapter 36).
- [ ] A strategy may return to an earlier stage when new evidence contradicts its current status.
- [ ] Skipping stages must be impossible by default.
- [ ] Any exception must require explicit, audited user confirmation.

### 65.2 Promotion evidence

- [ ] Promotion to `Paper Trading` requires backtest, validation, out-of-sample, robustness, and walk-forward evidence.
- [ ] Promotion to `Qualification` requires paper-trading evidence.
- [ ] Promotion to `Small Live Deployment` requires a positive qualification report (see Chapter 66).
- [ ] Live deployment must start with limited exposure and be monitored (see Chapter 62).

---

## [x] 66. Strategy qualification

Qualification is a formal evaluation stage. A strategy must not be considered “qualified” merely because `Profit > 0`.

### 66.1 Evaluation criteria

The qualification process must consider, where applicable:

- [x] out-of-sample performance;
- [x] drawdown;
- [x] risk-adjusted metrics;
- [x] benchmark comparison (see Chapter 42);
- [x] sample size;
- [x] parameter stability (see Chapter 39);
- [x] robustness (see Chapter 44);
- [x] walk-forward (see Chapter 45);
- [x] paper trading (see Chapter 57);
- [x] execution realism (see Chapter 56);
- [x] data quality (see Chapter 29);
- [x] complexity (see Chapter 35);
- [x] statistical evidence (see Chapter 43);
- [x] operational stability (see Chapter 62).

### 66.2 Qualification outcomes

Qualification must produce one of:

```text
Qualified
Conditionally Qualified
Not Qualified
```

- [x] “Conditionally Qualified” must list the conditions and their deadlines or thresholds.
- [x] “Not Qualified” must explain which criteria failed and why.
- [x] Qualification reports must be stored and referenced from the strategy registry (see Chapter 36).
- [x] Qualification is not a guarantee of future profitability.

### 66.3 Qualification review

- [x] A qualified strategy must be re-qualified after material changes (parameters, data, execution model, market conditions).
- [x] Re-qualification intervals must be documented.

---

# PART XIV — SAFETY GATES AND REAL TRADING

---

## [x] 67. Safety gates

Safety gates are the executable protection layer between the application and a real exchange.

> **Capital preservation takes priority over strategy execution** (see Chapter 61).

Before an order reaches a real exchange:

```text
Strategy
   ↓
Signal
   ↓
Portfolio State
   ↓
Risk Manager
   ↓
Safety Gates
   ↓
Execution Engine
   ↓
Exchange
```

The safety layer must verify:

- [x] Correct environment.
- [x] Correct exchange.
- [x] Correct account.
- [x] Current balances.
- [x] Current market data.
- [x] Valid order parameters.
- [x] Valid market constraints.
- [x] Risk limits.
- [x] Position limits.
- [x] Exposure limits.
- [x] Kill-switch state.
- [x] Connection state.

### 67.1 Safety-gate rules

- [x] A strategy can never disable a safety gate.
- [x] Safety gates must be verified on every order, not only on the first order.
- [x] Safety-gate failures must be audited with reason and timestamp.
- [x] Safety-gate configuration changes require explicit user confirmation.
- [x] The application must never silently disable a safety gate.

### 67.2 Environment separation

- [x] Environments are: `Backtest`, `Historical Replay`, `Paper Trading`, `Exchange Testnet`, `Real Trading`.
- [x] The environment must be visible at all times.
- [x] Switching from testnet/paper to real trading must require explicit confirmation.
- [x] Importing a configuration must never silently switch environments.

---

## [x] 68. Real trading

Real trading support must remain behind multiple independent safety protections.

The MVP may keep real trading completely disabled through a feature flag.

Real trading must never become active simply because an API key or exchange configuration was imported.

### 68.1 Activation requirements

A future real-trading activation flow must require:

- [x] 1. Enabling an explicit advanced option.
- [x] 2. Displaying a prominent risk warning.
- [x] 3. Requiring written confirmation.
- [x] 4. Confirming that the API key has no withdrawal permission.
- [x] 5. Checking the selected environment.
- [x] 6. Displaying the selected exchange.
- [x] 7. Displaying the selected account/environment.
- [x] 8. Configuring strict risk limits.
- [x] 9. Testing connectivity.
- [x] 10. Verifying account balances.
- [x] 11. Verifying market-data freshness.
- [x] 12. Verifying system time synchronization.
- [x] 13. Confirming the emergency kill switch configuration.
- [x] 14. Requiring a confirmation phrase.
- [x] 15. Permanently displaying a clear `REAL TRADING` indicator while active.

### 68.2 API credentials

- [x] Never store withdrawal-enabled credentials by default.
- [x] Recommend API keys without withdrawal permissions.
- [x] Store credentials using the platform's secure credential mechanism where available.
- [x] Never display complete credentials in logs.
- [x] Never include credentials in strategy files.
- [x] Never include credentials in exported reports.
- [x] Never include credentials in screenshots or diagnostic bundles.

### 68.3 Strategy restrictions

- [x] Real trading strategies must use the same signal/risk/execution architecture.
- [x] Strategies must never modify risk limits.
- [x] Strategies must never bypass the `RiskManager`.
- [x] Strategies must never access credentials directly.
- [x] Strategies must never select a real account automatically.

### 68.4 Testing restrictions

- [x] Never use a real account in automated tests.
- [x] Never send real orders from unit tests.
- [x] Never enable real trading automatically.
- [x] Never use real credentials in test fixtures.
- [x] Never require real credentials for CI.
- [x] Test real-trading logic against mocks, simulators, or testnet environments.

### 68.5 Monitoring

While real trading is active, display:

- [x] `REAL TRADING` status.
- [x] Exchange.
- [x] Account/environment.
- [x] Current balance.
- [x] Available balance.
- [x] Open positions.
- [x] Open orders.
- [x] Exposure.
- [x] Current drawdown.
- [x] Risk limits.
- [x] Connection state.
- [x] Market-data freshness.
- [x] Recent executions.
- [x] Recent risk decisions.
- [x] Emergency kill-switch status.

### 68.6 Failure handling

If a critical safety condition occurs:

- [x] Stop creating new orders.
- [x] Notify the user clearly.
- [x] Log the event.
- [x] Activate the appropriate risk protection.
- [x] Preserve the audit trail.
- [x] Do not silently continue trading.

### 68.7 Beginner protection

The beginner documentation must strongly recommend:

1. [x] Learning the fundamentals.
2. [x] Testing strategies historically.
3. [x] Using out-of-sample evaluation.
4. [x] Testing strategy robustness.
5. [x] Paper trading.
6. [x] Using testnet where supported.
7. [x] Starting with very limited exposure if the user eventually chooses to trade real funds.

The application must clearly state:

> **Real trading involves the possibility of losing money. Historical performance, backtesting, paper trading, or statistical analysis cannot guarantee future profits.**

---

# PART XV — DEVELOPMENT PROCESS AND ETHICS

---

## [~] 69. Development phases

- [ ] Do not try to implement the entire application in one change.

### Phase 0: Research

Before programming:

- [ ] 1. inspect the system;
- [ ] 2. confirm software versions;
- [ ] 3. verify Debian packages;
- [ ] 4. review official documentation;
- [ ] 5. propose the architecture;
- [ ] 6. create a dependency matrix;
- [ ] 7. identify risks;
- [ ] 8. write Architecture Decision Records;
- [ ] 9. define the documentation architecture;
- [ ] 10. define the translation workflow;
- [ ] 11. define the beginner-learning roadmap.

- [ ] Deliver a research report first.

### Phase 1: Project foundation

Create:

- [x] `pyproject.toml`;
- [x] project structure;
- [x] minimal PyQt6 application;
- [x] logging;
- [x] configuration;
- [x] English default language;
- [x] Spanish translation framework;
- [x] tests;
- [x] SQLite;
- [x] initial English beginner documentation;
- [x] initial Learning Center shell.

### Phase 2: Data and charts

Implement:

- [x] MockExchange;
- [x] CSV import;
- [x] candles;
- [x] storage;
- [x] charts;
- [x] basic indicators.

### Phase 3: Backtesting

Implement:

- [x] deterministic engine;
- [x] initial strategies;
- [x] commissions;
- [x] slippage;
- [x] metrics. (computed from backtest)
- [ ] reports;
- [ ] beginner backtesting guide.

### Phase 4: Paper trading

Implement:

- [ ] simulated account;
- [ ] orders;
- [ ] fills;
- [ ] portfolio;
- [ ] replay;
- [ ] risk management;
- [ ] beginner paper-trading guide.

### Phase 5: Real-time public data

Implement:

- [ ] public Binance adapter;
- [ ] WebSocket;
- [ ] reconnection;
- [ ] rate limiting;
- [ ] stale-data detection;
- [ ] beginner guide to live market data.

### Phase 6: Testnet

Implement:

- [ ] secure credentials;
- [ ] Binance Spot Testnet;
- [ ] test orders;
- [ ] reconciliation;
- [ ] auditing;
- [ ] beginner API-key security guide.

### Phase 7: Maturity

Improve:

- [ ] accessibility;
- [ ] performance;
- [ ] complete English documentation;
- [ ] Spanish documentation;
- [ ] package testing;
- [ ] complete translations;
- [ ] Learning Center quizzes;
- [ ] screenshots;
- [ ] tutorials.

### Phase 8: Distribution packages (move to final phase)

This phase is intentionally deferred until the program is ready for release.
Building AppImages and Debian packages on GitHub consumes significant storage
and should only be done when the software is stable.

- [ ] AppImage packaging;
- [ ] initial Debian package;
- [ ] beginner chart tutorials.

### Phase 8+: Advanced research

Implement after the core phases are stable:

- [ ] statistical edge analysis (Chapter 43);
- [ ] robustness and Monte Carlo (Chapter 44);
- [ ] walk-forward analysis (Chapter 45);
- [ ] regime analysis (Chapter 46);
- [ ] feature engineering (Chapter 47);
- [ ] machine learning (Chapter 48);
- [ ] advanced financial machine learning (Chapter 49);
- [ ] ensembles (Chapter 50);
- [ ] portfolio construction (Chapter 51);
- [ ] research infrastructure (Chapters 52–55);
- [ ] monitoring and strategy lifecycle (Chapters 62–66);
- [ ] qualification and safety gates (Chapters 66–67).

- [ ] Do not proceed to a new phase if the previous phase does not compile or its tests fail.

---

## [~] 70. Working method

Before modifying files:

- [ ] 1. inspect the repository;
- [ ] 2. report what was found;
- [ ] 3. list the files that will be created or changed;
- [ ] 4. briefly explain the objective;
- [ ] 5. make small changes;
- [ ] 6. run tests;
- [ ] 7. show the results;
- [ ] 8. fix failures;
- [ ] 9. update documentation;
- [ ] 10. update translations where visible strings changed.

- [ ] Do not replace entire files unnecessarily.
- [ ] Do not hide errors.
- [x] Do not claim that a test passed unless it was actually executed.

When a required tool is unavailable:

- [ ] state that clearly;
- [ ] provide the command the developer must run;
- [ ] do not pretend the action succeeded.

When a dependency must be installed (chapter 4.0):

- [ ] STOP development at that task;
- [ ] notify the developer with the package name, source (Debian or PyPI), reason, and exact install command;
- [ ] wait for the developer to install it (via `apt`, or via a venv for PyPI-only packages);
- [ ] never install packages or create virtual environments on your own.

Every completed feature must include:

- [ ] code;
- [ ] tests;
- [x] English documentation. (`docs/en/developers/`)
- [ ] translation-ready strings;
- [ ] Spanish translation where feasible;
- [ ] beginner-oriented explanation when the feature affects end users.

---

## [~] 71. First concrete task and expected result

### 71.1 First concrete task

- [x] Begin only with Phase 0 and the minimum foundation of Phase 1.

Perform these tasks:

- [x] 1. inspect the development environment.
- [x] 2. verify dependencies available in Debian. (`debian-dependencies.md`)
- [x] 3. create `docs/en/developers/debian-dependencies.md`.
- [x] 4. create `docs/en/developers/architecture-proposal.md`;
- [x] 5. create `docs/en/developers/threat-model.md`;
- [x] 6. create ADR-0001 for the architecture;
- [x] 7. create ADR-0002 for charting;
- [x] 8. create ADR-0003 for Qt and asyncio concurrency;
- [x] 9. create ADR-0004 for credential storage;
- [x] 10. create ADR-0005 for the packaging backend;
- [x] 11. create ADR-0006 for internationalization;
- [x] 12. create ADR-0007 for beginner documentation;
- [x] 13. create the initial project structure;
- [x] 14. create a minimal PyQt6 window;
- [x] 15. make English the default language;
- [x] 16. create the Spanish translation infrastructure;
- [x] 17. configure Qt Linguist files;
- [x] 18. create XDG configuration handling;
- [x] 19. create logging with secret redaction;
- [x] 20. create a minimal SQLite database;
- [x] 21. create initial unit tests;
- [x] 22. create `pyproject.toml`;
- [ ] 23. create an initial Debian package;
- [x] 24. create the first English beginner guide;
- [x] 25. create the initial glossary;
- [x] 26. create the Learning Center placeholder;
- [x] 27. execute available tests.

The initial application must open a window containing:

- [x] the name “Crypto Trading Lab”;
- [x] a File menu;
- [x] a View menu;
- [x] a Tools menu;
- [x] a Help menu;
- [x] a language selector;
- [x] English selected by default;
- [x] Spanish available as the second language;
- [x] a visible “Mode: Paper Trading” indicator;
- [x] a visible “Real trading: Disabled” indicator;
- [x] a “Disconnected” status;
- [x] a welcome panel;
- [x] an educational warning;
- [x] a button to load a CSV file;
- [x] a button to open the Backtesting Lab, initially disabled;
- [x] a button to open the Learning Center;
- [x] a link to “Start Here: Cryptocurrency for Complete Beginners.”

- [x] The first English beginner guide must be `docs/en/beginners/00-start-here.md`

It must explain:

- [x] what Crypto Trading Lab is;
- [x] what it is not;
- [x] that profits are not guaranteed;
- [x] that paper trading is the default;
- [x] where a complete beginner should begin;
- [x] how to open the Learning Center;
- [x] why real money should not be used while learning.

- [x] The first glossary file must be `docs/en/beginners/glossary.md`

It must initially define at least:

- [x] cryptocurrency.
- [x] Bitcoin.
- [x] exchange.
- [x] trading pair.
- [x] candle.
- [x] volume.
- [x] order;
- [x] fee.
- [x] slippage.
- [x] volatility.
- [x] strategy.
- [x] backtesting.
- [x] paper trading.
- [x] risk;
- [ ] drawdown.

### 71.2 Expected result of the first iteration

At the end, provide:

- [ ] 1. architecture summary;
- [ ] 2. project file tree;
- [ ] 3. dependencies used;
- [ ] 4. dependencies rejected and the reasons;
- [ ] 5. commands executed;
- [ ] 6. test results;
- [ ] 7. problems found;
- [ ] 8. files created;
- [ ] 9. documentation created;
- [ ] 10. translation files created;
- [ ] 11. next steps;
- [ ] 12. exact Debian 12 execution instructions.

- [ ] Do not implement real-money operations yet.
- [ ] Do not include example keys that look real.
- [ ] Do not use real funds.
- [ ] Do not claim that Crypto Trading Lab can guarantee profits.
- [ ] Do not leave beginner documentation until the end of the project.
- [ ] Documentation, translation, education, tests, and code must evolve together.

---

## [~] 72. Research ethics and honest reporting

The project must maintain scientific and professional honesty at every stage.

### 72.1 Honest evidence

- [x] Never present a backtest as proof of future profitability. (Every report carries the chapter-72 disclaimers and `EVIDENCE_LEVEL`, and `audit_report_ethics()` refuses to emit a report that lacks them.)
- [ ] Never present Monte Carlo, bootstrap, or statistical results as predictions of the future.
- [x] Never hide assumptions behind results. (Every report has an explicit assumptions section; the ethics checker warns when none is documented.)
- [ ] Never cherry-pick time periods, parameters, or datasets to make a result look better.
- [x] Always label evidence level: observed result, statistical evidence, research hypothesis, validated evidence (see Chapter 43). (`EVIDENCE_LEVEL` in reports; `ui/research/validity.py` for research runs.)
- [ ] Report failed experiments as faithfully as successful ones.

### 72.2 Warnings and disclaimers

- [ ] All warnings must be understandable to a complete beginner.
- [x] The application must explain the risks of cryptocurrency trading. (The mandatory `risk` disclaimer is embedded in every generated report.)
- [x] The application must explain that users can lose part or all of their capital. (Same `risk` disclaimer.)
- [x] The application must explain that most retail traders lose money and that trading is not a reliable income source. (Same `risk` disclaimer.)
- [ ] The application must not present itself as a solution to financial hardship.
- [x] The application must not provide financial advice. (The `general` disclaimer is embedded in every generated report; the ethics checker flags its absence.)

### 72.3 Scientific discipline

- [ ] Favor simpler explanations when they fit the evidence (see Chapter 35).
- [ ] Document uncertainty instead of hiding it.
- [ ] The interface must never present statistical tools as “proof of profitability”.
- [ ] Research automation must never run real operations (see Chapter 52).
- [ ] The AI assistant must never be presented as an oracle (see Chapter 55).

### 72.4 Educational responsibility

- [ ] Explain why backtests can be misleading.
- [ ] Explain why profits are never guaranteed.
- [ ] Explain why paper trading differs from real trading.
- [ ] Keep education separate from financial advice.

---

# Final verification note

This roadmap is complete when the following architectural checks hold:

- [x] The conceptual flow `FOUNDATION → DATA → MARKET MODEL → STRATEGIES → SIGNALS → BACKTESTING → DATA SPLITTING → OPTIMIZATION → PERFORMANCE → STATISTICAL RESEARCH → ROBUSTNESS → WALK-FORWARD → REGIME ANALYSIS → FEATURE ENGINEERING → MACHINE LEARNING → ADVANCED FINANCIAL ML → ENSEMBLES → PORTFOLIO → EXECUTION → PAPER TRADING → RISK → MONITORING → STRATEGY QUALIFICATION → SAFETY GATES → REAL TRADING` is respected.
- [x] Research, execution, and risk responsibilities are separated (see Chapter 6.1).
- [x] No feature appears twice with different owners.
- [x] Every cross-reference points to a chapter that exists.
- [x] Every chapter answers a concrete question.
- [x] Terminology is consistent (see Chapter 2).
- [x] A profitable backtest is never presented as evidence of future advantage.

---

# PART XVI — RESEARCH WORKFLOW (2026-09-19 improvements)

This part specifies the work requested by
`8vo/08-mejoras-para-crypto-trading-lab.md`: turning the existing
scientific engine into a workflow a single person can actually walk
through. It adds requirements only; the chapters above keep their
canonical ownership. Items are marked `[x]` only when they are
implemented **and tested**.

---

## [~] 73. Historical data acquisition and dataset identity

The user must be able to research a market without hunting for a CSV
file first (analysis §3, §8).

- [x] Download historical candles from Binance Spot public REST using
  only the Python standard library — no new dependency.
- [x] Supported timeframes: 1m, 5m, 15m, 1h, 4h, 1d.
- [x] A request names exchange, symbol, interval, start and end; naive
  datetimes are rejected.
- [x] Pagination with a hard candle cap so a mistaken range cannot
  download forever.
- [x] Downloads are public and never send credentials.
- [x] Validation reports candle count, missing candles, duplicates,
  invalid rows and timeframe-grid alignment (chapter 29).
- [x] Every dataset receives a stable identity
  (`EXCHANGE_SYMBOL_INTERVAL_START_END_Vn`) and a SHA-256 checksum.
- [x] Datasets are persisted with their identity card (chapter 53.2).
- [x] The network transport is injectable, so the test suite never
  touches the internet.
- [x] A beginner-readable explanation is produced on failure and on
  validation problems.
- [ ] Historical download from a second exchange (Coinbase) — pending,
  chapter 26.3.
- [x] Automatic retry/backoff on transient network errors (exponential backoff with jitter for REST API calls — implemented in adapter.py)
  chapter 27.

---

## [x] 74. Research workflow and validity dashboard

A result must arrive with an explicit statement of how much of the
research protocol was actually completed (analysis §9, §15, §16).

- [x] One service runs hypothesis → strategy → costs → backtest →
  benchmark → out-of-sample → robustness → (optional) walk-forward →
  qualification.
- [x] Every run is deterministic for identical inputs.
- [x] Every run records an experiment with dataset id and checksum,
  parameters, execution assumptions, metrics and conclusion
  (chapter 52).
- [x] A validity checklist reports, per item, pass/fail plus a plain
  explanation: dataset quality, look-ahead protection, train/test
  separation, transaction costs, slippage model, benchmark,
  out-of-sample, walk-forward, Monte Carlo, parameter sensitivity,
  sample size, multiple testing, liquidity realism.
- [x] Liquidity/market impact is reported as **not satisfied** until it
  is genuinely modelled: the laboratory never marks its own homework.
- [x] The number of tested configurations is recorded and triggers a
  multiple-testing warning (chapter 43.1).
- [x] A plain-language verdict never upgrades an observation into
  evidence.
- [x] The validity evidence ladder is shown in the interface.
- [x] A dedicated experiment-comparison screen (implemented in Research Notebook)
  notebook compares selected experiments).

---

## [x] 75. Observable experiment lifecycle

Experiments must be visible, searchable, taggable and persistent
(analysis §5).

- [x] Statuses: draft, running, completed, failed, cancelled, archived,
  qualified, rejected.
- [x] Rejected experiments are kept, never deleted.
- [x] Every mutation persists to the research directory.
- [x] Search over hypothesis, strategy, dataset, notes and tags.
- [x] Side-by-side comparison with a union of metric keys.
- [x] Export and import of the experiment history as JSON.
- [x] Queued batch research jobs with progress and cancellation (ResearchQueue in experiment_manager.py)

---

## [x] 76. Integrated research notebook

The notebook is the trader's scientific record, not a text box
(analysis §6).

- [x] Entries are experiment records: hypothesis, dataset identity and
  checksum, parameters, execution assumptions, metrics and conclusion.
- [x] Research notes can be appended over time.
- [x] Records are searchable and comparable.
- [x] The history can be exported as JSON.
- [x] Auto-filling the manifest from a completed backtest inside the notebook (added "Auto-fill from backtest" button to NotebookDialog)
  notebook (the wizard records it automatically today).

---

## [x] 77. Honest assistant and strategy rule builder

- [x] The assistant is offline and deterministic by default; it states
  that it is not a generative model.
- [x] A real model backend can be injected without changing the UI; the
  chapter-55 restrictions still apply.
- [x] Assistant conversations are persisted.
- [x] The strategy builder is backed by the real builder module:
  validate, explain, export and import a versioned JSON rule.
- [x] No `eval`/`exec` anywhere in the builder.
- [x] The builder reports when a rule is incomplete (no entry/exit)
  instead of pretending it is tradable.
- [x] Executable rule strategies: builder blocks become a declarative
  `RuleStrategySpec` (`rule_strategy.py`) the engine can run, with no
  `eval`/`exec`; stop-loss/take-profit are evaluated on candle closes
  and the limitation is stated.
- [x] The Backtesting Lab can load a rule JSON and backtest it as a
  custom strategy.
- [x] The builder explains *why* a rule cannot run yet (arithmetic
  operators, filters) instead of guessing.
- [x] Parameter sweep launched from the builder itself (the Backtesting
  Lab sweep currently supports SMA parameters only).

---

## [x] 78. Complexity and multiple-testing awareness

- [x] Strategy complexity is analysed from the real strategy class and
  shown with its violations and the chapter-35 warning.
- [x] The backtesting lab runs a real parameter sweep over SMA
  fast/slow ranges.
- [x] The sweep states that it is exploration, not validation, and
  counts the configurations tried.
- [x] The optimizer fails loudly when nothing can be evaluated instead
  of silently reporting zero combinations.

---

## [x] 79. Paper trading over real market data and trading journal

The largest remaining gap (analysis §10, §11, §13). Replaying a
downloaded dataset works today; a continuous feed does not.

- [x] A continuous market-data feed for paper trading (WebSocket) - implemented in paper_session.py run_paper_session_live()
- [x] Paper orders, fills, fees and slippage against a simulated
  account, replaying real candles (`paper_session.py`).
- [x] The strategy never bypasses the risk manager: every intended order
  is evaluated first and rejections are recorded in the journal.
- [x] A trading journal recording, per trade: strategy, signal, time,
  price, risk decision, simulated fill, slippage, fee, exit, P/L and
  reason (`paper_session.TradeJournal`).
- [x] The journal renders for reading and saves/loads as JSON.
- [x] The paper-trading screen shows the account, the journal and the
  chapter-57 limitation note.
- [x] Beginner guide: `docs/en/beginners/paper-trading.md`.
- [x] A dedicated post-trade follow-up view (“what did the strategy know
  at the time?”, answered manually from the journal today).
- [x] Realistic execution from chapter 56 (partial fills, market impact)
  integrated into the paper pipeline.
- [x] Binance WebSocket, reconnection, rate limiting and stale-data
  detection (chapter 26.2/27) — implemented in
  `exchanges/binance/websocket_client.py` and `exchanges/binance/adapter.py`.
- [x] Spot testnet (chapter 68) — implemented in `ui/trading/testnet.py`.

---

## [x] 80. Learning Center as a real course

- [x] Twenty beginner lessons with quizzes exist.
- [x] Level 2 — practical trading: support/resistance, trend, range,
  volatility, ATR, momentum, mean reversion, breakout, volume,
  liquidity, spread, slippage, position sizing, expectancy,
  R-multiple, risk of ruin (`education/curriculum.py`).
- [x] Level 3 — quantitative research: hypothesis, variables,
  train/test, out-of-sample, walk-forward, overfitting, multiple
  testing, Monte Carlo, bootstrap, regimes, robustness, statistical
  significance.
- [x] Every lesson carries a real body and a graded quiz question.
- [x] Progress tracking, bookmarks and resume-where-you-left-off persist
  under the user's data directory.
- [x] Lesson-to-screen links (each lesson opening the related tool).
- [x] Screenshots and tutorial media.



## PART XVII - Packaging (deferred until the loop runs)

## [ ] 81. Python packaging *(deferred — see §Delivery sequencing)*

- [ ] Use `pyproject.toml`.
- [ ] Prefer a simple Debian-compatible backend such as setuptools.

Include:

- [ ] project metadata;
- [ ] graphical entry point;
- [ ] console entry point;
- [ ] translation files;
- [ ] icons;
- [ ] license;
- [ ] example files;
- [ ] typing information;
- [ ] resources through `importlib.resources`.

Expected commands:

- [ ] `python3 -m build`
- [ ] `python3 -m pytest`
- [ ] `python3 -m crypto_trading_lab`
- [ ] `crypto-trading-lab`

- [ ] Do not use paths that depend on the current working directory.

---
## [ ] 82. Debian package *(deferred — see §Delivery sequencing)*

- [ ] Create a complete and valid `debian/` directory.

Expected files:

- [ ] `debian/changelog`
- [ ] `debian/control`
- [ ] `debian/copyright`
- [ ] `debian/rules`
- [ ] `debian/source/format`
- [ ] `debian/watch`
- [ ] `debian/upstream/metadata`
- [ ] `debian/crypto-trading-lab.install`
- [ ] `debian/crypto-trading-lab.manpages`
- [ ] `debian/crypto-trading-lab.desktop`
- [ ] `debian/crypto-trading-lab.metainfo.xml`

Use:

- [ ] debhelper-compat;
- [ ] dh-python;
- [ ] pybuild;
- [ ] `dh-sequence-python3` where appropriate;
- [ ] automatic Python dependency substitution;
- [ ] tests during package build;
- [ ] `Rules-Requires-Root: no`;
- [ ] source format `3.0 (quilt)`.

The package must:

- [ ] install into standard paths;
- [ ] not install into `/opt`;
- [ ] not include a virtual environment;
- [ ] not download dependencies during the build;
- [ ] not use pip during Debian package construction;
- [ ] not include prebuilt wheels;
- [ ] not modify user files during installation;
- [ ] respect XDG directories;
- [ ] store user data in appropriate user directories;
- [ ] install icons;
- [ ] install a `.desktop` file;
- [ ] install AppStream metadata;
- [ ] include a man page;
- [ ] pass `lintian` reasonably;
- [ ] build in a clean environment using `sbuild` or `pbuilder`.

Carefully classify:

- [ ] `Build-Depends`;
- [ ] `Depends`;
- [ ] `Recommends`;
- [ ] `Suggests`.

- [ ] Do not declare a development-only package as a mandatory runtime dependency.

Include instructions for:

- [ ] `dpkg-buildpackage -us -uc -b`
- [ ] `lintian ../*.changes`

- [ ] Verify exact Debian 12 package names before writing `debian/control`.

---
## [ ] 83. AppImage *(deferred — see §Delivery sequencing)*

- [ ] Prepare a separate AppImage strategy.
- [ ] Do not add AppImage tools to the official Debian package `Build-Depends`.

Create:

- [ ] `packaging/appimage/README.md`
- [ ] `packaging/appimage/AppRun`
- [ ] `packaging/appimage/crypto-trading-lab.desktop`
- [ ] `packaging/appimage/crypto-trading-lab.appdata.xml`
- [ ] `packaging/appimage/build-appimage.sh`

The build script must:

- [ ] use `set -euo pipefail`;
- [ ] detect errors;
- [ ] not require root;
- [ ] use a temporary directory;
- [ ] clean resources;
- [ ] document dependencies;
- [ ] generate checksums;
- [ ] avoid including credentials;
- [ ] verify the artifact.

- [ ] Do not download binaries without verifying their origin and checksum.

---
