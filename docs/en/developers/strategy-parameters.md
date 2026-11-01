# Strategy parameters (chapter 33.4)

> **Short version.** A strategy's parameters are a contract with declared
> types, defaults, bounds and rules. The registry validates them *before*
> the strategy is built, invalid combinations never reach a run, and the
> exact values that ran are recorded with the result.

## Why this exists

Before chapter 33.4, parameters were a bag of keyword arguments: the
registry stored loose dictionaries, each caller coerced them by hand, and a
mistake surfaced either as a `TypeError` deep inside a factory or — worse —
as a silently ignored typo. The chapter asks for seven things per
parameter and three guarantees:

| Asked for | Where |
|---|---|
| name, type, default, minimum, maximum, allowed values, description | `ParameterSpec` |
| validation rules | `ParameterSpec.minimum`/`maximum`/`allowed`, plus `CombinationRule` for rules about two or more parameters |
| parameters versioned with the strategy | `ParameterSet.version`, `StrategyMetadata.version` |
| invalid combinations rejected before execution | `StrategyRegistry.create_instance()` |
| parameters never change silently during a run | `ParameterSet` is frozen, and `run_backtest()` checks the strategy's fields afterwards |

## The three types

```text
ParameterSpec   one parameter: kind, default, bounds, allowed values, rule text
ParameterSchema the specs one strategy version declares, plus combination rules
ParameterSet    the validated values, frozen, with a signature()
```

`ParameterSpec.coerce()` is the only place that decides what a value means,
and it is strict on purpose:

- `"20"` becomes `20` for an `int` parameter, but `2.5` and `"2.5"` do not;
- `True` is **not** accepted as a number, even though Python says it is an
  `int` — a boolean there is a bug, not a 1;
- `"true"`, `"no"`, `"1"` and `1` are accepted for a boolean;
- a `choice` parameter only accepts the values it declares;
- the **default is validated like any other value**: a spec whose default it
  would itself reject raises at construction, because that is a bug rather
  than a default.

## Combination rules

Some rules cannot live on one parameter. `fast < slow` is the classic case:
each value is individually valid and together they mean nothing.

```python
fast_below_slow = CombinationRule(
    "fast < slow",
    lambda values: (
        "fast must be smaller than slow; with fast >= slow the 'fast' "
        "average is not faster and the crossover means nothing"
    ) if values["fast"] >= values["slow"] else None,
)
```

The check receives the **complete** dictionary — defaults included — so a
half-specified pair cannot slip through. It returns a sentence, or `None`
when the combination is valid.

## Where the gate is

`StrategyRegistry.create_instance()` and `StrategyRegistry.parameter_set()`
both call `schema.validate()` first. That matters because every entry point
goes through them: the CLI, the GUI and the application services.

```python
registry.create_instance("ma_crossover", fast="5", slow="20")   # fast=5, slow=20
registry.create_instance("ma_crossover", fast=30, slow=10)      # ParameterError
registry.create_instance("buy_and_hold", periods=10)            # unknown parameter
registry.create_instance("ma_crossover", fast=500)              # at most 200
```

A misspelt parameter is rejected instead of swallowed, which is the whole
point of declaring a contract.

## What ran, recorded

`ParameterSet.signature()` produces one auditable string:

```text
ma_crossover@1.0.0(fast=5, slow=20)
```

The application records it in `BacktestConfig.strategy_parameters`, so it
lands in `BacktestResult.config_metadata` and the CLI prints it:

```text
Strategy: SMA(5)xSMA(20) crossover
Candles: 240
Parameters: ma_crossover@1.0.0(fast=5, slow=20)
```

The set itself is frozen and its mapping cannot be written to, so a caller
cannot quietly change a value mid-run. And because a strategy *could* still
assign to its own fields, `run_backtest()` snapshots the strategy's
dataclass fields before the loop and compares them after it: a change raises
instead of producing a result nobody can trust.

```text
ValueError: the strategy changed its own parameters during the backtest
(fast: 5 -> 9); chapter 33.4 forbids parameters changing inside a run.
Build a new instance with the values you want instead.
```

Only dataclass fields are compared, so a strategy's internal streaming state
(a moving average updating every candle) is never mistaken for a parameter.

## Limits, stated plainly

- **Combination rules do not survive JSON.** They are Python callables, and
  the registry stores the dictionary form. An entry loaded from
  `registry.json` is validated parameter by parameter until the code that
  owns it registers it again — the same limitation factories already have.
- **A stored schema with no `default` cannot become a typed schema.** Chapter
  33.4 requires a default, so such an entry keeps `parameter_schema=None` and
  falls back to the strategy's own checks, instead of refusing to load the
  whole registry over one old file.
- **The rule language has no parameter bounds.** Declarative rules
  (`rule_strategy.py`) carry their periods inside the rule itself; chapter 35
  reports their grid as `1` rather than inventing a range. See
  [`strategy-complexity.md`](strategy-complexity.md).
