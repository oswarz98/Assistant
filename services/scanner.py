from __future__ import annotations

from typing import List

from data.api_base import MarketDataClient
from models.types import MarketType, ScannerFilters, ScannerResult
from services.analyzer import MarketAnalyzer


class MarketScanner:
    def __init__(self, client: MarketDataClient) -> None:
        self.client = client
        self.analyzer = MarketAnalyzer(client)

    def scan(self, filters: ScannerFilters) -> List[ScannerResult]:
        results: List[ScannerResult] = []
        markets = [filters.market] if filters.market else self.client.supported_markets()
        for market in markets:
            symbols = self.client.list_symbols(market)
            for symbol in symbols:
                analysis = self.analyzer.analyze(symbol, market, timeframe=filters.timeframe)
                if analysis.confidence < filters.min_confidence:
                    continue
                expected_r = round(1.5 + (analysis.confidence / 100) * 1.5, 2)
                setup_quality = round((analysis.confidence / 100) * 10, 2)
                summary = f"{analysis.bias.value} bias with {analysis.confidence:.0f}% confidence."
                results.append(
                    ScannerResult(
                        symbol=symbol,
                        market=market,
                        confidence=analysis.confidence,
                        expected_r=expected_r,
                        setup_quality=setup_quality,
                        summary=summary,
                    )
                )
        return sorted(results, key=lambda item: item.confidence, reverse=True)
