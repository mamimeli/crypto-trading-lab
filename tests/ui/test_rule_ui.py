"""UI tests for executable rules (chapters 34 and 77)."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

pytest.importorskip("PyQt6")

from crypto_trading_lab.domain.models import Candle, Symbol  # noqa: E402
from crypto_trading_lab.rule_strategy import (  # noqa: E402
    Condition,
    RuleStrategySpec,
)
from crypto_trading_lab.ui.backtesting.lab import BacktestingLabWidget  # noqa: E402
from crypto_trading_lab.ui.strategy_builder import StrategyBuilderDialog  # noqa: E402

HOUR = timedelta(hours=1)
START = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _candles(count: int = 300) -> list[Candle]:
    candles = []
    price = Decimal("100")
    for i in range(count):
        price = max(Decimal("10"), price + Decimal(str(0.6 * math.sin(i / 12.0))))
        open_time = START + i * HOUR
        candles.append(
            Candle(
                symbol=Symbol("BTC/USDT"),
                interval="1h",
                open_time=open_time,
                close_time=open_time + HOUR - timedelta(milliseconds=1),
                open=price,
                high=price + 1,
                low=price - 1,
                close=price,
                volume=Decimal("5"),
            )
        )
    return candles


def test_builder_converts_blocks_into_an_executable_rule(qapp):
    dialog = StrategyBuilderDialog()
    dialog.name_edit.setText("EMA rule")
    dialog.add_block("indicator", indicator_type="ema", params={"period": 10})
    dialog.add_block("indicator", indicator_type="ema", params={"period": 30})
    dialog.add_block("crossover")
    dialog.add_block("entry")
    dialog.add_block("indicator", indicator_type="ema", params={"period": 10})
    dialog.add_block("indicator", indicator_type="ema", params={"period": 30})
    dialog.add_block("crossunder")
    dialog.add_block("exit")

    executable, message = dialog.explain_executability()

    assert executable is True
    assert "Executable rule ready" in message
    spec = dialog.to_rule_spec()
    assert spec.entry[0].left == "ema(10)"
    assert spec.exit[0].operator == "crosses_below"
    dialog.close()


def test_builder_reports_why_a_rule_cannot_run(qapp):
    dialog = StrategyBuilderDialog()
    dialog.add_block("indicator", indicator_type="sma", params={"period": 20})
    dialog.add_block("indicator", indicator_type="sma", params={"period": 50})
    dialog.add_block("crossover")
    dialog.add_block("entry")
    # A cooldown filter is a valid block but not executable yet.
    dialog.add_block("cooldown", periods=5)

    executable, message = dialog.explain_executability()

    assert executable is False
    assert "cannot run" in message
    assert "filter" in message.lower()
    dialog.close()


def test_lab_runs_a_custom_rule_from_the_builder(qapp):
    lab = BacktestingLabWidget(_candles(), "BTC/USDT", "1h")
    spec = RuleStrategySpec(
        name="Loaded rule",
        entry=(Condition("sma(5)", "crosses_above", "sma(20)"),),
        exit=(Condition("sma(5)", "crosses_below", "sma(20)"),),
    )

    label = lab.set_rule_spec(spec)
    text = lab.run_and_display()

    assert "Loaded rule" in label
    assert "What was tested" in text
    # Chapter 33.9: a declarative rule has no written guide, but the report
    # still has to say how it sizes and how its stops are checked.
    assert "== What this rule is trying to do ==" in text
    assert "Stops: A rule can declare a stop-loss" in text
    assert lab._last_export is not None
    lab.close()


def test_lab_refuses_custom_rule_without_loading_one(qapp):
    from crypto_trading_lab.ui.backtesting.lab import STRATEGY_RULE

    lab = BacktestingLabWidget(_candles(), "BTC/USDT", "1h")
    lab.strategy_combo.addItem("Custom rule", STRATEGY_RULE)
    lab.strategy_combo.setCurrentIndex(lab.strategy_combo.count() - 1)

    message = lab.run_and_display()

    assert "No custom rule loaded" in message
    lab.close()
