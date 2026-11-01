# Trading rules (chapter 33.3)

ROADMAP chapter 33.3 asks each strategy to state its trading rules: entry,
exit, invalidation, stop-loss, take-profit, trailing stop, cooldown, time
restrictions and position sizing. The engine already *implements* most of
these — it is long-only spot, fills at the next candle's open, holds one
position at a time, uses no leverage, and gates every order (entries and
exits) through the risk manager (chapter 33.6 / 58). What was missing was a
single place that *says so* next to the strategy.

The single source of truth is
`src/crypto_trading_lab/trading_rules.py`. It holds one frozen
`TradingRules` record per built-in strategy with the nine declarations, and
`render_trading_rules()` turns it into the text shown to the reader. The
registry does not need it: the beginner guide (chapter 33.9) explains the
rules in plain words and the rule engine (`rule_strategy.py`) checks the
structured ones at construction. The declaration is the formal contract in
one block, so a strategy cannot drift from what the engine will do without
the reader noticing.

## The nine declarations

1. **Entry conditions** — the signal that opens a position.
2. **Exit conditions** — the signal that closes it.
3. **Invalidation** — a condition that cancels a pending or open position
   before the exit; "none" for the built-ins, which hold until the exit
   signal.
4. **Stop-loss** — "none" for every built-in (the engine never adds a stop
   of its own). A rule built in the Strategy Builder may declare a stop as a
   fraction of entry.
5. **Take-profit** — "none" for the built-ins; a rule may declare one.
6. **Trailing stop** — "none" everywhere today.
7. **Cooldown** — the RSI strategy may block new entries for `N` candles
   after an exit; "none" for the others.
8. **Time restrictions** — "none" for the built-ins.
9. **Position sizing** — the engine's shared rule, stated once in
   `POSITION_SIZING` so the six records cannot disagree about it.

## Why the stops read "none" matters

The exit of a built-in is its own sell signal; the engine never adds a stop
of its own, so a position stays open until the strategy closes it. A custom
rule's stop-loss and take-profit, by contrast, are checked on candle
**closes**, not on intrabar extremes — a fast wick can pass through them
unseen (this is documented in `STOPS_RULE` in `strategy_guide.py` and in
the beginner guide). That asymmetry is the single most common way a rule
backtest flatters itself, which is why it is stated in the same block as the
rules.

## The gate behind the declaration

The genuinely enforced parts of chapter 33.3 live in the rule engine, not
in the declaration:

* `RuleStrategySpec.__post_init__` rejects a rule with no entry condition,
  a mode outside `all`/`any`, or a stop-loss / take-profit fraction outside
  `(0, 1)`.
* `validate_for_run` (chapter 33.7) warns when a rule has no exit condition
  *and* no stop or take-profit — a position that can never close.

The declaration itself is checked structurally: `TradingRules.__post_init__`
refuses a blank entry, exit or any other field (a blank field is a
forgotten declaration, not a "none").

## Adding a new built-in

Append a `TradingRules` entry to `RULES` keyed by the strategy id, matching
what the code actually does (the engine's behaviour, not the author's
intent). `test_trading_rules.py` checks that every built-in has a coherent
record and that entry and exit are stated, so a new strategy cannot ship
without its contract.
