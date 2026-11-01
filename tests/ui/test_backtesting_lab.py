"""GUI tests for the Backtesting Lab (ROADMAP.md 37.9, 37.10, 40)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

pytest.importorskip("PyQt6")

from crypto_trading_lab.configuration.xdg import AppPaths  # noqa: E402
from crypto_trading_lab.domain.models import Candle, Symbol  # noqa: E402
from crypto_trading_lab.ui.backtesting.lab import (  # noqa: E402
    BacktestingLabWidget,
)

BASE = datetime(2024, 1, 1, tzinfo=timezone.utc)

HEADER = "timestamp,open,high,low,close,volume\n"
ROWS = "".join(
    f"2024-01-01T00:{m:02d}:00+00:00,100,110,90,105,10\n"
    for m in range(50)
)


def _candles(closes):
    return [
        Candle(
            Symbol("BTC/USDT"),
            "1m",
            BASE + timedelta(minutes=i),
            BASE + timedelta(minutes=i + 1),
            open=Decimal(str(c)),
            high=Decimal(str(c + 1)),
            low=Decimal(str(c - 1)),
            close=Decimal(str(c)),
            volume=Decimal("10"),
        )
        for i, c in enumerate(closes)
    ]


def _trending(n=80):
    """An up-then-down series so the SMA crossover actually trades."""
    return [100 + i for i in range(n // 2)] + [
        100 + n // 2 - i for i in range(n // 2)
    ]




@pytest.fixture()
def lab(qapp):
    widget = BacktestingLabWidget(_candles(_trending()))
    yield widget
    widget.close()


def test_results_show_all_mandatory_fields(lab):
    text = lab.run_and_display()
    # 37.9 catalogue
    for needle in (
        "Initial capital:",
        "Final equity:",
        "Net profit/loss:",
        "Total return:",
        "Number of trades:",
        "Win rate:",
        "Average winning trade:",
        "Average losing trade:",
        "Profit factor:",
        "Maximum drawdown:",
        "Maximum drawdown duration:",
        "Sharpe ratio:",
        "Sortino ratio:",
        "Commissions and fees:",
        "Estimated slippage:",
        "Execution model:",
        "Assumptions: long-only spot;",
        "Historical period:",
        "Dataset version:",
        "version 1.0.0",
        "Benchmark (Buy and hold) return:",
        "Excess return vs benchmark:",
    ):
        assert needle in text, needle


def test_the_report_explains_what_the_strategy_assumes(lab):
    # Chapter 33.9: the ten questions reach the GUI, not only the CLI.
    text = lab.run_and_display()
    assert "== What this strategy is trying to do ==" in text
    assert "What it tries to do:" in text
    assert "How position sizing works:" in text
    assert "Why a profitable backtest is not a promise:" in text


def test_the_report_shows_the_declared_weaknesses_and_warnings(lab):
    # Chapter 33.1: the strategy's own confession travels with its result.
    text = lab.run_and_display()
    assert "Category: trend-following" in text
    assert "Known weaknesses:" in text
    assert "Risk warnings:" in text
    assert "There is no stop." in text


def test_the_report_states_the_market_requirements(lab):
    # Chapter 33.2: the markets and data it can use reach the GUI too.
    text = lab.run_and_display()
    assert "Market requirements (chapter 33.2):" in text
    assert "Supported asset types: spot" in text
    assert "Required market-data fields:" in text
    assert "Minimum historical data (default configuration):" in text


def test_beginner_explanation_and_honesty(lab):
    text = lab.run_and_display()
    # 37.10 + 40.8 mandatory explanations and disclaimers.
    assert "BTC/USDT" in text
    # Chapter 33.8: the statements come from one canonical set shared with
    # the CLI, so they say the same thing on both surfaces.
    assert "IN-SAMPLE" in text
    assert "A strategy can perform well historically by chance" in text
    assert "does not necessarily mean a better strategy" in text
    assert "No single metric proves that a strategy is good" in text
    assert "Commissions and fees are what exchanges charge" in text
    assert "Liquidity matters" in text


def test_null_strategy_shows_small_sample_warnings(qapp):
    widget = BacktestingLabWidget(_candles([100, 101, 102]))
    widget.strategy_combo.setCurrentIndex(2)  # Null
    text = widget.run_and_display()
    assert "no trades" in text
    assert "n/a (insufficient data)" in text
    widget.close()


def test_invalid_parameters_are_explained(qapp):
    widget = BacktestingLabWidget(_candles(_trending()))
    widget.fast_spin.setValue(50)
    widget.slow_spin.setValue(10)
    text = widget.run_and_display()
    assert "must be smaller" in text
    widget.capital_edit.setText("abc")
    text = widget.run_and_display()
    assert "positive number" in text
    widget.close()


def test_report_export_writes_three_formats(lab, tmp_path):
    assert lab.save_report(str(tmp_path / "x")) == []  # nothing run yet
    lab.run_and_display()
    base = tmp_path / "report"
    written = lab.save_report(str(base))
    assert sorted(p.rsplit(".", 1)[-1] for p in written) == [
        "csv", "html", "json"
    ]
    for suffix in (".html", ".csv", ".json"):
        content = (tmp_path / f"report{suffix}").read_text()
        assert "No single metric proves" in content


def test_buy_and_hold_matches_itself_as_benchmark(qapp):
    widget = BacktestingLabWidget(_candles(_trending()))
    widget.strategy_combo.setCurrentIndex(1)  # Buy and hold
    text = widget.run_and_display()
    assert "Excess return vs benchmark: 0" in text
    # Chapter 42.1: identical benchmark must be flagged as useless.
    assert "benchmark is the same strategy" in text
    widget.close()


def test_benchmark_is_selectable_and_compared(lab):
    # Default benchmark (buy and hold) reports a full comparison (42.2).
    text = lab.run_and_display()
    assert "== Benchmark comparison (vs Buy and hold) ==" in text
    assert "Excess return (net of costs):" in text
    assert "Excess return (before costs):" in text
    assert "Cost drag on the comparison:" in text
    assert "Max drawdown difference:" in text
    assert "Sharpe difference:" in text
    # Plain-language verdict (mandatory in 42.2).
    assert ("beat the passive alternative" in text
            or "did NOT beat the passive alternative" in text)

    lab.benchmark_combo.setCurrentIndex(2)  # None
    text = lab.run_and_display()
    assert "No benchmark selected" in text

    lab.benchmark_combo.setCurrentIndex(1)  # Null
    text = lab.run_and_display()
    assert "== Benchmark comparison (vs Null (never trades)) ==" in text


# -- flow through the main window (mirrors test_chart_flow) -------------


@pytest.fixture()
def isolated_xdg(tmp_path):
    return AppPaths(
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        cache_dir=tmp_path / "cache",
        log_dir=tmp_path / "logs",
    )


def test_open_lab_without_data_returns_none(window, isolated_xdg):
    assert window.open_backtesting(paths=isolated_xdg, notify=False) is None


def test_import_then_open_lab(window, isolated_xdg, tmp_path):
    csv_path = tmp_path / "candles.csv"
    csv_path.write_text(HEADER + ROWS, encoding="utf-8")
    window.load_csv_file(str(csv_path), paths=isolated_xdg)
    lab = window.open_backtesting(paths=isolated_xdg, notify=False)
    assert lab is not None
    text = lab.run_and_display()
    assert "Number of trades:" in text
    lab.close()
