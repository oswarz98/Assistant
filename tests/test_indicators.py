from indicators.core import atr, ema, macd, rsi


def test_ema_length_matches_input() -> None:
    values = [1, 2, 3, 4, 5]
    result = ema(values, 3)
    assert len(result) == len(values)


def test_rsi_bounds() -> None:
    values = list(range(1, 50))
    result = rsi(values, 14)
    assert 0 <= result <= 100


def test_macd_returns_tuple() -> None:
    values = list(range(1, 60))
    macd_val, signal = macd(values)
    assert isinstance(macd_val, float)
    assert isinstance(signal, float)


def test_atr_positive() -> None:
    highs = [10, 11, 12, 13, 14, 15]
    lows = [9, 9.5, 10, 11, 12, 13]
    closes = [9.5, 10.5, 11, 12.5, 13, 14]
    value = atr(highs, lows, closes, period=3)
    assert value > 0
