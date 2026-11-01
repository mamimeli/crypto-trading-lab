# Strategy complexity control (chapter 35)

> **Short version.** Complexity is recorded per strategy *version*, it is
> shown in reports and in qualification, and it never wins an argument on
> its own: when two strategies show comparable evidence, the simpler one is
> preferred.

## Two questions, two answers

`src/crypto_trading_lab/complexity_control.py` answers two different
questions, and confusing them is how a project ends up measuring the wrong
thing.

| Question | Tool | Unit |
|---|---|---|
| Is the Python class that implements the strategy hard to maintain? | `ComplexityAnalyzer` (`analyze_strategy_complexity`) | cyclomatic complexity, Halstead volume, maintainability index |
| Is the strategy *itself* over-parameterised, and therefore easy to overfit? | `StrategyComplexity` | parameters, rules, indicators, filters, conditions, grid size, model size |

Chapter 35 is the second row. The first row is a maintainability check on
our own code and it is still shown in the Backtesting Lab, but a low
cyclomatic complexity says nothing about whether a strategy is overfitted.

## What is recorded

`StrategyComplexity` carries exactly what the chapter asks for:

| Field | Meaning |
|---|---|
| `num_parameters` | tunable knobs the version exposes |
| `num_rules` | things that can trigger an action (conditions, stop, target) |
| `num_indicators` | distinct indicators the rules read |
| `num_filters` | gates that can veto a signal (volume, trend, cooldown…) |
| `num_conditions` | comparisons in the entry/exit rules |
| `optimization_complexity` | how many configurations the declared parameter grid contains |
| `model_complexity` | size of a machine-learning model, `0` when there is none (chapter 48) |
| `version` | the strategy version these numbers belong to |

`score` is a single comparable number, so "simpler" can be decided without
hand-waving:

```
score = 4*parameters + 2*indicators + 2*filters + rules + conditions
        + order_of_magnitude(grid) + model_complexity
```

The weights are a **stated convention, not a measurement**: a parameter
weighs most because each one multiplies the configurations that could be
tried, an indicator or a filter weighs two because it adds a whole
comparison to every decision, and a rule and a condition weigh one because
they are the same thing counted from two angles. The grid contributes its
*order of magnitude* — subtracting 10² from 10¹¹ would drown every other
term.

## Where the numbers come from

- **Registry strategies** (`strategy_registry.py`): the parameter count and
  the grid are derived from the registered `parameters_schema`; the
  structural counts are declared by the strategy in `structure=`. The
  record is stored with the version and re-computed by
  `update_metadata()` when a new version changes the parameters.
- **Declarative rules** (`rule_strategy.py`): everything is derived from the
  rule itself (`strategy_complexity_from_rule`). The rule language declares
  no parameter bounds, so `optimization_complexity` stays `1` — unknown is
  reported as unknown instead of inventing a range.
- **A parameter with no declared bounds** counts as one setting, not as a
  guessed range. A continuous float range without a `step` is not a grid
  either. Both choices keep the record honest rather than flattering.

## The three rules that use it

1. **`prefer_simpler(evidence_a, complexity_a, evidence_b, complexity_b)`** —
   when the two evidence figures are within `tolerance` (10 % by default) of
   each other, the lower score wins. Otherwise the better evidence wins, and
   the reason says so, so a more complex winner is a decision rather than an
   accident.
2. **`complexity_growth_warning(previous, current, evidence_before,
   evidence_after)`** — returns a sentence when a version grew more complex
   without an evidence improvement larger than the tolerance, and `None`
   otherwise.
3. **`evaluate_complexity(acceptable, metrics)`** — the chapter 66
   qualification criterion. With `metrics` the review carries
   `score=…` and the full breakdown instead of a bare boolean.

## Where a user sees it

- **Backtesting Lab** → *Analyze complexity* prints both blocks: the code
  metrics and, under "What this strategy version declares", the chapter 35
  numbers for the selected strategy (registry metadata, or the loaded rule).
- **Qualification reports** (`qualification.py`) → the `complexity`
  criterion, with the numbers in `notes` when they were supplied.

## What this does not claim

Complexity is metadata about structure, not a verdict about money. A simple
strategy is not automatically good, a complex one is not automatically bad,
and none of these numbers predicts a return. The point is narrower and more
useful: extra structure has to earn its keep on data it was not designed on.
