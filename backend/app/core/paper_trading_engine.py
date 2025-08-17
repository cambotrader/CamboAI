"""
📊 PAPER TRADING ENGINE - REALISTIC SIMULATION
Complete paper trading system with realistic execution, slippage, and market impact
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import uuid
from decimal import Decimal, ROUND_HALF_UP

from ..models.trading_models import (
    Order, OrderStatus, OrderType, OrderSide, Account, Asset, Position, 
    OrderFill, Transaction, User
)
from ..core.websocket_manager import websocket_manager
from .market_data_stream import market_data_stream

logger = logging.getLogger(__name__)

class ExecutionQuality(Enum):
    EXCELLENT = "excellent"  # Minimal slippage
    GOOD = "good"           # Normal slippage
    POOR = "poor"           # High slippage
    REJECTED = "rejected"    # Order rejected

@dataclass
class MarketCondition:
    volatility: float           # Current volatility estimate
    liquidity_score: float     # 0-1, higher = more liquid
    spread_bps: float          # Bid-ask spread in basis points
    volume_ratio: float        # Current volume vs average
    trend_strength: float      # -1 to 1, trend direction strength
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None

@dataclass
class ExecutionResult:
    order_id: str
    status: OrderStatus
    filled_quantity: float
    average_fill_price: float
    total_fill_value: float
    commission: float
    fees: float
    slippage_bps: float
    market_impact_bps: float
    execution_time_ms: int
    fills: List[Dict[str, Any]] = field(default_factory=list)
    rejection_reason: Optional[str] = None

class RealisticPaperTradingEngine:
    """Advanced paper trading engine with realistic market simulation"""
    
    def __init__(self):
        self.pending_orders: Dict[str, Order] = {}
        self.order_queue = asyncio.Queue()
        self.market_conditions: Dict[str, MarketCondition] = {}
        
        # Execution parameters
        self.execution_params = {
            "base_commission": 0.0,      # Commission per share/contract
            "min_commission": 0.0,        # Minimum commission
            "sec_fee_rate": 0.0000221,   # SEC fee rate
            "taf_fee_rate": 0.000119,    # TAF fee rate
            "base_slippage_bps": 2.0,    # Base slippage in basis points
            "market_impact_factor": 0.1,  # Market impact coefficient
            "execution_delay_ms": (50, 500),  # Execution delay range
        }
        
        # Market simulation parameters
        self.simulation_params = {
            "volatility_mean_reversion": 0.95,
            "liquidity_persistence": 0.98,
            "spread_compression_factor": 0.85,
            "volume_clustering": 1.2,
        }
        
        # Performance tracking
        self.execution_stats = {
            "total_orders": 0,
            "filled_orders": 0,
            "rejected_orders": 0,
            "average_slippage": 0.0,
            "total_volume": 0.0,
        }
        
        # Start background tasks
        asyncio.create_task(self._order_processor())
        asyncio.create_task(self._market_condition_updater())
        asyncio.create_task(self._performance_monitor())
    
    async def submit_order(self, order: Order, db_session) -> ExecutionResult:
        """Submit order for paper trading execution"""
        
        order_id = str(order.id)
        logger.info(f"📝 Paper trading order submitted: {order_id} - {order.side.value} {order.quantity} {order.asset.symbol}")
        
        # Add to pending orders
        self.pending_orders[order_id] = order
        
        # Queue for processing
        await self.order_queue.put((order, db_session))
        
        self.execution_stats["total_orders"] += 1
        
        # Return immediate confirmation
        return ExecutionResult(
            order_id=order_id,
            status=OrderStatus.PENDING,
            filled_quantity=0.0,
            average_fill_price=0.0,
            total_fill_value=0.0,
            commission=0.0,
            fees=0.0,
            slippage_bps=0.0,
            market_impact_bps=0.0,
            execution_time_ms=0
        )
    
    async def cancel_order(self, order_id: str, db_session) -> bool:
        """Cancel pending order"""
        
        if order_id not in self.pending_orders:
            return False
        
        order = self.pending_orders[order_id]
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.utcnow()
        
        db_session.commit()
        
        # Remove from pending
        del self.pending_orders[order_id]
        
        # Notify via WebSocket
        await self._notify_order_update(order, "cancelled")
        
        logger.info(f"❌ Paper trading order cancelled: {order_id}")
        return True
    
    async def _order_processor(self):
        """Background order processing loop"""
        
        while True:
            try:
                # Get next order from queue
                order, db_session = await self.order_queue.get()
                
                # Process the order
                execution_result = await self._execute_order(order, db_session)
                
                # Update database
                await self._update_order_in_db(order, execution_result, db_session)
                
                # Update position if filled
                if execution_result.status == OrderStatus.FILLED:
                    await self._update_position(order, execution_result, db_session)
                    
                    # Record transaction
                    await self._record_transaction(order, execution_result, db_session)
                
                # Remove from pending if complete
                if execution_result.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                    self.pending_orders.pop(str(order.id), None)
                
                # Notify via WebSocket
                await self._notify_order_update(order, execution_result.status.value)
                
                # Update performance stats
                self._update_execution_stats(execution_result)
                
            except Exception as e:
                logger.error(f"❌ Order processing error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_order(self, order: Order, db_session) -> ExecutionResult:
        """Execute order with realistic simulation"""
        
        symbol = order.asset.symbol
        start_time = datetime.utcnow()
        
        # Get current market data
        market_tick = market_data_stream.get_latest_tick(symbol)
        if not market_tick:
            return ExecutionResult(
                order_id=str(order.id),
                status=OrderStatus.REJECTED,
                filled_quantity=0.0,
                average_fill_price=0.0,
                total_fill_value=0.0,
                commission=0.0,
                fees=0.0,
                slippage_bps=0.0,
                market_impact_bps=0.0,
                execution_time_ms=0,
                rejection_reason="No market data available"
            )
        
        # Get market conditions
        market_condition = self._get_market_condition(symbol, market_tick)
        
        # Simulate execution delay
        delay_ms = np.random.uniform(*self.execution_params["execution_delay_ms"])
        await asyncio.sleep(delay_ms / 1000)
        
        # Determine execution strategy based on order type
        if order.order_type == OrderType.MARKET:
            execution_result = await self._execute_market_order(order, market_tick, market_condition)
        elif order.order_type == OrderType.LIMIT:
            execution_result = await self._execute_limit_order(order, market_tick, market_condition)
        elif order.order_type == OrderType.STOP:
            execution_result = await self._execute_stop_order(order, market_tick, market_condition)
        else:
            execution_result = await self._execute_market_order(order, market_tick, market_condition)
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        execution_result.execution_time_ms = int(execution_time)
        
        return execution_result
    
    async def _execute_market_order(self, order: Order, market_tick, market_condition: MarketCondition) -> ExecutionResult:
        """Execute market order with realistic slippage"""
        
        # Determine base price
        if order.side in [OrderSide.BUY]:
            base_price = market_tick.ask
            price_direction = 1  # Price moves against us
        else:
            base_price = market_tick.bid  
            price_direction = -1
        
        # Calculate realistic slippage
        slippage_bps = self._calculate_slippage(order, market_condition)
        market_impact_bps = self._calculate_market_impact(order, market_condition)
        
        total_impact_bps = slippage_bps + market_impact_bps
        price_impact = (total_impact_bps / 10000) * base_price * price_direction
        
        # Final execution price
        execution_price = base_price + price_impact
        
        # Quality check - reject if impact too high
        if total_impact_bps > 100:  # 1% impact threshold
            return ExecutionResult(
                order_id=str(order.id),
                status=OrderStatus.REJECTED,
                filled_quantity=0.0,
                average_fill_price=0.0,
                total_fill_value=0.0,
                commission=0.0,
                fees=0.0,
                slippage_bps=slippage_bps,
                market_impact_bps=market_impact_bps,
                execution_time_ms=0,
                rejection_reason="Excessive market impact"
            )
        
        # Calculate fills (can be partial in poor conditions)
        fill_ratio = self._calculate_fill_ratio(order, market_condition)
        filled_quantity = order.quantity * fill_ratio
        
        if filled_quantity < 1:  # Minimum fill size
            return ExecutionResult(
                order_id=str(order.id),
                status=OrderStatus.REJECTED,
                filled_quantity=0.0,
                average_fill_price=0.0,
                total_fill_value=0.0,
                commission=0.0,
                fees=0.0,
                slippage_bps=slippage_bps,
                market_impact_bps=market_impact_bps,
                execution_time_ms=0,
                rejection_reason="Insufficient liquidity"
            )
        
        # Calculate costs
        total_value = filled_quantity * execution_price
        commission = self._calculate_commission(order, filled_quantity, execution_price)
        fees = self._calculate_fees(order, total_value)
        
        # Create fills
        fills = [{
            "fill_price": execution_price,
            "fill_quantity": filled_quantity,
            "fill_time": datetime.utcnow(),
            "execution_venue": "PAPER",
            "liquidity_flag": "Remove"
        }]
        
        # Determine final status
        status = OrderStatus.FILLED if fill_ratio >= 0.999 else OrderStatus.PARTIALLY_FILLED
        
        return ExecutionResult(
            order_id=str(order.id),
            status=status,
            filled_quantity=filled_quantity,
            average_fill_price=execution_price,
            total_fill_value=total_value,
            commission=commission,
            fees=fees,
            slippage_bps=slippage_bps,
            market_impact_bps=market_impact_bps,
            execution_time_ms=0,
            fills=fills
        )
    
    async def _execute_limit_order(self, order: Order, market_tick, market_condition: MarketCondition) -> ExecutionResult:
        """Execute limit order with price improvement opportunities"""
        
        # Check if limit price is marketable
        if order.side == OrderSide.BUY and order.limit_price >= market_tick.ask:
            # Marketable buy order - execute at better price
            execution_price = min(order.limit_price, market_tick.ask)
            return await self._execute_immediate_fill(order, execution_price, market_condition)
            
        elif order.side == OrderSide.SELL and order.limit_price <= market_tick.bid:
            # Marketable sell order - execute at better price  
            execution_price = max(order.limit_price, market_tick.bid)
            return await self._execute_immediate_fill(order, execution_price, market_condition)
        
        else:
            # Non-marketable - would go on book
            # For paper trading, simulate probability of fill
            fill_probability = self._calculate_limit_fill_probability(order, market_tick, market_condition)
            
            if np.random.random() < fill_probability:
                # Simulate fill at limit price
                return await self._execute_immediate_fill(order, order.limit_price, market_condition)
            else:
                # Remains pending
                return ExecutionResult(
                    order_id=str(order.id),
                    status=OrderStatus.PENDING,
                    filled_quantity=0.0,
                    average_fill_price=0.0,
                    total_fill_value=0.0,
                    commission=0.0,
                    fees=0.0,
                    slippage_bps=0.0,
                    market_impact_bps=0.0,
                    execution_time_ms=0
                )
    
    async def _execute_stop_order(self, order: Order, market_tick, market_condition: MarketCondition) -> ExecutionResult:
        """Execute stop order when triggered"""
        
        # Check if stop is triggered
        current_price = market_tick.price
        triggered = False
        
        if order.side == OrderSide.BUY and current_price >= order.stop_price:
            triggered = True
        elif order.side == OrderSide.SELL and current_price <= order.stop_price:
            triggered = True
        
        if triggered:
            # Convert to market order
            logger.info(f"🛑 Stop order triggered: {order.id} at {current_price}")
            return await self._execute_market_order(order, market_tick, market_condition)
        else:
            # Remains pending
            return ExecutionResult(
                order_id=str(order.id),
                status=OrderStatus.PENDING,
                filled_quantity=0.0,
                average_fill_price=0.0,
                total_fill_value=0.0,
                commission=0.0,
                fees=0.0,
                slippage_bps=0.0,
                market_impact_bps=0.0,
                execution_time_ms=0
            )
    
    async def _execute_immediate_fill(self, order: Order, price: float, market_condition: MarketCondition) -> ExecutionResult:
        """Execute immediate fill at specified price"""
        
        # Calculate fill ratio based on conditions
        fill_ratio = self._calculate_fill_ratio(order, market_condition)
        filled_quantity = order.quantity * fill_ratio
        
        if filled_quantity < 1:
            return ExecutionResult(
                order_id=str(order.id),
                status=OrderStatus.REJECTED,
                filled_quantity=0.0,
                average_fill_price=0.0,
                total_fill_value=0.0,
                commission=0.0,
                fees=0.0,
                slippage_bps=0.0,
                market_impact_bps=0.0,
                execution_time_ms=0,
                rejection_reason="Insufficient liquidity"
            )
        
        # Calculate costs
        total_value = filled_quantity * price
        commission = self._calculate_commission(order, filled_quantity, price)
        fees = self._calculate_fees(order, total_value)
        
        # Create fills
        fills = [{
            "fill_price": price,
            "fill_quantity": filled_quantity,
            "fill_time": datetime.utcnow(),
            "execution_venue": "PAPER",
            "liquidity_flag": "Remove"
        }]
        
        status = OrderStatus.FILLED if fill_ratio >= 0.999 else OrderStatus.PARTIALLY_FILLED
        
        return ExecutionResult(
            order_id=str(order.id),
            status=status,
            filled_quantity=filled_quantity,
            average_fill_price=price,
            total_fill_value=total_value,
            commission=commission,
            fees=fees,
            slippage_bps=0.0,
            market_impact_bps=0.0,
            execution_time_ms=0,
            fills=fills
        )
    
    def _get_market_condition(self, symbol: str, market_tick) -> MarketCondition:
        """Calculate current market conditions for symbol"""
        
        # Get or create market condition
        if symbol not in self.market_conditions:
            # Initialize with defaults
            self.market_conditions[symbol] = MarketCondition(
                volatility=0.20,  # 20% annualized
                liquidity_score=0.8,
                spread_bps=5.0,
                volume_ratio=1.0,
                trend_strength=0.0
            )
        
        condition = self.market_conditions[symbol]
        
        # Update based on current market data
        spread = market_tick.ask - market_tick.bid
        spread_bps = (spread / market_tick.price) * 10000
        condition.spread_bps = spread_bps
        
        # Estimate volatility from price movement
        volatility_estimate = abs(market_tick.change_percent / 100) * np.sqrt(252)  # Annualized
        condition.volatility = condition.volatility * 0.95 + volatility_estimate * 0.05  # EMA
        
        # Volume ratio
        avg_volume = 1000000  # Would calculate from historical data
        condition.volume_ratio = market_tick.volume / avg_volume
        
        # Liquidity score based on volume and spread
        condition.liquidity_score = min(1.0, (market_tick.volume / 1000000) * (10 / spread_bps))
        
        return condition
    
    def _calculate_slippage(self, order: Order, market_condition: MarketCondition) -> float:
        """Calculate realistic slippage in basis points"""
        
        base_slippage = self.execution_params["base_slippage_bps"]
        
        # Adjust for market conditions
        volatility_multiplier = 1 + (market_condition.volatility / 0.20) * 0.5  # Scale by vol
        liquidity_multiplier = 2 - market_condition.liquidity_score  # Lower liquidity = higher slippage
        spread_multiplier = 1 + (market_condition.spread_bps / 10) * 0.1  # Wider spread = more slippage
        
        # Order size impact
        order_value = order.quantity * 100  # Rough estimate
        size_multiplier = 1 + min(order_value / 100000, 2.0)  # Max 3x for large orders
        
        slippage = base_slippage * volatility_multiplier * liquidity_multiplier * spread_multiplier * size_multiplier
        
        return min(slippage, 50.0)  # Cap at 0.5%
    
    def _calculate_market_impact(self, order: Order, market_condition: MarketCondition) -> float:
        """Calculate market impact in basis points"""
        
        # Square root impact model
        order_value = order.quantity * 100  # Rough estimate
        daily_volume = market_condition.volume_ratio * 1000000 * 100  # Estimate daily volume in $
        
        participation_rate = order_value / max(daily_volume, 1000000)  # Prevent division by zero
        impact_bps = self.execution_params["market_impact_factor"] * np.sqrt(participation_rate) * 10000
        
        # Adjust for liquidity
        liquidity_adjustment = 2 - market_condition.liquidity_score
        impact_bps *= liquidity_adjustment
        
        return min(impact_bps, 25.0)  # Cap at 0.25%
    
    def _calculate_fill_ratio(self, order: Order, market_condition: MarketCondition) -> float:
        """Calculate what percentage of order gets filled"""
        
        # Base fill ratio
        base_fill = 1.0
        
        # Adjust for liquidity
        if market_condition.liquidity_score < 0.5:
            base_fill *= 0.8 + (market_condition.liquidity_score * 0.4)
        
        # Adjust for order size
        order_value = order.quantity * 100
        if order_value > 50000:  # Large orders
            base_fill *= max(0.5, 1 - (order_value - 50000) / 500000)
        
        # Add some randomness
        noise = np.random.uniform(0.95, 1.0)
        
        return min(1.0, base_fill * noise)
    
    def _calculate_limit_fill_probability(self, order: Order, market_tick, market_condition: MarketCondition) -> float:
        """Calculate probability of limit order fill"""
        
        # Distance from market
        if order.side == OrderSide.BUY:
            distance = (market_tick.ask - order.limit_price) / market_tick.ask
        else:
            distance = (order.limit_price - market_tick.bid) / market_tick.bid
        
        # Base probability decreases with distance
        base_prob = max(0.01, 0.5 - distance * 10)
        
        # Adjust for volatility (higher vol = higher chance of fill)
        vol_multiplier = 1 + market_condition.volatility * 2
        
        # Adjust for liquidity
        liquidity_multiplier = market_condition.liquidity_score
        
        probability = base_prob * vol_multiplier * liquidity_multiplier
        
        return min(0.8, probability)  # Cap at 80%
    
    def _calculate_commission(self, order: Order, quantity: float, price: float) -> float:
        """Calculate commission for trade"""
        
        # Paper trading has no commissions
        return 0.0
    
    def _calculate_fees(self, order: Order, total_value: float) -> float:
        """Calculate regulatory fees"""
        
        # Paper trading has no fees
        return 0.0
    
    async def _update_order_in_db(self, order: Order, execution_result: ExecutionResult, db_session):
        """Update order in database"""
        
        order.status = execution_result.status
        order.filled_quantity = execution_result.filled_quantity
        order.average_fill_price = execution_result.average_fill_price
        order.commission = execution_result.commission
        order.fees = execution_result.fees
        
        if execution_result.status == OrderStatus.FILLED:
            order.filled_at = datetime.utcnow()
        elif execution_result.status == OrderStatus.REJECTED:
            order.cancelled_at = datetime.utcnow()
        
        # Add order fills
        for fill_data in execution_result.fills:
            order_fill = OrderFill(
                order_id=order.id,
                fill_price=fill_data["fill_price"],
                fill_quantity=fill_data["fill_quantity"],
                fill_time=fill_data["fill_time"],
                venue=fill_data["execution_venue"],
                liquidity_flag=fill_data["liquidity_flag"],
                commission=execution_result.commission,
                fees=execution_result.fees
            )
            db_session.add(order_fill)
        
        db_session.commit()
    
    async def _update_position(self, order: Order, execution_result: ExecutionResult, db_session):
        """Update or create position"""
        
        # Find existing position
        position = db_session.query(Position).filter(
            Position.account_id == order.account_id,
            Position.asset_id == order.asset_id
        ).first()
        
        filled_qty = execution_result.filled_quantity
        avg_price = execution_result.average_fill_price
        
        if order.side == OrderSide.SELL:
            filled_qty = -filled_qty
        
        if position:
            # Update existing position
            new_quantity = position.quantity + filled_qty
            
            if new_quantity == 0:
                # Position closed
                db_session.delete(position)
            else:
                # Update position
                if (position.quantity > 0 and filled_qty > 0) or (position.quantity < 0 and filled_qty < 0):
                    # Same side - update average price
                    total_cost = (position.quantity * position.average_price) + (filled_qty * avg_price)
                    position.average_price = total_cost / new_quantity
                
                position.quantity = new_quantity
                position.updated_at = datetime.utcnow()
                
                # Update market values
                current_price = market_data_stream.get_latest_tick(order.asset.symbol)
                if current_price:
                    position.market_price = current_price.price
                    position.market_value = position.quantity * current_price.price
                    position.unrealized_pnl = (current_price.price - position.average_price) * position.quantity
                    position.unrealized_pnl_percent = (position.unrealized_pnl / abs(position.quantity * position.average_price)) * 100
        else:
            # Create new position
            current_price = market_data_stream.get_latest_tick(order.asset.symbol)
            market_price = current_price.price if current_price else avg_price
            
            position = Position(
                account_id=order.account_id,
                asset_id=order.asset_id,
                quantity=filled_qty,
                average_price=avg_price,
                market_price=market_price,
                market_value=filled_qty * market_price,
                cost_basis=abs(filled_qty) * avg_price,
                unrealized_pnl=(market_price - avg_price) * filled_qty,
                unrealized_pnl_percent=((market_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0,
                opened_at=datetime.utcnow()
            )
            db_session.add(position)
        
        db_session.commit()
    
    async def _record_transaction(self, order: Order, execution_result: ExecutionResult, db_session):
        """Record transaction in account"""
        
        transaction = Transaction(
            account_id=order.account_id,
            transaction_type="TRADE",
            amount=-execution_result.total_fill_value if order.side == OrderSide.BUY else execution_result.total_fill_value,
            description=f"{order.side.value} {execution_result.filled_quantity} {order.asset.symbol} @ ${execution_result.average_fill_price:.2f}",
            reference_id=str(order.id),
            asset_id=order.asset_id,
            quantity=execution_result.filled_quantity if order.side == OrderSide.BUY else -execution_result.filled_quantity,
            price=execution_result.average_fill_price,
            transaction_date=datetime.utcnow(),
            settlement_date=datetime.utcnow() + timedelta(days=1)  # T+1 settlement
        )
        
        db_session.add(transaction)
        
        # Update account balances
        account = db_session.query(Account).filter(Account.id == order.account_id).first()
        if account:
            if order.side == OrderSide.BUY:
                # Decrease cash, increase position value
                total_cost = execution_result.total_fill_value + execution_result.commission + execution_result.fees
                account.cash_balance -= total_cost
            else:
                # Increase cash, decrease position value
                total_proceeds = execution_result.total_fill_value - execution_result.commission - execution_result.fees
                account.cash_balance += total_proceeds
            
            transaction.cash_balance_after = account.cash_balance
        
        db_session.commit()
    
    async def _notify_order_update(self, order: Order, status: str):
        """Notify user of order update via WebSocket"""
        
        try:
            # Get user ID from account
            user_id = str(order.account.user_id)
            
            # Send order update notification
            await websocket_manager.broadcast_order_update(user_id, {
                "order_id": str(order.id),
                "symbol": order.asset.symbol,
                "status": status,
                "filled_quantity": order.filled_quantity,
                "average_fill_price": order.average_fill_price,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"❌ Failed to notify order update: {e}")
    
    async def _market_condition_updater(self):
        """Update market conditions periodically"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                # Update conditions for active symbols
                for symbol in self.market_conditions.keys():
                    market_tick = market_data_stream.get_latest_tick(symbol)
                    if market_tick:
                        self._get_market_condition(symbol, market_tick)
                        
            except Exception as e:
                logger.error(f"❌ Market condition update error: {e}")
    
    async def _performance_monitor(self):
        """Monitor execution performance"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes
                
                if self.execution_stats["total_orders"] > 0:
                    fill_rate = (self.execution_stats["filled_orders"] / self.execution_stats["total_orders"]) * 100
                    
                    logger.info(
                        f"📊 Paper Trading Stats - "
                        f"Orders: {self.execution_stats['total_orders']}, "
                        f"Fill Rate: {fill_rate:.1f}%, "
                        f"Volume: ${self.execution_stats['total_volume']:,.0f}, "
                        f"Avg Slippage: {self.execution_stats['average_slippage']:.1f}bps"
                    )
                    
            except Exception as e:
                logger.error(f"❌ Performance monitoring error: {e}")
    
    def _update_execution_stats(self, execution_result: ExecutionResult):
        """Update execution statistics"""
        
        if execution_result.status == OrderStatus.FILLED:
            self.execution_stats["filled_orders"] += 1
            self.execution_stats["total_volume"] += execution_result.total_fill_value
            
            # Update average slippage
            current_avg = self.execution_stats["average_slippage"]
            new_slippage = execution_result.slippage_bps
            count = self.execution_stats["filled_orders"]
            
            self.execution_stats["average_slippage"] = (current_avg * (count - 1) + new_slippage) / count
            
        elif execution_result.status == OrderStatus.REJECTED:
            self.execution_stats["rejected_orders"] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        
        total_orders = self.execution_stats["total_orders"]
        filled_orders = self.execution_stats["filled_orders"]
        
        return {
            "total_orders": total_orders,
            "filled_orders": filled_orders,
            "rejected_orders": self.execution_stats["rejected_orders"],
            "pending_orders": len(self.pending_orders),
            "fill_rate": (filled_orders / max(total_orders, 1)) * 100,
            "total_volume": self.execution_stats["total_volume"],
            "average_slippage_bps": self.execution_stats["average_slippage"],
            "market_conditions": {
                symbol: {
                    "volatility": condition.volatility,
                    "liquidity_score": condition.liquidity_score,
                    "spread_bps": condition.spread_bps
                }
                for symbol, condition in self.market_conditions.items()
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown paper trading engine"""
        
        logger.info("🛑 Shutting down paper trading engine...")
        
        # Cancel all pending orders
        for order_id in list(self.pending_orders.keys()):
            try:
                await self.cancel_order(order_id, None)
            except:
                pass
        
        logger.info("✅ Paper trading engine shutdown complete")

# Global paper trading engine instance
paper_trading_engine = RealisticPaperTradingEngine()