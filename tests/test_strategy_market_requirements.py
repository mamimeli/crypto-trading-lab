"""Tests for chapter 33.2 — market requirements.

A strategy that needs something from a market should say what, and the gate
should reject a run that cannot supply it. These tests cover both: the
declarations themselves (every built-in has a coherent record) and the
behaviour of ``validate_for_run`` when a requirement is violated.
"""

import pytest

from crypto_trading_lab.backtesting.engine import (
    BollingerBandsMeanReversionStrategy,
    BuyAndHoldStrategy,
    MACrossoverStrategy,
    NullStrategy,
    RSIStrategy,
    RollingHighLowBreakoutStrategy,
)
from crypto_trading_lab.domain.models import Candle, Symbol
from crypto_trading_lab.market_requirements import (
    ANY_MARKET,
    ASSET_TYPES,
    ENGINE_TRADING_MODE,
    SUPPORTED_FIELDS,
    MarketRequirements,
    market_requirements_for,
    render_market_requirements,
)
from crypto_trading_lab.strategy_validation import validate_for_run


# -- the declarations --------------------------------------------------------


def test_every_builtin_has_market_requirements():
    for strategy_id in (
        "ma_crossover",
        "rsi",
        "breakout",
        "bollinger",
        "buy_and_hold",
        "null_strategy",
    ):
        assert market_requirements_for(strategy_id) is not None, strategy_id


def test_an_unknown_strategy_has_no_requirements():
    assert market_requirements_for("does_not_exist") is None
    assert market_requirements_for(None) is None


def test_requirements_declare_a_supported_asset_type():
    for requirements in _all_requirements():
        assert requirements.asset_types, requirements.strategy_id
        for asset_type in requirements.asset_types:
            assert asset_type in ASSET_TYPES, asset_type
        # Every built-in must run on the engine's only supported mode.
        assert ENGINE_TRADING_MODE in requirements.asset_types


def test_requirements_declare_at_least_one_market():
    for requirements in _all_requirements():
        assert requirements.compatible_markets, requirements.strategy_id
        assert ANY_MARKET in requirements.compatible_markets


def test_required_fields_are_supplied_by_the_engine():
    for requirements in _all_requirements():
        for field in requirements.required_fields:
            assert field in SUPPORTED_FIELDS, (requirements.strategy_id, field)


def test_required_indicator_names_are_non_empty():
    for requirements in _all_requirements():
        for indicator in requirements.required_indicators:
            assert str(indicator).strip(), requirements.strategy_id


def test_min_data_required_is_non_negative():
    for requirements in _all_requirements():
        assert requirements.min_data_required >= 0, requirements.strategy_id


def test_requirements_are_frozen_and_round_trip():
    requirements = market_requirements_for("ma_crossover")
    assert isinstance(requirements.to_dict()["asset_types"], list)
    with pytest.raises(Exception):
        requirements.min_data_required = 999  # type: ignore[misc]


# -- the declarations match the code ----------------------------------------


def test_required_indicators_are_exposed_by_the_strategy():
    # The deeper check: indicator_values() must actually return what the
    # record lists. This cannot run inside validate_for_run (it would touch
    # the strategy's streaming state), so it lives here with real instances.
    cases = [
        (MACrossoverStrategy(), ("sma_fast", "sma_slow")),
        (RSIStrategy(), ("rsi",)),
        (RollingHighLowBreakoutStrategy(), ("rolling_high", "rolling_low")),
        (
            BollingerBandsMeanReversionStrategy(),
            ("middle", "upper", "lower"),
        ),
    ]
    for strategy, expected in cases:
        requirements = market_requirements_for(strategy.identifier)
        assert requirements is not None
        # Warm up the stream, then read the values the signal record would
        # carry. After the warm-up the keys must match the declaration.
        candles = _candles(requirements.min_data_required + 5)
        for index in range(len(candles)):
            strategy.on_candle(index, candles)
        values = strategy.indicator_values(len(candles) - 1, candles)
        for name in requirements.required_indicators:
            assert name in values, (strategy.identifier, name)
        assert set(requirements.required_indicators) == set(expected)


def test_benchmarks_declare_no_required_indicators():
    assert market_requirements_for("buy_and_hold").required_indicators == ()
    assert market_requirements_for("null_strategy").required_indicators == ()


def test_min_data_required_matches_the_default_warmup():
    # The documented floor must equal the default configuration's warm-up,
    # or the report would understate what the strategy needs.
    assert market_requirements_for("ma_crossover").min_data_required == 31
    assert market_requirements_for("rsi").min_data_required == 15
    assert market_requirements_for("breakout").min_data_required == 21
    assert market_requirements_for("bollinger").min_data_required == 20


