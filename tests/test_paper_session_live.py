"""Live WebSocket paper trading (ROADMAP chapters 26.2 and 57).

The feed is driven by a scripted socket, so the whole path — parse, risk
gate, fill, journal, shutdown — runs offline and deterministically.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from crypto_trading_lab.domain.models import ConnectionState, OrderSide
from crypto_trading_lab.exchanges.binance.config import (
    BINANCE_SPOT_TESTNET_ENDPOINTS,
)
from crypto_trading_lab.exchanges.binance.websocket_client import (
    BinanceWebSocketClient,
)
from crypto_trading_lab.exchanges.connection_manager import (
    ReconnectionPolicy,
    StaleDataDetector,
)
from crypto_trading_lab.execution_realism import ExecutionConfig
from crypto_trading_lab.paper_session import LivePaperConfig, run_paper_session_live

D = Decimal
MINUTE_MS = 60_000
BASE_MS = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)


class ScriptedSocket:
    """A WebSocket that yields scripted messages and then stays open."""

    def __init__(self, messages):
        self._messages = list(messages)
        self.closed = False
        self._closed_event = asyncio.Event()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        self.closed = True
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._messages:
            return self._messages.pop(0)
        # A real socket stays open waiting for data; blocking here keeps the
        # feed alive instead of pretending the connection died.
        await self._closed_event.wait()
        raise StopAsyncIteration

    async def close(self):
        self.closed = True
        self._closed_event.set()


def kline_message(
    index: int,
    close: str,
    *,
    closed: bool = True,
    interval: str = "1m",
    symbol: str = "BTCUSDT",
) -> str:
    open_ms = BASE_MS + index * MINUTE_MS
    # Every update of the same candle carries its own event time, as the
    # exchange does; a forming update arrives before the closing one.
    event_ms = open_ms + (MINUTE_MS - 1 if closed else MINUTE_MS // 2)
    return json.dumps(
        {
            "stream": f"{symbol.lower()}@kline_{interval}",
            "data": {
                "e": "kline",
                "E": event_ms,
                "s": symbol,
                "k": {
                    "t": open_ms,
                    "T": open_ms + MINUTE_MS - 1,
                    "s": symbol,
                    "i": interval,
                    "o": close,
                    "h": close,
                    "l": close,
                    "c": close,
                    "v": "5",
                    "x": closed,
                },
            },
        }
    )


class BuyThenSell:
    """Buys on the first candle it sees and sells on the third."""

    name = "buy then sell"
    version = "1.0.0"

    def __init__(self) -> None:
        self.seen = 0

    def on_candle(self, index, candles):
        self.seen += 1
        if self.seen == 1:
            return OrderSide.BUY
        if self.seen == 3:
            return OrderSide.SELL
        return None


def _config(**overrides) -> LivePaperConfig:
    values = dict(
        endpoints=BINANCE_SPOT_TESTNET_ENDPOINTS,
        symbol="BTC/USDT",
        interval="1m",
        max_runtime_seconds=0.15,
        position_fraction=D("0.5"),
    )
    values.update(overrides)
    return LivePaperConfig(**values)


def _run_live(messages, strategy=None, **overrides):
    sockets = []

    def factory(url):
        socket = ScriptedSocket(messages)
        sockets.append(socket)
        return socket

    result = asyncio.run(
        run_paper_session_live(
            strategy or BuyThenSell(),
            _config(**overrides),
            websocket_factory=factory,
        )
    )
    return result, sockets


# -- the session -----------------------------------------------------------


def test_live_session_trades_the_closed_candles_it_receives():
    messages = [
        kline_message(0, "100"),
        kline_message(1, "101"),
        kline_message(2, "102"),
    ]

    result, sockets = _run_live(messages)

    assert sockets and sockets[0].closed
    assert len(result.equity_curve) == 3
    assert result.journal.entries, "every decision is journalled"
    assert result.total_fees > 0
    # Bought on candle 1, sold on candle 3: the position is flat at the end.
    assert result.open_position == 0
    assert result.realized_pnl != 0
    assert result.final_equity != result.config.initial_capital


def test_forming_candles_are_ignored():
    messages = [
        kline_message(0, "100", closed=False),
        kline_message(0, "100", closed=True),
    ]

    result, _ = _run_live(messages)

    assert len(result.equity_curve) == 1


def test_a_session_without_candles_says_so_instead_of_pretending():
    result, _ = _run_live([])

    assert result.equity_curve == ()
    assert result.final_equity == result.config.initial_capital
    assert result.open_position == 0
    assert "no closed candle" in result.note




# -- sub-minute intervals ---------------------------------------------------


def test_a_one_second_session_still_fills_with_the_execution_model():
    # The chapter-56 model sizes the book from average daily volume, which is
    # derived from the interval. When 1s was missing from the duration table
    # the proxy came back as zero, the book had no depth and every order was
    # rejected — a silent realism loss, not a visible error.
    messages = [kline_message(index, str(100 + index)) for index in range(6)]
    result, _ = _run_live(
        messages,
        strategy=BuyThenSell(),
        interval="1s",
        execution_config=ExecutionConfig(),
    )

    assert result.config.interval == "1s"
    assert result.journal.filled_entries
    assert not [
        entry
        for entry in result.journal.entries
        if entry.risk_decision == "reject"
    ]


# -- warm-up ---------------------------------------------------------------


class SlowStrategy:
    """A strategy that needs more candles than the session will deliver."""

    name = "slow"
    version = "1.0.0"
    warmup_candles = 31

    def on_candle(self, index, candles):
        if len(candles) < self.warmup_candles:
            return None
        return OrderSide.BUY


def test_a_short_session_explains_the_warm_up_instead_of_looking_flat():
    result, _ = _run_live(
        [kline_message(0, "100"), kline_message(1, "101")],
        strategy=SlowStrategy(),
    )

    assert result.warmup_candles == 31
    assert "needs 31 candles to warm up" in result.note
    assert "received 2" in result.note
    assert "empty journal" in result.note
    # The warning must not change the account: it is an explanation, not a trade.
    assert not result.journal.entries
    assert result.final_equity == result.config.initial_capital


class EagerStrategy(SlowStrategy):
    """Declares a long warm-up but trades on the first candle anyway."""

    def on_candle(self, index, candles):
        return OrderSide.BUY


def test_the_warning_never_claims_an_empty_journal_that_is_not_empty():
    result, _ = _run_live(
        [kline_message(0, "100"), kline_message(1, "101")],
        strategy=EagerStrategy(),
    )

    assert result.warmup_candles == 31
    assert result.journal.entries, "this strategy traded during its warm-up"
    assert "could not generate a single signal" not in result.note


def test_a_session_that_warmed_up_carries_no_warm_up_warning():
    messages = [kline_message(index, "100") for index in range(31)]
    result, _ = _run_live(messages, strategy=SlowStrategy())

    assert len(result.equity_curve) == 31
    assert "warm up" not in result.note
    assert result.journal.entries, "the strategy can signal once it is warm"


def test_a_strategy_without_a_declared_warm_up_reports_zero():
    result, _ = _run_live([kline_message(0, "100")])

    assert result.warmup_candles == 0
    assert "warm up" not in result.note


def test_the_result_keeps_the_callers_capital_and_fees():
    result, _ = _run_live(
        [kline_message(0, "100")],
        initial_capital=D("2500"),
        taker_fee=D("0.002"),
    )

    assert result.config.initial_capital == D("2500")
    assert result.config.taker_fee == D("0.002")
    assert result.final_equity <= D("2500")


def test_a_live_session_writes_nothing_to_the_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    _run_live([kline_message(0, "100"), kline_message(1, "101")])

    assert list(tmp_path.iterdir()) == []


def test_the_feed_note_reports_the_connection_state():
    result, _ = _run_live([kline_message(0, "100")])

    assert "Feed:" in result.note
    assert "messages" in result.note


# -- the client ------------------------------------------------------------


def _client(socket, **kwargs) -> BinanceWebSocketClient:
    return BinanceWebSocketClient(
        BINANCE_SPOT_TESTNET_ENDPOINTS,
        lambda url: socket,
        policy=ReconnectionPolicy(base_delay=0.01, max_delay=0.02, jitter=0.0),
        **kwargs,
    )


def test_start_returns_immediately_and_stop_ends_the_feed():
    async def scenario():
        socket = ScriptedSocket([])
        client = _client(socket)
        client.subscribe("btcusdt@kline_1m")
        await asyncio.wait_for(client.start(), timeout=1.0)
        # start() only schedules the runner; the state moves when it runs.
        for _ in range(50):
            if client.state is ConnectionState.CONNECTED:
                break
            await asyncio.sleep(0.01)
        assert client.state is ConnectionState.CONNECTED
        await client.stop()
        assert client.state is ConnectionState.STOPPED
        assert socket.closed

    asyncio.run(scenario())


def test_an_empty_client_stops_instead_of_spinning():
    async def scenario():
        client = _client(ScriptedSocket([]))
        await client.start()
        assert client._run_task is not None
        await asyncio.wait_for(client._run_task, timeout=1.0)
        assert client.state is ConnectionState.STOPPED
        await client.stop()

    asyncio.run(scenario())


def test_stale_data_is_detected_without_waiting_for_a_message():
    """The watchdog, not the message handler, is what notices silence."""

    async def scenario():
        socket = ScriptedSocket([])
        client = _client(
            socket,
            stale_detector=StaleDataDetector(max_age_seconds=0.0),
            watchdog_interval=0.01,
        )
        client.subscribe("btcusdt@kline_1m")
        warnings = []
        degraded = asyncio.Event()

        def on_warning(state, message):
            warnings.append(state)
            if state == "degraded":
                degraded.set()

        client.add_warning_callback(on_warning)
        await client.start()
        try:
            # Wait for the signal, not for a fixed number of 10 ms sleeps:
            # the watchdog needs real elapsed time, and on Windows those
            # sleeps can all return early.
            try:
                await asyncio.wait_for(degraded.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                pytest.fail("the watchdog must report stale data on its own")
            assert client.state is ConnectionState.DEGRADED
            assert "degraded" in warnings
        finally:
            await client.stop()

    asyncio.run(scenario())


def test_renewal_really_closes_and_reconnects():
    """Renewal used to log a line and keep the dead socket open."""

    async def scenario():
        sockets = []
        reopened = asyncio.Event()

        def factory(url):
            socket = ScriptedSocket([])
            sockets.append(socket)
            if len(sockets) >= 2:
                reopened.set()
            return socket

        client = BinanceWebSocketClient(
            BINANCE_SPOT_TESTNET_ENDPOINTS,
            factory,
            policy=ReconnectionPolicy(base_delay=0.01, max_delay=0.02, jitter=0.0),
            watchdog_interval=0.01,
            renewal_interval=0.03,
        )
        client.subscribe("btcusdt@kline_1m")
        await client.start()
        try:
            # Wait for the signal instead of polling: a loop of 100 sleeps of
            # 10 ms is not a clock. On Windows the event loop clock advances
            # only every 15.6 ms, so those sleeps can all return early and the
            # loop finishes before the 30 ms renewal interval has elapsed.
            try:
                await asyncio.wait_for(reopened.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                pytest.fail("the feed must reopen the socket")
            assert sockets[0].closed
        finally:
            await client.stop()

    asyncio.run(scenario())


def test_duplicate_detection_is_per_stream():
    """A kline and a trade can share a timestamp without being duplicates."""

    async def scenario():
        kline = kline_message(0, "100")
        trade = json.dumps(
            {
                "stream": "btcusdt@trade",
                "data": {"e": "trade", "E": BASE_MS + 5, "t": 7, "p": "100"},
            }
        )
        socket = ScriptedSocket([kline, trade, trade])
        client = _client(socket)
        seen = {"kline": 0, "trade": 0}
        client.add_candle_handler(lambda payload: seen.__setitem__("kline", seen["kline"] + 1))
        client.add_trade_handler(lambda payload: seen.__setitem__("trade", seen["trade"] + 1))
        client.subscribe("btcusdt@kline_1m")
        client.subscribe("btcusdt@trade")
        await client.start()
        try:
            for _ in range(50):
                if seen["trade"] == 1 and seen["kline"] == 1:
                    break
                await asyncio.sleep(0.01)
            assert seen == {"kline": 1, "trade": 1}, (
                "the repeated trade must be dropped, the kline must not be"
            )
        finally:
            await client.stop()

    asyncio.run(scenario())


def test_ticker_messages_are_dispatched():
    async def scenario():
        ticker = json.dumps(
            {
                "stream": "btcusdt@ticker",
                "data": {"e": "24hrTicker", "E": BASE_MS, "s": "BTCUSDT", "c": "100"},
            }
        )
        socket = ScriptedSocket([ticker])
        client = _client(socket)
        received = []
        client.add_ticker_handler(received.append)
        client.subscribe("btcusdt@ticker")
        await client.start()
        try:
            for _ in range(50):
                if received:
                    break
                await asyncio.sleep(0.01)
            assert received and received[0]["s"] == "BTCUSDT"
        finally:
            await client.stop()

    asyncio.run(scenario())


def test_a_broken_handler_does_not_kill_the_feed():
    async def scenario():
        socket = ScriptedSocket(
            [kline_message(0, "100"), kline_message(1, "101")]
        )
        client = _client(socket)
        calls = []

        def broken(payload):
            raise RuntimeError("handler bug")

        client.add_candle_handler(broken)
        client.add_candle_handler(calls.append)
        client.subscribe("btcusdt@kline_1m")
        await client.start()
        try:
            for _ in range(50):
                if len(calls) >= 2:
                    break
                await asyncio.sleep(0.01)
            assert len(calls) == 2
        finally:
            await client.stop()

    asyncio.run(scenario())


def test_a_malformed_message_is_ignored():
    async def scenario():
        socket = ScriptedSocket(["not json", json.dumps({"stream": "x"})])
        client = _client(socket)
        received = []
        client.add_candle_handler(received.append)
        client.subscribe("btcusdt@kline_1m")
        await client.start()
        try:
            await asyncio.sleep(0.05)
            assert received == []
            assert client.state is not ConnectionState.ERROR
        finally:
            await client.stop()

    asyncio.run(scenario())


# -- never signal on stale data (chapter 27) --------------------------------


class StubFeedClient:
    """A feed client whose state the test controls directly."""

    def __init__(self) -> None:
        self.state = ConnectionState.CONNECTED
        self._candle_handlers = []
        self._warning_handlers = []
        self._stopped = asyncio.Event()
        self.subscriptions = []

    def add_candle_handler(self, handler) -> None:
        self._candle_handlers.append(handler)

    def add_warning_callback(self, callback) -> None:
        self._warning_handlers.append(callback)

    def subscribe(self, stream: str) -> None:
        self.subscriptions.append(stream)

    def push(self, message: str) -> None:
        payload = json.loads(message)["data"]
        for handler in self._candle_handlers:
            handler(payload)

    async def start(self) -> None:
        return None

    async def wait_stopped(self) -> None:
        await self._stopped.wait()

    async def stop(self) -> None:
        self._stopped.set()

    def get_health_metrics(self):
        return {
            "state": self.state.value,
            "message_count": 0,
            "reconnect_attempts": 0,
        }


def test_no_signal_is_generated_while_the_feed_is_degraded():
    """Chapter 27: stale data must not produce a buy or a sell."""

    async def scenario():
        client = StubFeedClient()
        strategy = BuyThenSell()
        task = asyncio.create_task(
            run_paper_session_live(
                strategy,
                _config(max_runtime_seconds=5),
                client=client,
            )
        )
        await asyncio.sleep(0)
        client.push(kline_message(0, "100"))  # BUY here
        client.state = ConnectionState.DEGRADED
        client.push(kline_message(1, "101"))  # buffered, not evaluated
        client.push(kline_message(2, "102"))  # the SELL would be here
        await client.stop()
        result = await task
        return result, strategy

    result, strategy = asyncio.run(scenario())

    # Only the first candle was evaluated: the strategy saw one candle, so
    # its third-candle sell never happened and the position stays open.
    assert strategy.seen == 1
    assert result.open_position > 0
    assert "degraded" in result.note
    assert "without generating any signal" in result.note
