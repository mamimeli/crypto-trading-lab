"""Strategy identity: the nine facts every strategy must declare (33.1).

ROADMAP chapter 33.1 asks each strategy to declare who and what it is before
it declares how it trades. Those nine facts used to be spread over three
places — a registry record built from the id (``ma_crossover`` became
"Ma Crossover"), a guide written later for beginners, and prose in the docs —
so nothing could check that they agreed.

This module is the one place a built-in strategy is named. The registry reads
it to fill its metadata, so the name in ``list-strategies``, the name in a
backtest report and the name in the docs are the same string by construction
rather than by discipline.

The nine declarations, in the chapter's order:

1. name                     → :attr:`StrategyIdentity.name`
2. unique identifier        → :attr:`StrategyIdentity.strategy_id`
3. version                  → :attr:`StrategyIdentity.version`
4. author or source         → :attr:`StrategyIdentity.author`
5. description              → :attr:`StrategyIdentity.description`
6. strategy category        → :attr:`StrategyIdentity.category`
7. beginner-oriented
   explanation              → :attr:`StrategyIdentity.beginner_explanation`
8. known weaknesses         → :attr:`StrategyIdentity.known_weaknesses`
9. risk warnings            → :attr:`StrategyIdentity.risk_warnings`

Weaknesses and warnings are deliberately separate. A *weakness* is where the
strategy itself is fragile (it cannot tell a range from a trend). A *risk
warning* is what that fragility does to an account (a drawdown can run
further than you expect). Merging them into one list would let a strategy
declare the mild version of each and skip the expensive one.

Chapter 33.2 (market requirements) and 33.3 (trading rules) extend this
record in their own modules; identity stays a description of the *thing*,
not of its behaviour.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

__all__ = [
    "StrategyCategory",
    "CATEGORIES",
    "StrategyIdentity",
    "IDENTITIES",
    "identity_for",
    "render_identity",
    "IDENTIFIER_RE",
    "VERSION_RE",
]

#: The closed set of categories. A free-text category cannot be counted,
#: filtered or compared, so an unknown one is rejected instead of stored.
TREND_FOLLOWING = "trend-following"
MEAN_REVERSION = "mean-reversion"
BREAKOUT = "breakout"
BENCHMARK = "benchmark"
BASELINE = "baseline"

CATEGORIES: Tuple[str, ...] = (
    TREND_FOLLOWING,
    MEAN_REVERSION,
    BREAKOUT,
    BENCHMARK,
    BASELINE,
)


class StrategyCategory:
    """Names for :data:`CATEGORIES`, so callers need not retype strings."""

    TREND_FOLLOWING = TREND_FOLLOWING
    MEAN_REVERSION = MEAN_REVERSION
    BREAKOUT = BREAKOUT
    BENCHMARK = BENCHMARK
    BASELINE = BASELINE


#: An identifier is what a config file, a CLI argument and a signal record
#: all carry, so it stays lowercase, ASCII and free of spaces.
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_]*$")

#: ``MAJOR.MINOR.PATCH``, the version the registry already uses (chapter 36).
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass(frozen=True)
class StrategyIdentity:
    """Who a strategy is, before it says anything about trading (33.1)."""

    strategy_id: str
    name: str
    version: str
    author: str
    description: str
    category: str
    beginner_explanation: str
    known_weaknesses: Tuple[str, ...]
    risk_warnings: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not IDENTIFIER_RE.match(self.strategy_id):
            raise ValueError(
                f"{self.strategy_id!r} is not a valid strategy identifier: "
                "use lowercase letters, digits and underscores, starting "
                "with a letter"
            )
        if not VERSION_RE.match(self.version):
            raise ValueError(
                f"{self.strategy_id}: version {self.version!r} is not "
                "MAJOR.MINOR.PATCH"
            )
        if self.category not in CATEGORIES:
            raise ValueError(
                f"{self.strategy_id}: unknown category {self.category!r}; "
                f"use one of {', '.join(CATEGORIES)}"
            )
        for field in ("name", "author", "description", "beginner_explanation"):
            if not getattr(self, field).strip():
                raise ValueError(f"{self.strategy_id}: {field} must not be empty")
        # A strategy with nothing to confess is a strategy nobody reviewed.
        if not self.known_weaknesses:
            raise ValueError(f"{self.strategy_id}: declare at least one weakness")
        if not self.risk_warnings:
            raise ValueError(f"{self.strategy_id}: declare at least one risk warning")

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-safe view, for reports and the registry export."""
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "category": self.category,
            "beginner_explanation": self.beginner_explanation,
            "known_weaknesses": list(self.known_weaknesses),
            "risk_warnings": list(self.risk_warnings),
        }

    def summary(self) -> str:
        """One line: the name, the identifier and what kind of strategy it is."""
        return f"{self.name} ({self.strategy_id}, {self.category})"


