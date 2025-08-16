from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

from app.services import news_sentiment as svc

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment"])


@router.get("/summary")
async def get_sentiment_summary(
    symbol: Optional[str] = None,
    sources: Optional[str] = Query(default=None, description="Comma-separated sources e.g. yahoo,google,reddit,macro_feeds"),
    limit: int = 50,
) -> Dict[str, Any]:
    try:
        src_list: Optional[List[str]] = [s.strip() for s in sources.split(",") if s.strip()] if sources else None
        return svc.sentiment_summary(symbol, sources=src_list, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))