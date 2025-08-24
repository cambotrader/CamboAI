from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

from .market_data_providers import get_market_data_router


# Typed schema for output
@dataclass
class SignalOutput:
    label: str              # BUY | SELL | NEUTRAL
    score: float            # -1..1 normalized
    confidence: float       # 0..1 calibrated
    version: str            # model version id
    detail: Dict[str, Any]  # feature snapshot and diagnostics


class SignalModelV2:
    """Baseline heuristic-as-model with clear feature map and versioning.
    Replace internals later with trained model; keep same interface.
    """

    version = "v2.0.0-baseline"

    def _features(self, close: pd.Series) -> Dict[str, float]:
        # Basic, deterministic feature set
        rets = close.pct_change().dropna()
        mom_5 = (close / close.shift(5) - 1).iloc[-1]
        mom_20 = (close / close.shift(20) - 1).iloc[-1] if len(close) >= 21 else 0.0
        vol_20 = rets.rolling(20).std().iloc[-1] if len(rets) >= 20 else rets.std()
        rsi = self._rsi(close, 14)
        bb_u, bb_m, bb_l = self._bb(close, 20, 2.0)
        width = (bb_u - bb_l).iloc[-1] if hasattr(bb_u - bb_l, "iloc") else (bb_u - bb_l)
        width = float(width) if not isinstance(width, (float, int)) else width
        band_pos = float((close.iloc[-1] - (bb_l.iloc[-1] if hasattr(bb_l, "iloc") else bb_l)) / max(1e-9, width)) if width != 0 else 0.5
        return {
            "mom_5": float(mom_5),
            "mom_20": float(mom_20),
            "vol_20": float(vol_20),
            "rsi": float(rsi),
            "band_pos": float(band_pos),
        }

    def _rsi(self, s: pd.Series, period: int = 14) -> float:
        if len(s) < period + 1:
            return 50.0
        d = s.diff()
        gain = d.clip(lower=0.0)
        loss = -d.clip(upper=0.0)
        ag = gain.ewm(alpha=1/period, adjust=False).mean()
        al = loss.ewm(alpha=1/period, adjust=False).mean() + 1e-12
        rs = ag / al
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    def _bb(self, s: pd.Series, period: int = 20, mult: float = 2.0):
        ma = s.rolling(period, min_periods=1).mean()
        sd = s.rolling(period, min_periods=1).std(ddof=0)
        return ma + mult * sd, ma, ma - mult * sd

    def _score(self, f: Dict[str, float]) -> float:
        # Weighted linear combo (transparent baseline)
        w = {
            "mom_5": 0.35,
            "mom_20": 0.25,
            "vol_20": -0.10,  # penalize high vol for baseline
            "rsi": 0.20,      # scaled later
            "band_pos": 0.30,
        }
        # Scale rsi to [-1,1]
        rsi_norm = (f["rsi"] - 50.0) / 50.0
        raw = (
            w["mom_5"] * f["mom_5"] +
            w["mom_20"] * f["mom_20"] +
            w["vol_20"] * f["vol_20"] +
            w["rsi"] * rsi_norm +
            w["band_pos"] * (f["band_pos"] - 0.5)
        )
        # Squash to [-1,1] by tanh
        return float(np.tanh(raw * 3.0))

    def _label(self, s: float) -> str:
        if s > 0.25:
            return "BUY"
        if s < -0.25:
            return "SELL"
        return "NEUTRAL"

    def _confidence(self, s: float) -> float:
        # Monotonic mapping; later replace with calibration
        return float(abs(s))

    def predict(self, symbol: str, period: str = "3mo", interval: str = "1d", preferred_provider: str | None = None) -> SignalOutput:
        md = get_market_data_router().fetch_ohlcv(symbol, period=period, interval=interval, preferred_provider=preferred_provider)
        df: pd.DataFrame = md["df"]
        if df is None or df.empty or "Close" not in df:
            # Minimal stub output
            return SignalOutput(
                label="NEUTRAL", score=0.0, confidence=0.0, version=self.version,
                detail={"reason": "no_data", "provider": getattr(md.get("provider"), "name", "unknown")}
            )
        # Ensure Close is a clean float series
        close = pd.Series(pd.to_numeric(df["Close"], errors="coerce")).fillna(method="ffill").fillna(method="bfill").fillna(0.0)
        features = self._features(close)
        score = self._score(features)
        label = self._label(score)
        conf = self._confidence(score)
        return SignalOutput(
            label=label,
            score=round(score, 6),
            confidence=round(conf, 6),
            version=self.version,
            detail={
                "symbol": symbol,
                "features": {k: round(v, 6) for k, v in features.items()},
                "provider": getattr(md.get("provider"), "name", "unknown"),
                "period": period,
                "interval": interval,
            }
        )


_model_singleton: Optional[SignalModelV2] = None

def get_signals_model_v2() -> SignalModelV2:
    global _model_singleton
    if _model_singleton is None:
        _model_singleton = SignalModelV2()
    return _model_singleton