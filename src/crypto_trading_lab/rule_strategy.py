"""Executable rule strategies (ROADMAP.md chapters 33, 34 and 77).

Turns the visual builder's declarative conditions into a real strategy
the backtesting engine can run — **without** ``eval``, ``exec`` or
generated code. A rule is data: operands (price fields or indicators),
comparison operators, and optional stop-loss/take-profit fractions.

Documented limitation (honest by design): the engine fills at the next
candle's open, so stop-loss and take-profit are evaluated on candle
*closes*, not on intrabar extremes. That is conservative about
look-ahead but can differ from a real stop order.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Sequence

from crypto_trading_lab.domain.models import Candle, OrderSide
from crypto_trading_lab.indicators.library import (
    ATR,
    ATRStream,
    EMA,
    EMAStream,
    ROC,
    ROCStream,
    RSI,
    RSIStream,
    SMA,
    SMAStream,
)

__all__ = [
    "RuleError",
    "Condition",
    "RuleStrategySpec",
    "RuleStrategy",
    "OPERATORS",
    "SUPPORTED_INDICATORS",
    "operand_indicator",
    "spec_from_blocks",
]

#: Comparison operators the rule language understands.
OPERATORS: tuple[str, ...] = (
    ">",
    "<",
    ">=",
    "<=",
    "crosses_above",
    "crosses_below",
)

SUPPORTED_INDICATORS = ("sma", "ema", "rsi", "atr", "roc")

_PRICE_FIELDS = ("open", "high", "low", "close")
_INDICATOR_RE = re.compile(r"^(sma|ema|rsi|atr|roc)\(\s*(\d+)\s*\)$")
_NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?$")


class RuleError(ValueError):
    """A rule is malformed and cannot be executed."""


def _indicator(name: str, period: int):
    if period < 1:
        raise RuleError(f"{name} period must be at least 1")
    return {
        "sma": SMA,
        "ema": EMA,
        "rsi": RSI,
        "atr": ATR,
        "roc": ROC,
    }[name](period)


def _stream(name: str, period: int):
    """The incremental form of an indicator, so a run stays O(N).

    ``_indicator`` recomputes the whole series; calling it once per candle
    would make a rule backtest quadratic. These keep the same state the batch
    formulas use and are compared against them in
    ``tests/indicators/test_streams.py``.
    """
    return {
        "sma": SMAStream,
        "ema": EMAStream,
        "rsi": RSIStream,
        "atr": ATRStream,
        "roc": ROCStream,
    }[name](period)


@dataclass(frozen=True)
class Condition:
    """One comparison between two operands.

    Operand syntax: a price field (``close``), an indicator
    (``sma(20)``), or a numeric constant (``50``).
    """

    left: str
    operator: str
    right: str

    def __post_init__(self) -> None:
        if self.operator not in OPERATORS:
            raise RuleError(
                f"unsupported operator {self.operator!r}; "
                f"use one of {', '.join(OPERATORS)}"
            )
        validate_operand(self.left)
        validate_operand(self.right)

    def to_dict(self) -> dict[str, str]:
        return {"left": self.left, "operator": self.operator, "right": self.right}

    @classmethod
    def from_dict(cls, data: dict) -> "Condition":
        return cls(str(data["left"]), str(data["operator"]), str(data["right"]))


def validate_operand(operand: str) -> str:
    """Return the canonical operand or raise :class:`RuleError`."""
    text = operand.strip().lower()
    if text in _PRICE_FIELDS:
        return text
    if _NUMBER_RE.match(text):
        return text
    match = _INDICATOR_RE.match(text)
    if match:
        _indicator(match.group(1), int(match.group(2)))
        return f"{match.group(1)}({int(match.group(2))})"
    raise RuleError(
        f"unsupported operand {operand!r}; use a price field "
        f"({', '.join(_PRICE_FIELDS)}), an indicator such as sma(20), "
        "or a number"
    )


def operand_indicator(operand: str) -> tuple[str, int] | None:
    """The indicator an operand names, or ``None`` for a field or a number.

    ``"sma(20)"`` → ``("sma", 20)``; ``"close"`` and ``"50"`` → ``None``.
    Chapter 35 counts indicators, so the grammar that defines them lives
    here, next to the parser, instead of being re-derived elsewhere.
    """
    match = _INDICATOR_RE.match(validate_operand(operand))
    if match is None:
        return None
    return match.group(1), int(match.group(2))


@dataclass(frozen=True)
class RuleStrategySpec:
    """A complete, serialisable, executable rule (versioned schema)."""

    name: str
    entry: tuple[Condition, ...]
    exit: tuple[Condition, ...] = ()
    entry_mode: str = "all"   # "all" (AND) or "any" (OR)
    exit_mode: str = "all"
    stop_loss_fraction: Decimal | None = None
    take_profit_fraction: Decimal | None = None
    version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise RuleError("a rule needs a name")
        if not self.entry:
            raise RuleError("a rule needs at least one entry condition")
        for mode in (self.entry_mode, self.exit_mode):
            if mode not in ("all", "any"):
                raise RuleError("mode must be 'all' or 'any'")
        for fraction in (self.stop_loss_fraction, self.take_profit_fraction):
            if fraction is not None and not (Decimal(0) < fraction < Decimal(1)):
                raise RuleError(
                    "stop-loss and take-profit fractions must be between 0 and 1"
                )

    def to_dict(self) -> dict:
        return {
            "schema": "crypto-trading-lab.rule/1",
            "name": self.name,
            "version": self.version,
            "entry_mode": self.entry_mode,
            "exit_mode": self.exit_mode,
            "entry": [c.to_dict() for c in self.entry],
            "exit": [c.to_dict() for c in self.exit],
            "stop_loss_fraction": (
                str(self.stop_loss_fraction)
                if self.stop_loss_fraction is not None
                else None
            ),
            "take_profit_fraction": (
                str(self.take_profit_fraction)
                if self.take_profit_fraction is not None
                else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RuleStrategySpec":
        try:
            def optional(key: str) -> Decimal | None:
                value = data.get(key)
                return Decimal(str(value)) if value is not None else None

            return cls(
                name=str(data["name"]),
                entry=tuple(Condition.from_dict(c) for c in data.get("entry", [])),
                exit=tuple(Condition.from_dict(c) for c in data.get("exit", [])),
                entry_mode=str(data.get("entry_mode", "all")),
                exit_mode=str(data.get("exit_mode", "all")),
                stop_loss_fraction=optional("stop_loss_fraction"),
                take_profit_fraction=optional("take_profit_fraction"),
                version=str(data.get("version", "1.0")),
            )
        except (KeyError, TypeError, InvalidOperation) as error:
            raise RuleError(f"invalid rule document: {error}") from error

    def describe(self) -> str:
        """Plain-language explanation of the rule."""
        def phrase(conditions, mode: str) -> str:
            joiner = " AND " if mode == "all" else " OR "
            return joiner.join(
                f"{c.left} {c.operator.replace('_', ' ')} {c.right}"
                for c in conditions
            )

        parts = [f"Enter when {phrase(self.entry, self.entry_mode)}."]
        if self.exit:
            parts.append(f"Exit when {phrase(self.exit, self.exit_mode)}.")
        if self.stop_loss_fraction is not None:
            parts.append(
                f"Stop loss at {self.stop_loss_fraction:.1%} against the entry."
            )
        if self.take_profit_fraction is not None:
            parts.append(
                f"Take profit at {self.take_profit_fraction:.1%} in favour."
            )
        return " ".join(parts)


class RuleStrategy:
    """Executes a :class:`RuleStrategySpec` candle by candle (chapter 33)."""

    def __init__(self, spec: RuleStrategySpec) -> None:
        self.spec = spec
        self.version = spec.version
        # One growing list per operand and one stream per indicator, so a run
        # of N candles costs O(N) instead of recomputing each series on every
        # candle (the engine hands over a growing view of the past, so a
        # length-keyed cache would be invalidated every step).
        self._cache: dict[str, list] = {}
        self._streams: dict[str, object] = {}
        self._entry_price: Decimal | None = None
        self._in_market = False

    @property
    def name(self) -> str:
        return self.spec.name

    # -- operand evaluation ----------------------------------------------

    def _series(self, operand: str, candles: Sequence[Candle]):
        key = validate_operand(operand)
        if _NUMBER_RE.match(key):
            return Decimal(key)
        series = self._cache.get(key)
        if series is None:
            series = []
            self._cache[key] = series
        if key in _PRICE_FIELDS:
            self._extend(series, candles, lambda candle: getattr(candle, key))
            return series
        match = _INDICATOR_RE.match(key)
        assert match is not None
        stream = self._streams.get(key)
        if stream is None:
            stream = _stream(match.group(1), int(match.group(2)))
            self._streams[key] = stream
        self._extend(series, candles, stream.update)
        return series

    @staticmethod
    def _extend(series: list, candles: Sequence[Candle], produce) -> None:
        """Feed the candles the strategy has not seen yet into the series."""
        while len(series) < len(candles):
            series.append(produce(candles[len(series)]))

    def _value(self, operand: str, index: int, candles: Sequence[Candle]):
        series = self._series(operand, candles)
        if isinstance(series, Decimal):
            return series
        if index < 0 or index >= len(series):
            return None
        return series[index]

    def _compare(self, condition: Condition, index: int, candles) -> bool:
        left = self._value(condition.left, index, candles)
        right = self._value(condition.right, index, candles)
        if left is None or right is None:
            return False
        if condition.operator == ">":
            return left > right
        if condition.operator == "<":
            return left < right
        if condition.operator == ">=":
            return left >= right
        if condition.operator == "<=":
            return left <= right
        previous_left = self._value(condition.left, index - 1, candles)
        previous_right = self._value(condition.right, index - 1, candles)
        if previous_left is None or previous_right is None:
            return False
        if condition.operator == "crosses_above":
            return previous_left <= previous_right and left > right
        return previous_left >= previous_right and left < right

    def _matches(self, conditions, mode: str, index: int, candles) -> bool:
        results = [self._compare(c, index, candles) for c in conditions]
        if not results:
            return False
        return all(results) if mode == "all" else any(results)

    # -- strategy protocol ------------------------------------------------

    def on_candle(self, index: int, candles: Sequence[Candle]) -> OrderSide | None:
        if index == 0:
            return None
        close = candles[index].close

        if self._in_market and self._entry_price is not None:
            stop = self.spec.stop_loss_fraction
            target = self.spec.take_profit_fraction
            if stop is not None and close <= self._entry_price * (Decimal(1) - stop):
                self._in_market = False
                return OrderSide.SELL
            if target is not None and close >= self._entry_price * (
                Decimal(1) + target
            ):
                self._in_market = False
                return OrderSide.SELL
            if self.spec.exit and self._matches(
                self.spec.exit, self.spec.exit_mode, index, candles
            ):
                self._in_market = False
                return OrderSide.SELL
            return None

        if self._matches(self.spec.entry, self.spec.entry_mode, index, candles):
            self._in_market = True
            self._entry_price = close
            return OrderSide.BUY
        return None

    def indicator_values(self, index: int, candles: Sequence[Candle]) -> dict:
        """Every operand the rule reads, at this candle (chapter 33.5).

        A rule is data, so the signal record can name exactly what the
        decision looked at: ``{"close": 100, "sma(20)": 99.4}``.
        """
        values: dict[str, object] = {}
        for condition in tuple(self.spec.entry) + tuple(self.spec.exit):
            for operand in (condition.left, condition.right):
                key = validate_operand(operand)
                if operand_indicator(key) is None and key not in _PRICE_FIELDS:
                    continue  # a numeric constant is not an indicator
                values[key] = self._value(key, index, candles)
        return values


#: Builder operator → rule-language operator.
_BUILDER_OPERATORS = {
    "greater": ">",
    "less": "<",
    "crossover": "crosses_above",
    "crossunder": "crosses_below",
}


def spec_from_blocks(
    name: str,
    blocks,
    version: str = "1.0",
) -> RuleStrategySpec:
    """Convert visual-builder blocks into an executable rule.

    The block list is flat, so operands are read left to right and every
    operator consumes the two most recent operands (a small stack
    machine). Conditions are assigned to entry or exit by the entry/exit
    blocks, exactly as the builder expects. Arithmetic operators and
    filters are rejected with a clear reason rather than guessed.
    """
    operands: list[str] = []
    pending: list[Condition] = []
    entry: list[Condition] = []
    exit_conditions: list[Condition] = []
    pending_mode = "all"
    entry_mode = "all"
    exit_mode = "all"
    stop: Decimal | None = None
    target: Decimal | None = None

    for block in blocks:
        kind = block.type
        params = getattr(block, "params", {}) or {}
        if kind == "indicator":
            indicator_type = str(params.get("indicator_type", "")).lower()
            # The builder stores parameters flat (``period``) while the
            # UI passes them nested (``params={"period": n}``); accept both.
            period = params.get("period")
            if period is None:
                period = (params.get("params") or {}).get("period")
            if period is None:
                raise RuleError("an indicator block needs a period")
            operands.append(validate_operand(f"{indicator_type}({int(period)})"))
        elif kind == "value":
            operands.append(validate_operand(str(params.get("value"))))
        elif kind == "operator":
            mapped = _BUILDER_OPERATORS.get(str(params.get("op")))
            if mapped is None:
                raise RuleError(
                    f"operator {params.get('op')!r} is not executable yet; "
                    "use greater, less, crossover or crossunder"
                )
            if len(operands) < 2:
                raise RuleError("an operator needs two operands before it")
            right = operands.pop()
            left = operands.pop()
            pending.append(Condition(left, mapped, right))
        elif kind == "condition":
            condition = str(params.get("condition", "and"))
            if condition == "and":
                pending_mode = "all"
            elif condition == "or":
                pending_mode = "any"
            else:
                raise RuleError("'not' conditions are not executable yet")
        elif kind == "entry":
            entry.extend(pending)
            entry_mode = pending_mode
            pending.clear()
        elif kind == "exit":
            exit_conditions.extend(pending)
            exit_mode = pending_mode
            pending.clear()
        elif kind == "stop_loss":
            stop = Decimal(str(params.get("value")))
        elif kind == "take_profit":
            target = Decimal(str(params.get("value")))
        elif kind == "filter":
            raise RuleError(
                "time/volatility filters are not executable yet; remove "
                "the filter block to run the rule"
            )
        else:
            raise RuleError(f"unsupported block type {kind!r}")

    if pending:
        if not entry:
            entry.extend(pending)
            entry_mode = pending_mode
        else:
            exit_conditions.extend(pending)
            exit_mode = pending_mode

    return RuleStrategySpec(
        name=name,
        entry=tuple(entry),
        exit=tuple(exit_conditions),
        entry_mode=entry_mode,
        exit_mode=exit_mode,
        stop_loss_fraction=stop,
        take_profit_fraction=target,
        version=version,
    )
