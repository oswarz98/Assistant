from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np


def ema(values: List[float], period: int) -> List[float]:
    if not values:
        return []
    alpha = 2 / (period + 1)
    ema_values = [values[0]]
    for value in values[1:]:
        ema_values.append(alpha * value + (1 - alpha) * ema_values[-1])
    return ema_values


def rsi(values: List[float], period: int = 14) -> float:
    if len(values) < period + 1:
        return 50.0
    deltas = np.diff(values)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(values: List[float]) -> Tuple[float, float]:
    if len(values) < 26:
        return 0.0, 0.0
    ema_fast = ema(values, 12)
    ema_slow = ema(values, 26)
    macd_line = np.array(ema_fast[-len(ema_slow):]) - np.array(ema_slow)
    signal = ema(macd_line.tolist(), 9)
    return float(macd_line[-1]), float(signal[-1])


def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return float(np.mean(np.array(highs) - np.array(lows))) if highs else 0.0
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    return float(np.mean(trs[-period:]))


def vwap(highs: List[float], lows: List[float], closes: List[float], volumes: List[float]) -> Optional[float]:
    if not volumes:
        return None
    typical = (np.array(highs) + np.array(lows) + np.array(closes)) / 3
    cumulative = np.cumsum(typical * np.array(volumes))
    volume_sum = np.cumsum(volumes)
    if volume_sum[-1] == 0:
        return None
    return float(cumulative[-1] / volume_sum[-1])


def detect_levels(values: List[float], window: int = 5) -> Tuple[List[float], List[float]]:
    supports: List[float] = []
    resistances: List[float] = []
    if len(values) < window * 2:
        return supports, resistances
    for idx in range(window, len(values) - window):
        slice_vals = values[idx - window : idx + window + 1]
        current = values[idx]
        if current == min(slice_vals):
            supports.append(current)
        if current == max(slice_vals):
            resistances.append(current)
    return supports[-3:], resistances[-3:]
