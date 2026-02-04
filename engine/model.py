from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from engine.odds import expected_value, implied_probability_from_american
from engine.scoring import ConfidenceScorer
from features.explanations import build_reasoning
from models.types import Game, MarketRecommendation, MarketSnapshot, MarketType, ModelOutput


class OutcomeModel:
    def __init__(self) -> None:
        self.scorer = ConfidenceScorer()

    def analyze_game(self, game: Game, snapshots: List[MarketSnapshot]) -> Dict[MarketType, MarketRecommendation]:
        recommendations: Dict[MarketType, MarketRecommendation] = {}
        for snapshot in snapshots:
            if snapshot.market == MarketType.MONEYLINE:
                rec = self._moneyline_recommendation(game, snapshot)
            elif snapshot.market == MarketType.SPREAD:
                rec = self._spread_recommendation(game, snapshot)
            else:
                rec = self._total_recommendation(game, snapshot)
            recommendations[snapshot.market] = rec
        return recommendations

    def _moneyline_recommendation(self, game: Game, snapshot: MarketSnapshot) -> MarketRecommendation:
        model_prob, model_output = self._model_probability(game, snapshot)
        best_book, best_odds = self._best_price(snapshot, side="home")
        implied_prob = implied_probability_from_american(best_odds)
        ev = expected_value(model_prob, best_odds)
        pick = f"{game.home_team} ML" if model_prob >= 0.5 else f"{game.away_team} ML"
        if model_prob < 0.5:
            best_book, best_odds = self._best_price(snapshot, side="away")
            implied_prob = implied_probability_from_american(best_odds)
            ev = expected_value(1 - model_prob, best_odds)
        return MarketRecommendation(
            market=MarketType.MONEYLINE,
            pick=pick,
            model_probability=round(max(model_prob, 1 - model_prob), 4),
            implied_probability=implied_prob,
            confidence=model_output.confidence,
            breakdown=model_output.breakdown,
            top_drivers=model_output.top_drivers,
            expected_value=ev,
            best_book=best_book,
            line=None,
            why=self._build_why(game, model_output),
            risk_flags=self._risk_flags(game),
        )

    def _spread_recommendation(self, game: Game, snapshot: MarketSnapshot) -> MarketRecommendation:
        predicted_margin = self._predicted_margin(game)
        line = snapshot.line or 0.0
        side = "home" if predicted_margin > line else "away"
        best_book, best_odds = self._best_price(snapshot, side=side)
        model_prob = 0.52 + min(abs(predicted_margin - line) / 10, 0.15)
        implied_prob = implied_probability_from_american(best_odds)
        ev = expected_value(model_prob, best_odds)
        pick = f"{game.home_team} {line:+}" if side == "home" else f"{game.away_team} {abs(line):+}"
        output = self._model_probability(game, snapshot)[1]
        return MarketRecommendation(
            market=MarketType.SPREAD,
            pick=pick,
            model_probability=round(model_prob, 4),
            implied_probability=implied_prob,
            confidence=output.confidence,
            breakdown=output.breakdown,
            top_drivers=output.top_drivers,
            expected_value=ev,
            best_book=best_book,
            line=line,
            why=self._build_why(game, output),
            risk_flags=self._risk_flags(game),
        )

    def _total_recommendation(self, game: Game, snapshot: MarketSnapshot) -> MarketRecommendation:
        projected_total = self._projected_total(game)
        line = snapshot.line or 0.0
        side = "over" if projected_total > line else "under"
        best_book, best_odds = self._best_price(snapshot, side="home")
        model_prob = 0.51 + min(abs(projected_total - line) / 15, 0.18)
        implied_prob = implied_probability_from_american(best_odds)
        ev = expected_value(model_prob, best_odds)
        pick = f"{side.title()} {line}" if line else f"{side.title()}"
        output = self._model_probability(game, snapshot)[1]
        return MarketRecommendation(
            market=MarketType.TOTAL,
            pick=pick,
            model_probability=round(model_prob, 4),
            implied_probability=implied_prob,
            confidence=output.confidence,
            breakdown=output.breakdown,
            top_drivers=output.top_drivers,
            expected_value=ev,
            best_book=best_book,
            line=line,
            why=self._build_why(game, output),
            risk_flags=self._risk_flags(game),
        )

    def _model_probability(self, game: Game, snapshot: MarketSnapshot) -> tuple[float, ModelOutput]:
        diff_strength = game.metrics_home.team_strength - game.metrics_away.team_strength
        diff_form = game.metrics_home.recent_form - game.metrics_away.recent_form
        diff_matchup = game.metrics_home.matchup_edge - game.metrics_away.matchup_edge
        diff_injury = game.metrics_home.injury_impact - game.metrics_away.injury_impact
        diff_rest = game.metrics_home.rest_travel - game.metrics_away.rest_travel
        market_signal = self._market_signal(snapshot)
        raw = 0.5 + diff_strength * 0.25 + diff_form * 0.2 + diff_matchup * 0.15
        raw += diff_injury * 0.1 + diff_rest * 0.05 + market_signal * 0.1
        model_prob = min(max(raw, 0.05), 0.95)
        confidence, breakdown, drivers = self.scorer.score(
            team_strength=abs(diff_strength),
            recent_form=abs(diff_form),
            matchup_edges=abs(diff_matchup),
            injuries=abs(diff_injury),
            rest_travel=abs(diff_rest),
            market_signal=abs(market_signal),
        )
        output = ModelOutput(
            probability=model_prob,
            confidence=confidence,
            breakdown=breakdown,
            top_drivers=drivers,
        )
        return model_prob, output

    def _market_signal(self, snapshot: MarketSnapshot) -> float:
        if not snapshot.movement:
            return 0.0
        opening = snapshot.movement[0].home
        latest = snapshot.movement[-1].home
        if opening == 0:
            return 0.0
        return min(max((opening - latest) / 200, -0.2), 0.2)

    def _predicted_margin(self, game: Game) -> float:
        base = (game.metrics_home.efficiency - game.metrics_away.efficiency) * 12
        pace_adj = (game.metrics_home.pace - game.metrics_away.pace) * 4
        return round(base + pace_adj, 2)

    def _projected_total(self, game: Game) -> float:
        pace = (game.metrics_home.pace + game.metrics_away.pace) / 2
        efficiency = (game.metrics_home.efficiency + game.metrics_away.efficiency) / 2
        return round(180 + pace * 30 + efficiency * 40, 2)

    def _best_price(self, snapshot: MarketSnapshot, side: str) -> tuple[str, float]:
        best_book = ""
        best_odds: Optional[float] = None
        for book in snapshot.books:
            odds = book.home if side in {"home", "over"} else book.away
            if best_odds is None or odds > best_odds:
                best_odds = odds
                best_book = book.book
        return best_book, best_odds or 0.0

    def _build_why(self, game: Game, output: ModelOutput) -> List[str]:
        return build_reasoning(game, output.top_drivers)

    def _risk_flags(self, game: Game) -> List[str]:
        flags = ["Informational analysis only. No guaranteed outcomes."]
        if "questionable" in game.context.injuries.lower():
            flags.append("Injury status could change closer to tip-off.")
        if "back-to-back" in game.context.schedule.lower():
            flags.append("Back-to-back scheduling adds volatility.")
        return flags


def timestamp_now() -> str:
    return datetime.utcnow().isoformat()
