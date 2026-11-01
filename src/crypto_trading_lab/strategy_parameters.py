"""Strategy parameters (ROADMAP.md chapter 33.4).

A strategy's parameters are a *contract*, not a bag of kwargs. Chapter 33.4
asks every configurable parameter to declare its name, type, default,
bounds, allowed values, description and validation rules, and asks the
program to reject an invalid combination **before** execution instead of
letting a strategy fail halfway through a backtest.

Three types, in the order they are used:

``ParameterSpec``
    one parameter: what it accepts, what it defaults to, and what makes a
    value invalid.
``ParameterSchema``
    the set of specs a strategy version declares, plus the cross-parameter
    rules that no single spec can express (``fast < slow``, ``oversold <
    overbought``).
``ParameterSet``
    the validated values, frozen, with a ``signature()`` that records exactly
    which parameters ran. Parameters must never change silently during a
    backtest or a live session, and an immutable object is the simplest way
    to make that impossible rather than merely discouraged.

The serialised form of a schema is the same dictionary shape the registry
has always stored (``{"type": "int", "min": 1, "max": 200, ...}``), so
existing registry files keep working. Combination rules are Python callables
and therefore do not survive a JSON round trip: an imported strategy is
validated parameter by parameter, and the registry says so.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional, Sequence

__all__ = [
    "ParameterError",
    "ParameterType",
    "ParameterSpec",
    "CombinationRule",
    "ParameterSchema",
    "ParameterSet",
]


class ParameterError(ValueError):
    """A parameter value, or a combination of them, cannot be used."""


class ParameterType(str, Enum):
    """The value kinds a parameter can declare."""

    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STR = "str"
    CHOICE = "choice"


_TRUE = {"true", "yes", "1", "on"}
_FALSE = {"false", "no", "0", "off"}


@dataclass(frozen=True)
class ParameterSpec:
    """One declared parameter (chapter 33.4)."""

    name: str
    kind: ParameterType
    default: Any
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    allowed: tuple[Any, ...] = ()
    description: str = ""
    #: Human-readable validation rule, for the UI and the docs. The checks
    #: themselves are the bounds and the allowed values above.
    rule: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ParameterError("a parameter needs a name")
        # ``kind`` is declared as the enum, but the registry's JSON form says
        # "int" and so does every caller writing a schema by hand. Coercing it
        # here means a plain string works, while an unknown one fails at the
        # declaration instead of silently falling through ``coerce()``.
        if not isinstance(self.kind, ParameterType):
            try:
                object.__setattr__(self, "kind", ParameterType(str(self.kind)))
            except ValueError as error:
                known = ", ".join(kind.value for kind in ParameterType)
                raise ParameterError(
                    f"{self.name}: unknown type {self.kind!r}; use one of {known}"
                ) from error
        if self.kind is ParameterType.CHOICE and not self.allowed:
            raise ParameterError(
                f"{self.name}: a choice parameter needs the values it allows"
            )
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise ParameterError(
                f"{self.name}: minimum {self.minimum} is above maximum "
                f"{self.maximum}"
            )
        # The default is validated like any other value: a default that the
        # spec itself would reject is a bug, not a default.
        self.coerce(self.default)

    # -- conversion ------------------------------------------------------

    def coerce(self, value: Any) -> Any:
        """Return `value` as this parameter's type, or raise."""
        if value is None:
            raise ParameterError(f"{self.name}: a value is required")

        if self.kind is ParameterType.INT:
            if isinstance(value, bool):
                raise ParameterError(f"{self.name}: expected a whole number")
            if isinstance(value, float) and not value.is_integer():
                raise ParameterError(
                    f"{self.name}: expected a whole number, got {value!r}"
                )
            if isinstance(value, str) and "." in value:
                raise ParameterError(
                    f"{self.name}: expected a whole number, got {value!r}"
                )
            try:
                number = int(value)
            except (TypeError, ValueError) as error:
                raise ParameterError(
                    f"{self.name}: expected a whole number, got {value!r}"
                ) from error
            return self._check_bounds(number)

        if self.kind is ParameterType.FLOAT:
            if isinstance(value, bool):
                raise ParameterError(f"{self.name}: expected a number")
            try:
                number = float(value)
            except (TypeError, ValueError) as error:
                raise ParameterError(
                    f"{self.name}: expected a number, got {value!r}"
                ) from error
            return self._check_bounds(number)

        if self.kind is ParameterType.BOOL:
            if isinstance(value, bool):
                return value
            if isinstance(value, int) and value in (0, 1):
                return bool(value)
            if isinstance(value, str):
                text = value.strip().lower()
                if text in _TRUE:
                    return True
                if text in _FALSE:
                    return False
            raise ParameterError(
                f"{self.name}: expected true or false, got {value!r}"
            )

        if self.kind is ParameterType.STR:
            if not isinstance(value, str):
                raise ParameterError(
                    f"{self.name}: expected text, got {value!r}"
                )
            return value

        # CHOICE
        if value in self.allowed:
            return value
        for candidate in self.allowed:
            if isinstance(candidate, int) and not isinstance(candidate, bool):
                try:
                    if int(value) == candidate:
                        return candidate
                except (TypeError, ValueError):
                    pass
        raise ParameterError(
            f"{self.name}: {value!r} is not one of "
            f"{', '.join(repr(v) for v in self.allowed)}"
        )

    def _check_bounds(self, number: float) -> Any:
        if self.minimum is not None and number < self.minimum:
            raise ParameterError(
                f"{self.name} must be at least {_format_number(self.minimum)}"
            )
        if self.maximum is not None and number > self.maximum:
            raise ParameterError(
                f"{self.name} must be at most {_format_number(self.maximum)}"
            )
        return number

    # -- serialisation ---------------------------------------------------

    def to_dict(self) -> dict:
        data: dict[str, Any] = {
            "type": self.kind.value,
            "default": self.default,
            "description": self.description,
        }
        if self.minimum is not None:
            data["min"] = self.minimum
        if self.maximum is not None:
            data["max"] = self.maximum
        if self.allowed:
            data["allowed"] = list(self.allowed)
        if self.rule:
            data["rule"] = self.rule
        return data

    @classmethod
    def from_dict(cls, name: str, data: Mapping[str, Any]) -> "ParameterSpec":
        kind = str(data.get("type", "int")).lower()
        try:
            parameter_type = ParameterType(kind)
        except ValueError as error:
            raise ParameterError(
                f"{name}: unknown parameter type {kind!r}; use one of "
                f"{', '.join(t.value for t in ParameterType)}"
            ) from error
        allowed = data.get("allowed") or data.get("choices") or ()
        return cls(
            name=name,
            kind=parameter_type,
            default=data.get("default"),
            minimum=data.get("min"),
            maximum=data.get("max"),
            allowed=tuple(allowed),
            description=str(data.get("description", "")),
            rule=str(data.get("rule", "")),
        )


