"""Shared application use cases (ROADMAP.md chapter 22).

The CLI and the GUI both call the functions in this module, so neither
re-implements a business rule. Chapter 22 is explicit about it: "The CLI
must reuse the same use cases as the GUI." Everything here is a thin
orchestration layer over the modules that already own the logic:
crypto_trading_lab.market_data.importer for CSV validation,
crypto_trading_lab.persistence for storage and
crypto_trading_lab.backtesting for the engine and metrics.

Nothing in this module opens a GUI, touches the network by default, or
prints anything: callers decide how to present the result.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from crypto_trading_lab.backtesting.engine import (
    BacktestConfig,
    BacktestResult,
    BuyAndHoldStrategy,
    CostModel,
    NullStrategy,
    run_backtest,
)
from crypto_trading_lab.backtesting.metrics import (
    PerformanceReport,
    compute_performance,
)
from crypto_trading_lab.configuration.xdg import AppPaths
from crypto_trading_lab.domain.models import Symbol
from crypto_trading_lab.execution_realism import ExecutionConfig
from crypto_trading_lab.education.curriculum import (
    CURRICULUM,
    LessonContent,
    lessons_for_level,
)
from crypto_trading_lab.market_data.historical import DatasetVersion
from crypto_trading_lab.market_data.importer import parse_csv

__all__ = [
    "REQUIRED_MODULES",
    "SUPPORTED_PYTHON",
    "ApplicationError",
    "BacktestRun",
    "CheckResult",
    "DatabaseReport",
    "GlossaryEntry",
    "ImportOutcome",
    "check_database",
    "docs_root",
    "glossary_entries",
    "import_csv_file",
    "list_lessons",
    "list_strategies",
    "load_config_file",
    "run_backtest_file",
    "run_live_paper_session",
    "run_doctor",
    "search_glossary",
]

#: Chapter 3/4: the supported Python floor.
SUPPORTED_PYTHON = (3, 11)

#: Chapter 22 "required modules" -- the four Debian runtime packages.
REQUIRED_MODULES = ("PyQt6", "pyqtgraph", "sqlalchemy", "platformdirs")


class ApplicationError(ValueError):
    """A problem the caller must show to the user, with a readable reason."""


# ---------------------------------------------------------------------------
# CSV import (chapters 22 and 28)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImportOutcome:
    """Result of importing one CSV file into the candle store."""

    ok: bool
    saved: int
    symbol: str
    interval: str
    message: str


def import_csv_file(
    path: str | Path,
    *,
    symbol: str = "BTC/USDT",
    interval: str = "1m",
    paths: AppPaths | None = None,
) -> ImportOutcome:
    """Validate a CSV and persist its candles (chapter 28).

    Validation runs before any database file is created, so a rejected
    file leaves the data directory untouched. The returned message is
    the same text the GUI shows.
    """
    from crypto_trading_lab.persistence.candles import CandleRepository
    from crypto_trading_lab.persistence.database import (
        create_database,
        database_engine,
        make_session_factory,
    )

    csv_path = Path(path)
    if not csv_path.exists():
        return ImportOutcome(
            ok=False,
            saved=0,
            symbol=symbol,
            interval=interval,
            message=f"The file {csv_path} does not exist.",
        )
    if not csv_path.is_file():
        return ImportOutcome(
            ok=False,
            saved=0,
            symbol=symbol,
            interval=interval,
            message=f"{csv_path} is not a regular file.",
        )

    summary = parse_csv(
        csv_path, symbol_default=symbol, interval_default=interval
    )
    if not summary.ok:
        return ImportOutcome(
            ok=False,
            saved=0,
            symbol=summary.symbol or symbol,
            interval=summary.interval or interval,
            message=summary.beginner_explanation(),
        )

    paths = paths or AppPaths()
    engine = database_engine(paths.database_file)
    create_database(engine)
    session = make_session_factory(engine)()
    try:
        saved = CandleRepository(session).save_candles(summary.candles)
    finally:
        session.close()
        engine.dispose()
    return ImportOutcome(
        ok=True,
        saved=saved,
        symbol=summary.symbol,
        interval=summary.interval,
        message=(
            f"Imported {saved} candles of {summary.symbol} "
            f"({summary.interval})."
        ),
    )


# ---------------------------------------------------------------------------
# Database inspection (chapters 8 and 22)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DatabaseReport:
    """What 'database check' found (chapter 22)."""

    path: Path
    exists: bool
    schema_version: int | None
    integrity: str
    tables: dict[str, int] = field(default_factory=dict)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.exists and self.error is None and self.integrity == "ok"


def check_database(*, paths: AppPaths | None = None) -> DatabaseReport:
    """Run SQLite's own integrity check without mutating the database.

    The file is never created here: a missing database is reported as
    such instead of being silently initialised (the old CLI printed
    "Database check passed." without opening anything).
    """
    from sqlalchemy import inspect, text

    from crypto_trading_lab.persistence.database import database_engine

    paths = paths or AppPaths()
    database_file = paths.database_file
    if not database_file.exists():
        return DatabaseReport(
            path=database_file,
            exists=False,
            schema_version=None,
            integrity="missing",
        )
    try:
        engine = database_engine(database_file)
    except Exception as exc:  # pragma: no cover - defensive
        return DatabaseReport(
            path=database_file,
            exists=True,
            schema_version=None,
            integrity="unreadable",
            error=f"could not open the database: {exc}",
        )
    try:
        with engine.connect() as connection:
            integrity = str(
                connection.execute(text("PRAGMA integrity_check")).scalar()
            )
            tables = {
                name: int(
                    connection.execute(
                        text(f'SELECT COUNT(*) FROM "{name}"')
                    ).scalar()
                )
                for name in inspect(engine).get_table_names()
            }
            version: int | None = None
            if "schema_migrations" in tables:
                version = connection.execute(
                    text("SELECT MAX(version) FROM schema_migrations")
                ).scalar()
                version = int(version) if version is not None else None
        return DatabaseReport(
            path=database_file,
            exists=True,
            schema_version=version,
            integrity=integrity,
            tables=tables,
        )
    except Exception as exc:
        return DatabaseReport(
            path=database_file,
            exists=True,
            schema_version=None,
            integrity="unreadable",
            error=str(exc),
        )
    finally:
        engine.dispose()


# ---------------------------------------------------------------------------
# Backtest from a configuration file (chapters 22, 37 and 40)
# ---------------------------------------------------------------------------

#: Keys that configure the run itself rather than the strategy.
_COMMON_KEYS = frozenset(
    {
        "strategy",
        "initial_capital",
        "position_fraction",
        "maker_fee",
        "taker_fee",
        "slippage",
        "spread",
        "symbol",
        "interval",
        "benchmark",
        "execution_model",
        "execution_seed",
    }
    )


@dataclass(frozen=True)
class BacktestRun:
    """One CLI backtest with the metrics that belong to it."""

    strategy_name: str
    config: BacktestConfig
    result: BacktestResult
    report: PerformanceReport
    dataset: DatasetVersion | None
    candle_count: int


def load_config_file(path: str | Path) -> dict[str, Any]:
    """Read a JSON or YAML strategy configuration.

    YAML needs the optional python3-yaml Debian package (PyPI:
    PyYAML); JSON works with the standard library alone. A missing YAML
    reader is reported with the exact command to run instead of a
    traceback.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ApplicationError(f"configuration file not found: {config_path}")
    if not config_path.is_file():
        raise ApplicationError(f"{config_path} is not a regular file")

    suffix = config_path.suffix.lower()
    if suffix == ".json":
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ApplicationError(
                f"could not read {config_path}: {exc}"
            ) from exc
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ApplicationError(
                "reading YAML needs the optional PyYAML package. On "
                "Debian: sudo apt install python3-yaml. Alternatively "
                "save the same configuration as JSON."
            ) from exc
        try:
            payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise ApplicationError(
                f"could not read {config_path}: {exc}"
            ) from exc
    else:
        raise ApplicationError(
            f"unsupported configuration format {suffix or '(none)'}; "
            "use .json, .yaml or .yml"
        )

    if payload is None:
        raise ApplicationError(f"{config_path} is empty")
    if not isinstance(payload, dict):
        raise ApplicationError(
            f"{config_path} must contain key/value pairs at the top level"
        )
    return {str(key): value for key, value in payload.items()}


