"""Compare two strategies on evidence and complexity (chapters 33.8 and 35).

Chapter 33.8 asks the application to favour the simpler strategy when
performance is otherwise comparable; chapter 35 asks the same and records
complexity per version. ``complexity_control.prefer_simpler`` already
implements the rule and is tested, but until now nothing called it — the
chapter-33.8 ``SIMPLER_WINS`` statement was carried in the warning set and
shown as policy, never as a decision the program actually made.

This module is that caller. It resolves two strategies from the registry,
reads the complexity each version declares, and applies the parsimony rule
to the evidence the user supplies: the *same* performance metric from two
backtests (e.g. both deflated Sharpe, or both total return), so the figures
are comparable.

When no evidence is supplied the module does not pretend to decide. It
reports the two complexities and the ``SIMPLER_WINS`` policy statement, so
the warning stays honest about being policy rather than behaviour. That is
the same honest state the rest of the application holds for a run that has
no two strategies to weigh.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from crypto_trading_lab.complexity_control import (
    ComplexityComparison,
    StrategyComplexity,
    prefer_simpler,
)
from crypto_trading_lab.research_warnings import SIMPLER_WINS
from crypto_trading_lab.strategy_registry import StrategyRegistry

#: Default relative tolerance for "comparable evidence" (chapter 35 rule).
DEFAULT_TOLERANCE = Decimal("0.10")


@dataclass(frozen=True)
class StrategyComparison:
    """The result of comparing two strategies (chapters 33.8 and 35)."""

    strategy_a_id: str
    strategy_b_id: str
    complexity_a: Optional[StrategyComplexity]
    complexity_b: Optional[StrategyComplexity]
    evidence_a: Optional[Decimal] = None
    evidence_b: Optional[Decimal] = None
    #: ``"decision"`` when evidence was supplied and ``prefer_simpler`` ran;
    #: ``"policy"`` when no evidence was supplied, so only the rule is stated.
    mode: str = "policy"
    decision: Optional[ComplexityComparison] = None

    @property
    def applied(self) -> bool:
        """Whether the simpler-wins rule actually ran (vs. only stated)."""
        return self.mode == "decision" and self.decision is not None


def _as_decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _as_tolerance(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def compare_strategies(
    strategy_a_id: str,
    strategy_b_id: str,
    *,
    evidence_a: Any = None,
    evidence_b: Any = None,
    tolerance: Any = DEFAULT_TOLERANCE,
    registry: Optional[StrategyRegistry] = None,
) -> StrategyComparison:
    """Compare two registered strategies on evidence and complexity.

    ``evidence_a`` and ``evidence_b`` must be the *same* performance metric
    from two backtests (both deflated Sharpe, or both total return), so they
    are comparable. When both are supplied, the chapter-33.8 / chapter-35
    parsimony rule runs and ``mode`` is ``"decision"``. When either is
    missing, ``mode`` is ``"policy"``: the two complexities are reported and
    the ``SIMPLER_WINS`` statement is shown as policy, not as a decision the
    tool made.

    Complexity is read from each strategy version's declared record in the
    registry; a strategy with no recorded complexity still compares on
    evidence alone. The registry is read only — this function never mutates
    it, so it leaves no file behind.
    """
    if registry is None:
        registry = StrategyRegistry()

    reg_a = registry.get(strategy_a_id)
    reg_b = registry.get(strategy_b_id)
    complexity_a = reg_a.metadata.complexity if reg_a is not None else None
    complexity_b = reg_b.metadata.complexity if reg_b is not None else None

    ev_a = _as_decimal(evidence_a)
    ev_b = _as_decimal(evidence_b)

    if (
        ev_a is not None
        and ev_b is not None
        and complexity_a is not None
        and complexity_b is not None
    ):
        decision = prefer_simpler(
            ev_a,
            complexity_a,
            ev_b,
            complexity_b,
            tolerance=_as_tolerance(tolerance),
        )
        return StrategyComparison(
            strategy_a_id=strategy_a_id,
            strategy_b_id=strategy_b_id,
            complexity_a=complexity_a,
            complexity_b=complexity_b,
            evidence_a=ev_a,
            evidence_b=ev_b,
            mode="decision",
            decision=decision,
        )

    return StrategyComparison(
        strategy_a_id=strategy_a_id,
        strategy_b_id=strategy_b_id,
        complexity_a=complexity_a,
        complexity_b=complexity_b,
        evidence_a=ev_a,
        evidence_b=ev_b,
        mode="policy",
    )


def _describe(complexity: Optional[StrategyComplexity]) -> str:
    if complexity is None:
        return "not recorded"
    return f"score {complexity.score} — {complexity.describe()}"


def render_comparison(comparison: StrategyComparison) -> str:
    """One text block for the CLI or a report (chapters 33.8 and 35)."""
    lines: list[str] = []
    lines.append(
        f"Comparing {comparison.strategy_a_id} vs {comparison.strategy_b_id}"
    )
    lines.append("")
    lines.append("Complexity (chapter 35, what each version declares):")
    lines.append(f"  {comparison.strategy_a_id}: {_describe(comparison.complexity_a)}")
    lines.append(f"  {comparison.strategy_b_id}: {_describe(comparison.complexity_b)}")
    lines.append("")

    if comparison.applied and comparison.decision is not None:
        decision = comparison.decision
        lines.append("Evidence supplied — the simpler-wins rule was applied:")
        lines.append(f"  {comparison.strategy_a_id}: {comparison.evidence_a}")
        lines.append(f"  {comparison.strategy_b_id}: {comparison.evidence_b}")
        lines.append("")
        winner = {
            "a": comparison.strategy_a_id,
            "b": comparison.strategy_b_id,
            "tie": "tie — prefer the one with more out-of-sample evidence",
        }.get(decision.preferred, decision.preferred)
        lines.append(f"Decision: {winner}")
        lines.append(f"Reason: {decision.reason}")
    else:
        lines.append(
            "No evidence supplied — the simpler-wins rule is shown as policy,"
        )
        lines.append(
            "not as a decision. Supply --evidence-a and --evidence-b (the same"
        )
        lines.append(
            "metric from two backtests, e.g. both deflated Sharpe) to apply it."
        )
        lines.append("")
        lines.append(f"Policy: {SIMPLER_WINS}")

    return "\n".join(lines)


__all__ = [
    "StrategyComparison",
    "compare_strategies",
    "render_comparison",
    "DEFAULT_TOLERANCE",
]
