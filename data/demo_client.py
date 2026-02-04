from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import List

import numpy as np

from data.api_base import MarketDataClient
from models.types import MarketType, PriceBar


class DemoDataClient(MarketDataClient):
    def supported_markets(self) -> List[MarketType]:
        return [MarketType.STOCKS, MarketType.CRYPTO, MarketType.FOREX]

    def list_symbols(self, market: MarketType) -> List[str]:
        if market == MarketType.STOCKS:
            return ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]
        if market == MarketType.CRYPTO:
            return ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
        return ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD"]

    def fetch_bars(self, symbol: str, market: MarketType, timeframe: str, limit: int = 200) -> List[PriceBar]:
        now = datetime.utcnow()
        delta = self._timeframe_to_delta(timeframe)
        times = [now - i * delta for i in range(limit)][::-1]
        base = self._base_price(symbol, market)
        noise = np.random.default_rng(seed=len(symbol) + len(timeframe)).normal(0, 0.8, size=limit)
        trend = np.linspace(-2.5, 2.5, limit)
        prices = base + trend + noise + 2.5 * np.sin(np.linspace(0, 3 * math.pi, limit))

        bars: List[PriceBar] = []
        for idx, ts in enumerate(times):
            open_price = prices[idx] + np.random.normal(0, 0.3)
            close_price = prices[idx] + np.random.normal(0, 0.3)
            high = max(open_price, close_price) + abs(np.random.normal(0.4, 0.2))
            low = min(open_price, close_price) - abs(np.random.normal(0.4, 0.2))
            volume = abs(np.random.normal(1200, 350))
            bars.append(
                PriceBar(
                    timestamp=ts.isoformat(),
                    open=float(open_price),
                    high=float(high),
                    low=float(low),
                    close=float(close_price),
                    volume=float(volume),
                )
            )
        return bars

    def _timeframe_to_delta(self, timeframe: str) -> timedelta:
        if timeframe.endswith("m"):
            minutes = int(timeframe.replace("m", ""))
            return timedelta(minutes=minutes)
        if timeframe.endswith("h"):
            hours = int(timeframe.replace("h", ""))
            return timedelta(hours=hours)
        return timedelta(days=1)

    def _base_price(self, symbol: str, market: MarketType) -> float:
        if market == MarketType.CRYPTO:
            return 20000 if symbol.startswith("BTC") else 1500
        if market == MarketType.FOREX:
            return 1.05 if "EUR" in symbol else 135
        return 150
