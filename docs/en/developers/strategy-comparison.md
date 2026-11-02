# Strategy comparison (chapters 33.8 and 35)

How two strategies are weighed against each other on evidence and complexity,
and why the "favour the simpler one" rule is now something the program does
rather than only something it says.

## What this is

Chapter 33.8 says the application must *favour the simpler strategy when
performance is otherwise comparable*, and chapter 35 records complexity per
strategy version and says a more complex strategy must not be considered
automatically superior. The rule already existed as
`complexity_control.prefer_simpler`, and `complexity_growth_warning`
existed too — both tested — but nothing called them. So `SIMPLER_WINS` was
carried in the research-warning set and shown as **policy**, never as a
decision the program actually made.

This feature is the caller. It is the "screen that compares two strategies
side by side" the honest note in `ROADMAP.md` said did not yet exist.

## The command

```text
crypto_trading_lab compare-strategies A_ID B_ID
    [--evidence-a X] [--evidence-b Y] [--tolerance 0.10]
```

`A_ID` and `B_ID` are strategy identifiers from `list-strategies`. The
command resolves each from the registry and reads the complexity that
version declares (chapter 35), then:

* **Decision mode** — when both `--evidence-a` and `--evidence-b` are
  supplied. The two numbers must be the *same* performance metric from two
  backtests (both deflated Sharpe, or both total return), so they are
  comparable. `prefer_simpler` runs: within the tolerance the simpler
  strategy wins; beyond it the better evidence wins, and the reason says so.
* **Policy mode** — when either evidence is missing. The two complexities
  are reported and the `SIMPLER_WINS` statement is shown as policy, not as a
  decision. This is the honest state: without two measured numbers there is
  nothing to weigh.

## The module

`src/crypto_trading_lab/strategy_comparison.py` is read-only and small on
purpose:

* `compare_strategies(a_id, b_id, *, evidence_a, evidence_b, tolerance,
  registry)` returns a frozen `StrategyComparison` (`mode`, the two
  `StrategyComplexity` records, the optional evidence, and the
  `ComplexityComparison` when it ran). It never mutates the registry, so it
  leaves no file behind.
* `render_comparison(comparison)` turns the result into the text the CLI
  prints. It is also usable by the Backtesting Lab or a report.

The tolerance is *relative*: evidence is "comparable" when
`|a - b| <= tolerance * max(|a|, |b|)`. The default is 10%.

## Why evidence is supplied, not fetched

The tool consumes a metric; it does not decide which metric matters. A
backtest produces many numbers (return, Sharpe, drawdown…), and which one
is the right evidence for a choice is a research decision the user owns.
Supplying it explicitly keeps the comparison honest and unit-testable
without a market-data dependency.

## What closed

* ROADMAP 33.8 — the seventh box (favour simpler when comparable) is now
  behaviour, not just a carried statement.
* ROADMAP 35 — "when two strategies provide comparable evidence, the simpler
  strategy must be favored" (and, by the same mechanism, "a more complex
  strategy must not be considered automatically superior") are now backed by
  a screen that does exactly that.

Still open, and honestly so: chapter 35's "warn when complexity grows
without a corresponding evidence improvement" needs a *version*-comparison
surface (two versions of the same strategy), which this two-*strategy*
command does not provide; and chapter 33.5's two short-side boxes remain
unticked because the engine is long-only spot.
