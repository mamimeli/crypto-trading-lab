# Architecture boundaries (chapter 33.6)

> **Short version.** A strategy decides. It does not place orders, reach an
> exchange, read credentials, or touch the risk manager — and that is checked
> by the test suite, not just stated here.

## The flow

```text
Market data → Strategy → Signal → Risk manager → Approved order → Execution
```

The engine owns everything after `Signal`. The strategy owns one method:

```python
def on_candle(self, index: int, candles: Sequence[Candle]) -> OrderSide | None
```

Two arguments, one return value. There is no exchange handle to misuse, no
account to drain and no limit to overwrite — the signature is the first
boundary.

## The five prohibitions, and how each is enforced

| Prohibition | Enforcement |
|---|---|
| no orders created by a strategy | it returns `OrderSide`, never an `OrderRequest`; `tests/test_architecture_boundaries.py` pins the signature and the return type |
| no direct exchange access | static import scan over the strategy-surface modules |
| no bypassing the `RiskManager` | the engine evaluates every order before creating it |
| no modifying global limits | `RiskLimits` is frozen, read from the config, and a fresh manager is built per run |
| no access to credentials | static import scan (no `security`, no keyring) |

## The import scan

Every strategy-surface module — `backtesting/engine.py`, `rule_strategy.py`,
`strategy_builder.py`, `strategy_registry.py`, `signals.py`,
`strategy_parameters.py`, `strategy_validation.py`,
`complexity_control.py` — is parsed with `ast` and rejected if it imports
`crypto_trading_lab.exchanges`, `crypto_trading_lab.security`, `ccxt`,
`requests`, `httpx`, `aiohttp`, `websockets`, `socket`, `urllib` or
`http.client`.

It is **static** on purpose: a module that *can* import an exchange has the
capability whether or not this particular run used it, and a runtime trace
would only catch the runs that happened to connect.

`risk_manager` is forbidden in the strategy-side modules but allowed in
`engine.py`, because the engine *is* the executor and the chapter requires it
to call the manager. That asymmetry is the point: the gate lives where the
orders are made.

The scan is itself tested against a file that violates it, so it cannot pass
by being broken.

## The risk gate

`run_backtest()` builds a `RiskManager` per run and evaluates every order it
would create — including exits, because a gate that blocks a risk-reducing
exit is worse than no gate:

```python
BacktestConfig(risk_limits=RiskLimits(
    max_risk_per_trade=Decimal("0.01"),
    max_position_size=Decimal("0.5"),
    max_total_exposure=Decimal("0.5"),
    max_long_exposure=Decimal("0.5"),
    max_short_exposure=Decimal("0"),
))
```

A refusal means **no order that candle**, and it is information, not an
error: the signal is still recorded (chapter 33.5), and the result carries
`risk_rejections` and `risk_rejection_reasons`.

**The default is permissive, and that is a decision.** With no limits
configured the engine uses `RiskManager.permissive()`: the gate is in the
path, it simply has nothing to refuse. A backtest that silently applied a
2 % daily-loss stop would report a smaller, wrong result for a risk appetite
the user never stated; the real numbers belong to chapter 58.
`config_metadata["risk_gate"]` records which of the two ran, so a report
never has to guess.

The portfolio the manager sees is valued at the price the order would trade
at, not at the candle's close. Valuing at the close made a full exit look
like it opened a short whenever `open > close`, and the manager then refused
the very order that reduced exposure.

## Look-ahead: a view, not a promise

`on_candle` receives `_VisibleCandles`, a `Sequence` whose `len()`,
iteration and indices stop at the current candle. The engine used to pass the
whole list and trust every strategy to slice it — a guarantee that depends on
the caller's good behaviour is not a guarantee.

The view is O(1). Slicing the real list per candle would copy it, which is
O(N²) over a run. Indexing past the current candle raises an `IndexError`
that distinguishes *hidden* ("not visible yet") from *absent* ("does not
exist"), because a strategy debugging its own logic should be told which one
it hit.

## Limits, stated plainly

- **The engine has no day boundary.** A configured daily or weekly loss limit
  acts as a run-level stop, because `daily_pnl` and `weekly_pnl` are the
  run's cumulative P&L. Honest, but not a simulation of a trading day.
- **Consecutive losses are not tracked**, so `max_consecutive_losses` is
  inert in a backtest.
- **The scan is about imports, not behaviour.** A strategy could still encode
  an exchange's fee schedule as constants; that is not a boundary violation,
  it is a modelling choice.
- **The gate cannot see the future either.** It runs on the same candle the
  order is created from, before the fill.
