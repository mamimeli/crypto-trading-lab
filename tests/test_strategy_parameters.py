"""Tests for strategy parameters (ROADMAP.md chapter 33.4).

The chapter asks for a declared contract per parameter — name, type, default,
bounds, allowed values, description, validation rules — and for invalid
combinations to be rejected *before* execution. It also forbids parameters
changing silently during a run, which is why the validated set is immutable.
"""

from __future__ import annotations

import pytest

from crypto_trading_lab.strategy_parameters import (
    CombinationRule,
    ParameterError,
    ParameterSchema,
    ParameterSet,
    ParameterSpec,
    ParameterType,
)
from crypto_trading_lab.strategy_registry import StrategyRegistry


def _spec(**kwargs) -> ParameterSpec:
    defaults = dict(
        name="period",
        kind=ParameterType.INT,
        default=14,
        minimum=1,
        maximum=200,
        description="Lookback",
    )
    defaults.update(kwargs)
    return ParameterSpec(**defaults)


# -- one parameter -----------------------------------------------------------


def test_a_whole_number_is_accepted_and_coerced():
    assert _spec().coerce(20) == 20
    assert _spec().coerce("20") == 20
    assert _spec().coerce(20.0) == 20


def test_a_string_kind_is_coerced_and_an_unknown_one_is_refused():
    """Schemas are written by hand and stored as JSON, where the kind is
    ``"int"``; an unknown name must fail at the declaration, not later
    inside ``coerce()`` where it looked like an allowed-values problem."""
    assert _spec(kind="int").kind is ParameterType.INT
    with pytest.raises(ParameterError, match="unknown type"):
        _spec(kind="integer")


def test_a_fractional_number_is_not_a_whole_number():
    with pytest.raises(ParameterError, match="whole number"):
        _spec().coerce(2.5)


def test_a_boolean_is_not_a_number():
    """`True` is an `int` in Python; accepting it here would be a bug."""
    with pytest.raises(ParameterError, match="whole number"):
        _spec().coerce(True)


def test_text_that_is_not_a_number_is_rejected():
    with pytest.raises(ParameterError, match="whole number"):
        _spec().coerce("fast")


def test_the_bounds_are_enforced_with_a_readable_message():
    with pytest.raises(ParameterError, match="at least 1"):
        _spec().coerce(0)
    with pytest.raises(ParameterError, match="at most 200"):
        _spec().coerce(201)


def test_a_default_the_spec_itself_rejects_is_a_bug_not_a_default():
    with pytest.raises(ParameterError, match="at most 200"):
        _spec(default=500)


def test_a_parameter_without_a_default_is_rejected():
    """Chapter 33.4 requires every parameter to declare one."""
    with pytest.raises(ParameterError, match="a value is required"):
        _spec(default=None)


def test_minimum_above_maximum_is_rejected():
    with pytest.raises(ParameterError, match="above maximum"):
        _spec(minimum=10, maximum=5)


def test_a_choice_only_accepts_its_declared_values():
    spec = ParameterSpec(
        name="mode",
        kind=ParameterType.CHOICE,
        default="trend",
        allowed=("trend", "range"),
    )
    assert spec.coerce("range") == "range"
    with pytest.raises(ParameterError, match="not one of"):
        spec.coerce("scalp")


def test_a_choice_needs_values_to_choose_from():
    with pytest.raises(ParameterError, match="needs the values"):
        ParameterSpec(name="mode", kind=ParameterType.CHOICE, default="x")


def test_numeric_choices_accept_numeric_text():
    spec = ParameterSpec(
        name="level", kind=ParameterType.CHOICE, default=1, allowed=(1, 2, 3)
    )
    assert spec.coerce("2") == 2


def test_a_boolean_accepts_the_usual_spellings():
    spec = ParameterSpec(name="flag", kind=ParameterType.BOOL, default=False)
    assert spec.coerce("true") is True
    assert spec.coerce("no") is False
    assert spec.coerce(1) is True
    with pytest.raises(ParameterError, match="true or false"):
        spec.coerce("maybe")


def test_text_parameters_reject_numbers():
    spec = ParameterSpec(name="tag", kind=ParameterType.STR, default="a")
    assert spec.coerce("b") == "b"
    with pytest.raises(ParameterError, match="expected text"):
        spec.coerce(3)


def test_the_spec_round_trips_through_its_dictionary_form():
    original = _spec(rule="period must be at least 1")
    restored = ParameterSpec.from_dict("period", original.to_dict())

    assert restored == original


def test_an_unknown_type_is_named_in_the_error():
    with pytest.raises(ParameterError, match="unknown parameter type"):
        ParameterSpec.from_dict("x", {"type": "money", "default": 1})


# -- a whole schema ----------------------------------------------------------


def _schema(rules=()) -> ParameterSchema:
    return ParameterSchema(
        specs=(
            ParameterSpec(
                name="fast", kind=ParameterType.INT, default=10, minimum=1
            ),
            ParameterSpec(
                name="slow", kind=ParameterType.INT, default=30, minimum=1
            ),
        ),
        rules=rules,
    )


