from __future__ import annotations

from dataclasses import dataclass

from models.types import ConfidenceBreakdown


@dataclass
class ConfidenceConfig:
    trend_weight: float = 25.0
    momentum_weight: float = 20.0
    volatility_weight: float = 15.0
    volume_weight: float = 15.0
    structure_weight: float = 25.0


class ConfidenceModel:
    def __init__(self, config: ConfidenceConfig | None = None) -> None:
        self.config = config or ConfidenceConfig()

    def score(
        self,
        trend_alignment: float,
        momentum: float,
        volatility: float,
        volume: float,
        structure_quality: float,
    ) -> tuple[float, ConfidenceBreakdown]:
        trend_score = self._normalize(trend_alignment, self.config.trend_weight)
        momentum_score = self._normalize(momentum, self.config.momentum_weight)
        volatility_score = self._normalize(volatility, self.config.volatility_weight)
        volume_score = self._normalize(volume, self.config.volume_weight)
        structure_score = self._normalize(structure_quality, self.config.structure_weight)
        total = trend_score + momentum_score + volatility_score + volume_score + structure_score
        breakdown = ConfidenceBreakdown(
            trend_alignment=trend_score,
            momentum=momentum_score,
            volatility=volatility_score,
            volume=volume_score,
            structure_quality=structure_score,
        )
        return min(total, 100.0), breakdown

    def _normalize(self, value: float, weight: float) -> float:
        clamped = max(0.0, min(value, 1.0))
        return round(clamped * weight, 2)
