from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from models.types import BreakdownScore


@dataclass
class ScoringWeights:
    team_strength: float = 25.0
    recent_form: float = 15.0
    matchup_edges: float = 20.0
    injuries: float = 15.0
    rest_travel: float = 10.0
    market_signal: float = 15.0


class ConfidenceScorer:
    def __init__(self, weights: ScoringWeights | None = None) -> None:
        self.weights = weights or ScoringWeights()

    def score(
        self,
        team_strength: float,
        recent_form: float,
        matchup_edges: float,
        injuries: float,
        rest_travel: float,
        market_signal: float,
    ) -> Tuple[float, BreakdownScore, List[str]]:
        breakdown = BreakdownScore(
            team_strength=self._normalize(team_strength, self.weights.team_strength),
            recent_form=self._normalize(recent_form, self.weights.recent_form),
            matchup_edges=self._normalize(matchup_edges, self.weights.matchup_edges),
            injuries=self._normalize(injuries, self.weights.injuries),
            rest_travel=self._normalize(rest_travel, self.weights.rest_travel),
            market_signal=self._normalize(market_signal, self.weights.market_signal),
        )
        total = sum(
            [
                breakdown.team_strength,
                breakdown.recent_form,
                breakdown.matchup_edges,
                breakdown.injuries,
                breakdown.rest_travel,
                breakdown.market_signal,
            ]
        )
        drivers = self._top_drivers(breakdown)
        return min(total, 100.0), breakdown, drivers

    def _normalize(self, value: float, weight: float) -> float:
        clamped = max(0.0, min(value, 1.0))
        return round(clamped * weight, 2)

    def _top_drivers(self, breakdown: BreakdownScore) -> List[str]:
        score_map = {
            "Team strength differential": breakdown.team_strength,
            "Recent form & consistency": breakdown.recent_form,
            "Matchup edges": breakdown.matchup_edges,
            "Injuries/lineup impact": breakdown.injuries,
            "Schedule/rest/travel": breakdown.rest_travel,
            "Market movement/price efficiency": breakdown.market_signal,
        }
        return [
            name
            for name, _ in sorted(score_map.items(), key=lambda item: item[1], reverse=True)[:3]
        ]
