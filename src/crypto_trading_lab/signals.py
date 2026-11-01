"""Signal records (ROADMAP.md chapter 33.5).

A strategy decides; a *signal* is that decision written down with the
context needed to audit it later. Chapter 33.5 fixes both halves: the
vocabulary (enter/exit long, enter/exit short, hold, no signal) and the
record (timestamp, strategy id and version, market, timeframe, type,
relevant indicator values, and the parameter set that produced it).

Two distinctions the record keeps on purpose:

* **Hold vs no signal.** Both mean "nothing to do", but not the same
  nothing: *hold* is a strategy that is already in the market and stays
  there, *no signal* is a strategy with no position and nothing to say.
  Collapsing them into ``None`` — what the engine used to do — loses the
  difference between "it is sitting in a trade" and "it is not in the
  market at all".
* **The decision vs what the engine could do with it.** The current engine
  is long-only spot, so a BUY while already long is a decision it cannot
  act on. ``actionable`` records that, instead of quietly dropping the
  signal or pretending it filled.

Short signals exist in the vocabulary because the chapter requires them;
the current engine never emits them, and it says so rather than pretending
otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from crypto_trading_lab.domain.models import Candle, OrderSide

__all__ = [
    "SignalType",
    "Signal",
    "signal_from_decision",
    "SIGNAL_DISCLAIMER",
]


class SignalType(str, Enum):
    """The explicit vocabulary of chapter 33.5."""

    ENTER_LONG = "enter_long"
    EXIT_LONG = "exit_long"
    ENTER_SHORT = "enter_short"
    EXIT_SHORT = "exit_short"
    HOLD = "hold"
    NO_SIGNAL = "no_signal"


SIGNAL_DISCLAIMER = (
    "A signal is a decision, not a fill and not a recommendation. Whether it "
    "became an order depends on the position, the risk manager and the "
    "execution model — and no signal is evidence of an edge."
)


@dataclass(frozen=True)
class Signal:
    """One decision, with the context chapter 33.5 requires."""

    timestamp: datetime
    strategy_id: str
    strategy_version: str
    market: str
    timeframe: str
    type: SignalType
    #: The indicator values the decision was taken on. Empty when the
    #: strategy reads none (buy-and-hold, the null strategy) — an honest
    #: empty, not a missing field.
    indicator_values: Mapping[str, Decimal] = field(default_factory=dict)
    #: The chapter 33.4 parameter set that produced the signal, as
    #: ``ma_crossover@1.0.0(fast=5, slow=20)``. Empty when the caller did not
    #: supply one.
    parameters: str = ""
    #: Whether the engine could act on the decision given the position at
    #: that moment. A BUY while already long is a decision it cannot use.
    actionable: bool = True

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("a signal timestamp must be timezone-aware (UTC)")
        if not isinstance(self.type, SignalType):
            raise ValueError(
                f"signal type must be a SignalType, got {self.type!r}"
            )
        frozen = {
            str(name): value for name, value in (self.indicator_values or {}).items()
        }
        object.__setattr__(self, "indicator_values", MappingProxyType(frozen))

    def __str__(self) -> str:
        return (
            f"{self.timestamp.isoformat()} {self.market} {self.timeframe} "
            f"{self.type.value} ({self.strategy_id}@{self.strategy_version})"
        )

    def to_dict(self) -> dict[str, Any]:
        """JSON-friendly form, for journals and reports."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "strategy_id": self.strategy_id,
            "strategy_version": self.strategy_version,
            "market": self.market,
            "timeframe": self.timeframe,
            "type": self.type.value,
            "indicator_values": {
                name: str(value) for name, value in self.indicator_values.items()
            },
            "parameters": self.parameters,
            "actionable": self.actionable,
        }


def signal_from_decision(
    *,
    candle: Candle,
    side: Optional[OrderSide],
    in_position: bool,
    strategy_id: str,
    strategy_version: str,
    parameters: str = "",
    indicators: Optional[Mapping[str, Decimal]] = None,
) -> Signal:
    """Turn one engine decision into a chapter 33.5 record.

    ``side`` is what the strategy returned (BUY, SELL or ``None``);
    ``in_position`` is the position *at that candle*, which is what makes
    hold distinguishable from no signal.
    """
    if side is None:
        kind = SignalType.HOLD if in_position else SignalType.NO_SIGNAL
        actionable = False
    elif side is OrderSide.BUY:
        kind = SignalType.ENTER_LONG
        actionable = not in_position
    elif side is OrderSide.SELL:
        kind = SignalType.EXIT_LONG
        actionable = in_position
    else:  # pragma: no cover - OrderSide has two members
        raise ValueError(f"unknown order side {side!r}")

    return Signal(
        timestamp=candle.open_time.astimezone(timezone.utc),
        strategy_id=strategy_id or "unknown",
        strategy_version=strategy_version or "unknown",
        market=str(candle.symbol),
        timeframe=candle.interval,
        type=kind,
        indicator_values=dict(indicators or {}),
        parameters=parameters,
        actionable=actionable,
    )
