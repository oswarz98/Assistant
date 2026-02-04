from __future__ import annotations

from typing import List

from models.types import League, MarketType, ScannerFilters, ScannerResult
from services.analyzer import OddsAnalyzer


class OddsScanner:
    def __init__(self, analyzer: OddsAnalyzer) -> None:
        self.analyzer = analyzer

    def scan(self, filters: ScannerFilters) -> List[ScannerResult]:
        leagues = [filters.league] if filters.league else [League.NBA, League.NHL]
        results: List[ScannerResult] = []
        for league in leagues:
            analyses = self.analyzer.analyze_league(league)
            for analysis in analyses:
                for market, recommendation in analysis.recommendations.items():
                    if filters.market and filters.market != market:
                        continue
                    edge = (recommendation.model_probability - recommendation.implied_probability) * 100
                    if recommendation.confidence < filters.min_confidence:
                        continue
                    if edge < filters.min_edge:
                        continue
                    if filters.books and recommendation.best_book not in filters.books:
                        continue
                    results.append(
                        ScannerResult(
                            game_id=analysis.game.id,
                            matchup=f"{analysis.game.away_team} @ {analysis.game.home_team}",
                            league=analysis.game.league,
                            market=market,
                            pick=recommendation.pick,
                            confidence=recommendation.confidence,
                            edge=round(edge, 2),
                            summary="; ".join(recommendation.why[:2]),
                            best_book=recommendation.best_book,
                            start_time=analysis.game.start_time,
                        )
                    )
        return sorted(results, key=lambda item: item.confidence, reverse=True)

    def top_confident(self, count: int = 5) -> List[ScannerResult]:
        filters = ScannerFilters(min_confidence=65.0)
        return self.scan(filters)[:count]

    def top_value(self, count: int = 5) -> List[ScannerResult]:
        filters = ScannerFilters(min_confidence=50.0, min_edge=2.0)
        return sorted(self.scan(filters), key=lambda item: item.edge, reverse=True)[:count]
