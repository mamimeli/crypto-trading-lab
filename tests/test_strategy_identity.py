"""Strategy identity (ROADMAP.md chapter 33.1).

The nine declarations are only worth having if they are the *same* nine the
registry reports and the guide explains. These tests compare the three
records against each other rather than against a hand-written list, so a
seventh strategy cannot arrive with a name nobody else uses.
"""

from __future__ import annotations

import pytest

from crypto_trading_lab.strategy_guide import GUIDES
from crypto_trading_lab.strategy_identity import (
    CATEGORIES,
    IDENTITIES,
    StrategyIdentity,
    identity_for,
    render_identity,
)
from crypto_trading_lab.strategy_registry import StrategyRegistry


def _registry_metadata():
    registry = StrategyRegistry()
    return {meta.strategy_id: meta for meta in registry.list_strategies()}


def test_every_builtin_strategy_declares_an_identity():
    builtins = {
        sid
        for sid, meta in _registry_metadata().items()
        if meta.author == "Built-in"
    }
    assert builtins - set(IDENTITIES) == set()


def test_no_identity_exists_for_an_unknown_strategy():
    assert set(IDENTITIES) - set(_registry_metadata()) == set()


def test_identity_set_matches_the_guide_set():
    # Chapter 33.1 and 33.9 describe the same strategies; a strategy with one
    # and not the other is half-documented.
    assert set(IDENTITIES) == set(GUIDES)


@pytest.mark.parametrize("strategy_id", sorted(IDENTITIES))
def test_the_registry_reports_the_declared_identity(strategy_id):
    identity = IDENTITIES[strategy_id]
    meta = _registry_metadata()[strategy_id]
    assert meta.name == identity.name
    assert meta.version == identity.version
    assert meta.author == identity.author
    assert meta.description == identity.description
    assert meta.category == identity.category


@pytest.mark.parametrize("strategy_id", sorted(IDENTITIES))
def test_every_declaration_is_present_and_substantial(strategy_id):
    identity = IDENTITIES[strategy_id]
    assert identity.strategy_id == strategy_id
    assert identity.category in CATEGORIES
    # Nine boxes, not nine empty strings.
    assert len(identity.beginner_explanation.split()) >= 15
    assert len(identity.known_weaknesses) >= 2
    assert len(identity.risk_warnings) >= 2
    assert all(len(item.split()) >= 6 for item in identity.known_weaknesses)
    assert all(len(item.split()) >= 6 for item in identity.risk_warnings)


def test_categories_are_used_not_just_declared():
    used = {identity.category for identity in IDENTITIES.values()}
    assert used <= set(CATEGORIES)
    # A category nothing belongs to is a category nobody needs.
    assert set(CATEGORIES) - used == set()


def test_an_identifier_must_be_lowercase_and_stable():
    with pytest.raises(ValueError):
        StrategyIdentity(
            strategy_id="Not An Id",
            name="x",
            version="1.0.0",
            author="x",
            description="x",
            category=CATEGORIES[0],
            beginner_explanation="x",
            known_weaknesses=("x",),
            risk_warnings=("x",),
        )


def test_a_version_must_be_semantic():
    with pytest.raises(ValueError):
        StrategyIdentity(
            strategy_id="ok",
            name="x",
            version="v1",
            author="x",
            description="x",
            category=CATEGORIES[0],
            beginner_explanation="x",
            known_weaknesses=("x",),
            risk_warnings=("x",),
        )


def test_an_unknown_category_is_rejected():
    with pytest.raises(ValueError):
        StrategyIdentity(
            strategy_id="ok",
            name="x",
            version="1.0.0",
            author="x",
            description="x",
            category="whatever",
            beginner_explanation="x",
            known_weaknesses=("x",),
            risk_warnings=("x",),
        )


def test_a_strategy_must_confess_something():
    # A strategy with no declared weakness is a strategy nobody reviewed.
    with pytest.raises(ValueError):
        StrategyIdentity(
            strategy_id="ok",
            name="x",
            version="1.0.0",
            author="x",
            description="x",
            category=CATEGORIES[0],
            beginner_explanation="x",
            known_weaknesses=(),
            risk_warnings=("x",),
        )
    with pytest.raises(ValueError):
        StrategyIdentity(
            strategy_id="ok",
            name="x",
            version="1.0.0",
            author="x",
            description="x",
            category=CATEGORIES[0],
            beginner_explanation="x",
            known_weaknesses=("x",),
            risk_warnings=(),
        )


def test_identity_for_returns_none_for_an_unknown_strategy():
    assert identity_for("does_not_exist") is None
    assert identity_for(None) is None
    assert identity_for("rsi") is not None


def test_to_dict_round_trips_the_declarations():
    data = IDENTITIES["rsi"].to_dict()
    assert data["strategy_id"] == "rsi"
    assert data["category"] == "mean-reversion"
    assert isinstance(data["known_weaknesses"], list)
    assert isinstance(data["risk_warnings"], list)


def test_render_identity_shows_every_declaration():
    text = render_identity(IDENTITIES["breakout"])
    assert "Rolling high/low breakout (breakout)" in text
    assert "version 1.0.0" in text
    assert "Author: Built-in" in text
    assert "Category: breakout" in text
    assert "Description:" in text
    assert "Known weaknesses:" in text
    assert "Risk warnings:" in text


def test_the_registry_survives_a_round_trip_with_the_category(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path, load=False)
    registry.export_registry(tmp_path / "registry.json")
    other = StrategyRegistry(storage_path=tmp_path, load=True)
    meta = {m.strategy_id: m for m in other.list_strategies()}
    assert meta["ma_crossover"].category == "trend-following"
