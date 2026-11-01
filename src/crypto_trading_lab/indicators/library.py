"""Technical indicators (ROADMAP.md chapter 31).

Every indicator uses a common interface, validates its parameters,
documents its formula and warm-up period, avoids look-ahead bias, and
supports batch calculation. Results are aligned with the input: index
``i`` uses only candles up to and including ``i``.
"""

from __future__ import annotations

import abc
from collections import deque
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from crypto_trading_lab.domain.models import Candle

__all__ = [
    "Indicator",
    "IndicatorResult",
    "IndicatorError",
    "SMA",
    "SMAStream",
    "EMA",
    "EMAStream",
    "RSI",
    "RSIStream",
    "BollingerBands",
    "ATR",
    "ATRStream",
    "ROC",
    "ROCStream",
]


class IndicatorError(ValueError):
    """Invalid indicator configuration or input."""


@dataclass(frozen=True)
class IndicatorResult:
    """One indicator run: values aligned with the input candles.

    ``values[i]`` is the indicator value after candle ``i``, or ``None``
    during the warm-up period.
    """

    name: str
    values: tuple[Decimal | None, ...]

    @property
    def warmup_length(self) -> int:
        """How many initial values are ``None`` (parameter-dependent)."""
        for index, value in enumerate(self.values):
            if value is not None:
                return index
        return len(self.values)


class Indicator(abc.ABC):
    """Common indicator interface (chapter 31)."""

    #: Human-readable formula for docs/UI (chapter 31).
    formula: str = ""

    @abc.abstractmethod
    def warmup(self) -> int:
        """Number of candles needed before the first value."""

    @abc.abstractmethod
    def validate(self) -> None:
        """Reject invalid parameters (e.g. period < 1)."""

    @abc.abstractmethod
    def compute(self, candles: Sequence[Candle]) -> IndicatorResult:
        """Batch calculation over ordered candles (no look-ahead)."""

    # -- shared input guard ------------------------------------------------

    @staticmethod
    def _require_ordered(candles: Sequence[Candle]) -> None:
        previous = None
        for candle in candles:
            if previous is not None and candle.open_time <= previous:
                raise IndicatorError(
                    "candles must be chronological and unique"
                )
            previous = candle.open_time


class SMA(Indicator):
    """Simple Moving Average of the close price.

    Formula: SMA(n) at time t = (C[t-n+1] + ... + C[t]) / n.
    Warm-up: the first ``n-1`` candles produce ``None``.
    """

    def __init__(self, period: int = 20) -> None:
        self.period = period
        self.validate()

    formula = "SMA(n) = (C1 + C2 + ... + Cn) / n over the last n closes"

    def validate(self) -> None:
        if not isinstance(self.period, int) or self.period < 1:
            raise IndicatorError(
                f"SMA period must be a positive integer, got {self.period!r}"
            )

    def warmup(self) -> int:
        return self.period - 1

    def compute(self, candles: Sequence[Candle]) -> IndicatorResult:
        self._require_ordered(candles)
        values: list[Decimal | None] = [None] * len(candles)
        if len(candles) < self.period:
            return IndicatorResult("SMA", tuple(values))
        window_sum = Decimal(0)
        for index, candle in enumerate(candles):
            window_sum += candle.close
            if index >= self.period:
                window_sum -= candles[index - self.period].close
            if index >= self.period - 1:
                values[index] = window_sum / Decimal(self.period)
        return IndicatorResult("SMA", tuple(values))

    def stream(self) -> "SMAStream":
        """An incremental, O(1)-per-update calculator for this period."""
        return SMAStream(self.period)


class SMAStream:
    """Incremental simple moving average (chapter 13 performance).

    Feed candles one at a time with :meth:`update`; the running mean is
    maintained in O(1) so a strategy traversing N candles does not pay an
    O(N) recompute per step. This removes the O(N^2) behaviour of
    re-running :meth:`SMA.compute` on every growing window.

    Uses a circular buffer (fixed-size array) for true O(1) updates.
    """

    def __init__(self, period: int = 20) -> None:
        if not isinstance(period, int) or period < 1:
            raise IndicatorError(
                f"SMA period must be a positive integer, got {period!r}"
            )
        self.period = period
        self._buffer = [Decimal(0)] * period
        self._index = 0
        self._count = 0
        self._sum = Decimal(0)
        self.value: Decimal | None = None
        self.prev_value: Decimal | None = None

    def update(self, candle: Candle) -> Decimal | None:
        """Feed one candle; returns the SMA value after it (or None)."""
        self.prev_value = self.value
        
        # Circular buffer: overwrite oldest value
        if self._count == self.period:
            self._sum -= self._buffer[self._index]
        else:
            self._count += 1
        
        self._buffer[self._index] = candle.close
        self._sum += candle.close
        self._index = (self._index + 1) % self.period
        
        if self._count == self.period:
            self.value = self._sum / Decimal(self.period)
        else:
            self.value = None
        return self.value