def _decimal(
    payload: dict[str, Any], key: str, default: str, *, minimum: Decimal
) -> Decimal:
    raw = payload.get(key, default)
    try:
        value = Decimal(str(raw))
    except (InvalidOperation, ValueError) as exc:
        raise ApplicationError(
            f"{key} must be a number, got {raw!r}"
        ) from exc
    if value < minimum:
        raise ApplicationError(f"{key} must be at least {minimum}, got {value}")
    return value


def _most_populated_market(
    session, *, symbol: str | None, interval: str | None
) -> tuple[str, str] | None:
    """The stored market/interval with the most candles (chapter 22).

    Used only when the configuration does not name a market and no
    dataset identity was recorded: a backtest then runs over what the
    user actually imported instead of failing on an empty guess.
    """
    from sqlalchemy import func, select

    from crypto_trading_lab.persistence.database import (
        CandleRecord,
        MarketRecord,
    )

    statement = (
        select(
            MarketRecord.symbol,
            CandleRecord.interval,
            func.count(CandleRecord.id).label("candles"),
        )
        .join(MarketRecord, CandleRecord.market_id == MarketRecord.id)
        .group_by(MarketRecord.symbol, CandleRecord.interval)
        .order_by(func.count(CandleRecord.id).desc())
        .limit(1)
    )
    if symbol is not None:
        statement = statement.where(MarketRecord.symbol == symbol)
    if interval is not None:
        statement = statement.where(CandleRecord.interval == interval)
    row = session.execute(statement).first()
    if row is None:
        return None
    return str(row[0]), str(row[1])


