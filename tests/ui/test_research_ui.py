"""Behavioural tests for the research UI (chapters 34, 39, 52-55).

These deliberately replaced the old import-only smoke tests: a green
suite must mean the screens work, not merely that they import.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

pytest.importorskip("PyQt6")

from crypto_trading_lab.ai_assistant import AIAssistant  # noqa: E402
from crypto_trading_lab.configuration.xdg import AppPaths  # noqa: E402
from crypto_trading_lab.domain.models import Candle, Symbol  # noqa: E402
from crypto_trading_lab.machine_learning.experiment_manager import (  # noqa: E402
    ExperimentManager,
)
from crypto_trading_lab.market_data.historical import DatasetVersion  # noqa: E402
from crypto_trading_lab.ui.research.assistant import (  # noqa: E402
    LOCAL_BACKEND_NOTICE,
    ResearchAssistant,
    ResearchAssistantDialog,
)
from crypto_trading_lab.ui.research.notebook import NotebookDialog  # noqa: E402
from crypto_trading_lab.ui.research.validity import (  # noqa: E402
    render_research_run,
    render_validity,
)
from crypto_trading_lab.ui.research.wizard import ResearchWizardDialog  # noqa: E402

HOUR = timedelta(hours=1)
START = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _candles(count: int = 220) -> list[Candle]:
    candles = []
    price = Decimal("100")
    for i in range(count):
        price = max(Decimal("10"), price + Decimal(str(0.4 * math.sin(i / 18.0))))
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
                volume=Decimal("1"),
            )
        )
    return candles


def _dataset() -> DatasetVersion:
    return DatasetVersion(
        dataset_id="BINANCE_BTCUSDT_1H_2024_V1",
        exchange="binance",
        symbol="BTC/USDT",
        interval="1h",
        start=START,
        end=START + 220 * HOUR,
        candle_count=220,
        missing=0,
        duplicates=0,
        invalid=0,
        checksum="abc123def456",
        source="test",
        downloaded_at=START,
    )


def _manager(tmp_path) -> ExperimentManager:
    return ExperimentManager(storage_path=tmp_path / "experiments.json")


# -- notebook (chapters 52-54) -------------------------------------------


def test_notebook_creates_lists_and_annotates(qapp, tmp_path):
    manager = _manager(tmp_path)
    dialog = NotebookDialog(manager)

    record = dialog.create_entry("BTC breaks the 20-candle high", notes="first idea")

    assert dialog.list_widget.count() == 1
    detail = dialog.detail_text(record.experiment_id)
    assert "BTC breaks the 20-candle high" in detail

    updated = dialog.add_note("added a volume filter")
    assert updated is not None
    assert "added a volume filter" in updated.notes
    dialog.close()


def test_notebook_compares_two_experiments(qapp, tmp_path):
    manager = _manager(tmp_path)
    dialog = NotebookDialog(manager)
    first = dialog.create_entry("Hypothesis A")
    second = dialog.create_entry("Hypothesis B")
    dialog.refresh()

    dialog.select_experiments([first.experiment_id, second.experiment_id])
    text = dialog.compare_selected()

    assert "Experiment comparison" in text
    assert "Hypothesis A" in text
    assert "Hypothesis B" in text
    dialog.close()


def test_notebook_exports_records(qapp, tmp_path):
    manager = _manager(tmp_path)
    dialog = NotebookDialog(manager)
    dialog.create_entry("Exportable hypothesis")

    target = dialog.export_to(tmp_path / "export.json")

    assert target.exists()
    assert "Exportable hypothesis" in target.read_text(encoding="utf-8")
    dialog.close()


# -- assistant (chapter 55) ----------------------------------------------


def test_assistant_answers_from_methodology_not_canned_context():
    assistant = ResearchAssistant()
    answer = assistant.answer(
        "How do I avoid overfitting on BTC?", "Strategy development"
    )

    assert "How do I avoid overfitting on BTC?" in answer
    assert LOCAL_BACKEND_NOTICE in answer
    assert "multiple testing" in answer.lower()
    assert assistant.has_model_backend is False


def test_assistant_uses_a_real_backend_when_provided():
    calls = []

    def backend(question: str, context: str) -> str:
        calls.append((question, context))
        return "model answer"

    assistant = ResearchAssistant(backend=backend)
    assert assistant.answer("q", "ctx") == "model answer"
    assert calls == [("q", "ctx")]
    assert assistant.has_model_backend is True


def test_assistant_mentions_the_users_own_experiments(tmp_path):
    manager = _manager(tmp_path)
    manager.create(
        hypothesis="RSI mean reversion",
        strategy_name="rsi",
        strategy_version="1.0.0",
        dataset_version="v1",
        parameters={},
    )
    answer = ResearchAssistant(manager=manager).answer(
        "what next?", "Risk assessment"
    )
    assert "RSI mean reversion" in answer


def test_assistant_dialog_persists_the_conversation(qapp, tmp_path):
    store = AIAssistant(tmp_path / "ai")
    dialog = ResearchAssistantDialog(
        manager=_manager(tmp_path), assistant=store
    )
    dialog.question_field.setPlainText("Does my strategy have an edge?")

    response = dialog.ask()

    assert "edge" in response.lower()
    assert dialog.conversation_id is not None
    history = store.get_conversation_history(dialog.conversation_id)
    assert any(m["role"] == "user" for m in history)
    assert any(m["role"] == "assistant" for m in history)
    dialog.close()


# -- wizard + validity dashboard (analysis §15-16) -----------------------


def test_wizard_runs_research_and_records_it(qapp, tmp_path):
    manager = _manager(tmp_path)
    dialog = ResearchWizardDialog(_candles(220), _dataset(), manager)
    dialog.hypothesis_edit.setText("SMA crossover has an edge")
    dialog.fast_spin.setValue(5)
    dialog.slow_spin.setValue(20)
    dialog.robustness_check.setChecked(False)  # keep the test fast
    dialog.benchmark_check.setChecked(True)

    run = dialog.run()

    assert run is not None
    assert run.experiment is not None
    assert manager.get(run.experiment.experiment_id) is not None
    text = dialog.results.view.toPlainText()
    assert "RESEARCH VALIDITY" in text
    assert "liquidity_realism" in text
    dialog.close()


def test_wizard_refuses_to_run_without_a_dataset(qapp, tmp_path):
    dialog = ResearchWizardDialog(_candles(50), None, _manager(tmp_path))
    dialog.hypothesis_edit.setText("No dataset")

    result = dialog.run()

    assert result is None
    assert dialog.run_button.isEnabled() is False
    dialog.close()


def test_wizard_requires_a_hypothesis(qapp, tmp_path):
    dialog = ResearchWizardDialog(_candles(220), _dataset(), _manager(tmp_path))
    dialog.run_button.setEnabled(True)

    assert dialog.run() is None
    assert "hypothesis" in dialog.results.view.toPlainText().lower()
    dialog.close()


def test_validity_renderer_flags_unmet_checks(qapp, tmp_path):
    dialog = ResearchWizardDialog(_candles(220), _dataset(), _manager(tmp_path))
    dialog.hypothesis_edit.setText("Validity rendering")
    dialog.robustness_check.setChecked(False)
    dialog.walk_forward_check.setChecked(False)

    run = dialog.run()
    assert run is not None

    text = render_validity(run)
    assert "RESEARCH VALIDITY" in text
    assert "walk_forward" in text
    assert "observed result only" in render_research_run(run)
    dialog.close()


# -- strategy builder (chapter 34) ---------------------------------------


def test_strategy_builder_validates_and_exports(qapp):
    from crypto_trading_lab.ui.strategy_builder import StrategyBuilderDialog

    dialog = StrategyBuilderDialog()
    dialog.name_edit.setText("EMA + RSI")
    dialog.add_block("indicator", indicator_type="ema", params={"period": 200})
    dialog.add_block("crossover")
    dialog.add_block("entry")

    warnings = dialog.validate()
    # An entry exists but no exit: the rule must be reported incomplete.
    assert any("exit" in w.lower() for w in warnings)

    exported = dialog.export_rule_text()
    assert "EMA + RSI" in exported

    other = StrategyBuilderDialog()
    rule = other.import_rule_text(exported)
    assert rule is not None
    assert rule.name == "EMA + RSI"
    assert other.blocks_view.count() == 3
    dialog.close()
    other.close()


def test_strategy_builder_import_rejects_garbage(qapp):
    from crypto_trading_lab.ui.strategy_builder import StrategyBuilderDialog

    dialog = StrategyBuilderDialog()
    assert dialog.import_rule_text("not json") is None
    assert "not a valid strategy rule" in dialog.feedback.toPlainText()
    dialog.close()


# -- backtesting lab research tools (chapters 35, 39) --------------------


def test_lab_complexity_and_parameter_sweep(qapp):
    from crypto_trading_lab.ui.backtesting.lab import BacktestingLabWidget

    lab = BacktestingLabWidget(_candles(300), "BTC/USDT", "1h")
    complexity = lab.analyze_complexity()
    assert "complexity" in complexity.lower()
    # Chapter 35: the report shows what the strategy version declares, not
    # only how complicated its Python class is.
    assert "What this strategy version declares" in complexity
    assert "Parameter grid" in complexity

    lab.fast_spin.setValue(5)
    lab.slow_spin.setValue(20)
    sweep = lab.optimize_parameters()

    assert "Parameter sweep" in sweep
    assert "EXPLORATION" in sweep
    assert lab.trials > 0
    lab.close()


def test_lab_parameter_sweep_refuses_non_sma(qapp):
    from crypto_trading_lab.ui.backtesting.lab import BacktestingLabWidget

    lab = BacktestingLabWidget(_candles(120), "BTC/USDT", "1h")
    lab.strategy_combo.setCurrentIndex(1)  # buy and hold

    message = lab.optimize_parameters()

    assert "SMA" in message
    lab.close()


# -- main window wiring --------------------------------------------------


def test_main_window_opens_notebook_without_crashing(qapp, tmp_path, monkeypatch):
    from crypto_trading_lab.ui.main_window.window import MainWindow

    window = MainWindow()
    paths = AppPaths(
        config_dir=tmp_path / "c",
        data_dir=tmp_path / "d",
        cache_dir=tmp_path / "k",
        log_dir=tmp_path / "l",
    )
    monkeypatch.setattr(window, "_paths", lambda: paths)

    window._open_notebook()  # used to raise AttributeError

    assert window._notebook_window is not None
    window._notebook_window.close()
    window.close()


def test_main_window_opens_assistant(qapp, tmp_path, monkeypatch):
    from crypto_trading_lab.ui.main_window.window import MainWindow

    window = MainWindow()
    paths = AppPaths(
        config_dir=tmp_path / "c",
        data_dir=tmp_path / "d",
        cache_dir=tmp_path / "k",
        log_dir=tmp_path / "l",
    )
    monkeypatch.setattr(window, "_paths", lambda: paths)

    window._open_assistant()

    assert window._assistant_window is not None
    window._assistant_window.close()
    window.close()
