"""Advanced Chart Pattern Recognizer (stub)

Future implementation roadmap:
- Head & Shoulders via pivot point sequence validation
- Triangles by converging trendline slope comparison
- Flags/Wedges using recent consolidation range + pole length ratio

Current MVP returns empty list to integrate interface early.
"""
from __future__ import annotations

from typing import List
from modules.models import PatternDetection
import pandas as pd


def _pivots(close: pd.Series, left: int = 2, right: int = 2):
    pivots = []  # (index, price, type)
    for i in range(left, len(close) - right):
        window = close[i - left:i + right + 1]
        c = close.iloc[i]
        if c == window.max() and (c > window.head(left).max()) and (c >= window.tail(right + 1)[1:].max()):
            pivots.append((close.index[i], c, 'H'))
        if c == window.min() and (c < window.head(left).min()) and (c <= window.tail(right + 1)[1:].min()):
            pivots.append((close.index[i], c, 'L'))
    return pivots


def _detect_head_and_shoulders(close: pd.Series) -> List[dict]:
    piv = _pivots(close)
    # Extract recent sequence of highs
    highs = [p for p in piv if p[2] == 'H'][-7:]  # limit search window
    patterns = []
    if len(highs) < 3:
        return patterns
    # Naive scan: iterate triples
    for i in range(len(highs) - 2):
        ls, head, rs = highs[i], highs[i + 1], highs[i + 2]
        ls_h, head_h, rs_h = ls[1], head[1], rs[1]
        # Head should be highest
        if not (head_h > ls_h and head_h > rs_h):
            continue
        # Shoulders roughly similar height (within 8%)
        if ls_h == 0 or rs_h == 0:
            continue
        rel_diff = abs(ls_h - rs_h) / ((ls_h + rs_h) / 2)
        if rel_diff > 0.08:
            continue
        # Time spacing constraint (avoid clustering too close)
        if (head[0] - ls[0]).days < 1 or (rs[0] - head[0]).days < 1:
            continue
        patterns.append({
            'type': 'head_and_shoulders',
            'left_shoulder': ls[0],
            'head': head[0],
            'right_shoulder': rs[0],
            'confidence': 0.55,
        })
    return patterns


def detect_advanced(symbol: str, df) -> List[PatternDetection]:  # noqa: ANN001
    detections: List[PatternDetection] = []
    if df is None or len(df) < 50:
        return detections
    if 'Close' not in df.columns:
        return detections
    close = df['Close'] if isinstance(df, pd.DataFrame) else df
    try:
        hs_patterns = _detect_head_and_shoulders(close)
        for p in hs_patterns:
            detections.append(PatternDetection(pattern_type=p['type'], direction='bearish', confidence=p['confidence'], symbol=symbol, meta={
                'left_shoulder': str(p['left_shoulder']),
                'head': str(p['head']),
                'right_shoulder': str(p['right_shoulder']),
            }))
    except (KeyError, ValueError, TypeError):  # fail soft on data shape issues
        return detections
    return detections


__all__ = ["detect_advanced"]