def _load_candles(
    session, *, symbol: str | None, interval: str | None
) -> tuple[DatasetVersion | None, list]:
    """Most recent matching dataset and its candles."""
    from crypto_trading_lab.persistence.candles import CandleRepository
    from crypto_trading_lab.persistence.datasets import DatasetRepository

    dataset = DatasetRepository(session).latest(
        symbol=symbol, interval=interval
    )
    if dataset is not None:
        candles = CandleRepository(session).load_candles(
            Symbol(dataset.symbol),
            dataset.interval,
            exchange_name=dataset.exchange,
        )
        return dataset, candles

    # No dataset identity recorded (a plain CSV import): fall back to
    # the requested market, or to the most populated stored one.
    chosen = (
        (symbol, interval)
        if symbol is not None and interval is not None
        else _most_populated_market(
            session, symbol=symbol, interval=interval
        )
    )
    if chosen is None:
        return None, []
    chosen_symbol, chosen_interval = chosen
    candles = CandleRepository(session).load_candles(
        Symbol(chosen_symbol), chosen_interval, exchange_name="mock"
    )
    return None, candles


def run_backtest_file(
    config_path: str | Path, *, paths: AppPaths | None = None
) -> BacktestRun:
    """Run the chapter 37 engine over stored candles.

    The configuration names a registered strategy and its parameters;
    the candles come from the most recent matching dataset. Errors are
    raised as ApplicationError with a message a beginner can act on.
    """
    from crypto_trading_lab.persistence.database import (
        create_database,
        database_engine,
        make_session_factory,
    )
    from crypto_trading_lab.strategy_registry import StrategyRegistry
    from crypto_trading_lab.market_data.quality import DatasetProvenance

    payload = load_config_file(config_path)
    strategy_id = payload.get("strategy")
    if not isinstance(strategy_id, str) or not strategy_id:
        raise ApplicationError(
            "the configuration must name a strategy, for example "
            "'strategy: ma_crossover'"
        )

    paths = paths or AppPaths()
    registry = StrategyRegistry(
        storage_path=paths.data_dir / "strategy_registry"
    )
    registration = registry.get(strategy_id)
    if registration is None or registration.factory is None:
        known = ", ".join(
            meta.strategy_id for meta in registry.list_strategies()
        )
        raise ApplicationError(
            f"unknown strategy {strategy_id!r}; available: {known}"
        )

    schema = registration.metadata.parameters_schema
    allowed = _COMMON_KEYS | set(schema)
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ApplicationError(
            f"unknown configuration key(s): {', '.join(unknown)}. "
            f"Allowed keys for {strategy_id}: "
            f"{', '.join(sorted(allowed))}"
        )

    # Chapter 33.4: the registry owns the parameter contract — types, bounds
    # and cross-parameter rules — so this layer must not re-implement them.
    params = {key: payload[key] for key in schema if key in payload}

    try:
        strategy = registry.create_instance(strategy_id, **params)
        parameters = registry.parameter_set(strategy_id, **params)
    except (TypeError, ValueError) as exc:
        raise ApplicationError(
            f"could not create strategy {strategy_id!r}: {exc}"
        ) from exc
    if strategy is None or parameters is None:
        raise ApplicationError(
            f"strategy {strategy_id!r} has no factory and cannot run"
        )

    initial_capital = _decimal(
        payload, "initial_capital", "10000", minimum=Decimal("0.01")
    )
    position_fraction = _decimal(
        payload, "position_fraction", "1", minimum=Decimal("0")
    )
    if position_fraction > 1:
        raise ApplicationError("position_fraction must be at most 1")
    costs = CostModel(
        maker_fee=_decimal(
            payload, "maker_fee", "0.001", minimum=Decimal("0")
        ),
        taker_fee=_decimal(
            payload, "taker_fee", "0.001", minimum=Decimal("0")
        ),
        slippage_fraction=_decimal(
            payload, "slippage", "0.0005", minimum=Decimal("0")
        ),
        spread_fraction=_decimal(
            payload, "spread", "0.0002", minimum=Decimal("0")
        ),
    )
    execution_model = str(
        payload.get("execution_model", "cost_model")
    ).strip().lower()
    if execution_model in ("cost_model", "cost-model", "simple"):
        execution_config = None
    elif execution_model in (
        "chapter_56",
        "chapter-56",
        "execution_realism",
        "realistic",
    ):
        execution_config = ExecutionConfig()
    else:
        raise ApplicationError(
            f"unknown execution_model {execution_model!r}; use "
            "'cost_model' or 'chapter_56'"
        )
    seed_raw = payload.get("execution_seed", 42)
    try:
        execution_seed = int(seed_raw)
    except (TypeError, ValueError) as exc:
        raise ApplicationError(
            f"execution_seed must be an integer, got {seed_raw!r}"
        ) from exc

    config = BacktestConfig(
        initial_capital=initial_capital,
        position_fraction=position_fraction,
        costs=costs,
        execution_config=execution_config,
        execution_seed=execution_seed,
        strategy_parameters=parameters.signature(),
    )

    symbol = payload.get("symbol")
    interval = payload.get("interval")
    symbol = str(symbol) if symbol is not None else None
    interval = str(interval) if interval is not None else None

    if not paths.database_file.exists():
        raise ApplicationError(
            "no database yet: import a CSV with "
            "'crypto-trading-lab import-csv file.csv' first"
        )
    engine = database_engine(paths.database_file)
    create_database(engine)
    session = make_session_factory(engine)()
    try:
        dataset, candles = _load_candles(
            session, symbol=symbol, interval=interval
        )
    finally:
        session.close()
        engine.dispose()

    if len(candles) < 2:
        where = f" for {symbol} {interval}" if symbol or interval else ""
        raise ApplicationError(
            f"not enough stored candles{where} (found {len(candles)}). "
            "Import a CSV first, or widen the symbol/interval filters."
        )

    result = run_backtest(candles, strategy, config, dataset=(DatasetProvenance.from_dataset_version(dataset) if dataset is not None else None))

    benchmark_name = str(payload.get("benchmark", "buy_and_hold")).lower()
    benchmark_result: BacktestResult | None
    if benchmark_name in ("none", "null", "off"):
        benchmark_result = None
    elif benchmark_name in ("buy_and_hold", "buy-and-hold", "hold"):
        benchmark_result = run_backtest(candles, BuyAndHoldStrategy(), config, dataset=(DatasetProvenance.from_dataset_version(dataset) if dataset is not None else None))
    elif benchmark_name in ("null_strategy", "null-strategy"):
        benchmark_result = run_backtest(candles, NullStrategy(), config, dataset=(DatasetProvenance.from_dataset_version(dataset) if dataset is not None else None))
    else:
        raise ApplicationError(
            f"unknown benchmark {benchmark_name!r}; use buy_and_hold, "
            "null_strategy or none"
        )

    report = compute_performance(result, benchmark=benchmark_result)
    return BacktestRun(
        strategy_name=strategy.name,
        config=config,
        result=result,
        report=report,
        dataset=dataset,
        candle_count=len(candles),
    )


