from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from data.api_base import MarketDataClient
from indicators.core import atr, detect_levels, ema, macd, rsi, vwap
from models.types import (
    AnalysisResult,
    ConfidenceBreakdown,
    IndicatorSnapshot,
    KeyLevels,
    MarketType,
    PriceBar,
    TradeIdea,
    TrendBias,
)
from scoring.confidence import ConfidenceModel


class MarketAnalyzer:
    def __init__(self, client: MarketDataClient) -> None:
        self.client = client
        self.scorer = ConfidenceModel()

    def analyze(self, symbol: str, market: MarketType, timeframe: str = "15m") -> AnalysisResult:
        bars = self.client.fetch_bars(symbol, market, timeframe, limit=200)
        closes = [bar.close for bar in bars]
        highs = [bar.high for bar in bars]
        lows = [bar.low for bar in bars]
        volumes = [bar.volume for bar in bars]

        ema_20 = ema(closes, 20)[-1]
        ema_50 = ema(closes, 50)[-1]
        ema_200 = ema(closes, 200)[-1]
        rsi_val = rsi(closes, 14)
        macd_val, macd_signal = macd(closes)
        atr_val = atr(highs, lows, closes)
        vwap_val = vwap(highs, lows, closes, volumes)
        supports, resistances = detect_levels(closes)

        bias = self._determine_bias(ema_20, ema_50, ema_200, rsi_val)
        trend_alignment = self._trend_alignment_score(ema_20, ema_50, ema_200)
        momentum_score = self._momentum_score(rsi_val, macd_val, macd_signal)
        volatility_score = self._volatility_score(atr_val, closes[-1])
        volume_score = self._volume_score(volumes)
        structure_score = self._structure_score(supports, resistances)

        confidence, breakdown = self.scorer.score(
            trend_alignment=trend_alignment,
            momentum=momentum_score,
            volatility=volatility_score,
            volume=volume_score,
            structure_quality=structure_score,
        )

        trend_summary = self._trend_summary(closes)
        trade_idea = self._trade_idea(bars, bias, atr_val)

        return AnalysisResult(
            symbol=symbol,
            market=market,
            bias=bias,
            confidence=confidence,
            confidence_breakdown=breakdown,
            key_levels=KeyLevels(support=supports, resistance=resistances),
            indicators=IndicatorSnapshot(
                rsi=rsi_val,
                macd=macd_val,
                macd_signal=macd_signal,
                ema_20=ema_20,
                ema_50=ema_50,
                ema_200=ema_200,
                atr=atr_val,
                vwap=vwap_val,
            ),
            trend_summary=trend_summary,
            momentum_notes=self._momentum_notes(rsi_val, macd_val, macd_signal),
            volatility_notes=self._volatility_notes(atr_val, closes[-1]),
            structure_notes=self._structure_notes(supports, resistances),
            risk_notes=self._risk_notes(market),
            trade_idea=trade_idea,
            updated_at=datetime.utcnow().isoformat(),
        )

    def _determine_bias(self, ema_20: float, ema_50: float, ema_200: float, rsi_val: float) -> TrendBias:
        if ema_20 > ema_50 > ema_200 and rsi_val > 55:
            return TrendBias.BULLISH
        if ema_20 < ema_50 < ema_200 and rsi_val < 45:
            return TrendBias.BEARISH
        return TrendBias.NEUTRAL

    def _trend_alignment_score(self, ema_20: float, ema_50: float, ema_200: float) -> float:
        if ema_20 > ema_50 > ema_200:
            return 1.0
        if ema_20 < ema_50 < ema_200:
            return 0.9
        return 0.5

    def _momentum_score(self, rsi_val: float, macd_val: float, macd_signal: float) -> float:
        score = 0.5
        if rsi_val > 60:
            score += 0.25
        if rsi_val < 40:
            score += 0.2
        if macd_val > macd_signal:
            score += 0.2
        return min(score, 1.0)

    def _volatility_score(self, atr_val: float, price: float) -> float:
        if price == 0:
            return 0.0
        ratio = atr_val / price
        if 0.002 <= ratio <= 0.03:
            return 1.0
        if 0.001 <= ratio <= 0.05:
            return 0.7
        return 0.4

    def _volume_score(self, volumes: List[float]) -> float:
        if not volumes:
            return 0.4
        recent = sum(volumes[-20:]) / 20
        older = sum(volumes[-60:-40]) / 20
        if recent > older * 1.2:
            return 1.0
        if recent > older:
            return 0.7
        return 0.5

    def _structure_score(self, supports: List[float], resistances: List[float]) -> float:
        if supports and resistances:
            return 0.9
        if supports or resistances:
            return 0.7
        return 0.4

    def _trend_summary(self, closes: List[float]) -> Dict[str, str]:
        return {
            "1m": self._simple_trend(closes, 15),
            "5m": self._simple_trend(closes, 30),
            "15m": self._simple_trend(closes, 60),
            "1h": self._simple_trend(closes, 90),
            "4h": self._simple_trend(closes, 120),
            "1d": self._simple_trend(closes, 180),
        }

    def _simple_trend(self, values: List[float], window: int) -> str:
        if len(values) < window:
            return "Sideways"
        if values[-1] > values[-window]:
            return "Up"
        if values[-1] < values[-window]:
            return "Down"
        return "Sideways"

    def _momentum_notes(self, rsi_val: float, macd_val: float, macd_signal: float) -> str:
        if rsi_val > 70:
            return "Momentum is strong with RSI over 70; watch for mean reversion risk."
        if rsi_val < 30:
            return "Momentum is oversold; monitor for basing or reversal signals."
        if macd_val > macd_signal:
            return "MACD is above signal line, supporting bullish momentum."
        return "Momentum is mixed; wait for clearer confirmation."

    def _volatility_notes(self, atr_val: float, price: float) -> str:
        if price == 0:
            return "Volatility data is unavailable."
        ratio = atr_val / price
        if ratio > 0.04:
            return "Volatility is elevated; widen stops and reduce size."
        if ratio < 0.01:
            return "Volatility is compressed; watch for breakout expansion."
        return "Volatility is moderate; suitable for directional setups."

    def _structure_notes(self, supports: List[float], resistances: List[float]) -> str:
        if supports and resistances:
            return "Structure shows clear support/resistance zones for planning entries."
        if supports:
            return "Support zones are visible; monitor for higher lows."
        if resistances:
            return "Resistance zones are visible; watch for breakout confirmation."
        return "Structure is less defined; use smaller position sizes."

    def _risk_notes(self, market: MarketType) -> List[str]:
        notes = ["Analysis is informational only. No guarantees of performance."]
        if market == MarketType.STOCKS:
            notes.append("Monitor earnings calendar and news risk for gaps.")
        if market == MarketType.CRYPTO:
            notes.append("Crypto spreads and funding rates can impact short-term moves.")
        if market == MarketType.FOREX:
            notes.append("Forex liquidity can vary across sessions; watch major data releases.")
        return notes

    def _trade_idea(self, bars: List[PriceBar], bias: TrendBias, atr_val: float) -> TradeIdea:
        last = bars[-1].close if bars else 0.0
        entry = f"{last:.2f} ± {atr_val * 0.3:.2f}"
        stop = f"{last - atr_val * 1.2:.2f}"
        take_profit = [
            f"{last + atr_val * 1.5:.2f} (1.5R)",
            f"{last + atr_val * 2.0:.2f} (2R)",
            f"{last + atr_val * 3.0:.2f} (3R)",
        ]
        invalidation = "Trend alignment breaks or price closes below support."
        position_hint = "Risk 1% per trade; size based on stop distance."
        if bias == TrendBias.BEARISH:
            stop = f"{last + atr_val * 1.2:.2f}"
            take_profit = [
                f"{last - atr_val * 1.5:.2f} (1.5R)",
                f"{last - atr_val * 2.0:.2f} (2R)",
                f"{last - atr_val * 3.0:.2f} (3R)",
            ]
        return TradeIdea(
            entry_zone=entry,
            stop_zone=stop,
            take_profit_targets=take_profit,
            invalidation=invalidation,
            position_size_hint=position_hint,
        )
