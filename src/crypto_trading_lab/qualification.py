"""Strategy qualification (ROADMAP.md chapter 66).

A formal evaluation stage: a strategy is not "qualified" merely because
Profit > 0. Qualification considers every applicable criterion (66.1),
produces one of Qualified / Conditionally Qualified / Not Qualified (66.2),
and records when re-qualification is due (66.3).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # keeps this module free of runtime project imports
    from crypto_trading_lab.complexity_control import StrategyComplexity


class QualificationOutcome(Enum):
    QUALIFIED = "qualified"
    CONDITIONALLY_QUALIFIED = "conditionally_qualified"
    NOT_QUALIFIED = "not_qualified"


DEFAULT_REQUALIFICATION_INTERVAL_DAYS = 90


@dataclass(frozen=True)
class CriterionResult:
    name: str
    passed: bool
    value: str | None
    threshold: str | None
    notes: str | None


@dataclass(frozen=True)
class StrategyQualification:
    strategy_name: str
    strategy_version: str
    outcome: QualificationOutcome
    criterion_results: list[CriterionResult]
    conditions: list[str]
    failed_criteria: list[str]
    notes: str
    re_qualification_due: str | None


def evaluate_out_of_sample(oos_return: Decimal, min_return: Decimal = Decimal("0.05")) -> CriterionResult:
    passed = oos_return >= min_return
    return CriterionResult(
        name="out_of_sample_performance",
        passed=passed,
        value=f"{oos_return:.1%}",
        threshold=f">={min_return:.1%}",
        notes="Positive out-of-sample return required",
    )


def evaluate_drawdown(max_drawdown: Decimal, max_allowed: Decimal = Decimal("0.20")) -> CriterionResult:
    passed = max_drawdown <= max_allowed
    return CriterionResult(
        name="drawdown",
        passed=passed,
        value=f"{max_drawdown:.1%}",
        threshold=f"<={max_allowed:.1%}",
        notes="Max drawdown must be within acceptable limits",
    )


def evaluate_sample_size(number_of_trades: int, min_trades: int = 30) -> CriterionResult:
    passed = number_of_trades >= min_trades
    return CriterionResult(
        name="sample_size",
        passed=passed,
        value=str(number_of_trades),
        threshold=f">={min_trades}",
        notes="Minimum 30 trades for statistical significance",
    )


def evaluate_robustness(perturbation_collapsed: bool, monte_carlo_ruin: Decimal, max_ruin: Decimal = Decimal("0.10")) -> CriterionResult:
    passed = not perturbation_collapsed and monte_carlo_ruin <= max_ruin
    value = f"ruin={monte_carlo_ruin:.1%}"
    notes = "No parameter collapse, risk of ruin < 10%" if passed else "See detailed analysis"
    return CriterionResult(
        name="robustness",
        passed=passed,
        value=value,
        threshold=f"ruin<={max_ruin:.1%}",
        notes=notes,
    )


def evaluate_risk_adjusted(sharpe_ratio: Decimal, min_sharpe: Decimal = Decimal("0.5")) -> CriterionResult:
    passed = sharpe_ratio >= min_sharpe
    return CriterionResult(
        name="risk_adjusted_metrics",
        passed=passed,
        value=f"sharpe={sharpe_ratio:.2f}",
        threshold=f"sharpe>={min_sharpe:.1f}",
        notes="Positive risk-adjusted returns required",
    )


def _flag(name: str, ok: bool, notes: str) -> CriterionResult:
    return CriterionResult(
        name=name,
        passed=ok,
        value=str(ok),
        threshold="acceptable",
        notes=notes,
    )


def evaluate_benchmark(strategy_return: Decimal, benchmark_return: Decimal) -> CriterionResult:
    passed = strategy_return >= benchmark_return
    return CriterionResult(
        name="benchmark_comparison",
        passed=passed,
        value=f"{strategy_return:.1%}",
        threshold=f">={benchmark_return:.1%}",
        notes="Strategy must beat or match its benchmark (chapter 42)",
    )


def evaluate_parameter_stability(stable: bool) -> CriterionResult:
    return _flag(
        "parameter_stability",
        stable,
        "Parameters must be stable out-of-sample (chapter 39)",
    )


def evaluate_walk_forward(passed: bool) -> CriterionResult:
    return _flag(
        "walk_forward",
        passed,
        "Walk-forward must confirm the edge (chapter 45)",
    )


def evaluate_paper_trading(passed: bool) -> CriterionResult:
    return _flag(
        "paper_trading",
        passed,
        "Paper-trading evidence required (chapter 57)",
    )


def evaluate_execution_realism(realistic: bool) -> CriterionResult:
    return _flag(
        "execution_realism",
        realistic,
        "Fills must be executable, not idealized (chapter 56)",
    )


def evaluate_data_quality(ok: bool) -> CriterionResult:
    return _flag(
        "data_quality",
        ok,
        "Data quality must be acceptable (chapter 29)",
    )


def evaluate_complexity(
    acceptable: bool,
    metrics: Optional["StrategyComplexity"] = None,
) -> CriterionResult:
    """The chapter 35 criterion, with the metrics shown (chapter 66.1).

    ``metrics`` is optional so existing callers that only know the verdict
    keep working; when it is supplied the review carries the numbers instead
    of a bare boolean, which is what chapter 35 asks for.
    """
    if metrics is None:
        return _flag(
            "complexity",
            acceptable,
            "Complexity must be justified by edge (chapter 35)",
        )
    return CriterionResult(
        name="complexity",
        passed=acceptable,
        value=f"score={metrics.score}",
        threshold="justified by out-of-sample evidence",
        notes=metrics.describe() + " (chapter 35)",
    )


def evaluate_statistical_evidence(ok: bool) -> CriterionResult:
    return _flag(
        "statistical_evidence",
        ok,
        "Statistical evidence must support the edge (chapter 43)",
    )


def evaluate_operational_stability(stable: bool) -> CriterionResult:
    return _flag(
        "operational_stability",
        stable,
        "Operation must be stable under load (chapter 62)",
    )


def qualify_strategy(
    oos_return: Decimal,
    max_drawdown: Decimal,
    number_of_trades: int,
    sharpe_ratio: Decimal,
    perturbation_collapsed: bool = False,
    monte_carlo_ruin: Decimal = Decimal("0.05"),
    benchmark_return: Optional[Decimal] = None,
    parameters_stable: Optional[bool] = None,
    walk_forward_passed: Optional[bool] = None,
    paper_trading_passed: Optional[bool] = None,
    execution_realistic: Optional[bool] = None,
    data_quality_ok: Optional[bool] = None,
    complexity_acceptable: Optional[bool] = None,
    complexity_metrics: Optional["StrategyComplexity"] = None,
    statistical_evidence_ok: Optional[bool] = None,
    operational_stable: Optional[bool] = None,
    strategy_name: str = "Strategy",
    strategy_version: str = "1.0.0",
    store_path: Optional[str] = None,
    on_store: Optional[callable] = None,
    requalification_interval_days: int = DEFAULT_REQUALIFICATION_INTERVAL_DAYS,
) -> StrategyQualification:
    """Perform complete strategy qualification (66.1, 66.2, 66.3).

    A criterion is only evaluated when its input is supplied ("where
    applicable"); missing evidence is not treated as failure. The report can
    be persisted (66.2 storage) and a re-qualification date is computed (66.3).
    """
    criteria: list[CriterionResult] = [
        evaluate_out_of_sample(oos_return),
        evaluate_drawdown(max_drawdown),
        evaluate_sample_size(number_of_trades),
        evaluate_risk_adjusted(sharpe_ratio),
        evaluate_robustness(perturbation_collapsed, monte_carlo_ruin),
    ]
    if benchmark_return is not None:
        criteria.append(evaluate_benchmark(oos_return, benchmark_return))
    if parameters_stable is not None:
        criteria.append(evaluate_parameter_stability(parameters_stable))
    if walk_forward_passed is not None:
        criteria.append(evaluate_walk_forward(walk_forward_passed))
    if paper_trading_passed is not None:
        criteria.append(evaluate_paper_trading(paper_trading_passed))
    if execution_realistic is not None:
        criteria.append(evaluate_execution_realism(execution_realistic))
    if data_quality_ok is not None:
        criteria.append(evaluate_data_quality(data_quality_ok))
    if complexity_acceptable is not None:
        criteria.append(
            evaluate_complexity(complexity_acceptable, complexity_metrics)
        )
    if statistical_evidence_ok is not None:
        criteria.append(evaluate_statistical_evidence(statistical_evidence_ok))
    if operational_stable is not None:
        criteria.append(evaluate_operational_stability(operational_stable))

    passed_count = sum(1 for c in criteria if c.passed)
    total = len(criteria)
    failed = [c.name for c in criteria if not c.passed]

    if passed_count == total:
        outcome = QualificationOutcome.QUALIFIED
        conditions = []
    elif passed_count >= total // 2:
        outcome = QualificationOutcome.CONDITIONALLY_QUALIFIED
        conditions = [f"Address: {c}" for c in failed]
    else:
        outcome = QualificationOutcome.NOT_QUALIFIED
        conditions = []

    due = (datetime.now(timezone.utc) + timedelta(days=requalification_interval_days)).date().isoformat()
    notes = (
        "Qualification is not a guarantee of future profitability. "
        "See Chapter 66 for details. Re-qualify after material changes "
        f"(interval: {requalification_interval_days} days, due {due})."
    )

    report = StrategyQualification(
        strategy_name=strategy_name,
        strategy_version=strategy_version,
        outcome=outcome,
        criterion_results=criteria,
        conditions=conditions,
        failed_criteria=failed,
        notes=notes,
        re_qualification_due=due,
    )

    if store_path is not None:
        save_qualification_report(report, store_path)
    if on_store is not None:
        on_store(report)
    return report


def save_qualification_report(report: StrategyQualification, path: str) -> None:
    """Persist a qualification report so it can be referenced (66.2)."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(asdict(report), fh, indent=2, default=lambda o: o.value if isinstance(o, Enum) else str(o))


QUALIFICATION_WARNING = (
    "Qualification is a historical analysis, not a guarantee of future "
    "performance. All qualification outcomes must be reviewed before any "
    "real trading decision."
)
