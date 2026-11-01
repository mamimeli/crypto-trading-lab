"""Architectural boundaries of chapter 33.6.

The chapter fixes one flow — market data → strategy → signal → risk manager
→ order → execution — and five prohibitions. This module checks the
prohibitions mechanically, because an architecture that is only described
in a document is an architecture that drifts:

* a strategy cannot create orders (it returns a side, nothing more);
* it cannot talk to an exchange, read credentials, or touch the risk
  manager — enforced by scanning its imports;
* it cannot bypass the risk manager, because the engine is the only path to
  a fill and it consults the manager on every order;
* it cannot modify global limits: it never receives them.

The import scan is deliberately static (``ast``, not a runtime trace): a
strategy that imports an exchange module has the capability whether or not
this particular run used it.
"""

from __future__ import annotations

import ast
import dataclasses
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from crypto_trading_lab.backtesting.engine import (
    BacktestConfig,
    BuyAndHoldStrategy,
    Strategy,
    run_backtest,
)
from crypto_trading_lab.domain.models import Candle, Symbol
from crypto_trading_lab.risk_manager import RiskLimits

SOURCE = Path(__file__).resolve().parents[1] / "src" / "crypto_trading_lab"

#: Every module on the strategy surface: the strategies themselves, the rule
#: language, the builder, the registry and the strategy-side records.
STRATEGY_MODULES = (
    "backtesting/engine.py",
    "rule_strategy.py",
    "strategy_builder.py",
    "strategy_registry.py",
    "signals.py",
    "strategy_parameters.py",
    "strategy_validation.py",
    "complexity_control.py",
)

#: Modules that hold *only* strategy-side logic. ``backtesting/engine.py`` is
#: excluded from this list on purpose: it also *is* the executor, and the
#: chapter requires the executor to call the risk manager, so it must be able
#: to import it. Everything else must not.
PURE_STRATEGY_MODULES = tuple(
    name for name in STRATEGY_MODULES if name != "backtesting/engine.py"
)

FORBIDDEN_EVERYWHERE = (
    "crypto_trading_lab.exchanges",
    "crypto_trading_lab.security",
    "ccxt",
    "requests",
    "httpx",
    "aiohttp",
    "websockets",
    "socket",
    "urllib",
    "http.client",
)

FORBIDDEN_IN_STRATEGY_LOGIC = ("crypto_trading_lab.risk_manager",)

BASE = datetime(2024, 1, 1, tzinfo=timezone.utc)
HOUR = timedelta(hours=1)


def _candles(closes) -> list[Candle]:
    return [
        Candle(
            symbol=Symbol("BTC/USDT"),
            interval="1h",
            open_time=BASE + index * HOUR,
            close_time=BASE + (index + 1) * HOUR,
            open=Decimal(str(value)),
            high=Decimal(str(value)) + Decimal("1"),
            low=Decimal(str(value)) - Decimal("1"),
            close=Decimal(str(value)),
            volume=Decimal("10"),
        )
        for index, value in enumerate(closes)
    ]