# ---------------------------------------------------------------------------
# Live paper trading over the WebSocket feed (chapters 22, 26.2 and 57)
# ---------------------------------------------------------------------------


def run_live_paper_session(
    *,
    strategy_id: str = "ma_crossover",
    parameters: dict[str, Any] | None = None,
    symbol: str = "BTC/USDT",
    interval: str = "1m",
    minutes: float = 5.0,
    initial_capital: Decimal = Decimal("10000"),
    taker_fee: Decimal = Decimal("0.001"),
    environment: str = "spot-testnet",
    paths: AppPaths | None = None,
    websocket_factory: Any = None,
):
    """Run one paper session against the live Binance WebSocket feed.

    This is the use case behind the ``paper-live`` subcommand. It resolves
    the strategy from the registry, builds a chapter 26.2 configuration for
    the requested environment and runs the session for at most ``minutes``.
    Real money is never involved: the feed is public market data and the
    account is simulated.

    ``websocket_factory`` exists so tests can drive a scripted feed; the
    CLI never passes it.
    """
    from crypto_trading_lab.exchanges.binance.config import (
        BINANCE_INTERVALS,
        endpoints_for,
    )
    from crypto_trading_lab.paper_session import (
        LivePaperConfig,
        run_paper_session_live,
    )
    from crypto_trading_lab.strategy_registry import StrategyRegistry

    if minutes <= 0:
        raise ApplicationError("minutes must be positive")
    if interval not in BINANCE_INTERVALS:
        known_intervals = ", ".join(BINANCE_INTERVALS)
        raise ApplicationError(
            f"unsupported interval {interval!r}; use one of {known_intervals}"
        )
    try:
        Symbol(symbol)
    except (TypeError, ValueError) as exc:
        raise ApplicationError(f"invalid symbol {symbol!r}: {exc}") from exc
    try:
        endpoints = endpoints_for(environment)
    except ValueError as exc:
        raise ApplicationError(str(exc)) from exc

    paths = paths or AppPaths()
    registry = StrategyRegistry(
        storage_path=paths.data_dir / "strategy_registry"
    )
    registration = registry.get(strategy_id)
    if registration is None or registration.factory is None:
        known = ", ".join(
            meta.strategy_id for meta in registry.list_strategies()
        )
        raise ApplicationError(
            f"unknown strategy {strategy_id!r}; available: {known}"
        )
    try:
        strategy = registry.create_instance(strategy_id, **(parameters or {}))
    except (TypeError, ValueError) as exc:
        raise ApplicationError(
            f"could not create strategy {strategy_id!r}: {exc}"
        ) from exc
    if strategy is None:
        raise ApplicationError(
            f"strategy {strategy_id!r} has no factory and cannot run"
        )

    config = LivePaperConfig(
        endpoints=endpoints,
        symbol=symbol,
        interval=interval,
        max_runtime_seconds=max(1, int(minutes * 60)),
        initial_capital=initial_capital,
        taker_fee=taker_fee,
    )
    try:
        return asyncio.run(
            run_paper_session_live(
                strategy, config, websocket_factory=websocket_factory
            )
        )
    except RuntimeError as exc:
        # Raised when the optional websockets package is missing.
        raise ApplicationError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Read-only catalogue access (chapters 22, 23 and 24)
