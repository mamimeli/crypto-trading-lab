"""Command-line interface (ROADMAP.md chapter 22).

Every subcommand calls the shared use cases in
:mod:`crypto_trading_lab.application`, the same functions the GUI
uses, so the CLI cannot drift from the desktop application. The CLI
prints what it actually did and returns a non-zero status when it
could not do it -- a silent success is worse than an honest failure.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from typing import Any, Sequence

from crypto_trading_lab import __version__
from crypto_trading_lab import application

#: How each doctor status is shown.
_STATUS_LABEL = {
    "pass": "PASS",
    "warn": "WARN",
    "skip": "SKIP",
    "fail": "FAIL",
}


def _percent(value: Decimal | None) -> str:
    if value is None:
        return "not meaningful"
    return f"{value * Decimal(100):.2f}%"


def _money(value: Decimal) -> str:
    return f"{value:.2f}"


def _ratio(value: Decimal | None) -> str:
    if value is None:
        return "not meaningful"
    return f"{value:.3f}"


def _flagged(value: Decimal | None, valid: bool) -> str:
    """A ratio, marked when the report calls it descriptive only.

    The GUI already annotates these; printing the bare number here would
    let a 30-candle run look like a conclusion.
    """
    text = _ratio(value)
    if value is not None and not valid:
        text += " (descriptive only, not statistically supported)"
    return text


def doctor(args: Any) -> int:
    """Run the chapter 22 diagnostics (never prints a secret)."""
    print("Checking system configuration...")
    results = application.run_doctor(
        paths=getattr(args, "paths", None),
        network=getattr(args, "network", False),
    )
    for result in results:
        label = _STATUS_LABEL.get(result.status, result.status.upper())
        print(f"[{label}] {result.name}: {result.detail}")

    counts = {
        status: sum(1 for item in results if item.status == status)
        for status in ("pass", "warn", "skip", "fail")
    }
    print(
        "Doctor finished: "
        f"{counts['pass']} passed, {counts['warn']} warning(s), "
        f"{counts['skip']} skipped, {counts['fail']} failed."
    )
    return 1 if counts["fail"] else 0


def database_check(args: Any) -> int:
    """Open the SQLite file and run its own integrity check."""
    report = application.check_database(paths=getattr(args, "paths", None))
    if not report.exists:
        print(
            f"Database not found at {report.path}. Nothing was checked. "
            "Import a CSV or open the application to create it.",
            file=sys.stderr,
        )
        return 1
    if report.error is not None:
        print(f"Database check FAILED: {report.error}", file=sys.stderr)
        return 1
    print(f"Database: {report.path}")
    print(f"Schema version: {report.schema_version}")
    print(f"Integrity: {report.integrity}")
    print("Tables:")
    for name in sorted(report.tables):
        print(f"  {name}: {report.tables[name]} row(s)")
    if not report.ok:
        print(
            f"Database check FAILED: integrity is {report.integrity!r}.",
            file=sys.stderr,
        )
        return 1
    print("Database check passed.")
    return 0


def list_strategies(args: Any) -> int:
    """List every registered strategy (chapter 36)."""
    strategies = application.list_strategies(paths=getattr(args, "paths", None))
    if not strategies:
        print("No strategies are registered.", file=sys.stderr)
        return 1
    print("Available Strategies:")
    for strategy in strategies:
        print(
            f"- {strategy.name} (ID: {strategy.strategy_id}, "
            f"Ver: {strategy.version})"
        )
    return 0


def list_lessons(args: Any) -> int:
    """List the curriculum (chapter 23)."""
    level = getattr(args, "level", None)
    lessons = application.list_lessons(level=level)
    if not lessons:
        print("No lessons found.", file=sys.stderr)
        return 1
    print("Lessons:")
    for lesson in lessons:
        print(f"  {lesson.number:>2}. [Level {lesson.level}] {lesson.title}")
    print(f"Total: {len(lessons)} lesson(s).")
    return 0


def glossary_search(args: Any) -> int:
    """Search the beginner glossary (chapter 24)."""
    matches = application.search_glossary(args.term)
    if not matches:
        print(
            f"No glossary entry matched {args.term!r}. "
            "Try a shorter word, for example 'slip' or 'spread'.",
            file=sys.stderr,
        )
        return 1
    for index, entry in enumerate(matches):
        if index:
            print()
        print(f"### {entry.term}")
        print(entry.body)
    print()
    plural = "entry" if len(matches) == 1 else "entries"
    print(f"{len(matches)} {plural} matched {args.term!r}.")
    return 0


def import_csv_cmd(args: Any) -> int:
    """Validate a CSV and store its candles (chapter 28)."""
    print(f"Reading {args.file} ...")
    outcome = application.import_csv_file(
        args.file,
        symbol=args.symbol,
        interval=args.interval,
        paths=getattr(args, "paths", None),
    )
    if not outcome.ok:
        print(outcome.message, file=sys.stderr)
        return 1
    print(outcome.message)
    return 0


def _print_backtest(run: application.BacktestRun) -> None:
    result = run.result
    report = run.report
    print(f"Strategy: {run.strategy_name}")
    if run.dataset is not None:
        print(
            f"Dataset: {run.dataset.dataset_id} "
            f"({run.dataset.symbol} {run.dataset.interval})"
        )
    print(f"Candles: {run.candle_count}")
    # Chapter 33.7: what validation saw before the run. Errors never get this
    # far; warnings are shown with the result they apply to.
    if run.validation is not None:
        for warning in run.validation.warnings:
            print(f"Warning: {warning.message}")
    parameters = run.result.config_metadata.get("strategy_parameters")
    if parameters:
        print(f"Parameters: {parameters}")
    print(f"Execution model: {run.config.execution_realism_name()}")
    if run.config.execution_config is not None:
        print(f"Execution seed: {run.config.execution_seed}")
        print(
            f"Orders rejected: {result.rejected_orders}, "
            f"partially filled: {result.partial_fills}"
        )
    print(f"Initial capital: {_money(result.initial_capital)}")
    print(f"Final equity: {_money(result.final_equity)}")
    print(
        f"Net profit: {_money(report.returns.net_profit)} "
        f"({_percent(report.returns.total_return)})"
    )
    print(f"Max drawdown: {_percent(report.risk.max_drawdown)}")
    trades = report.trades
    print(
        f"Trades: {trades.number_of_trades} "
        f"({trades.winning_trades} winning / "
        f"{trades.losing_trades} losing)"
    )
    print(f"Win rate: {_percent(trades.win_rate)}")
    print(f"Profit factor: {_ratio(trades.profit_factor)}")
    print(
        f"Sharpe ratio: "
        f"{_flagged(report.risk.sharpe_ratio, report.risk.sharpe_is_valid)}"
    )
    print(f"Total fees: {_money(report.activity.trading_fees)}")
    print(f"Slippage cost: {_money(report.activity.slippage_cost)}")
    print(f"Spread cost: {_money(report.activity.spread_cost)}")
    if report.benchmark is not None:
        print(
            f"Benchmark ({report.benchmark.benchmark_name}): "
            f"{_percent(report.benchmark.benchmark_return)}, "
            f"excess {_percent(report.benchmark.excess_return)}"
        )
    for warning in report.warnings:
        print(f"Warning: {warning}")
    print()
    print(report.disclaimer)


def backtest_cmd(args: Any) -> int:
    """Run the chapter 37 engine from a JSON/YAML configuration."""
    try:
        run = application.run_backtest_file(
            args.strategy, paths=getattr(args, "paths", None)
        )
    except application.ApplicationError as error:
        print(f"Backtest not run: {error}", file=sys.stderr)
        return 1
    _print_backtest(run)
    return 0


def _parse_parameters(items: list[str]) -> dict[str, int]:
    """Turn repeated ``--set key=value`` flags into strategy parameters."""
    parameters: dict[str, int] = {}
    for item in items:
        key, separator, raw = item.partition("=")
        if not separator or not key:
            raise application.ApplicationError(
                f"--set expects key=value, got {item!r}"
            )
        try:
            parameters[key] = int(raw)
        except ValueError as exc:
            raise application.ApplicationError(
                f"--set {key} must be an integer, got {raw!r}"
            ) from exc
    return parameters


def paper_live_cmd(args: Any) -> int:
    """Run paper trading against the live Binance WebSocket feed (26.2)."""
    try:
        parameters = _parse_parameters(getattr(args, "set", []) or [])
        result = application.run_live_paper_session(
            strategy_id=args.strategy,
            parameters=parameters,
            symbol=args.symbol,
            interval=args.interval,
            minutes=args.minutes,
            initial_capital=Decimal(str(args.capital)),
            taker_fee=Decimal(str(args.fee)),
            environment=args.environment,
            paths=getattr(args, "paths", None),
        )
    except application.ApplicationError as error:
        print(f"Live session not run: {error}", file=sys.stderr)
        return 1

    print("== Live paper trading (chapter 26.2) ==")
    print(f"Strategy: {result.strategy_name}")
    print(f"Dataset: {result.dataset_id}")
    received = len(result.equity_curve)
    print(f"Candles received: {received}")
    if result.warmup_candles:
        line = (
            f"Warm-up: the strategy needs {result.warmup_candles} "
            "candles before its first signal"
        )
        if received < result.warmup_candles:
            line += f", and only {received} arrived"
        print(line)
    print()
    print(result.summary())
    return 0


def _add_paths_option(parser: argparse.ArgumentParser) -> None:
    """Let tests and scripts point the CLI at an isolated data directory."""
    parser.add_argument(
        "--data-dir",
        default=None,
        help=(
            "use this directory instead of the XDG data directory "
            "(scripts and tests)"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crypto-trading-lab",
        description="CLI for Crypto Trading Lab",
    )
    parser.add_argument(
        "--version", action="version", version=f"Crypto Trading Lab {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    doctor_parser = subparsers.add_parser(
        "doctor", help="Run system diagnostics"
    )
    doctor_parser.add_argument(
        "--network",
        action="store_true",
        help="also test public connectivity and measure clock drift",
    )
    _add_paths_option(doctor_parser)

    database = subparsers.add_parser("database", help="Database operations")
    database_sub = database.add_subparsers(dest="subcommand", required=True)
    database_check_parser = database_sub.add_parser(
        "check", help="Check database integrity"
    )
    _add_paths_option(database_check_parser)

    import_csv = subparsers.add_parser(
        "import-csv", help="Import CSV market data"
    )
    import_csv.add_argument("file", help="CSV file path")
    import_csv.add_argument(
        "--symbol",
        default="BTC/USDT",
        help="trading pair for the file (default: BTC/USDT)",
    )
    import_csv.add_argument(
        "--interval",
        default="1m",
        help="candle interval for the file (default: 1m)",
    )
    _add_paths_option(import_csv)

    paper_live = subparsers.add_parser(
        "paper-live",
        help="Paper-trade the live Binance WebSocket feed (chapters 26.2/57)",
    )
    paper_live.add_argument(
        "--strategy",
        default="ma_crossover",
        help="strategy id from list-strategies (default: ma_crossover)",
    )
    paper_live.add_argument(
        "--set",
        action="append",
        metavar="KEY=VALUE",
        default=[],
        help="strategy parameter, repeatable (e.g. --set fast=5)",
    )
    paper_live.add_argument("--symbol", default="BTC/USDT")
    paper_live.add_argument(
        "--interval",
        default="1m",
        help=(
            "any Binance kline interval: 1s, 1m, 3m, 5m, 15m, 30m, 1h, "
            "2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M (default: 1m)"
        ),
    )
    paper_live.add_argument(
        "--minutes",
        type=float,
        default=5.0,
        help="how long to listen before returning (default: 5)",
    )
    paper_live.add_argument("--capital", default="10000")
    paper_live.add_argument("--fee", default="0.001")
    paper_live.add_argument(
        "--environment",
        default="spot-testnet",
        help="spot-testnet (default) or production",
    )
    _add_paths_option(paper_live)

    backtest = subparsers.add_parser("backtest", help="Run a backtest")
    backtest.add_argument(
        "strategy", help="strategy configuration file (.json, .yaml, .yml)"
    )
    _add_paths_option(backtest)

    list_strategies_parser = subparsers.add_parser(
        "list-strategies", help="List available strategies"
    )
    _add_paths_option(list_strategies_parser)

    list_lessons_parser = subparsers.add_parser(
        "list-lessons", help="List the lessons in the curriculum"
    )
    list_lessons_parser.add_argument(
        "--level", type=int, choices=(1, 2, 3), default=None,
        help="only lessons from this level",
    )
    _add_paths_option(list_lessons_parser)

    # Chapter 22 spells the commands with hyphens; the older grouped
    # form stays as an alias so existing notes keep working.
    list_cmd = subparsers.add_parser("list", help="List resources")
    list_sub = list_cmd.add_subparsers(dest="subcommand", required=True)
    list_strategies_alias = list_sub.add_parser(
        "strategies", help="List strategies"
    )
    _add_paths_option(list_strategies_alias)
    list_lessons_alias = list_sub.add_parser("lessons", help="List lessons")
    list_lessons_alias.add_argument(
        "--level", type=int, choices=(1, 2, 3), default=None
    )
    _add_paths_option(list_lessons_alias)

    glossary = subparsers.add_parser("glossary", help="Glossary operations")
    glossary_sub = glossary.add_subparsers(dest="subcommand", required=True)
    glossary_search_parser = glossary_sub.add_parser(
        "search", help="Search glossary"
    )
    glossary_search_parser.add_argument("term", help="Term to search for")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "data_dir", None):
        from crypto_trading_lab.configuration.xdg import AppPaths

        args.paths = AppPaths(data_dir=args.data_dir)
    else:
        args.paths = None

    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "doctor":
        return doctor(args)
    if args.command == "database":
        return database_check(args)
    if args.command == "list-strategies":
        return list_strategies(args)
    if args.command == "list-lessons":
        return list_lessons(args)
    if args.command == "list":
        if args.subcommand == "strategies":
            return list_strategies(args)
        return list_lessons(args)
    if args.command == "glossary":
        return glossary_search(args)
    if args.command == "import-csv":
        return import_csv_cmd(args)
    if args.command == "backtest":
        return backtest_cmd(args)
    if args.command == "paper-live":
        return paper_live_cmd(args)

    print(f"Command not implemented: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
