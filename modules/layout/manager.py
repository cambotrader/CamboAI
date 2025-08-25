"""Layout Manager (MVP)

Provides a registry of panels with default visibility and category.
Streamlit UI can reference this to build dynamic toggles and future persistence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Panel:
    key: str
    label: str
    category: str
    default: bool = True
    description: str = ""


_PANELS: Dict[str, Panel] = {
    "chart_plotly": Panel("chart_plotly", "Plotly Chart", "chart", True),
    "chart_tradingview": Panel("chart_tradingview", "TradingView Embed", "chart", False),
    "patterns_candles": Panel("patterns_candles", "Candlestick Patterns", "analysis", True),
    "patterns_advanced": Panel("patterns_advanced", "Advanced Chart Patterns", "analysis", True),
    "signals_strategy": Panel("signals_strategy", "Strategy Engine", "signals", True),
    "signals_scanner": Panel("signals_scanner", "Scanner Findings", "signals", True),
    "signals_tradeplan": Panel("signals_tradeplan", "Trade Plan", "signals", True),
    "sentiment_panel": Panel("sentiment_panel", "Sentiment Panel", "sentiment", True),
}


def all_panels() -> List[Panel]:
    return list(_PANELS.values())


def get_panel(key: str) -> Panel | None:
    return _PANELS.get(key)


__all__ = ["Panel", "all_panels", "get_panel"]