# ---------------------------------------------------------------------------


def list_strategies(*, paths: AppPaths | None = None):
    """Every registered strategy, built-in and imported (chapter 36)."""
    from crypto_trading_lab.strategy_registry import StrategyRegistry

    paths = paths or AppPaths()
    registry = StrategyRegistry(
        storage_path=paths.data_dir / "strategy_registry"
    )
    return registry.list_strategies()


def list_lessons(*, level: int | None = None) -> tuple[LessonContent, ...]:
    """The curriculum, optionally filtered to one level (chapter 23)."""
    if level is None:
        return CURRICULUM
    return lessons_for_level(level)


# ---------------------------------------------------------------------------
# Glossary (chapter 24)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GlossaryEntry:
    """One '### term' section of the beginner glossary."""

    term: str
    body: str


def docs_root() -> Path | None:
    """Locate the documentation tree, from the source tree or an install."""
    candidates = [
        Path(__file__).resolve().parents[2] / "docs",  # repo checkout
        Path(__file__).resolve().parent / "docs",      # packaged copy
        Path.cwd() / "docs",
    ]
    for candidate in candidates:
        if (candidate / "en" / "beginners").is_dir():
            return candidate
    return None


def glossary_entries(root: Path | None = None) -> tuple[GlossaryEntry, ...]:
    """Parse docs/en/beginners/glossary.md into entries.

    Duplicate headings exist in the file (the same term explained twice
    from different angles); the first definition wins so a search
    prints one result per term.
    """
    root = root or docs_root()
    if root is None:
        return ()
    path = Path(root) / "en" / "beginners" / "glossary.md"
    if not path.exists():
        return ()

    entries: list[GlossaryEntry] = []
    seen: set[str] = set()
    term: str | None = None
    body: list[str] = []

    def flush() -> None:
        if term is None:
            return
        key = term.casefold()
        if key in seen:
            return
        seen.add(key)
        entries.append(
            GlossaryEntry(term=term, body="\n".join(body).strip())
        )

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            flush()
            term = line[4:].strip()
            body = []
        elif term is not None:
            body.append(line)
    flush()
    return tuple(entries)