def _format_number(value: float) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


@dataclass(frozen=True)
class CombinationRule:
    """A rule about two or more parameters together (chapter 33.4).

    ``check`` receives the complete, already-coerced parameter dictionary and
    returns the problem in one sentence, or ``None`` when the combination is
    valid. Returning a sentence instead of raising keeps the caller in charge
    of the error type.
    """

    description: str
    check: Callable[[Mapping[str, Any]], Optional[str]]

    def __call__(self, values: Mapping[str, Any]) -> Optional[str]:
        return self.check(values)


@dataclass(frozen=True)
class ParameterSchema:
    """Every parameter one strategy version declares (chapter 33.4)."""

    specs: tuple[ParameterSpec, ...] = ()
    rules: tuple[CombinationRule, ...] = ()

    def __post_init__(self) -> None:
        names = [spec.name for spec in self.specs]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            raise ParameterError(
                f"declared twice: {', '.join(sorted(duplicates))}"
            )

    # -- lookups ---------------------------------------------------------

    def __len__(self) -> int:
        return len(self.specs)

    def __iter__(self):
        return iter(self.specs)

    def get(self, name: str) -> Optional[ParameterSpec]:
        for spec in self.specs:
            if spec.name == name:
                return spec
        return None

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(spec.name for spec in self.specs)

    def defaults(self) -> dict[str, Any]:
        return {spec.name: spec.default for spec in self.specs}

    # -- validation ------------------------------------------------------

    def validate(self, values: Optional[Mapping[str, Any]] = None) -> dict:
        """Return the complete, coerced parameter dictionary.

        Missing parameters take their declared default. Unknown names,
        out-of-range values and invalid combinations raise
        :class:`ParameterError` — this is the gate chapter 33.4 asks for
        before execution.
        """
        given = dict(values or {})
        unknown = sorted(set(given) - set(self.names))
        if unknown:
            declared = ", ".join(self.names) or "none"
            raise ParameterError(
                f"unknown parameter(s): {', '.join(unknown)}; this strategy "
                f"declares: {declared}"
            )

        complete: dict[str, Any] = {}
        for spec in self.specs:
            complete[spec.name] = spec.coerce(
                given.get(spec.name, spec.default)
            )

        for rule in self.rules:
            problem = rule(complete)
            if problem:
                raise ParameterError(problem)
        return complete

    # -- serialisation ---------------------------------------------------

    def to_mapping(self) -> dict[str, dict]:
        """The dictionary form the registry stores and exports."""
        return {spec.name: spec.to_dict() for spec in self.specs}

    @classmethod
    def from_mapping(
        cls,
        mapping: Optional[Mapping[str, Mapping[str, Any]]] = None,
        *,
        rules: Sequence[CombinationRule] = (),
    ) -> "ParameterSchema":
        specs = tuple(
            ParameterSpec.from_dict(name, data)
            for name, data in (mapping or {}).items()
        )
        return cls(specs=specs, rules=tuple(rules))

    def describe(self) -> str:
        """One line per parameter, for the UI and the docs."""
        lines = []
        for spec in self.specs:
            bounds = []
            if spec.minimum is not None:
                bounds.append(f"min {_format_number(spec.minimum)}")
            if spec.maximum is not None:
                bounds.append(f"max {_format_number(spec.maximum)}")
            if spec.allowed:
                bounds.append(
                    "one of " + ", ".join(str(v) for v in spec.allowed)
                )
            limits = f" ({'; '.join(bounds)})" if bounds else ""
            lines.append(
                f"{spec.name}: {spec.kind.value}, default "
                f"{spec.default!r}{limits} — {spec.description}"
            )
        lines.extend(f"rule: {rule.description}" for rule in self.rules)
        return "\n".join(lines)


@dataclass(frozen=True)
class ParameterSet:
    """The validated parameters one strategy version ran with.

    Frozen, and its mapping cannot be written to: chapter 33.4 forbids
    parameters changing silently during a backtest or a live session, and an
    immutable object enforces that instead of trusting every caller.
    """

    strategy_id: str
    version: str
    values: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.strategy_id.strip():
            raise ParameterError("a parameter set needs a strategy id")
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))

    def __getitem__(self, name: str) -> Any:
        return self.values[name]

    def get(self, name: str, default: Any = None) -> Any:
        return self.values.get(name, default)

    def as_dict(self) -> dict[str, Any]:
        return dict(self.values)

    def signature(self) -> str:
        """What ran, in one auditable string.

        ``ma_crossover@1.0.0(fast=5, slow=20)`` — recorded with a backtest so
        a result can always be traced back to the parameters that produced
        it, and so a silent change is visible rather than assumed.
        """
        ordered = ", ".join(
            f"{name}={self.values[name]!r}" for name in sorted(self.values)
        )
        return f"{self.strategy_id}@{self.version}({ordered})"
