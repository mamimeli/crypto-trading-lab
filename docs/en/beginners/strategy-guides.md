# Every Strategy, Explained — The Ten Questions

A strategy is a rule about the future, written by somebody looking at
the past. If you cannot say what it assumes, you cannot notice the day
that assumption stops being true — and that is exactly the day it
starts losing your money.

This page answers the same ten questions for every strategy built into
Crypto Trading Lab. They are the questions ROADMAP chapter 33.9
requires, and the application will not let you run a strategy without
them being answerable.

1. What does the strategy attempt to do?
2. What market behaviour does it assume?
3. What indicators does it use?
4. What causes an entry?
5. What causes an exit?
6. How does position sizing work?
7. How do stop-loss and take-profit work?
8. What conditions may favour it?
9. What conditions may hurt it?
10. Why does historical profitability not guarantee future
    profitability?

You do not have to read this page to use the program: the same answers
appear in the Backtesting Lab report under **"What this strategy is
trying to do"**, and from the command line:

```bash
python -m crypto_trading_lab list-strategies --explain
python -m crypto_trading_lab list-strategies --explain rsi
```

The text is generated from a single source (`strategy_guide.py`), so
the page, the window and the terminal cannot drift into telling three
different stories.

---

## What each strategy needs from the market (chapter 33.2)

Before a strategy runs, it must say what it can run on. ROADMAP
chapter 33.2 asks for seven declarations; six of them are stated here,
and the seventh — the warm-up period — is the strategy's own
`warmup_candles` attribute, which chapter 33.7 checks before every run.

"Any market" means any spot `BASE/QUOTE` pair. All built-ins are
long-only spot, so none is restricted to a single symbol, but the
declaration is what lets the program refuse a strategy that was built
for a market it cannot trade. "Required fields" are the candle fields
the strategy reads; "Required indicators" are the values its signals
record (chapter 33.5). "Minimum data" is the *default* configuration's
warm-up — the runtime gate is the actual warm-up, which rises with the
parameters.

| Strategy | Asset types | Compatible markets | Required fields | Required indicators | Min. data (default) |
| --- | --- | --- | --- | --- | --- |
| `ma_crossover` | spot | any | open, close | sma_fast, sma_slow | 31 |
| `rsi` | spot | any | close, volume | rsi | 15 |
| `breakout` | spot | any | close, high, low | rolling_high, rolling_low | 21 |
| `bollinger` | spot | any | close | middle, upper, lower | 20 |
| `buy_and_hold` | spot | any | close | — | 2 |
| `null_strategy` | spot | any | — | — | 0 |

These declarations are not decoration. They are the difference between a
backtest that tells you "this strategy could not have used this data"
and one that quietly reports a number from data the strategy was never
built for. The same text is printed by `list-strategies --explain` and
in the Backtesting Lab report, generated from `market_requirements.py`.

---

## The formal contract of each strategy (chapter 33.3)

Before the plain-language questions, the formal trading rules — what each
strategy is allowed to do once it holds a position. Every built-in is
long-only spot with **no stop, no take-profit and no trailing stop of its
own**: the engine never adds one, so a position stays open until the
strategy's own sell signal. Position sizing is the engine's shared rule
(fixed fraction of available cash, sized at the next open, one position at a
time, no leverage, every order gated by the risk manager). The chapter 33.3
declaration is generated from `trading_rules.py`.

| Strategy | Entry | Exit | Cooldown | Stop / take-profit |
| --- | --- | --- | --- | --- |
| `ma_crossover` | fast SMA above slow SMA | fast SMA below slow SMA | none | none / none |
| `rsi` | RSI crosses down through oversold (filters optional) | RSI crosses up through overbought | optional N candles after exit | none / none |
| `breakout` | close above rolling high | close below rolling low | none | none / none |
| `bollinger` | close crosses down through lower band | close returns to middle band | none | none / none |
| `buy_and_hold` | first fillable candle | never (by itself) | none | none / none |
| `null_strategy` | never trades | never trades | none | none / none |

A rule you build in the Strategy Builder can declare its own stop-loss and
take-profit as fractions of the entry price — but they are checked on
candle **closes**, not on intrabar extremes, so a fast wick can pass through
them unseen. That is the single most common way a rule backtest looks better
than the live account would, so it is stated here on purpose.

---

## Questions 6 and 7, answered once

Sizing and stops belong to the **engine**, not to any one strategy.
Writing six slightly different versions of the same paragraph would be
six chances to disagree, so they are stated once:

**How position sizing works.** Each entry uses a fixed fraction of the
available cash (`position_fraction`; `1.0` by default means all of it),
sized at the next candle's open. One position at a time, no
pyramiding, no leverage: the engine is long-only spot.

**How stops work for the built-in strategies.** None. The exit is the
strategy's own sell signal; the engine never adds a stop of its own, so
a position stays open until the strategy closes it.

**How stops work for a custom rule.** A rule can declare a stop-loss
and a take-profit as fractions of the entry price. They are checked on
candle **closes**, not on intrabar extremes, so a fast wick can pass
through them unseen.

That last sentence is the important one. A backtest that checks stops
on closes will always look better than a real account that had a stop
order sitting in the book during a wick.

---

## Moving average crossover (`ma_crossover`)

**1. What it tries to do.** Ride a trend: buy when a fast average of
the price rises above a slower one, and step out when it falls back
below.

**2. What it assumes.** Prices move in trends that last long enough to
pay the cost of entering and leaving. In a market that chops sideways
it buys near local tops and sells near local bottoms.