class EMA(Indicator):
    """Exponential Moving Average of the close price.

    Formula: EMA[0] = SMA(n) of the first n closes; afterwards
    EMA[t] = alpha * C[t] + (1 - alpha) * EMA[t-1] with
    alpha = 2 / (n + 1). Warm-up: first ``n-1`` candles are ``None``.
    """

    def __init__(self, period: int = 20) -> None:
        self.period = period
        self.validate()

    formula = (
        "EMA[t] = alpha * C[t] + (1 - alpha) * EMA[t-1], "
        "alpha = 2 / (n + 1); seeded with SMA(n)"
    )

    def validate(self) -> None:
        if not isinstance(self.period, int) or self.period < 1:
            raise IndicatorError(
                f"EMA period must be a positive integer, got {self.period!r}"
            )

    def warmup(self) -> int:
        return self.period - 1

    def compute(self, candles: Sequence[Candle]) -> IndicatorResult:
        self._require_ordered(candles)
        values: list[Decimal | None] = [None] * len(candles)
        n = self.period
        if len(candles) < n:
            return IndicatorResult("EMA", tuple(values))
        alpha = Decimal(2) / Decimal(n + 1)
        # Seed with the SMA of the first n closes.
        seed = sum(candles[i].close for i in range(n)) / Decimal(n)
        values[n - 1] = seed
        ema = seed
        for index in range(n, len(candles)):
            ema = alpha * candles[index].close + (Decimal(1) - alpha) * ema
            values[index] = ema
        return IndicatorResult("EMA", tuple(values))


class RSI(Indicator):
    """Relative Strength Index (Wilder).

    Formula: RSI = 100 - 100 / (1 + RS), where RS = average gain /
    average loss over the period (Wilder smoothing). Warm-up: first
    ``period`` candles are ``None``; the first value appears at index
    ``period``.
    """

    def __init__(self, period: int = 14) -> None:
        self.period = period
        self.validate()

    formula = (
        "RSI = 100 - 100 / (1 + RS); RS = avg gain / avg loss "
        "(Wilder smoothing over n periods)"
    )

    def validate(self) -> None:
        if not isinstance(self.period, int) or self.period < 1:
            raise IndicatorError(
                f"RSI period must be a positive integer, got {self.period!r}"
            )

    def warmup(self) -> int:
        return self.period

    def compute(self, candles: Sequence[Candle]) -> IndicatorResult:
        self._require_ordered(candles)
        values: list[Decimal | None] = [None] * len(candles)
        n = self.period
        if len(candles) <= n:
            return IndicatorResult("RSI", tuple(values))
        gains: list[Decimal] = []
        losses: list[Decimal] = []
        for index in range(1, n + 1):
            change = candles[index].close - candles[index - 1].close
            gains.append(max(change, Decimal(0)))
            losses.append(max(-change, Decimal(0)))
        avg_gain = sum(gains) / Decimal(n)
        avg_loss = sum(losses) / Decimal(n)
        values[n] = self._rsi_from(avg_gain, avg_loss)
        for index in range(n + 1, len(candles)):
            change = candles[index].close - candles[index - 1].close
            gain = max(change, Decimal(0))
            loss = max(-change, Decimal(0))
            avg_gain = (avg_gain * Decimal(n - 1) + gain) / Decimal(n)
            avg_loss = (avg_loss * Decimal(n - 1) + loss) / Decimal(n)
            values[index] = self._rsi_from(avg_gain, avg_loss)
        return IndicatorResult("RSI", tuple(values))

    @staticmethod
    def _rsi_from(avg_gain: Decimal, avg_loss: Decimal) -> Decimal:
        if avg_loss == 0:
            return Decimal(100) if avg_gain > 0 else Decimal(50)
        rs = avg_gain / avg_loss
        return Decimal(100) - Decimal(100) / (Decimal(1) + rs)


