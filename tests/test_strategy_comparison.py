"""Tests for the strategy comparison feature (chapters 33.8 and 35).

The point of this module is that ``complexity_control.prefer_simpler`` — a
rule the chapter says the application must actually apply — now has a caller.
These tests pin that the caller resolves complexity from the registry, runs
the rule when evidence is supplied, and honestly reports policy when it is
not.
"""

from decimal import Decimal

import pytest

from crypto_trading_lab.strategy_comparison import (
    StrategyComparison,
    compare_strategies,
    render_comparison,
)
from crypto_trading_lab.strategy_registry import StrategyRegistry


@pytest.fixture()
def registry() -> StrategyRegistry:
    # Read-only for the test: ``compare_strategies`` never mutates it, so
    # skipping the persisted file keeps the test hermetic.
    return StrategyRegistry(load=False)


def test_policy_mode_without_evidence_does_not_decide(registry) -> None:
    comparison = compare_strategies("ma_crossover", "rsi", registry=registry)
    assert comparison.mode == "policy"
    assert comparison.decision is None
    assert comparison.applied is False
    assert comparison.complexity_a is not None
    assert comparison.complexity_b is not None


def test_policy_mode_when_only_one_evidence_supplied(registry) -> None:
    comparison = compare_strategies(
        "ma_crossover", "rsi", evidence_a=1.05, registry=registry
    )
    assert comparison.mode == "policy"
    assert comparison.applied is False


def test_decision_mode_favours_simpler_when_evidence_comparable(registry) -> None:
    # ma_crossover (simpler, score 21) vs rsi (score 53), within 10%.
    comparison = compare_strategies(
        "ma_crossover",
        "rsi",
        evidence_a=Decimal("1.05"),
        evidence_b=Decimal("1.00"),
        registry=registry,
    )
    assert comparison.mode == "decision"
    assert comparison.applied is True
    assert comparison.decision is not None
    assert comparison.decision.preferred == "a"
    assert "simpler" in comparison.decision.reason.lower()


def test_decision_mode_favours_better_evidence_when_not_comparable(registry) -> None:
    # rsi (complex) has clearly better evidence; it must win on evidence,
    # not be rejected for complexity.
    comparison = compare_strategies(
        "ma_crossover",
        "rsi",
        evidence_a=Decimal("1.00"),
        evidence_b=Decimal("2.00"),
        registry=registry,
    )
    assert comparison.mode == "decision"
    assert comparison.decision is not None
    assert comparison.decision.preferred == "b"
    assert "evidence differs" in comparison.decision.reason.lower()


def test_tolerance_is_respected(registry) -> None:
    # Exactly at the 10% boundary counts as comparable -> simpler wins.
    comparison = compare_strategies(
        "ma_crossover",
        "rsi",
        evidence_a=Decimal("1.10"),
        evidence_b=Decimal("1.00"),
        tolerance=Decimal("0.10"),
        registry=registry,
    )
    assert comparison.mode == "decision"
    assert comparison.decision is not None
    assert comparison.decision.preferred == "a"


def test_missing_strategy_yields_no_complexity(registry) -> None:
    comparison = compare_strategies(
        "ma_crossover", "does_not_exist", registry=registry
    )
    assert comparison.complexity_b is None
    assert comparison.mode == "policy"


def test_render_includes_both_complexities_and_policy_in_policy_mode(registry) -> None:
    comparison = compare_strategies("ma_crossover", "rsi", registry=registry)
    text = render_comparison(comparison)
    assert "ma_crossover" in text
    assert "rsi" in text
    assert "score 21" in text
    assert "Policy:" in text
    assert "favours the simpler" in text


def test_render_reports_decision_and_reason_in_decision_mode(registry) -> None:
    comparison = compare_strategies(
        "ma_crossover",
        "rsi",
        evidence_a=Decimal("1.05"),
        evidence_b=Decimal("1.00"),
        registry=registry,
    )
    text = render_comparison(comparison)
    assert "Decision:" in text
    assert "Reason:" in text
    assert "ma_crossover" in text


def test_result_is_frozen_and_typed() -> None:
    comparison = StrategyComparison(
        strategy_a_id="a",
        strategy_b_id="b",
        complexity_a=None,
        complexity_b=None,
    )
    assert isinstance(comparison, StrategyComparison)
    with pytest.raises(Exception):
        comparison.mode = "decision"  # frozen
