# Developer documentation — index

Where to look, and when. Everything here is in English, which is the source
language for this project (Spanish ships through Qt Linguist).

If you are new, read in this order:

1. [`AGENT-HANDOFF.md`](../../../AGENT-HANDOFF.md) — what exists today and
   where development left off.
2. [`AGENTS.md`](../../../AGENTS.md) — the non-negotiable ground rules.
3. [`ROADMAP.md`](../../../ROADMAP.md) — **the specification.** Find the
   chapter that owns your task.
4. [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) — workflow, definition of
   done and good first contributions.
5. [`architecture-proposal.md`](architecture-proposal.md) — how the layers
   fit together.

## Reference

| Document | Read it when you need to… |
|---|---|
| [`architecture-proposal.md`](architecture-proposal.md) | understand the layer boundaries and where new code belongs |
| [`unwired-modules-audit.md`](unwired-modules-audit.md) | know which modules were found unwired, what was done with each and why |
| [`venv-setup.md`](venv-setup.md) | install with pip/virtualenv (Linux, macOS, Windows), or evaluate `ccxt` |
| [`debian-dependencies.md`](debian-dependencies.md) | check the supported Debian package matrix and how to install |
| [`configuration-guide.md`](configuration-guide.md) | touch settings, XDG paths or `config.json` |
| [`cli.md`](cli.md) | use, extend or test the chapter 22 command-line interface |
| [`working-method.md`](working-method.md) | make a change the way this project expects (tests, docs, honesty) |
| [`agent-onboarding-tracker.md`](agent-onboarding-tracker.md) | check whether the agent-onboarding surface (AGENTS.md, CLAUDE.md, reading lists, baseline) is complete and current |
| [`small-context-contributing.md`](small-context-contributing.md) | contribute with a small context window — measured costs, what never to load |
| [`threat-model.md`](threat-model.md) | touch credentials, logging, adapters or anything security-shaped |
| [`capital-protection.md`](capital-protection.md) | work on risk, position sizing or drawdown limits |
| [`research-ethics.md`](research-ethics.md) | write anything a user might read as advice |
| [`live-trading-roadmap.md`](live-trading-roadmap.md) | work towards live data, testnet or real money |
| [`live-monitoring.md`](live-monitoring.md) | work on chapter 62 (live health, alerts) |
| [`live-vs-backtest-drift.md`](live-vs-backtest-drift.md) | work on chapter 63 drift thresholds and interpretation |
| [`strategy-complexity.md`](strategy-complexity.md) | work on chapter 35 — what a strategy version declares, and why simpler wins a tie |
| [`strategy-parameters.md`](strategy-parameters.md) | work on chapter 33.4 — declared parameters, validation and what ran |
| [`signal-records.md`](signal-records.md) | work on chapter 33.5 — the signal vocabulary and the record the engine writes per candle |
| [`strategy-validation.md`](strategy-validation.md) | work on chapter 33.7 — what is checked before a run, and why errors and warnings differ |
| [`strategy-identity.md`](strategy-identity.md) | work on chapter 33.1 — the nine facts every strategy declares, and why the registry reads them instead of inventing them |
| [`architecture-boundaries.md`](architecture-boundaries.md) | work on chapter 33.6 — how the strategy/risk/execution boundary is enforced |
| [`afml-techniques.md`](afml-techniques.md) | implement anything from chapters 47–50 (read it **before** coding) |
| [`reference-projects.md`](reference-projects.md) | study the eight vendored reference projects and what was learned |
| [`adr/`](adr/) | understand why a past decision was made (0001–0007) |

## The book rule

*Advances in Financial Machine Learning* (López de Prado, Wiley 2018) is
cited **by bibliographic reference only**. Never copy its text, code, figures
or tables into this repository, and never commit the book. The project's own
specification of every technique it borrows lives in
[`afml-techniques.md`](afml-techniques.md). See `AGENTS.md` rule 6.

## Beginner documentation

The teaching arm of the product lives in
[`../beginners/`](../beginners/): start-here, glossary, indicators,
performance metrics, data splitting, paper trading and regime analysis.
Clarity there is a feature, not an afterthought.
