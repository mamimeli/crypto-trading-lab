"""Tests for Strategy Registry (ROADMAP chapter 36)."""

from __future__ import annotations

from pathlib import Path
from crypto_trading_lab.strategy_registry import StrategyRegistry
from crypto_trading_lab.backtesting.engine import MACrossoverStrategy


def test_registry_loads_builtins(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path)
    strategies = registry.list_strategies()
    assert len(strategies) >= 3
    
    ids = [s.strategy_id for s in strategies]
    assert "ma_crossover" in ids
    assert "buy_and_hold" in ids
    assert "null_strategy" in ids


def test_registry_create_instance(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path)
    strategy = registry.create_instance("ma_crossover", fast=5, slow=15)
    assert isinstance(strategy, MACrossoverStrategy)
    assert strategy.fast == 5
    assert strategy.slow == 15


def test_every_builtin_strategy_knows_its_registry_id(tmp_path):
    """Chapter 33.5 stamps the identifier on every signal.

    ``Strategy.name`` is a sentence that changes with the parameters
    ("SMA(5)xSMA(15) crossover"), so it cannot be the identifier. Each
    built-in declares its own, and this test keeps the declaration and the
    registry entry from drifting apart.
    """
    registry = StrategyRegistry(storage_path=tmp_path)

    for metadata in registry.list_strategies():
        if metadata.author != "Built-in":
            continue
        instance = registry.create_instance(metadata.strategy_id)
        assert instance.identifier == metadata.strategy_id


def test_constructing_a_registry_does_not_write_to_disk(tmp_path, monkeypatch):
    """Building a registry is read-only, whatever the working directory is.

    It used to create ``data/strategy_registry/registry.json`` next to
    whatever directory the process started in — including the source tree.
    """
    monkeypatch.chdir(tmp_path)

    registry = StrategyRegistry()  # default storage path: ./data/..., under the cwd

    assert not (tmp_path / "data").exists()
    # It is still fully usable in memory.
    assert registry.create_instance("buy_and_hold") is not None

    # The file appears only once something is actually registered.
    registry.register(
        strategy_id="custom_demo",
        factory=MACrossoverStrategy,
        name="Custom Demo",
        version="0.1.0",
        author="tests",
        description="Registered by the test suite.",
        parameters_schema={},
    )
    assert (tmp_path / "data" / "strategy_registry" / "registry.json").exists()


def test_reload_keeps_builtin_factories_and_flags_metadata_only_entries(tmp_path):
    """A reloaded registry is honest about what it cannot run.

    Built-ins keep the Python factories bound at construction; strategies
    that came from JSON are metadata only, because a factory is a live
    callable that JSON cannot carry.
    """
    first = StrategyRegistry(storage_path=tmp_path)
    first.register(
        strategy_id="custom_demo",
        factory=MACrossoverStrategy,
        name="Custom Demo",
        version="0.1.0",
        author="tests",
        description="Registered by the test suite.",
        parameters_schema={},
    )
    assert (tmp_path / "registry.json").exists()

    reloaded = StrategyRegistry(storage_path=tmp_path)

    ids = [s.strategy_id for s in reloaded.list_strategies()]
    assert "custom_demo" in ids
    # Built-ins survive with a usable factory...
    assert reloaded.get_factory("ma_crossover") is not None
    assert isinstance(reloaded.create_instance("ma_crossover"), MACrossoverStrategy)
    # ...while the JSON-only entry is listed but cannot be instantiated.
    assert reloaded.get_factory("custom_demo") is None
    assert reloaded.create_instance("custom_demo") is None


def test_reload_without_a_previous_file_is_a_no_op(tmp_path):
    """An empty storage path must not raise (first run of a fresh install)."""
    registry = StrategyRegistry(storage_path=tmp_path / "does-not-exist-yet")
    assert registry.create_instance("null_strategy") is not None
    assert not (tmp_path / "does-not-exist-yet").exists()
