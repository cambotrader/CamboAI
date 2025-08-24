from fastapi import APIRouter, HTTPException
import numpy as np
from typing import List, Dict

# Optional TA-Lib import with graceful fallback
try:
    import talib  # type: ignore
    HAS_TALIB = True
except Exception:
    talib = None  # type: ignore
    HAS_TALIB = False

router = APIRouter()


def _sma_np(values: np.ndarray, period: int) -> np.ndarray:
    if len(values) < period:
        return np.array([np.nan] * len(values))
    kernel = np.ones(period) / period
    sma = np.convolve(values, kernel, mode="valid")
    pad = np.array([np.nan] * (period - 1))
    return np.concatenate([pad, sma])


def _rsi_np(values: np.ndarray, period: int) -> np.ndarray:
    if len(values) < period + 1:
        return np.array([np.nan] * len(values))
    deltas = np.diff(values)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = np.empty_like(values)
    avg_loss = np.empty_like(values)
    avg_gain[:period] = np.nan
    avg_loss[:period] = np.nan
    avg_gain[period] = gains[:period].mean()
    avg_loss[period] = losses[:period].mean()
    for i in range(period + 1, len(values)):
        avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gains[i - 1]) / period
        avg_loss[i] = (avg_loss[i - 1] * (period - 1) + losses[i - 1]) / period
    rs = avg_gain / np.where(avg_loss == 0, np.nan, avg_loss)
    rsi = 100 - (100 / (1 + rs))
    rsi[:period] = np.nan
    return rsi


def _bbands_np(values: np.ndarray, period: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    middle = _sma_np(values, period)
    if len(values) < period:
        return (np.array([np.nan] * len(values)), middle, np.array([np.nan] * len(values)))
    rolling_std = np.array([np.nan] * len(values))
    for i in range(period - 1, len(values)):
        rolling_std[i] = np.std(values[i - period + 1 : i + 1])
    upper = middle + 2 * rolling_std
    lower = middle - 2 * rolling_std
    return upper, middle, lower


@router.post("/technical")
async def analyze_technical(data: Dict[str, List[float]]):
    try:
        close_prices = np.array(data["close"], dtype=float)

        if HAS_TALIB:
            sma = talib.SMA(close_prices, timeperiod=20)
            rsi = talib.RSI(close_prices, timeperiod=14)
            upper, middle, lower = talib.BBANDS(close_prices, timeperiod=20)
        else:
            sma = _sma_np(close_prices, 20)
            rsi = _rsi_np(close_prices, 14)
            upper, middle, lower = _bbands_np(close_prices, 20)

        return {
            "sma": np.nan_to_num(sma, nan=None).tolist(),
            "rsi": np.nan_to_num(rsi, nan=None).tolist(),
            "bollinger_bands": {
                "upper": np.nan_to_num(upper, nan=None).tolist(),
                "middle": np.nan_to_num(middle, nan=None).tolist(),
                "lower": np.nan_to_num(lower, nan=None).tolist(),
            },
            "using_talib": HAS_TALIB,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
