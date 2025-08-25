import asyncio, json, logging, os
from typing import Dict, Any, Optional, Callable
from datetime import datetime
try:
    from binance import AsyncClient, BinanceSocketManager
except ImportError:
    AsyncClient = None
    BinanceSocketManager = None

logger = logging.getLogger("external_feed")

class ExternalFeed:
    def __init__(self):
        self.client: Optional[Any] = None
        self.symbol = "btcusdt"
        self.last_tick: Optional[Dict[str, Any]] = None
        self.callback: Optional[Callable[[Dict[str,Any]], None]] = None

    async def start(self, symbol: str, callback: Callable[[Dict[str,Any]], None]):
        if AsyncClient is None:
            return
        self.symbol = symbol.lower()
        self.callback = callback
        self.client = await AsyncClient.create(api_key=os.getenv("BINANCE_KEY"),
                                               api_secret=os.getenv("BINANCE_SECRET"))
        bsm = BinanceSocketManager(self.client)
        ts = bsm.symbol_ticker_socket(symbol.upper())
        async with ts as stream:
            async for msg in stream:
                tick = {
                    "symbol": msg["s"],
                    "ts": datetime.utcfromtimestamp(msg["E"]/1000).isoformat(),
                    "price": float(msg["c"])
                }
                self.last_tick = tick
                if self.callback:
                    self.callback(tick)

    async def shutdown(self):
        if self.client:
            await self.client.close_connection()

external_feed = ExternalFeed()

def _broadcast_tick(tick: Dict[str,Any]):
    # placeholder; actual broadcast wired in ws_market
    pass