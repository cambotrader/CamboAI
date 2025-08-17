"""
🌉 FRONTEND INTEGRATION SERVICE - SEAMLESS CONNECTIVITY
Complete integration layer for React/mobile frontend connections
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
from collections import defaultdict

from ..core.websocket_manager import websocket_manager
from ..core.market_data_stream import market_data_stream
from ..core.paper_trading_engine import paper_trading_engine
from ..core.risk_manager import risk_manager
from ..core.order_manager import order_manager
from ..services.crypto.defi_engine import defi_data_aggregator, portfolio_optimizer
from ..services.arbitrage.cross_asset_engine import detection_engine

logger = logging.getLogger(__name__)

class FrontendEventType(Enum):
    # Market Data Events
    MARKET_TICK_UPDATE = "market_tick_update"
    WATCHLIST_UPDATE = "watchlist_update"
    MARKET_STATUS_CHANGE = "market_status_change"
    
    # Trading Events
    ORDER_STATUS_UPDATE = "order_status_update"
    POSITION_UPDATE = "position_update"
    ACCOUNT_BALANCE_UPDATE = "account_balance_update"
    TRADE_EXECUTION = "trade_execution"
    
    # Risk Events
    RISK_ALERT = "risk_alert"
    PORTFOLIO_RISK_UPDATE = "portfolio_risk_update"
    LIMIT_BREACH_WARNING = "limit_breach_warning"
    
    # AI & Analytics Events
    AI_SIGNAL_GENERATED = "ai_signal_generated"
    DEFI_OPPORTUNITY_UPDATE = "defi_opportunity_update"
    ARBITRAGE_OPPORTUNITY = "arbitrage_opportunity"
    STRATEGY_UPDATE = "strategy_update"
    
    # System Events
    SYSTEM_STATUS = "system_status"
    NOTIFICATION = "notification"
    ERROR = "error"

@dataclass
class FrontendMessage:
    event_type: FrontendEventType
    data: Dict[str, Any]
    timestamp: datetime
    user_id: str
    message_id: str
    priority: str = "normal"  # low, normal, high, critical

@dataclass
class UIState:
    user_id: str
    active_page: str = "dashboard"
    selected_symbols: List[str] = None
    chart_timeframe: str = "1h"
    notifications_enabled: bool = True
    theme: str = "dark"
    last_activity: datetime = None
    
    def __post_init__(self):
        if self.selected_symbols is None:
            self.selected_symbols = ["SPY", "QQQ", "AAPL"]
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()

class FrontendIntegrationService:
    """Complete frontend integration and communication service"""
    
    def __init__(self):
        self.connected_users: Dict[str, UIState] = {}
        self.user_subscriptions: Dict[str, Dict[str, bool]] = defaultdict(dict)
        self.message_queue: Dict[str, List[FrontendMessage]] = defaultdict(list)
        
        # Real-time data aggregators
        self.market_data_aggregator = {}
        self.portfolio_summaries: Dict[str, Dict[str, Any]] = {}
        
        # Event handlers
        self.event_handlers = {
            "market_data": self._handle_market_data_event,
            "order_update": self._handle_order_update_event,
            "risk_alert": self._handle_risk_alert_event,
            "ai_signal": self._handle_ai_signal_event,
            "system_notification": self._handle_system_notification
        }
        
        # Performance tracking
        self.integration_stats = {
            "messages_sent": 0,
            "messages_queued": 0,
            "active_connections": 0,
            "event_processing_errors": 0
        }
        
        # Start background services
        asyncio.create_task(self._message_dispatcher())
        asyncio.create_task(self._data_aggregator())
        asyncio.create_task(self._heartbeat_service())
        asyncio.create_task(self._performance_monitor())
    
    async def register_user_connection(self, user_id: str, 
                                     initial_subscriptions: Dict[str, bool] = None) -> Dict[str, Any]:
        """Register new user connection with frontend"""
        
        # Create or update UI state
        if user_id not in self.connected_users:
            self.connected_users[user_id] = UIState(user_id=user_id)
        else:
            self.connected_users[user_id].last_activity = datetime.utcnow()
        
        # Set up subscriptions
        default_subscriptions = {
            "market_data": True,
            "order_updates": True,
            "portfolio_updates": True,
            "risk_alerts": True,
            "ai_signals": False,
            "defi_opportunities": False,
            "system_notifications": True
        }
        
        if initial_subscriptions:
            default_subscriptions.update(initial_subscriptions)
        
        self.user_subscriptions[user_id] = default_subscriptions
        
        # Subscribe to market data for user's symbols
        ui_state = self.connected_users[user_id]
        for symbol in ui_state.selected_symbols:
            await market_data_stream.subscribe_symbol(symbol)
        
        self.integration_stats["active_connections"] += 1
        
        logger.info(f"🔗 User {user_id} connected to frontend integration")
        
        # Send initial data package
        initial_data = await self._get_initial_data_package(user_id)
        
        return {
            "status": "connected",
            "user_id": user_id,
            "subscriptions": self.user_subscriptions[user_id],
            "initial_data": initial_data
        }
    
    async def disconnect_user(self, user_id: str):
        """Handle user disconnection"""
        
        if user_id in self.connected_users:
            del self.connected_users[user_id]
        
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
        
        if user_id in self.message_queue:
            del self.message_queue[user_id]
        
        if user_id in self.portfolio_summaries:
            del self.portfolio_summaries[user_id]
        
        self.integration_stats["active_connections"] = max(0, self.integration_stats["active_connections"] - 1)
        
        logger.info(f"🔌 User {user_id} disconnected from frontend integration")
    
    async def update_user_subscriptions(self, user_id: str, 
                                      subscriptions: Dict[str, bool]) -> Dict[str, Any]:
        """Update user's event subscriptions"""
        
        if user_id not in self.user_subscriptions:
            return {"error": "User not connected"}
        
        # Update subscriptions
        self.user_subscriptions[user_id].update(subscriptions)
        
        # Handle market data subscription changes
        ui_state = self.connected_users.get(user_id)
        if ui_state and subscriptions.get("market_data"):
            for symbol in ui_state.selected_symbols:
                await market_data_stream.subscribe_symbol(symbol)
        
        return {
            "status": "updated",
            "subscriptions": self.user_subscriptions[user_id]
        }
    
    async def update_user_watchlist(self, user_id: str, symbols: List[str]) -> Dict[str, Any]:
        """Update user's watchlist symbols"""
        
        if user_id not in self.connected_users:
            return {"error": "User not connected"}
        
        ui_state = self.connected_users[user_id]
        old_symbols = set(ui_state.selected_symbols)
        new_symbols = set(symbols)
        
        # Subscribe to new symbols
        for symbol in new_symbols - old_symbols:
            await market_data_stream.subscribe_symbol(symbol)
        
        # Unsubscribe from removed symbols (if no other users watching)
        # In practice, would check if other users are subscribed
        
        # Update UI state
        ui_state.selected_symbols = symbols
        ui_state.last_activity = datetime.utcnow()
        
        # Send market data for new symbols
        watchlist_data = []
        for symbol in symbols:
            tick = market_data_stream.get_latest_tick(symbol)
            if tick:
                watchlist_data.append({
                    "symbol": symbol,
                    "price": tick.price,
                    "change": tick.change,
                    "change_percent": tick.change_percent,
                    "volume": tick.volume,
                    "timestamp": tick.timestamp.isoformat()
                })
        
        # Send update to frontend
        await self.send_event_to_user(user_id, FrontendEventType.WATCHLIST_UPDATE, {
            "symbols": symbols,
            "market_data": watchlist_data
        })
        
        return {"status": "updated", "symbols": symbols, "market_data": watchlist_data}
    
    async def send_event_to_user(self, user_id: str, event_type: FrontendEventType, 
                               data: Dict[str, Any], priority: str = "normal") -> bool:
        """Send event to specific user"""
        
        if user_id not in self.connected_users:
            return False
        
        # Check if user is subscribed to this event type
        subscription_key = self._get_subscription_key(event_type)
        if subscription_key and not self.user_subscriptions[user_id].get(subscription_key, True):
            return False
        
        # Create message
        message = FrontendMessage(
            event_type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            message_id=str(uuid.uuid4()),
            priority=priority
        )
        
        # Queue message for delivery
        self.message_queue[user_id].append(message)
        self.integration_stats["messages_queued"] += 1
        
        return True
    
    async def broadcast_event(self, event_type: FrontendEventType, 
                            data: Dict[str, Any], user_filter: Optional[List[str]] = None) -> int:
        """Broadcast event to all connected users (or filtered subset)"""
        
        target_users = user_filter if user_filter else list(self.connected_users.keys())
        sent_count = 0
        
        for user_id in target_users:
            if await self.send_event_to_user(user_id, event_type, data):
                sent_count += 1
        
        return sent_count
    
    async def get_portfolio_summary(self, user_id: str, account_id: str) -> Dict[str, Any]:
        """Get comprehensive portfolio summary for frontend"""
        
        try:
            # Get from cache if available and recent
            cache_key = f"{user_id}_{account_id}"
            cached_summary = self.portfolio_summaries.get(cache_key)
            
            if cached_summary and (datetime.utcnow() - cached_summary["last_updated"]).seconds < 30:
                return cached_summary
            
            # Generate fresh summary
            summary = {
                "account_id": account_id,
                "user_id": user_id,
                "last_updated": datetime.utcnow(),
                "account_summary": await self._get_account_summary(account_id),
                "positions": await self._get_positions_summary(account_id),
                "orders": await self._get_orders_summary(account_id),
                "risk_metrics": await self._get_risk_summary(account_id),
                "performance": await self._get_performance_summary(account_id),
                "alerts": await self._get_active_alerts(account_id)
            }
            
            # Cache summary
            self.portfolio_summaries[cache_key] = summary
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Portfolio summary error for {user_id}: {e}")
            return {"error": "Failed to generate portfolio summary"}
    
    async def get_market_overview(self, user_id: str) -> Dict[str, Any]:
        """Get market overview data for frontend"""
        
        ui_state = self.connected_users.get(user_id)
        if not ui_state:
            return {"error": "User not connected"}
        
        # Get market data for watchlist symbols
        market_overview = {
            "watchlist": [],
            "market_status": "open",  # Would get from market data service
            "indices": [],
            "market_movers": {
                "gainers": [],
                "losers": [],
                "most_active": []
            },
            "news_alerts": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Populate watchlist data
        for symbol in ui_state.selected_symbols:
            tick = market_data_stream.get_latest_tick(symbol)
            if tick:
                market_overview["watchlist"].append({
                    "symbol": symbol,
                    "price": tick.price,
                    "change": tick.change,
                    "change_percent": tick.change_percent,
                    "volume": tick.volume,
                    "high": tick.high,
                    "low": tick.low,
                    "bid": tick.bid,
                    "ask": tick.ask
                })
        
        # Add major indices
        for index_symbol in ["SPY", "QQQ", "DIA", "IWM"]:
            tick = market_data_stream.get_latest_tick(index_symbol)
            if tick:
                market_overview["indices"].append({
                    "symbol": index_symbol,
                    "price": tick.price,
                    "change": tick.change,
                    "change_percent": tick.change_percent
                })
        
        return market_overview
    
    async def get_ai_insights(self, user_id: str) -> Dict[str, Any]:
        """Get AI-powered insights for frontend"""
        
        if not self.user_subscriptions.get(user_id, {}).get("ai_signals", False):
            return {"error": "AI signals not enabled for user"}
        
        # Mock AI insights (would integrate with actual AI services)
        insights = {
            "market_sentiment": {
                "overall": "bullish",
                "score": 0.65,  # -1 to 1
                "confidence": 0.78
            },
            "trade_recommendations": [
                {
                    "symbol": "AAPL",
                    "action": "buy",
                    "confidence": 0.82,
                    "target_price": 185.0,
                    "reasoning": "Strong technical indicators and earnings momentum"
                }
            ],
            "risk_warnings": [
                {
                    "type": "volatility_spike",
                    "symbol": "TSLA",
                    "probability": 0.35,
                    "impact": "high"
                }
            ],
            "opportunities": {
                "options_plays": [],
                "arbitrage": [],
                "defi_yields": []
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return insights
    
    async def get_defi_opportunities(self, user_id: str) -> Dict[str, Any]:
        """Get DeFi opportunities for frontend"""
        
        if not self.user_subscriptions.get(user_id, {}).get("defi_opportunities", False):
            return {"error": "DeFi opportunities not enabled for user"}
        
        try:
            # Get fresh DeFi data
            defi_data = await defi_data_aggregator.aggregate_all_data()
            
            # Format for frontend
            frontend_data = {
                "yield_opportunities": defi_data.get("yield_opportunities", [])[:10],  # Top 10
                "market_overview": defi_data.get("market_overview", {}),
                "trending_protocols": defi_data.get("protocol_analysis", [])[:5],
                "risk_analysis": defi_data.get("risk_metrics", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return frontend_data
            
        except Exception as e:
            logger.error(f"❌ DeFi opportunities error: {e}")
            return {"error": "Failed to fetch DeFi opportunities"}
    
    async def _get_initial_data_package(self, user_id: str) -> Dict[str, Any]:
        """Get initial data package for new connection"""
        
        initial_data = {
            "user_profile": await self._get_user_profile(user_id),
            "market_overview": await self.get_market_overview(user_id),
            "system_status": self._get_system_status(),
            "ui_preferences": self._get_ui_preferences(user_id)
        }
        
        # Add AI insights if enabled
        if self.user_subscriptions[user_id].get("ai_signals", False):
            initial_data["ai_insights"] = await self.get_ai_insights(user_id)
        
        # Add DeFi data if enabled
        if self.user_subscriptions[user_id].get("defi_opportunities", False):
            initial_data["defi_opportunities"] = await self.get_defi_opportunities(user_id)
        
        return initial_data
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile data"""
        # Would fetch from database
        return {
            "user_id": user_id,
            "display_name": "Demo User",
            "account_type": "paper",
            "risk_tolerance": "moderate",
            "trading_level": "intermediate"
        }
    
    async def _get_account_summary(self, account_id: str) -> Dict[str, Any]:
        """Get account summary"""
        # Mock account summary
        return {
            "account_id": account_id,
            "cash_balance": 98750.50,
            "buying_power": 197501.00,
            "portfolio_value": 125430.25,
            "day_pnl": 2340.75,
            "day_pnl_percent": 1.9,
            "positions_count": 8,
            "orders_count": 2
        }
    
    async def _get_positions_summary(self, account_id: str) -> List[Dict[str, Any]]:
        """Get positions summary"""
        # Mock positions
        return [
            {
                "symbol": "AAPL",
                "quantity": 100,
                "avg_price": 175.25,
                "market_price": 180.50,
                "market_value": 18050.0,
                "unrealized_pnl": 525.0,
                "unrealized_pnl_percent": 3.0
            },
            {
                "symbol": "MSFT",
                "quantity": 50,
                "avg_price": 335.00,
                "market_price": 340.75,
                "market_value": 17037.50,
                "unrealized_pnl": 287.50,
                "unrealized_pnl_percent": 1.7
            }
        ]
    
    async def _get_orders_summary(self, account_id: str) -> List[Dict[str, Any]]:
        """Get orders summary"""
        # Get from order manager
        return order_manager.get_active_orders()
    
    async def _get_risk_summary(self, account_id: str) -> Dict[str, Any]:
        """Get risk summary"""
        portfolio_risk = risk_manager.get_portfolio_risk(account_id)
        
        if portfolio_risk:
            return {
                "portfolio_var": portfolio_risk.var_1d_95,
                "beta": portfolio_risk.beta,
                "max_drawdown": portfolio_risk.max_drawdown,
                "concentration_score": portfolio_risk.concentration_score,
                "leverage_ratio": portfolio_risk.leverage_ratio,
                "risk_score": "medium"
            }
        
        return {"risk_score": "low", "message": "No positions to analyze"}
    
    async def _get_performance_summary(self, account_id: str) -> Dict[str, Any]:
        """Get performance summary"""
        # Mock performance data
        return {
            "total_return": 8.5,
            "total_return_percent": 12.3,
            "ytd_return": 5.2,
            "ytd_return_percent": 7.8,
            "best_performer": {"symbol": "NVDA", "return_percent": 45.2},
            "worst_performer": {"symbol": "META", "return_percent": -8.3}
        }
    
    async def _get_active_alerts(self, account_id: str) -> List[Dict[str, Any]]:
        """Get active alerts"""
        alerts = risk_manager.get_account_alerts(account_id)
        
        return [
            {
                "alert_id": alert.alert_id,
                "type": alert.risk_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "requires_action": alert.requires_action
            }
            for alert in alerts[-5:]  # Last 5 alerts
        ]
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "market_data": "online",
            "trading": "online", 
            "risk_management": "online",
            "ai_services": "online",
            "defi_services": "online",
            "last_updated": datetime.utcnow().isoformat(),
            "latency_ms": 12
        }
    
    def _get_ui_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get UI preferences"""
        ui_state = self.connected_users.get(user_id)
        
        if ui_state:
            return {
                "theme": ui_state.theme,
                "chart_timeframe": ui_state.chart_timeframe,
                "notifications_enabled": ui_state.notifications_enabled,
                "selected_symbols": ui_state.selected_symbols
            }
        
        return {"theme": "dark", "chart_timeframe": "1h"}
    
    def _get_subscription_key(self, event_type: FrontendEventType) -> Optional[str]:
        """Get subscription key for event type"""
        
        mapping = {
            FrontendEventType.MARKET_TICK_UPDATE: "market_data",
            FrontendEventType.WATCHLIST_UPDATE: "market_data",
            FrontendEventType.ORDER_STATUS_UPDATE: "order_updates",
            FrontendEventType.POSITION_UPDATE: "portfolio_updates",
            FrontendEventType.ACCOUNT_BALANCE_UPDATE: "portfolio_updates",
            FrontendEventType.RISK_ALERT: "risk_alerts",
            FrontendEventType.AI_SIGNAL_GENERATED: "ai_signals",
            FrontendEventType.DEFI_OPPORTUNITY_UPDATE: "defi_opportunities",
            FrontendEventType.SYSTEM_STATUS: "system_notifications"
        }
        
        return mapping.get(event_type)
    
    async def _message_dispatcher(self):
        """Background message dispatcher"""
        
        while True:
            try:
                # Process message queues for all users
                for user_id, messages in list(self.message_queue.items()):
                    if not messages:
                        continue
                    
                    # Sort by priority and timestamp
                    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
                    messages.sort(key=lambda m: (priority_order.get(m.priority, 2), m.timestamp))
                    
                    # Send messages via WebSocket
                    for message in messages[:10]:  # Send up to 10 messages at once
                        try:
                            await websocket_manager.broadcast_order_update(user_id, {
                                "event_type": message.event_type.value,
                                "data": message.data,
                                "timestamp": message.timestamp.isoformat(),
                                "message_id": message.message_id,
                                "priority": message.priority
                            })
                            
                            self.integration_stats["messages_sent"] += 1
                            
                        except Exception as e:
                            logger.error(f"❌ Message dispatch error for {user_id}: {e}")
                            self.integration_stats["event_processing_errors"] += 1
                    
                    # Remove sent messages
                    self.message_queue[user_id] = messages[10:]
                
                await asyncio.sleep(0.1)  # 100ms dispatch interval
                
            except Exception as e:
                logger.error(f"❌ Message dispatcher error: {e}")
                await asyncio.sleep(1)
    
    async def _data_aggregator(self):
        """Background data aggregation for frontend"""
        
        while True:
            try:
                await asyncio.sleep(5)  # Update every 5 seconds
                
                # Update market data for all connected users
                all_symbols = set()
                for ui_state in self.connected_users.values():
                    all_symbols.update(ui_state.selected_symbols)
                
                # Collect latest market data
                market_updates = {}
                for symbol in all_symbols:
                    tick = market_data_stream.get_latest_tick(symbol)
                    if tick:
                        market_updates[symbol] = {
                            "price": tick.price,
                            "change": tick.change,
                            "change_percent": tick.change_percent,
                            "volume": tick.volume,
                            "timestamp": tick.timestamp.isoformat()
                        }
                
                # Send updates to subscribed users
                if market_updates:
                    for user_id, ui_state in self.connected_users.items():
                        user_updates = {
                            symbol: data for symbol, data in market_updates.items()
                            if symbol in ui_state.selected_symbols
                        }
                        
                        if user_updates:
                            await self.send_event_to_user(
                                user_id,
                                FrontendEventType.MARKET_TICK_UPDATE,
                                {"updates": user_updates}
                            )
                
            except Exception as e:
                logger.error(f"❌ Data aggregator error: {e}")
    
    async def _heartbeat_service(self):
        """Heartbeat service for frontend connections"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
                current_time = datetime.utcnow()
                
                # Send heartbeat to all connected users
                for user_id in list(self.connected_users.keys()):
                    await self.send_event_to_user(
                        user_id,
                        FrontendEventType.SYSTEM_STATUS,
                        {
                            "type": "heartbeat",
                            "timestamp": current_time.isoformat(),
                            "active_connections": len(self.connected_users)
                        },
                        priority="low"
                    )
                
            except Exception as e:
                logger.error(f"❌ Heartbeat service error: {e}")
    
    async def _performance_monitor(self):
        """Monitor integration performance"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes
                
                total_queued = sum(len(messages) for messages in self.message_queue.values())
                
                logger.info(
                    f"🌉 Frontend Integration Stats - "
                    f"Connections: {self.integration_stats['active_connections']}, "
                    f"Messages Sent: {self.integration_stats['messages_sent']}, "
                    f"Queued: {total_queued}, "
                    f"Errors: {self.integration_stats['event_processing_errors']}"
                )
                
            except Exception as e:
                logger.error(f"❌ Performance monitor error: {e}")
    
    # Event handlers for integration with other services
    async def _handle_market_data_event(self, event_data: Dict[str, Any]):
        """Handle market data events"""
        symbol = event_data.get("symbol")
        
        # Find users watching this symbol
        interested_users = [
            user_id for user_id, ui_state in self.connected_users.items()
            if symbol in ui_state.selected_symbols
        ]
        
        # Send update to interested users
        for user_id in interested_users:
            await self.send_event_to_user(
                user_id,
                FrontendEventType.MARKET_TICK_UPDATE,
                event_data
            )
    
    async def _handle_order_update_event(self, event_data: Dict[str, Any]):
        """Handle order update events"""
        user_id = event_data.get("user_id")
        
        if user_id and user_id in self.connected_users:
            await self.send_event_to_user(
                user_id,
                FrontendEventType.ORDER_STATUS_UPDATE,
                event_data
            )
    
    async def _handle_risk_alert_event(self, event_data: Dict[str, Any]):
        """Handle risk alert events"""
        user_id = event_data.get("user_id")
        
        if user_id and user_id in self.connected_users:
            await self.send_event_to_user(
                user_id,
                FrontendEventType.RISK_ALERT,
                event_data,
                priority="high"
            )
    
    async def _handle_ai_signal_event(self, event_data: Dict[str, Any]):
        """Handle AI signal events"""
        user_id = event_data.get("user_id")
        
        if user_id and user_id in self.connected_users:
            await self.send_event_to_user(
                user_id,
                FrontendEventType.AI_SIGNAL_GENERATED,
                event_data
            )
    
    async def _handle_system_notification(self, event_data: Dict[str, Any]):
        """Handle system notifications"""
        # Broadcast to all users
        await self.broadcast_event(
            FrontendEventType.NOTIFICATION,
            event_data
        )
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        
        return {
            **self.integration_stats,
            "total_queued_messages": sum(len(messages) for messages in self.message_queue.values()),
            "connected_users": list(self.connected_users.keys()),
            "subscription_breakdown": {
                user_id: subscriptions for user_id, subscriptions in self.user_subscriptions.items()
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown frontend integration service"""
        
        logger.info("🛑 Shutting down frontend integration service...")
        
        # Disconnect all users
        for user_id in list(self.connected_users.keys()):
            await self.disconnect_user(user_id)
        
        # Clear all data
        self.connected_users.clear()
        self.user_subscriptions.clear()
        self.message_queue.clear()
        self.portfolio_summaries.clear()
        
        logger.info("✅ Frontend integration service shutdown complete")

# Global frontend integration service
frontend_integration = FrontendIntegrationService()