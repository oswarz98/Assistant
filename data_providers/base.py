from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from models.types import Game, League, MarketSnapshot


class SportsDataProvider(ABC):
    @abstractmethod
    def supported_leagues(self) -> List[League]:
        raise NotImplementedError

    @abstractmethod
    def list_games(self, league: League) -> List[Game]:
        raise NotImplementedError


class OddsDataProvider(ABC):
    @abstractmethod
    def list_snapshots(self, league: League) -> List[MarketSnapshot]:
        raise NotImplementedError


class ProviderBundle:
    def __init__(self, sports: SportsDataProvider, odds: OddsDataProvider) -> None:
        self.sports = sports
        self.odds = odds
