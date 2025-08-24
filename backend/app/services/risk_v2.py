from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .market_data_providers import get_market_data_router


@dataclass
class RiskMetrics:
    volatility_annual: float
    max_drawdown: float
    var_95_daily: float
    es_95_daily: float
    sharpe: float


class RiskEngineV2:
    version = "v2.0.0"

    def _returns(self, close: pd.Series) -> pd.Series:
        return close.pct_change().dropna()

    def _max_dd(self, values: pd.Series) -> float:
        peak = values.cummax()
        dd = (values / peak) - 1.0
        return float(dd.min()) if len(dd) else 0.0

    def _historical_var_es(self, rets: pd.Series, alpha: float = 0.95) -> tuple[float, float]:
        if len(rets) == 0:
            return 0.0, 0.0
        q = np.quantile(rets, 1 - alpha)
        tail = rets[rets <= q]
        es = float(tail.mean()) if len(tail) else float(q)
        return float(q), es

    def _mc_var_es(self, mu: float, sigma: float, n: int = 20000, alpha: float = 0.95) -> tuple[float, float]:
        if sigma <= 0:
            return 0.0, 0.0
        sims = np.random.normal(mu, sigma, size=n)
        q = np.quantile(sims, 1 - alpha)
        es = float(sims[sims <= q].mean())
        return float(q), es

    def summarize(self, symbol: str, period: str = "6mo", interval: str = "1d", preferred_provider: str | None = None) -> Dict[str, Any]:
        md = get_market_data_router().fetch_ohlcv(symbol, period=period, interval=interval, preferred_provider=preferred_provider)
        df: pd.DataFrame = md["df"]
        if df is None or df.empty or "Close" not in df:
            return {"symbol": symbol, "version": self.version, "metrics": RiskMetrics(0,0,0,0,0).__dict__}
        close = df["Close"].astype(float)
        rets = self._returns(close)
        vol_ann = float(rets.std() * np.sqrt(252)) if len(rets) else 0.0
        mdd = self._max_dd(close)
        mu = float(rets.mean())
        sd = float(rets.std())
        var_h, es_h = self._historical_var_es(rets)
        var_mc, es_mc = self._mc_var_es(mu, sd)
        sharpe = (mu * 252) / (vol_ann + 1e-12)
        return {
            "symbol": symbol,
            "version": self.version,
            "metrics": RiskMetrics(
                volatility_annual=round(vol_ann, 6),
                max_drawdown=round(mdd, 6),
                var_95_daily=round(min(var_h, var_mc), 6),
                es_95_daily=round(min(es_h, es_mc), 6),
                sharpe=round(sharpe, 6),
            ).__dict__,
            "detail": {
                "provider": getattr(md.get("provider"), "name", "unknown"),
                "period": period,
                "interval": interval,
            }
        }


_engine_singleton: Optional[RiskEngineV2] = None

def get_risk_engine_v2() -> RiskEngineV2:
    global _engine_singleton
    if _engine_singleton is None:
        _engine_singleton = RiskEngineV2()
    return _engine_singleton