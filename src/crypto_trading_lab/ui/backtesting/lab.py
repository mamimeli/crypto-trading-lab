"""Backtesting Lab window (ROADMAP.md chapters 37.9, 37.10 and 40).

Runs the chapter 37 engine over imported candles and shows every
result with the chapter 40 metrics, the statistical-validity warnings
and the mandatory beginner-oriented explanation. A profitable backtest
is never presented as proof that a strategy will be profitable.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from crypto_trading_lab.backtesting.engine import (
    BacktestConfig,
    BuyAndHoldStrategy,
    MACrossoverStrategy,
    NullStrategy,
    run_backtest,
)

from crypto_trading_lab.optimization import (
    run_optimization,
    OBJECTIVE_SHARPE_RATIO,
    OptimizationConfig,
    ParameterRange,
)

from crypto_trading_lab.complexity_control import (
    analyze_strategy_complexity,
    COMPLEXITY_CONTROL_WARNING,
    STRATEGY_COMPLEXITY_EXPLANATION,
    strategy_complexity_from_rule,
)

from crypto_trading_lab.backtesting.metrics import (
    DISCLAIMER,
    compare_reports,
    compute_performance,
)
from crypto_trading_lab.domain.models import Candle
from crypto_trading_lab.rule_strategy import (
    RuleError,
    RuleStrategy,
    RuleStrategySpec,
)

from crypto_trading_lab.strategy_registry import StrategyRegistry
from crypto_trading_lab.research_warnings import warnings_for_run
from crypto_trading_lab.strategy_guide import (
    SIZING,
    STOPS_RULE,
    guide_for,
    render as render_guide,
)
from crypto_trading_lab.strategy_identity import identity_for
from crypto_trading_lab.market_requirements import (
    market_requirements_for,
    render_market_requirements,
)

STRATEGY_SMA = "ma_crossover"
STRATEGY_BUY_HOLD = "buy_and_hold"
STRATEGY_NULL = "null_strategy"
STRATEGY_RULE = "custom_rule"


class BacktestingLabWidget(QWidget):
    """Run a backtest over loaded candles and show honest results."""

    def __init__(
        self,
        candles: Sequence[Candle],
        symbol: str = "BTC/USDT",
        interval: str = "1m",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._candles = list(candles)
        self._symbol = symbol
        self._interval = interval
        self._rule_spec: RuleStrategySpec | None = None

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.registry = StrategyRegistry()
        self.strategy_combo = QComboBox()
        # Chapter 36: the registry is the single source of truth for which
        # strategies exist, and only the entries that can actually be
        # instantiated are offered — a registry restored from JSON carries
        # metadata without a factory, and offering those would only produce a
        # failed run. The visible labels stay literal `self.tr()` strings so
        # `pylupdate6` can extract them; a strategy registered by other code
        # falls back to its own (untranslatable) registry name.
        builtin_labels = {
            STRATEGY_SMA: self.tr("SMA crossover"),
            STRATEGY_BUY_HOLD: self.tr("Buy and hold"),
            STRATEGY_NULL: self.tr("Null (never trades)"),
        }
        for meta in self.registry.list_strategies():
            if self.registry.get_factory(meta.strategy_id) is None:
                continue
            label = builtin_labels.get(meta.strategy_id, meta.name)
            self.strategy_combo.addItem(label, meta.strategy_id)
        self.strategy_combo.addItem(self.tr("Custom Rule"), STRATEGY_RULE)
        form.addRow(self.tr("Strategy:"), self.strategy_combo)

        parameters = QHBoxLayout()
        self.fast_spin = QSpinBox()
        self.fast_spin.setRange(2, 500)
        self.fast_spin.setValue(10)
        self.slow_spin = QSpinBox()
        self.slow_spin.setRange(3, 1000)
        self.slow_spin.setValue(30)
        parameters.addWidget(self.fast_spin)
        parameters.addWidget(self.slow_spin)
        form.addRow(self.tr("SMA fast / slow:"), parameters)

        self.capital_edit = QLineEdit("10000")
        form.addRow(self.tr("Initial capital:"), self.capital_edit)

        # Chapter 42.1: benchmark selection must be visible and changeable.
        self.benchmark_combo = QComboBox()
        self.benchmark_combo.addItem(
            self.tr("Buy and hold (default)"), STRATEGY_BUY_HOLD
        )
        self.benchmark_combo.addItem(
            self.tr("Null (never trades)"), STRATEGY_NULL
        )
        self.benchmark_combo.addItem(self.tr("None"), None)
        form.addRow(self.tr("Benchmark:"), self.benchmark_combo)
        layout.addLayout(form)

        self.run_button = QPushButton(self.tr("Run backtest"))
        self.run_button.clicked.connect(self.run_and_display)
        layout.addWidget(self.run_button)

        self.save_button = QPushButton(self.tr("Save report (HTML/CSV/JSON)"))
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save_dialog)
        layout.addWidget(self.save_button)
        self._last_export: tuple | None = None  # (result, report, warning)

        tools = QHBoxLayout()
        self.complexity_button = QPushButton(self.tr("Analyze complexity"))
        self.complexity_button.clicked.connect(self.analyze_complexity)
        self.optimize_button = QPushButton(self.tr("Parameter sweep…"))
        self.optimize_button.clicked.connect(self.optimize_parameters)
        self.load_rule_button = QPushButton(self.tr("Load rule…"))
        self.load_rule_button.clicked.connect(self._load_rule_dialog)
        tools.addWidget(self.complexity_button)
        tools.addWidget(self.optimize_button)
        tools.addWidget(self.load_rule_button)
        layout.addLayout(tools)
        #: Number of configurations the user has evaluated for this idea,
        #: used for the multiple-testing warning (chapter 43.1).
        self.trials = 0

        self.results_view = QTextBrowser()
        self.results_view.setPlainText(
            self.tr(
                "Choose a strategy and press “Run backtest”. Every "
                "result is shown with its risks, costs and statistical "
                "warnings."
            )
        )
        layout.addWidget(self.results_view)

    # -- the actual work (kept side-effect free for tests) ---------------

    def run_and_display(self) -> str:
        """Run the selected backtest, render results, return the text.

        Returns the rendered text so tests can assert on it; on invalid
        input an explanation is shown and returned instead.
        """
        try:
            capital = Decimal(self.capital_edit.text().strip())
            if capital <= 0:
                raise ValueError
        except Exception:
            message = self.tr(
                "Initial capital must be a positive number, "
                "for example 10000."
            )
            self.results_view.setPlainText(message)
            return message

        kind = self.strategy_combo.currentData()
        if kind == STRATEGY_RULE:
            if self._rule_spec is None:
                message = self.tr(
                    "No custom rule loaded. Use “Load rule…” to open one "
                    "exported by the Strategy Builder."
                )
                self.results_view.setPlainText(message)
                return message
            strategy = RuleStrategy(self._rule_spec)
        else:
            # Only pass parameters to SMA
            if kind == STRATEGY_SMA:
                fast, slow = self.fast_spin.value(), self.slow_spin.value()
                if fast >= slow:
                    message = self.tr(
                        "The fast SMA period must be smaller than the slow "
                        "one (for example 10 and 30)."
                    )
                    self.results_view.setPlainText(message)
                    return message
                strategy = self.registry.create_instance(kind, fast=fast, slow=slow)
            else:
                strategy = self.registry.create_instance(kind)

            # `create_instance` returns None for an id that is not registered
            # (or that was restored from JSON without a factory). Running a
            # backtest with None would fail far from the cause, so stop here
            # with a message the user can act on.
            if strategy is None:
                message = self.tr(
                    "The selected strategy could not be created. Choose "
                    "another one from the list and run again."
                )
                self.results_view.setPlainText(message)
                return message

        config = BacktestConfig(initial_capital=capital)
        result = run_backtest(self._candles, strategy, config)

        benchmark_kind = self.benchmark_combo.currentData()
        benchmark_warning: str | None = None
        benchmark_result = None
        benchmark_report = None
        if benchmark_kind is not None:
            benchmark_strategy = (
                BuyAndHoldStrategy()
                if benchmark_kind == STRATEGY_BUY_HOLD
                else NullStrategy()
            )
            benchmark_result = run_backtest(
                self._candles, benchmark_strategy, config
            )
            benchmark_report = compute_performance(benchmark_result)
            if benchmark_kind == kind:
                benchmark_warning = self.tr(
                    "The chosen benchmark is the same strategy you are "
                    "testing: the excess return is 0 by construction. "
                    "Pick a different benchmark for a meaningful "
                    "comparison."
                )
        report = compute_performance(result, benchmark=benchmark_result)

        self._last_export = (result, report, benchmark_warning)
        self.save_button.setEnabled(True)
        # Chapter 33.8: the statements that apply to this run.
        complexity = self._declared_complexity()
        research_warnings = warnings_for_run(
            parameters=(
                complexity.num_parameters if complexity is not None else 0
            ),
            filters=complexity.num_filters if complexity is not None else 0,
            complexity_recorded=complexity is not None,
        )
        text = self._render(result, report, benchmark_warning,
                            benchmark_report, research_warnings,
                            strategy_id=kind)
        self.results_view.setPlainText(text)
        return text

    # -- report export (chapter 41) --------------------------------------

    def save_report(self, base_path: str) -> list[str]:
        """Write the last run as ``.html``, ``.csv`` and ``.json``.

        Returns the written file paths; empty list when nothing has
        been run yet.
        """
        if self._last_export is None:
            return []
        from crypto_trading_lab.reporting.report import (
            build_backtest_report,
            render_csv,
            render_html,
            render_json,
        )

        result, performance = self._last_export[0], self._last_export[1]
        data = build_backtest_report(
            result, performance, self._symbol, self._interval
        )
        written: list[str] = []
        for suffix, render in (
            (".html", render_html),
            (".csv", render_csv),
            (".json", render_json),
        ):
            path = base_path + suffix
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(render(data))
            written.append(path)
        return written

    # -- research tools: complexity and parameter sweep (ch. 35, 39) -----

    def set_rule_spec(self, spec: RuleStrategySpec) -> str:
        """Make a builder rule available as a backtestable strategy."""
        self._rule_spec = spec
        label = self.tr("Custom rule: {name}").format(name=spec.name)
        for index in range(self.strategy_combo.count()):
            if self.strategy_combo.itemData(index) == STRATEGY_RULE:
                self.strategy_combo.setItemText(index, label)
                self.strategy_combo.setCurrentIndex(index)
                return label
        self.strategy_combo.addItem(label, STRATEGY_RULE)
        self.strategy_combo.setCurrentIndex(self.strategy_combo.count() - 1)
        return label

    def load_rule(self, path: str) -> RuleStrategySpec | None:
        """Load a rule JSON exported by the Strategy Builder."""
        import json

        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            spec = RuleStrategySpec.from_dict(data)
        except (OSError, ValueError, RuleError) as error:
            self.results_view.setPlainText(
                self.tr("Could not load the rule: {error}").format(error=error)
            )
            return None
        self.set_rule_spec(spec)
        self.results_view.setPlainText(
            self.tr("Loaded rule “{name}”: {description}").format(
                name=spec.name, description=spec.describe()
            )
        )
        return spec

    def _load_rule_dialog(self) -> None:
        from PyQt6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Load rule"), "", self.tr("JSON (*.json)")
        )
        if path:
            self.load_rule(path)

    def _strategy_class(self):
        """Class of the currently selected strategy (for complexity)."""
        kind = self.strategy_combo.currentData()
        if kind == STRATEGY_SMA:
            return MACrossoverStrategy
        if kind == STRATEGY_BUY_HOLD:
            return BuyAndHoldStrategy
        if kind == STRATEGY_RULE:
            return RuleStrategy
        return NullStrategy

    def _declared_complexity(self):
        """Chapter 35 metrics for the selected strategy, or ``None``."""
        kind = self.strategy_combo.currentData()
        if kind == STRATEGY_RULE:
            return (
                strategy_complexity_from_rule(self._rule_spec)
                if self._rule_spec is not None
                else None
            )
        registration = self.registry.get(kind)
        if registration is None:
            return None
        return registration.metadata.complexity

    def analyze_complexity(self) -> str:
        """Chapter 35 report for the selected strategy, shown to the user."""
        try:
            report = analyze_strategy_complexity(self._strategy_class())
        except Exception as error:  # source may be unavailable when frozen
            message = self.tr(
                "Complexity analysis is unavailable here: {error}"
            ).format(error=error)
            self.results_view.setPlainText(message)
            return message
        lines = [
            self.tr("== Strategy complexity (chapter 35) =="),
            self.tr("Level: {level}").format(level=report.level.value),
            self.tr("Cyclomatic complexity: {x}").format(
                x=report.metrics.cyclomatic_complexity
            ),
            self.tr("Lines of code: {x}").format(x=report.metrics.lines_of_code),
            self.tr("Parameters: {x}").format(x=report.metrics.num_parameters),
            self.tr("Passed the configured limits: {x}").format(
                x=report.passed
            ),
        ]
        lines.extend(f"  - {v}" for v in report.violations)
        lines.extend(f"  - {w}" for w in report.warnings)

        declared = self._declared_complexity()
        if declared is not None:
            lines.extend(
                [
                    "",
                    self.tr("-- What this strategy version declares --"),
                    self.tr("Parameters: {x}").format(x=declared.num_parameters),
                    self.tr("Rules: {x}").format(x=declared.num_rules),
                    self.tr("Indicators: {x}").format(x=declared.num_indicators),
                    self.tr("Filters: {x}").format(x=declared.num_filters),
                    self.tr("Conditions: {x}").format(x=declared.num_conditions),
                    self.tr("Parameter grid: {x} configuration(s)").format(
                        x=declared.optimization_complexity
                    ),
                    self.tr("Complexity score: {x}").format(x=declared.score),
                ]
            )

        lines.append("")
        lines.append(self.tr(COMPLEXITY_CONTROL_WARNING))
        lines.append(self.tr(STRATEGY_COMPLEXITY_EXPLANATION))
        lines.append(
            self.tr(
                "Remember: when two strategies show comparable evidence, "
                "the simpler one is preferred."
            )
        )
        text = "\n".join(lines)
        self.results_view.setPlainText(text)
        return text

    def optimize_parameters(self) -> str:
        """Real parameter sweep (chapter 39) with honest accounting.

        The sweep is *exploration*: choosing the best of many
        configurations is selection bias, so the number of trials is
        reported and carried into the multiple-testing warning.
        """
        if self.strategy_combo.currentData() != STRATEGY_SMA:
            message = self.tr(
                "The parameter sweep currently supports the SMA "
                "crossover strategy only."
            )
            self.results_view.setPlainText(message)
            return message
        fast, slow = self.fast_spin.value(), self.slow_spin.value()
        if fast >= slow:
            message = self.tr(
                "The fast SMA period must be smaller than the slow one "
                "before sweeping."
            )
            self.results_view.setPlainText(message)
            return message

        ranges = [
            ParameterRange(
                "fast", float(max(2, fast - 5)), float(min(slow - 1, fast + 5)), 5
            ),
            ParameterRange(
                "slow", float(fast + 1), float(slow + 10), 5
            ),
        ]
        config = OptimizationConfig(parameter_ranges=ranges, max_combinations=64)
        try:
            capital = Decimal(self.capital_edit.text().strip())
            report = run_optimization(
                self._candles,
                lambda fast, slow: MACrossoverStrategy(
                    fast=int(fast), slow=int(slow)
                ),
                config,
                OBJECTIVE_SHARPE_RATIO,
                BacktestConfig(initial_capital=capital),
            )
        except ValueError as error:
            message = self.tr("The sweep found nothing to evaluate: {error}").format(
                error=error
            )
            self.results_view.setPlainText(message)
            return message

        self.trials += report.n_combinations_tested
        lines = [
            self.tr("== Parameter sweep (chapter 39) =="),
            self.tr("Configurations tested: {x}").format(
                x=report.n_combinations_tested
            ),
            self.tr("Best parameters: {x}").format(x=report.best_parameters),
            self.tr("Objective ({name}) value: {x}").format(
                name=report.objective_name,
                x=report.best_result.objective_value,
            ),
            self.tr("Best backtest return: {x}").format(
                x=report.best_result.backtest_return
            ),
            self.tr("Trades in the best configuration: {x}").format(
                x=report.best_result.n_trades
            ),
        ]
        lines.extend(f"  - {w}" for w in report.overfitting_warnings)
        lines += [
            "",
            self.tr(
                "This sweep is EXPLORATION, not validation: picking the "
                "best of {n} configurations makes a good historical "
                "result more likely to be luck. Total configurations "
                "tried for this idea so far: {total}."
            ).format(
                n=report.n_combinations_tested, total=self.trials
            ),
            self.tr(
                "Confirm the winner out-of-sample and with walk-forward "
                "analysis before believing it."
            ),
        ]
        text = "\n".join(lines)
        self.results_view.setPlainText(text)
        return text

    def launch_rule_parameter_sweep(self) -> str:
        """Parameter sweep for a RuleStrategy (chapter 77).

        Sweeps numeric parameters from the loaded rule:
        - stop_loss_fraction (if present)
        - take_profit_fraction (if present)
        - Indicator periods in entry/exit conditions
        """
        if self._rule_spec is None:
            message = self.tr("No custom rule loaded for sweep.")
            self.results_view.setPlainText(message)
            return message

        spec = self._rule_spec
        ranges = self._build_sweep_ranges(spec)

        if not ranges:
            message = self.tr(
                "No sweepable parameters found in this rule. "
                "Add a stop-loss, take-profit, or indicators with periods."
            )
            self.results_view.setPlainText(message)
            return message

        try:
            capital = Decimal(self.capital_edit.text().strip())
            if capital <= 0:
                raise ValueError
        except Exception:
            message = self.tr(
                "Initial capital must be a positive number, "
                "for example 10000."
            )
            self.results_view.setPlainText(message)
            return message

        config = OptimizationConfig(parameter_ranges=ranges, max_combinations=64)
        try:
            report = run_optimization(
                self._candles,
                lambda **params: RuleStrategy(self._make_spec_variant(spec, params)),
                config,
                OBJECTIVE_SHARPE_RATIO,
                BacktestConfig(initial_capital=capital),
            )
        except ValueError as error:
            message = self.tr("The sweep found nothing to evaluate: {error}").format(
                error=error
            )
            self.results_view.setPlainText(message)
            return message

        self.trials += report.n_combinations_tested
        lines = [
            self.tr("== Parameter sweep: {name} (chapter 39, 77) ==").format(
                name=spec.name
            ),
            self.tr("Configurations tested: {x}").format(
                x=report.n_combinations_tested
            ),
            self.tr("Best parameters: {x}").format(x=report.best_parameters),
            self.tr("Objective ({name}) value: {x}").format(
                name=report.objective_name,
                x=report.best_result.objective_value,
            ),
            self.tr("Best backtest return: {x}").format(
                x=report.best_result.backtest_return
            ),
            self.tr("Trades in the best configuration: {x}").format(
                x=report.best_result.n_trades
            ),
        ]
        lines.extend(f"  - {w}" for w in report.overfitting_warnings)
        lines += [
            "",
            self.tr(
                "This sweep is EXPLORATION, not validation: picking the "
                "best of {n} configurations makes a good historical "
                "result more likely to be luck. Total configurations "
                "tried for this idea so far: {total}."
            ).format(
                n=report.n_combinations_tested, total=self.trials
            ),
            self.tr(
                "Confirm the winner out-of-sample and with walk-forward "
                "analysis before believing it."
            ),
        ]
        text = "\n".join(lines)
        self.results_view.setPlainText(text)
        return text

    def _build_sweep_ranges(self, spec: RuleStrategySpec) -> list:
        """Extract sweepable parameters from a RuleStrategySpec."""
        ranges = []

        # Stop-loss fraction
        if spec.stop_loss_fraction is not None:
            base = float(spec.stop_loss_fraction)
            ranges.append(ParameterRange(
                "stop_loss_fraction",
                max(0.01, base * 0.5),
                min(0.5, base * 2.0),
                step=0.01
            ))

        # Take-profit fraction
        if spec.take_profit_fraction is not None:
            base = float(spec.take_profit_fraction)
            ranges.append(ParameterRange(
                "take_profit_fraction",
                max(0.01, base * 0.5),
                min(1.0, base * 2.0),
                step=0.01
            ))

        # Indicator periods from entry conditions
        for condition in spec.entry:
            self._extract_indicator_periods(condition.left, ranges)
            self._extract_indicator_periods(condition.right, ranges)

        # Indicator periods from exit conditions
        for condition in spec.exit:
            self._extract_indicator_periods(condition.left, ranges)
            self._extract_indicator_periods(condition.right, ranges)

        return ranges

    def _extract_indicator_periods(self, operand: str, ranges: list) -> None:
        """Extract indicator period from operand and add to ranges."""
        import re
        match = re.match(r'^(sma|ema|rsi|atr|roc)\((\d+)\)$', operand.strip().lower())
        if match:
            name, period = match.group(1), int(match.group(2))
            param_name = f"{name}_{period}"
            # Only add if not already in ranges
            if not any(r.name == param_name for r in ranges):
                ranges.append(ParameterRange(
                    param_name,
                    max(2, period - 5),
                    period + 10,
                    step=5
                ))

    def _make_spec_variant(self, spec: RuleStrategySpec, params: dict) -> RuleStrategySpec:
        """Create a variant of the spec with updated parameters."""
        import re

        # Update stop_loss and take_profit
        stop_loss = params.get("stop_loss_fraction", spec.stop_loss_fraction)
        take_profit = params.get("take_profit_fraction", spec.take_profit_fraction)

        # Update indicator periods in conditions
        def update_conditions(conditions):
            updated = []
            for c in conditions:
                left = self._update_operand(c.left, params)
                right = self._update_operand(c.right, params)
                updated.append(type(c)(left, c.operator, right))
            return tuple(updated)

        return type(spec)(
            name=spec.name,
            entry=update_conditions(spec.entry),
            exit=update_conditions(spec.exit),
            entry_mode=spec.entry_mode,
            exit_mode=spec.exit_mode,
            stop_loss_fraction=Decimal(str(stop_loss)) if stop_loss is not None else None,
            take_profit_fraction=Decimal(str(take_profit)) if take_profit is not None else None,
            version=spec.version,
        )

    def _update_operand(self, operand: str, params: dict) -> str:
        """Update indicator period in operand based on params."""
        import re
        match = re.match(r'^(sma|ema|rsi|atr|roc)\((\d+)\)$', operand.strip().lower())
        if match:
            name, period = match.group(1), int(match.group(2))
            param_name = f"{name}_{period}"
            if param_name in params:
                new_period = int(params[param_name])
                return f"{name}({new_period})"
        return operand

    def _save_dialog(self) -> None:
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        base, _filter = QFileDialog.getSaveFileName(
            self,
            self.tr("Save report"),
            "backtest_report",
            self.tr("Report base name (*)"),
        )
        if not base:
            return
        for suffix in (".html", ".csv", ".json"):
            if base.endswith(suffix):
                base = base[: -len(suffix)]
        written = self.save_report(base)
        QMessageBox.information(
            self,
            self.tr("Report"),
            self.tr("Saved: {files}").format(files=", ".join(written)),
        )

    def _render(self, result, report, benchmark_warning: str | None = None,
                benchmark_report=None,
                research_warnings: tuple[str, ...] = (),
                strategy_id: str = "") -> str:
        """Plain-language result report (chapters 37.9, 37.10, 40.8)."""
        r, s, risk, a = report.returns, report.trades, report.risk, report.activity
        lines = [
            self.tr("== What was tested =="),
            self.tr("Strategy: {name} (version {version})").format(
                name=result.strategy_name, version=result.strategy_version
            ),
            self.tr("Asset and timeframe: {symbol}, {interval} candles").format(
                symbol=self._symbol, interval=self._interval
            ),
            self.tr("Historical period: {period} ({n} candles)").format(
                period=result.dataset_period, n=result.candle_count
            ),
            self.tr("Dataset version: {version}").format(
                version=result.dataset_version
            ),
            self.tr("Execution model: {model} (signals at a candle's close "
              "fill at the NEXT candle's open — no look-ahead)").format(
                model=result.config_metadata.get("execution_model")
            ),
            self.tr("Assumptions: long-only spot; every order fills "
              "completely at the modeled price (no rejections, no "
              "partial fills); taker fee {fee}, slippage {slip}, "
              "spread {spread} per trade.").format(
                fee=result.config_metadata.get("taker_fee"),
                slip=result.config_metadata.get("slippage_fraction"),
                spread=result.config_metadata.get("spread_fraction"),
            ),
            "",
        ]
        # Chapter 33.9: the ten questions, answered next to the number they
        # explain rather than in a manual nobody opens mid-decision.
        lines.extend(self._guide_lines(strategy_id))
        lines += [
            self.tr("== Money (all costs included) =="),
            self.tr("Initial capital: {x}").format(x=r.initial_capital),
            self.tr("Final equity: {x}").format(x=r.final_equity),
            self.tr("Net profit/loss: {x}").format(x=r.net_profit),
            self.tr("Total return: {x}").format(x=r.total_return),
            self.tr("Annualized return: {x}").format(
                x=self._fmt(r.annualized_return, r.annualized_is_valid)
            ),
            "",
            self.tr("== Trades =="),
            self.tr("Number of trades: {x}").format(x=s.number_of_trades),
            self.tr("Win rate: {x}").format(x=self._fmt(s.win_rate)),
            self.tr("Average winning trade: {x}").format(
                x=self._fmt(s.average_winning_trade)
            ),
            self.tr("Average losing trade: {x}").format(
                x=self._fmt(s.average_losing_trade)
            ),
            self.tr("Profit factor: {x}").format(x=self._fmt(s.profit_factor)),
            "",
            self.tr("== Risk =="),
            self.tr("Maximum drawdown: {x} (worst drop from a previous "
              "peak)").format(x=risk.max_drawdown),
            self.tr("Maximum drawdown duration: {x} candles").format(
                x=risk.max_drawdown_duration
            ),
            self.tr("Sharpe ratio: {x}").format(
                x=self._fmt(risk.sharpe_ratio, risk.sharpe_is_valid)
            ),
            self.tr("Sortino ratio: {x}").format(
                x=self._fmt(risk.sortino_ratio, risk.sortino_is_valid)
            ),
            self.tr("Market exposure: {x} of candles in the market").format(
                x=risk.market_exposure
            ),
            "",
            self.tr("== Costs and benchmark =="),
            self.tr("Commissions and fees: {x}").format(x=a.trading_fees),
            self.tr("Estimated slippage: {x}").format(x=a.slippage_cost),
            self.tr("Estimated spread cost: {x}").format(x=a.spread_cost),
            self.tr("Benchmark ({name}) return: {x}").format(
                name=report.benchmark.benchmark_name
                if report.benchmark
                else self.tr("none"),
                x=report.benchmark.benchmark_return
                if report.benchmark
                else "n/a",
            ),
            self.tr("Excess return vs benchmark: {x}").format(
                x=report.benchmark.excess_return
                if report.benchmark
                else "n/a"
            ),
            "",
        ]
        lines.extend(self._comparison_lines(report, benchmark_report))
        lines.append(self.tr("== Warnings =="))
        if benchmark_warning:
            lines.append(f"  • {benchmark_warning}")
        lines.extend(f"  • {w}" for w in report.warnings)
        if not report.warnings:
            lines.append(self.tr("  (none)"))
        lines += [
            "",
            self.tr("== Please read before trusting this =="),
            self.tr(
                "• Commissions and fees are what exchanges charge per "
                "trade; spread and slippage are the extra cost of "
                "buying a bit too high and selling a bit too low."
            ),
            self.tr(
                "• Liquidity matters: real orders move the price, so "
                "real fills can be worse than simulated ones."
            ),
        ]
        # Chapter 33.8: the canonical statements, shared with the CLI, so the
        # two surfaces cannot drift into saying slightly different things.
        lines.extend(f"• {statement}" for statement in research_warnings)
        lines += [
            "",
            DISCLAIMER,
        ]
        return "\n".join(lines)

    def _guide_lines(self, strategy_id: str) -> list[str]:
        """Chapter 33.9: what this strategy is trying to do, in plain words.

        A strategy without a guide gets one honest line saying so instead of
        a silently shorter report: a missing guide is a documentation gap the
        reader deserves to see.
        """
        if strategy_id == STRATEGY_RULE:
            return [
                self.tr("== What this rule is trying to do =="),
                self.tr("Sizing: {x}").format(x=SIZING),
                self.tr("Stops: {x}").format(x=STOPS_RULE),
                "",
            ]
        guide = guide_for(strategy_id)
        if guide is None:
            if not strategy_id:
                return []
            return [
                self.tr("== What this strategy is trying to do =="),
                self.tr(
                    "  No beginner guide is written for “{x}” yet. Treat "
                    "every number below as a description of the past that "
                    "nobody has explained."
                ).format(x=strategy_id),
                "",
            ]
        lines = [self.tr("== What this strategy is trying to do ==")]
        # Chapter 33.1: the weaknesses and risk warnings the strategy itself
        # declares, next to the result they apply to.
        identity = identity_for(strategy_id)
        if identity is not None:
            lines.append(
                self.tr("Category: {x}").format(x=identity.category)
            )
            lines.append(self.tr("Known weaknesses:"))
            lines.extend(f"  - {item}" for item in identity.known_weaknesses)
            lines.append(self.tr("Risk warnings:"))
            lines.extend(f"  - {item}" for item in identity.risk_warnings)
            lines.append("")
        # Chapter 33.2: the markets and data it can actually use, so the
        # reader knows when a result does not apply to their market.
        requirements = market_requirements_for(strategy_id)
        if requirements is not None:
            lines.append(self.tr("Market requirements (chapter 33.2):"))
            lines.extend(
                render_market_requirements(requirements).splitlines()
            )
            lines.append("")
        lines.extend([render_guide(guide), ""])
        return lines

    def _comparison_lines(self, report, benchmark_report) -> list[str]:
        """Relative benchmark comparison (chapter 42.2)."""
        if report.benchmark is None or benchmark_report is None:
            return [
                self.tr("== Benchmark comparison =="),
                self.tr(
                    "  No benchmark selected — absolute performance "
                    "alone cannot tell you whether the strategy added "
                    "value over doing nothing."
                ),
                "",
            ]
        view = compare_reports(
            report, benchmark_report, report.benchmark.benchmark_name
        )
        lines = [
            self.tr("== Benchmark comparison (vs {name}) ==").format(
                name=view.benchmark_name
            ),
            self.tr("  Excess return (net of costs): {x}").format(
                x=view.excess_return
            ),
            self.tr("  Excess return (before costs): {x}").format(
                x=view.gross_excess_return
            ),
            self.tr("  Cost drag on the comparison: {x}").format(
                x=view.cost_drag
            ),
            self.tr("  Volatility difference: {x}").format(
                x=self._fmt(view.volatility_difference)
            ),
            self.tr("  Max drawdown difference: {x}").format(
                x=self._fmt(view.max_drawdown_difference)
            ),
            self.tr("  Sharpe difference: {x}").format(
                x=self._fmt(view.sharpe_difference)
            ),
        ]
        # Plain-language verdict (chapter 42.2, 40.8).
        if view.beats_benchmark:
            lines.append(
                self.tr(
                    "  The strategy beat the passive alternative by "
                    "{x} after costs — described, not proven."
                ).format(x=view.excess_return)
            )
        else:
            lines.append(
                self.tr(
                    "  The strategy did NOT beat the passive "
                    "alternative after costs ({x}). The honest "
                    "conclusion: this configuration added nothing over "
                    "doing the simple thing."
                ).format(x=view.excess_return)
            )
        lines.append("")
        return lines

    def _fmt(self, value, valid: bool = True) -> str:
        if value is None:
            return self.tr("n/a (insufficient data)")
        if isinstance(value, Decimal):
            text = f"{value:.6f}"
        else:
            text = str(value)
        if not valid:
            text += self.tr("  (descriptive only, not statistically "
                            "supported)")
        return text
