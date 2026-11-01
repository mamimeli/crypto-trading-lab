"""Trading rules: what each strategy is allowed to do (33.3).

ROADMAP chapter 33.3 asks each strategy to state its trading rules: entry,
exit, invalidation, stop-loss, take-profit, trailing stop, cooldown, time
restrictions and position sizing. The engine already *implements* most of
these — it is long-only spot, fills at the next candle's open, holds one
position at a time, uses no leverage, and gates every order (entries and
exits) through the risk manager (chapter 33.6 / 58). What was missing was a
single place that *says so*, next to the strategy, instead of leaving the
reader to infer the contract from the code or from the beginner guide.

This module is that place. The registry does not need it; the guide
(chapter 33.9) explains the rules in plain words and the rule engine
(chapter 33.4 / rule_strategy) checks the structured ones at construction.
But a strategy that never states its rules can drift from what the engine
will actually do, and the reader deserves the formal contract in one
block.

Nine declarations, in the chapter's order:

1. entry conditions      → :attr:`TradingRules.entry_rule`
2. exit conditions       → :attr:`TradingRules.exit_rule`
3. invalidation          → :attr:`TradingRules.invalidation`
4. stop-loss rules       → :attr:`TradingRules.stop_loss`
5. take-profit rules     → :attr:`TradingRules.take_profit`
6. trailing-stop rules   → :attr:`TradingRules.trailing_stop`
7. cooldown rules        → :attr:`TradingRules.cooldown`
8. time restrictions     → :attr:`TradingRules.time_restrictions`
9. position sizing       → :attr:`TradingRules.position_sizing`

The built-in strategies are deliberately plain: long-only spot with no
stops, so the stop-loss, take-profit and trailing-stop fields read "none"
and the position-sizing field states the engine's rule. A rule built in the
Strategy Builder supplies its entry, exit and optional stop/take-profit
through :class:`~crypto_trading_lab.rule_strategy.RuleStrategySpec`, which
validates the fractions at construction; this record documents that path
for the reader in the same block.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

__all__ = [
    "TradingRules",
    "RULES",
    "trading_rules_for",
    "render_trading_rules",
]

#: The engine's position-sizing rule, shared by every built-in. It is stated
#: here once so the record can reference it without paraphrasing it six times
#: (six paraphrases would be six chances to disagree about what the engine
#: actually does).
POSITION_SIZING = (
    "A fixed fraction of the available cash (position_fraction; 1.0 by default "
    "means all of it), sized at the next candle's open. One position at a time, "
    "no pyramiding, no leverage: the engine is long-only spot. Sizing is subject "
    "to the risk manager (chapter 33.6 / 58): a fresh RiskManager is built per "
    "run and every order, including exits, is evaluated; a refusal means no "
    "order that candle."
)


@dataclass(frozen=True)
class TradingRules:
    """The formal trading contract of a strategy (33.3)."""

    strategy_id: str
    entry_rule: str
    exit_rule: str
    invalidation: str
    stop_loss: str
    take_profit: str
    trailing_stop: str
    cooldown: str
    time_restrictions: str
    position_sizing: str = POSITION_SIZING

    def __post_init__(self) -> None:
        # Entry and exit are the two a strategy cannot omit: without an entry
        # it never trades, without an exit it never stops. "none" is a valid
        # answer for the others (a strategy may legitimately have no stop),
        # but the field must still say so rather than being blank.
        for field in (
            "entry_rule",
            "exit_rule",
            "invalidation",
            "stop_loss",
            "take_profit",
            "trailing_stop",
            "cooldown",
            "time_restrictions",
            "position_sizing",
        ):
            if not getattr(self, field).strip():
                raise ValueError(
                    f"{self.strategy_id}: trading rule {field} must not be empty"
                )

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-safe view, for reports and the registry export."""
        return {
            "strategy_id": self.strategy_id,
            "entry_rule": self.entry_rule,
            "exit_rule": self.exit_rule,
            "invalidation": self.invalidation,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "trailing_stop": self.trailing_stop,
            "cooldown": self.cooldown,
            "time_restrictions": self.time_restrictions,
            "position_sizing": self.position_sizing,
        }