class BollingerBands(Indicator):
    """Bollinger Bands: SMA center ± k * rolling standard deviation.

    Warm-up: first ``period - 1`` candles are ``None`` for all three
    bands.
    """

    def __init__(self, period: int = 20, k: int | float = 2) -> None:
        self.period = period
        self.k = k
        self.validate()

    formula = "middle = SMA(n); upper/lower = middle ± k * stdev(n)"

    def validate(self) -> None:
        if not isinstance(self.period, int) or self.period < 1:
            raise IndicatorError("Bollinger period must be a positive integer")
        if not (isinstance(self.k, (int, float)) and self.k > 0):
            raise IndicatorError("Bollinger k must be a positive number")

    def warmup(self) -> int:
        return self.period - 1

    def compute(self, candles: Sequence[Candle]) -> IndicatorResult:
        self._require_ordered(candles)
        n = self.period
        values: list[Decimal | None] = [None] * len(candles)
        if len(candles) < n:
            return IndicatorResult("BB", tuple(values))
        k = Decimal(str(self.k))
        # Rolling sum and sum of squares (population stdev, classic
        # Bollinger definition).
        window_sum = Decimal(0)
        window_sq = Decimal(0)
        for index, candle in enumerate(candles):
            window_sum += candle.close
            window_sq += candle.close * candle.close
            if index >= n:
                old = candles[index - n].close
                window_sum -= old
                window_sq -= old * old
            if index >= n - 1:
                mean = window_sum / Decimal(n)
                variance = window_sq / Decimal(n) - mean * mean
                if variance < 0:  # numeric noise guard
                    variance = Decimal(0)
                stdev = variance.sqrt()
                values[index] = mean + k * stdev  # upper by convention
        return IndicatorResult("BB", tuple(values))


class ATR(Indicator):
    """Average True Range (Wilder).

    True Range = max(high - low, |high - prev close|, |low - prev
    close|). Warm-up: first ``period`` candles are ``None``.
    """

    def __init__(self, period: int = 14) -> None:
        self.period = period
        self.validate()

    formula = (
        "TR = max(H-L, |H-prevC|, |L-prevC|); "
        "ATR = Wilder-smoothed average of TR"
    )

    def validate(self) -> None:
        if not isinstance(self.period, int) or self.period < 1:
            raise IndicatorError("ATR period must be a positive integer")

    def warmup(self) -> int:
        return self.period

    def compute(self, candles: Sequence[Candle]) -> IndicatorResult:
        self._require_ordered(candles)
        n = self.period
        values: list[Decimal | None] = [None] * len(candles)
        if len(candles) <= n:
            return IndicatorResult("ATR", tuple(values))
        trs: list[Decimal] = []
        for index in range(1, len(candles)):
            candle = candles[index]
            previous = candles[index - 1].close
            tr = max(
                candle.high - candle.low,
                abs(candle.high - previous),
                abs(candle.low - previous),
            )
            trs.append(tr)
        atr = sum(trs[:n]) / Decimal(n)
        values[n] = atr
        for index in range(n + 1, len(candles)):
            atr = (atr * Decimal(n - 1) + trs[index - 1]) / Decimal(n)
            values[index] = atr
        return IndicatorResult("ATR", tuple(values))


class ROC(Indicator):
    """Rate of Change: (close[t] / close[t-n] - 1) * 100.

    Warm-up: first ``period`` candles are ``None``.
    """

    def __init__(self, period: int = 10) -> None:
        self.period = period
        self.validate()

    formula = "ROC = (C[t] / C[t-n] - 1) * 100"

    def validate(self) -> None:
        if not isinstance(self.period, int) or self.period < 1:
            raise IndicatorError("ROC period must be a positive integer")

    def warmup(self) -> int:
        return self.period

    def compute(self, candles: Sequence[Candle]) -> IndicatorResult:
        self._require_ordered(candles)
        n = self.period
        values: list[Decimal | None] = [None] * len(candles)
        for index in range(n, len(candles)):
            past = candles[index - n].close
            if past == 0:
                continue  # undefined rate of change; stays None
            values[index] = (
                candles[index].close / past - Decimal(1)
            ) * Decimal(100)
        return IndicatorResult("ROC", tuple(values))


# -- streaming variants (chapter 13 performance) -----------------------------
#
# ``X.compute(candles)`` recomputes the whole series, so calling it once per
# candle inside a backtest costs O(N^2). The streams below keep the state the
# formula needs and return one value per candle in O(1). Each one reproduces
# its batch counterpart exactly — ``tests/indicators/test_streams.py`` compares
# them value by value, because a stream that drifts from the documented
# formula would silently change every backtest that uses it.


