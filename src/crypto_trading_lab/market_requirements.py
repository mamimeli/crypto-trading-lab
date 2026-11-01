"""Market requirements: what a strategy needs before it may run (33.2).

ROADMAP chapter 33.2 asks each strategy to state, up front, the markets and
the data it can work with. That list used to be implicit — a strategy read
``candle.volume`` and hoped the feed had it, or it assumed spot and silently
blew up on a contract it was never designed for. Implicit assumptions are how
a backtest reports a number for data the strategy could not actually have
used.

This module is the one place a built-in strategy declares its requirements.
The registry does not need them — the engine already refuses to run a
strategy on data it cannot use — but stating them makes the refusal
*explainable*: when a run is rejected, the message can say "this strategy
only runs on spot markets" instead of "something was wrong with the market".

The seven declarations, in the chapter's order:

1. compatible markets  → :attr:`MarketRequirements.compatible_markets`
2. supported asset
   types               → :attr:`MarketRequirements.asset_types`
3. required timeframe  → :attr:`MarketRequirements.required_timeframe`
4. required market-data
   fields              → :attr:`MarketRequirements.required_fields`
5. required indicators → :attr:`MarketRequirements.required_indicators`
6. warm-up period      → the strategy's ``warmup_candles`` attribute
                          (chapter 33.7 checks it; it lives on the strategy,
                          not here, so it cannot drift from the code)
7. minimum historical
   data required       → :attr:`MarketRequirements.min_data_required`
                          (the default-configuration figure; the runtime
                          gate is the strategy's ``warmup_candles``)

Two declarations are deliberately *excluded* from this record to avoid
duplication and the drift that follows:

* The warm-up period is the strategy's own ``warmup_candles`` attribute. It
  is derived from the indicator periods, so copying it here would invite a
  number that disagrees with the code. Chapter 33.7 validates the attribute
  directly.
* The asset type the engine actually supports is a fact of the program, not
  of any strategy. :data:`ENGINE_TRADING_MODE` records it once; a strategy
  whose ``asset_types`` omits it cannot run, and the validation says so.

Closed sets everywhere. A free-text asset type or field name cannot be
checked against the engine's capabilities, so an unknown one is rejected at
construction rather than stored and silently ignored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

__all__ = [
    "ENGINE_TRADING_MODE",
    "ASSET_TYPES",
    "SUPPORTED_FIELDS",
    "ANY_MARKET",
    "TIMEFRAME_RE",
    "MarketRequirements",
    "REQUIREMENTS",
    "market_requirements_for",
    "render_market_requirements",
]

#: The interval grammar the project uses: ``1m``, ``15m``, ``4h``, ``1d``,
#: ``1w``. Seconds are accepted because exchanges publish ``30s`` feeds.
#: Defined here so ``strategy_validation`` and this module can both use it
#: without importing each other.
TIMEFRAME_RE = re.compile(r"^(\d+)([smhdw])$")

#: The asset type the engine can trade today. The whole program is a
#: long-only spot laboratory (chapter 1); futures, perpetuals and options
#: are out of scope for the MVP. A strategy that does not list this here
#: cannot run, and the validation says so instead of discovering it mid-run.
ENGINE_TRADING_MODE = "spot"

#: The closed set of asset types a strategy may claim to support. Anything
#: outside this list is rejected, because the engine cannot verify a claim it
#: does not understand.
ASSET_TYPES: Tuple[str, ...] = ("spot", "perpetual", "futures", "options")

#: The market-data fields the engine can supply. A strategy may only require
#: what the engine can actually deliver; requiring ``funding_rate`` when no
#: feed provides it is a declaration error, not a runtime surprise.
SUPPORTED_FIELDS: Tuple[str, ...] = ("open", "high", "low", "close", "volume")

#: The marker in :attr:`compatible_markets` that means "any market of a
#: supported asset type". Built-in strategies are asset-class agnostic — they
#: work on any spot ``BASE/QUOTE`` pair — so they use this instead of
#: enumerating symbols.
ANY_MARKET = "any"


@dataclass(frozen=True)
class MarketRequirements:
    """What a strategy needs from a market and its data (33.2)."""

    strategy_id: str
    asset_types: Tuple[str, ...] = ("spot",)
    compatible_markets: Tuple[str, ...] = (ANY_MARKET,)
    required_timeframe: Optional[str] = None
    required_fields: Tuple[str, ...] = ()
    required_indicators: Tuple[str, ...] = ()
    #: The minimum sample for the *default* configuration. A parametrised
    #: strategy's true minimum is its ``warmup_candles``, which rises with
    #: its parameters, so this figure documents the default rather than
    #: acting as a second gate (chapter 33.7's warm-up check owns that).
    min_data_required: int = 0

    def __post_init__(self) -> None:
        if not self.asset_types:
            raise ValueError(f"{self.strategy_id}: declare at least one asset type")
        for asset_type in self.asset_types:
            if asset_type not in ASSET_TYPES:
                raise ValueError(
                    f"{self.strategy_id}: unknown asset type {asset_type!r}; "
                    f"use one of {', '.join(ASSET_TYPES)}"
                )
        if not self.compatible_markets:
            raise ValueError(
                f"{self.strategy_id}: declare at least one compatible market "
                f"(or {ANY_MARKET!r} for any)"
            )
        if self.required_timeframe is not None and not TIMEFRAME_RE.match(
            str(self.required_timeframe)
        ):
            raise ValueError(
                f"{self.strategy_id}: required_timeframe "
                f"{self.required_timeframe!r} is not a valid interval "
                "(use a count and one of s, m, h, d, w)"
            )
        for field in self.required_fields:
            if field not in SUPPORTED_FIELDS:
                raise ValueError(
                    f"{self.strategy_id}: required field {field!r} is not "
                    f"supplied by the engine; choose from "
                    f"{', '.join(SUPPORTED_FIELDS)}"
                )
        for indicator in self.required_indicators:
            if not str(indicator).strip():
                raise ValueError(
                    f"{self.strategy_id}: required indicator names must not "
                    "be empty"
                )
        if self.min_data_required < 0:
            raise ValueError(
                f"{self.strategy_id}: min_data_required must be non-negative, "
                f"got {self.min_data_required!r}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-safe view, for reports and the registry export."""
        return {
            "strategy_id": self.strategy_id,
            "asset_types": list(self.asset_types),
            "compatible_markets": list(self.compatible_markets),
            "required_timeframe": self.required_timeframe,
            "required_fields": list(self.required_fields),
            "required_indicators": list(self.required_indicators),
            "min_data_required": self.min_data_required,
        }


