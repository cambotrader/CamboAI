from fastapi import APIRouter, HTTPException
from typing import List
import yfinance as yf
import pandas as pd

router = APIRouter()

@router.get("/stock/{symbol}")
async def get_stock_data(symbol: str, interval: str = "1d", period: str = "1mo"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/crypto/{symbol}")
async def get_crypto_data(symbol: str):
    try:
        ticker = yf.Ticker(f"{symbol}-USD")
        df = ticker.history(period="1d", interval="1m")
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
