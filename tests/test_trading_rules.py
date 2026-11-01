"""Tests for chapter 33.3 — trading rules.

The rules themselves are implemented by the engine (long-only spot, next-open
fill, single position, risk-manager-gated sizing) and, for declarative
rules, by ``RuleStrategySpec``. Chapter 33.3 is the *declaration* that sits
next to each strategy so the reader sees the formal contract in one block.
These tests check that every built-in has a coherent declaration and that the
gate behind the declaration behaves.
"""

import pytest

from crypto_trading_lab.backtesting.engine import BuyAndHoldStrategy
from crypto_trading_lab.rule_strategy import Condition, RuleError, RuleStrategySpec
from crypto_trading_lab.strategy_validation import validate_for_run
from crypto_trading_lab.trading_rules import (
    POSITION_SIZING,
    RULES,
    TradingRules,
    render_trading_rules,
    trading_rules_for,
)


# -- the declarations --------------------------------------------------------


def test_every_builtin_has_trading_rules():
    for strategy_id in (
        "ma_crossover",
        "rsi",
        "breakout",
        "bollinger",
        "buy_and_hold",
        "null_strategy",
    ):
        assert trading_rules_for(strategy_id) is not None, strategy_id


def test_an_unknown_strategy_has_no_rules():
    assert trading_rules_for("does_not_exist") is None
    assert trading_rules_for(None) is None


def test_entry_and_exit_are_stated():
    for rules in RULES.values():
        assert rules.entry_rule.strip(), rules.strategy_id
        assert rules.exit_rule.strip(), rules.strategy_id


def test_stop_take_profit_trailing_and_cooldown_are_stated():
    # "none" is a valid answer, but the field must say so rather than being
    # blank — a blank field is a declaration that was forgotten.
    for rules in RULES.values():
        for field in (
            "invalidation",
            "stop_loss",
            "take_profit",
            "trailing_stop",
            "cooldown",
            "time_restrictions",
        ):
            assert getattr(rules, field).strip(), (rules.strategy_id, field)


def test_position_sizing_is_the_shared_engine_rule():
    for rules in RULES.values():
        assert rules.position_sizing == POSITION_SIZING


def test_declaration_is_frozen_and_round_trips():
    rules = trading_rules_for("ma_crossover")
    assert isinstance(rules.to_dict()["entry_rule"], str)
    with pytest.raises(Exception):
        rules.entry_rule = "changed"  # type: ignore[misc]


def test_a_declaration_refuses_blank_entry():
    with pytest.raises(ValueError):
        TradingRules(
            strategy_id="demo",
            entry_rule="",
            exit_rule="sell signal",
            invalidation="none",
            stop_loss="none",
            take_profit="none",
            trailing_stop="none",
            cooldown="none",
            time_restrictions="none",
        )


# -- the gate behind the declaration ----------------------------------------


def test_rule_engine_enforces_stop_fraction_bounds():
    # The 33.3 declaration says stops are a fraction of entry; the rule engine
    # rejects anything outside (0, 1) at construction.
    with pytest.raises(RuleError):
        RuleStrategySpec(
            name="bad-stop",
            entry=(Condition("close", ">", "sma(5)"),),
            stop_loss_fraction=__import__("decimal").Decimal("1.5"),
        )
    with pytest.raises(RuleError):
        RuleStrategySpec(
            name="negative-stop",
            entry=(Condition("close", ">", "sma(5)"),),
            stop_loss_fraction=__import__("decimal").Decimal("-0.1"),
        )


def test_a_rule_with_no_exit_and_no_stops_is_a_warning():
    # Chapter 33.3 + 33.7: a rule that can never close (no exit condition and
    # no stop or take-profit) is a warning, not a refusal.
    validation = validate_for_run(
        BuyAndHoldStrategy(),
        rule_spec=RuleStrategySpec(
            name="no-exit",
            entry=(Condition("close", ">", "sma(5)"),),
        ),
    )
    assert validation.ok
    assert "rules" in validation.codes()
    assert "never be closed" in validation.summary()


def test_a_rule_with_a_stop_needs_no_exit_condition():
    from decimal import Decimal

    validation = validate_for_run(
        BuyAndHoldStrategy(),
        rule_spec=RuleStrategySpec(
            name="stop-only",
            entry=(Condition("close", ">", "sma(5)"),),
            stop_loss_fraction=Decimal("0.05"),
        ),
    )
    assert validation.ok


# -- rendering ---------------------------------------------------------------


def test_render_includes_every_declaration():
    text = render_trading_rules(trading_rules_for("ma_crossover"))
    for line in (
        "Entry:",
        "Exit:",
        "Invalidation:",
        "Stop-loss:",
        "Take-profit:",
        "Trailing stop:",
        "Cooldown:",
        "Time restrictions:",
        "Position sizing:",
    ):
        assert line in text