RULES: Mapping[str, TradingRules] = {
    "ma_crossover": TradingRules(
        strategy_id="ma_crossover",
        entry_rule="The fast SMA crosses above the slow SMA (a golden cross).",
        exit_rule="The fast SMA crosses back below the slow SMA (a death cross).",
        invalidation="None — the position is held until the exit signal.",
        stop_loss="None — the engine never adds a stop of its own.",
        take_profit="None — the exit is the strategy's own sell signal.",
        trailing_stop="None.",
        cooldown="None.",
        time_restrictions="None.",
    ),
    "rsi": TradingRules(
        strategy_id="rsi",
        entry_rule=(
            "RSI crosses down through the oversold level (with the optional "
            "volume and trend filters, if configured)."
        ),
        exit_rule=(
            "RSI crosses up through the overbought level; the cooldown is then "
            "armed so a fresh entry cannot fire immediately."
        ),
        invalidation="None — held until the overbought exit.",
        stop_loss="None — the engine never adds a stop of its own.",
        take_profit="None — the exit is the overbought signal.",
        trailing_stop="None.",
        cooldown=(
            "Optional: N candles after an exit during which new entries are "
            "blocked (the cooldown parameter; 0 disables it)."
        ),
        time_restrictions="None.",
    ),
    "breakout": TradingRules(
        strategy_id="breakout",
        entry_rule="The close breaks above the highest high of the recent window.",
        exit_rule="The close breaks below the lowest low of the recent window.",
        invalidation="None — held until the opposite breakout.",
        stop_loss="None — the engine never adds a stop of its own.",
        take_profit="None — the exit is the breakdown signal.",
        trailing_stop="None.",
        cooldown="None.",
        time_restrictions="None.",
    ),
    "bollinger": TradingRules(
        strategy_id="bollinger",
        entry_rule="The close crosses down through the lower Bollinger band.",
        exit_rule="The close crosses back up to the middle band.",
        invalidation="None — held until the middle-band exit.",
        stop_loss="None — the engine never adds a stop of its own.",
        take_profit="None — the exit is the middle-band signal.",
        trailing_stop="None.",
        cooldown="None.",
        time_restrictions="None.",
    ),
    "buy_and_hold": TradingRules(
        strategy_id="buy_and_hold",
        entry_rule="The first candle it can fill: the signal at candle 0 fills at candle 1's open.",
        exit_rule="Never, by itself — it is the benchmark to beat, not a strategy to trade.",
        invalidation="Not applicable — it never exits on its own.",
        stop_loss="None — it is a buy-and-hold benchmark.",
        take_profit="None.",
        trailing_stop="None.",
        cooldown="None.",
        time_restrictions="None.",
    ),
    "null_strategy": TradingRules(
        strategy_id="null_strategy",
        entry_rule="Never — it does not trade.",
        exit_rule="Never — it does not trade.",
        invalidation="Not applicable.",
        stop_loss="None.",
        take_profit="None.",
        trailing_stop="None.",
        cooldown="None.",
        time_restrictions="None.",
    ),
}


def trading_rules_for(strategy_id: Optional[str]) -> Optional[TradingRules]:
    """The trading rules of a built-in strategy, or ``None``.

    A strategy imported from a file carries its own configuration; a rule
    built in the Strategy Builder expresses its rules through
    :class:`~crypto_trading_lab.rule_strategy.RuleStrategySpec`. So ``None``
    here is a normal answer for anything that is not a built-in, and the
    caller falls back to the rule spec or to "no declared rules".
    """
    if strategy_id is None:
        return None
    return RULES.get(str(strategy_id))


def render_trading_rules(rules: TradingRules) -> str:
    """The chapter 33.3 contract as readable text."""
    lines = [
        f"Entry: {rules.entry_rule}",
        f"Exit: {rules.exit_rule}",
        f"Invalidation: {rules.invalidation}",
        f"Stop-loss: {rules.stop_loss}",
        f"Take-profit: {rules.take_profit}",
        f"Trailing stop: {rules.trailing_stop}",
        f"Cooldown: {rules.cooldown}",
        f"Time restrictions: {rules.time_restrictions}",
        f"Position sizing: {rules.position_sizing}",
    ]
    return "\n".join(lines)
