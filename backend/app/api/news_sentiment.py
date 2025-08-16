from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta
import asyncio
import aiohttp
import re
from dataclasses import dataclass

router = APIRouter(prefix="/api/news", tags=["News & Sentiment"])

@dataclass
class NewsArticle:
    title: str
    description: str
    url: str
    source: str
    published_at: str
    sentiment_score: float = 0.0
    sentiment_label: Literal["bullish", "bearish", "neutral"] = "neutral"
    confidence: float = 0.0
    emoji: str = "⚪"

class SentimentResponse(BaseModel):
    articles: List[Dict[str, Any]]
    summary: Dict[str, Any]
    total_count: int
    avg_sentiment: float
    bullish_count: int
    bearish_count: int
    neutral_count: int

# Simple sentiment analysis (placeholder for FinBERT/transformers)
BULLISH_KEYWORDS = [
    'bull', 'bullish', 'positive', 'growth', 'gains', 'profit', 'earnings beat',
    'upgrade', 'buy', 'strong', 'surge', 'rally', 'breakout', 'momentum',
    'outperform', 'increase', 'rise', 'high', 'record', 'expansion', 'acquisition'
]

BEARISH_KEYWORDS = [
    'bear', 'bearish', 'negative', 'decline', 'loss', 'earnings miss',
    'downgrade', 'sell', 'weak', 'crash', 'correction', 'recession',
    'underperform', 'decrease', 'fall', 'low', 'layoffs', 'bankruptcy', 'risks'
]

def simple_sentiment_analysis(text: str) -> tuple[float, str, str]:
    """
    Simple rule-based sentiment analysis.
    Returns (score, label, emoji) where score is -1 to 1.
    """
    text_lower = text.lower()
    
    bullish_count = sum(1 for word in BULLISH_KEYWORDS if word in text_lower)
    bearish_count = sum(1 for word in BEARISH_KEYWORDS if word in text_lower)
    
    # Simple scoring
    if bullish_count > bearish_count:
        if bullish_count - bearish_count >= 2:
            return 0.8, "bullish", "🟢"
        else:
            return 0.4, "bullish", "🟢"
    elif bearish_count > bullish_count:
        if bearish_count - bullish_count >= 2:
            return -0.8, "bearish", "🔴"
        else:
            return -0.4, "bearish", "🔴"
    else:
        return 0.0, "neutral", "⚪"

# Mock news data (in production, integrate with NewsAPI, Alpha Vantage, etc.)
MOCK_NEWS = [
    {
        "title": "Tech Stocks Rally on Strong Earnings Reports",
        "description": "Major technology companies beat earnings expectations, driving broad market gains and investor optimism.",
        "url": "https://example.com/news1",
        "source": "MarketWatch",
        "published_at": (datetime.utcnow() - timedelta(hours=1)).isoformat()
    },
    {
        "title": "Federal Reserve Signals Potential Rate Cuts",
        "description": "Fed officials indicate possible monetary policy easing amid economic uncertainty and inflation concerns.",
        "url": "https://example.com/news2", 
        "source": "Reuters",
        "published_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
    },
    {
        "title": "Oil Prices Decline on Supply Concerns",
        "description": "Crude oil futures fall as traders worry about oversupply and weak demand from major economies.",
        "url": "https://example.com/news3",
        "source": "Bloomberg",
        "published_at": (datetime.utcnow() - timedelta(hours=3)).isoformat()
    },
    {
        "title": "AI Companies See Record Investment Flows",
        "description": "Artificial intelligence startups attract billions in venture capital funding, signaling strong sector momentum.",
        "url": "https://example.com/news4",
        "source": "CNBC",
        "published_at": (datetime.utcnow() - timedelta(hours=4)).isoformat()
    },
    {
        "title": "Banking Sector Faces Regulatory Headwinds",
        "description": "New financial regulations may impact bank profitability and lending practices across the industry.",
        "url": "https://example.com/news5",
        "source": "Financial Times",
        "published_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()
    }
]

