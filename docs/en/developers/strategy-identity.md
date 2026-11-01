# Strategy identity — the nine declarations (chapter 33.1)

ROADMAP chapter 33.1 asks every strategy to declare who and what it is before
it says anything about how it trades. `strategy_identity.py` is where a
built-in strategy is named, once.

## The nine declarations

| # | Chapter 33.1 asks for | Field |
|---|---|---|
| 1 | Name | `name` |
| 2 | Unique identifier | `strategy_id` |
| 3 | Version | `version` |
| 4 | Author or source | `author` |
| 5 | Description | `description` |
| 6 | Strategy category | `category` |
| 7 | Beginner-oriented explanation | `beginner_explanation` |
| 8 | Known weaknesses | `known_weaknesses` |
| 9 | Risk warnings | `risk_warnings` |

`StrategyIdentity` is frozen and validates itself on construction: the
identifier must be lowercase ASCII (`^[a-z][a-z0-9_]*$`), the version must be
`MAJOR.MINOR.PATCH`, the category must come from the closed `CATEGORIES` set,
and at least one weakness and one risk warning must be declared. A strategy
with nothing to confess is a strategy nobody reviewed, so the record refuses
to exist without them.

## Why the registry reads this file

Before this change the registry built its metadata from the identifier:
`ma_crossover` became `"Ma Crossover"`, and the description was a hand-typed
string that lived only in `_load_builtin_strategies`. The name a user saw in
`list-strategies`, the name in a backtest report and the name in the docs were
three separate strings that happened to agree.

Now `_load_builtin_strategies` fills `name`, `version`, `author`,
`description` and `category` from `IDENTITIES`, so they agree by construction.
`tests/test_strategy_identity.py` compares the registry metadata against the
identity record field by field; it would fail if either side were edited
alone.

## Categories

`CATEGORIES` is closed and small on purpose — a free-text category cannot be
counted, filtered or compared:

- `trend-following` — moving average crossover
- `mean-reversion` — RSI mean reversion, Bollinger Bands mean reversion
- `breakout` — rolling high/low breakout
- `benchmark` — buy and hold
- `baseline` — null strategy

`test_categories_are_used_not_just_declared` fails if a category is declared
and nothing belongs to it, so the vocabulary cannot grow faster than the
strategies do.

## Weaknesses versus risk warnings

They are separate fields because they answer different questions, and merging
them lets a strategy declare the mild version of each and skip the expensive
one.

- A **weakness** is where the strategy itself is fragile: "it cannot tell a
  trend from a range", "it is always late".
- A **risk warning** is what that fragility does to an account: "a position
  stays open until the sell signal fires, so a drawdown can run further than
  you expect".

Chapter 33.9's guide answers a third, related question — *which market
conditions* favour or hurt the strategy — and stays in `strategy_guide.py`.
The two modules are linked by identifier only: `test_identity_set_matches_the_guide_set`
requires that every identity has a guide and vice versa.

## Where a user sees it

- `list-strategies` prints the category next to the version.
- `list-strategies --explain ID` prints the identity block (author, category,
  description, weaknesses, risk warnings) **before** the chapter 33.9 guide,
  because who a strategy is comes before what it does.
- The Backtesting Lab report prints the category, the weaknesses and the risk
  warnings under "What this strategy is trying to do", above the money.

## What is not here

Chapters 33.2 (market requirements) and 33.3 (trading rules) extend the
declaration in their own modules. Identity describes the *thing*; those
describe its *behaviour*, and keeping them apart means a strategy can be
renamed without its trading rules being re-reviewed.
