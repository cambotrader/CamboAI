from fastapi import APIRouter, HTTPException
import talib
import numpy as np
from typing import List, Dict

router = APIRouter()

@router.post("/technical")
async def analyze_technical(data: Dict[str, List[float]]):
    try:
        close_prices = np.array(data["close"])
        
        # Calculate indicators
        sma = talib.SMA(close_prices, timeperiod=20)
        rsi = talib.RSI(close_prices, timeperiod=14)
        upper, middle, lower = talib.BBANDS(close_prices, timeperiod=20)
        
        return {
            "sma": sma.tolist(),
            "rsi": rsi.tolist(),
            "bollinger_bands": {
                "upper": upper.tolist(),
                "middle": middle.tolist(),
                "lower": lower.tolist()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
