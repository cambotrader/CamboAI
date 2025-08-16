from __future__ import annotations
from typing import Dict, List, Any, Optional
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Store active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Store subscriptions by topic
        self.subscriptions: Dict[str, List[str]] = {}  # topic -> [connection_ids]
        # Store connection metadata
        self.connection_info: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, connection_id: Optional[str] = None) -> str:
        """Accept WebSocket connection and return connection ID."""
        await websocket.accept()
        
        if not connection_id:
            connection_id = str(uuid.uuid4())
            
        self.active_connections[connection_id] = websocket
        self.connection_info[connection_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "subscriptions": []
        }
        
        logger.info(f"WebSocket connected: {connection_id}")
        return connection_id

    def disconnect(self, connection_id: str):
        """Remove connection and clean up subscriptions."""
        if connection_id in self.active_connections:
            # Remove from all subscriptions
            for topic, subscribers in self.subscriptions.items():
                if connection_id in subscribers:
                    subscribers.remove(connection_id)
                    
            # Clean up empty subscription topics
            self.subscriptions = {
                topic: subs for topic, subs in self.subscriptions.items() 
                if len(subs) > 0
            }
            
            # Remove connection
            del self.active_connections[connection_id]
            if connection_id in self.connection_info:
                del self.connection_info[connection_id]
                
            logger.info(f"WebSocket disconnected: {connection_id}")

    async def subscribe(self, connection_id: str, topic: str):
        """Subscribe connection to a topic."""
        if connection_id not in self.active_connections:
            return False
            
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
            
        if connection_id not in self.subscriptions[topic]:
            self.subscriptions[topic].append(connection_id)
            self.connection_info[connection_id]["subscriptions"].append(topic)
            
        logger.info(f"Subscribed {connection_id} to {topic}")
        return True

    async def unsubscribe(self, connection_id: str, topic: str):
        """Unsubscribe connection from a topic."""
        if topic in self.subscriptions and connection_id in self.subscriptions[topic]:
            self.subscriptions[topic].remove(connection_id)
            if connection_id in self.connection_info:
                if topic in self.connection_info[connection_id]["subscriptions"]:
                    self.connection_info[connection_id]["subscriptions"].remove(topic)
                    
        logger.info(f"Unsubscribed {connection_id} from {topic}")

    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
                return False
        return False

    async def broadcast_to_topic(self, message: dict, topic: str):
        """Broadcast message to all subscribers of a topic."""
        if topic not in self.subscriptions:
            return 0
            
        sent_count = 0
        failed_connections = []
        
        for connection_id in self.subscriptions[topic]:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_text(json.dumps(message))
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to {connection_id}: {e}")
                    failed_connections.append(connection_id)
                    
        # Clean up failed connections
        for conn_id in failed_connections:
            self.disconnect(conn_id)
            
        logger.info(f"Broadcast to topic '{topic}': {sent_count} messages sent")
        return sent_count

    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all active connections."""
        sent_count = 0
        failed_connections = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                failed_connections.append(connection_id)
                
        # Clean up failed connections
        for conn_id in failed_connections:
            self.disconnect(conn_id)
            
        logger.info(f"Broadcast to all: {sent_count} messages sent")
        return sent_count

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "active_topics": len(self.subscriptions),
            "topic_stats": {
                topic: len(subscribers) 
                for topic, subscribers in self.subscriptions.items()
            },
            "connections": [
                {
                    "id": conn_id[:8] + "...",  # Truncate for privacy
                    "connected_at": info["connected_at"],
                    "subscriptions": info["subscriptions"]
                }
                for conn_id, info in self.connection_info.items()
            ]
        }

# Global connection manager instance
manager = ConnectionManager()

# Real-time data simulation and broadcasting
class RealTimeDataBroadcaster:
    """Handles real-time data broadcasting to WebSocket clients."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.is_running = False
        
    async def start_broadcasting(self):
        """Start background task for real-time data broadcasting."""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting real-time data broadcaster")
        
        # Start background tasks
        asyncio.create_task(self.broadcast_price_updates())
        asyncio.create_task(self.broadcast_alert_checks())
        asyncio.create_task(self.broadcast_market_news())
        
    async def stop_broadcasting(self):
        """Stop broadcasting."""
        self.is_running = False
        logger.info("Stopped real-time data broadcaster")
        
    async def broadcast_price_updates(self):
        """Simulate real-time price updates."""
        import random
        
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'BTC/USD', 'ETH/USD']
        prices = {symbol: 100 + random.uniform(-50, 150) for symbol in symbols}
        
        while self.is_running:
            try:
                # Simulate price changes
                for symbol in symbols:
                    change_pct = random.uniform(-0.02, 0.02)  # ±2% change
                    prices[symbol] *= (1 + change_pct)
                    
                    message = {
                        "type": "price_update",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "symbol": symbol,
                            "price": round(prices[symbol], 2),
                            "change": round(change_pct * 100, 2),
                            "volume": random.randint(100000, 5000000)
                        }
                    }
                    
                    # Broadcast to symbol-specific topic
                    await self.manager.broadcast_to_topic(message, f"prices_{symbol}")
                    # Also broadcast to general prices topic
                    await self.manager.broadcast_to_topic(message, "prices")
                    
                await asyncio.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in price updates: {e}")
                await asyncio.sleep(5)
                
    async def broadcast_alert_checks(self):
        """Periodically check and broadcast triggered alerts."""
        while self.is_running:
            try:
                # Import here to avoid circular imports
                from app.services import alerts_service
                
                # Run alert evaluation
                result = await alerts_service.evaluate_once()
                
                if result.get("triggered"):
                    message = {
                        "type": "alerts_triggered",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "alerts": result["triggered"],
                            "count": len(result["triggered"])
                        }
                    }
                    
                    await self.manager.broadcast_to_topic(message, "alerts")
                    
                await asyncio.sleep(30)  # Check alerts every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in alert broadcasting: {e}")
                await asyncio.sleep(60)
                
    async def broadcast_market_news(self):
        """Periodically broadcast market sentiment updates."""
        while self.is_running:
            try:
                # Simulate market sentiment updates
                import random
                
                sentiments = ["🟢 Bullish", "🔴 Bearish", "⚪ Neutral", "🚀 Very Bullish", "📉 Very Bearish"]
                
                message = {
                    "type": "market_sentiment",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "mood": random.choice(sentiments),
                        "score": random.uniform(-1, 1),
                        "confidence": random.uniform(0.5, 0.95),
                        "summary": "AI analysis of recent market news and social sentiment"
                    }
                }
                
                await self.manager.broadcast_to_topic(message, "sentiment")
                await asyncio.sleep(120)  # Update every 2 minutes
                
            except Exception as e:
                logger.error(f"Error in sentiment broadcasting: {e}")
                await asyncio.sleep(300)

# Global broadcaster instance
broadcaster = RealTimeDataBroadcaster(manager)