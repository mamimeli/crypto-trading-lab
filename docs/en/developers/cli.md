# The command-line interface (chapter 22)

The desktop application and the CLI are two front ends over the same
use cases. Every command below that does work calls a function in
`src/crypto_trading_lab/application.py`, and the GUI calls the same
functions, so the two cannot drift apart. The CLI never prints a secret
and never claims success it did not achieve: a command that cannot do
its job prints the reason and returns a non-zero exit status.

## Running it

From a source checkout:

```bash
PYTHONPATH=src python3 -m crypto_trading_lab --help
```

After an install (pip or the Debian package):

```bash
crypto-trading-lab --help
```

With no arguments it starts the graphical application; with any
argument it runs the CLI.

## Commands

| Command | What it really does |
|---|---|
| `crypto-trading-lab --version` | Prints the package version. |
| `crypto-trading-lab doctor` | Runs every chapter 22 diagnostic (see below). |
| `crypto-trading-lab database check` | Opens the SQLite file, runs `PRAGMA integrity_check`, prints the schema version and the row count of every table. A missing database is reported as missing — nothing is created. |
| `crypto-trading-lab import-csv file.csv` | Validates the file with the chapter 28 parser and stores the candles. Invalid rows are rejected **before** the database is created. |
| `crypto-trading-lab backtest strategy.yaml` | Loads stored candles and runs the chapter 37 engine plus the chapter 40 metric catalogue. |
| `crypto-trading-lab list-strategies` | Lists the chapter 36 registry (built-ins and imported metadata). `--explain` prints the chapter 33.9 beginner guide — one strategy if you name its id, all of them if you do not. |
| `crypto-trading-lab list-lessons` | Lists the 48-lesson curriculum; `--level` 1, 2 or 3 filters it. |
| `crypto-trading-lab glossary search "slippage"` | Searches the English beginner glossary; entry-name matches are listed first, definition matches after. Exit status 1 when nothing matches. |

`import-csv` accepts `--symbol` (default `BTC/USDT`) and `--interval`
(default `1m`). Every data-reading command accepts `--data-dir`, which
points the CLI at another XDG data directory — useful for scripts and
for tests that must not touch your real data.

The grouped spellings `list strategies` and `list lessons` still work;
chapter 22 names the hyphenated forms.

## Writing a strategy configuration

`backtest` takes a small key/value file. JSON works everywhere. YAML
needs PyYAML: the Debian package depends on `python3-yaml`, pip users get
it from `requirements-all.txt` or `pip install -e ".[yaml]"`, and a
missing reader is reported with the install command instead of a
traceback.

```yaml
strategy: ma_crossover     # any id from list-strategies
fast: 10                   # strategy parameters, validated against
slow: 30                   #   the registry's parameter schema
initial_capital: 10000
position_fraction: 1       # 0 < fraction <= 1
maker_fee: 0.001
taker_fee: 0.001
slippage: 0.0005
spread: 0.0002
benchmark: buy_and_hold    # buy_and_hold | null_strategy | none
execution_model: cost_model # cost_model | chapter_56 (see below)
execution_seed: 42         # reproduces the chapter 56 fills
# symbol: BTC/USDT         # optional: which stored market to use
# interval: 1m
```

Unknown keys are rejected with the list of allowed ones, so a typo is
never silently ignored. When `symbol`/`interval` are omitted the CLI
uses the most recent matching dataset, or the stored market with the
most candles.

The output is the same evidence the Lab shows: net profit, drawdown,
trade statistics, risk ratios, cost attribution, the benchmark
comparison, every statistical warning, and the disclaimer. A backtest
that looks profitable and a backtest that says "no edge here" are both
legitimate results. The output always names the execution model it used.

### Choosing the execution model (chapter 56)

`execution_model: cost_model` (the default) fills every order in full at
the next candle's open, moved by the configured `slippage` and `spread`
fractions. It is fast, deterministic, and a fair first look.

