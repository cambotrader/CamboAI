from __future__ import annotations
from typing import Dict, Any, List, Literal
import numpy as np
from dataclasses import dataclass

@dataclass
class HedgeInputs:
    paths: int = 2000
    dt: float = 1/252
    mu: float = 0.0
    transaction_bps: float = 0.0

# Simple delta-hedging backtest using BS delta on a single European option
# This is a baseline; later versions will support gamma/vega hedging and multi-leg portfolios.
def delta_hedge_backtest(
    spot0: float,
    sigma: float,
    rate: float,
    t_years: float,
    strike: float,
    right: Literal['call','put']='call',
    hedging_dt: float=1/252,
    mu: float=0.0,
    transaction_bps: float=0.0,
) -> Dict[str, Any]:
    steps = max(1, int(t_years / hedging_dt))
    dt = t_years / steps
    # Simulate one GBM path for the underlying. For determinism, seed can be added.
    S = spot0
    pnl = 0.0
    delta_prev = 0.0

    for i in range(steps):
        t_remain = t_years - i*dt
        delta_now = _bs_delta(S, strike, rate, 0.0, sigma, t_remain, right)
        # Rebalance
        rebalance = delta_now - delta_prev
        cost = (abs(rebalance) * S) * (transaction_bps / 10000.0)
        pnl -= cost
        delta_prev = delta_now
        # Evolve S
        z = np.random.normal()
        S = S * np.exp((mu - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*z)
    # Option payoff at maturity
    payoff = max(S - strike, 0.0) if right=='call' else max(strike - S, 0.0)
    # Short option + hedging PnL from stock
    option_pnl = -payoff  # short 1 option unit for hedging perspective
    stock_pnl = delta_prev * (S - spot0)
    total = pnl + option_pnl + stock_pnl
    return {
        'final_underlying': S,
        'option_payoff': payoff,
        'stock_pnl': stock_pnl,
        'transaction_costs': -pnl if pnl<0 else 0.0,
        'total_pnl': total,
        'steps': steps,
    }


def _bs_delta(S: float, K: float, r: float, q: float, sigma: float, T: float, right: str) -> float:
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0
    import math
    from math import log, sqrt
    d1 = (log(S/K) + (r - q + 0.5*sigma*sigma)*T) / (sigma*sqrt(T))
    Nd1 = 0.5*(1+math.erf(d1/math.sqrt(2)))
    if right == 'call':
        return math.exp(-q*T)*Nd1
    else:
        return -math.exp(-q*T)*(1-Nd1)