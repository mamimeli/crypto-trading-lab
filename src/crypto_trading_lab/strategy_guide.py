"""Beginner documentation for every strategy (ROADMAP.md chapter 33.9).

A strategy is a rule about the future written by someone looking at the past.
If the person running it cannot say what it assumes, they cannot recognise the
day the assumption stops being true. Chapter 33.9 fixes the ten questions
every strategy must answer, and this module answers them in one place so the
CLI, the GUI and the beginner docs cannot tell three different stories.

The questions:

1. What does it attempt to do?
2. What market behaviour does it assume?
3. What indicators does it use?
4. What causes an entry?
5. What causes an exit?
6. How does position sizing work?
7. How do stop-loss and take-profit work?
8. What conditions may favour it?
9. What conditions may hurt it?
10. Why does historical profitability not guarantee future profitability?

Sizing and stops are answered once, because they belong to the engine rather
than to any one strategy — and saying so is more honest than writing six
slightly different versions of the same paragraph.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

__all__ = [
    "StrategyGuide",
    "GUIDES",
    "SIZING",
    "STOPS_BUILTIN",
    "STOPS_RULE",
    "guide_for",
    "render",
]

#: How the engine sizes a position, for every built-in strategy (chapter 37.4).
SIZING = (
    "Each entry uses a fixed fraction of the available cash "
    "(position_fraction; 1.0 by default means all of it), sized at the next "
    "candle's open. One position at a time, no pyramiding, no leverage: the "
    "engine is long-only spot."
)

#: Built-in strategies have no stop of their own.
STOPS_BUILTIN = (
    "None. The exit is the strategy's own sell signal; the engine never adds "
    "a stop of its own, so a position stays open until the strategy closes "
    "it."
)

#: Declarative rules can declare both, with a documented limitation.
STOPS_RULE = (
    "A rule can declare a stop-loss and a take-profit as fractions of the "
    "entry price. They are checked on candle closes, not on intrabar "
    "extremes, so a fast wick can pass through them unseen."
)


@dataclass(frozen=True)
class StrategyGuide:
    """The ten answers of chapter 33.9 for one strategy."""

    strategy_id: str
    title: str
    attempts: str
    assumes: str
    indicators: tuple[str, ...]
    entry: str
    exit: str
    favors: tuple[str, ...]
    hurts: tuple[str, ...]
    honesty: str
    sizing: str = SIZING
    stops: str = STOPS_BUILTIN

    def __post_init__(self) -> None:
        for name in ("strategy_id", "title", "attempts", "assumes", "entry", "exit"):
            if not getattr(self, name).strip():
                raise ValueError(f"{self.strategy_id}: {name} must not be empty")
        if not self.honesty.strip():
            raise ValueError(f"{self.strategy_id}: honesty must not be empty")


GUIDES: Mapping[str, StrategyGuide] = {
    "ma_crossover": StrategyGuide(
        strategy_id="ma_crossover",
        title="Moving average crossover",
        attempts=(
            "Ride a trend: buy when a fast average of the price rises above a "
            "slower one, and step out when it falls back below."
        ),
        assumes=(
            "Prices move in trends that last long enough to pay the cost of "
            "entering and leaving. In a market that chops sideways it buys "
            "near local tops and sells near local bottoms."
        ),
        indicators=("SMA(fast)", "SMA(slow)"),
        entry=(
            "The fast SMA crosses above the slow SMA (a golden cross). The "
            "engine fills at the next candle's open, never at the crossing "
            "price."
        ),
        exit="The fast SMA crosses back below the slow SMA (a death cross).",
        favors=(
            "persistent trends in either direction",
            "timeframes long enough that one good trade pays many fees",
        ),
        hurts=(
            "sideways, choppy markets",
            "very short timeframes where fees and spread dominate the edge",
            "a sharp reversal right after a cross",
        ),
        honesty=(
            "A crossover only works while trends persist. The same rule that "
            "caught the last rally buys the top of the next range, and a "
            "backtest on a trending sample cannot show you that."
        ),
    ),
    "rsi": StrategyGuide(
        strategy_id="rsi",
        title="RSI mean reversion",
        attempts=(
            "Buy after a sharp fall and sell after a sharp rise: a bet that "
            "short-term extremes are followed by at least a pause."
        ),
        assumes=(
            "Extremes revert. In a strong trend the 'oversold' reading can "
            "stay low for a long time while the price keeps falling."
        ),
        indicators=("RSI(period)", "volume average (optional)", "trend average (optional)"),
        entry=(
            "RSI crosses down through the oversold level. If filters are "
            "configured they must pass too: volume above its own average, and "
            "the close above its trend average."
        ),
        exit=(
            "RSI crosses up through the overbought level. A cooldown can block "
            "new entries for a number of candles after an exit."
        ),
        favors=(
            "range-bound markets that oscillate",
            "assets that overshoot and snap back",
        ),
        hurts=(
            "strong sustained downtrends: it buys falling knives",
            "long trends in either direction, where 'overbought' stays "
            "overbought for weeks",
        ),
        honesty=(
            "'Oversold' is not 'cheap'. The indicator measures how fast the "
            "price fell, not what the price is worth, so a downtrend can keep "
            "it below the level while the account loses money."
        ),
    ),
    "breakout": StrategyGuide(
        strategy_id="breakout",
        title="Rolling high/low breakout",
        attempts=(
            "Follow strength: buy when the close breaks above the highest high "
            "of the recent window, leave when it breaks below the lowest low."
        ),
        assumes=(
            "A move through a level many traders are watching attracts more "
            "buyers, so the move continues."
        ),
        indicators=("rolling high", "rolling low"),
        entry=(
            "The close is above the highest high of the previous period "
            "candles."
        ),
        exit="The close is below the lowest low of the previous period candles.",
        favors=(
            "a market leaving a quiet range",
            "volatile assets that run once they start moving",
        ),
        hurts=(
            "false breakouts that reverse immediately",
            "quiet ranges, where the window closes in around the price",
        ),
        honesty=(
            "Breakouts are the classic place to be faked out. The damage comes "
            "from many small failures, not from the few large wins, and a "
            "backtest that happens to include a big run hides that."
        ),
    ),
    "bollinger": StrategyGuide(
        strategy_id="bollinger",
        title="Bollinger Bands mean reversion",
        attempts=(
            "Buy when the price stretches below its own average (the lower "
            "band) and take the profit when it returns to the middle."
        ),
        assumes=(
            "The price oscillates around a moving average and extremes revert."
        ),
        indicators=("SMA(period)", "standard deviation", "upper/lower bands"),
        entry="The close crosses down through the lower band.",
        exit="The close crosses back up to the middle band.",
        favors=(
            "range-bound markets",
            "assets whose volatility stays roughly stable",
        ),
        hurts=(
            "trending markets, where the price rides the band instead of "
            "bouncing off it",
            "volatility spikes that move the bands away from the price",
        ),
        honesty=(
            "The bands describe how much the price has been moving; they do "
            "not say where it will go. A widening band can look like an "
            "opportunity and be a warning."
        ),
    ),
    "buy_and_hold": StrategyGuide(
        strategy_id="buy_and_hold",
        title="Buy and hold (benchmark)",
        attempts=(
            "Buy once and stay invested. It is the benchmark every strategy "
            "must beat, not a strategy to trade."
        ),
        assumes="Only that the asset goes up over the period. Nothing else.",
        indicators=(),
        entry="The first candle it can fill: the signal at candle 0 fills at candle 1's open.",
        exit="Never, by itself.",
        favors=("long bull markets",),
        hurts=("long bear markets", "assets that go to zero"),
        honesty=(
            "Beating it is the minimum bar. A strategy that loses to buy and "
            "hold after costs added fees and complexity without adding "
            "information."
        ),
    ),
    "null_strategy": StrategyGuide(
        strategy_id="null_strategy",
        title="Null strategy (does nothing)",
        attempts=(
            "Never trade. It is the honest baseline: what the account does "
            "when nothing happens."
        ),
        assumes="Nothing.",
        indicators=(),
        entry="Never.",
        exit="Never.",
        favors=("measuring what costs and time alone do to a result",),
        hurts=("nothing: it cannot lose money, and it cannot make any either",),
        honesty=(
            "If a strategy cannot beat doing nothing after costs, it is not a "
            "strategy; it is a fee generator."
        ),
    ),
}


def guide_for(strategy_id: Optional[str]) -> Optional[StrategyGuide]:
    """The guide for a registered strategy, or ``None`` when there is none.

    A strategy added later without a guide is a documentation gap, not an
    error: the caller decides whether to say so.
    """
    if strategy_id is None:
        return None
    return GUIDES.get(str(strategy_id))


def render(guide: StrategyGuide) -> str:
    """The ten questions as readable text, for a terminal or a panel."""
    lines = [f"{guide.title} ({guide.strategy_id})", ""]
    lines.append(f"What it tries to do: {guide.attempts}")
    lines.append(f"What it assumes: {guide.assumes}")
    lines.append(
        "Indicators it uses: "
        + (", ".join(guide.indicators) if guide.indicators else "none")
    )
    lines.append(f"What makes it enter: {guide.entry}")
    lines.append(f"What makes it exit: {guide.exit}")
    lines.append(f"How position sizing works: {guide.sizing}")
    lines.append(f"How stops work: {guide.stops}")
    lines.append("Conditions that may favour it:")
    lines.extend(f"  - {item}" for item in guide.favors)
    lines.append("Conditions that may hurt it:")
    lines.extend(f"  - {item}" for item in guide.hurts)
    lines.append(f"Why a profitable backtest is not a promise: {guide.honesty}")
    return "\n".join(lines)