`execution_model: chapter_56` runs the execution-realism model instead: a
synthetic order book is built from the traded volume of the candles
**before** the fill candle, and the order walks that book. Three things can
happen, and all three are reported:

- a **full fill** at a price that includes the half-spread, the market
  impact and a seeded random component;
- a **partial fill** when the order is larger than the modelled depth —
  only what the book absorbs is bought or sold;
- a **rejection** when there is no depth at all, which includes the case
  where the stored candles carry no volume. The model refuses to assume
  unlimited liquidity, so it refuses the order.

`execution_seed` makes the random component reproducible: the same candles,
configuration and seed produce the same fills. Real latency and slippage
depend on market conditions that no offline model can observe, so treat a
difference between the two models as a measure of *how much the result
depends on execution assumptions* — not as a prediction.

## paper-live

`paper-live` paper-trades the **live** Binance WebSocket feed instead of a
stored dataset (chapters 26.2 and 57). Public market data needs no API key;
the account is simulated and no order ever reaches an exchange.

```bash
crypto-trading-lab paper-live --symbol BTC/USDT --interval 1m --minutes 5
crypto-trading-lab paper-live --strategy ma_crossover --set fast=5 --set slow=20
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--strategy` | `ma_crossover` | Any id from `list-strategies`. |
| `--set KEY=VALUE` | none | Strategy parameter; repeatable. |
| `--symbol` | `BTC/USDT` | Streamed pair. |
| `--interval` | `1m` | Any Binance kline interval: `1s`, `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`. |
| `--minutes` | `5` | How long to listen before returning. |
| `--capital` | `10000` | Simulated starting balance. |
| `--fee` | `0.001` | Taker fee as a fraction. |
| `--environment` | `spot-testnet` | `spot-testnet` or `production`. |

The session applies the same risk gate, the same chapter-56 execution
model and the same journal as a replay, with three differences that the
output states: fills use the closed candle's own close (there is no next
open yet), a session that receives no candle returns an empty curve instead
of a fabricated one, and **no signal is evaluated while the feed is
degraded** — those candles are buffered so the strategy keeps its history,
and the note says how many were skipped.

A strategy cannot trade before it has seen enough candles. The default
`ma_crossover` needs 31 one-minute candles (30 to fill the slow average,
plus one to compare it with); `buy_and_hold` needs 1. When the session ends
first, the output prints a `Warm-up:` line with the number the strategy
needed and the number that arrived, so an empty journal reads as *not
warmed up yet* rather than *no opportunity*. A strategy that does not
declare a warm-up prints no line, because guessing a number would be worse
than saying nothing.

The live path accepts every interval the exchange streams, `1s` included,
and the GUI's Historical Data screen offers the same set for downloads.
Monthly candles (`1M`) are validated month by month rather than against a
fixed step, because a calendar month is 28-31 days. One limit stays: a
period that would need more than 2,000,000 candles is refused *before*
the first request, telling you to shorten the period or pick a slower
timeframe.

Be careful with what a faster interval buys you — a 100-second SMA(5/20)
session over 1s candles made three trades and paid 25.5 in fees and
slippage against a smaller price move. The cost per trade is fixed; the
number of trades is not.

The command needs the optional `websockets` package. Without it the command
fails with the install line instead of a traceback, the same way a missing
YAML reader does.

## doctor

`doctor` checks, in order: Python version, required modules, the
database, filesystem permissions, keyring availability, public
connectivity, system-clock drift, Qt resources, translations, XDG
paths, English documentation and Spanish translation availability.

Two checks need the outside world (connectivity and clock drift). They
are **off by default** so the command is deterministic and the test
suite stays offline; `doctor --network` runs them. The report uses
`PASS`, `WARN`, `SKIP` and `FAIL`, and the exit status is 1 only when
something failed — a warning is information, not a build breaker.

`doctor` never reads a credential store, so it cannot print a secret.
A test enforces that by making `KeyringCredentialStore.load` and
`.list` raise if they are ever called during a doctor run.
