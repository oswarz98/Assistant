from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from data_providers.base import OddsDataProvider, ProviderBundle, SportsDataProvider
from models.types import Game, GameContext, League, MarketOdds, MarketSnapshot, MarketType, OddsMovementPoint, TeamMetrics


class DemoSportsProvider(SportsDataProvider):
    def __init__(self, payload: Dict) -> None:
        self.payload = payload

    def supported_leagues(self) -> List[League]:
        leagues = {game["league"] for game in self.payload.get("games", [])}
        return [League(league) for league in sorted(leagues)]

    def list_games(self, league: League) -> List[Game]:
        games: List[Game] = []
        for entry in self.payload.get("games", []):
            if entry["league"] != league.value:
                continue
            games.append(
                Game(
                    id=entry["id"],
                    league=league,
                    start_time=entry["start_time"],
                    home_team=entry["home_team"],
                    away_team=entry["away_team"],
                    venue=entry["venue"],
                    metrics_home=TeamMetrics(**entry["metrics_home"]),
                    metrics_away=TeamMetrics(**entry["metrics_away"]),
                    context=GameContext(**entry["context"]),
                )
            )
        return games


class DemoOddsProvider(OddsDataProvider):
    def __init__(self, payload: Dict) -> None:
        self.payload = payload

    def list_snapshots(self, league: League) -> List[MarketSnapshot]:
        game_ids = {game["id"] for game in self.payload.get("games", []) if game["league"] == league.value}
        snapshots: List[MarketSnapshot] = []
        for entry in self.payload.get("odds", []):
            if entry["game_id"] not in game_ids:
                continue
            market = MarketType(entry["market"])
            books: List[MarketOdds] = []
            for book, sides in entry["books"].items():
                books.append(
                    MarketOdds(
                        book=book,
                        home=sides["home"],
                        away=sides["away"],
                        line=entry.get("line"),
                        updated_at=entry["updated_at"],
                    )
                )
            movement = [
                OddsMovementPoint(
                    timestamp=point["timestamp"],
                    home=point["home"],
                    away=point["away"],
                    line=point.get("line"),
                )
                for point in entry.get("movement", [])
            ]
            snapshots.append(
                MarketSnapshot(
                    game_id=entry["game_id"],
                    market=market,
                    line=entry.get("line"),
                    books=books,
                    movement=movement,
                )
            )
        return snapshots


def load_demo_bundle(path: str = "data/oddscope_demo.json") -> ProviderBundle:
    payload = json.loads(Path(path).read_text())
    return ProviderBundle(sports=DemoSportsProvider(payload), odds=DemoOddsProvider(payload))