def _imported_modules(path: Path) -> set[str]:
    """Every module name a file imports, at any depth."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _matches(module: str, forbidden: str) -> bool:
    return module == forbidden or module.startswith(forbidden + ".")


# -- no exchange, no credentials, no network ---------------------------------


@pytest.mark.parametrize("relative", STRATEGY_MODULES)
def test_a_strategy_module_cannot_reach_an_exchange_or_a_credential(relative):
    """A strategy that can import an exchange has the capability, whether or
    not this run used it."""
    imported = _imported_modules(SOURCE / relative)
    offenders = sorted(
        module
        for module in imported
        for forbidden in FORBIDDEN_EVERYWHERE
        if _matches(module, forbidden)
    )

    assert offenders == [], (
        f"{relative} imports {offenders}; chapter 33.6 forbids a strategy "
        "from reaching an exchange, credentials or the network"
    )


@pytest.mark.parametrize("relative", PURE_STRATEGY_MODULES)
def test_strategy_logic_cannot_import_the_risk_manager(relative):
    """The gate belongs to the executor. A strategy-side module importing the
    manager could evaluate — or dodge — its own orders."""
    imported = _imported_modules(SOURCE / relative)
    offenders = [
        module
        for module in imported
        if _matches(module, "crypto_trading_lab.risk_manager")
    ]

    assert offenders == []


def test_the_scan_would_catch_a_real_violation(tmp_path):
    """The check is only worth having if it fails when it should."""
    smuggled = tmp_path / "smuggled.py"
    smuggled.write_text(
        "import ccxt\nfrom crypto_trading_lab.exchanges.binance import adapter\n",
        encoding="utf-8",
    )

    imported = _imported_modules(smuggled)
    caught = [
        module
        for module in imported
        for forbidden in FORBIDDEN_EVERYWHERE
        if _matches(module, forbidden)
    ]

    assert caught


# -- the strategy only decides ----------------------------------------------


def test_the_strategy_protocol_hands_over_candles_and_nothing_else():
    """No exchange handle, no account, no risk manager: two arguments."""
    import inspect

    parameters = list(inspect.signature(Strategy.on_candle).parameters)

    assert parameters == ["self", "index", "candles"]


def test_a_strategy_is_given_only_the_candles_it_may_see():
    """It sees candles up to ``index`` — no future, no other object."""
    seen: list[tuple[int, int]] = []

    class Spy:
        name = "spy"
        warmup_candles = 0

        def on_candle(self, index, candles):
            seen.append((index, len(candles)))
            return None

    run_backtest(_candles([1, 2, 3, 4, 5]), Spy())

    assert seen == [(index, index + 1) for index in range(5)]


def test_a_strategy_cannot_return_an_order():
    """The protocol says ``OrderSide | None``: a side, not a request."""
    import typing

    hints = typing.get_type_hints(Strategy.on_candle, include_extras=False)

    assert "return" in hints
    assert "OrderSide" in str(hints["return"])


# -- the risk manager is in the path ----------------------------------------


def _strict_limits() -> RiskLimits:
    return RiskLimits(
        max_risk_per_trade=Decimal("0.01"),
        max_position_size=Decimal("0.5"),
        max_total_exposure=Decimal("0.5"),
        max_long_exposure=Decimal("0.5"),
        max_short_exposure=Decimal("0"),
    )


def test_a_configured_limit_really_refuses_the_order():
    """The gate is not decoration: a limit that is too tight stops the trade."""
    result = run_backtest(
        _candles([100, 101, 102]),
        BuyAndHoldStrategy(),
        BacktestConfig(risk_limits=_strict_limits()),
    )

    assert result.trades == []
    assert result.risk_rejections >= 1
    assert result.risk_rejection_reasons == ("Order exceeds maximum position size",)


def test_the_default_gate_approves_everything_a_spot_run_can_propose():
    """A research run must not invent a risk appetite nobody stated."""
    result = run_backtest(_candles([100, 101, 102]), BuyAndHoldStrategy())

    assert result.risk_rejections == 0
    assert result.order_count == 1
    assert result.config_metadata["risk_gate"] == "permissive"


def test_the_result_says_whether_a_real_gate_was_configured():
    configured = run_backtest(
        _candles([100, 101, 102]),
        BuyAndHoldStrategy(),
        BacktestConfig(risk_limits=_strict_limits()),
    )

    assert configured.config_metadata["risk_gate"] == "configured"


def test_a_refused_order_still_leaves_its_signal_recorded():
    """The strategy decided; the manager refused. Both facts survive."""
    result = run_backtest(
        _candles([100, 101, 102]),
        BuyAndHoldStrategy(),
        BacktestConfig(risk_limits=_strict_limits()),
    )

    assert result.signals[0].type.value == "enter_long"
    assert result.exposure_curve == (False, False, False)


# -- global limits are not the strategy's to touch --------------------------


def test_risk_limits_are_immutable():
    limits = _strict_limits()

    with pytest.raises(dataclasses.FrozenInstanceError):
        limits.max_position_size = Decimal("1")


def test_each_run_builds_its_own_manager():
    """A counter carried over from a previous run would silently change the
    second result; two identical runs must agree."""
    limits = _strict_limits()
    first = run_backtest(
        _candles([100, 101, 102, 101, 100]),
        BuyAndHoldStrategy(),
        BacktestConfig(risk_limits=limits),
    )
    second = run_backtest(
        _candles([100, 101, 102, 101, 100]),
        BuyAndHoldStrategy(),
        BacktestConfig(risk_limits=limits),
    )

    assert first.risk_rejections == second.risk_rejections
    assert first.final_equity == second.final_equity
    assert first.trades == second.trades
