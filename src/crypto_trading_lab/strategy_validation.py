"""Strategy validation before a run (ROADMAP.md chapter 33.7).

A strategy that cannot work should say so *before* it burns a run, and a
strategy that can work but will not do what its author expects should say
so too. This module is the gate between "I have a strategy object" and
"the engine is allowed to spend candles on it".

The chapter lists eight checks; each one is a function of things the
strategy already declares, plus the data it is about to receive:

===============  ==========================================================
configuration    callable ``on_candle``, a name, a sane ``warmup_candles``
parameters       re-validated through the chapter 33.4 schema when given
indicators       a rule's longest indicator period must fit in the data
timeframe        one interval, in the expected form, matching the request
warm-up          the strategy must be able to emit at least one signal
market           ``BASE/QUOTE``, and the data must be for that market
rules            impossible or contradictory conditions are refused
warnings         everything above that is not fatal is reported, not hidden
===============  ==========================================================

Two rules of the house apply to the design itself:

* **Errors and warnings are different things.** An error means the run
  cannot produce a meaningful result (no candle will ever be enough for
  the warm-up). A warning means it can, but the user should know (the
  warm-up eats most of the sample). Collapsing them would make the gate
  either useless or infuriating.
* **Nothing here runs the strategy.** Validation reads what the strategy
  declares. Calling ``on_candle`` to "see if it works" would mutate its
  streaming state before the real run, which is exactly the kind of
  silent interference chapter 33.4 forbids.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, Sequence

from crypto_trading_lab.domain.models import Candle, Symbol
from crypto_trading_lab.market_requirements import (
    ENGINE_TRADING_MODE,
    MarketRequirements,
    TIMEFRAME_RE,
    market_requirements_for,
)
from crypto_trading_lab.rule_strategy import RuleStrategySpec, operand_indicator

__all__ = [
    "Severity",
    "ValidationIssue",
    "StrategyValidation",
    "StrategyValidationError",
    "validate_for_run",
    "TIMEFRAME_RE",
]

_COMPARISONS = (">", ">=", "<", "<=")
_NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?$")


class Severity(str, Enum):
    """How much an issue matters."""

    ERROR = "error"
    WARNING = "warning"


class StrategyValidationError(ValueError):
    """Raised when a strategy may not run."""

    def __init__(self, validation: "StrategyValidation") -> None:
        self.validation = validation
        super().__init__(validation.summary())


@dataclass(frozen=True)
class ValidationIssue:
    """One finding, with a stable code so callers can filter it."""

    severity: Severity
    code: str
    message: str

    def __str__(self) -> str:
        # The code is in the line on purpose: a report a user pastes into an
        # issue should say which check fired, not only what it saw.
        return f"{self.severity.value} [{self.code}]: {self.message}"

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class StrategyValidation:
    """Everything validation found, kept apart by severity."""

    issues: tuple[ValidationIssue, ...] = ()

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity is Severity.WARNING)

    @property
    def ok(self) -> bool:
        """True when the run may proceed (warnings do not block)."""
        return not self.errors

    def raise_for_errors(self) -> None:
        """Refuse to run, with every reason in one message."""
        if not self.ok:
            raise StrategyValidationError(self)

    def summary(self) -> str:
        """One line per finding, errors first."""
        lines = [str(issue) for issue in (*self.errors, *self.warnings)]
        if not lines:
            return "the strategy is valid for this run"
        return "\n".join(lines)

    def codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)


def validate_for_run(
    strategy: Any,
    *,
    candles: Optional[Sequence[Candle]] = None,
    market: Optional[str] = None,
    timeframe: Optional[str] = None,
    schema: Any = None,
    rule_spec: Optional[RuleStrategySpec] = None,
    market_requirements: Optional[MarketRequirements] = None,
) -> StrategyValidation:
    """Check a strategy against the data it is about to run on.

    ``candles`` may be ``None`` when the run is live and the amount of data
    is not known yet (paper trading): the length-dependent checks are then
    skipped instead of guessing. ``schema`` is the chapter 33.4
    :class:`~crypto_trading_lab.strategy_parameters.ParameterSchema` when the
    caller has one; parameters are normally already validated by the
    registry, so this is a second opinion rather than the gate.

    ``market_requirements`` is the chapter 33.2 record. When the caller does
    not pass one (the common case), it is looked up by the strategy's
    ``identifier`` — so built-in strategies are checked automatically and
    strategies without a record are simply skipped rather than rejected.
    """
    if market_requirements is None:
        market_requirements = market_requirements_for(
            getattr(strategy, "identifier", None)
        )
    issues: list[ValidationIssue] = []
    issues.extend(_check_configuration(strategy))
    issues.extend(_check_parameters(schema))
    issues.extend(_check_market(market, candles))
    issues.extend(_check_timeframe(timeframe, candles))
    if market_requirements is not None:
        issues.extend(
            _check_market_requirements(market_requirements, market, timeframe)
        )
    if candles is not None:
        issues.extend(_check_warmup(strategy, len(candles)))
        issues.extend(_check_indicators(strategy, rule_spec, len(candles)))
    if rule_spec is not None:
        issues.extend(_check_rules(rule_spec))
    return StrategyValidation(tuple(issues))


# -- the individual checks ---------------------------------------------------


def _error(code: str, message: str) -> ValidationIssue:
    return ValidationIssue(Severity.ERROR, code, message)


def _warning(code: str, message: str) -> ValidationIssue:
    return ValidationIssue(Severity.WARNING, code, message)


def _check_configuration(strategy: Any) -> list[ValidationIssue]:
    """The minimum a strategy must be to be callable at all."""
    issues: list[ValidationIssue] = []
    if not callable(getattr(strategy, "on_candle", None)):
        issues.append(
            _error(
                "configuration",
                "the strategy has no callable on_candle(index, candles); "
                "the engine cannot ask it for a decision",
            )
        )
    name = getattr(strategy, "name", "")
    if not str(name).strip():
        issues.append(
            _warning(
                "configuration",
                "the strategy has no name; reports and signals will be "
                "harder to read",
            )
        )
    warmup = getattr(strategy, "warmup_candles", None)
    if warmup is None:
        issues.append(
            _warning(
                "configuration",
                "the strategy does not declare warmup_candles; the run cannot "
                "warn when the sample is too short for it",
            )
        )
    elif not isinstance(warmup, int) or isinstance(warmup, bool) or warmup < 0:
        issues.append(
            _error(
                "configuration",
                f"warmup_candles must be a non-negative integer, got {warmup!r}",
            )
        )
    return issues


def _check_market_requirements(
    requirements: MarketRequirements,
    market: Optional[str],
    timeframe: Optional[str],
) -> list[ValidationIssue]:
    """Chapter 33.2: the strategy's stated needs versus what it is given.

    These are *declaration* checks. None of them runs the strategy: they
    compare what the strategy said it needs against the market and timeframe
    the caller provided. The minimum-sample gate is deliberately *not* here:
    a parametrised strategy's true minimum is its ``warmup_candles`` (which
    depends on the parameters), so chapter 33.7's warm-up check owns that
    gate and stays correct for every configuration. ``min_data_required`` is
    therefore a documented figure for the default configuration, not a
    second floor. The deeper check — that ``indicator_values()`` actually
    returns the indicators a strategy lists — lives in the test suite,
    because verifying it at runtime would mean calling into the strategy's
    streaming state before the real run (chapter 33.7 forbids that).
    """
    issues: list[ValidationIssue] = []

    # The engine can only trade one asset type today. A strategy that does
    # not include it cannot run here, and saying so beats a mid-run surprise.
    if ENGINE_TRADING_MODE not in requirements.asset_types:
        issues.append(
            _error(
                "market",
                f"the strategy supports {', '.join(requirements.asset_types)} "
                f"but the engine only trades {ENGINE_TRADING_MODE}; it cannot "
                "run in this program",
            )
        )

    # A strategy may restrict itself to named markets. "any" means it accepts
    # every market of a supported asset type, so there is nothing to check.
    # A malformed market is already an error from ``_check_market``; only
    # compare once the symbol string is known to parse.
    if market is not None and "any" not in requirements.compatible_markets:
        try:
            requested = str(Symbol(market))
        except (TypeError, ValueError):
            requested = None
        if requested is not None and requested not in requirements.compatible_markets:
            issues.append(
                _error(
                    "market",
                    f"the strategy is restricted to "
                    f"{', '.join(requirements.compatible_markets)} but was asked "
                    f"to run on {market}",
                )
            )

    # A strategy tuned for one interval is a warning, not a refusal — it may
    # still behave, just not as designed.
    if (
        timeframe is not None
        and requirements.required_timeframe is not None
        and timeframe != requirements.required_timeframe
    ):
        issues.append(
            _warning(
                "market",
                f"the strategy is designed for {requirements.required_timeframe} "
                f"but was asked to run on {timeframe}; its parameters may not "
                "fit the interval",
            )
        )

    return issues


def _check_parameters(schema: Any) -> list[ValidationIssue]:
    """Chapter 33.4 validation, when the caller supplies the schema."""
    if schema is None:
        return []
    try:
        schema.validate()
    except (TypeError, ValueError) as exc:
        return [_error("parameters", f"invalid parameters: {exc}")]
    return []


def _check_market(
    market: Optional[str], candles: Optional[Sequence[Candle]]
) -> list[ValidationIssue]:
    """``BASE/QUOTE``, and the data must be for that market."""
    issues: list[ValidationIssue] = []
    requested: Optional[str] = None
    if market is not None:
        try:
            requested = str(Symbol(market))
        except (TypeError, ValueError) as exc:
            issues.append(_error("market", f"invalid market {market!r}: {exc}"))
    if candles:
        data_market = str(candles[0].symbol)
        if requested is not None and data_market != requested:
            issues.append(
                _error(
                    "market",
                    f"the strategy was asked to run on {requested} but the "
                    f"data is for {data_market}",
                )
            )
        if len({str(c.symbol) for c in candles}) > 1:
            issues.append(
                _error(
                    "market",
                    "the data mixes more than one market; a run must use one",
                )
            )
    return issues


def _check_timeframe(
    timeframe: Optional[str], candles: Optional[Sequence[Candle]]
) -> list[ValidationIssue]:
    """One interval, in the project's grammar, matching the request."""
    issues: list[ValidationIssue] = []
    if timeframe is not None and not TIMEFRAME_RE.match(str(timeframe)):
        issues.append(
            _error(
                "timeframe",
                f"unsupported timeframe {timeframe!r}; use a count and one of "
                "s, m, h, d, w (for example 15m or 4h)",
            )
        )
    if candles:
        intervals = {c.interval for c in candles}
        if len(intervals) > 1:
            issues.append(
                _error(
                    "timeframe",
                    "the data mixes more than one interval "
                    f"({', '.join(sorted(intervals))}); a run must use one",
                )
            )
        elif timeframe is not None and intervals != {str(timeframe)}:
            issues.append(
                _error(
                    "timeframe",
                    f"the strategy was asked to run on {timeframe} but the "
                    f"data is {next(iter(intervals))}",
                )
            )
    return issues


