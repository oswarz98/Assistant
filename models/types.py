from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class League(str, Enum):
    NBA = "NBA"
    NHL = "NHL"


class MarketType(str, Enum):
    MONEYLINE = "Moneyline"
    SPREAD = "Spread"
    TOTAL = "Total"


class OddsFormat(str, Enum):
    AMERICAN = "American"
    DECIMAL = "Decimal"
    FRACTIONAL = "Fractional"


@dataclass
class TeamMetrics:
    team_strength: float
    recent_form: float
    matchup_edge: float
    injury_impact: float
    rest_travel: float
    pace: float
    efficiency: float


@dataclass
class GameContext:
    injuries: str
    form: str
    matchup: str
    schedule: str
    market_movement: str
    weather: Optional[str] = None


@dataclass
class Game:
    id: str
    league: League
    start_time: str
    home_team: str
    away_team: str
    venue: str
    metrics_home: TeamMetrics
    metrics_away: TeamMetrics
    context: GameContext


@dataclass
class OddsMovementPoint:
    timestamp: str
    home: float
    away: float
    line: Optional[float] = None


@dataclass
class MarketOdds:
    book: str
    home: float
    away: float
    line: Optional[float]
    updated_at: str


@dataclass
class MarketSnapshot:
    game_id: str
    market: MarketType
    line: Optional[float]
    books: List[MarketOdds]
    movement: List[OddsMovementPoint] = field(default_factory=list)


@dataclass
class BreakdownScore:
    team_strength: float
    recent_form: float
    matchup_edges: float
    injuries: float
    rest_travel: float
    market_signal: float


@dataclass
class ModelOutput:
    probability: float
    confidence: float
    breakdown: BreakdownScore
    top_drivers: List[str]


@dataclass
class MarketRecommendation:
    market: MarketType
    pick: str
    model_probability: float
    implied_probability: float
    confidence: float
    breakdown: BreakdownScore
    top_drivers: List[str]
    expected_value: float
    best_book: str
    line: Optional[float]
    why: List[str]
    risk_flags: List[str]


@dataclass
class GameAnalysis:
    game: Game
    recommendations: Dict[MarketType, MarketRecommendation]
    updated_at: str


@dataclass
class ScannerFilters:
    league: Optional[League] = None
    market: Optional[MarketType] = None
    min_confidence: float = 60.0
    min_edge: float = 0.0
    books: List[str] = field(default_factory=list)


@dataclass
class ScannerResult:
    game_id: str
    matchup: str
    league: League
    market: MarketType
    pick: str
    confidence: float
    edge: float
    summary: str
    best_book: str
    start_time: str
