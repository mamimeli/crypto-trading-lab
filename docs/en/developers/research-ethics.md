# Research Ethics and Honest Reporting (Chapter 72)

## Core principle

Crypto Trading Lab maintains **scientific and professional honesty at every stage**.

## Evidence discipline

### What we promise

- Observed results from backtests
- Statistical evidence with stated assumptions
- Honest warnings about limitations

### What we never promise

- Future profitability
- Guarantees of any kind
- Financial advice
- Predictions from Monte Carlo or statistical analysis

## Requirements

### Never claim false certainty

* Never present a backtest as proof of future profitability
* Never present Monte Carlo or bootstrap results as predictions
* Never hide assumptions behind results
* Never cherry-pick time periods or parameters to improve appearance

### Always label evidence level

| Level | Meaning |
|-------|---------|
| Observed result | What happened in one historical run |
| Statistical evidence | Distinguishable from noise with stated methods |
| Research hypothesis | Idea being tested |
| Validated evidence | Survived OOS, robustness, qualification |

### Report failed experiments

* Document failed strategies alongside successful ones
* Track negative results with the same rigor
* Never hide unsuccessful experiments

## Warnings and disclaimers

### Required warnings

* Cryptocurrency trading involves substantial risk
* Users can lose part or all of their capital
* Historical performance does not guarantee future results
* Most retail traders lose money
* Trading is not a reliable income source

### What we are not

* A solution to financial hardship
* Financial advice
* A guarantee of profits
* An oracle that knows which trades to make

### The chapter 33.8 statements (single source of truth)

The seven things a user must be told next to a backtest number live in
`research_warnings.py` as constants, because a warning paraphrased
differently on every screen is a warning nobody can test:

| Constant | When it appears |
|---|---|
| `CHANCE` | always |
| `OVERFITTING` | three or more parameters, **or** the run was optimized on the same data |
| `FILTERS` | the strategy declares filters |
| `HIGHER_PROFIT` | always |
| `OUT_OF_SAMPLE` | unless the run was evaluated out of sample |
| `COMPLEXITY` | when the chapter 35 record is missing |
| `SIMPLER_WINS` | not per run: it is standing policy, shown in the full set |

`warnings_for_run()` returns the applicable ones in chapter order; the CLI
prints them under "Before you trust this result" and the Backtesting Lab
appends the same text to its "Please read before trusting this" block.
Because both read this module, the two surfaces cannot drift.

One limit, stated: `prefer_simpler` (chapter 35) is implemented and tested
but nothing calls it yet, so `SIMPLER_WINS` is shown as policy rather than
claimed as behaviour, and the matching roadmap box stays open.

## Scientific discipline

* Favor simpler explanations when they fit the evidence
* Document uncertainty instead of hiding it
* Keep research automation separate from real operations
* Never present statistical tools as "proof of profitability"

## Educational responsibility

Explain to users:

* Why backtests can be misleading
* Why profits are never guaranteed
* Why paper trading differs from real trading
* The difference between education and financial advice

## Implementation checklist

* [x] Disclaimers in all reports (Chapter 41)
* [x] Evidence labels in all results (Chapter 43)
* [x] Beginner warnings in Learning Center
* [x] Honest metrics in performance reports (Chapter 40)
* [x] Monte Carlo warnings (Chapter 44)