def _check_warmup(strategy: Any, available: int) -> list[ValidationIssue]:
    """A warm-up longer than the sample means no signal, ever."""
    warmup = getattr(strategy, "warmup_candles", 0)
    if not isinstance(warmup, int) or isinstance(warmup, bool) or warmup <= 0:
        return []
    if available <= warmup:
        return [
            _error(
                "warmup",
                f"the strategy needs {warmup} candles before its first signal "
                f"and the run has {available}: it can never act",
            )
        ]
    if available < 2 * warmup:
        return [
            _warning(
                "warmup",
                f"the warm-up eats {warmup} of {available} candles, so most of "
                "the sample cannot contain a trade",
            )
        ]
    return []


def _check_indicators(
    strategy: Any,
    rule_spec: Optional[RuleStrategySpec],
    available: int,
) -> list[ValidationIssue]:
    """Required indicators must be able to fill, and must be recordable."""
    issues: list[ValidationIssue] = []
    if rule_spec is not None:
        longest = _longest_indicator_period(rule_spec)
        if longest is not None and longest[1] >= available:
            name, period = longest
            issues.append(
                _error(
                    "indicators",
                    f"the rule uses {name}({period}) and the run has "
                    f"{available} candles: the indicator can never be ready",
                )
            )
    if not hasattr(strategy, "indicator_values"):
        issues.append(
            _warning(
                "indicators",
                "the strategy does not expose indicator_values(), so its "
                "signals cannot record the values behind the decision "
                "(chapter 33.5)",
            )
        )
    return issues


