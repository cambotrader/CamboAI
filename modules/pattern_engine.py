"""
Pattern Engine: Detects basic candlestick and technical patterns on OHLCV data.
- Inputs: pandas.DataFrame with columns [open, high, low, close] (case-insensitive accepted)
- Outputs: list of detected patterns on the latest candle with confidences

Notes:
- This is intentionally simple and fast for realtime and educational use.
- Do not treat as financial advice. Tune thresholds per instrument/timeframe.
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