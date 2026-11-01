# Strategy validation (chapter 33.7)

> **Short version.** Before a run, the strategy is checked against the data
> it is about to receive: configuration, parameters, indicators, timeframe,
> warm-up, market, and its own rules. **Errors stop the run; warnings travel
> with the result and are printed.**

## Why this exists

A backtest that cannot mean anything is worse than no backtest: it produces
a number, a chart and a report, and all three are noise. The classic case is
the warm-up — a strategy that needs 501 candles on a sample of 240 never
emits a single signal, so its "0% return" is not a result, it is an empty
run. The chapter asks for that to be refused *before* the sample is spent.

The second case is quieter: the run works, but most of the sample is warm-up,
or the data is for a different market than the one requested. Those must not
stop anything; they must be visible.

## Errors versus warnings

| | Meaning | Effect |
|---|---|---|
| `Severity.ERROR` | the run cannot produce a meaningful result | refuses to run |
| `Severity.WARNING` | it can, but the user should know | runs, and the warning is kept |

Collapsing the two would make the gate either useless (nothing blocks) or
infuriating (every short sample refuses). `StrategyValidation.ok` is true
when there are no errors; `raise_for_errors()` raises
`StrategyValidationError` with every reason in one message.

```text
error [warmup]: the strategy needs 501 candles before its first signal and
the run has 240: it can never act
```

Every issue carries a **stable code** (`configuration`, `parameters`,
`indicators`, `timeframe`, `warmup`, `market`, `rules`) so a caller can
filter or translate without parsing prose, and the code is in the printed
line so a report a user pastes into an issue says which check fired.

## The eight checks

| Check | What it looks at |
|---|---|
| configuration | `on_candle` is callable; `warmup_candles` is a non-negative int; a name exists (warning) |
| parameters | the chapter 33.4 schema, re-validated when the caller supplies it |
| indicators | the longest indicator a rule reads must fit in the sample; a strategy without `indicator_values()` is a warning (chapter 33.5) |
| timeframe | the `1m`/`4h`/`1d` grammar; one interval in the data; the data matches the request |
| warm-up | `available <= warmup` is an error; `available < 2 * warmup` is a warning |
| market | `BASE/QUOTE`; one market in the data; the data matches the request |
| rules | identical entry and exit, conditions between two constants, bounds that cannot both hold |
| warnings | everything above that is not fatal, reported instead of hidden |

## Contradictory rules

Rules are data, so they can be inspected without running them. Three
contradictions are refused:

```python
# entry and exit are the same condition: open and close at once
RuleStrategySpec(name="x", entry=(Condition("close", ">", "sma(5)"),),
                 exit=(Condition("close", ">", "sma(5)"),))

# always true or always false, never a decision
Condition("50", ">", "40")

# cannot both hold
entry=(Condition("close", ">", "100"), Condition("close", "<", "50"))
```

The last one is computed from the numeric bounds each condition implies: per
operand, the tightest lower and upper bound are collected, and the entry is
impossible when the lower bound is above the upper — or equal to it while at
least one comparison is strict. Comparisons between two indicators have no
fixed bound, so they are not judged.

## Where it runs

Both halves of the chapter, because they have different information:

- **Backtest** (`run_backtest` in `application.py`): the candles are already
  loaded, so everything is checked. Errors become an
  `ApplicationError` listing every reason; warnings are kept on
  `BacktestRun.validation` and the CLI prints them under `Candles:`.
- **Paper trading** (`run_live_paper_session`): the candles have not arrived
  yet, so `validate_for_run(..., candles=None)` skips the length-dependent
  checks instead of guessing. Configuration, market and timeframe form are
  still checked; the warm-up is reported after the session.

## Limits, stated plainly

- **Validation does not run the strategy.** It reads declarations only.
  Calling `on_candle` to "see if it works" would advance the streaming
  state before the real run, which is the silent interference chapter 33.4
  forbids. The cost: a strategy that is wrong *internally* but declares
  sane things passes.
- **No cross-condition reasoning beyond numeric bounds.** `close > sma(20)`
  and `close < sma(20)` is also impossible, but it needs symbolic reasoning;
  the check only understands numbers.
- **The rule checks need a `RuleStrategySpec`.** A strategy built by hand has
  no declarative rules to inspect, so only the generic checks apply.
- **Validation is not a quality judgement.** A valid strategy can still be a
  bad strategy; see [`research-ethics.md`](research-ethics.md) and chapter
  33.8.
