"""
⚡ ADVANCED ORDER MANAGEMENT SYSTEM - INSTITUTIONAL GRADE
Complete order lifecycle management with smart routing and execution algorithms
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import uuid
from collections import defaultdict, deque

from ..models.trading_models import (
    Order, OrderStatus, OrderType, OrderSide, Account, Asset, User
)
from ..core.paper_trading_engine import paper_trading_engine
from ..core.risk_manager import risk_manager
from ..core.websocket_manager import websocket_manager
from .market_data_stream import market_data_stream

logger = logging.getLogger(__name__)

class ExecutionAlgorithm(Enum):
    IMMEDIATE = "immediate"      # Execute immediately at market
    TWAP = "twap"               # Time-Weighted Average Price
    VWAP = "vwap"               # Volume-Weighted Average Price
    ICEBERG = "iceberg"         # Hide large orders
    SMART_ROUTING = "smart_routing"  # Intelligent routing
    DARK_POOL = "dark_pool"     # Dark pool execution

class OrderPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class ExecutionInstruction:
    algorithm: ExecutionAlgorithm
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participation_rate: float = 0.20  # Max 20% of volume
    slice_size: int = 100  # Order slice size
    min_fill_size: int = 1  # Minimum fill size
    max_spread_bps: float = 50.0  # Max spread in basis points
    allow_partial_fills: bool = True
    iceberg_visible_size: int = 100  # For iceberg orders
    dark_pool_preference: bool = False

@dataclass
class OrderMetrics:
    order_id: str
    submission_time: datetime
    first_fill_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    total_execution_time_ms: int = 0
    average_slippage_bps: float = 0.0
    implementation_shortfall: float = 0.0  # Cost vs benchmark
    fill_rate: float = 0.0  # Percentage filled
    venue_breakdown: Dict[str, float] = field(default_factory=dict)
    algorithm_performance: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SmartRouting:
    primary_venue: str
    backup_venues: List[str]
    routing_logic: str  # "price_improvement", "liquidity", "speed"
    max_venue_concentration: float = 0.60  # Max 60% to single venue
    min_improvement_bps: float = 1.0  # Minimum price improvement required

class AdvancedOrderManager:
    """Professional order management with smart routing and algorithms"""
    
    def __init__(self):
        self.active_orders: Dict[str, Order] = {}
        self.order_queue = asyncio.PriorityQueue()
        self.execution_algorithms: Dict[str, Any] = {}
        self.order_metrics: Dict[str, OrderMetrics] = {}
        
        # Execution venues and routing
        self.execution_venues = {
            "NASDAQ": {"latency_ms": 1, "fee_per_share": 0.0, "liquidity_score": 0.95},
            "NYSE": {"latency_ms": 2, "fee_per_share": 0.0, "liquidity_score": 0.90},
            "IEX": {"latency_ms": 3, "fee_per_share": 0.0, "liquidity_score": 0.85},
            "CBSX": {"latency_ms": 2, "fee_per_share": 0.0, "liquidity_score": 0.80},
            "PAPER": {"latency_ms": 50, "fee_per_share": 0.0, "liquidity_score": 1.0}
        }
        
        # Algorithm configurations
        self.algorithm_configs = {
            ExecutionAlgorithm.TWAP: {
                "min_duration_minutes": 1,
                "max_duration_minutes": 480,
                "slice_interval_seconds": 30
            },
            ExecutionAlgorithm.VWAP: {
                "lookback_days": 20,
                "volume_participation_limit": 0.25,
                "slice_interval_seconds": 60
            },
            ExecutionAlgorithm.ICEBERG: {
                "visible_ratio": 0.10,  # Show 10% of order
                "refresh_threshold": 0.25,
                "price_improvement_bps": 1.0
            }
        }
        
        # Performance tracking
        self.execution_stats = {
            "orders_submitted": 0,
            "orders_executed": 0,
            "orders_cancelled": 0,
            "orders_rejected": 0,
            "average_execution_time_ms": 0.0,
            "average_slippage_bps": 0.0,
            "fill_rate": 0.0,
            "venue_utilization": defaultdict(int)
        }
        
        # Market connectivity
        self.venue_connections = {}
        self.market_center_status = defaultdict(bool)
        
        # Start background tasks only if an event loop is running
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._order_processor())
            loop.create_task(self._algorithm_engine())
            loop.create_task(self._market_monitor())
            loop.create_task(self._performance_analyzer())
        except RuntimeError:
            # No running loop during import (e.g., tests). Start on app startup.
            pass
    
    async def submit_order(self, order: Order, db_session, 
                          execution_instruction: Optional[ExecutionInstruction] = None,
                          priority: OrderPriority = OrderPriority.NORMAL) -> Dict[str, Any]:
        """Submit order for execution with advanced routing"""
        
        order_id = str(order.id)
        logger.info(f"📋 Order submitted: {order_id} - {order.side.value} {order.quantity} {order.asset.symbol}")
        
        # Create order metrics tracking
        self.order_metrics[order_id] = OrderMetrics(
            order_id=order_id,
            submission_time=datetime.utcnow()
        )
        
        # Set default execution instruction
        if not execution_instruction:
            execution_instruction = self._get_default_execution_instruction(order)
        
        # Pre-execution risk check
        risk_check = await risk_manager.validate_order(
            db_session.query(Account).filter(Account.id == order.account_id).first(),
            order,
            db_session
        )
        
        if not risk_check.approved:
            order.status = OrderStatus.REJECTED
            db_session.commit()
            
            self.execution_stats["orders_rejected"] += 1
            
            # Notify rejection
            await self._notify_order_status(order, "rejected", risk_check.reason)
            
            return {
                "order_id": order_id,
                "status": "rejected",
                "reason": risk_check.reason,
                "risk_warnings": risk_check.warnings
            }
        
        # Add to active orders
        self.active_orders[order_id] = order
        
        # Queue for processing with priority
        priority_score = priority.value * 1000 + int(datetime.utcnow().timestamp())
        await self.order_queue.put((priority_score, order_id, order, execution_instruction, db_session))
        
        self.execution_stats["orders_submitted"] += 1
        
        # Immediate confirmation
        await self._notify_order_status(order, "pending", "Order queued for execution")
        
        return {
            "order_id": order_id,
            "status": "pending",
            "execution_algorithm": execution_instruction.algorithm.value,
            "estimated_completion": self._estimate_completion_time(order, execution_instruction),
            "risk_score": risk_check.risk_score
        }
    
    async def cancel_order(self, order_id: str, db_session) -> Dict[str, Any]:
        """Cancel active order"""
        
        if order_id not in self.active_orders:
            return {"success": False, "reason": "Order not found or already completed"}
        
        order = self.active_orders[order_id]
        
        # Attempt cancellation
        if order.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]:
            # For paper trading, cancel immediately
            success = await paper_trading_engine.cancel_order(order_id, db_session)
            
            if success:
                order.status = OrderStatus.CANCELLED
                order.cancelled_at = datetime.utcnow()
                db_session.commit()
                
                # Update metrics
                if order_id in self.order_metrics:
                    metrics = self.order_metrics[order_id]
                    metrics.completion_time = datetime.utcnow()
                    metrics.total_execution_time_ms = int(
                        (metrics.completion_time - metrics.submission_time).total_seconds() * 1000
                    )
                
                # Remove from active orders
                del self.active_orders[order_id]
                
                # Update stats
                self.execution_stats["orders_cancelled"] += 1
                
                # Notify cancellation
                await self._notify_order_status(order, "cancelled", "Order cancelled by user")
                
                logger.info(f"✅ Order cancelled: {order_id}")
                
                return {"success": True, "status": "cancelled"}
            else:
                return {"success": False, "reason": "Failed to cancel order"}
        else:
            return {"success": False, "reason": f"Cannot cancel order in {order.status.value} status"}
    
    async def modify_order(self, order_id: str, new_quantity: Optional[float] = None,
                          new_price: Optional[float] = None, db_session = None) -> Dict[str, Any]:
        """Modify active order"""
        
        if order_id not in self.active_orders:
            return {"success": False, "reason": "Order not found"}
        
        order = self.active_orders[order_id]
        
        if order.status != OrderStatus.PENDING:
            return {"success": False, "reason": "Can only modify pending orders"}
        
        # Update order parameters
        original_quantity = order.quantity
        original_price = order.limit_price
        
        if new_quantity is not None:
            order.quantity = new_quantity
            order.remaining_quantity = new_quantity - order.filled_quantity
        
        if new_price is not None and order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            order.limit_price = new_price
        
        db_session.commit()
        
        # Notify modification
        await self._notify_order_status(order, "modified", 
            f"Order modified - Qty: {original_quantity}->{order.quantity}, Price: {original_price}->{order.limit_price}")
        
        logger.info(f"📝 Order modified: {order_id}")
        
        return {
            "success": True,
            "status": "modified",
            "new_quantity": order.quantity,
            "new_price": order.limit_price
        }
    
    async def execute_order(self, order_id: str, db_session) -> Dict[str, Any]:
        """Execute order (called by background processor)"""
        
        if order_id not in self.active_orders:
            return {"success": False, "reason": "Order not found"}
        
        order = self.active_orders[order_id]
        
        try:
            # For paper trading, route to paper trading engine
            execution_result = await paper_trading_engine.submit_order(order, db_session)
            
            # Update order metrics
            if order_id in self.order_metrics:
                metrics = self.order_metrics[order_id]
                
                if execution_result.status == OrderStatus.FILLED:
                    metrics.completion_time = datetime.utcnow()
                    metrics.fill_rate = 1.0
                    
                    if not metrics.first_fill_time:
                        metrics.first_fill_time = datetime.utcnow()
                    
                    metrics.total_execution_time_ms = int(
                        (metrics.completion_time - metrics.submission_time).total_seconds() * 1000
                    )
                    
                    metrics.average_slippage_bps = execution_result.slippage_bps
                    metrics.venue_breakdown["PAPER"] = 1.0
                    
                    # Remove from active orders
                    del self.active_orders[order_id]
                    
                    # Update stats
                    self.execution_stats["orders_executed"] += 1
                    self._update_execution_stats(execution_result)
            
            return {
                "success": True,
                "execution_result": execution_result,
                "metrics": self.order_metrics.get(order_id)
            }
            
        except Exception as e:
            logger.error(f"❌ Order execution error: {e}")
            return {"success": False, "reason": str(e)}
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get comprehensive order status"""
        
        if order_id not in self.active_orders and order_id not in self.order_metrics:
            return {"error": "Order not found"}
        
        # Get order (from active or database)
        order = self.active_orders.get(order_id)
        metrics = self.order_metrics.get(order_id)
        
        status_info = {
            "order_id": order_id,
            "status": order.status.value if order else "unknown",
            "filled_quantity": order.filled_quantity if order else 0,
            "remaining_quantity": order.remaining_quantity if order else 0,
            "average_fill_price": order.average_fill_price if order else 0,
        }
        
        if metrics:
            status_info.update({
                "submission_time": metrics.submission_time.isoformat(),
                "execution_time_ms": metrics.total_execution_time_ms,
                "slippage_bps": metrics.average_slippage_bps,
                "fill_rate": metrics.fill_rate,
                "venue_breakdown": metrics.venue_breakdown
            })
        
        return status_info
    
    async def _order_processor(self):
        """Background order processing loop"""
        
        while True:
            try:
                # Get next order from priority queue
                _, order_id, order, execution_instruction, db_session = await self.order_queue.get()
                
                # Check if order still active (might have been cancelled)
                if order_id not in self.active_orders:
                    continue
                
                # Route order based on execution instruction
                if execution_instruction.algorithm == ExecutionAlgorithm.IMMEDIATE:
                    await self._execute_immediate(order, db_session)
                elif execution_instruction.algorithm == ExecutionAlgorithm.TWAP:
                    await self._execute_twap(order, execution_instruction, db_session)
                elif execution_instruction.algorithm == ExecutionAlgorithm.VWAP:
                    await self._execute_vwap(order, execution_instruction, db_session)
                elif execution_instruction.algorithm == ExecutionAlgorithm.ICEBERG:
                    await self._execute_iceberg(order, execution_instruction, db_session)
                elif execution_instruction.algorithm == ExecutionAlgorithm.SMART_ROUTING:
                    await self._execute_smart_routing(order, execution_instruction, db_session)
                else:
                    # Default to immediate execution
                    await self._execute_immediate(order, db_session)
                
            except Exception as e:
                logger.error(f"❌ Order processor error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_immediate(self, order: Order, db_session):
        """Execute order immediately"""
        
        logger.info(f"⚡ Executing immediate: {order.id}")
        result = await self.execute_order(str(order.id), db_session)
        
        if result["success"]:
            await self._notify_order_status(order, "executed", "Order executed immediately")
    
    async def _execute_twap(self, order: Order, instruction: ExecutionInstruction, db_session):
        """Execute Time-Weighted Average Price algorithm"""
        
        logger.info(f"⏰ Executing TWAP: {order.id}")
        
        # Calculate execution parameters
        start_time = instruction.start_time or datetime.utcnow()
        end_time = instruction.end_time or (start_time + timedelta(minutes=30))  # Default 30 minutes
        duration_seconds = (end_time - start_time).total_seconds()
        
        config = self.algorithm_configs[ExecutionAlgorithm.TWAP]
        slice_interval = config["slice_interval_seconds"]
        num_slices = max(1, int(duration_seconds / slice_interval))
        slice_size = max(1, int(order.quantity / num_slices))
        
        executed_quantity = 0
        slice_count = 0
        
        while executed_quantity < order.quantity and slice_count < num_slices:
            remaining_quantity = order.quantity - executed_quantity
            current_slice_size = min(slice_size, remaining_quantity)
            
            # Create child order for slice
            slice_order = Order(
                account_id=order.account_id,
                asset_id=order.asset_id,
                order_type=OrderType.MARKET,  # Execute slices as market orders
                side=order.side,
                quantity=current_slice_size,
                parent_order_id=order.id,
                client_order_id=f"{order.client_order_id}_slice_{slice_count}",
                submitted_at=datetime.utcnow()
            )
            
            # Execute slice
            execution_result = await paper_trading_engine.submit_order(slice_order, db_session)
            
            if execution_result.status == OrderStatus.FILLED:
                executed_quantity += execution_result.filled_quantity
                
                # Update parent order
                order.filled_quantity += execution_result.filled_quantity
                order.remaining_quantity = order.quantity - order.filled_quantity
                
                # Update average fill price
                if order.average_fill_price is None:
                    order.average_fill_price = execution_result.average_fill_price
                else:
                    total_value = (order.filled_quantity - execution_result.filled_quantity) * order.average_fill_price
                    total_value += execution_result.filled_quantity * execution_result.average_fill_price
                    order.average_fill_price = total_value / order.filled_quantity
                
                await self._notify_order_status(order, "partially_filled", f"TWAP slice {slice_count + 1} completed")
            
            slice_count += 1
            
            # Wait for next slice (unless it's the last one)
            if slice_count < num_slices and executed_quantity < order.quantity:
                await asyncio.sleep(slice_interval)
        
        # Mark order as completed
        if order.filled_quantity >= order.quantity * 0.99:  # Allow for rounding
            order.status = OrderStatus.FILLED
            order.filled_at = datetime.utcnow()
            await self._notify_order_status(order, "filled", f"TWAP execution completed")
        else:
            order.status = OrderStatus.PARTIALLY_FILLED
            await self._notify_order_status(order, "partially_filled", f"TWAP execution completed with partial fill")
        
        db_session.commit()
        logger.info(f"✅ TWAP execution completed: {order.id} - {order.filled_quantity}/{order.quantity} filled")
    
    async def _execute_vwap(self, order: Order, instruction: ExecutionInstruction, db_session):
        """Execute Volume-Weighted Average Price algorithm"""
        
        logger.info(f"📊 Executing VWAP: {order.id}")
        
        # Simplified VWAP implementation
        # In practice, would analyze historical volume patterns
        
        # Get current market data
        market_tick = market_data_stream.get_latest_tick(order.asset.symbol)
        if not market_tick:
            await self._execute_immediate(order, db_session)
            return
        
        # Estimate participation rate
        participation_rate = min(instruction.participation_rate, 0.25)  # Max 25%
        estimated_daily_volume = market_tick.volume * 6.5  # Rough daily estimate
        max_slice_volume = estimated_daily_volume * participation_rate
        
        config = self.algorithm_configs[ExecutionAlgorithm.VWAP]
        slice_interval = config["slice_interval_seconds"]
        
        executed_quantity = 0
        total_slices = max(1, int(order.quantity * 100 / max_slice_volume))  # Rough estimate
        
        for slice_num in range(total_slices):
            if executed_quantity >= order.quantity:
                break
            
            remaining_quantity = order.quantity - executed_quantity
            slice_size = min(remaining_quantity, max_slice_volume / 100)  # Convert back to shares
            
            # Execute slice similar to TWAP but with volume considerations
            slice_order = Order(
                account_id=order.account_id,
                asset_id=order.asset_id,
                order_type=OrderType.MARKET,
                side=order.side,
                quantity=slice_size,
                parent_order_id=order.id,
                client_order_id=f"{order.client_order_id}_vwap_{slice_num}",
                submitted_at=datetime.utcnow()
            )
            
            execution_result = await paper_trading_engine.submit_order(slice_order, db_session)
            
            if execution_result.status == OrderStatus.FILLED:
                executed_quantity += execution_result.filled_quantity
                order.filled_quantity += execution_result.filled_quantity
                order.remaining_quantity = order.quantity - order.filled_quantity
                
                # Update average price
                if order.average_fill_price is None:
                    order.average_fill_price = execution_result.average_fill_price
                else:
                    total_value = (order.filled_quantity - execution_result.filled_quantity) * order.average_fill_price
                    total_value += execution_result.filled_quantity * execution_result.average_fill_price
                    order.average_fill_price = total_value / order.filled_quantity
            
            # Wait between slices
            await asyncio.sleep(slice_interval)
        
        # Complete order
        order.status = OrderStatus.FILLED if order.filled_quantity >= order.quantity * 0.99 else OrderStatus.PARTIALLY_FILLED
        if order.status == OrderStatus.FILLED:
            order.filled_at = datetime.utcnow()
        
        db_session.commit()
        logger.info(f"✅ VWAP execution completed: {order.id}")
    
    async def _execute_iceberg(self, order: Order, instruction: ExecutionInstruction, db_session):
        """Execute Iceberg algorithm (hide large orders)"""
        
        logger.info(f"🧊 Executing Iceberg: {order.id}")
        
        visible_size = instruction.iceberg_visible_size
        executed_quantity = 0
        
        while executed_quantity < order.quantity:
            remaining_quantity = order.quantity - executed_quantity
            current_visible_size = min(visible_size, remaining_quantity)
            
            # Create visible slice
            slice_order = Order(
                account_id=order.account_id,
                asset_id=order.asset_id,
                order_type=order.order_type,  # Maintain original order type
                side=order.side,
                quantity=current_visible_size,
                limit_price=order.limit_price,
                parent_order_id=order.id,
                client_order_id=f"{order.client_order_id}_iceberg_{executed_quantity}",
                submitted_at=datetime.utcnow()
            )
            
            execution_result = await paper_trading_engine.submit_order(slice_order, db_session)
            
            if execution_result.status == OrderStatus.FILLED:
                executed_quantity += execution_result.filled_quantity
                order.filled_quantity += execution_result.filled_quantity
                order.remaining_quantity = order.quantity - order.filled_quantity
                
                # Update average price
                if order.average_fill_price is None:
                    order.average_fill_price = execution_result.average_fill_price
                else:
                    total_value = (order.filled_quantity - execution_result.filled_quantity) * order.average_fill_price
                    total_value += execution_result.filled_quantity * execution_result.average_fill_price
                    order.average_fill_price = total_value / order.filled_quantity
                
                await self._notify_order_status(order, "partially_filled", f"Iceberg slice completed")
            else:
                # If slice not filled, wait and try again or abort
                break
            
            # Small delay before next slice
            await asyncio.sleep(1)
        
        # Complete order
        order.status = OrderStatus.FILLED if order.filled_quantity >= order.quantity * 0.99 else OrderStatus.PARTIALLY_FILLED
        if order.status == OrderStatus.FILLED:
            order.filled_at = datetime.utcnow()
        
        db_session.commit()
        logger.info(f"✅ Iceberg execution completed: {order.id}")
    
    async def _execute_smart_routing(self, order: Order, instruction: ExecutionInstruction, db_session):
        """Execute with smart routing across venues"""
        
        logger.info(f"🧠 Executing Smart Routing: {order.id}")
        
        # For paper trading, simulate smart routing by adding slight randomness
        # In practice, would route to actual venues based on liquidity and pricing
        
        # Simulate venue selection
        best_venue = self._select_best_venue(order)
        
        # Route to paper trading engine (representing best venue)
        execution_result = await paper_trading_engine.submit_order(order, db_session)
        
        # Update venue utilization stats
        self.execution_stats["venue_utilization"][best_venue] += 1
        
        # Update order metrics
        order_id = str(order.id)
        if order_id in self.order_metrics:
            self.order_metrics[order_id].venue_breakdown[best_venue] = 1.0
        
        logger.info(f"✅ Smart routing completed: {order.id} -> {best_venue}")
    
    def _select_best_venue(self, order: Order) -> str:
        """Select best execution venue for order"""
        
        # Simplified venue selection logic
        # In practice, would consider:
        # - Real-time liquidity
        # - Price improvement opportunities
        # - Venue fees and rebates
        # - Historical execution quality
        
        # For paper trading, return PAPER venue
        return "PAPER"
    
    def _get_default_execution_instruction(self, order: Order) -> ExecutionInstruction:
        """Get default execution instruction based on order characteristics"""
        
        order_value = order.quantity * 100  # Rough estimate
        
        # Small orders: immediate execution
        if order_value < 10000:  # < $10k
            algorithm = ExecutionAlgorithm.IMMEDIATE
        # Medium orders: TWAP
        elif order_value < 100000:  # < $100k
            algorithm = ExecutionAlgorithm.TWAP
        # Large orders: VWAP or Iceberg
        else:
            algorithm = ExecutionAlgorithm.ICEBERG
        
        return ExecutionInstruction(
            algorithm=algorithm,
            participation_rate=0.15,  # 15% participation rate
            slice_size=min(100, order.quantity // 5),  # 5 slices minimum
            allow_partial_fills=True
        )
    
    def _estimate_completion_time(self, order: Order, instruction: ExecutionInstruction) -> datetime:
        """Estimate order completion time"""
        
        base_time = datetime.utcnow()
        
        if instruction.algorithm == ExecutionAlgorithm.IMMEDIATE:
            return base_time + timedelta(seconds=30)
        elif instruction.algorithm == ExecutionAlgorithm.TWAP:
            return base_time + timedelta(minutes=30)  # Default TWAP duration
        elif instruction.algorithm == ExecutionAlgorithm.VWAP:
            return base_time + timedelta(minutes=60)  # Longer for VWAP
        elif instruction.algorithm == ExecutionAlgorithm.ICEBERG:
            # Estimate based on order size and visible size
            slices = order.quantity / instruction.iceberg_visible_size
            return base_time + timedelta(minutes=slices * 5)  # 5 minutes per slice
        else:
            return base_time + timedelta(minutes=15)  # Default estimate
    
    async def _notify_order_status(self, order: Order, status: str, message: str):
        """Notify order status via WebSocket"""
        
        try:
            # Get user ID from order
            account = order.account
            user_id = str(account.user_id)
            
            # Send notification
            await websocket_manager.broadcast_order_update(user_id, {
                "order_id": str(order.id),
                "symbol": order.asset.symbol,
                "status": status,
                "message": message,
                "filled_quantity": order.filled_quantity or 0,
                "remaining_quantity": order.remaining_quantity or 0,
                "average_fill_price": order.average_fill_price or 0,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to notify order status: {e}")
    
    def _update_execution_stats(self, execution_result):
        """Update execution statistics"""
        
        # Update average execution time
        if execution_result.execution_time_ms > 0:
            current_avg = self.execution_stats["average_execution_time_ms"]
            count = self.execution_stats["orders_executed"]
            new_avg = (current_avg * (count - 1) + execution_result.execution_time_ms) / count
            self.execution_stats["average_execution_time_ms"] = new_avg
        
        # Update average slippage
        if execution_result.slippage_bps > 0:
            current_avg = self.execution_stats["average_slippage_bps"]
            count = self.execution_stats["orders_executed"]
            new_avg = (current_avg * (count - 1) + execution_result.slippage_bps) / count
            self.execution_stats["average_slippage_bps"] = new_avg
        
        # Update fill rate
        filled_orders = self.execution_stats["orders_executed"]
        total_orders = self.execution_stats["orders_submitted"]
        self.execution_stats["fill_rate"] = (filled_orders / max(total_orders, 1)) * 100
    
    async def _algorithm_engine(self):
        """Background algorithm engine for advanced order types"""
        
        while True:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Monitor and manage active algorithm executions
                # This would handle things like:
                # - TWAP timing adjustments
                # - VWAP volume monitoring  
                # - Iceberg refreshing
                # - Smart routing decisions
                
                active_algorithm_orders = [
                    order for order in self.active_orders.values()
                    if order.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
                ]
                
                if active_algorithm_orders:
                    logger.debug(f"🤖 Managing {len(active_algorithm_orders)} algorithm orders")
                
            except Exception as e:
                logger.error(f"❌ Algorithm engine error: {e}")
    
    async def _market_monitor(self):
        """Monitor market conditions for execution optimization"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                # Monitor market conditions that affect execution:
                # - Volatility changes
                # - Liquidity changes
                # - Venue connectivity issues
                # - Unusual market activity
                
                # Update venue status
                for venue in self.execution_venues:
                    # In practice, would ping venues or check connectivity
                    self.market_center_status[venue] = True  # Mock: all venues available
                
            except Exception as e:
                logger.error(f"❌ Market monitor error: {e}")
    
    async def _performance_analyzer(self):
        """Analyze execution performance"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes
                
                # Calculate and report performance metrics
                total_orders = self.execution_stats["orders_submitted"]
                
                if total_orders > 0:
                    logger.info(
                        f"📈 Order Management Stats - "
                        f"Submitted: {total_orders}, "
                        f"Executed: {self.execution_stats['orders_executed']}, "
                        f"Fill Rate: {self.execution_stats['fill_rate']:.1f}%, "
                        f"Avg Execution Time: {self.execution_stats['average_execution_time_ms']:.1f}ms, "
                        f"Avg Slippage: {self.execution_stats['average_slippage_bps']:.1f}bps"
                    )
                
            except Exception as e:
                logger.error(f"❌ Performance analyzer error: {e}")
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        
        return {
            **self.execution_stats,
            "active_orders": len(self.active_orders),
            "venue_utilization": dict(self.execution_stats["venue_utilization"]),
            "market_center_status": dict(self.market_center_status),
            "algorithm_breakdown": {
                algorithm.value: sum(
                    1 for metrics in self.order_metrics.values()
                    if metrics.algorithm_performance.get("algorithm") == algorithm.value
                )
                for algorithm in ExecutionAlgorithm
            }
        }
    
    def get_order_metrics(self, order_id: str) -> Optional[OrderMetrics]:
        """Get detailed metrics for specific order"""
        return self.order_metrics.get(order_id)
    
    def get_active_orders(self) -> List[Dict[str, Any]]:
        """Get list of active orders with status"""
        
        return [
            {
                "order_id": str(order.id),
                "symbol": order.asset.symbol,
                "side": order.side.value,
                "quantity": order.quantity,
                "filled_quantity": order.filled_quantity or 0,
                "remaining_quantity": order.remaining_quantity or order.quantity,
                "status": order.status.value,
                "order_type": order.order_type.value,
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None
            }
            for order in self.active_orders.values()
        ]
    
    async def shutdown(self):
        """Gracefully shutdown order manager"""
        
        logger.info("🛑 Shutting down order manager...")
        
        # Cancel all active orders
        for order_id in list(self.active_orders.keys()):
            try:
                await self.cancel_order(order_id, None)
            except:
                pass
        
        # Clear data structures
        self.active_orders.clear()
        self.order_metrics.clear()
        
        logger.info("✅ Order manager shutdown complete")

# Global order manager instance
order_manager = AdvancedOrderManager()