@router.get("/sentiment", response_model=SentimentResponse)
async def get_news_sentiment(
    symbol: Optional[str] = Query(None, description="Filter by symbol (e.g., AAPL)"),
    limit: int = Query(20, ge=1, le=100, description="Max articles to return"),
    hours: int = Query(24, ge=1, le=168, description="Hours back to search")
):
    """
    Get news articles with sentiment analysis.
    Returns articles with sentiment scores, emojis, and aggregated metrics.
    """
    try:
        # In production: fetch from real news APIs
        articles = []
        
        for news_item in MOCK_NEWS[:limit]:
            # Analyze sentiment
            combined_text = f"{news_item['title']} {news_item['description']}"
            sentiment_score, sentiment_label, emoji = simple_sentiment_analysis(combined_text)
            
            # Filter by symbol if provided
            if symbol and symbol.upper() not in combined_text.upper():
                # In real implementation, use proper symbol matching
                if symbol.upper() not in ['TECH', 'AI', 'OIL', 'BANK']:
                    continue
                    
            article = {
                "title": news_item["title"],
                "description": news_item["description"],
                "url": news_item["url"],
                "source": news_item["source"],
                "published_at": news_item["published_at"],
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label,
                "confidence": abs(sentiment_score) * 0.8,  # Mock confidence
                "emoji": emoji,
                "timestamp_relative": _get_relative_time(news_item["published_at"])
            }
            articles.append(article)
            
        # Calculate aggregated metrics
        total_count = len(articles)
        bullish_count = len([a for a in articles if a["sentiment_label"] == "bullish"])
        bearish_count = len([a for a in articles if a["sentiment_label"] == "bearish"])  
        neutral_count = total_count - bullish_count - bearish_count
        
        avg_sentiment = sum(a["sentiment_score"] for a in articles) / max(total_count, 1)
        
        summary = {
            "overall_mood": "🟢 Bullish" if avg_sentiment > 0.1 else "🔴 Bearish" if avg_sentiment < -0.1 else "⚪ Neutral",
            "sentiment_distribution": {
                "bullish": f"{bullish_count}/{total_count} ({bullish_count/max(total_count,1)*100:.0f}%)",
                "bearish": f"{bearish_count}/{total_count} ({bearish_count/max(total_count,1)*100:.0f}%)",
                "neutral": f"{neutral_count}/{total_count} ({neutral_count/max(total_count,1)*100:.0f}%)"
            },
            "market_tone": _get_market_tone(avg_sentiment),
            "top_themes": ["Tech earnings", "Fed policy", "AI investment", "Banking regulation"]
        }
        
        return SentimentResponse(
            articles=articles,
            summary=summary,
            total_count=total_count,
            avg_sentiment=avg_sentiment,
            bullish_count=bullish_count,
            bearish_count=bearish_count,
            neutral_count=neutral_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News sentiment analysis failed: {str(e)}")

@router.post("/analyze-text")
async def analyze_text_sentiment(text: str):
    """
    Analyze sentiment of custom text input.
    Useful for analyzing headlines, tweets, or other market-related text.
    """
    try:
        sentiment_score, sentiment_label, emoji = simple_sentiment_analysis(text)
        
        return {
            "text": text,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "confidence": abs(sentiment_score) * 0.8,
            "emoji": emoji,
            "interpretation": _interpret_sentiment(sentiment_score)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@router.get("/market-mood")
async def get_market_mood():
    """
    Get overall market sentiment mood based on recent news flow.
    """
    try:
        # Analyze recent news for overall mood
        sentiment_data = await get_news_sentiment(limit=50)
        
        mood_score = sentiment_data.avg_sentiment
        
        if mood_score > 0.3:
            mood = "🚀 Very Bullish"
            description = "Strong positive sentiment dominates market news"
        elif mood_score > 0.1:
            mood = "🟢 Bullish"
            description = "Generally positive market sentiment"
        elif mood_score > -0.1:
            mood = "⚖️ Neutral"
            description = "Mixed signals with balanced sentiment"
        elif mood_score > -0.3:
            mood = "🔴 Bearish"
            description = "Generally negative market sentiment"
        else:
            mood = "📉 Very Bearish"
            description = "Strong negative sentiment in market news"
            
        return {
            "mood": mood,
            "description": description,
            "score": mood_score,
            "bullish_percentage": sentiment_data.bullish_count / max(sentiment_data.total_count, 1) * 100,
            "bearish_percentage": sentiment_data.bearish_count / max(sentiment_data.total_count, 1) * 100,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market mood analysis failed: {str(e)}")

def _get_relative_time(iso_time: str) -> str:
    """Convert ISO timestamp to relative time string."""
    try:
        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        diff = datetime.utcnow() - dt.replace(tzinfo=None)
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
    except:
        return "unknown"

def _get_market_tone(avg_sentiment: float) -> str:
    """Get descriptive market tone from sentiment score."""
    if avg_sentiment > 0.4:
        return "Euphoric - Risk-on sentiment"
    elif avg_sentiment > 0.2:
        return "Optimistic - Bullish undertone"
    elif avg_sentiment > -0.2:
        return "Cautious - Wait-and-see approach"
    elif avg_sentiment > -0.4:
        return "Pessimistic - Risk-off sentiment"
    else:
        return "Panic - Flight to safety"

def _interpret_sentiment(score: float) -> str:
    """Provide trading interpretation of sentiment score."""
    if score > 0.6:
        return "Strong buy signal - High conviction bullish"
    elif score > 0.2:
        return "Moderate buy signal - Cautiously bullish"
    elif score > -0.2:
        return "Hold signal - Neutral sentiment"
    elif score > -0.6:
        return "Moderate sell signal - Cautiously bearish"
    else:
        return "Strong sell signal - High conviction bearish"