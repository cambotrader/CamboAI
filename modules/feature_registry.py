"""Central feature registry derived from SPEC_FEATURE_INDEX.md (machine-usable).

The registry allows runtime discovery of feature status & priority for UI toggles,
conditional loading, and progress tracking. Keep this file lightweight and pure-Python.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FeatureMeta:
    key: str
    name: str
    category: str
    status: str  # EXISTS | PARTIAL | PLANNED | MISSING
    priority: str  # P1 | P2 | P3
    module_path: str | None
    notes: str = ""


_FEATURES: List[FeatureMeta] = [
    FeatureMeta("chart_engine", "Multi-Source Chart Engine", "core", "PARTIAL", "P1", "modules/chart_module.py", "Needs provider toggles"),
    FeatureMeta("candlestick_lab", "Candlestick Pattern Lab", "analysis", "PARTIAL", "P1", "modules/pattern_engine.py", "Expand catalog & bias tags"),
    FeatureMeta("chart_pattern_recognizer", "Chart Pattern Recognizer", "analysis", "PARTIAL", "P1", "modules/chart_patterns.py", "Head & Shoulders implemented; add triangles next"),
    FeatureMeta("strategy_engine", "Strategy Engine & Screener", "strategy", "PARTIAL", "P1", "modules/strategy/strategy_engine.py", "MA crossover & RSI reversion live"),
    FeatureMeta("scanner_framework", "Universal Scanner", "analysis", "PARTIAL", "P1", "modules/scan/scanner.py", "Momentum & volume spike scanners"),
    FeatureMeta("trade_plan_generator", "Trade Plan Generator", "strategy", "PARTIAL", "P1", "modules/strategy/plan_generator.py", "Sizing + narrative; needs risk metrics"),
    FeatureMeta("sentiment_expanded", "Expanded Sentiment & News", "sentiment", "PARTIAL", "P1", "modules/news_sentiment.py", "Stub zones integrated"),
    FeatureMeta("finbert_zones", "FinBERT Sentiment Zones", "sentiment", "PARTIAL", "P1", "modules/sentiment/finbert.py", "Lexicon placeholder before model"),
]


def all_features() -> List[FeatureMeta]:
    return list(_FEATURES)


def feature_map() -> Dict[str, FeatureMeta]:
    return {f.key: f for f in _FEATURES}


def by_status(status: str) -> List[FeatureMeta]:
    return [f for f in _FEATURES if f.status == status]


def upgrade_status(key: str, new_status: str):
    m = feature_map().get(key)
    if m:
        m.status = new_status


__all__ = ["FeatureMeta", "all_features", "feature_map", "by_status", "upgrade_status"]
