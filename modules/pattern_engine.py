"""
Pattern Engine: Detects a broad (but heuristic) set of candlestick patterns on OHLCV data.
- Inputs: pandas.DataFrame with columns [open, high, low, close] (case-insensitive accepted)
- Outputs: list of detected patterns with confidences emphasizing recency.

Coverage (heuristic implementations):
  Core: doji, hammer, shooting_star, bullish_engulfing, bearish_engulfing,
      golden_cross, death_cross, rsi_oversold, rsi_overbought
  Extended: morning_star, evening_star, dark_cloud_cover, piercing_line,
        three_white_soldiers, three_black_crows, spinning_top, marubozu,
        tweezer_top, tweezer_bottom, harami_bullish, harami_bearish

Notes / Limitations:
- All logic uses simple proportional thresholds (no trend filters except basic body direction context).
- Gaps are approximated (many crypto symbols have 24h trading; gap criteria relaxed).
- Use as educational scaffolding; for production-grade detection incorporate volatility normalization & trend context.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

import numpy as np
import pandas as pd


CLOSE_COLS = {"close", "Close", "CLOSE"}
OPEN_COLS = {"open", "Open", "OPEN"}
HIGH_COLS = {"high", "High", "HIGH"}
LOW_COLS = {"low", "Low", "LOW"}


@dataclass
class PatternSignal:
    type: str
    direction: str | None  # "bullish" | "bearish" | None
    confidence: float      # 0..1
    meta: Dict[str, Any]


def _col(df: pd.DataFrame, candidates: set[str]) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"Required columns missing. Looking for one of: {sorted(list(candidates))}")


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    # Simple RSI implementation
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(method="bfill").fillna(50)


def enrich(df: pd.DataFrame, ma_fast: int = 20, ma_slow: int = 50) -> pd.DataFrame:
    oc = _col(df, OPEN_COLS)
    cc = _col(df, CLOSE_COLS)
    hc = _col(df, HIGH_COLS)
    lc = _col(df, LOW_COLS)

    out = df.copy()
    out["body"] = (out[cc] - out[oc]).abs()
    out["range"] = (out[hc] - out[lc]).replace(0, np.nan)
    out["upper_shadow"] = out[hc] - out[[oc, cc]].max(axis=1)
    out["lower_shadow"] = out[[oc, cc]].min(axis=1) - out[lc]
    out["ma_fast"] = out[cc].rolling(ma_fast, min_periods=1).mean()
    out["ma_slow"] = out[cc].rolling(ma_slow, min_periods=1).mean()
    out["rsi"] = _rsi(out[cc])
    return out


def _last_two(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) < 2:
        raise ValueError("Need at least 2 rows for pattern detection")
    return df.iloc[-2:].copy()


def detect(df: pd.DataFrame) -> List[PatternSignal]:
    """Detect patterns on the last candle using previous candle for context."""
    oc = _col(df, OPEN_COLS)
    cc = _col(df, CLOSE_COLS)
    hc = _col(df, HIGH_COLS)
    lc = _col(df, LOW_COLS)

    x = enrich(df)
    last2 = _last_two(x)
    prev, curr = last2.iloc[0], last2.iloc[1]

    signals: List[PatternSignal] = []

    # Helpers
    def pct(x: float, y: float) -> float:
        if y == 0:
            return 0.0
        return float(x) / float(y)

    # ---------- 1-Candle & 2-Candle Patterns ----------
    # Doji (small body relative to range)
    if pct(curr["body"], curr["range"]) <= 0.1:
        signals.append(PatternSignal("doji", None, 0.4, {"ratio": pct(curr["body"], curr["range"])}))

    # Hammer (long lower shadow, small upper shadow)
    if pct(curr["lower_shadow"], curr["body"]) >= 2 and pct(curr["upper_shadow"], curr["body"]) <= 0.25:
        signals.append(PatternSignal("hammer", "bullish", 0.6, {
            "lower_to_body": pct(curr["lower_shadow"], curr["body"]),
        }))

    # Shooting star (long upper shadow)
    if pct(curr["upper_shadow"], curr["body"]) >= 2 and pct(curr["lower_shadow"], curr["body"]) <= 0.25:
        signals.append(PatternSignal("shooting_star", "bearish", 0.6, {
            "upper_to_body": pct(curr["upper_shadow"], curr["body"]),
        }))

    # Engulfing
    prev_bear = prev[cc] < prev[oc]
    prev_bull = prev[cc] > prev[oc]
    curr_bear = curr[cc] < curr[oc]
    curr_bull = curr[cc] > curr[oc]
    prev_body = abs(prev[cc] - prev[oc])
    curr_body = abs(curr[cc] - curr[oc])

    if curr_bull and prev_bear and curr_body > prev_body and curr[oc] <= prev[cc] and curr[cc] >= prev[oc]:
        signals.append(PatternSignal("bullish_engulfing", "bullish", 0.65, {"body_ratio": pct(curr_body, prev_body)}))
    if curr_bear and prev_bull and curr_body > prev_body and curr[oc] >= prev[cc] and curr[cc] <= prev[oc]:
        signals.append(PatternSignal("bearish_engulfing", "bearish", 0.65, {"body_ratio": pct(curr_body, prev_body)}))

    # Moving average cross
    prev_fast, prev_slow = float(prev["ma_fast"]), float(prev["ma_slow"])
    curr_fast, curr_slow = float(curr["ma_fast"]), float(curr["ma_slow"])
    if prev_fast <= prev_slow and curr_fast > curr_slow:
        signals.append(PatternSignal("golden_cross", "bullish", 0.7, {}))
    if prev_fast >= prev_slow and curr_fast < curr_slow:
        signals.append(PatternSignal("death_cross", "bearish", 0.7, {}))

    # RSI zones
    if float(curr["rsi"]) < 30:
        signals.append(PatternSignal("rsi_oversold", "bullish", 0.5, {"rsi": float(curr["rsi"]) }))
    if float(curr["rsi"]) > 70:
        signals.append(PatternSignal("rsi_overbought", "bearish", 0.5, {"rsi": float(curr["rsi"]) }))

    # ---------- Multi-Candle Extensions ----------
    last3 = x.iloc[-3:] if len(x) >= 3 else None
    last4 = x.iloc[-4:] if len(x) >= 4 else None

    if last3 is not None and len(last3) == 3:
        c1, c2, c3 = last3.iloc[0], last3.iloc[1], last3.iloc[2]
        body1 = abs(c1[cc] - c1[oc])
        body2 = abs(c2[cc] - c2[oc])
        body3 = abs(c3[cc] - c3[oc])
        range1 = (c1[hc] - c1[lc]) or 1
        range3 = (c3[hc] - c3[lc]) or 1

        # Morning Star: bearish large body, small body (any), bullish close into >= 50% of first body
        if c1[cc] < c1[oc] and body1 / range1 > 0.5 and body2 < body1 * 0.6 and c3[cc] > c3[oc] and (c3[cc] - c1[cc]) >= 0.5 * (c1[oc] - c1[cc]):
            signals.append(PatternSignal("morning_star", "bullish", 0.6, {}))
        # Evening Star inverse
        if c1[cc] > c1[oc] and body1 / range1 > 0.5 and body2 < body1 * 0.6 and c3[cc] < c3[oc] and (c1[cc] - c3[cc]) >= 0.5 * (c1[cc] - c1[oc]):
            signals.append(PatternSignal("evening_star", "bearish", 0.6, {}))

        # Three White Soldiers / Three Black Crows
        if all(last3.iloc[i][cc] > last3.iloc[i][oc] for i in range(3)) and all(abs(last3.iloc[i][cc] - last3.iloc[i][oc]) > (last3.iloc[i][hc] - last3.iloc[i][lc]) * 0.5 for i in range(3)):
            signals.append(PatternSignal("three_white_soldiers", "bullish", 0.65, {}))
        if all(last3.iloc[i][cc] < last3.iloc[i][oc] for i in range(3)) and all(abs(last3.iloc[i][cc] - last3.iloc[i][oc]) > (last3.iloc[i][hc] - last3.iloc[i][lc]) * 0.5 for i in range(3)):
            signals.append(PatternSignal("three_black_crows", "bearish", 0.65, {}))

    if last4 is not None and len(last4) == 4:
        # Tweezer top/bottom look at last two highs/lows equality within tolerance
        l1, l2 = last4.iloc[-2], last4.iloc[-1]
        tol = 0.002  # 0.2%
        if abs(l1[hc] - l2[hc]) / max(1e-9, (l1[hc] + l2[hc]) / 2) < tol and l2[cc] < l2[oc] and l1[cc] > l1[oc]:
            signals.append(PatternSignal("tweezer_top", "bearish", 0.55, {}))
        if abs(l1[lc] - l2[lc]) / max(1e-9, (l1[lc] + l2[lc]) / 2) < tol and l2[cc] > l2[oc] and l1[cc] < l1[oc]:
            signals.append(PatternSignal("tweezer_bottom", "bullish", 0.55, {}))

    # Dark Cloud Cover / Piercing Line use last2 context (already have prev, curr)
    if prev_bull and curr_bear:
        midpoint_prev = prev[oc] + (prev[cc] - prev[oc]) / 2
        if curr[oc] >= prev[cc] and curr[cc] < midpoint_prev and curr[cc] > prev[oc]:
            signals.append(PatternSignal("dark_cloud_cover", "bearish", 0.6, {}))
    if prev_bear and curr_bull:
        midpoint_prev = prev[cc] + (prev[oc] - prev[cc]) / 2
        if curr[oc] <= prev[cc] and curr[cc] > midpoint_prev and curr[cc] < prev[oc]:
            signals.append(PatternSignal("piercing_line", "bullish", 0.6, {}))

    # Spinning top (not already doji): moderate body, relatively long shadows
    if 0.1 < pct(curr["body"], curr["range"]) < 0.4 and pct(curr["upper_shadow"] + curr["lower_shadow"], curr["range"]) > 0.5:
        signals.append(PatternSignal("spinning_top", None, 0.35, {}))

    # Marubozu (full body, tiny shadows)
    if pct(curr["body"], curr["range"]) > 0.9 and pct(curr["upper_shadow"] + curr["lower_shadow"], curr["range"]) < 0.1:
        direction = "bullish" if curr[cc] > curr[oc] else "bearish"
        signals.append(PatternSignal("marubozu", direction, 0.5, {}))

    # Harami patterns
    if prev_body > 0 and curr_body < prev_body * 0.6 and min(curr[oc], curr[cc]) > min(prev[oc], prev[cc]) and max(curr[oc], curr[cc]) < max(prev[oc], prev[cc]):
        if prev_bear and curr_bull:
            signals.append(PatternSignal("harami_bullish", "bullish", 0.55, {}))
        if prev_bull and curr_bear:
            signals.append(PatternSignal("harami_bearish", "bearish", 0.55, {}))

    return signals


def analyze(df: pd.DataFrame) -> Dict[str, Any]:
    """High-level convenience function returning patterns for last bar."""
    if not isinstance(df, pd.DataFrame) or len(df) < 2:
        raise ValueError("DataFrame with at least 2 rows required")
    signals = detect(df)
    return {
        "count": len(signals),
        "signals": [s.__dict__ for s in signals],
    }