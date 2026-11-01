"""Streaming indicators must equal their batch formulas, value by value.

``SMAStream``, ``EMAStream``, ``RSIStream``, ``ATRStream`` and ``ROCStream``
exist because calling ``X.compute(candles)`` once per candle inside a backtest
costs O(N^2). A stream that drifts from the documented formula would silently
change every backtest that uses it, so each one is compared here against its
batch counterpart over the same candles, including the warm-up ``None``s.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from crypto_trading_lab.domain.models import Candle, Symbol
from crypto_trading_lab.indicators.library import (
    ATR,
    EMA,
    ROC,
    RSI,
    SMA,
    ATRStream,
    EMAStream,
    ROCStream,
    RSIStream,
    SMAStream,
)

BASE = datetime(2024, 1, 1, tzinfo=timezone.utc)
HOUR = timedelta(hours=1)


def _candles(closes) -> list[Candle]:
    """A series with a non-trivial high/low so ATR has something to measure."""
    return [
        Candle(
            symbol=Symbol("BTC/USDT"),
            interval="1h",
            open_time=BASE + index * HOUR,
            close_time=BASE + (index + 1) * HOUR,
            open=Decimal(str(value)),
            high=Decimal(str(value)) + Decimal("1.5"),
            low=Decimal(str(value)) - Decimal("0.5"),
            close=Decimal(str(value)),
            volume=Decimal("10"),
        )
        for index, value in enumerate(closes)
    ]


#: A wave with both directions, so RSI is neither 0 nor 100 throughout.
CLOSES = [100 + 5 * ((index * 7) % 23) / 7 for index in range(80)]


def _batch(indicator, candles):
    return indicator.compute(candles).values


def _streamed(stream, candles):
    return tuple(stream.update(candle) for candle in candles)


@pytest.mark.parametrize(
    "indicator, stream",
    [
        (SMA(period=5), SMAStream(period=5)),
        (EMA(period=5), EMAStream(period=5)),
        (RSI(period=14), RSIStream(period=14)),
        (ATR(period=14), ATRStream(period=14)),
        (ROC(period=10), ROCStream(period=10)),
    ],
)
def test_the_stream_reproduces_the_batch_values(indicator, stream):
    candles = _candles(CLOSES)

    assert _streamed(stream, candles) == _batch(indicator, candles)


@pytest.mark.parametrize(
    "indicator, stream",
    [
        (SMA(period=1), SMAStream(period=1)),
        (EMA(period=1), EMAStream(period=1)),
        (RSI(period=1), RSIStream(period=1)),
        (ATR(period=1), ATRStream(period=1)),
        (ROC(period=1), ROCStream(period=1)),
    ],
)
def test_the_stream_reproduces_the_batch_values_with_period_one(indicator, stream):
    """The off-by-one cases live at period 1."""
    candles = _candles(CLOSES[:12])

    assert _streamed(stream, candles) == _batch(indicator, candles)


@pytest.mark.parametrize(
    "indicator, stream",
    [
        (SMA(period=50), SMAStream(period=50)),
        (EMA(period=50), EMAStream(period=50)),
        (RSI(period=50), RSIStream(period=50)),
        (ATR(period=50), ATRStream(period=50)),
        (ROC(period=50), ROCStream(period=50)),
    ],
)
def test_a_stream_with_no_warm_up_yet_is_all_none(indicator, stream):
    candles = _candles(CLOSES[:10])

    assert _streamed(stream, candles) == (None,) * 10
    assert _batch(indicator, candles) == (None,) * 10


def test_the_stream_keeps_the_previous_value_for_crossovers():
    """Strategies compare "now" with "one candle ago" (RSI, MA crossover)."""
    stream = RSIStream(period=14)
    candles = _candles(CLOSES[:30])

    values = [stream.update(candle) for candle in candles]

    assert stream.value == values[-1]
    assert stream.prev_value == values[-2]


def test_a_zero_close_makes_the_rate_of_change_undefined_in_both_forms():
    """A price of 0 has no percentage change; both forms leave it as ``None``."""
    candles = [
        Candle(
            symbol=Symbol("BTC/USDT"),
            interval="1h",
            open_time=BASE + index * HOUR,
            close_time=BASE + (index + 1) * HOUR,
            open=Decimal(str(value)),
            high=Decimal(str(value)) + Decimal("1"),
            low=Decimal(str(max(value - 1, 0))),
            close=Decimal(str(value)),
            volume=Decimal("10"),
        )
        for index, value in enumerate([0, 10, 20, 30])
    ]

    assert _streamed(ROCStream(period=2), candles) == _batch(ROC(period=2), candles)
    assert _batch(ROC(period=2), candles)[2] is None
