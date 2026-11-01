"""Research warnings the application owes the user (ROADMAP.md chapter 33.8).

A backtest produces a number, and a number is persuasive for reasons that
have nothing to do with its meaning. Chapter 33.8 lists what the
application must say out loud so a user can read that number with the right
amount of doubt:

* a strategy can perform well historically by chance;
* more parameters increase the risk of overfitting;
* adding filters does not necessarily improve a strategy;
* a higher historical profit does not necessarily mean a better strategy;
* a strategy must be evaluated on data that was not used to design or
  optimize it;
* strategy complexity should be recorded (chapter 35);
* the system should favour simpler strategies when performance is otherwise
  comparable.

The statements live here, as constants, for one reason: a warning that is
rewritten slightly differently on every screen is a warning nobody can
test. The UI decides *where* to show them; this module decides *what* they
say.

They are deliberately not translated through ``self.tr()`` at the call site:
they are generated messages (like ``report.warnings``), not labels, and a
``self.tr()`` on a variable cannot find a translation anyway.
"""

from __future__ import annotations

from typing import Optional

__all__ = [
    "CHANCE",
    "OVERFITTING",
    "FILTERS",
    "HIGHER_PROFIT",
    "OUT_OF_SAMPLE",
    "COMPLEXITY",
    "SIMPLER_WINS",
    "RESEARCH_WARNINGS",
    "OVERFITTING_PARAMETER_THRESHOLD",
    "warnings_for_run",
]

#: Above this many parameters the overfitting warning is shown even when no
#: optimization was recorded. Three is the first count where a "strategy" can
#: describe a shape rather than a threshold; it is a presentation threshold,
#: not a statistical claim.
OVERFITTING_PARAMETER_THRESHOLD = 3

CHANCE = (
    "A strategy can perform well historically by chance. A backtest is "
    "evidence, not proof."
)

OVERFITTING = (
    "More parameters increase the risk of overfitting: the more knobs there "
    "are, the easier it is to fit the past instead of the future."
)

FILTERS = (
    "Adding filters does not necessarily improve a strategy. A filter that "
    "only removes bad trades in this sample may remove good ones in the next."
)

HIGHER_PROFIT = (
    "A higher historical profit does not necessarily mean a better strategy. "
    "Risk taken, sample length and luck all move that number."
)

OUT_OF_SAMPLE = (
    "A strategy must be evaluated on data that was not used to design or "
    "optimize it. This test used IN-SAMPLE historical data only, so its "
    "result is closer to an upper bound than to an expectation."
)

COMPLEXITY = (
    "Strategy complexity should be recorded (chapter 35) so that a simpler "
    "version with the same evidence can be preferred."
)

SIMPLER_WINS = (
    "When performance is otherwise comparable, the system favours the simpler "
    "strategy: fewer parameters, fewer rules, less to overfit."
)

#: Every statement of the chapter, in the order the chapter lists them.
RESEARCH_WARNINGS: tuple[str, ...] = (
    CHANCE,
    OVERFITTING,
    FILTERS,
    HIGHER_PROFIT,
    OUT_OF_SAMPLE,
    COMPLEXITY,
    SIMPLER_WINS,
)


def warnings_for_run(
    *,
    parameters: int = 0,
    filters: int = 0,
    optimized: bool = False,
    evaluated_out_of_sample: bool = False,
    complexity_recorded: bool = True,
) -> tuple[str, ...]:
    """The statements that apply to one run, in chapter order.

    Two are always true of any backtest (chance, and profit not being
    quality). The rest depend on what the run actually did: a strategy with
    many parameters gets the overfitting warning, one with filters gets the
    filter warning, a run with no out-of-sample step gets the one that says
    so, and a strategy whose complexity was not recorded gets told that too.

    ``optimized`` means the parameters were chosen by searching this same
    data — the case where overfitting is not a risk but a likelihood.
    """
    warnings: list[str] = [CHANCE]
    if optimized or parameters >= OVERFITTING_PARAMETER_THRESHOLD:
        warnings.append(OVERFITTING)
    if filters > 0:
        warnings.append(FILTERS)
    warnings.append(HIGHER_PROFIT)
    if not evaluated_out_of_sample:
        warnings.append(OUT_OF_SAMPLE)
    if not complexity_recorded:
        warnings.append(COMPLEXITY)
    return tuple(warnings)


def summary(statements: Optional[tuple[str, ...]] = None) -> str:
    """The statements as one block of text, for a report or a log."""
    chosen = RESEARCH_WARNINGS if statements is None else statements
    return "\n".join(f"- {statement}" for statement in chosen)