**3. Indicators.** `SMA(fast)`, `SMA(slow)`.

**4. Entry.** The fast SMA crosses above the slow SMA (a golden cross).
The engine fills at the next candle's open, never at the crossing
price.

**5. Exit.** The fast SMA crosses back below the slow SMA (a death
cross).

**8. May favour it.** Persistent trends in either direction; timeframes
long enough that one good trade pays many fees.

**9. May hurt it.** Sideways, choppy markets; very short timeframes
where fees and spread dominate the edge; a sharp reversal right after
a cross.

**10. Why the backtest is not a promise.** A crossover only works while
trends persist. The same rule that caught the last rally buys the top
of the next range, and a backtest on a trending sample cannot show you
that.

## RSI mean reversion (`rsi`)

**1. What it tries to do.** Buy after a sharp fall and sell after a
sharp rise: a bet that short-term extremes are followed by at least a
pause.

**2. What it assumes.** Extremes revert. In a strong trend the
"oversold" reading can stay low for a long time while the price keeps
falling.

**3. Indicators.** `RSI(period)`, volume average (optional), trend
average (optional).

**4. Entry.** RSI crosses down through the oversold level. If filters
are configured they must pass too: volume above its own average, and
the close above its trend average.

**5. Exit.** RSI crosses up through the overbought level. A cooldown
can block new entries for a number of candles after an exit.

**8. May favour it.** Range-bound markets that oscillate; assets that
overshoot and snap back.

**9. May hurt it.** Strong sustained downtrends — it buys falling
knives; long trends in either direction, where "overbought" stays
overbought for weeks.

**10. Why the backtest is not a promise.** "Oversold" is not "cheap".
The indicator measures how fast the price fell, not what the price is
worth, so a downtrend can keep it below the level while the account
loses money.

## Rolling high/low breakout (`breakout`)

**1. What it tries to do.** Follow strength: buy when the close breaks
above the highest high of the recent window, leave when it breaks
below the lowest low.

**2. What it assumes.** A move through a level many traders are
watching attracts more buyers, so the move continues.

**3. Indicators.** Rolling high, rolling low.

**4. Entry.** The close is above the highest high of the previous
`period` candles.

**5. Exit.** The close is below the lowest low of the previous `period`
candles.

**8. May favour it.** A market leaving a quiet range; volatile assets
that run once they start moving.

**9. May hurt it.** False breakouts that reverse immediately; quiet
ranges, where the window closes in around the price.

**10. Why the backtest is not a promise.** Breakouts are the classic
place to be faked out. The damage comes from many small failures, not
from the few large wins, and a backtest that happens to include a big
run hides that.

## Bollinger Bands mean reversion (`bollinger`)

**1. What it tries to do.** Buy when the price stretches below its own
average (the lower band) and take the profit when it returns to the
middle.

**2. What it assumes.** The price oscillates around a moving average
and extremes revert.

**3. Indicators.** `SMA(period)`, standard deviation, upper/lower
bands.

**4. Entry.** The close crosses down through the lower band.

**5. Exit.** The close crosses back up to the middle band.

**8. May favour it.** Range-bound markets; assets whose volatility
stays roughly stable.

**9. May hurt it.** Trending markets, where the price rides the band
instead of bouncing off it; volatility spikes that move the bands away
from the price.

**10. Why the backtest is not a promise.** The bands describe how much
the price has been moving; they do not say where it will go. A
widening band can look like an opportunity and be a warning.

## Buy and hold (`buy_and_hold`)

**1. What it tries to do.** Buy once and stay invested. It is the
benchmark every strategy must beat, not a strategy to trade.

**2. What it assumes.** Only that the asset goes up over the period.
Nothing else.

**3. Indicators.** None.

**4. Entry.** The first candle it can fill: the signal at candle 0
fills at candle 1's open.

**5. Exit.** Never, by itself.

**8. May favour it.** Long bull markets.

**9. May hurt it.** Long bear markets; assets that go to zero.

**10. Why the backtest is not a promise.** Beating it is the minimum
bar. A strategy that loses to buy and hold after costs added fees and
complexity without adding information.

## Null strategy (`null_strategy`)

**1. What it tries to do.** Never trade. It is the honest baseline:
what the account does when nothing happens.

**2. What it assumes.** Nothing.

**3. Indicators.** None.

**4. Entry.** Never.

**5. Exit.** Never.

**8. May favour it.** Measuring what costs and time alone do to a
result.

**9. May hurt it.** Nothing: it cannot lose money, and it cannot make
any either.

**10. Why the backtest is not a promise.** If a strategy cannot beat
doing nothing after costs, it is not a strategy; it is a fee
generator.

---

## Custom rules

A declarative rule written in the Strategy Builder describes its own
conditions, so it has no fixed guide. What it does not describe is the
engine around it: the sizing paragraph above still applies, and the
stops paragraph is the one to re-read, because close-checked stops are
the most common way a rule backtest flatters itself.

## Reading the answers together

Notice the pattern. Every strategy has one market it is built for and
one market that punishes it, and the two are the same market seen at
different times. That is not a flaw in these six strategies; it is what
a strategy is. The honest question is never "does it work?" but "when
does it stop working, and would I notice?"

If you cannot answer that second question about a strategy — yours or
one from this page — you do not have a strategy yet. You have a
backtest.

---

*See also: [indicators explained](indicators-explained.md),
[performance metrics](performance-metrics.md),
[statistical edge](statistical-edge.md) and the developer page on
[research ethics](../developers/research-ethics.md).*
