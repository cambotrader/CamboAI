from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
import json
import yfinance as yf
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[WebSocket, List[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = []
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message to websocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    async def send_to_subscribers(self, symbol: str, data: dict):
        message = json.dumps({
            "type": "price_update",
            "symbol": symbol,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        disconnected = []
        for websocket, symbols in self.subscriptions.items():
            if symbol in symbols:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending to subscriber: {e}")
                    disconnected.append(websocket)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    def subscribe(self, websocket: WebSocket, symbols: List[str]):
        if websocket in self.subscriptions:
            self.subscriptions[websocket].extend(symbols)
            # Remove duplicates
            self.subscriptions[websocket] = list(set(self.subscriptions[websocket]))

    def unsubscribe(self, websocket: WebSocket, symbols: List[str]):
        if websocket in self.subscriptions:
            for symbol in symbols:
                if symbol in self.subscriptions[websocket]:
                    self.subscriptions[websocket].remove(symbol)

manager = ConnectionManager()

@router.websocket("/prices")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "subscribe":
                symbols = message.get("symbols", [])
                manager.subscribe(websocket, symbols)
                await manager.send_personal_message(
                    json.dumps({
                        "type": "subscription_confirmed",
                        "symbols": symbols,
                        "message": f"Subscribed to {len(symbols)} symbols"
                    }),
                    websocket
                )
            
            elif message["type"] == "unsubscribe":
                symbols = message.get("symbols", [])
                manager.unsubscribe(websocket, symbols)
                await manager.send_personal_message(
                    json.dumps({
                        "type": "unsubscription_confirmed",
                        "symbols": symbols,
                        "message": f"Unsubscribed from {len(symbols)} symbols"
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.websocket("/portfolio")
async def portfolio_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send portfolio updates every 5 seconds
            await asyncio.sleep(5)
            
            # In a real implementation, this would fetch actual portfolio changes
            portfolio_update = {
                "type": "portfolio_update",
                "timestamp": datetime.now().isoformat(),
                "total_value": 125000.00,  # Mock data
                "daily_pnl": 2500.00,
                "positions_updated": ["AAPL", "MSFT", "GOOGL"]
            }
            
            await manager.send_personal_message(
                json.dumps(portfolio_update),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Portfolio WebSocket error: {e}")
        manager.disconnect(websocket)

# Background task to fetch and broadcast real-time price updates
async def price_update_task():
    """Background task to fetch and broadcast price updates"""
    while True:
        try:
            # Get all unique subscribed symbols
            all_symbols = set()
            for symbols in manager.subscriptions.values():
                all_symbols.update(symbols)
            
            if all_symbols:
                for symbol in all_symbols:
                    try:
                        ticker = yf.Ticker(symbol)
                        data = ticker.history(period="1d", interval="1m")
                        
                        if not data.empty:
                            latest = data.iloc[-1]
                            price_data = {
                                "price": round(float(latest['Close']), 2),
                                "volume": int(latest['Volume']),
                                "high": round(float(latest['High']), 2),
                                "low": round(float(latest['Low']), 2),
                                "open": round(float(latest['Open']), 2)
                            }
                            
                            await manager.send_to_subscribers(symbol, price_data)
                    
                    except Exception as e:
                        logger.error(f"Error fetching price for {symbol}: {e}")
            
            await asyncio.sleep(10)  # Update every 10 seconds
            
        except Exception as e:
            logger.error(f"Error in price update task: {e}")
            await asyncio.sleep(30)  # Wait longer on error