def test_missing_parameters_take_their_default():
    assert _schema().validate({}) == {"fast": 10, "slow": 30}


def test_validation_coerces_before_it_checks_combinations():
    """`"40"` must be compared as 40, not as text."""
    assert _schema().validate({"fast": "5", "slow": "40"}) == {
        "fast": 5,
        "slow": 40,
    }


def test_an_unknown_parameter_is_rejected_and_the_declared_ones_are_listed():
    with pytest.raises(ParameterError, match="unknown parameter"):
        _schema().validate({"fats": 5})


def test_a_combination_rule_rejects_an_impossible_pair():
    rule = CombinationRule(
        "fast < slow",
        lambda values: "fast must be smaller" if values["fast"] >= values["slow"] else None,
    )
    schema = _schema(rules=(rule,))

    with pytest.raises(ParameterError, match="fast must be smaller"):
        schema.validate({"fast": 30, "slow": 10})


def test_a_combination_rule_sees_the_complete_dictionary():
    """It must see defaults too, or a half-specified pair slips through."""
    seen = {}

    def check(values):
        seen.update(values)
        return None

    _schema(rules=(CombinationRule("inspect", check),)).validate({"fast": 5})

    assert seen == {"fast": 5, "slow": 30}


def test_a_duplicated_name_is_rejected():
    with pytest.raises(ParameterError, match="declared twice"):
        ParameterSchema(specs=(_spec(), _spec()))


def test_the_schema_round_trips_through_the_registry_form():
    schema = _schema()
    restored = ParameterSchema.from_mapping(schema.to_mapping())

    assert restored.names == schema.names
    assert restored.defaults() == schema.defaults()


def test_the_description_lists_every_parameter():
    text = _schema().describe()

    assert "fast" in text and "slow" in text
    assert "default 10" in text


# -- the validated set -------------------------------------------------------


def test_a_parameter_set_cannot_be_written_to():
    """Chapter 33.4: parameters never change silently during a run."""
    params = ParameterSet("ma_crossover", "1.0.0", {"fast": 5, "slow": 20})

    with pytest.raises(TypeError):
        params.values["fast"] = 99
    with pytest.raises(Exception):
        params.version = "2.0.0"


def test_the_signature_says_exactly_what_ran():
    params = ParameterSet("ma_crossover", "1.0.0", {"slow": 20, "fast": 5})

    assert params.signature() == "ma_crossover@1.0.0(fast=5, slow=20)"


def test_a_parameter_set_needs_a_strategy_id():
    with pytest.raises(ParameterError, match="strategy id"):
        ParameterSet("  ", "1.0.0", {})


# -- the registry is the gate ------------------------------------------------


def test_the_registry_coerces_before_building_the_strategy(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path / "registry")

    strategy = registry.create_instance("ma_crossover", fast="5", slow="20")

    assert strategy.fast == 5 and strategy.slow == 20


def test_the_registry_rejects_an_impossible_pair_before_execution(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path / "registry")

    with pytest.raises(ParameterError, match="fast must be smaller than slow"):
        registry.create_instance("ma_crossover", fast=30, slow=10)


def test_the_registry_rejects_an_inverted_rsi_threshold(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path / "registry")

    with pytest.raises(ParameterError, match="oversold must be smaller"):
        registry.create_instance("rsi", oversold=80, overbought=20)


def test_a_typo_is_rejected_instead_of_ignored(tmp_path):
    """A misspelt parameter used to be swallowed by the factory signature."""
    registry = StrategyRegistry(storage_path=tmp_path / "registry")

    with pytest.raises(ParameterError, match="unknown parameter"):
        registry.create_instance("buy_and_hold", periods=10)


def test_an_out_of_range_value_is_rejected_with_the_bound(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path / "registry")

    with pytest.raises(ParameterError, match="at most 200"):
        registry.create_instance("ma_crossover", fast=500)


def test_the_registry_hands_out_a_frozen_parameter_set(tmp_path):
    registry = StrategyRegistry(storage_path=tmp_path / "registry")

    params = registry.parameter_set("rsi", period=5)

    assert params.version == "1.0.0"
    assert params["period"] == 5
    assert params["oversold"] == 30  # the declared default
    assert params.signature().startswith("rsi@1.0.0(")


def test_a_reloaded_strategy_keeps_its_parameter_checks(tmp_path):
    """Built-ins are re-registered on load, so their rules survive."""
    registry = StrategyRegistry(storage_path=tmp_path / "registry")
    reloaded = StrategyRegistry(storage_path=tmp_path / "registry")

    with pytest.raises(ParameterError, match="fast must be smaller than slow"):
        reloaded.create_instance("ma_crossover", fast=30, slow=10)
    assert registry.get("ma_crossover").metadata.parameter_schema is not None
