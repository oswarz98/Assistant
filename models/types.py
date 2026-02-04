from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class MarketType(str, Enum):
    STOCKS = "stocks"
    CRYPTO = "crypto"
    FOREX = "forex"


class TrendBias(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


@dataclass
class PriceBar:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class IndicatorSnapshot:
    rsi: float
    macd: float
    macd_signal: float
    ema_20: float
    ema_50: float
    ema_200: float
    atr: float
    vwap: Optional[float] = None


@dataclass
class KeyLevels:
    support: List[float] = field(default_factory=list)
    resistance: List[float] = field(default_factory=list)


@dataclass
class TradeIdea:
    entry_zone: str
    stop_zone: str
    take_profit_targets: List[str]
    invalidation: str
    position_size_hint: str


@dataclass
class ConfidenceBreakdown:
    trend_alignment: float
    momentum: float
    volatility: float
    volume: float
    structure_quality: float


@dataclass
class AnalysisResult:
    symbol: str
    market: MarketType
    bias: TrendBias
    confidence: float
    confidence_breakdown: ConfidenceBreakdown
    key_levels: KeyLevels
    indicators: IndicatorSnapshot
    trend_summary: Dict[str, str]
    momentum_notes: str
    volatility_notes: str
    structure_notes: str
    risk_notes: List[str]
    trade_idea: TradeIdea
    updated_at: str


@dataclass
class ScannerFilters:
    market: Optional[MarketType] = None
    min_confidence: float = 60.0
    min_volume: float = 0.0
    volatility_band: Optional[str] = None
    timeframe: str = "15m"


@dataclass
class ScannerResult:
    symbol: str
    market: MarketType
    confidence: float
    expected_r: float
    setup_quality: float
    summary: str
