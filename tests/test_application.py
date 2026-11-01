"""Tests for the shared application use cases (ROADMAP chapter 22).

These are the functions both the CLI and the GUI call, so they are
tested here without a Qt application and without any network access.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from crypto_trading_lab import application
from crypto_trading_lab.configuration.xdg import AppPaths


@pytest.fixture()
def paths(tmp_path) -> AppPaths:
    return AppPaths(
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        cache_dir=tmp_path / "cache",
        log_dir=tmp_path / "logs",
    )


def write_candles(path: Path, count: int = 240, step_minutes: int = 1) -> Path:
    """A deterministic wave: it crosses its own moving averages."""
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    lines = ["timestamp,open,high,low,close,volume"]
    for index in range(count):
        price = 100 + 8 * math.sin(index / 7)
        open_ = price
        close = 100 + 8 * math.sin((index + 1) / 7)
        high = max(open_, close) + 0.5
        low = min(open_, close) - 0.5
        stamp = (
            start + timedelta(minutes=index * step_minutes)
        ).isoformat()
        lines.append(
            f"{stamp},{open_:.4f},{high:.4f},{low:.4f},{close:.4f},10"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_config(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# -- CSV import ------------------------------------------------------------


def test_import_csv_file_persists_candles(paths, tmp_path):
    csv_path = write_candles(tmp_path / "candles.csv", count=3)
    outcome = application.import_csv_file(csv_path, paths=paths)
    assert outcome.ok
    assert outcome.saved == 3
    assert outcome.symbol == "BTC/USDT"
    assert outcome.interval == "1m"
    assert "Imported 3 candles" in outcome.message
    assert paths.database_file.exists()


def test_import_csv_file_rejects_bad_rows_without_creating_database(
    paths, tmp_path
):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text(
        "timestamp,open,high,low,close,volume\n"
        "2024-01-01T00:00:00+00:00,100,110,90,-5,10\n",
        encoding="utf-8",
    )
    outcome = application.import_csv_file(csv_path, paths=paths)
    assert not outcome.ok
    assert outcome.saved == 0
    assert "negative" in outcome.message
    assert not paths.database_file.exists()


def test_import_csv_file_missing_file_is_reported(paths, tmp_path):
    outcome = application.import_csv_file(tmp_path / "nope.csv", paths=paths)
    assert not outcome.ok
    assert "does not exist" in outcome.message


def test_import_csv_file_honours_symbol_and_interval(paths, tmp_path):
    csv_path = write_candles(tmp_path / "eth.csv", count=2, step_minutes=5)
    outcome = application.import_csv_file(
        csv_path, symbol="ETH/USDT", interval="5m", paths=paths
    )
    assert outcome.ok
    assert outcome.symbol == "ETH/USDT"
    assert outcome.interval == "5m"


# -- database check --------------------------------------------------------


def test_check_database_reports_missing_file(paths):
    report = application.check_database(paths=paths)
    assert not report.exists
    assert not report.ok
    assert report.integrity == "missing"
    assert not paths.database_file.exists()


def test_check_database_reports_real_counts(paths, tmp_path):
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv", count=4), paths=paths
    )
    report = application.check_database(paths=paths)
    assert report.ok
    assert report.schema_version == 2
    assert report.integrity == "ok"
    assert report.tables["candles"] == 4
    assert "audit" in report.tables


# -- backtest --------------------------------------------------------------


def test_backtest_runs_over_imported_candles(paths, tmp_path):
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv"), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "fast": 5, "slow": 20},
    )
    run = application.run_backtest_file(config, paths=paths)
    assert run.candle_count == 240
    assert "SMA(5)" in run.strategy_name
    assert run.result.candle_count == 240
    assert run.result.initial_capital == 10000
    # The wave crosses repeatedly, so the strategy must trade.
    assert run.report.trades.number_of_trades > 0
    assert run.report.benchmark is not None
    assert run.report.benchmark.benchmark_name == "Buy and hold"


def test_the_backtest_records_which_parameters_ran(paths, tmp_path):
    """Chapter 33.4: a result must be traceable to the parameters used."""
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv"), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "fast": 5, "slow": 20},
    )

    run = application.run_backtest_file(config, paths=paths)

    recorded = run.result.config_metadata["strategy_parameters"]
    assert recorded == "ma_crossover@1.0.0(fast=5, slow=20)"


def test_the_backtest_rejects_an_impossible_parameter_pair(paths, tmp_path):
    """Chapter 33.4: invalid combinations die before execution, not during."""
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv"), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "fast": 30, "slow": 10},
    )

    with pytest.raises(application.ApplicationError) as error:
        application.run_backtest_file(config, paths=paths)
    assert "fast must be smaller than slow" in str(error.value)


def test_the_backtest_refuses_a_strategy_whose_warmup_cannot_fit(paths, tmp_path):
    """Chapter 33.7: no candle will ever be enough, so do not spend the run."""
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv", count=240), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "fast": 10, "slow": 500},
    )

    with pytest.raises(application.ApplicationError) as error:
        application.run_backtest_file(config, paths=paths)
    message = str(error.value)
    assert "can never act" in message
    assert "warmup" in message


def test_the_backtest_keeps_the_warnings_validation_raised(paths, tmp_path):
    """A warning does not stop the run; it travels with the result."""
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv", count=240), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "fast": 5, "slow": 150},
    )

    run = application.run_backtest_file(config, paths=paths)

    assert run.validation is not None
    assert run.validation.ok
    assert any("warm-up eats" in issue.message for issue in run.validation.warnings)


def test_the_backtest_says_what_the_user_must_not_forget(paths, tmp_path):
    """Chapter 33.8: the number is never shown without its caveats."""
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv"), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "fast": 5, "slow": 20},
    )

    run = application.run_backtest_file(config, paths=paths)

    assert run.research_warnings
    assert any("IN-SAMPLE" in statement for statement in run.research_warnings)
    assert any(
        "does not necessarily mean a better strategy" in statement
        for statement in run.research_warnings
    )



def test_backtest_benchmark_can_be_disabled(paths, tmp_path):
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv"), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "buy_and_hold", "benchmark": "none"},
    )
    run = application.run_backtest_file(config, paths=paths)
    assert run.report.benchmark is None


def test_backtest_without_database_is_an_honest_error(paths, tmp_path):
    config = write_config(
        tmp_path / "strategy.json", {"strategy": "ma_crossover"}
    )
    with pytest.raises(application.ApplicationError) as error:
        application.run_backtest_file(config, paths=paths)
    assert "no database yet" in str(error.value)
    assert not paths.database_file.exists()


def test_backtest_without_candles_is_an_honest_error(paths, tmp_path):
    # A database that exists but holds no candles.
    from crypto_trading_lab.persistence.database import (
        create_database,
        database_engine,
    )

    paths.data_dir.mkdir(parents=True, exist_ok=True)
    engine = database_engine(paths.database_file)
    create_database(engine)
    engine.dispose()
    config = write_config(
        tmp_path / "strategy.json", {"strategy": "ma_crossover"}
    )
    with pytest.raises(application.ApplicationError) as error:
        application.run_backtest_file(config, paths=paths)
    assert "not enough stored candles" in str(error.value)


def test_backtest_rejects_unknown_strategy(paths, tmp_path):
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv", count=10), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json", {"strategy": "does_not_exist"}
    )
    with pytest.raises(application.ApplicationError) as error:
        application.run_backtest_file(config, paths=paths)
    message = str(error.value)
    assert "unknown strategy" in message
    assert "ma_crossover" in message


def test_backtest_rejects_unknown_key(paths, tmp_path):
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv", count=10), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "leverage": 10},
    )
    with pytest.raises(application.ApplicationError) as error:
        application.run_backtest_file(config, paths=paths)
    assert "leverage" in str(error.value)


def test_backtest_rejects_parameter_outside_schema(paths, tmp_path):
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv", count=10), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "fast": 0},
    )
    with pytest.raises(application.ApplicationError) as error:
        application.run_backtest_file(config, paths=paths)
    assert "fast" in str(error.value)


def test_backtest_rejects_non_numeric_capital(paths, tmp_path):
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv", count=10), paths=paths
    )
    config = write_config(
        tmp_path / "strategy.json",
        {"strategy": "ma_crossover", "initial_capital": "lots"},
    )
    with pytest.raises(application.ApplicationError) as error:
        application.run_backtest_file(config, paths=paths)
    assert "initial_capital" in str(error.value)


def test_backtest_rejects_unsupported_file_extension(tmp_path):
    path = tmp_path / "strategy.txt"
    path.write_text("strategy: ma_crossover", encoding="utf-8")
    with pytest.raises(application.ApplicationError) as error:
        application.load_config_file(path)
    assert "unsupported configuration format" in str(error.value)


def test_missing_pyyaml_is_reported_with_the_command(tmp_path, monkeypatch):
    # 'None in sys.modules' makes the next import of yaml raise ImportError.
    monkeypatch.setitem(sys.modules, "yaml", None)
    path = tmp_path / "strategy.yaml"
    path.write_text("strategy: ma_crossover\n", encoding="utf-8")
    with pytest.raises(application.ApplicationError) as error:
        application.load_config_file(path)
    assert "python3-yaml" in str(error.value)


def test_backtest_reads_yaml_when_pyyaml_is_available(paths, tmp_path):
    pytest.importorskip("yaml")
    application.import_csv_file(
        write_candles(tmp_path / "candles.csv"), paths=paths
    )
    config = tmp_path / "strategy.yaml"
    config.write_text(
        "strategy: ma_crossover\nfast: 5\nslow: 20\n", encoding="utf-8"
    )
    run = application.run_backtest_file(config, paths=paths)
    assert "SMA(5)" in run.strategy_name


# -- catalogues ------------------------------------------------------------


def test_list_strategies_includes_builtins(paths):
    ids = [item.strategy_id for item in application.list_strategies(paths=paths)]
    assert "ma_crossover" in ids
    assert "buy_and_hold" in ids
    assert "null_strategy" in ids


def test_list_lessons_covers_the_curriculum():
    assert len(application.list_lessons()) == 48
    level_one = application.list_lessons(level=1)
    assert level_one
    assert all(lesson.level == 1 for lesson in level_one)
    assert len(level_one) < 48


def test_glossary_entries_are_parsed_from_the_markdown():
    entries = application.glossary_entries()
    assert entries
    terms = {entry.term.casefold() for entry in entries}
    assert "slippage" in terms
    # Duplicate headings collapse to one entry per term.
    assert len(terms) == len(entries)


def test_glossary_search_finds_term_and_body_matches():
    by_term = application.search_glossary("slippage")
    assert by_term
    assert by_term[0].term.casefold() == "slippage"
    assert "Definition:" in by_term[0].body

    by_body = application.search_glossary("drawdown")
    assert by_body
    assert application.search_glossary("zzzz-not-a-term") == ()
    assert application.search_glossary("   ") == ()


# -- doctor ----------------------------------------------------------------


def test_doctor_covers_every_chapter_22_check(paths):
    results = application.run_doctor(paths=paths, network=False)
    names = [result.name for result in results]
    for expected in (
        "python_version",
        "required_modules",
        "database",
        "permissions",
        "keyring",
        "public_connectivity",
        "system_clock",
        "qt_resources",
        "translations",
        "xdg_paths",
        "english_documentation",
        "spanish_documentation",
    ):
        assert expected in names
    assert all(result.status in {"pass", "warn", "skip", "fail"} for result in results)


def test_doctor_never_fails_on_a_healthy_environment(paths):
    results = application.run_doctor(paths=paths, network=False)
    failures = [result for result in results if result.status == "fail"]
    assert failures == []


def test_doctor_is_offline_by_default(paths):
    results = application.run_doctor(paths=paths, network=False)
    by_name = {result.name: result for result in results}
    assert by_name["public_connectivity"].status == "skip"
    assert by_name["system_clock"].status == "skip"


def test_doctor_never_reads_a_credential(paths, monkeypatch):
    from crypto_trading_lab.security.credentials import KeyringCredentialStore

    def forbidden(*_args, **_kwargs):
        raise AssertionError("doctor must not read credentials")

    monkeypatch.setattr(KeyringCredentialStore, "load", forbidden)
    monkeypatch.setattr(KeyringCredentialStore, "list", forbidden)
    results = application.run_doctor(paths=paths, network=False)
    assert results


def test_doctor_reports_a_missing_database_as_a_warning(paths):
    results = application.run_doctor(paths=paths, network=False)
    database = next(item for item in results if item.name == "database")
    assert database.status == "warn"
    assert "not created yet" in database.detail
