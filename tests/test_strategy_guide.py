"""Beginner documentation for every strategy (ROADMAP.md chapter 33.9).

The chapter's promise is that no strategy can be run without a plain-language
answer to ten questions. A test is the only thing that keeps that promise
true for the seventh strategy somebody adds later, so these tests compare the
guide set against the registry rather than against a hand-written list.
"""

from __future__ import annotations

import pytest

from crypto_trading_lab.strategy_guide import (
    GUIDES,
    SIZING,
    STOPS_BUILTIN,
    STOPS_RULE,
    StrategyGuide,
    guide_for,
    render,
)
from crypto_trading_lab.strategy_registry import StrategyRegistry


def _builtin_ids():
    registry = StrategyRegistry()
    return [
        metadata.strategy_id
        for metadata in registry.list_strategies()
        if metadata.author == "Built-in"
    ]


def test_every_builtin_strategy_has_a_guide():
    missing = [sid for sid in _builtin_ids() if sid not in GUIDES]
    assert missing == []


def test_every_guide_belongs_to_a_registered_strategy():
    known = set(_builtin_ids())
    extra = [sid for sid in GUIDES if sid not in known]
    assert extra == []


@pytest.mark.parametrize("strategy_id", sorted(GUIDES))
def test_every_answer_is_present(strategy_id):
    guide = GUIDES[strategy_id]
    assert guide.strategy_id == strategy_id
    assert guide.title.strip()
    assert guide.attempts.strip()
    assert guide.assumes.strip()
    assert guide.entry.strip()
    assert guide.exit.strip()
    assert guide.honesty.strip()
    assert guide.sizing.strip()
    assert guide.stops.strip()
    # Conditions are lists, and an empty one would be an unanswered question.
    assert guide.favors
    assert guide.hurts
    assert all(item.strip() for item in guide.favors)
    assert all(item.strip() for item in guide.hurts)


@pytest.mark.parametrize("strategy_id", sorted(GUIDES))
def test_every_guide_says_why_the_backtest_is_not_a_promise(strategy_id):
    # Chapter 33.9's last question is the one that gets skipped, so it is the
    # one worth pinning: a sentence, not a word.
    honesty = GUIDES[strategy_id].honesty
    assert len(honesty.split()) >= 8


def test_render_answers_all_ten_questions():
    text = render(GUIDES["ma_crossover"])
    for heading in (
        "What it tries to do:",
        "What it assumes:",
        "Indicators it uses:",
        "What makes it enter:",
        "What makes it exit:",
        "How position sizing works:",
        "How stops work:",
        "Conditions that may favour it:",
        "Conditions that may hurt it:",
        "Why a profitable backtest is not a promise:",
    ):
        assert heading in text, heading


def test_render_names_a_strategy_without_indicators():
    text = render(GUIDES["null_strategy"])
    assert "Indicators it uses: none" in text


def test_sizing_and_stops_are_stated_once():
    # They belong to the engine, not to a strategy: six versions of the same
    # paragraph would be six chances to disagree.
    assert all(guide.sizing is SIZING for guide in GUIDES.values())
    assert GUIDES["buy_and_hold"].stops is STOPS_BUILTIN
    assert STOPS_RULE not in [guide.stops for guide in GUIDES.values()]


def test_guide_for_returns_none_for_an_unknown_strategy():
    assert guide_for("does_not_exist") is None
    assert guide_for(None) is None
    assert guide_for("") is None


def test_guide_for_returns_the_guide():
    guide = guide_for("rsi")
    assert guide is not None
    assert guide.strategy_id == "rsi"


def test_a_guide_without_an_answer_is_rejected():
    with pytest.raises(ValueError):
        StrategyGuide(
            strategy_id="empty",
            title="Empty",
            attempts="   ",
            assumes="x",
            indicators=(),
            entry="x",
            exit="x",
            favors=("x",),
            hurts=("x",),
            honesty="x",
        )
