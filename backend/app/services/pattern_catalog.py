from __future__ import annotations
from typing import Dict, Any

# Minimal catalog to power hover tooltips. We can expand continuously.
# Keys are lowercase identifiers; alias map lets us match detections.

CATALOG: Dict[str, Dict[str, Any]] = {
    # Candlestick patterns
    "bullish_engulfing": {
        "name": "Bullish Engulfing",
        "type": "candlestick",
        "why": "Signals a potential bullish reversal after a down move when a large green candle engulfs the prior red candle.",
        "how_to_detect": "Body of current candle completely engulfs body of prior candle; close > open and prior close < prior open.",
        "trade_notes": "Confirmation via next candle close or support bounce; combine with rising volume and uptrend resumption.",
        "refs": ["TA-Lib CDLENGULFING"],
    },
    "bearish_engulfing": {
        "name": "Bearish Engulfing",
        "type": "candlestick",
        "why": "Potential bearish reversal after an up move as a large red candle engulfs the prior green candle.",
        "how_to_detect": "Body of current candle completely engulfs body of prior candle; close < open and prior close > prior open.",
        "trade_notes": "Look for breakdowns from resistance; combine with weakening momentum (e.g., RSI divergence).",
        "refs": ["TA-Lib CDLENGULFING"],
    },
    "hammer": {
        "name": "Hammer",
        "type": "candlestick",
        "why": "Suggests capitulation and potential reversal when long lower shadow shows buyers stepped in.",
        "how_to_detect": "Small real body near top of range with long lower shadow (>=2x body); appears after decline.",
        "trade_notes": "Prefer near support with volume spike; confirm with follow-through next bar.",
        "refs": ["TA-Lib CDLHAMMER"],
    },
    "shooting_star": {
        "name": "Shooting Star",
        "type": "candlestick",
        "why": "Potential bearish reversal when price rejects higher levels, leaving a long upper shadow.",
        "how_to_detect": "Small real body near low with long upper shadow (>=2x body); after an up move.",
        "trade_notes": "Stronger near resistance or on distribution volume; confirm with next bar weakness.",
        "refs": ["TA-Lib CDLSHOOTINGSTAR"],
    },
    "morning_star": {
        "name": "Morning Star",
        "type": "candlestick",
        "why": "Three-candle bullish reversal sequence after decline.",
        "how_to_detect": "Long red, gap/down small body, then long green closing into first candle's body.",
        "trade_notes": "Best with volume expansion and support zone confluence.",
        "refs": ["TA-Lib CDLMORNINGSTAR"],
    },
    "evening_star": {
        "name": "Evening Star",
        "type": "candlestick",
        "why": "Three-candle bearish reversal sequence after advance.",
        "how_to_detect": "Long green, gap/up small body, then long red closing into first candle's body.",
        "trade_notes": "Prefer at resistance; confirm with momentum rollover.",
        "refs": ["TA-Lib CDLEVENINGSTAR"],
    },
    "doji": {
        "name": "Doji",
        "type": "candlestick",
        "why": "Indecision that can precede reversals near key levels.",
        "how_to_detect": "Open ≈ Close; very small body with shadows.",
        "trade_notes": "Needs context; treat as a caution flag not a signal by itself.",
        "refs": ["TA-Lib CDLDOJI"],
    },
    "harami_bullish": {
        "name": "Harami (Bullish)",
        "type": "candlestick",
        "why": "Potential bullish reversal as a small body fits within prior large red body.",
        "how_to_detect": "Today's body entirely within prior body's range; color flip.",
        "trade_notes": "Confirmation improves reliability; combine with support and volume.",
        "refs": ["TA-Lib CDLHARAMI"],
    },
    "harami_bearish": {
        "name": "Harami (Bearish)",
        "type": "candlestick",
        "why": "Potential bearish reversal as a small body fits within prior large green body.",
        "how_to_detect": "Today's body entirely within prior body's range; color flip.",
        "trade_notes": "Prefer at resistance; confirm with breakdown.",
        "refs": ["TA-Lib CDLHARAMI"],
    },

    # Chart patterns
    "head_shoulders": {
        "name": "Head & Shoulders",
        "type": "chart",
        "why": "Classic reversal pattern signaling distribution and potential trend change.",
        "how_to_detect": "Three peaks with the middle (head) higher; neckline break confirms.",
        "trade_notes": "Entry on neckline break or retest; measured move equals head-to-neckline height.",
        "refs": ["Edwards & Magee"],
    },
    "inverse_head_shoulders": {
        "name": "Inverse Head & Shoulders",
        "type": "chart",
        "why": "Accumulation and potential trend reversal to the upside.",
        "how_to_detect": "Three troughs with middle lower; neckline breakout confirms.",
        "trade_notes": "Targets via head-to-neckline height; watch volume on breakout.",
        "refs": ["Edwards & Magee"],
    },
    "double_top": {
        "name": "Double Top",
        "type": "chart",
        "why": "Failed attempt to break highs; potential reversal.",
        "how_to_detect": "Two similar highs separated by a pullback; break of valley confirms.",
        "trade_notes": "Wait for confirmation below valley; stops above highs.",
        "refs": ["Bulkowski"],
    },
    "double_bottom": {
        "name": "Double Bottom",
        "type": "chart",
        "why": "Failed attempt to break lows; potential reversal.",
        "how_to_detect": "Two similar lows separated by a bounce; breakout above swing confirms.",
        "trade_notes": "Stops below lows; measure target to neckline.",
        "refs": ["Bulkowski"],
    },
    "triangle_sym": {
        "name": "Symmetrical Triangle",
        "type": "chart",
        "why": "Compression that often precedes continuation; energy builds.",
        "how_to_detect": "Lower highs and higher lows forming converging trendlines.",
        "trade_notes": "Breakout direction matters; measure height at start of pattern.",
        "refs": ["Bulkowski"],
    },
    "triangle_asc": {
        "name": "Ascending Triangle",
        "type": "chart",
        "why": "Bullish continuation as supply caps at resistance while demand rises.",
        "how_to_detect": "Flat top with rising lows.",
        "trade_notes": "Breakout volume confirmation; stops below last higher low.",
        "refs": ["Bulkowski"],
    },
    "triangle_desc": {
        "name": "Descending Triangle",
        "type": "chart",
        "why": "Bearish continuation as demand weakens at support.",
        "how_to_detect": "Flat bottom with falling highs.",
        "trade_notes": "Breakdown volume confirmation; stops above last lower high.",
        "refs": ["Bulkowski"],
    },
    "flag": {
        "name": "Flag",
        "type": "chart",
        "why": "Brief consolidation after a sharp move, often continues in same direction.",
        "how_to_detect": "Small channel sloping against prior strong impulse.",
        "trade_notes": "Enter on break of flag; target via flagpole.",
        "refs": ["Bulkowski"],
    },
    "pennant": {
        "name": "Pennant",
        "type": "chart",
        "why": "Small symmetrical triangle after a strong impulse.",
        "how_to_detect": "Mini converging trendlines; short duration.",
        "trade_notes": "Breakout with volume; target via pole height.",
        "refs": ["Bulkowski"],
    },
    "wedge_rising": {
        "name": "Rising Wedge",
        "type": "chart",
        "why": "Bearish bias as price rises on weakening momentum.",
        "how_to_detect": "Two rising, converging trendlines; breakdown is bearish.",
        "trade_notes": "Stops above wedge; confirm with momentum divergence.",
        "refs": ["Bulkowski"],
    },
    "wedge_falling": {
        "name": "Falling Wedge",
        "type": "chart",
        "why": "Bullish bias as price falls on weakening downside momentum.",
        "how_to_detect": "Two falling, converging trendlines; breakout is bullish.",
        "trade_notes": "Stops below wedge; confirm with momentum divergence.",
        "refs": ["Bulkowski"],
    },
    "cup_handle": {
        "name": "Cup & Handle",
        "type": "chart",
        "why": "Bullish continuation after rounded base with a brief pullback.",
        "how_to_detect": "U-shaped base followed by small downward drift; breakout confirms.",
        "trade_notes": "Target equals cup depth; watch volume on breakout.",
        "refs": ["O'Neil"],
    },
}

ALIASES = {
    # map detection names -> catalog keys
    "bullish engulfing": "bullish_engulfing",
    "bearish engulfing": "bearish_engulfing",
    "hammer": "hammer",
    "shooting star": "shooting_star",
    "morning star": "morning_star",
    "evening star": "evening_star",
    "doji": "doji",
    "harami": "harami_bullish",  # fallback
    "harami bullish": "harami_bullish",
    "harami bearish": "harami_bearish",
    # chart patterns generic fallbacks
    "triangle": "triangle_sym",
    "cup & handle": "cup_handle",
}


def describe(name: str) -> Dict[str, Any]:
    key = name.strip().lower()
    key = ALIASES.get(key, key.replace(" ", "_"))
    return CATALOG.get(key, {
        "name": name,
        "type": "unknown",
        "why": "",
        "how_to_detect": "",
        "trade_notes": "",
        "refs": [],
    })


def catalog() -> Dict[str, Any]:
    return {"items": list(CATALOG.values())}