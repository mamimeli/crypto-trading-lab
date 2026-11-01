"""Strategy complexity control (ROADMAP.md chapter 35).

Two different questions live here, and mixing them up is how a project ends
up measuring the wrong thing:

* **Code complexity** (:class:`ComplexityAnalyzer`) asks whether the Python
  class that implements a strategy is hard to maintain: cyclomatic
  complexity, Halstead volume, maintainability index. It is about *our*
  code, not about the strategy.
* **Strategy complexity** (:class:`StrategyComplexity`) is what chapter 35
  asks for: how many parameters, rules, indicators, filters and conditions
  a strategy *version* declares, how large the parameter grid is, and how
  big any machine-learning model is. This is the number that matters for
  overfitting, and it is the one qualification and reports must show.

Neither measurement promises anything: a simple strategy is not good, and a
complex one is not bad. Complexity is one input among many.
"""

from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Mapping, Optional, Set

from crypto_trading_lab.backtesting.engine import Strategy
from crypto_trading_lab.rule_strategy import RuleStrategySpec, operand_indicator


class ComplexityLevel(Enum):
    """Complexity level classification."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass(frozen=True)
class ComplexityMetrics:
    """Complexity metrics for a strategy."""
    cyclomatic_complexity: int
    lines_of_code: int
    num_parameters: int
    num_functions: int
    num_classes: int
    max_nesting_depth: int
    halstead_volume: float
    maintainability_index: float


@dataclass(frozen=True)
class ComplexityLimits:
    """Complexity limits configuration (35.1)."""
    max_cyclomatic: int = 10
    max_lines: int = 200
    max_parameters: int = 8
    max_functions: int = 10
    max_classes: int = 3
    max_nesting: int = 4
    max_halstead_volume: float = 1000.0
    min_maintainability: float = 20.0


@dataclass(frozen=True)
class ComplexityReport:
    """Complexity analysis report (35.2)."""
    metrics: ComplexityMetrics
    level: ComplexityLevel
    passed: bool
    violations: list[str]
    warnings: list[str]


class ComplexityAnalyzer:
    """
    Analyzes strategy complexity to prevent overfitting and ensure maintainability (Chapter 35).
    """

    def __init__(self, limits: ComplexityLimits = None):
        self.limits = limits or ComplexityLimits()

    def analyze_strategy(self, strategy_class: type) -> ComplexityReport:
        """Analyze a strategy class for complexity."""
        source = inspect.getsource(strategy_class)
        tree = ast.parse(source)

        # Find the strategy class definition
        strategy_class_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == strategy_class.__name__:
                strategy_class_node = node
                break

        if not strategy_class_node:
            raise ValueError(f"Could not find class {strategy_class.__name__}")

        # Calculate metrics
        metrics = self._calculate_metrics(strategy_class_node, source)

        # Evaluate against limits
        violations = []
        warnings = []

        if metrics.cyclomatic_complexity > self.limits.max_cyclomatic:
            violations.append(f"Cyclomatic complexity {metrics.cyclomatic_complexity} exceeds limit {self.limits.max_cyclomatic}")

        if metrics.lines_of_code > self.limits.max_lines:
            violations.append(f"Lines of code {metrics.lines_of_code} exceeds limit {self.limits.max_lines}")

        if metrics.num_parameters > self.limits.max_parameters:
            violations.append(f"Number of parameters {metrics.num_parameters} exceeds limit {self.limits.max_parameters}")

        if metrics.num_functions > self.limits.max_functions:
            violations.append(f"Number of functions {metrics.num_functions} exceeds limit {self.limits.max_functions}")

        if metrics.max_nesting_depth > self.limits.max_nesting:
            violations.append(f"Max nesting depth {metrics.max_nesting_depth} exceeds limit {self.limits.max_nesting}")

        if metrics.halstead_volume > self.limits.max_halstead_volume:
            warnings.append(f"Halstead volume {metrics.halstead_volume:.1f} exceeds recommended limit {self.limits.max_halstead_volume}")

        if metrics.maintainability_index < self.limits.min_maintainability:
            warnings.append(f"Maintainability index {metrics.maintainability_index:.1f} below recommended {self.limits.min_maintainability}")

        # Determine complexity level
        level = self._classify_complexity(metrics)

        passed = len(violations) == 0

        return ComplexityReport(
            metrics=metrics,
            level=level,
            passed=passed,
            violations=violations,
            warnings=warnings,
        )

    def _calculate_metrics(self, class_node: ast.ClassDef, source: str) -> ComplexityMetrics:
        """Calculate complexity metrics from AST."""
        # Count lines of code
        lines = source.split('\n')
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])

        # Cyclomatic complexity
        cc = self._calculate_cyclomatic(class_node)

        # Count parameters (from __init__ or __post_init__)
        num_params = self._count_parameters(class_node)

        # Count functions
        num_functions = len([n for n in ast.walk(class_node) if isinstance(n, ast.FunctionDef)])

        # Count classes (nested)
        num_classes = len([n for n in ast.walk(class_node) if isinstance(n, ast.ClassDef)]) - 1

        # Max nesting depth
        max_nesting = self._max_nesting_depth(class_node)

        # Halstead volume (simplified)
        halstead_volume = self._halstead_volume(class_node)

        # Maintainability index (simplified)
        mi = self._maintainability_index(loc, cc, halstead_volume)

        return ComplexityMetrics(
            cyclomatic_complexity=cc,
            lines_of_code=loc,
            num_parameters=num_params,
            num_functions=num_functions,
            num_classes=num_classes,
            max_nesting_depth=max_nesting,
            halstead_volume=halstead_volume,
            maintainability_index=mi,
        )

    def _calculate_cyclomatic(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        cc = 1  # Base complexity
        for node in ast.walk(node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)):
                cc += 1
            elif isinstance(node, ast.BoolOp):
                cc += len(node.values) - 1
            elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                cc += 1
        return cc

    def _count_parameters(self, class_node: ast.ClassDef) -> int:
        """Count parameters in __init__ and __post_init__."""
        count = 0
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name in ('__init__', '__post_init__'):
                for arg in node.args.args:
                    if arg.arg != 'self':
                        count += 1
                for arg in node.args.kwonlyargs:
                    count += 1
        return count

    def _max_nesting_depth(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        current_depth = 0

        def walk(n, depth):
            nonlocal max_depth
            if isinstance(n, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try, ast.With, ast.AsyncWith)):
                depth += 1
                max_depth = max(max_depth, depth)
            elif isinstance(n, ast.FunctionDef):
                depth += 1
                max_depth = max(max_depth, depth)

            for child in ast.iter_child_nodes(n):
                walk(child, depth)

            if isinstance(n, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try, ast.With, ast.AsyncWith, ast.FunctionDef)):
                depth -= 1

        walk(node, 0)
        return max_depth

    def _halstead_volume(self, node: ast.AST) -> float:
        """Calculate simplified Halstead volume."""
        operators = 0
        operands = 0

        for node in ast.walk(node):
            if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp)):
                operators += 1
            elif isinstance(node, (ast.Name, ast.Constant, ast.Attribute, ast.Subscript)):
                operands += 1
            elif isinstance(node, (ast.Call, ast.Attribute)):
                operands += 1

        if operators == 0 or operands == 0:
            return 0.0

        n1 = operators  # distinct operators (simplified)
        n2 = operands   # distinct operands (simplified)
        N1 = operators  # total operators
        N2 = operands   # total operands

        # Volume = N * log2(n) where N = N1 + N2, n = n1 + n2
        import math
        N = N1 + N2
        n = 2  # simplified
        return N * math.log2(n) if n > 0 else 0.0

    def _maintainability_index(self, loc: int, cc: int, halstead: float) -> float:
        """Calculate maintainability index (simplified)."""
        import math
        if loc == 0 or cc == 0:
            return 100.0
        # MI = 171 - 5.2 * ln(Volume) - 0.23 * CC - 16.2 * ln(LOC)
        volume = max(halstead, 1)
        mi = 171 - 5.2 * math.log(volume) - 0.23 * cc - 16.2 * math.log(loc)
        return max(0, min(100, mi))

    def _classify_complexity(self, metrics: ComplexityMetrics) -> ComplexityLevel:
        """Classify complexity level."""
        score = 0
        score += metrics.cyclomatic_complexity
        score += metrics.lines_of_code // 20
        score += metrics.num_parameters * 2
        score += metrics.max_nesting_depth * 3

        if score <= 20:
            return ComplexityLevel.SIMPLE
        elif score <= 40:
            return ComplexityLevel.MODERATE
        elif score <= 60:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.VERY_COMPLEX


def analyze_strategy_complexity(
    strategy_class: type,
    limits: ComplexityLimits = None,
) -> ComplexityReport:
    """Convenience function to analyze strategy complexity."""
    analyzer = ComplexityAnalyzer(limits)
    return analyzer.analyze_strategy(strategy_class)


COMPLEXITY_CONTROL_WARNING = (
    "Complexity metrics are heuristics, not guarantees. "
    "Low complexity does not guarantee profitability. "
    "High complexity does not guarantee failure. "
    "Use as one input among many for strategy evaluation."
)


# ---------------------------------------------------------------------------
# Strategy complexity (chapter 35) — what a strategy version declares
# ---------------------------------------------------------------------------

#: Weights of the single comparable score. A parameter weighs most because
#: every one of them multiplies the number of configurations that were (or
#: could be) tried; an indicator or a filter weighs two because it adds a
#: whole comparison to every decision; a rule and a condition weigh one
#: because they are the same thing counted from two angles. The weights are
#: a stated convention, not a measurement — see the warning above.
PARAMETER_WEIGHT = 4
INDICATOR_WEIGHT = 2
FILTER_WEIGHT = 2
RULE_WEIGHT = 1
CONDITION_WEIGHT = 1


@dataclass(frozen=True)
class StrategyComplexity:
    """The complexity a strategy *version* declares (chapter 35).

    This is metadata, not a measurement of quality: two strategies with the
    same score can differ completely in how well they work.
    """

    num_parameters: int = 0
    num_rules: int = 0
    num_indicators: int = 0
    num_filters: int = 0
    num_conditions: int = 0
    optimization_complexity: int = 1
    model_complexity: int = 0
    version: str = ""

    def __post_init__(self) -> None:
        for name in (
            "num_parameters",
            "num_rules",
            "num_indicators",
            "num_filters",
            "num_conditions",
            "model_complexity",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.optimization_complexity < 1:
            raise ValueError(
                "optimization_complexity is a count of configurations and "
                "cannot be below 1"
            )

    @property
    def search_space_order(self) -> int:
        """Order of magnitude of the parameter grid (0 when it is one setting).

        The raw product is reported as it is, but comparing 10^2 with 10^11
        by subtraction would drown every other term, so the score uses its
        order of magnitude.
        """
        return len(str(self.optimization_complexity)) - 1

    @property
    def score(self) -> int:
        """One comparable number, so "simpler" can be decided."""
        return (
            PARAMETER_WEIGHT * self.num_parameters
            + INDICATOR_WEIGHT * self.num_indicators
            + FILTER_WEIGHT * self.num_filters
            + RULE_WEIGHT * self.num_rules
            + CONDITION_WEIGHT * self.num_conditions
            + self.search_space_order
            + self.model_complexity
        )

    def describe(self) -> str:
        """One line for reports and qualification reviews (chapter 35)."""
        parts = [
            f"{self.num_parameters} parameter(s)",
            f"{self.num_rules} rule(s)",
            f"{self.num_indicators} indicator(s)",
            f"{self.num_filters} filter(s)",
            f"{self.num_conditions} condition(s)",
            f"{self.optimization_complexity} configuration(s) in the grid",
        ]
        if self.model_complexity:
            parts.append(f"model complexity {self.model_complexity}")
        return ", ".join(parts)

    def to_dict(self) -> dict:
        return {
            "num_parameters": self.num_parameters,
            "num_rules": self.num_rules,
            "num_indicators": self.num_indicators,
            "num_filters": self.num_filters,
            "num_conditions": self.num_conditions,
            "optimization_complexity": self.optimization_complexity,
            "model_complexity": self.model_complexity,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "StrategyComplexity":
        def number(key: str, default: int) -> int:
            value = data.get(key, default)
            return int(value) if value is not None else default

        return cls(
            num_parameters=number("num_parameters", 0),
            num_rules=number("num_rules", 0),
            num_indicators=number("num_indicators", 0),
            num_filters=number("num_filters", 0),
            num_conditions=number("num_conditions", 0),
            optimization_complexity=number("optimization_complexity", 1),
            model_complexity=number("model_complexity", 0),
            version=str(data.get("version", "")),
        )


def _configurations(declaration: Mapping[str, Any]) -> int:
    """How many values one declared parameter can take (1 when unknown).

    Only an explicit range, step or list of allowed values defines a grid. A
    parameter with no declared bounds is counted as one setting instead of
    inventing a range: the search space is then honestly unknown, not large.
    """
    if not isinstance(declaration, Mapping):
        return 1
    allowed = declaration.get("allowed") or declaration.get("choices")
    if allowed:
        try:
            return max(1, len(list(allowed)))
        except TypeError:
            return 1
    kind = str(declaration.get("type", "")).lower()
    if kind in ("bool", "boolean"):
        return 2
    low, high = declaration.get("min"), declaration.get("max")
    if low is None or high is None:
        return 1
    try:
        if kind in ("float", "number", "decimal"):
            step = declaration.get("step")
            if not step:
                return 1  # a continuous range is not a grid
            # Decimal, not float: (1.0 - 0.0) // 0.1 is 9 in binary floating
            # point, which would report one configuration fewer than exists.
            span = Decimal(str(high)) - Decimal(str(low))
            return max(1, int(span / Decimal(str(step))) + 1)
        return max(1, int(high) - int(low) + 1)
    except (TypeError, ValueError, ArithmeticError):
        return 1


def strategy_complexity_from_schema(
    parameters_schema: Optional[Mapping[str, Any]] = None,
    *,
    rules: int = 0,
    indicators: int = 0,
    filters: int = 0,
    conditions: int = 0,
    model_complexity: int = 0,
    version: str = "",
) -> StrategyComplexity:
    """Complexity of a strategy described by its parameter schema (ch. 35).

    The parameter count and the grid size come from the schema itself; the
    structural counts (rules, indicators, filters, conditions) cannot be
    derived from parameters, so the strategy has to declare them.
    """
    grid = 1
    for declaration in (parameters_schema or {}).values():
        grid *= _configurations(declaration)
    return StrategyComplexity(
        num_parameters=len(parameters_schema or {}),
        num_rules=rules,
        num_indicators=indicators,
        num_filters=filters,
        num_conditions=conditions,
        optimization_complexity=grid,
        model_complexity=model_complexity,
        version=version,
    )


def strategy_complexity_from_rule(spec: RuleStrategySpec) -> StrategyComplexity:
    """Complexity of a declarative rule (chapters 33.5 and 35).

    Rules declare no parameter bounds, so the search space is unknown and
    ``optimization_complexity`` stays 1 rather than pretending a range.
    """
    conditions = tuple(spec.entry) + tuple(spec.exit)
    indicators = set()
    periods = set()
    for condition in conditions:
        for operand in (condition.left, condition.right):
            found = operand_indicator(operand)
            if found is not None:
                indicators.add(found)
                periods.add(found[1])
    tunables = set(periods)
    rules = len(conditions)
    if spec.stop_loss_fraction is not None:
        rules += 1
        tunables.add("stop_loss")
    if spec.take_profit_fraction is not None:
        rules += 1
        tunables.add("take_profit")
    return StrategyComplexity(
        num_parameters=len(tunables),
        num_rules=rules,
        num_indicators=len(indicators),
        num_filters=0,
        num_conditions=len(conditions),
        optimization_complexity=1,
        version=spec.version,
    )


@dataclass(frozen=True)
class ComplexityComparison:
    """Which of two strategies should be preferred, and why (chapter 35)."""

    preferred: str  # "a", "b" or "tie"
    reason: str


def _as_decimal(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def prefer_simpler(
    evidence_a: Any,
    complexity_a: StrategyComplexity,
    evidence_b: Any,
    complexity_b: StrategyComplexity,
    *,
    tolerance: Decimal = Decimal("0.10"),
) -> ComplexityComparison:
    """Choose between two strategies, favouring the simpler one on a tie.

    "Comparable evidence" means the two evidence figures are within
    ``tolerance`` (relative) of each other. In that case the lower complexity
    score wins, because the extra structure bought nothing measurable — the
    rule chapter 35 states. Otherwise the better evidence wins, and the
    reason says so, so a more complex winner is a decision and not an
    accident.
    """
    a = _as_decimal(evidence_a)
    b = _as_decimal(evidence_b)
    scale = max(abs(a), abs(b))
    comparable = abs(a - b) <= tolerance * scale

    if comparable:
        if complexity_a.score < complexity_b.score:
            return ComplexityComparison(
                "a",
                f"Evidence is comparable ({a} vs {b}, within "
                f"{tolerance:.0%}); the simpler strategy wins "
                f"(score {complexity_a.score} vs {complexity_b.score}).",
            )
        if complexity_b.score < complexity_a.score:
            return ComplexityComparison(
                "b",
                f"Evidence is comparable ({a} vs {b}, within "
                f"{tolerance:.0%}); the simpler strategy wins "
                f"(score {complexity_b.score} vs {complexity_a.score}).",
            )
        return ComplexityComparison(
            "tie",
            f"Evidence and complexity are both comparable ({a} vs {b}, "
            f"score {complexity_a.score}); prefer the one with more "
            "out-of-sample evidence, not the newer one.",
        )

    better = "a" if a > b else "b"
    return ComplexityComparison(
        better,
        f"Evidence differs ({a} vs {b}, more than {tolerance:.0%}): the "
        "better evidence wins, but a more complex winner must still "
        "justify the extra structure out-of-sample.",
    )


def complexity_growth_warning(
    previous: StrategyComplexity,
    current: StrategyComplexity,
    evidence_before: Any,
    evidence_after: Any,
    *,
    tolerance: Decimal = Decimal("0.10"),
) -> Optional[str]:
    """Warn when a version grew more complex without better evidence (35).

    Returns ``None`` when complexity did not grow, or when the growth came
    with an evidence improvement larger than ``tolerance``.
    """
    if current.score <= previous.score:
        return None
    before = _as_decimal(evidence_before)
    after = _as_decimal(evidence_after)
    improvement = after - before
    required = tolerance * max(abs(before), abs(after))
    if improvement > required:
        return None
    return (
        f"Complexity grew from {previous.score} to {current.score} while "
        f"evidence moved from {before} to {after}. Extra parameters, "
        "indicators and filters are not free: they make it easier to fit "
        "noise. Keep the simpler version unless the new one proves itself "
        "on data it was not designed on."
    )


STRATEGY_COMPLEXITY_EXPLANATION = (
    "Every parameter is a knob, and every knob multiplies the number of "
    "combinations you could try. Try enough combinations on the same "
    "history and one of them will look brilliant by luck alone. That is why "
    "a strategy with many parameters, indicators and filters is not "
    "automatically better than a simple one: it is automatically easier to "
    "overfit. When two strategies show comparable evidence, prefer the "
    "simpler one — and when a new version adds structure without adding "
    "evidence, that is a warning, not progress."
)


__all__ = [
    "ComplexityLevel",
    "ComplexityMetrics",
    "ComplexityLimits",
    "ComplexityReport",
    "ComplexityAnalyzer",
    "analyze_strategy_complexity",
    "COMPLEXITY_CONTROL_WARNING",
    "StrategyComplexity",
    "ComplexityComparison",
    "strategy_complexity_from_schema",
    "strategy_complexity_from_rule",
    "prefer_simpler",
    "complexity_growth_warning",
    "STRATEGY_COMPLEXITY_EXPLANATION",
]
