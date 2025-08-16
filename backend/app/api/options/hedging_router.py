from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Dict, Any

from app.services.options.hedging import delta_hedge_backtest

router = APIRouter(prefix="/api/options/hedging", tags=["Options Hedging"]) 

class DeltaHedgeReq(BaseModel):
    spot: float
    vol: float
    rate: float
    t: float
    strike: float
    right: Literal['call','put'] = 'call'
    hedging_dt: float = 1/252
    mu: float = 0.0
    transaction_bps: float = 0.0

@router.post("/delta")
async def delta_hedge(req: DeltaHedgeReq) -> Dict[str, Any]:
    try:
        return delta_hedge_backtest(
            spot0=req.spot,
            sigma=req.vol,
            rate=req.rate,
            t_years=req.t,
            strike=req.strike,
            right=req.right,
            hedging_dt=req.hedging_dt,
            mu=req.mu,
            transaction_bps=req.transaction_bps,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))