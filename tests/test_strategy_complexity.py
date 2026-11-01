"""Tests for strategy complexity control (ROADMAP.md chapter 35).

Chapter 35 asks for two different things and this module checks both:

* every strategy version *records* how many parameters, rules, indicators,
  filters and conditions it declares, how big its parameter grid is, and how
  big any machine-learning model is;
* the program never treats a more complex strategy as automatically better —
  comparable evidence means the simpler one wins, and growth without
  evidence is a warning.

The counts are metadata, not quality: a test here may not claim that a
simple strategy is profitable.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from crypto_trading_lab.complexity_control import (
    ComplexityComparison,
    StrategyComplexity,
    complexity_growth_warning,
    prefer_simpler,
    strategy_complexity_from_rule,
    strategy_complexity_from_schema,
)
from crypto_trading_lab.qualification import evaluate_complexity, qualify_strategy
from crypto_trading_lab.rule_strategy import Condition, RuleStrategySpec
from crypto_trading_lab.strategy_registry import StrategyRegistry


# -- the record itself -------------------------------------------------------


def test_negative_counts_are_rejected():
    with pytest.raises(ValueError, match="num_parameters"):
        StrategyComplexity(num_parameters=-1)


def test_a_grid_of_no_configurations_is_rejected():
    """One setting is the floor: zero configurations is not a search space."""
    with pytest.raises(ValueError, match="optimization_complexity"):
        StrategyComplexity(optimization_complexity=0)


def test_the_schema_gives_the_parameter_count_and_the_grid_size():
    schema = {
        "fast": {"type": "int", "min": 1, "max": 200},
        "slow": {"type": "int", "min": 1, "max": 500},
    }
    complexity = strategy_complexity_from_schema(
        schema, rules=2, indicators=2, conditions=2, version="1.0.0"
    )

    assert complexity.num_parameters == 2
    assert complexity.optimization_complexity == 200 * 500
    assert complexity.version == "1.0.0"


def test_a_parameter_without_bounds_is_one_setting_not_an_invented_range():
    """Unknown bounds must not be guessed into a huge grid."""
    complexity = strategy_complexity_from_schema({"period": {"type": "int"}})

    assert complexity.num_parameters == 1
    assert complexity.optimization_complexity == 1
    assert complexity.search_space_order == 0


def test_a_continuous_range_without_a_step_is_not_a_grid():
    complexity = strategy_complexity_from_schema(
        {"threshold": {"type": "float", "min": 0.0, "max": 1.0}}
    )
    assert complexity.optimization_complexity == 1


def test_a_float_range_with_a_step_counts_its_points():
    complexity = strategy_complexity_from_schema(
        {"threshold": {"type": "float", "min": 0.0, "max": 1.0, "step": 0.1}}
    )
    assert complexity.optimization_complexity == 11


def test_an_allowed_list_counts_its_values():
    complexity = strategy_complexity_from_schema(
        {"mode": {"type": "str", "allowed": ["trend", "range"]}}
    )
    assert complexity.optimization_complexity == 2


def test_the_score_uses_the_order_of_magnitude_of_the_grid():
    """10^2 against 10^11 by subtraction would drown every other term."""
    small = StrategyComplexity(num_parameters=2, optimization_complexity=100)
    large = StrategyComplexity(num_parameters=2, optimization_complexity=10**11)

    assert large.score - small.score == 9


# -- declarative rules -------------------------------------------------------


def _spec(**kwargs) -> RuleStrategySpec:
    entry = (Condition("close", "crosses_above", "sma(20)"),)
    return RuleStrategySpec(name="test rule", entry=entry, **kwargs)


def test_a_rule_reports_its_conditions_indicators_and_tunables():
    spec = RuleStrategySpec(
        name="two averages",
        entry=(Condition("sma(10)", "crosses_above", "sma(30)"),),
        exit=(Condition("close", "<", "sma(30)"),),
        stop_loss_fraction=Decimal("0.05"),
        take_profit_fraction=Decimal("0.15"),
        version="2.0",
    )

    complexity = strategy_complexity_from_rule(spec)

    assert complexity.num_conditions == 2
    assert complexity.num_rules == 4  # two conditions + stop + target
    assert complexity.num_indicators == 2  # sma(10) and sma(30)
    assert complexity.num_parameters == 4  # two periods + stop + target
    assert complexity.version == "2.0"


def test_a_rule_declares_no_bounds_so_its_grid_is_one():
    """The rule language has no parameter ranges; saying so beats guessing."""
    complexity = strategy_complexity_from_rule(_spec())

    assert complexity.optimization_complexity == 1


def test_repeating_an_indicator_does_not_count_it_twice():
    spec = RuleStrategySpec(
        name="same average twice",
        entry=(
            Condition("sma(20)", ">", "close"),
            Condition("sma(20)", ">", "100"),
        ),
    )

    complexity = strategy_complexity_from_rule(spec)

    assert complexity.num_conditions == 2
    assert complexity.num_indicators == 1
    assert complexity.num_parameters == 1


# -- comparable evidence favours the simple one ------------------------------


def test_comparable_evidence_prefers_the_simpler_strategy():
    simple = StrategyComplexity(num_rules=2, num_indicators=2, num_conditions=2)
    complex_one = StrategyComplexity(
        num_parameters=4,
        num_rules=5,
        num_indicators=3,
        num_filters=2,
        num_conditions=5,
        optimization_complexity=10_000,
    )

    verdict = prefer_simpler(
        Decimal("0.100"), simple, Decimal("0.105"), complex_one
    )

    assert verdict.preferred == "a"
    assert "simpler" in verdict.reason


def test_comparable_evidence_does_not_favour_the_complex_one_when_it_is_b():
    simple = StrategyComplexity(num_rules=1)
    complex_one = StrategyComplexity(num_parameters=6, optimization_complexity=10**8)

    verdict = prefer_simpler(Decimal("0.10"), complex_one, Decimal("0.102"), simple)

    assert verdict.preferred == "b"


def test_a_clear_evidence_gap_beats_simplicity():
    simple = StrategyComplexity(num_rules=1)
    complex_one = StrategyComplexity(num_parameters=6, optimization_complexity=10**8)

    verdict = prefer_simpler(Decimal("0.02"), simple, Decimal("0.30"), complex_one)

    assert verdict.preferred == "b"
    assert "Evidence differs" in verdict.reason


def test_equal_evidence_and_equal_complexity_is_a_tie():
    same = StrategyComplexity(num_rules=2)
    verdict = prefer_simpler(Decimal("0.10"), same, Decimal("0.10"), same)

    assert verdict.preferred == "tie"
    assert isinstance(verdict, ComplexityComparison)


def test_zero_evidence_on_both_sides_is_comparable():
    simple = StrategyComplexity(num_rules=1)
    complex_one = StrategyComplexity(num_parameters=3)

    verdict = prefer_simpler(Decimal("0"), simple, Decimal("0"), complex_one)

    assert verdict.preferred == "a"


# -- growth without evidence is a warning ------------------------------------


def test_growth_without_better_evidence_warns():
    before = StrategyComplexity(num_rules=2, num_indicators=2, num_conditions=2)
    after = StrategyComplexity(
        num_parameters=3,
        num_rules=4,
        num_indicators=3,
        num_filters=1,
        num_conditions=4,
    )

    warning = complexity_growth_warning(
        before, after, Decimal("0.10"), Decimal("0.101")
    )

    assert warning is not None
    assert "not free" in warning


def test_growth_with_real_improvement_does_not_warn():
    before = StrategyComplexity(num_rules=2)
    after = StrategyComplexity(num_parameters=3, num_rules=4)

    assert (
        complexity_growth_warning(before, after, Decimal("0.05"), Decimal("0.20"))
        is None
    )


def test_a_simpler_version_never_warns():
    before = StrategyComplexity(num_parameters=4, num_rules=5)
    after = StrategyComplexity(num_rules=2)

    assert (
        complexity_growth_warning(before, after, Decimal("0.10"), Decimal("0.10"))
        is None
    )


# -- the registry records it per version -------------------------------------


def test_builtin_strategies_record_their_complexity(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path / "registry")

    crossover = registry.get("ma_crossover").metadata.complexity
    null = registry.get("null_strategy").metadata.complexity

    assert crossover.num_parameters == 2
    assert crossover.num_indicators == 2
    assert crossover.optimization_complexity == 200 * 500
    assert null.score < crossover.score
    assert null.num_parameters == 0


def test_the_registry_round_trips_the_complexity_record(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path / "registry")
    registry.register(
        strategy_id="custom",
        factory=lambda **kwargs: None,
        name="Custom",
        version="1.2.3",
        author="tester",
        description="declares a structure",
        parameters_schema={
            "period": {"type": "int", "min": 5, "max": 20, "default": 10}
        },
        structure={"rules": 2, "indicators": 1, "filters": 1, "conditions": 3},
    )

    reloaded = StrategyRegistry(storage_path=tmp_path / "registry")
    record = reloaded.get("custom").metadata.complexity

    assert record.num_rules == 2
    assert record.num_filters == 1
    assert record.num_conditions == 3
    assert record.optimization_complexity == 16
    assert record.version == "1.2.3"


def test_a_new_version_recomputes_the_parameter_grid(tmp_path):
    """The record follows the version, which is the point of chapter 35."""
    registry = StrategyRegistry(storage_path=tmp_path / "registry")
    registry.register(
        strategy_id="custom",
        factory=lambda **kwargs: None,
        name="Custom",
        version="1.0.0",
        author="tester",
        description="one parameter",
        parameters_schema={
            "period": {"type": "int", "min": 1, "max": 10, "default": 5}
        },
        structure={"rules": 1, "conditions": 1},
    )

    registry.update_metadata(
        "custom",
        version="1.1.0",
        parameters_schema={
            "period": {"type": "int", "min": 1, "max": 10, "default": 5},
            "threshold": {"type": "int", "min": 1, "max": 5, "default": 3},
        },
    )

    record = registry.get("custom").metadata.complexity
    assert record.version == "1.1.0"
    assert record.num_parameters == 2
    assert record.optimization_complexity == 50
    assert record.num_rules == 1  # structure is not lost on update


# -- qualification shows the numbers -----------------------------------------


def test_the_qualification_criterion_carries_the_metrics():
    metrics = StrategyComplexity(
        num_parameters=2, num_rules=2, num_indicators=2, num_conditions=2
    )

    result = evaluate_complexity(True, metrics)

    assert result.passed
    assert result.value == f"score={metrics.score}"
    assert "2 parameter(s)" in result.notes


def test_the_criterion_still_works_without_metrics():
    """Older callers only know the verdict, and must keep working."""
    result = evaluate_complexity(False)

    assert not result.passed
    assert result.value == "False"


def test_a_qualification_review_displays_the_complexity_metrics():
    metrics = StrategyComplexity(num_parameters=3, num_rules=4, num_conditions=4)

    report = qualify_strategy(
        oos_return=Decimal("0.10"),
        max_drawdown=Decimal("0.05"),
        number_of_trades=40,
        sharpe_ratio=Decimal("1.2"),
        complexity_acceptable=True,
        complexity_metrics=metrics,
    )

    criterion = next(
        c for c in report.criterion_results if c.name == "complexity"
    )
    assert criterion.value == f"score={metrics.score}"
    assert "3 parameter(s)" in criterion.notes
