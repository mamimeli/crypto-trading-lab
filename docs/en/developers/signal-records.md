# Signal records (chapter 33.5)

> **Short version.** A strategy decides, and a *signal* is that decision
> written down with the context needed to audit it later: when, which
> strategy and version, which market and timeframe, what type, on which
> indicator values, with which parameter set. The engine writes one record
> per candle and keeps them on the result.

## Why this exists

The engine used to keep only the `OrderSide | None` the strategy returned
and throw it away. That loses two distinctions the chapter cares about:

- **hold vs no signal.** `None` from a strategy that is *in* a position
  means "stay". `None` from a strategy that is *flat* means "nothing to
  say". Both used to be the same `None`.
- **the decision vs what the engine could act on.** A BUY while already
  long is a real decision that a long-only spot engine cannot use.

Neither loss is visible in a backtest's final equity, which is exactly why
it needs recording rather than reconstructing.

## The vocabulary

| `SignalType` | Emitted today | Means |
|---|---|---|
| `enter_long` | yes | the strategy wants to be long; actionable only when flat |
| `exit_long` | yes | the strategy wants to be out; actionable only when long |
| `enter_short` | **no** | in the vocabulary, no engine side to emit it |
| `exit_short` | **no** | same |
| `hold` | yes | in a position, nothing to change |
| `no_signal` | yes | flat, nothing to do |

The short names exist because chapter 33.5 lists them, and `Signal`
rejects anything that is not a `SignalType`, so a typo cannot become a
seventh kind. But the engine is long-only spot: **no code path emits
`enter_short` or `exit_short`**, and the ROADMAP boxes for them stay
unticked until a short-capable engine exists. An enum member is not the
feature the chapter asks for.

## The record

```python
Signal(
    timestamp=...,          # UTC, timezone-aware (naive is rejected)
    strategy_id="ma_crossover",
    strategy_version="1.0.0",
    market="BTC/USDT",
    timeframe="1h",
    type=SignalType.ENTER_LONG,
    indicator_values={"sma_fast": Decimal("101.2"), "sma_slow": Decimal("99.8")},
    parameters="ma_crossover@1.0.0(fast=5, slow=20)",
    actionable=True,
)
```

| Chapter 33.5 asks for | Field |
|---|---|
| timestamp | `timestamp` (UTC; a naive datetime raises) |
| strategy identifier | `strategy_id` |
| strategy version | `strategy_version` |
| market | `market` (from `candle.symbol`) |
| timeframe | `timeframe` (from `candle.interval`) |
| signal type | `type` |
| relevant indicator values | `indicator_values` |
| parameters or parameter-set identifier | `parameters` — the chapter 33.4 `signature()` |

The record is frozen and `indicator_values` is a `MappingProxyType`, so a
signal cannot be edited after the fact; `to_dict()` gives the JSON-friendly
form (decimals as strings, so `30.50` does not become `30.5`).

## Where the identifier comes from

`Strategy.name` is a sentence that changes with the parameters
(`"SMA(5)xSMA(20) crossover"`), so it cannot be the identifier. Each
built-in declares a `ClassVar` `identifier` equal to its registry id, and
the engine resolves the stamp in this order:

1. `BacktestConfig.strategy_id` — the application knows the registry id;
2. the strategy's own `identifier`;
3. `name`, for a strategy that is not registered;
4. `"unknown"`, which is honest rather than a guess.

`tests/test_strategy_registry.py` asserts that every built-in's
`identifier` equals the id it is registered under, so the two cannot drift
apart silently.

## Indicator values

Each strategy exposes `indicator_values(index, candles)`, so a record can be
read back without re-running the strategy:

| Strategy | Records |
|---|---|
| `ma_crossover` | `sma_fast`, `sma_slow` |
| `rsi` | `rsi` |
| `breakout` | `rolling_high`, `rolling_low` — the window the decision was taken on, captured *before* the current candle joins the deque |
| `bollinger` | `middle`, `upper`, `lower` |
| `rule` | every non-constant operand in the rule (`close`, `sma(20)`, …) |
| `buy_and_hold`, `null_strategy` | nothing — an honest empty, not a missing field |

## What the engine does with them

`run_backtest()` appends one record per candle to `BacktestResult.signals`,
including the candles where nothing happened — a run of 240 candles has 240
signals, because the *absence* of a decision is part of the record. The
record is taken at the close of candle `i` while the fill happens at the
open of `i+1`, so a signal is never mistaken for a fill:

```python
result = run_backtest(candles, BuyAndHoldStrategy())
result.signals[0].type        # SignalType.ENTER_LONG
result.exposure_curve         # (False, True, True) — the fill lands later
```

## Limits, stated plainly

- **Signals are not persisted yet.** They live on the result object and
  `to_dict()` exists for journals and reports, but nothing writes them to
  the database. Chapter 62's journal is where that belongs.
- **One record per candle costs memory.** A 500k-candle run holds 500k
  frozen records. That is fine for research sizes and is the price of
  auditable output; a streaming consumer would need a callback instead.
- **The short vocabulary is unused.** See above: no emitter, so the boxes
  stay open.
- **No signal is evidence of an edge.** See
  [`research-ethics.md`](research-ethics.md).
