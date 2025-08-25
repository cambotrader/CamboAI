from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd

from backend.app.services.pattern_service import PatternService

router = APIRouter(prefix="/patterns", tags=["patterns"])
pattern_service = PatternService()

class OHLCIn(BaseModel):
    symbol: str
    timeframe: str = "1d"
    open: list[float]
    high: list[float]
    low: list[float]
    close: list[float]
    index: list[str]
    patterns: list[str] | None = None
    calibrate: bool = True
    persist: bool = False
    persist_harmonic: bool = True

@router.post("/scan")
def scan_patterns(payload: OHLCIn):
    df = pd.DataFrame({
        "open": payload.open,
        "high": payload.high,
        "low": payload.low,
        "close": payload.close
    }, index=pd.to_datetime(payload.index))
    detections = pattern_service.scan(
        df,
        include=payload.patterns,
        calibrate=payload.calibrate,
        persist=payload.persist,
        symbol=payload.symbol,
        timeframe=payload.timeframe,
        persist_harmonic=payload.persist_harmonic
    )
    return {"count": len(detections), "detections": detections}