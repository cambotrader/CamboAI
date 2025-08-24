from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..models.auth import get_current_user, User
from ..services.cache_service import cache_result, PaginationService, CacheInvalidator
from ..services.database_service import TransactionService, PortfolioService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transactions", tags=["transactions"])

class TransactionCreate(BaseModel):
    portfolio_id: str
    symbol: str
    type: str  # BUY, SELL
    quantity: float
    price: float
    commission: float = 0.0
    notes: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    portfolio_id: str
    symbol: str
    type: str
    quantity: float
    price: float
    total_amount: float
    commission: float
    notes: Optional[str]
    executed_at: datetime
    created_at: datetime

@router.get("/")
@cache_result("transactions", ttl=300)  # Cache for 5 minutes
async def get_transactions(
    portfolio_id: Optional[str] = Query(None, description="Filter by portfolio ID"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("executed_at", description="Sort by field"),
    order: str = Query("desc", description="Sort order (asc/desc)"),
    current_user: User = Depends(get_current_user)
):
    """Get paginated transaction history with filters"""
    try:
        transaction_service = TransactionService()
        portfolio_service = PortfolioService()
        
        # Verify portfolio access if portfolio_id is provided
        if portfolio_id:
            portfolio = await portfolio_service.get_portfolio(portfolio_id)
            if not portfolio or portfolio.user_id != current_user.id:
                raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Calculate pagination
        offset, limit = PaginationService.get_offset_limit(page, per_page)
        
        # Build filters
        filters = {"user_id": current_user.id}
        if portfolio_id:
            filters["portfolio_id"] = portfolio_id
        if symbol:
            filters["symbol"] = symbol.upper()
        if transaction_type:
            filters["type"] = transaction_type.upper()
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        
        # Get transactions with pagination
        transactions, total = await transaction_service.get_transactions_paginated(
            filters=filters,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        # Create pagination info
        pagination = PaginationService.create_pagination_info(total, page, per_page)
        
        return {
            "transactions": transactions,
            "pagination": pagination,
            "summary": {
                "total_transactions": total,
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create a new transaction"""
    try:
        transaction_service = TransactionService()
        portfolio_service = PortfolioService()
        
        # Verify portfolio ownership
        portfolio = await portfolio_service.get_portfolio(transaction.portfolio_id)
        if not portfolio or portfolio.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Create transaction
        new_transaction = await transaction_service.create_transaction(
            portfolio_id=transaction.portfolio_id,
            symbol=transaction.symbol.upper(),
            transaction_type=transaction.type.upper(),
            quantity=transaction.quantity,
            price=transaction.price,
            commission=transaction.commission,
            notes=transaction.notes,
            executed_at=datetime.utcnow()
        )
        
        # Invalidate relevant caches in background
        background_tasks.add_task(
            CacheInvalidator.invalidate_portfolio_cache, 
            transaction.portfolio_id
        )
        
        return new_transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/summary")
@cache_result("transaction_summary", ttl=300)
async def get_transaction_summary(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_user)
):
    """Get transaction summary statistics"""
    try:
        transaction_service = TransactionService()
        portfolio_service = PortfolioService()
        
        # Verify portfolio access
        if portfolio_id:
            portfolio = await portfolio_service.get_portfolio(portfolio_id)
            if not portfolio or portfolio.user_id != current_user.id:
                raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Calculate date range
        period_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365
        }
        
        days = period_days.get(period, 30)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get transaction summary
        summary = await transaction_service.get_transaction_summary(
            user_id=current_user.id,
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/export")
async def export_transactions(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    format: str = Query("csv", description="Export format: csv, json"),
    current_user: User = Depends(get_current_user)
):
    """Export transaction history"""
    try:
        from fastapi.responses import StreamingResponse
        import csv
        import json
        from io import StringIO
        
        transaction_service = TransactionService()
        portfolio_service = PortfolioService()
        
        # Verify portfolio access
        if portfolio_id:
            portfolio = await portfolio_service.get_portfolio(portfolio_id)
            if not portfolio or portfolio.user_id != current_user.id:
                raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Build filters
        filters = {"user_id": current_user.id}
        if portfolio_id:
            filters["portfolio_id"] = portfolio_id
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        
        # Get all transactions (no pagination for export)
        transactions, _ = await transaction_service.get_transactions_paginated(
            filters=filters,
            offset=0,
            limit=10000,  # Large limit for export
            sort_by="executed_at",
            order="desc"
        )
        
        if format.lower() == "csv":
            # CSV export
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Date", "Symbol", "Type", "Quantity", "Price", 
                "Total Amount", "Commission", "Notes"
            ])
            
            # Write data
            for txn in transactions:
                writer.writerow([
                    txn.executed_at.strftime("%Y-%m-%d %H:%M:%S"),
                    txn.symbol,
                    txn.type,
                    txn.quantity,
                    txn.price,
                    txn.total_amount,
                    txn.commission,
                    txn.notes or ""
                ])
            
            output.seek(0)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=transactions.csv"}
            )
        
        else:
            # JSON export
            data = []
            for txn in transactions:
                data.append({
                    "id": txn.id,
                    "portfolio_id": txn.portfolio_id,
                    "symbol": txn.symbol,
                    "type": txn.type,
                    "quantity": txn.quantity,
                    "price": txn.price,
                    "total_amount": txn.total_amount,
                    "commission": txn.commission,
                    "notes": txn.notes,
                    "executed_at": txn.executed_at.isoformat(),
                    "created_at": txn.created_at.isoformat()
                })
            
            return StreamingResponse(
                iter([json.dumps(data, indent=2)]),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=transactions.json"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
