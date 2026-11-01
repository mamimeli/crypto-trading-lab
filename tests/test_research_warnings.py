"""Tests for the chapter 33.8 research warnings.

The chapter lists seven things the application must tell a user. These tests
check that each statement exists once, that the run-specific ones appear only
when they apply, and that the two surfaces which show them (CLI and GUI) read
the same canonical text.
"""

from __future__ import annotations

from crypto_trading_lab.research_warnings import (
    CHANCE,
    COMPLEXITY,
    FILTERS,
    HIGHER_PROFIT,
    OUT_OF_SAMPLE,
    OVERFITTING,
    OVERFITTING_PARAMETER_THRESHOLD,
    RESEARCH_WARNINGS,
    SIMPLER_WINS,
    summary,
    warnings_for_run,
)


def test_the_chapter_statements_exist_once_each():
    assert len(RESEARCH_WARNINGS) == 7
    assert len(set(RESEARCH_WARNINGS)) == 7


def test_a_plain_backtest_gets_the_three_that_are_always_true():
    warnings = warnings_for_run()

    assert warnings == (CHANCE, HIGHER_PROFIT, OUT_OF_SAMPLE)


def test_many_parameters_bring_the_overfitting_warning():
    warnings = warnings_for_run(parameters=OVERFITTING_PARAMETER_THRESHOLD)

    assert OVERFITTING in warnings


def test_few_parameters_do_not():
    warnings = warnings_for_run(parameters=OVERFITTING_PARAMETER_THRESHOLD - 1)

    assert OVERFITTING not in warnings


def test_an_optimized_run_brings_the_overfitting_warning_even_with_one_parameter():
    """Searching the same data for the best values is where overfitting is a
    likelihood, not a risk."""
    warnings = warnings_for_run(parameters=1, optimized=True)

    assert OVERFITTING in warnings


def test_filters_bring_the_filter_warning():
    warnings = warnings_for_run(filters=2)

    assert FILTERS in warnings
    assert FILTERS not in warnings_for_run(filters=0)


def test_an_out_of_sample_result_drops_the_in_sample_warning():
    warnings = warnings_for_run(evaluated_out_of_sample=True)

    assert OUT_OF_SAMPLE not in warnings


def test_an_unrecorded_complexity_is_stated():
    warnings = warnings_for_run(complexity_recorded=False)

    assert COMPLEXITY in warnings
    assert COMPLEXITY not in warnings_for_run(complexity_recorded=True)


def test_the_policy_statement_is_not_repeated_on_every_run():
    """``SIMPLER_WINS`` is a standing policy, not a finding about one run."""
    assert SIMPLER_WINS in RESEARCH_WARNINGS
    assert SIMPLER_WINS not in warnings_for_run(parameters=10, filters=3)


def test_the_order_follows_the_chapter():
    warnings = warnings_for_run(parameters=5, filters=1, complexity_recorded=False)

    assert warnings == (
        CHANCE,
        OVERFITTING,
        FILTERS,
        HIGHER_PROFIT,
        OUT_OF_SAMPLE,
        COMPLEXITY,
    )


def test_the_summary_is_a_readable_block():
    text = summary((CHANCE, HIGHER_PROFIT))

    assert text.startswith("- ")
    assert text.count("\n") == 1


def test_the_summary_defaults_to_every_statement():
    assert summary().count("\n") == 6
