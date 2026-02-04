from __future__ import annotations

from typing import Dict, List

from data_providers.base import ProviderBundle
from engine.model import OutcomeModel, timestamp_now
from models.types import GameAnalysis, League, MarketSnapshot, MarketType


class OddsAnalyzer:
    def __init__(self, providers: ProviderBundle) -> None:
        self.providers = providers
        self.model = OutcomeModel()

    def analyze_league(self, league: League) -> List[GameAnalysis]:
        games = self.providers.sports.list_games(league)
        snapshots = self.providers.odds.list_snapshots(league)
        by_game: Dict[str, List[MarketSnapshot]] = {}
        for snapshot in snapshots:
            by_game.setdefault(snapshot.game_id, []).append(snapshot)

        analyses: List[GameAnalysis] = []
        for game in games:
            game_snapshots = by_game.get(game.id, [])
            recommendations = self.model.analyze_game(game, game_snapshots)
            analyses.append(
                GameAnalysis(
                    game=game,
                    recommendations=recommendations,
                    updated_at=timestamp_now(),
                )
            )
        return analyses

    def analyze_game(self, league: League, game_id: str) -> GameAnalysis | None:
        analyses = self.analyze_league(league)
        for analysis in analyses:
            if analysis.game.id == game_id:
                return analysis
        return None

    def list_snapshots(self, league: League) -> List[MarketSnapshot]:
        return self.providers.odds.list_snapshots(league)

    def list_games(self, league: League) -> List[str]:
        return [game.id for game in self.providers.sports.list_games(league)]

    def get_markets_for_game(self, league: League, game_id: str) -> List[MarketType]:
        snapshots = self.providers.odds.list_snapshots(league)
        return [snap.market for snap in snapshots if snap.game_id == game_id]
