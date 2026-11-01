"""Tests for strategy validation before a run (ROADMAP.md chapter 33.7).

The chapter asks for eight checks before a strategy is backtested or
paper-traded. These tests check that each one fires when it should, that it
stays quiet when it should, and that errors and warnings are not the same
thing: a warning never stops a run, an error always does.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from crypto_trading_lab.backtesting.engine import (
    BuyAndHoldStrategy,
    MACrossoverStrategy,
)
from crypto_trading_lab.domain.models import Candle, Symbol
from crypto_trading_lab.rule_strategy import Condition, RuleStrategySpec
from crypto_trading_lab.strategy_parameters import (
    CombinationRule,
    ParameterSchema,
    ParameterSpec,
)
from crypto_trading_lab.strategy_validation import (
    Severity,
    StrategyValidationError,
    TIMEFRAME_RE,
    validate_for_run,
)

BASE = datetime(2024, 1, 1, tzinfo=timezone.utc)
HOUR = timedelta(hours=1)


def _candles(count=10, interval="1h", symbol="BTC/USDT") -> list[Candle]:
    return [
        Candle(
            symbol=Symbol(symbol),
            interval=interval,
            open_time=BASE + index * HOUR,
            close_time=BASE + (index + 1) * HOUR,
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal("100"),
            volume=Decimal("10"),
        )
        for index in range(count)
    ]


def _codes(validation) -> tuple[str, ...]:
    return validation.codes()


# -- a valid strategy --------------------------------------------------------


def test_a_valid_strategy_passes_cleanly():
    validation = validate_for_run(
        MACrossoverStrategy(fast=2, slow=3),
        candles=_candles(20),
        market="BTC/USDT",
        timeframe="1h",
    )

    assert validation.ok
    assert validation.errors == ()
    assert validation.warnings == ()
    assert validation.summary() == "the strategy is valid for this run"


# -- configuration -----------------------------------------------------------


def test_a_strategy_without_on_candle_is_refused():
    validation = validate_for_run(object(), candles=_candles())

    assert not validation.ok
    assert "configuration" in _codes(validation)


def test_a_negative_warmup_is_an_error():
    class Broken:
        name = "broken"
        warmup_candles = -3

        def on_candle(self, index, candles):
            return None

    validation = validate_for_run(Broken(), candles=_candles())

    assert not validation.ok
    assert "configuration" in _codes(validation)


def test_a_missing_warmup_is_only_a_warning():
    """It can run; it just cannot warn about a short sample."""

    class Quiet:
        name = "quiet"

        def on_candle(self, index, candles):
            return None

        def indicator_values(self, index, candles):
            return {}

    validation = validate_for_run(Quiet(), candles=_candles())

    assert validation.ok
    assert "configuration" in _codes(validation)


# -- warm-up -----------------------------------------------------------------


def test_a_warmup_longer_than_the_sample_is_an_error():
    """No candle will ever be enough, so the run cannot mean anything."""
    validation = validate_for_run(
        MACrossoverStrategy(fast=10, slow=30), candles=_candles(10)
    )

    assert not validation.ok
    assert "warmup" in _codes(validation)
    assert "can never act" in validation.summary()


def test_a_warmup_that_eats_most_of_the_sample_is_a_warning():
    validation = validate_for_run(
        MACrossoverStrategy(fast=2, slow=5), candles=_candles(8)
    )

    assert validation.ok
    assert [i.severity for i in validation.warnings] == [Severity.WARNING]
    assert "warm-up eats" in validation.warnings[0].message


def test_an_unknown_sample_length_skips_the_length_checks():
    """Live paper trading has not received the candles yet."""
    validation = validate_for_run(
        MACrossoverStrategy(fast=10, slow=30),
        candles=None,
        market="BTC/USDT",
        timeframe="1m",
    )

    assert validation.ok
    assert "warmup" not in _codes(validation)


# -- timeframe ---------------------------------------------------------------


def test_the_timeframe_grammar_is_what_the_project_uses():
    assert TIMEFRAME_RE.match("15m")
    assert TIMEFRAME_RE.match("4h")
    assert TIMEFRAME_RE.match("1d")
    assert not TIMEFRAME_RE.match("1 hour")
    assert not TIMEFRAME_RE.match("hourly")


def test_an_unreadable_timeframe_is_an_error():
    validation = validate_for_run(BuyAndHoldStrategy(), timeframe="hourly")

    assert not validation.ok
    assert "timeframe" in _codes(validation)


def test_a_timeframe_the_data_does_not_have_is_an_error():
    validation = validate_for_run(
        BuyAndHoldStrategy(), candles=_candles(5, interval="1h"), timeframe="1d"
    )

    assert not validation.ok
    assert "timeframe" in _codes(validation)


def test_data_mixing_intervals_is_an_error():
    mixed = _candles(3) + _candles(3, interval="1d")

    validation = validate_for_run(BuyAndHoldStrategy(), candles=mixed)

    assert not validation.ok
    assert "timeframe" in _codes(validation)


# -- market ------------------------------------------------------------------


def test_data_for_another_market_is_an_error():
    validation = validate_for_run(
        BuyAndHoldStrategy(), candles=_candles(5), market="ETH/USDT"
    )

    assert not validation.ok
    assert "market" in _codes(validation)


def test_a_market_without_a_quote_currency_is_an_error():
    validation = validate_for_run(BuyAndHoldStrategy(), market="BTCUSDT")

    assert not validation.ok
    assert "market" in _codes(validation)


def test_market_comparison_ignores_case():
    """``Symbol`` normalises to upper case; the check must too."""
    validation = validate_for_run(
        BuyAndHoldStrategy(), candles=_candles(5), market="btc/usdt"
    )

    assert validation.ok


def test_data_mixing_markets_is_an_error():
    mixed = _candles(3) + _candles(3, symbol="ETH/USDT")

    validation = validate_for_run(BuyAndHoldStrategy(), candles=mixed)

    assert not validation.ok
    assert "market" in _codes(validation)


# -- parameters --------------------------------------------------------------


def test_a_parameter_schema_whose_own_defaults_break_a_rule_is_an_error():
    """A spec validates its own default, so only a combination rule can
    make a schema invalid on its own terms."""
    schema = ParameterSchema(
        specs=(
            ParameterSpec("fast", "int", default=10, minimum=1, maximum=20),
            ParameterSpec("slow", "int", default=5, minimum=1, maximum=20),
        ),
        rules=(
            CombinationRule(
                "fast < slow",
                lambda values: (
                    "fast must be smaller than slow"
                    if values["fast"] >= values["slow"]
                    else None
                ),
            ),
        ),
    )

    validation = validate_for_run(BuyAndHoldStrategy(), schema=schema)

    assert not validation.ok
    assert "parameters" in _codes(validation)
    assert "fast must be smaller than slow" in validation.summary()


def test_a_valid_parameter_schema_passes():
    schema = ParameterSchema(
        specs=(ParameterSpec("fast", "int", default=10, minimum=1, maximum=20),)
    )

    validation = validate_for_run(BuyAndHoldStrategy(), schema=schema)

    assert validation.ok


# -- rules -------------------------------------------------------------------


def _rule(**kwargs) -> RuleStrategySpec:
    return RuleStrategySpec(name="test", **kwargs)


def test_identical_entry_and_exit_are_refused():
    condition = Condition("close", ">", "sma(5)")
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        rule_spec=_rule(entry=(condition,), exit=(condition,)),
    )

    assert not validation.ok
    assert "rules" in _codes(validation)
    assert "open and close the position at once" in validation.summary()


def test_a_condition_between_two_constants_is_refused():
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        rule_spec=_rule(entry=(Condition("50", ">", "40"),)),
    )

    assert not validation.ok
    assert "always true or always false" in validation.summary()


def test_contradictory_bounds_are_refused():
    """``close > 100`` and ``close < 50`` can never both hold."""
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        rule_spec=_rule(
            entry=(Condition("close", ">", "100"), Condition("close", "<", "50"))
        ),
    )

    assert not validation.ok
    assert "cannot all be true at once" in validation.summary()


def test_bounds_that_merely_touch_are_contradictory_when_strict():
    """``close > 100`` and ``close < 100`` cannot both hold either."""
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        rule_spec=_rule(
            entry=(Condition("close", ">", "100"), Condition("close", "<", "100"))
        ),
    )

    assert not validation.ok
    assert "cannot all be true at once" in validation.summary()


def test_consistent_bounds_pass():
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        rule_spec=_rule(
            entry=(Condition("close", ">", "50"), Condition("close", "<", "100")),
            exit=(Condition("close", "<", "50"),),
        ),
    )

    assert validation.ok


def test_an_indicator_that_cannot_fill_is_an_error():
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(10),
        rule_spec=_rule(entry=(Condition("close", ">", "sma(50)"),)),
    )

    assert not validation.ok
    assert "indicators" in _codes(validation)
    assert "can never be ready" in validation.summary()


def test_a_rule_with_no_exit_and_no_stops_is_a_warning():
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        rule_spec=_rule(entry=(Condition("close", ">", "sma(5)"),)),
    )

    assert validation.ok
    assert "rules" in _codes(validation)
    assert "never be closed" in validation.summary()


def test_a_rule_with_a_stop_loss_does_not_need_an_exit_condition():
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        candles=_candles(20),
        rule_spec=_rule(
            entry=(Condition("close", ">", "sma(5)"),),
            stop_loss_fraction=Decimal("0.05"),
        ),
    )

    assert validation.ok


# -- the verdict -------------------------------------------------------------


def test_errors_raise_and_carry_every_reason():
    validation = validate_for_run(
        BuyAndHoldStrategy(), candles=_candles(5), market="ETH/USDT", timeframe="1d"
    )

    with pytest.raises(StrategyValidationError) as caught:
        validation.raise_for_errors()

    message = str(caught.value)
    assert "market" in message and "timeframe" in message
    assert caught.value.validation is validation


def test_a_warning_does_not_raise():
    validation = validate_for_run(
        MACrossoverStrategy(fast=2, slow=5), candles=_candles(8)
    )

    validation.raise_for_errors()  # does not raise


def test_the_issues_serialise_for_reports():
    validation = validate_for_run(BuyAndHoldStrategy(), timeframe="hourly")

    payload = validation.errors[0].to_dict()

    assert payload["severity"] == "error"
    assert payload["code"] == "timeframe"
    assert "hourly" in payload["message"]
