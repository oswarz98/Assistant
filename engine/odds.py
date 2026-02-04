from __future__ import annotations

from typing import Tuple


def american_to_decimal(odds: float) -> float:
    if odds == 0:
        raise ValueError("American odds cannot be zero.")
    if odds > 0:
        return round(1 + odds / 100, 4)
    return round(1 + 100 / abs(odds), 4)


def decimal_to_american(decimal_odds: float) -> float:
    if decimal_odds <= 1:
        raise ValueError("Decimal odds must be greater than 1.")
    if decimal_odds >= 2:
        return round((decimal_odds - 1) * 100, 2)
    return round(-100 / (decimal_odds - 1), 2)


def american_to_fractional(odds: float) -> Tuple[int, int]:
    decimal_odds = american_to_decimal(odds)
    numerator = decimal_odds - 1
    return _approx_fraction(numerator)


def implied_probability_from_american(odds: float) -> float:
    if odds == 0:
        raise ValueError("American odds cannot be zero.")
    if odds > 0:
        return round(100 / (odds + 100), 4)
    return round(abs(odds) / (abs(odds) + 100), 4)


def expected_value(model_probability: float, odds: float) -> float:
    decimal_odds = american_to_decimal(odds)
    return round((model_probability * (decimal_odds - 1)) - (1 - model_probability), 4)


def _approx_fraction(value: float) -> Tuple[int, int]:
    denominator = 100
    numerator = int(round(value * denominator))
    divisor = _gcd(abs(numerator), denominator)
    return numerator // divisor, denominator // divisor


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a