REQUIREMENTS: Mapping[str, MarketRequirements] = {
    "ma_crossover": MarketRequirements(
        strategy_id="ma_crossover",
        asset_types=("spot",),
        compatible_markets=(ANY_MARKET,),
        required_timeframe=None,
        # The decision reads the close; the engine fills at the next open,
        # so the feed must carry both.
        required_fields=("open", "close"),
        required_indicators=("sma_fast", "sma_slow"),
        # Default configuration (slow=30) needs 31 candles before its first
        # signal; that is the floor a run must clear.
        min_data_required=31,
    ),
    "rsi": MarketRequirements(
        strategy_id="rsi",
        asset_types=("spot",),
        compatible_markets=(ANY_MARKET,),
        required_timeframe=None,
        # The optional volume filter reads candle volume, so the feed must
        # carry it even when the filter is switched off by default.
        required_fields=("close", "volume"),
        required_indicators=("rsi",),
        # Default configuration (period=14) needs 15 candles.
        min_data_required=15,
    ),
    "breakout": MarketRequirements(
        strategy_id="breakout",
        asset_types=("spot",),
        compatible_markets=(ANY_MARKET,),
        required_timeframe=None,
        # The window is built from the highs and lows; the close breaks it.
        required_fields=("close", "high", "low"),
        required_indicators=("rolling_high", "rolling_low"),
        # Default configuration (period=20) needs 21 candles.
        min_data_required=21,
    ),
    "bollinger": MarketRequirements(
        strategy_id="bollinger",
        asset_types=("spot",),
        compatible_markets=(ANY_MARKET,),
        required_timeframe=None,
        required_fields=("close",),
        required_indicators=("middle", "upper", "lower"),
        # Default configuration (period=20) needs 20 candles.
        min_data_required=20,
    ),
    "buy_and_hold": MarketRequirements(
        strategy_id="buy_and_hold",
        asset_types=("spot",),
        compatible_markets=(ANY_MARKET,),
        required_timeframe=None,
        required_fields=("close",),
        required_indicators=(),
        # It buys at the open after the first candle, so it needs at least
        # two to do anything.
        min_data_required=2,
    ),
    "null_strategy": MarketRequirements(
        strategy_id="null_strategy",
        asset_types=("spot",),
        compatible_markets=(ANY_MARKET,),
        required_timeframe=None,
        required_fields=(),
        required_indicators=(),
        # It never trades, so any amount of data is enough.
        min_data_required=0,
    ),
}


def market_requirements_for(
    strategy_id: Optional[str],
) -> Optional[MarketRequirements]:
    """The market requirements of a built-in strategy, or ``None``.

    A strategy imported from a file has no entry here — it carries its own
    metadata — so ``None`` is a normal answer, not an error. A custom
    strategy that wants these checks simply has not declared them yet.
    """
    if strategy_id is None:
        return None
    return REQUIREMENTS.get(str(strategy_id))


def render_market_requirements(requirements: MarketRequirements) -> str:
    """The chapter 33.2 declarations as readable text."""
    markets = (
        "any market"
        if ANY_MARKET in requirements.compatible_markets
        else ", ".join(requirements.compatible_markets)
    )
    timeframe = (
        requirements.required_timeframe
        if requirements.required_timeframe is not None
        else "any interval"
    )
    fields = (
        ", ".join(requirements.required_fields)
        if requirements.required_fields
        else "none beyond OHLCV"
    )
    indicators = (
        ", ".join(requirements.required_indicators)
        if requirements.required_indicators
        else "none"
    )
    lines = [
        f"Compatible markets: {markets}",
        f"Supported asset types: {', '.join(requirements.asset_types)}",
        f"Required timeframe: {timeframe}",
        f"Required market-data fields: {fields}",
        f"Required indicators: {indicators}",
        f"Minimum historical data (default configuration): "
        f"{requirements.min_data_required} candles",
    ]
    return "\n".join(lines)