def search_glossary(
    term: str, *, root: Path | None = None
) -> tuple[GlossaryEntry, ...]:
    """Case-insensitive search over term names and definitions."""
    needle = term.strip().casefold()
    if not needle:
        return ()
    matches = [
        entry
        for entry in glossary_entries(root)
        if needle in entry.term.casefold() or needle in entry.body.casefold()
    ]
    # Entries whose *name* matches come first; body matches (a term that
    # merely appears inside another definition) follow alphabetically.
    matches.sort(key=lambda entry: (needle not in entry.term.casefold(), entry.term))
    return tuple(matches)


# ---------------------------------------------------------------------------
# doctor (chapter 22)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CheckResult:
    """One doctor line: a name, a status and a readable detail."""

    name: str
    status: str  # "pass" | "warn" | "skip" | "fail"
    detail: str


def _nearest_writable(directory: Path) -> tuple[bool, str]:
    """Whether the nearest existing ancestor accepts new files."""
    current = directory
    while not current.exists() and current != current.parent:
        current = current.parent
    if not current.exists():
        return False, f"{directory} has no existing ancestor"
    if not os.access(current, os.W_OK):
        return False, f"{current} is not writable"
    return True, f"{current} is writable"


def _check_python() -> CheckResult:
    version = sys.version_info
    text = f"{version.major}.{version.minor}.{version.micro}"
    required = ".".join(str(part) for part in SUPPORTED_PYTHON)
    if (version.major, version.minor) >= SUPPORTED_PYTHON:
        return CheckResult(
            "python_version", "pass", f"{text} (needs >= {required})"
        )
    return CheckResult(
        "python_version", "fail", f"{text} is older than {required}"
    )