def _longest_indicator_period(
    rule_spec: RuleStrategySpec,
) -> Optional[tuple[str, int]]:
    """The slowest indicator a rule reads, if it reads any."""
    longest: Optional[tuple[str, int]] = None
    for condition in (*rule_spec.entry, *rule_spec.exit):
        for operand in (condition.left, condition.right):
            found = operand_indicator(operand)
            if found is None:
                continue
            if longest is None or found[1] > longest[1]:
                longest = found
    return longest


def _check_rules(rule_spec: RuleStrategySpec) -> list[ValidationIssue]:
    """Impossible or contradictory conditions, refused before the run."""
    issues: list[ValidationIssue] = []

    entry = {_key(c) for c in rule_spec.entry}
    exit_ = {_key(c) for c in rule_spec.exit}
    if exit_ and entry == exit_:
        issues.append(
            _error(
                "rules",
                "the entry and exit conditions are the same, so every candle "
                "would open and close the position at once",
            )
        )

    for condition in (*rule_spec.entry, *rule_spec.exit):
        if _is_constant(condition.left) and _is_constant(condition.right):
            issues.append(
                _error(
                    "rules",
                    f"the condition {condition.left} {condition.operator} "
                    f"{condition.right} compares two constants: it is always "
                    "true or always false, never a decision",
                )
            )

    if rule_spec.entry_mode == "all":
        bound = _numeric_bounds(rule_spec.entry)
        for operand, (lower, upper) in bound.items():
            if lower is None or upper is None:
                continue
            low_value, low_operator = lower
            high_value, high_operator = upper
            if low_value > high_value or (
                low_value == high_value
                and (low_operator in (">", "<") or high_operator in (">", "<"))
            ):
                issues.append(
                    _error(
                        "rules",
                        f"the entry conditions on {operand} cannot all be true "
                        f"at once ({operand} {low_operator} {low_value} and "
                        f"{operand} {high_operator} {high_value})",
                    )
                )

    if not rule_spec.exit and (
        rule_spec.stop_loss_fraction is None
        and rule_spec.take_profit_fraction is None
    ):
        issues.append(
            _warning(
                "rules",
                "the rule has no exit condition and no stop-loss or "
                "take-profit, so a position would never be closed",
            )
        )
    return issues


