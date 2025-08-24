from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.services.sentiment_v2 import SentimentDoc as SDoc, get_sentiment_v2
from app.core.metrics import MetricsManager

router = APIRouter(prefix="/api/v2/sentiment", tags=["Sentiment v2"]) 

class SentDoc(BaseModel):
    id: str
    source: str
    title: str
    text: str | None = None
    url: str | None = None
    timestamp: str | None = None

class SentAggregateResponse(BaseModel):
    score: float
    label: str
    detail: dict

@router.post("/aggregate", response_model=SentAggregateResponse)
async def aggregate(docs: List[SentDoc]):
    MetricsManager.record_analysis_request("sentiment_v2")
    agg = get_sentiment_v2().aggregate([SDoc(**d.model_dump()) for d in docs])
    return SentAggregateResponse(score=agg.score, label=agg.label, detail=agg.detail)