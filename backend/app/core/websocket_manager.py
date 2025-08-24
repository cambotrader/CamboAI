"""
🌐 REAL-TIME WEBSOCKET MANAGER - ULTRA-LOW LATENCY
Professional-grade WebSocket management for real-time trading data
"""

import asyncio
import json
import uuid
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from fastapi import WebSocket
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class MessageType(Enum):
    # Market Data
    MARKET_TICK = "market_tick"
    LEVEL2_UPDATE = "level2_update"
    TRADE_TICK = "trade_tick"
    
    # Trading Updates
    ORDER_UPDATE = "order_update"
    FILL_UPDATE = "fill_update"
    POSITION_UPDATE = "position_update"
    ACCOUNT_UPDATE = "account_update"
    
    # News and Alerts
    NEWS_ALERT = "news_alert"
    PRICE_ALERT = "price_alert"
    RISK_ALERT = "risk_alert"
    
    # AI Signals
    AI_SIGNAL = "ai_signal"
    STRATEGY_UPDATE = "strategy_update"
    
    # System
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    SUBSCRIPTION_CONFIRMED = "subscription_confirmed"

@dataclass
class WebSocketConnection:
    websocket: WebSocket
    user_id: str
    session_id: str
    subscriptions: Set[str]
    last_heartbeat: datetime
    connection_time: datetime
    message_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0

@dataclass
class MarketTick:
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    change: float
    change_percent: float
    high: float
    low: float
    open: float
    vwap: float

@dataclass
class Level2Update:
    symbol: str
    bids: List[List[float]]  # [price, size, num_orders]
    asks: List[List[float]]  # [price, size, num_orders]
    timestamp: datetime

@dataclass
class OrderUpdate:
    order_id: str
    user_id: str
    symbol: str
    status: str
    filled_quantity: float
    average_fill_price: Optional[float]
    timestamp: datetime