def _key(condition: Any) -> tuple[str, str, str]:
    return (str(condition.left), str(condition.operator), str(condition.right))


def _is_constant(operand: str) -> bool:
    return bool(_NUMBER_RE.match(str(operand).strip()))


def _numeric_bounds(
    conditions: Sequence[Any],
) -> dict[str, tuple[Optional[tuple[Decimal, str]], Optional[tuple[Decimal, str]]]]:
    """Per operand, the tightest lower and upper bound the conditions imply.

    Returns ``{operand: ((value, operator), (value, operator))}`` where either
    side may be ``None``. Only conditions of the form ``operand > number`` are
    considered: a comparison between two indicators has no fixed bound to
    compare.
    """
    bounds: dict[str, list[Any]] = {}
    for condition in conditions:
        if condition.operator not in _COMPARISONS:
            continue
        if _is_constant(condition.left) or not _is_constant(condition.right):
            continue
        operand = str(condition.left)
        value = Decimal(str(condition.right))
        strict = condition.operator in (">", "<")
        lower, upper = bounds.setdefault(operand, [None, None])
        if condition.operator in (">", ">="):
            if lower is None or value > lower[0] or (value == lower[0] and strict):
                bounds[operand][0] = (value, condition.operator)
        else:
            if upper is None or value < upper[0] or (value == upper[0] and strict):
                bounds[operand][1] = (value, condition.operator)
    return {operand: (values[0], values[1]) for operand, values in bounds.items()}
