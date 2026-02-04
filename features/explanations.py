from __future__ import annotations

from typing import List

from models.types import Game


def build_reasoning(game: Game, top_drivers: List[str]) -> List[str]:
    reasons = [
        game.context.injuries,
        game.context.form,
        game.context.matchup,
        game.context.schedule,
        game.context.market_movement,
    ]
    reasons.append(f"Top drivers: {', '.join(top_drivers)}.")
    if game.context.weather:
        reasons.append(f"Weather impact: {game.context.weather}")
    return reasons
