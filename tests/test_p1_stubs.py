"""Smoke tests for newly added P1 scaffolds.

Run with: python -m pytest tests/test_p1_stubs.py  (if pytest available) or simply python tests/test_p1_stubs.py
"""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from modules.strategy import strategy_engine as se
from modules.strategy.plan_generator import generate_trade_plan
from modules.scan.scanner import default_scanner
from modules.sentiment import finbert
from modules import pattern_engine
from modules import chart_patterns
from modules.models import PatternDetection, SentimentSnapshot


def _make_df():
    import numpy as np
    import pandas as pd
    data = {
        "Open": [100 + i for i in range(60)],
        "High": [101 + i for i in range(60)],
        "Low": [99 + i for i in range(60)],
        "Close": [100 + i + (1 if i % 15 == 0 else 0) for i in range(60)],
        "Volume": [1000 + (i * 5) for i in range(60)],
    }
    return pd.DataFrame(data)


def smoke_run():
    df = _make_df()
    symbol = "TEST"
    # Strategies
    strat_sigs = se.evaluate(symbol, df)
    # Patterns (basic)
    p_basic = pattern_engine.detect(df)
    patterns = [
        PatternDetection(pattern_type=s.type, direction=s.direction, confidence=s.confidence, symbol=symbol, meta=s.meta)
        for s in p_basic
    ]
    # Advanced (currently empty)
    patterns.extend(chart_patterns.detect_advanced(symbol, df))
    # Sentiment
    headline_scores = finbert.summarize(["Stock surge on strong upgrade", "Weak guidance causes drop"])
    sent_label = finbert.label(headline_scores)
    sentiment = [SentimentSnapshot(symbol=symbol, provider="finbert_stub", scores=headline_scores, label=sent_label)]
    # Scanner
    scanner = default_scanner()
    findings = scanner.run(symbol, {"data": df})
    # Trade Plan
    plan = generate_trade_plan(symbol, strat_sigs, patterns, sentiment)
    assert plan["symbol"] == symbol
    # Basic invariants
    return {
        "strategies": len(strat_sigs),
        "patterns": len(patterns),
        "findings": len(findings),
        "plan_bias": plan["bias"],
    }


if __name__ == "__main__":
    out = smoke_run()
    print(json.dumps(out, indent=2))