# -- the gate ----------------------------------------------------------------


def test_a_strategy_that_cannot_trade_the_engine_mode_is_refused():
    requirements = MarketRequirements(
        strategy_id="demo",
        asset_types=("perpetual",),
        compatible_markets=(ANY_MARKET,),
        required_fields=("close",),
    )
    # The engine only trades spot, so a perpetual-only strategy cannot run,
    # regardless of the data it is handed.
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        market="BTC/USDT",
        timeframe="1h",
        market_requirements=requirements,
    )
    assert not validation.ok
    assert "market" in validation.codes()
    assert "cannot run" in validation.summary()


def test_a_strategy_restricted_to_another_market_is_refused():
    requirements = MarketRequirements(
        strategy_id="demo",
        asset_types=(ENGINE_TRADING_MODE,),
        compatible_markets=("ETH/USDT",),
        required_fields=("close",),
    )
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        market="BTC/USDT",
        timeframe="1h",
        market_requirements=requirements,
    )
    assert not validation.ok
    assert "restricted to" in validation.summary()


def test_an_any_market_requirement_accepts_the_requested_market():
    requirements = MarketRequirements(
        strategy_id="demo",
        asset_types=(ENGINE_TRADING_MODE,),
        compatible_markets=(ANY_MARKET,),
        required_fields=("close",),
    )
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        market="BTC/USDT",
        timeframe="1h",
        market_requirements=requirements,
    )
    assert validation.ok


def test_a_required_field_the_engine_cannot_supply_is_rejected():
    with pytest.raises(ValueError):
        MarketRequirements(
            strategy_id="demo",
            asset_types=(ENGINE_TRADING_MODE,),
            compatible_markets=(ANY_MARKET,),
            required_fields=("funding_rate",),
        )


def test_an_unknown_asset_type_is_rejected():
    with pytest.raises(ValueError):
        MarketRequirements(
            strategy_id="demo",
            asset_types=("swaps",),
            compatible_markets=(ANY_MARKET,),
            required_fields=("close",),
        )


def test_a_bad_required_timeframe_is_rejected():
    with pytest.raises(ValueError):
        MarketRequirements(
            strategy_id="demo",
            asset_types=(ENGINE_TRADING_MODE,),
            compatible_markets=(ANY_MARKET,),
            required_fields=("close",),
            required_timeframe="hourly",
        )


def test_a_mismatched_required_timeframe_is_a_warning():
    requirements = MarketRequirements(
        strategy_id="demo",
        asset_types=(ENGINE_TRADING_MODE,),
        compatible_markets=(ANY_MARKET,),
        required_fields=("close",),
        required_timeframe="1h",
    )
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20, interval="15m"),
        market="BTC/USDT",
        timeframe="15m",
        market_requirements=requirements,
    )
    assert validation.ok  # a warning, not a refusal
    assert "designed for 1h" in validation.summary()


def test_builtin_without_requirements_passes_unchanged():
    # A strategy with no record is not rejected by the market-requirements
    # branch; the other checks still apply.
    validation = validate_for_run(
        BuyAndHoldStrategy(), candles=_candles(20), market="BTC/USDT", timeframe="1h"
    )
    assert validation.ok


# -- rendering ---------------------------------------------------------------


def test_render_includes_every_declaration():
    text = render_market_requirements(market_requirements_for("ma_crossover"))
    for line in (
        "Compatible markets",
        "Supported asset types",
        "Required timeframe",
        "Required market-data fields",
        "Required indicators",
        "Minimum historical data",
    ):
        assert line in text


# -- helpers -----------------------------------------------------------------


def _all_requirements():
    return [
        market_requirements_for(strategy_id)
        for strategy_id in (
            "ma_crossover",
            "rsi",
            "breakout",
            "bollinger",
            "buy_and_hold",
            "null_strategy",
        )
    ]


def _candles(count=10, interval="1h", symbol="BTC/USDT") -> list[Candle]:
    from datetime import datetime, timedelta, timezone
    from decimal import Decimal

    base_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
    hour = timedelta(hours=1)
    candles: list[Candle] = []
    for i in range(count):
        candles.append(
            Candle(
                symbol=Symbol(symbol),
                interval=interval,
                open_time=base_time + i * hour,
                close_time=base_time + (i + 1) * hour,
                open=Decimal("100"),
                high=Decimal("101"),
                low=Decimal("99"),
                close=Decimal("100"),
                volume=Decimal("10"),
            )
        )
    return candles
