"""Tests for chapter 33 initial strategies: RSI, breakout, Bollinger (items 2/3/4).

Offline and deterministic: each strategy runs through run_backtest on
crafted candles and its signal logic is checked directly.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from crypto_trading_lab.backtesting.engine import (
    BollingerBandsMeanReversionStrategy,
    RollingHighLowBreakoutStrategy,
    RSIStrategy,
    run_backtest,
)
from crypto_trading_lab.domain.models import Candle, OrderSide, Symbol
from crypto_trading_lab.indicators.library import RSI
from crypto_trading_lab.strategy_registry import StrategyRegistry

BASE = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _candles(closes):
    return [
        Candle(
            Symbol("BTC/USDT"),
            "1m",
            BASE + timedelta(minutes=i),
            BASE + timedelta(minutes=i + 1),
            open=Decimal(str(c)),
            high=Decimal(str(c + 1)),
            low=Decimal(str(c - 1)),
            close=Decimal(str(c)),
            volume=Decimal("10"),
        )
        for i, c in enumerate(closes)
    ]


def test_rsi_validation_rejects_bad_params():
    import pytest
    with pytest.raises(ValueError):
        RSIStrategy(period=0)
    with pytest.raises(ValueError):
        RSIStrategy(oversold=80, overbought=70)
    with pytest.raises(ValueError):
        RSIStrategy(oversold=30, overbought=70, volume_filter_period=-1)
    with pytest.raises(ValueError):
        RSIStrategy(cooldown=-1)


def test_rsi_name_and_warmup():
    s = RSIStrategy(period=14, oversold=30, overbought=70)
    assert s.name == "RSI(14) 30/70"
    assert s.warmup_candles == 15
    assert s.version == "1.0.0"


def test_rsi_emits_buy_and_sell_on_crossings():
    period = 5
    closes = [100] * 20 + list(range(100, 40, -4)) + [40] * 3 + list(range(40, 120, 4))
    candles = _candles(closes)
    rsi_vals = RSI(period).compute(candles).values
    s = RSIStrategy(period=period, oversold=30, overbought=70)
    buy_idx = sell_idx = None
    for i in range(1, len(rsi_vals)):
        if rsi_vals[i] is None or rsi_vals[i - 1] is None:
            continue
        if buy_idx is None and rsi_vals[i - 1] > 30 and rsi_vals[i] <= 30:
            buy_idx = i
        if sell_idx is None and rsi_vals[i - 1] < 70 and rsi_vals[i] >= 70:
            sell_idx = i
    assert buy_idx is not None
    assert sell_idx is not None
    # ``on_candle`` is a streaming interface: the engine feeds every candle in
    # order, so the test must too (the RSI used to be recomputed from scratch,
    # which allowed jumping to an index but cost O(N) per candle).
    decisions = [s.on_candle(i, candles[: i + 1]) for i in range(len(candles))]
    assert decisions[buy_idx] == OrderSide.BUY
    assert decisions[sell_idx] == OrderSide.SELL


def test_rsi_trend_filter_blocks_entry():
    period = 5
    closes = [100] * 20 + list(range(100, 40, -4)) + [40] * 3
    candles = _candles(closes)
    rsi_vals = RSI(period).compute(candles).values
    s = RSIStrategy(period=period, oversold=30, overbought=70, trend_filter_period=10)
    buy_idx = None
    for i in range(1, len(rsi_vals)):
        if rsi_vals[i] is None or rsi_vals[i - 1] is None:
            continue
        if rsi_vals[i - 1] > 30 and rsi_vals[i] <= 30:
            buy_idx = i
            break
    assert buy_idx is not None
    # In a falling market the close is below its SMA, so the trend filter
    # blocks the long entry.
    assert s.on_candle(buy_idx, candles) is None
def test_breakout_validation():
    import pytest
    with pytest.raises(ValueError):
        RollingHighLowBreakoutStrategy(period=1)


def test_breakout_buys_on_spike_and_sells_on_drop():
    closes = [100] * 25 + [100, 130, 100, 70]
    candles = _candles(closes)
    s = RollingHighLowBreakoutStrategy(period=20)
    signals = [s.on_candle(i, candles) for i in range(len(candles))]
    assert OrderSide.BUY in signals
    assert OrderSide.SELL in signals


def test_bollinger_validation():
    import pytest
    with pytest.raises(ValueError):
        BollingerBandsMeanReversionStrategy(period=0)
    with pytest.raises(ValueError):
        BollingerBandsMeanReversionStrategy(k=0)


def test_bollinger_buys_on_lower_band_and_sells_on_recovery():
    closes = [100] * 20 + [70, 90, 110]
    candles = _candles(closes)
    s = BollingerBandsMeanReversionStrategy(period=10, k=2)
    signals = [s.on_candle(i, candles) for i in range(len(candles))]
    assert OrderSide.BUY in signals
    assert OrderSide.SELL in signals


def test_registry_lists_new_strategies():
    reg = StrategyRegistry(load=False)
    ids = {m.strategy_id for m in reg.list_strategies()}
    assert {"rsi", "breakout", "bollinger"} <= ids


def test_registry_create_instance_with_params():
    reg = StrategyRegistry(load=False)
    s = reg.create_instance("rsi", period=5, oversold=25, overbought=75)
    assert isinstance(s, RSIStrategy)
    assert s.period == 5 and s.oversold == 25 and s.overbought == 75
    b = reg.create_instance("bollinger", period=10, k=3)
    assert b.period == 10 and b.k == 3


def test_rsi_runs_in_backtest():
    closes = [100] * 20 + list(range(100, 40, -4)) + [40] * 3 + list(range(40, 120, 4))
    result = run_backtest(_candles(closes), RSIStrategy(period=5))
    assert result.strategy_name == "RSI(5) 30/70"
    assert result.candle_count == len(closes)


def test_breakout_runs_in_backtest():
    closes = [100] * 25 + [100, 130, 100, 70, 100]
    result = run_backtest(_candles(closes), RollingHighLowBreakoutStrategy(period=20))
    assert result.strategy_name == "Rolling 20-bar high/low breakout"
    assert len(result.trades) >= 1


def test_bollinger_runs_in_backtest():
    closes = [100] * 20 + [70, 90, 110, 100]
    result = run_backtest(_candles(closes), BollingerBandsMeanReversionStrategy(period=10, k=2))
    assert result.strategy_name == "Bollinger(10,2) mean reversion"
    assert len(result.trades) >= 1