IDENTITIES: Mapping[str, StrategyIdentity] = {
    "ma_crossover": StrategyIdentity(
        strategy_id="ma_crossover",
        name="Moving average crossover",
        version="1.0.0",
        author="Built-in",
        description=(
            "Buys when a fast simple moving average crosses above a slow one "
            "and sells when it crosses back below."
        ),
        category=TREND_FOLLOWING,
        beginner_explanation=(
            "Two averages of the price, one quick and one slow. When the "
            "quick one climbs above the slow one, the price has started "
            "rising faster than before, and the strategy buys; when it falls "
            "back below, it sells. You are trying to be in the market while a "
            "trend lasts and out of it while the price chops sideways."
        ),
        known_weaknesses=(
            "It cannot tell a trend from a range: a sideways market produces "
            "crossovers that are pure noise.",
            "It is always late. The averages are made of past prices, so both "
            "the entry and the exit happen after the move began.",
            "One bad candle can flip the signal, because it only looks at "
            "whether one average is above the other.",
        ),
        risk_warnings=(
            "Whipsaw losses arrive in clusters: several small losses in a row "
            "is the normal cost of waiting for a trend.",
            "There is no stop. A position stays open until the sell signal "
            "fires, so a drawdown can run further than you expect.",
            "It is long-only spot, so a sustained fall is either a loss or a "
            "flat period; it cannot profit from the decline.",
        ),
    ),
    "rsi": StrategyIdentity(
        strategy_id="rsi",
        name="RSI mean reversion",
        version="1.0.0",
        author="Built-in",
        description=(
            "Buys when the Relative Strength Index falls through an oversold "
            "level and sells when it rises through an overbought one, with "
            "optional volume, trend and cooldown filters."
        ),
        category=MEAN_REVERSION,
        beginner_explanation=(
            "The RSI measures how fast the price has been falling or rising. "
            "When it drops below a low level the price has fallen hard and "
            "quickly, and the strategy bets on at least a pause; when the "
            "indicator climbs above a high level, it takes the profit. The "
            "optional filters ask for confirmation before buying: volume "
            "above its own average, and the price above its trend average."
        ),
        known_weaknesses=(
            "'Oversold' is not 'cheap'. The indicator measures speed, not "
            "value, so it can stay below the level for weeks.",
            "It buys falling knives: the sharpest falls are often the ones "
            "that continue.",
            "The filters are correlated with each other — volume and trend "
            "usually confirm each other — so adding both does less than it "
            "looks like it does.",
        ),
        risk_warnings=(
            "A single position held through a sustained decline can lose more "
            "than several winning trades make back.",
            "There is no stop. The exit is the overbought signal, which may "
            "never arrive in a downtrend.",
            "The filters reduce the number of trades, which also reduces the "
            "sample you can judge the strategy on.",
        ),
    ),
    "breakout": StrategyIdentity(
        strategy_id="breakout",
        name="Rolling high/low breakout",
        version="1.0.0",
        author="Built-in",
        description=(
            "Buys when the close breaks above the highest high of the recent "
            "window and sells when it breaks below the lowest low."
        ),
        category=BREAKOUT,
        beginner_explanation=(
            "Look back a fixed number of candles and note the highest and "
            "lowest price in that window. If the price closes above the "
            "highest high, something changed and buyers are in control, so "
            "the strategy buys. If it closes below the lowest low, the sellers "
            "won and it sells."
        ),
        known_weaknesses=(
            "False breakouts: a move through the level that reverses "
            "immediately is the most common outcome in quiet markets.",
            "The window is a fixed length, so the level it watches adapts "
            "slowly to a market that changed character.",
            "It enters late by construction — after the level is already "
            "broken, which is often after the cheapest part of the move.",
        ),
        risk_warnings=(
            "The loss pattern is many small failures and a few large wins: a "
            "backtest that happens to include one big run flatters the "
            "strategy.",
            "There is no stop. A breakout that reverses is held until the "
            "opposite signal, which can be far away.",
            "Gaps and thin liquidity can fill the entry well past the level, "
            "so the modeled price is optimistic.",
        ),
    ),
    "bollinger": StrategyIdentity(
        strategy_id="bollinger",
        name="Bollinger Bands mean reversion",
        version="1.0.0",
        author="Built-in",
        description=(
            "Buys when the close falls below the lower Bollinger band and "
            "sells when it returns to the middle band."
        ),
        category=MEAN_REVERSION,
        beginner_explanation=(
            "The bands are a moving average with a corridor around it, sized "
            "by how much the price has been moving. The price spending time "
            "outside the corridor is unusual, so the strategy buys when it "
            "drops below the lower band and takes the profit when it comes "
            "back to the middle."
        ),
        known_weaknesses=(
            "In a trend the price rides the band instead of bouncing off it, "
            "and the strategy keeps buying into the move.",
            "The bands are built from volatility, so a volatility spike moves "
            "the corridor away from the price exactly when the signal fires.",
            "The exit at the middle band can be a very small profit that does "
            "not cover the fees of the round trip.",
        ),
        risk_warnings=(
            "A widening band looks like an opportunity and is often a warning: "
            "the position is largest when the market is least stable.",
            "There is no stop. A trend that keeps the price under the band "
            "leaves the position open through the whole decline.",
            "Small profits and occasional large losses need a high win rate to "
            "break even, and the win rate is the least stable number in a "
            "backtest.",
        ),
    ),
    "buy_and_hold": StrategyIdentity(
        strategy_id="buy_and_hold",
        name="Buy and hold",
        version="1.0.0",
        author="Built-in",
        description=(
            "Buys at the first opportunity and stays invested for the whole "
            "period. It is the benchmark a strategy has to beat."
        ),
        category=BENCHMARK,
        beginner_explanation=(
            "Do the simplest thing possible: buy once and never sell. It "
            "exists to answer one question honestly — did the strategy you "
            "are testing beat simply owning the asset, after costs?"
        ),
        known_weaknesses=(
            "It ignores every signal, so it takes the full drawdown of the "
            "asset.",
            "It assumes you can hold through any decline without selling, "
            "which is a statement about you, not about the market.",
        ),
        risk_warnings=(
            "It is not a safe default: an asset that falls 80% stays down "
            "until you sell.",
            "Beating it is the minimum bar, not a success. A strategy that "
            "loses to it added fees and complexity without adding "
            "information.",
        ),
    ),
    "null_strategy": StrategyIdentity(
        strategy_id="null_strategy",
        name="Null strategy",
        version="1.0.0",
        author="Built-in",
        description=(
            "Never trades. It measures what doing nothing does to the account "
            "over the same period."
        ),
        category=BASELINE,
        beginner_explanation=(
            "This strategy does nothing at all. Comparing against it answers a "
            "question people forget to ask: did the trading add anything, or "
            "would sitting still have produced the same result with less work?"
        ),
        known_weaknesses=(
            "It cannot make money, so it is only useful as a comparison.",
            "It says nothing about risk: a flat account looks calm because "
            "nothing happened, not because nothing could.",
        ),
        risk_warnings=(
            "A strategy that cannot beat this after costs is a fee generator.",
            "Its zero return is not a target to beat by a little; it is the "
            "line below which trading destroyed value.",
        ),
    ),
}


def identity_for(strategy_id: Optional[str]) -> Optional[StrategyIdentity]:
    """The identity of a built-in strategy, or ``None`` when it has none.

    A strategy imported from a file has no identity here — it carries its own
    metadata — so ``None`` is a normal answer, not an error.
    """
    if strategy_id is None:
        return None
    return IDENTITIES.get(str(strategy_id))


def render_identity(identity: StrategyIdentity) -> str:
    """The chapter 33.1 declarations as readable text."""
    lines = [
        f"{identity.name} ({identity.strategy_id}) — version {identity.version}",
        f"Author: {identity.author}",
        f"Category: {identity.category}",
        f"Description: {identity.description}",
        "Known weaknesses:",
    ]
    lines.extend(f"  - {item}" for item in identity.known_weaknesses)
    lines.append("Risk warnings:")
    lines.extend(f"  - {item}" for item in identity.risk_warnings)
    return "\n".join(lines)
