from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from pydantic import BaseModel
from ..models.auth import get_current_user, User
from ..services.broker_service import AlpacaBrokerService
from ..services.cache_service import cache_result, PaginationService, CacheInvalidator
from ..services.database_service import PortfolioService, PositionService, PerformanceService

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

class PortfolioPosition(BaseModel):
    id: int
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    market_value: float
    entry_date: datetime

class PerformanceData(BaseModel):
    date: datetime
    value: float
    daily_return: float
    cumulative_return: float

# Mock portfolio data - in production this would come from a database
mock_positions = [
    {
        "id": 1,
        "symbol": "AAPL",
        "quantity": 100,
        "entry_price": 150.00,
        "entry_date": datetime.now() - timedelta(days=30)
    },
    {
        "id": 2,
        "symbol": "MSFT",
        "quantity": 50,
        "entry_price": 300.00,
        "entry_date": datetime.now() - timedelta(days=45)
    },
    {
        "id": 3,
        "symbol": "GOOGL",
        "quantity": 25,
        "entry_price": 2800.00,
        "entry_date": datetime.now() - timedelta(days=60)
    }
]

@router.get("/positions")
@cache_result("positions", ttl=60)  # Cache for 1 minute
async def get_portfolio_positions(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("symbol", description="Sort by field"),
    order: str = Query("asc", description="Sort order (asc/desc)"),
    symbol_filter: Optional[str] = Query(None, description="Filter by symbol"),
    current_user: User = Depends(get_current_user)
):
    """Get paginated portfolio positions with caching and real-time pricing"""
    try:
        positions = []
        
        for pos in mock_positions:
            # Get current price from Yahoo Finance
            ticker = yf.Ticker(pos["symbol"])
            current_data = ticker.history(period="1d", interval="1m")
            
            if not current_data.empty:
                current_price = current_data['Close'].iloc[-1]
                market_value = pos["quantity"] * current_price
                total_cost = pos["quantity"] * pos["entry_price"]
                pnl = market_value - total_cost
                pnl_percentage = (pnl / total_cost) * 100
                
                positions.append(PortfolioPosition(
                    id=pos["id"],
                    symbol=pos["symbol"],
                    quantity=pos["quantity"],
                    entry_price=pos["entry_price"],
                    current_price=round(current_price, 2),
                    pnl=round(pnl, 2),
                    pnl_percentage=round(pnl_percentage, 2),
                    market_value=round(market_value, 2),
                    entry_date=pos["entry_date"]
                ))
        
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching positions: {str(e)}")

@router.get("/performance", response_model=List[PerformanceData])
async def get_portfolio_performance(days: int = 30):
    """Get portfolio performance over time"""
    try:
        # Generate mock performance data - in production this would be calculated from actual trades
        performance_data = []
        base_value = 100000  # Starting portfolio value
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            # Simulate some market movement
            daily_return = (hash(str(date)) % 1000 - 500) / 10000  # Random return between -5% and 5%
            
            if i == 0:
                value = base_value
                cumulative_return = 0
            else:
                value = performance_data[-1].value * (1 + daily_return)
                cumulative_return = (value - base_value) / base_value * 100
            
            performance_data.append(PerformanceData(
                date=date,
                value=round(value, 2),
                daily_return=round(daily_return * 100, 4),
                cumulative_return=round(cumulative_return, 2)
            ))
        
        return performance_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching performance: {str(e)}")

@router.get("/summary")
async def get_portfolio_summary():
    """Get portfolio summary statistics"""
    try:
        positions = await get_portfolio_positions()
        performance = await get_portfolio_performance()
        
        total_value = sum(pos.market_value for pos in positions)
        total_pnl = sum(pos.pnl for pos in positions)
        total_cost = sum(pos.quantity * pos.entry_price for pos in positions)
        total_return = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        current_performance = performance[-1] if performance else None
        
        return {
            "total_value": round(total_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_return_percentage": round(total_return, 2),
            "positions_count": len(positions),
            "current_day_value": current_performance.value if current_performance else 0,
            "current_day_return": current_performance.daily_return if current_performance else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")

@router.get("/watchlist")
async def get_watchlist():
    """Get user's watchlist with current prices"""
    try:
        watchlist_symbols = ["SPY", "QQQ", "IWM", "GLD", "TSLA", "NVDA", "AMD"]
        watchlist_data = []
        
        for symbol in watchlist_symbols:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="2d", interval="1d")
            
            if len(data) >= 2:
                current_price = data['Close'].iloc[-1]
                previous_price = data['Close'].iloc[-2]
                change = current_price - previous_price
                change_percentage = (change / previous_price) * 100
                
                watchlist_data.append({
                    "symbol": symbol,
                    "current_price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_percentage": round(change_percentage, 2),
                    "volume": int(data['Volume'].iloc[-1])
                })
        
        return watchlist_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching watchlist: {str(e)}")
