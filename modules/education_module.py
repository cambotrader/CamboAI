# education_module.py - CamboAI TraderStation Education Hub
# Consolidated helpers: glossary, tutorials, tips, and simple voice routing.
from __future__ import annotations
from typing import Dict, List

# Pattern glossary (selected examples)
PATTERN_GLOSSARY: Dict[str, str] = {
    "Hammer": "Bullish reversal candlestick with long lower shadow.",
    "Doji": "Indecision candle; potential turning point depending on context.",
    "Bullish Engulfing": "Larger green body engulfs prior red body; reversal potential.",
    "Bearish Engulfing": "Larger red body engulfs prior green; reversal potential.",
    "Morning Star": "Three-candle bullish reversal sequence.",
    "Evening Star": "Three-candle bearish reversal sequence.",
    "Head and Shoulders": "Bearish reversal chart pattern.",
    "Inverse H&S": "Bullish reversal chart pattern.",
    "Double Top": "Bearish reversal after two failed highs.",
    "Double Bottom": "Bullish reversal after two failed lows.",
    "Rising Wedge": "Bearish-leaning compression channel.",
    "Falling Wedge": "Bullish-leaning compression channel.",
    # Future enrichment: harmonic patterns, volume profile concepts.
}

# Tutorial content (sample curriculum outline)
TUTORIALS: List[Dict[str, str]] = [
    {"title": "Welcome", "level": "Beginner", "content": "Welcome to the CamboAI TraderStation Education Center."},
    {"title": "Candlestick Patterns", "level": "Beginner", "content": "Identify Doji, Hammer, Engulfing, Morning/Evening Star."},
    {"title": "Chart Structures", "level": "Intermediate", "content": "Head & Shoulders, Triangles, Wedges, Double/Triple setups."},
    {"title": "Sentiment Zones", "level": "Intermediate", "content": "Use FinBERT/heuristics to contextualize price action."},
    {"title": "Strategy Composition", "level": "Advanced", "content": "Combine structure + sentiment + risk into a trade plan."},
    # ISSUE: quizzes/flashcards enrichment planned (track in issue tracker)
]

TIP_MAP: Dict[str, str] = {
    "candlestick": "Focus on body vs. wick proportions; context at MAs and key levels.",
    "chart": "Confirm pattern with volume and retests; watch breakouts/throwbacks.",
    "sentiment": "Zone sentiment around catalysts to anticipate volatility shifts.",
}


def pattern_glossary() -> Dict[str, str]:
    return PATTERN_GLOSSARY


def tutorial_content() -> List[Dict[str, str]]:
    return TUTORIALS


def get_learning_tip(topic: str) -> str:
    return TIP_MAP.get(topic.lower(), "No tip available for this topic.")


# Simple command interpreter (stub for voice/text routing)
# Returns a small payload keyed by topic name to be rendered by UI

def interpret_command(command_text: str) -> Dict[str, List[str]]:
    t = command_text.lower()
    if any(k in t for k in ["pattern", "candle", "candlestick"]):
        return {"Patterns": list(PATTERN_GLOSSARY.keys())[:12]}
    if "indicator" in t:
        return {"Indicators": ["MA50", "MA200", "RSI", "MACD", "VWAP", "Bollinger"]}
    if any(k in t for k in ["macro", "calendar", "event"]):
        return {"Macro": ["CPI", "PPI", "FOMC", "Jobs", "GDP"]}
    if any(k in t for k in ["psych", "journal", "mind", "discipline"]):
        return {"Psychology": ["FOMO control", "process checklists", "risk discipline"]}
    return {"Help": ["Ask about patterns, indicators, macro events, or psychology"]}

# Placeholder for merged improvements from archived variants (currently identical variants).
