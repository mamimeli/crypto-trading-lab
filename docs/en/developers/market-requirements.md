# Market requirements (chapter 33.2)

ROADMAP chapter 33.2 asks each strategy to state, up front, the markets
and the data it can work with. The point is not paperwork: a strategy that
reads `candle.volume` and silently assumes the feed has it, or one that is
built for spot and is handed a contract it cannot trade, produces a
backtest number from data it could not actually have used. A declaration
that the gate can check is how the program says "this strategy could not
have used this data" instead of reporting a misleading result.

The single source of truth is `src/crypto_trading_lab/market_requirements.py`.
The registry does not need it — the engine already refuses to run a
strategy on data it cannot use — but the record makes the refusal
*explainable*.

## The seven declarations

1. **Compatible markets** — `compatible_markets`. A tuple of `BASE/QUOTE`
   symbols, or the `any` marker meaning "any market of a supported asset
   type". Built-in strategies are asset-class agnostic, so they use `any`.
2. **Supported asset types** — `asset_types`. A closed set
   (`spot`, `perpetual`, `futures`, `options`). The engine only trades
   `spot` today (`ENGINE_TRADING_MODE`), so a strategy that omits it
   cannot run, and `validate_for_run` says so.
3. **Required timeframe** — `required_timeframe`. `None` for built-ins
   (they work on any interval). A non-`None` value that disagrees with the
   requested timeframe is a *warning*, not a refusal.
4. **Required market-data fields** — `required_fields`. A subset of the
   fields the engine can supply (`open`, `high`, `low`, `close`,
   `volume`). A name outside that set is a declaration error, because the
   engine cannot provide it.
5. **Required indicators** — `required_indicators`. The values the
   strategy's `indicator_values()` must return for signal auditing
   (chapter 33.5). The deeper check — that `indicator_values()` actually
   returns them — lives in the test suite
   (`test_strategy_market_requirements.py`), because verifying it at
   runtime would mean touching the strategy's streaming state before the
   real run (chapter 33.7 forbids that). The consistency between the
   declared indicators and what `indicator_values()` returns is asserted
   in that same test file on real strategy instances.
6. **Warm-up period** — the strategy's `warmup_candles` attribute. It is
   derived from the indicator periods, so it is *not* duplicated here;
   chapter 33.7 validates the attribute directly.
7. **Minimum historical data required** — `min_data_required`. The floor
   for the *default* configuration. A parametrised strategy's true minimum
   is its `warmup_candles`, which rises with its parameters, so the
   runtime gate is the warm-up check (param-aware), and this figure is the
   documented default rather than a second floor.

## Why the minimum-data field is documentation, not a gate

A first implementation stored `min_data_required` and rejected runs below
it. That broke two things at once: it was wrong for non-default
configurations (a small `slow` period needs far fewer candles than the
default), and it would have fired a spurious warning on normal backtests.
The honest split is therefore:

* the *declared* minimum is documented per strategy (default configuration);
* the *enforced* minimum is the warm-up, checked by chapter 33.7 against
  the actual parameters.

The validation function `_check_market_requirements` in
`strategy_validation.py`
takes the `MarketRequirements` record, looks it up by the strategy
identifier when the caller does not pass one, and runs only the
declaration checks that do not depend on the sample length.

## Adding a new built-in

Append a `MarketRequirements` entry to `REQUIREMENTS` keyed by the
strategy id, matching its `required_fields` and `required_indicators` to
what the code actually reads and returns. The `__post_init__` rejects an
unknown asset type, an unsupported field, a malformed timeframe, or an
empty required-indicator name, so a typo fails at import time, not in a
backtest. Then add the strategy to `test_strategy_market_requirements.py`
so both the declaration and the code stay in agreement.
