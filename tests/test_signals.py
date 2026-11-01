"""Tests for signal records (ROADMAP.md chapter 33.5).

The chapter fixes a vocabulary (enter/exit long, enter/exit short, hold, no
signal) and a record (timestamp, strategy id and version, market, timeframe,
type, indicator values, parameter set). These tests check the vocabulary is
actually produced, that hold and no signal are not the same nothing, and
that the engine records every decision with the context it had.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from crypto_trading_lab.backtesting.engine import (
    BacktestConfig,
    BuyAndHoldStrategy,
    MACrossoverStrategy,
    NullStrategy,
    run_backtest,
)
from crypto_trading_lab.domain.models import Candle, OrderSide, Symbol
from crypto_trading_lab.rule_strategy import Condition, RuleStrategy, RuleStrategySpec
from crypto_trading_lab.signals import (
    Signal,
    SignalType,
    signal_from_decision,
)

BASE = datetime(2024, 1, 1, tzinfo=timezone.utc)
HOUR = timedelta(hours=1)


def _candles(closes, interval="1h") -> list[Candle]:
    return [
        Candle(
            symbol=Symbol("BTC/USDT"),
            interval=interval,
            open_time=BASE + index * HOUR,
            close_time=BASE + (index + 1) * HOUR,
            open=Decimal(str(value)),
            high=Decimal(str(value)) + Decimal("1"),
            low=Decimal(str(value)) - Decimal("1"),
            close=Decimal(str(value)),
            volume=Decimal("10"),
        )
        for index, value in enumerate(closes)
    ]


def _candle(value: Decimal = Decimal("100")) -> Candle:
    return _candles([value])[0]


# -- the vocabulary ----------------------------------------------------------


def test_a_buy_while_flat_enters_long():
    signal = signal_from_decision(
        candle=_candle(),
        side=OrderSide.BUY,
        in_position=False,
        strategy_id="ma_crossover",
        strategy_version="1.0.0",
    )

    assert signal.type is SignalType.ENTER_LONG
    assert signal.actionable


def test_a_buy_while_already_long_is_a_decision_the_engine_cannot_use():
    """The engine is long-only spot: a second BUY does nothing, and says so."""
    signal = signal_from_decision(
        candle=_candle(),
        side=OrderSide.BUY,
        in_position=True,
        strategy_id="ma_crossover",
        strategy_version="1.0.0",
    )

    assert signal.type is SignalType.ENTER_LONG
    assert not signal.actionable


def test_a_sell_while_long_exits():
    signal = signal_from_decision(
        candle=_candle(),
        side=OrderSide.SELL,
        in_position=True,
        strategy_id="ma_crossover",
        strategy_version="1.0.0",
    )

    assert signal.type is SignalType.EXIT_LONG
    assert signal.actionable


def test_a_sell_while_flat_exits_nothing():
    signal = signal_from_decision(
        candle=_candle(),
        side=OrderSide.SELL,
        in_position=False,
        strategy_id="ma_crossover",
        strategy_version="1.0.0",
    )

    assert signal.type is SignalType.EXIT_LONG
    assert not signal.actionable


def test_hold_and_no_signal_are_different_nothings():
    """In the market and silent is not the same as out of the market."""
    holding = signal_from_decision(
        candle=_candle(),
        side=None,
        in_position=True,
        strategy_id="ma_crossover",
        strategy_version="1.0.0",
    )
    flat = signal_from_decision(
        candle=_candle(),
        side=None,
        in_position=False,
        strategy_id="ma_crossover",
        strategy_version="1.0.0",
    )

    assert holding.type is SignalType.HOLD
    assert flat.type is SignalType.NO_SIGNAL
    assert not holding.actionable and not flat.actionable


def test_the_short_side_exists_in_the_vocabulary():
    """The chapter lists it; the engine does not emit it yet (long-only)."""
    assert SignalType.ENTER_SHORT.value == "enter_short"
    assert SignalType.EXIT_SHORT.value == "exit_short"


# -- the record --------------------------------------------------------------


def test_the_record_carries_every_field_the_chapter_asks_for():
    signal = signal_from_decision(
        candle=_candles([Decimal("101")], interval="15m")[0],
        side=OrderSide.BUY,
        in_position=False,
        strategy_id="ma_crossover",
        strategy_version="2.1.0",
        parameters="ma_crossover@2.1.0(fast=5, slow=20)",
        indicators={"sma_fast": Decimal("100.5")},
    )

    assert signal.timestamp == BASE
    assert signal.strategy_id == "ma_crossover"
    assert signal.strategy_version == "2.1.0"
    assert signal.market == "BTC/USDT"
    assert signal.timeframe == "15m"
    assert signal.type is SignalType.ENTER_LONG
    assert signal.indicator_values["sma_fast"] == Decimal("100.5")
    assert signal.parameters == "ma_crossover@2.1.0(fast=5, slow=20)"


def test_a_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        Signal(
            timestamp=datetime(2024, 1, 1),
            strategy_id="x",
            strategy_version="1",
            market="BTC/USDT",
            timeframe="1h",
            type=SignalType.NO_SIGNAL,
        )


def test_the_indicator_values_cannot_be_edited_after_the_fact():
    signal = signal_from_decision(
        candle=_candle(),
        side=None,
        in_position=False,
        strategy_id="x",
        strategy_version="1",
        indicators={"rsi": Decimal("30")},
    )

    with pytest.raises(TypeError):
        signal.indicator_values["rsi"] = Decimal("99")


def test_the_record_serialises_to_json_friendly_values():
    signal = signal_from_decision(
        candle=_candle(),
        side=OrderSide.BUY,
        in_position=False,
        strategy_id="x",
        strategy_version="1",
        indicators={"rsi": Decimal("30.5")},
    )

    data = signal.to_dict()

    assert data["timestamp"].startswith("2024-01-01T00:00:00")
    assert data["type"] == "enter_long"
    assert data["indicator_values"] == {"rsi": "30.5"}


# -- what the engine records -------------------------------------------------


def test_the_engine_records_one_signal_per_candle():
    result = run_backtest(_candles([1, 2, 3, 4]), NullStrategy())

    assert len(result.signals) == result.candle_count
    assert all(s.type is SignalType.NO_SIGNAL for s in result.signals)


def test_buy_and_hold_enters_once_and_then_holds():
    result = run_backtest(_candles([1, 2, 3, 4]), BuyAndHoldStrategy())

    types = [s.type for s in result.signals]
    assert types[0] is SignalType.ENTER_LONG
    assert types[1:] == [SignalType.HOLD, SignalType.HOLD, SignalType.HOLD]


def test_the_signals_carry_the_strategy_and_its_parameters():
    config = BacktestConfig(
        strategy_id="ma_crossover",
        strategy_parameters="ma_crossover@1.0.0(fast=2, slow=3)",
    )
    result = run_backtest(
        _candles([1, 2, 3, 4, 5, 6]), MACrossoverStrategy(fast=2, slow=3), config
    )

    first = result.signals[0]
    assert first.strategy_id == "ma_crossover"
    assert first.strategy_version == "1.0.0"
    assert first.parameters == "ma_crossover@1.0.0(fast=2, slow=3)"


def test_the_signals_fall_back_to_the_strategy_name_when_the_caller_says_nothing():
    """Research, optimization and walk-forward runs set no id; the record
    still has to name what produced it."""
    result = run_backtest(
        _candles([1, 2, 3, 4, 5, 6]), MACrossoverStrategy(fast=2, slow=3)
    )

    assert result.signals[0].strategy_id == "ma_crossover"
    assert result.signals[0].strategy_version == "1.0.0"


def test_the_signals_carry_the_indicator_values_behind_the_decision():
    result = run_backtest(
        _candles([1, 2, 3, 4, 5, 6, 7, 8]),
        MACrossoverStrategy(fast=2, slow=3),
    )

    last = result.signals[-1]
    assert set(last.indicator_values) == {"sma_fast", "sma_slow"}


def test_a_rule_signal_names_the_operands_it_read():
    """A user-authored rule must be auditable from its signal record."""
    spec = RuleStrategySpec(
        name="cross",
        entry=(Condition("close", "crosses_above", "sma(2)"),),
        exit=(Condition("close", "<", "sma(2)"),),
    )
    result = run_backtest(
        _candles([1, 2, 3, 2, 1, 2, 3, 4]), RuleStrategy(spec)
    )

    recorded = result.signals[-1].indicator_values
    assert "close" in recorded
    assert "sma(2)" in recorded


def test_a_strategy_without_indicators_records_none_instead_of_inventing_them():
    result = run_backtest(_candles([1, 2, 3]), BuyAndHoldStrategy())

    assert result.signals[0].indicator_values == {}


def test_a_signal_is_a_decision_not_a_fill():
    """ENTER_LONG is recorded on candle 0; the position appears on candle 1."""
    result = run_backtest(_candles([1, 2, 3]), BuyAndHoldStrategy())

    assert result.signals[0].type is SignalType.ENTER_LONG
    assert result.exposure_curve == (False, True, True)
