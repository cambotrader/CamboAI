"""
AI Engine Switcher: chooses best available analysis pipeline with safe fallbacks.

Usage example:
    df = ...  # OHLC DataFrame
    sentiment = 0.1  # -1..1
    result = get_signal(df, sentiment)
"""
from __future__ import annotations

from typing import Dict, Any, Callable

import pandas as pd

from . import pattern_engine
from . import fusion_engine


def _pattern_only(df: pd.DataFrame) -> Dict[str, Any]:
    patt = pattern_engine.analyze(df)
    # sentiment-neutral fusion
    fused = fusion_engine.fuse(patt["signals"], 0.0)
    fused["detail"]["fallback"] = "pattern_only"
    return fused


def get_signal(df: pd.DataFrame, sentiment_score: float | None = None, timeout_sec: float = 2.0) -> Dict[str, Any]:
    """Route to best available engine and fall back on error.

    - If sentiment is provided, use fusion of patterns + sentiment.
    - If sentiment is None or errors occur, fall back to pattern-only.
    """
    try:
        patt = pattern_engine.analyze(df)
        s = float(sentiment_score) if sentiment_score is not None else 0.0
        fused = fusion_engine.fuse(patt["signals"], s)
        fused["detail"]["engine"] = "fusion"
        return fused
    except Exception as e:
        fb = _pattern_only(df)
        fb["detail"]["engine_error"] = str(e)
        return fb