class EMAStream:
    """Incremental EMA, seeded with the SMA of the first ``period`` closes."""

    def __init__(self, period: int = 20) -> None:
        if not isinstance(period, int) or period < 1:
            raise IndicatorError(
                f"EMA period must be a positive integer, got {period!r}"
            )
        self.period = period
        self._alpha = Decimal(2) / Decimal(period + 1)
        self._seed_closes: list[Decimal] = []
        self._ema: Decimal | None = None
        self.value: Decimal | None = None
        self.prev_value: Decimal | None = None

    def update(self, candle: Candle) -> Decimal | None:
        self.prev_value = self.value
        if self._ema is None:
            self._seed_closes.append(candle.close)
            if len(self._seed_closes) == self.period:
                self._ema = sum(self._seed_closes) / Decimal(self.period)
                self.value = self._ema
            else:
                self.value = None
        else:
            self._ema = (
                self._alpha * candle.close
                + (Decimal(1) - self._alpha) * self._ema
            )
            self.value = self._ema
        return self.value


class RSIStream:
    """Incremental RSI with Wilder smoothing."""

    def __init__(self, period: int = 14) -> None:
        if not isinstance(period, int) or period < 1:
            raise IndicatorError(
                f"RSI period must be a positive integer, got {period!r}"
            )
        self.period = period
        self._previous_close: Decimal | None = None
        self._gains: list[Decimal] = []
        self._losses: list[Decimal] = []
        self._avg_gain: Decimal | None = None
        self._avg_loss: Decimal | None = None
        self.value: Decimal | None = None
        self.prev_value: Decimal | None = None

    def update(self, candle: Candle) -> Decimal | None:
        self.prev_value = self.value
        if self._previous_close is None:
            self._previous_close = candle.close
            self.value = None
            return None
        change = candle.close - self._previous_close
        self._previous_close = candle.close
        gain = max(change, Decimal(0))
        loss = max(-change, Decimal(0))
        if self._avg_gain is None:
            self._gains.append(gain)
            self._losses.append(loss)
            if len(self._gains) == self.period:
                self._avg_gain = sum(self._gains) / Decimal(self.period)
                self._avg_loss = sum(self._losses) / Decimal(self.period)
                self.value = RSI._rsi_from(self._avg_gain, self._avg_loss)
            else:
                self.value = None
        else:
            n = Decimal(self.period)
            self._avg_gain = (
                self._avg_gain * (n - 1) + gain
            ) / n
            self._avg_loss = (
                self._avg_loss * (n - 1) + loss
            ) / n
            self.value = RSI._rsi_from(self._avg_gain, self._avg_loss)
        return self.value


class ATRStream:
    """Incremental ATR with Wilder smoothing of the true range."""

    def __init__(self, period: int = 14) -> None:
        if not isinstance(period, int) or period < 1:
            raise IndicatorError("ATR period must be a positive integer")
        self.period = period
        self._previous_close: Decimal | None = None
        self._true_ranges: list[Decimal] = []
        self._atr: Decimal | None = None
        self.value: Decimal | None = None
        self.prev_value: Decimal | None = None

    def update(self, candle: Candle) -> Decimal | None:
        self.prev_value = self.value
        if self._previous_close is None:
            self._previous_close = candle.close
            self.value = None
            return None
        true_range = max(
            candle.high - candle.low,
            abs(candle.high - self._previous_close),
            abs(candle.low - self._previous_close),
        )
        self._previous_close = candle.close
        if self._atr is None:
            self._true_ranges.append(true_range)
            if len(self._true_ranges) == self.period:
                self._atr = sum(self._true_ranges) / Decimal(self.period)
                self.value = self._atr
            else:
                self.value = None
        else:
            n = Decimal(self.period)
            self._atr = (self._atr * (n - 1) + true_range) / n
            self.value = self._atr
        return self.value


class ROCStream:
    """Incremental rate of change over ``period`` candles."""

    def __init__(self, period: int = 10) -> None:
        if not isinstance(period, int) or period < 1:
            raise IndicatorError("ROC period must be a positive integer")
        self.period = period
        self._closes: deque = deque(maxlen=period + 1)
        self.value: Decimal | None = None
        self.prev_value: Decimal | None = None

    def update(self, candle: Candle) -> Decimal | None:
        self.prev_value = self.value
        self._closes.append(candle.close)
        if len(self._closes) < self.period + 1:
            self.value = None
            return None
        past = self._closes[0]
        if past == 0:
            self.value = None  # undefined rate of change, as in the batch form
            return None
        self.value = (candle.close / past - Decimal(1)) * Decimal(100)
        return self.value