def _check_modules() -> CheckResult:
    import importlib

    missing: list[str] = []
    for name in REQUIRED_MODULES:
        try:
            importlib.import_module(name)
        except Exception:  # noqa: BLE001 - any import failure is a failure
            missing.append(name)
    if missing:
        return CheckResult(
            "required_modules",
            "fail",
            "missing: "
            + ", ".join(missing)
            + " (Debian: sudo apt install python3-pyqt6 python3-pyqtgraph "
            "python3-sqlalchemy python3-platformdirs)",
        )
    return CheckResult(
        "required_modules", "pass", ", ".join(REQUIRED_MODULES)
    )


def _check_database(paths: AppPaths) -> CheckResult:
    report = check_database(paths=paths)
    if not report.exists:
        return CheckResult(
            "database",
            "warn",
            f"not created yet at {report.path} (import a CSV to create it)",
        )
    if report.error is not None:
        return CheckResult("database", "fail", report.error)
    if not report.ok:
        return CheckResult(
            "database",
            "fail",
            f"integrity check said {report.integrity!r}",
        )
    return CheckResult(
        "database",
        "pass",
        f"{report.path} (schema v{report.schema_version}, "
        f"{len(report.tables)} tables, integrity ok)",
    )


def _check_permissions(paths: AppPaths) -> CheckResult:
    problems: list[str] = []
    for label, directory in (
        ("data", paths.data_dir),
        ("config", paths.config_dir),
        ("cache", paths.cache_dir),
        ("logs", paths.log_dir),
    ):
        writable, detail = _nearest_writable(directory)
        if not writable:
            problems.append(f"{label}: {detail}")
    if problems:
        return CheckResult("permissions", "fail", "; ".join(problems))
    return CheckResult(
        "permissions",
        "pass",
        "data, config, cache and log paths are writable",
    )


def _check_keyring() -> CheckResult:
    try:
        import keyring  # type: ignore[import-not-found]
    except ImportError:
        return CheckResult(
            "keyring",
            "warn",
            "not installed; the in-memory credential store is used "
            "(Debian: sudo apt install python3-keyring)",
        )
    try:
        backend = keyring.get_keyring()
        name = type(backend).__name__
    except Exception as exc:  # noqa: BLE001
        return CheckResult("keyring", "warn", f"backend unavailable: {exc}")
    return CheckResult(
        "keyring", "pass", f"backend {name} (no credential was read)"
    )


def _check_connectivity() -> CheckResult:
    import urllib.error
    import urllib.request

    url = "https://api.binance.com/api/v3/ping"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = getattr(response, "status", 200)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return CheckResult(
            "public_connectivity", "warn", f"{url} unreachable: {exc}"
        )
    return CheckResult(
        "public_connectivity", "pass", f"{url} answered HTTP {status}"
    )


def _check_clock() -> CheckResult:
    import email.utils
    import urllib.request

    url = "https://api.binance.com/api/v3/time"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            header = response.headers.get("Date")
    except Exception as exc:  # noqa: BLE001
        return CheckResult(
            "system_clock", "warn", f"could not read a clock source: {exc}"
        )
    if not header:
        return CheckResult(
            "system_clock", "warn", "the clock source sent no Date header"
        )
    parsed = email.utils.parsedate_to_datetime(header)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    drift = abs((datetime.now(timezone.utc) - parsed).total_seconds())
    if drift <= 120:
        return CheckResult(
            "system_clock", "pass", f"drift {drift:.0f}s vs UTC"
        )
    return CheckResult(
        "system_clock",
        "warn",
        f"drift {drift:.0f}s vs UTC; enable NTP (timedatectl set-ntp true)",
    )


