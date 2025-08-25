"""Simple position sizing utilities (MVP).

Currently implements a naive fixed-fractional risk model and ATR-based sizing placeholder.
"""
from __future__ import annotations

from typing import Dict
import pandas as pd


def atr(df: pd.DataFrame, period: int = 14) -> float:
    if not {'High','Low','Close'}.issubset(df.columns) or len(df) < period + 1:
        return 0.0
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    tr = (high - low).abs().to_frame('hl')
    tr['hc'] = (high - prev_close).abs()
    tr['lc'] = (low - prev_close).abs()
    tr_val = tr.max(axis=1)
    return float(tr_val.rolling(period).mean().iloc[-1]) if tr_val.notna().sum() >= period else 0.0


def fixed_fractional(account_equity: float, risk_fraction: float) -> float:
    return max(0.0, account_equity * risk_fraction)


def position_size(account_equity: float, df: pd.DataFrame, risk_fraction: float = 0.01) -> Dict[str, float]:
    risk_capital = fixed_fractional(account_equity, risk_fraction)
    current_price = float(df['Close'].iloc[-1]) if 'Close' in df.columns and not df.empty else 0.0
    A = atr(df) or (0.01 * current_price)
    # Risk per share heuristic: 1 ATR
    risk_per_share = A if A > 0 else max(0.5, 0.01 * current_price)
    shares = risk_capital / risk_per_share if risk_per_share else 0
    return {
        'account_equity': account_equity,
        'risk_fraction': risk_fraction,
        'atr': A,
        'risk_capital': risk_capital,
        'approx_shares': int(shares) if shares > 0 else 0,
        'price': current_price,
    }

__all__ = ["position_size", "atr"]
