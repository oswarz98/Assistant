from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from models.types import MarketType, PriceBar


class MarketDataClient(ABC):
    @abstractmethod
    def supported_markets(self) -> List[MarketType]:
        raise NotImplementedError

    @abstractmethod
    def list_symbols(self, market: MarketType) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def fetch_bars(self, symbol: str, market: MarketType, timeframe: str, limit: int = 200) -> List[PriceBar]:
        raise NotImplementedError