def _check_qt() -> CheckResult:
    try:
        from PyQt6.QtCore import QLibraryInfo
    except Exception as exc:  # noqa: BLE001
        return CheckResult("qt_resources", "fail", f"PyQt6 unusable: {exc}")
    plugins = Path(
        QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
    )
    if not plugins.is_dir():
        return CheckResult(
            "qt_resources", "fail", f"Qt plugin directory missing: {plugins}"
        )
    return CheckResult("qt_resources", "pass", f"Qt plugins at {plugins}")


def _check_translations() -> CheckResult:
    from crypto_trading_lab.i18n.translations import (
        TRANSLATION_DIR,
        translation_file,
    )

    if not TRANSLATION_DIR.is_dir():
        return CheckResult(
            "translations",
            "warn",
            f"translation directory missing: {TRANSLATION_DIR}",
        )
    spanish = translation_file("es")
    if spanish.exists():
        return CheckResult(
            "translations",
            "pass",
            f"English source plus {spanish.name}",
        )
    return CheckResult(
        "translations",
        "warn",
        "English source only; no compiled Spanish file",
    )


def _check_xdg(paths: AppPaths) -> CheckResult:
    resolved = {
        "config": paths.config_dir,
        "data": paths.data_dir,
        "cache": paths.cache_dir,
        "log": paths.log_dir,
    }
    if not all(path.is_absolute() for path in resolved.values()):
        return CheckResult("xdg_paths", "fail", "some paths are not absolute")
    return CheckResult(
        "xdg_paths", "pass", f"data directory {paths.data_dir}"
    )


def _check_english_docs(root: Path | None) -> CheckResult:
    if root is None:
        return CheckResult(
            "english_documentation", "warn", "the docs/ tree was not found"
        )
    developers = Path(root) / "en" / "developers"
    if developers.is_dir():
        return CheckResult("english_documentation", "pass", f"{developers}")
    return CheckResult(
        "english_documentation", "warn", f"{developers} is missing"
    )


def _check_spanish_docs(root: Path | None) -> CheckResult:
    if root is None:
        return CheckResult(
            "spanish_documentation", "warn", "the docs/ tree was not found"
        )
    spanish = Path(root) / "es"
    if spanish.is_dir():
        return CheckResult("spanish_documentation", "pass", f"{spanish}")
    return CheckResult(
        "spanish_documentation",
        "warn",
        "no docs/es tree yet; Spanish falls back to English",
    )


def run_doctor(
    *,
    paths: AppPaths | None = None,
    network: bool = False,
    root: Path | None = None,
) -> list[CheckResult]:
    """Every check chapter 22 lists, in order.

    network=False keeps the command offline and deterministic; the two
    checks that need the outside world (connectivity and clock drift)
    then report 'skip' with the reason. No credential is ever read, so
    no secret can be printed.
    """
    paths = paths or AppPaths()
    root = root if root is not None else docs_root()
    results = [
        _check_python(),
        _check_modules(),
        _check_database(paths),
        _check_permissions(paths),
        _check_keyring(),
    ]
    if network:
        results.append(_check_connectivity())
        results.append(_check_clock())
    else:
        results.append(
            CheckResult(
                "public_connectivity",
                "skip",
                "offline by default; run 'doctor --network' to test it",
            )
        )
        results.append(
            CheckResult(
                "system_clock",
                "skip",
                "offline by default; run 'doctor --network' to measure drift",
            )
        )
    results.extend(
        [
            _check_qt(),
            _check_translations(),
            _check_xdg(paths),
            _check_english_docs(root),
            _check_spanish_docs(root),
        ]
    )
    return results
