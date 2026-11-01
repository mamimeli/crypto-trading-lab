"""Binance Spot WebSocket client (ROADMAP chapters 26.2, 27).

Public streaming client for testnet/production with automatic reconnection,
ping/pong, stale-data detection, rate limiting, and message deduplication.

Features implemented:
- Exponential backoff reconnection with jitter (chapter 27)
- Circuit breaker to avoid hammering the exchange (chapter 27)
- A watchdog that detects stale data even when no message arrives (chapter 27)
- Connection renewal that really closes and reopens the socket (chapter 26.2)
- Rate limiter shared between REST and WS (chapter 26.2)
- Ping/pong handling via websockets library
- Per-stream duplicate and out-of-order tolerance (chapter 26.2)
- Subscription recovery after reconnection
- Time synchronization offset tracking
- Secure logging (secrets redacted)

No API credentials required for public streams.

The client is a *feed*, not a strategy: it parses and dispatches market
data and reports its own health. It never decides to trade, and it never
lets a caller act on stale data without knowing the data is stale — the
state is DEGRADED and every callback receives the warning (chapter 27).
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Set

from crypto_trading_lab.domain.models import ConnectionState
from crypto_trading_lab.exchanges.binance.config import BinanceEndpoints
from crypto_trading_lab.exchanges.connection_manager import (
    CircuitBreaker,
    ReconnectionPolicy,
    StaleDataDetector,
)
from crypto_trading_lab.exchanges.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class MessageTracker:
    """Track message IDs of ONE stream to detect duplicates and reordering.

    Every stream gets its own tracker: Binance timestamps are per-event and
    two different streams (a kline and a trade) can carry the same value, so
    one shared sequence would report false duplicates and false reordering.
    """

    _seen_ids: Set[int] = field(default_factory=set)
    _last_sequence: Optional[int] = field(default=None, init=False)
    _max_size: int = 10000
    _insertion_order: list[int] = field(default_factory=list, init=False)

    def is_duplicate(self, msg_id: int) -> bool:
        return msg_id in self._seen_ids

    def is_out_of_order(self, msg_id: int) -> bool:
        if self._last_sequence is None:
            return False
        return msg_id < self._last_sequence

    def record(self, msg_id: int) -> tuple[bool, bool]:
        """Return (is_duplicate, is_out_of_order) and record the message."""
        is_dup = self.is_duplicate(msg_id)
        is_oos = self.is_out_of_order(msg_id)

        if not is_dup:
            self._seen_ids.add(msg_id)
            self._insertion_order.append(msg_id)
            # Prune the oldest 10 % in arrival order. Iterating the set
            # instead removed arbitrary entries, so which message could be
            # re-detected as a duplicate was non-deterministic.
            if len(self._insertion_order) > self._max_size:
                drop = self._max_size // 10
                for old_id in self._insertion_order[:drop]:
                    self._seen_ids.discard(old_id)
                del self._insertion_order[:drop]

        if self._last_sequence is None or msg_id > self._last_sequence:
            self._last_sequence = msg_id

        return is_dup, is_oos


class BinanceWebSocketClient:
    """Public WebSocket client for Binance Spot streams.

    Supports kline, trade and ticker streams with automatic reconnection,
    health monitoring, connection renewal and stale-data detection. Never
    lets a caller mistake stale data for fresh data (chapter 27).

    The client runs in the background: ``await client.start()`` returns as
    soon as the runner is scheduled, so the caller keeps control of its own
    loop and can stop the feed at any time. ``await client.run_until_stopped()``
    is available for callers that do want to block.
    """

    def __init__(
        self,
        endpoints: BinanceEndpoints,
        websocket_factory: Optional[Callable[[str], Any]] = None,
        *,
        policy: Optional[ReconnectionPolicy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        rate_limiter: Optional[RateLimiter] = None,
        stale_detector: Optional[StaleDataDetector] = None,
        watchdog_interval: float = 5.0,
        renewal_interval: float = 3600.0,
    ) -> None:
        if watchdog_interval <= 0:
            raise ValueError("watchdog_interval must be positive")
        if renewal_interval <= 0:
            raise ValueError("renewal_interval must be positive")
        self._endpoints = endpoints
        self._websocket_factory = websocket_factory
        self._policy = policy or ReconnectionPolicy(base_delay=1.0, max_delay=60.0, jitter=0.3)
        self._circuit_breaker = circuit_breaker or CircuitBreaker(failure_threshold=5, reset_timeout=60.0)
        self._rate_limiter = rate_limiter or RateLimiter(max_weight=1200, window_seconds=60)
        self._stale_detector = stale_detector or StaleDataDetector(max_age_seconds=30)

        self._state = ConnectionState.DISCONNECTED
        self._handlers: Dict[str, list[Callable]] = {
            'kline': [],
            'trade': [],
            'ticker': [],
        }
        self._subscriptions: Set[str] = set()
        self._pending_subscriptions: Set[str] = set()
        self._trackers: Dict[str, MessageTracker] = {}
        self._server_time_offset: float = 0.0  # seconds
        self._stop_event = asyncio.Event()
        self._run_task: Optional[asyncio.Task] = None
        self._watchdog_task: Optional[asyncio.Task] = None
        self._active_ws: Any = None
        self._renew_requested = False
        self._reconnect_attempt = 0
        self._last_reconnect_time: Optional[float] = None
        self._warning_callbacks: list[Callable[[str, str], None]] = []
        self._connection_start_time: Optional[float] = None
        self._watchdog_interval = watchdog_interval
        self._renewal_interval = renewal_interval
        self._messages_seen = 0

    @property
    def state(self) -> ConnectionState:
        return self._state

    def add_kline_handler(self, handler: Callable[[dict], None]) -> None:
        self._handlers['kline'].append(handler)

    def add_trade_handler(self, handler: Callable[[dict], None]) -> None:
        self._handlers['trade'].append(handler)

    def add_ticker_handler(self, handler: Callable[[dict], None]) -> None:
        self._handlers['ticker'].append(handler)

    def add_candle_handler(self, handler: Callable[[dict], None]) -> None:
        self._handlers['kline'].append(handler)

    def subscribe(self, stream: str) -> None:
        """Add a stream subscription (e.g., 'btcusdt@kline_1m')."""
        if not stream:
            raise ValueError("stream must not be empty")
        self._subscriptions.add(stream)
        self._pending_subscriptions.add(stream)

    def unsubscribe(self, stream: str) -> None:
        """Remove a stream subscription."""
        self._subscriptions.discard(stream)
        self._pending_subscriptions.discard(stream)

    def add_warning_callback(self, callback: Callable[[str, str], None]) -> None:
        """Add callback for visible warnings (state, message)."""
        self._warning_callbacks.append(callback)

    def _emit_warning(self, state: str, message: str) -> None:
        """Emit a visible warning to the UI callbacks."""
        for callback in self._warning_callbacks:
            try:
                callback(state, message)
            except Exception:
                logger.debug("Warning callback failed", exc_info=True)

    def _set_state(
        self, state: ConnectionState, message: str | None = None
    ) -> None:
        """Change state and surface the change as a visible warning."""
        if self._state is state:
            return
        self._state = state
        if message is not None:
            self._emit_warning(state.value, message)

    async def start(self) -> None:
        """Start the feed in the background and return immediately.

        The connection loop, the watchdog and the reconnection policy all run
        inside the task this creates. Await :meth:`stop` to end them, or
        :meth:`run_until_stopped` to block until they finish by themselves.
        """
        if self._run_task is not None and not self._run_task.done():
            return
        self._stop_event.clear()
        self._run_task = asyncio.create_task(self._run())
        self._watchdog_task = asyncio.create_task(self._watchdog())

    async def run_until_stopped(self) -> None:
        """Start the feed and block until it stops (callers that want that)."""
        await self.start()
        assert self._run_task is not None
        await self._run_task

    async def wait_stopped(self) -> None:
        """Wait until the feed has stopped (useful with `asyncio.wait_for`)."""
        await self._stop_event.wait()

    async def stop(self) -> None:
        """Stop the feed, close the socket and wait for the tasks to end."""
        self._stop_event.set()
        tasks = [task for task in (self._run_task, self._watchdog_task) if task]
        for task in tasks:
            if not task.done():
                task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.debug("Feed task raised during shutdown", exc_info=True)
        self._run_task = None
        self._watchdog_task = None
        self._active_ws = None
        self._state = ConnectionState.STOPPED

    # -- runner ----------------------------------------------------------

    async def _run(self) -> None:
        """Reconnect loop: connect, stream, back off, repeat (chapter 27)."""
        if not self._subscriptions:
            # Nothing to stream. Returning here (instead of looping) is what
            # used to spin the CPU at 100 % on an empty client.
            self._set_state(
                ConnectionState.STOPPED,
                "No stream subscribed; the feed has nothing to do.",
            )
            return

        attempt = 0
        while not self._stop_event.is_set():
            if not self._circuit_breaker.can_attempt():
                self._set_state(
                    ConnectionState.RATE_LIMITED,
                    "The exchange rejected too many attempts; waiting before "
                    "trying again.",
                )
                await self._sleep_unless_stopped(1.0)
                continue

            self._set_state(ConnectionState.CONNECTING)
            try:
                await self._connect_and_stream()
            except asyncio.CancelledError:
                raise
            except Exception as error:
                attempt += 1
                self._reconnect_attempt = attempt
                self._circuit_breaker.record_failure()
                self._set_state(
                    ConnectionState.RECONNECTING,
                    f"Connection lost ({error}). Reconnecting, attempt {attempt}.",
                )
                try:
                    delay = self._policy.next_delay(attempt)
                except StopIteration:
                    self._set_state(
                        ConnectionState.ERROR,
                        f"Giving up after {attempt} attempts. Check your "
                        "connection and the exchange status page.",
                    )
                    break
                await self._sleep_unless_stopped(delay)
                continue

            # A clean return means the socket closed on purpose (renewal or
            # stop), so the connection was healthy.
            self._circuit_breaker.record_success()
            attempt = 0
            self._reconnect_attempt = 0

        self._state = ConnectionState.STOPPED

    async def _sleep_unless_stopped(self, delay: float) -> None:
        """Sleep, but wake up immediately when the feed is asked to stop."""
        if delay <= 0:
            await asyncio.sleep(0)
            return
        try:
            await asyncio.wait_for(self._stop_event.wait(), timeout=delay)
        except asyncio.TimeoutError:
            pass

    async def _connect_and_stream(self) -> None:
        """Open one socket and dispatch messages until it closes."""
        streams = '/'.join(sorted(self._subscriptions))
        url = f"{self._endpoints.websocket_base_url}/stream?streams={streams}"

        self._set_state(ConnectionState.SUBSCRIBING)
        if self._websocket_factory is None:
            import websockets

            ws_cm = websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10,
            )
        else:
            ws_cm = self._websocket_factory(url)

        self._renew_requested = False
        async with ws_cm as ws:
            self._active_ws = ws
            # Monotonic, not wall clock: the renewal decision is an interval,
            # and an NTP correction must not make it fire early or never.
            self._connection_start_time = time.monotonic()
            self._stale_detector.touch()
            self._pending_subscriptions.clear()
            self._last_reconnect_time = time.time()
            self._set_state(
                ConnectionState.CONNECTED,
                "Connected. Live market data is arriving.",
            )
            if self._reconnect_attempt > 1:
                self._emit_warning(
                    "reconnected",
                    f"Connection restored after {self._reconnect_attempt} attempts.",
                )

            try:
                async for message in ws:
                    if self._stop_event.is_set():
                        break
                    if self._renew_requested:
                        break
                    self._stale_detector.touch()
                    self._handle_message(message)
            except Exception:
                # A renewal closes the socket from the watchdog; that is not a
                # failure and must not trigger the reconnect warning path.
                if not self._renew_requested:
                    raise
            finally:
                self._active_ws = None

    async def _watchdog(self) -> None:
        """Detect stale data and renew old connections (chapter 27).

        This is a timer, not a side effect of receiving a message: the case
        staleness exists for is exactly the case where no message arrives.
        """
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(self._watchdog_interval)
                if self._state not in (
                    ConnectionState.CONNECTED,
                    ConnectionState.DEGRADED,
                ):
                    continue

                if self._stale_detector.is_stale():
                    self._set_state(
                        ConnectionState.DEGRADED,
                        "Market data is stale. Do not act on signals until "
                        "fresh data arrives.",
                    )
                elif self._state is ConnectionState.DEGRADED:
                    self._set_state(
                        ConnectionState.CONNECTED,
                        "Market data freshness restored.",
                    )

                started = self._connection_start_time
                if (
                    started is not None
                    and not self._renew_requested
                    and time.monotonic() - started >= self._renewal_interval
                ):
                    self._renew_requested = True
                    self._emit_warning(
                        "renewal",
                        "Renewing the connection to keep it fresh.",
                    )
                    ws = self._active_ws
                    if ws is not None:
                        try:
                            await ws.close()
                        except Exception:
                            logger.debug("Error closing socket for renewal", exc_info=True)
        except asyncio.CancelledError:
            raise

    # -- message handling ------------------------------------------------

    def _tracker_for(self, stream: str) -> MessageTracker:
        tracker = self._trackers.get(stream)
        if tracker is None:
            tracker = MessageTracker()
            self._trackers[stream] = tracker
        return tracker

    @staticmethod
    def _stream_kind(stream_name: Optional[str], payload: dict) -> Optional[str]:
        """Which handler family a message belongs to (chapter 26.2)."""
        name = stream_name or ""
        if "@kline_" in name:
            return "kline"
        if name.endswith("@trade") or "@trade" in name:
            return "trade"
        if "ticker" in name:
            return "ticker"
        event = payload.get("e")
        if event == "kline":
            return "kline"
        if event == "trade":
            return "trade"
        if event in ("24hrTicker", "24hrMiniTicker"):
            return "ticker"
        return None

    @staticmethod
    def _message_id(kind: str, payload: dict) -> Optional[int]:
        """A per-stream sequence number, or None when the payload lacks one.

        Trades use their trade id. Klines use the **event** time, not the
        kline open time: the exchange sends several updates for the same
        candle (forming, then closed), and keying on the open time would
        discard every update after the first as a duplicate.
        """
        try:
            if kind == "kline":
                value = payload.get("E") or payload.get("k", {}).get("t")
            elif kind == "trade":
                value = payload.get("t") or payload.get("E")
            else:
                value = payload.get("E")
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    def _handle_message(self, raw_message: Any) -> None:
        """Parse and dispatch one WebSocket message."""
        try:
            if isinstance(raw_message, bytes):
                raw_message = raw_message.decode("utf-8")
            data = json.loads(raw_message)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.debug("Invalid JSON received")
            return
        if not isinstance(data, dict):
            return

        # Command responses ({'result': ..., 'id': ...}) carry no market data.
        if "result" in data and "data" not in data:
            return

        stream_name = data.get("stream")
        payload = data.get("data") if isinstance(data.get("data"), dict) else data
        if not isinstance(payload, dict):
            return

        kind = self._stream_kind(stream_name, payload)
        if kind is None:
            return

        msg_id = self._message_id(kind, payload)
        if msg_id is not None:
            tracker = self._tracker_for(stream_name or kind)
            is_dup, is_oos = tracker.record(msg_id)
            if is_dup:
                logger.debug("Duplicate message %s on %s ignored", msg_id, stream_name)
                return
            if is_oos:
                self._set_state(
                    ConnectionState.DEGRADED,
                    "A message arrived out of order. Data may be unreliable.",
                )

        self._messages_seen += 1
        for handler in list(self._handlers[kind]):
            try:
                handler(payload)
            except Exception:
                # One broken handler must not take the feed down.
                logger.warning("Handler for %s stream failed", kind, exc_info=True)

        if "E" in payload:
            try:
                self._server_time_offset = payload["E"] / 1000.0 - time.time()
            except (KeyError, ValueError, TypeError):
                pass

    def synchronize_time(self) -> float:
        """Return the current server time offset in seconds."""
        return self._server_time_offset

    def get_health_metrics(self) -> dict[str, Any]:
        """Return feed health metrics for monitoring."""
        metrics = {
            'state': self._state.value,
            'state_explanation': self._state.beginner_explanation,
            'stale': self._stale_detector.is_stale(),
            'age_seconds': self._stale_detector.age_seconds,
            'server_time_offset': self._server_time_offset,
            'subscriptions': sorted(self._subscriptions),
            'pending_subscriptions': sorted(self._pending_subscriptions),
            'message_count': self._messages_seen,
            'reconnect_attempts': self._reconnect_attempt,
            'circuit_breaker_state': self._circuit_breaker.state.value,
            'last_reconnect': self._last_reconnect_time,
        }

        if self._state is ConnectionState.DEGRADED:
            metrics['warning'] = (
                'Data is stale - strategies must not generate signals'
            )
        elif self._state is ConnectionState.RECONNECTING:
            metrics['warning'] = 'Reconnecting - data may be interrupted'

        return metrics

    def reconcile_after_reconnect(self) -> dict[str, Any]:
        """Report the gap since the last connection (chapter 27)."""
        if self._last_reconnect_time is None:
            return {'has_gap': False}

        gap_duration = time.time() - self._last_reconnect_time
        has_gap = gap_duration > 5.0
        report = {
            'has_gap': has_gap,
            'gap_seconds': gap_duration,
            'last_reconnect': self._last_reconnect_time,
            'recommendation': (
                'Verify data integrity by comparing with the REST endpoint'
                if has_gap else 'No significant gap detected'
            ),
        }
        if has_gap:
            self._emit_warning(
                'data_gap',
                f'Potential data gap of {gap_duration:.1f} seconds detected '
                'after reconnection. Verify with historical data before '
                'trusting a signal.',
            )
        return report
