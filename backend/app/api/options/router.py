from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any, Optional

from app.services.options.engine import price_multi_leg, presets, Exotic

router = APIRouter(prefix="/api/options", tags=["Options"])


class Leg(BaseModel):
    right: Literal["call", "put"]
    side: Literal["long", "short"] = "long"
    qty: float = 1.0
    strike: float
    expiry: float = Field(..., description="time to expiry in years")
    vol: float
    rate: float = 0.0
    div_yield: float = 0.0
    spot: Optional[float] = None


class MultiLegRequest(BaseModel):
    legs: List[Leg]
    preset: Literal["fast", "balanced", "high"] = "balanced"


@router.post("/price/multi-leg")
async def price_strategy(req: MultiLegRequest) -> Dict[str, Any]:
    try:
        result = price_multi_leg([l.model_dump() for l in req.legs], preset=req.preset)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class BarrierRequest(BaseModel):
    spot: float
    strike: float
    rate: float
    div_yield: float = 0.0
    vol: float
    t: float
    barrier: float
    barrier_type: Literal[
        "up-in","up-out","down-in","down-out"
    ]
    rebate: float = 0.0
    preset: Literal["fast", "balanced", "high"] = "balanced"


@router.post("/price/barrier")
async def price_barrier(req: BarrierRequest) -> Dict[str, Any]:
    # Placeholder wiring; implementation will be added in Phase 1/2
    return Exotic.price_barrier(**req.model_dump())


class AsianRequest(BaseModel):
    spot: float
    strike: float
    rate: float
    div_yield: float = 0.0
    vol: float
    t: float
    average: Literal["arith", "geom"] = "arith"
    preset: Literal["fast", "balanced", "high"] = "balanced"


@router.post("/price/asian")
async def price_asian(req: AsianRequest) -> Dict[str, Any]:
    return Exotic.price_asian(**req.model_dump())


@router.get("/presets")
async def get_presets() -> Dict[str, Any]:
    return presets()