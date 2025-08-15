from __future__ import annotations
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd

# Simple rule-based chart pattern detectors. These are heuristic starters and can be
# improved with more robust swing/line-fitting logic and volume confirmation.

@dataclass
class ChartDetection:
    id: str
    name: str
    confidence: float
    start: str
    end: str
    extra: Dict[str, Any]


def _pivots(series: np.ndarray, left: int = 3, right: int = 3) -> Tuple[List[int], List[int]]:
    """Return indices of local minima and maxima using a simple window check."""
    lows, highs = [], []
    n = len(series)
    for i in range(left, n - right):
        win = series[i - left:i + right + 1]
        if series[i] == win.min():
            lows.append(i)
        if series[i] == win.max():
            highs.append(i)
    return lows, highs


def _double_top(close: np.ndarray, idx_highs: List[int], tol: float = 0.01) -> List[Tuple[int, int]]:
    pairs = []
    for i in range(len(idx_highs) - 1):
        a, b = idx_highs[i], idx_highs[i + 1]
        pa, pb = close[a], close[b]
        if abs(pa - pb) / max(pa, pb) <= tol:
            pairs.append((a, b))
    return pairs


def _double_bottom(close: np.ndarray, idx_lows: List[int], tol: float = 0.01) -> List[Tuple[int, int]]:
    pairs = []
    for i in range(len(idx_lows) - 1):
        a, b = idx_lows[i], idx_lows[i + 1]
        pa, pb = close[a], close[b]
        if abs(pa - pb) / max(pa, pb) <= tol:
            pairs.append((a, b))
    return pairs


def _fit_trend(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    # returns slope, intercept using least squares
    if len(x) < 2:
        return 0.0, float(y[-1]) if len(y) else 0.0
    A = np.vstack([x, np.ones(len(x))]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(slope), float(intercept)


def detect(df: pd.DataFrame) -> List[ChartDetection]:
    """Detect a few common chart patterns with simple heuristics."""
    if df.empty:
        return []
    # Prepare
    close = df["close"].values.astype(float)
    highs = df["high"].values.astype(float)
    lows = df["low"].values.astype(float)
    ts_col = "Date" if "Date" in df.columns else ("Datetime" if "Datetime" in df.columns else df.columns[0])

    idx_lows, idx_highs = _pivots(close, left=3, right=3)

    detections: List[ChartDetection] = []

    # Double Top / Bottom
    for a, b in _double_top(close, idx_highs, tol=0.015):
        start = str(df.iloc[a][ts_col])
        end = str(df.iloc[b][ts_col])
        span = b - a
        conf = max(0.5, min(1.0, 0.6 + (20 - abs(span - 10)) / 50))  # rough shape preference
        detections.append(ChartDetection(
            id=f"chart-double-top-{a}-{b}",
            name="Double Top",
            confidence=round(conf, 2),
            start=start,
            end=end,
            extra={"a": int(a), "b": int(b), "peak1": float(close[a]), "peak2": float(close[b])}
        ))

    for a, b in _double_bottom(close, idx_lows, tol=0.015):
        start = str(df.iloc[a][ts_col])
        end = str(df.iloc[b][ts_col])
        span = b - a
        conf = max(0.5, min(1.0, 0.6 + (20 - abs(span - 10)) / 50))
        detections.append(ChartDetection(
            id=f"chart-double-bottom-{a}-{b}",
            name="Double Bottom",
            confidence=round(conf, 2),
            start=start,
            end=end,
            extra={"a": int(a), "b": int(b), "low1": float(close[a]), "low2": float(close[b])}
        ))

    # Triangle (sym): fit lines to recent highs and lows
    lookback = 80 if len(close) > 80 else len(close)
    if lookback >= 20:
        xs = np.arange(lookback)
        hi_seg = highs[-lookback:]
        lo_seg = lows[-lookback:]
        up_slope, up_inter = _fit_trend(xs, hi_seg)
        lo_slope, lo_inter = _fit_trend(xs, lo_seg)
        # Converging if up_slope < 0 and lo_slope > 0 and gap narrows
        if up_slope < 0 and lo_slope > 0:
            start = str(df.iloc[-lookback][ts_col])
            end = str(df.iloc[-1][ts_col])
            # Narrowing ratio
            gap_start = (up_inter + up_slope * 0) - (lo_inter + lo_slope * 0)
            gap_end = (up_inter + up_slope * (lookback - 1)) - (lo_inter + lo_slope * (lookback - 1))
            if gap_start > 0:
                ratio = max(0.0, min(1.0, 1.0 - gap_end / gap_start))
                conf = 0.6 + 0.4 * ratio
                detections.append(ChartDetection(
                    id=f"chart-triangle-sym-{len(detections)}",
                    name="Symmetrical Triangle",
                    confidence=round(float(conf), 2),
                    start=start,
                    end=end,
                    extra={"up_slope": round(up_slope, 6), "lo_slope": round(lo_slope, 6), "n": lookback}
                ))

    return detections