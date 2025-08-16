from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Dict, Any, List, Optional
import math
import numpy as np

# Core accuracy presets
AccuracyPreset = Literal["fast", "balanced", "high"]


def _norm_cdf(x: np.ndarray | float) -> np.ndarray | float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: np.ndarray | float) -> np.ndarray | float:
    return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x * x)


@dataclass
class MarketInputs:
    spot: float
    strike: float
    rate: float  # risk-free (annualized, continuous comp ok)
    div_yield: float  # continuous dividend yield
    vol: float  # implied vol (annualized)
    t: float  # time to expiry in years


@dataclass
class PriceResult:
    price: float
    greeks: Dict[str, float]


class VanillaBS:
    """European options via Black-Scholes (with continuous dividend yield)."""

    @staticmethod
    def price(inputs: MarketInputs, right: Literal["call", "put"]) -> PriceResult:
        S, K, r, q, sigma, T = (
            inputs.spot,
            inputs.strike,
            inputs.rate,
            inputs.div_yield,
            max(1e-12, inputs.vol),
            max(1e-12, inputs.t),
        )
        if T <= 0:
            if right == "call":
                return PriceResult(price=max(0.0, S - K), greeks={"delta": 1.0 if S > K else 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0})
            else:
                return PriceResult(price=max(0.0, K - S), greeks={"delta": -1.0 if S < K else 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0})

        d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        Nd1 = _norm_cdf(d1)
        Nd2 = _norm_cdf(d2)
        n_d1 = _norm_pdf(d1)
        disc_r = math.exp(-r * T)
        disc_q = math.exp(-q * T)

        if right == "call":
            price = S * disc_q * Nd1 - K * disc_r * Nd2
            delta = disc_q * Nd1
            rho = T * K * disc_r * Nd2
        else:
            price = K * disc_r * _norm_cdf(-d2) - S * disc_q * _norm_cdf(-d1)
            delta = -disc_q * _norm_cdf(-d1)
            rho = -T * K * disc_r * _norm_cdf(-d2)

        gamma = disc_q * n_d1 / (S * sigma * math.sqrt(T))
        vega = S * disc_q * n_d1 * math.sqrt(T)
        theta = (
            - (S * disc_q * n_d1 * sigma) / (2 * math.sqrt(T))
            - r * K * disc_r * (Nd2 if right == "call" else _norm_cdf(-d2))
            + q * S * disc_q * (Nd1 if right == "call" else _norm_cdf(-d1))
        )

        return PriceResult(
            price=float(price),
            greeks={
                "delta": float(delta),
                "gamma": float(gamma),
                "vega": float(vega),
                "theta": float(theta),
                "rho": float(rho),
            },
        )


def price_multi_leg(legs: List[Dict[str, Any]], preset: AccuracyPreset = "balanced") -> Dict[str, Any]:
    """
    Price a multi-leg options strategy by summing leg prices using BS.
    Each leg dict: {
      "right": "call"|"put", "side": "long"|"short",
      "qty": float, "strike": float, "expiry": years,
      "vol": float, "rate": float, "div_yield": float,
      "spot": float (optional, defaults to common spot)
    }
    """
    if not legs:
        return {"price": 0.0, "legs": [], "greeks": {}}

    # Determine common spot if not provided per-leg
    common_spot: Optional[float] = None
    for leg in legs:
        if "spot" in leg and leg["spot"] is not None:
            common_spot = leg["spot"]
            break
    if common_spot is None:
        # require provided at least on first leg
        common_spot = float(legs[0]["spot"]) if "spot" in legs[0] else None
    if common_spot is None:
        raise ValueError("spot must be provided on at least one leg")

    total_price = 0.0
    total_greeks: Dict[str, float] = {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0}
    leg_outputs = []

    for leg in legs:
        S = float(leg.get("spot", common_spot))
        K = float(leg["strike"]) 
        T = float(leg["expiry"])
        vol = float(leg["vol"]) 
        r = float(leg.get("rate", 0.0))
        q = float(leg.get("div_yield", 0.0))
        right = leg["right"]
        side = leg.get("side", "long")
        qty = float(leg.get("qty", 1.0))

        res = VanillaBS.price(
            MarketInputs(spot=S, strike=K, rate=r, div_yield=q, vol=vol, t=T),
            right=right, 
        )
        leg_price = res.price * qty * (1.0 if side == "long" else -1.0)
        total_price += leg_price
        for gk, gv in res.greeks.items():
            total_greeks[gk] += gv * qty * (1.0 if side == "long" else -1.0)

        leg_outputs.append({
            "input": leg,
            "price": res.price,
            "greeks": res.greeks,
            "signed_price": leg_price,
        })

    return {
        "price": total_price,
        "greeks": total_greeks,
        "legs": leg_outputs,
        "preset": preset,
    }


# Placeholders for exotics, American/Bermudan, and QuantLib-backed pricers
# These will be expanded with full implementations and selectable engines.
class Exotic:
    @staticmethod
    def price_barrier(**kwargs) -> Dict[str, Any]:
        return {"status": "not_implemented", "detail": "Barrier pricing to be added (MC/Binomial/QuantLib)"}

    @staticmethod
    def price_asian(**kwargs) -> Dict[str, Any]:
        """Geometric-average Asian option (closed-form). Arith: placeholder.
        kwargs: spot, strike, rate, div_yield, vol, t, average("geom"|"arith")
        """
        S = float(kwargs.get("spot"))
        K = float(kwargs.get("strike"))
        r = float(kwargs.get("rate", 0.0))
        q = float(kwargs.get("div_yield", 0.0))
        sigma = max(1e-12, float(kwargs.get("vol")))
        T = max(1e-12, float(kwargs.get("t")))
        avg = kwargs.get("average", "arith")
        right = kwargs.get("right", "call")

        if avg == "geom":
            # ln G_T ~ Normal(mg, vg)
            b = r - q
            vg = sigma * sigma * T / 3.0
            mg = math.log(S) + (b - 0.5 * sigma * sigma) * (T / 2.0)
            sg = math.sqrt(vg)
            # d1g, d2g for lognormal with variance vg
            d1g = (mg - math.log(K) + vg) / sg
            d2g = d1g - sg
            EG = math.exp(mg + 0.5 * vg)
            disc = math.exp(-r * T)
            if right == "call":
                price = disc * (EG * _norm_cdf(d1g) - K * _norm_cdf(d2g))
            else:
                price = disc * (K * _norm_cdf(-d2g) - EG * _norm_cdf(-d1g))
            return {"price": float(price), "method": "geom_closed_form", "right": right}
        else:
            return {"status": "not_implemented", "detail": "Arithmetic Asian pricing to be added (MC/control variates)"}

    @staticmethod
    def price_lookback(**kwargs) -> Dict[str, Any]:
        return {"status": "not_implemented"}


def presets() -> Dict[str, Dict[str, Any]]:
    return {
        "fast": {"mc_paths": 2_000, "binomial_steps": 100},
        "balanced": {"mc_paths": 10_000, "binomial_steps": 500},
        "high": {"mc_paths": 50_000, "binomial_steps": 1_500},
    }