class WebSocketManager:
    """Ultra-fast WebSocket connection manager with Redis pub/sub"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.symbol_subscribers: Dict[str, Set[str]] = defaultdict(set)
        self.message_queue = asyncio.Queue()
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.total_connections = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.start_time = datetime.utcnow()
        
        # Message rate limiting
        self.rate_limits = {
            "market_data": 1000,  # msgs/second per connection
            "order_updates": 100,
            "default": 50
        }
        
        # Subscription limits
        self.max_subscriptions_per_user = 200
        self.max_concurrent_connections = 10000
        
        # Heartbeat settings
        self.heartbeat_interval = 30  # seconds
        self.connection_timeout = 300  # 5 minutes
        
        # Start background tasks only if an event loop is running
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._heartbeat_monitor())
            loop.create_task(self._message_processor())
            loop.create_task(self._performance_monitor())
        except RuntimeError:
            # No running loop during import (e.g., tests). Start these on app startup.
            pass
    
    async def initialize_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection for pub/sub"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
            # Start pub/sub subscriber
            self.pubsub_task = asyncio.create_task(self._redis_subscriber())
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            # Continue without Redis - use local pub/sub only
    
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """Accept new WebSocket connection"""
        
        # Check connection limits
        if len(self.connections) >= self.max_concurrent_connections:
            await websocket.close(code=1008, reason="Server at capacity")
            raise Exception("Connection limit exceeded")
        
        await websocket.accept()
        
        session_id = str(uuid.uuid4())
        connection = WebSocketConnection(
            websocket=websocket,
            user_id=user_id,
            session_id=session_id,
            subscriptions=set(),
            last_heartbeat=datetime.utcnow(),
            connection_time=datetime.utcnow()
        )
        
        self.connections[session_id] = connection
        self.user_connections[user_id].add(session_id)
        self.total_connections += 1
        
        logger.info(f"🔗 WebSocket connected: user={user_id}, session={session_id}")
        
        # Send welcome message
        await self._send_to_connection(session_id, {
            "type": "connected",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "server_time": datetime.utcnow().timestamp()
        })
        
        return session_id
    
    def disconnect(self, session_id: str):
        """Handle WebSocket disconnection"""
        
        if session_id not in self.connections:
            return
        
        connection = self.connections[session_id]
        user_id = connection.user_id
        
        # Remove from subscriptions
        for symbol in connection.subscriptions:
            self.symbol_subscribers[symbol].discard(session_id)
            if not self.symbol_subscribers[symbol]:
                del self.symbol_subscribers[symbol]
        
        # Remove from user connections
        self.user_connections[user_id].discard(session_id)
        if not self.user_connections[user_id]:
            del self.user_connections[user_id]
        
        # Remove connection
        del self.connections[session_id]
        
        logger.info(f"🔌 WebSocket disconnected: user={user_id}, session={session_id}")
    
    async def subscribe_to_symbols(self, user_id: str, symbols: List[str]) -> bool:
        """Subscribe user to market data for symbols"""
        
        user_sessions = self.user_connections.get(user_id, set())
        if not user_sessions:
            return False
        
        # Check subscription limits
        total_subscriptions = sum(
            len(self.connections[session_id].subscriptions) 
            for session_id in user_sessions
        )
        
        if total_subscriptions + len(symbols) > self.max_subscriptions_per_user:
            logger.warning(f"Subscription limit exceeded for user {user_id}")
            return False
        
        # Add subscriptions
        for session_id in user_sessions:
            connection = self.connections[session_id]
            for symbol in symbols:
                symbol = symbol.upper()
                connection.subscriptions.add(symbol)
                self.symbol_subscribers[symbol].add(session_id)
            
            # Confirm subscription
            await self._send_to_connection(session_id, {
                "type": MessageType.SUBSCRIPTION_CONFIRMED.value,
                "symbols": symbols,
                "action": "subscribed",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        logger.info(f"📊 Subscribed user {user_id} to symbols: {symbols}")
        return True
    
    async def unsubscribe_from_symbols(self, user_id: str, symbols: List[str]) -> bool:
        """Unsubscribe user from market data symbols"""
        
        user_sessions = self.user_connections.get(user_id, set())
        if not user_sessions:
            return False
        
        # Remove subscriptions
        for session_id in user_sessions:
            connection = self.connections[session_id]
            for symbol in symbols:
                symbol = symbol.upper()
                connection.subscriptions.discard(symbol)
                self.symbol_subscribers[symbol].discard(session_id)
                
                # Clean up empty symbol subscriptions
                if not self.symbol_subscribers[symbol]:
                    del self.symbol_subscribers[symbol]
            
            # Confirm unsubscription
            await self._send_to_connection(session_id, {
                "type": MessageType.SUBSCRIPTION_CONFIRMED.value,
                "symbols": symbols,
                "action": "unsubscribed",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        logger.info(f"📊 Unsubscribed user {user_id} from symbols: {symbols}")
        return True
    
    async def broadcast_market_tick(self, tick: MarketTick):
        """Broadcast market tick to subscribers"""
        
        subscribers = self.symbol_subscribers.get(tick.symbol, set())
        if not subscribers:
            return
        
        message = {
            "type": MessageType.MARKET_TICK.value,
            "data": asdict(tick)
        }
        
        # Queue message for batch sending
        await self.message_queue.put(("broadcast", subscribers, message))
    
    async def broadcast_level2_update(self, level2: Level2Update):
        """Broadcast Level II order book updates"""
        
        subscribers = self.symbol_subscribers.get(level2.symbol, set())
        if not subscribers:
            return
        
        message = {
            "type": MessageType.LEVEL2_UPDATE.value,
            "data": asdict(level2)
        }
        
        await self.message_queue.put(("broadcast", subscribers, message))
    
    async def broadcast_order_update(self, user_id: str, order_update: Dict[str, Any]):
        """Send order update to specific user"""
        
        user_sessions = self.user_connections.get(user_id, set())
        if not user_sessions:
            return
        
        message = {
            "type": MessageType.ORDER_UPDATE.value,
            "data": order_update
        }
        
        await self.message_queue.put(("user_broadcast", user_sessions, message))
    
    async def broadcast_position_update(self, user_id: str, position_update: Dict[str, Any]):
        """Send position update to specific user"""
        
        user_sessions = self.user_connections.get(user_id, set())
        if not user_sessions:
            return
        
        message = {
            "type": MessageType.POSITION_UPDATE.value,
            "data": position_update
        }
        
        await self.message_queue.put(("user_broadcast", user_sessions, message))
    
    async def broadcast_news_alert(self, alert: Dict[str, Any], target_symbols: List[str] = None):
        """Broadcast news alert to relevant subscribers"""
        
        # If no target symbols, broadcast to all
        if not target_symbols:
            recipients = set(self.connections.keys())
        else:
            recipients = set()
            for symbol in target_symbols:
                recipients.update(self.symbol_subscribers.get(symbol.upper(), set()))
        
        message = {
            "type": MessageType.NEWS_ALERT.value,
            "data": alert
        }
        
        await self.message_queue.put(("broadcast", recipients, message))
    
    async def send_ai_signal(self, user_id: str, signal: Dict[str, Any]):
        """Send AI trading signal to specific user"""
        
        user_sessions = self.user_connections.get(user_id, set())
        if not user_sessions:
            return
        
        message = {
            "type": MessageType.AI_SIGNAL.value,
            "data": signal
        }
        
        await self.message_queue.put(("user_broadcast", user_sessions, message))
    
    async def send_risk_alert(self, user_id: str, risk_alert: Dict[str, Any]):
        """Send risk management alert to user"""
        
        user_sessions = self.user_connections.get(user_id, set())
        if not user_sessions:
            return
        
        message = {
            "type": MessageType.RISK_ALERT.value,
            "data": risk_alert,
            "urgency": risk_alert.get("severity", "medium")
        }
        
        await self.message_queue.put(("user_broadcast", user_sessions, message))
    
    async def _send_to_connection(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific connection"""
        
        if session_id not in self.connections:
            return False
        
        connection = self.connections[session_id]
        
        try:
            message_json = json.dumps(message, default=str)
            await connection.websocket.send_text(message_json)
            
            # Update metrics
            connection.message_count += 1
            connection.bytes_sent += len(message_json)
            self.messages_sent += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send message to {session_id}: {e}")
            # Connection is broken, clean up
            self.disconnect(session_id)
            return False
    
    async def _message_processor(self):
        """Background task to process message queue"""
        
        batch_size = 100
        batch_timeout = 0.01  # 10ms
        
        while True:
            messages = []
            
            try:
                # Collect messages for batch processing
                timeout = asyncio.wait_for(self.message_queue.get(), timeout=batch_timeout)
                messages.append(await timeout)
                
                # Get additional messages without waiting
                for _ in range(batch_size - 1):
                    try:
                        messages.append(self.message_queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break
                
            except asyncio.TimeoutError:
                # No messages to process
                await asyncio.sleep(0.001)  # 1ms sleep
                continue
            
            # Process batch
            await self._process_message_batch(messages)
    
    async def _process_message_batch(self, messages: List[tuple]):
        """Process a batch of messages efficiently"""
        
        # Group messages by type for optimization
        broadcasts = []
        user_broadcasts = []
        
        for msg_type, recipients, message in messages:
            if msg_type == "broadcast":
                broadcasts.append((recipients, message))
            elif msg_type == "user_broadcast":
                user_broadcasts.append((recipients, message))
        
        # Process broadcasts
        for recipients, message in broadcasts:
            tasks = [
                self._send_to_connection(session_id, message)
                for session_id in recipients
                if session_id in self.connections
            ]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process user broadcasts
        for user_sessions, message in user_broadcasts:
            tasks = [
                self._send_to_connection(session_id, message)
                for session_id in user_sessions
                if session_id in self.connections
            ]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _heartbeat_monitor(self):
        """Monitor connection health with heartbeats"""
        
        while True:
            try:
                current_time = datetime.utcnow()
                stale_connections = []
                
                # Check all connections
                for session_id, connection in self.connections.items():
                    time_since_heartbeat = (current_time - connection.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > self.connection_timeout:
                        stale_connections.append(session_id)
                    elif time_since_heartbeat > self.heartbeat_interval:
                        # Send heartbeat
                        await self._send_to_connection(session_id, {
                            "type": MessageType.HEARTBEAT.value,
                            "timestamp": current_time.isoformat(),
                            "server_time": current_time.timestamp()
                        })
                
                # Clean up stale connections
                for session_id in stale_connections:
                    logger.info(f"💀 Cleaning up stale connection: {session_id}")
                    self.disconnect(session_id)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Heartbeat monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _performance_monitor(self):
        """Monitor and log performance metrics"""
        
        while True:
            try:
                await asyncio.sleep(60)  # Report every minute
                
                current_time = datetime.utcnow()
                uptime = (current_time - self.start_time).total_seconds()
                
                # Calculate rates
                msg_rate = self.messages_sent / max(uptime, 1)
                connection_count = len(self.connections)
                
                # Calculate bandwidth
                total_bytes_sent = sum(conn.bytes_sent for conn in self.connections.values())
                bandwidth_mbps = (total_bytes_sent * 8) / (uptime * 1024 * 1024)
                
                # Log metrics
                logger.info(
                    f"📊 WebSocket Metrics - "
                    f"Connections: {connection_count}, "
                    f"Messages/sec: {msg_rate:.1f}, "
                    f"Bandwidth: {bandwidth_mbps:.2f} Mbps, "
                    f"Subscriptions: {sum(len(subs) for subs in self.symbol_subscribers.values())}"
                )
                
                # Reset counters periodically
                if uptime > 3600:  # Reset every hour
                    self.messages_sent = 0
                    self.start_time = current_time
                    for conn in self.connections.values():
                        conn.bytes_sent = 0
                        conn.bytes_received = 0
                
            except Exception as e:
                logger.error(f"❌ Performance monitor error: {e}")
    
    async def _redis_subscriber(self):
        """Subscribe to Redis pub/sub for distributed messaging"""
        
        if not self.redis_client:
            return
        
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(
                "market_data",
                "order_updates",
                "news_alerts",
                "ai_signals"
            )
            
            logger.info("📡 Redis pub/sub subscriber started")
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await self._handle_redis_message(data)
                    except Exception as e:
                        logger.error(f"❌ Redis message processing error: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Redis subscriber error: {e}")
    
    async def _handle_redis_message(self, data: Dict[str, Any]):
        """Handle incoming Redis pub/sub messages"""
        
        msg_type = data.get("type")
        
        if msg_type == "market_tick":
            tick_data = data.get("data", {})
            tick = MarketTick(**tick_data)
            await self.broadcast_market_tick(tick)
            
        elif msg_type == "order_update":
            user_id = data.get("user_id")
            update_data = data.get("data", {})
            await self.broadcast_order_update(user_id, update_data)
            
        elif msg_type == "news_alert":
            alert_data = data.get("data", {})
            target_symbols = data.get("symbols", [])
            await self.broadcast_news_alert(alert_data, target_symbols)
            
        elif msg_type == "ai_signal":
            user_id = data.get("user_id")
            signal_data = data.get("data", {})
            await self.send_ai_signal(user_id, signal_data)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics"""
        
        current_time = datetime.utcnow()
        uptime = (current_time - self.start_time).total_seconds()
        
        # Connection statistics
        active_connections = len(self.connections)
        total_subscriptions = sum(len(conn.subscriptions) for conn in self.connections.values())
        unique_symbols = len(self.symbol_subscribers)
        
        # Performance metrics
        total_messages = sum(conn.message_count for conn in self.connections.values())
        total_bytes_sent = sum(conn.bytes_sent for conn in self.connections.values())
        
        # Connection distribution
        connections_per_user = {}
        for user_id, sessions in self.user_connections.items():
            connections_per_user[user_id] = len(sessions)
        
        return {
            "server": {
                "uptime_seconds": uptime,
                "start_time": self.start_time.isoformat(),
                "redis_connected": self.redis_client is not None
            },
            "connections": {
                "active": active_connections,
                "total_created": self.total_connections,
                "unique_users": len(self.user_connections),
                "avg_per_user": active_connections / max(len(self.user_connections), 1)
            },
            "subscriptions": {
                "total": total_subscriptions,
                "unique_symbols": unique_symbols,
                "avg_per_connection": total_subscriptions / max(active_connections, 1)
            },
            "performance": {
                "messages_sent": self.messages_sent,
                "total_messages": total_messages,
                "messages_per_second": total_messages / max(uptime, 1),
                "total_bytes_sent": total_bytes_sent,
                "bandwidth_mbps": (total_bytes_sent * 8) / (max(uptime, 1) * 1024 * 1024)
            },
            "top_symbols": [
                {"symbol": symbol, "subscribers": len(subscribers)}
                for symbol, subscribers in sorted(
                    self.symbol_subscribers.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:10]
            ]
        }
    
    async def shutdown(self):
        """Gracefully shutdown WebSocket manager"""
        
        logger.info("🛑 Shutting down WebSocket manager...")
        
        # Close all connections
        for session_id in list(self.connections.keys()):
            connection = self.connections[session_id]
            try:
                await connection.websocket.close()
            except:
                pass
            self.disconnect(session_id)
        
        # Cancel background tasks
        if self.pubsub_task:
            self.pubsub_task.cancel()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("✅ WebSocket manager shutdown complete")

# Global instance
websocket_manager = WebSocketManager()