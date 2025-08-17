"""
📡 REAL-TIME MARKET DATA STREAMING - INSTITUTIONAL GRADE
Ultra-low latency market data aggregation and distribution
"""

import asyncio
import aiohttp
import websockets
import json
import logging
from typing import Dict, List, Optional, Callable, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import time

from .websocket_manager import websocket_manager, MarketTick, Level2Update

logger = logging.getLogger(__name__)

class DataProvider(Enum):
    ALPACA = "alpaca"
    YAHOO_FINANCE = "yahoo"
    ALPHA_VANTAGE = "alpha_vantage"
    IEX_CLOUD = "iex_cloud"
    POLYGON = "polygon"
    FINNHUB = "finnhub"
    MOCK = "mock"

@dataclass
class DataFeedConfig:
    provider: DataProvider
    api_key: Optional[str]
    websocket_url: Optional[str]
    rest_url: Optional[str]
    symbols: List[str]
    update_frequency: int  # milliseconds
    retry_attempts: int = 3
    timeout: float = 10.0
    enabled: bool = True

@dataclass
class TradeData:
    symbol: str
    price: float
    size: int
    timestamp: datetime
    conditions: List[str]
    exchange: str

@dataclass
class QuoteData:
    symbol: str
    bid_price: float
    ask_price: float
    bid_size: int
    ask_size: int
    timestamp: datetime
    exchange: str

class MarketDataStream:
    """High-performance market data streaming engine"""
    
    def __init__(self):
        self.data_feeds: Dict[DataProvider, DataFeedConfig] = {}
        self.active_connections: Dict[DataProvider, Any] = {}
        self.subscribed_symbols: Set[str] = set()
        
        # Data aggregation
        self.latest_ticks: Dict[str, MarketTick] = {}
        self.trade_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.quote_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Performance metrics
        self.messages_processed = 0
        self.messages_per_second = 0
        self.latency_stats = defaultdict(list)
        self.start_time = time.time()
        
        # Quality control
        self.price_validators: Dict[str, float] = {}  # Last known good price
        self.suspicious_moves_threshold = 0.10  # 10% price move threshold
        
        # Callbacks
        self.tick_callbacks: List[Callable] = []
        self.trade_callbacks: List[Callable] = []
        self.quote_callbacks: List[Callable] = []
        
        # Background tasks
        self.stream_tasks: Dict[DataProvider, asyncio.Task] = {}
        self.aggregation_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Rate limiting
        self.message_rate_limiter = defaultdict(lambda: deque(maxlen=1000))
        self.max_messages_per_second = 10000
        
    async def initialize(self):
        """Initialize market data streaming system"""
        
        # Configure data feeds
        await self._configure_data_feeds()
        
        # Start aggregation engine
        self.aggregation_task = asyncio.create_task(self._market_data_aggregator())
        
        # Start monitoring
        self.monitoring_task = asyncio.create_task(self._performance_monitor())
        
        # Start WebSocket streams
        for provider, config in self.data_feeds.items():
            if config.enabled:
                self.stream_tasks[provider] = asyncio.create_task(
                    self._start_provider_stream(provider, config)
                )
        
        logger.info("🚀 Market data streaming engine initialized")
    
    async def _configure_data_feeds(self):
        """Configure market data providers"""
        
        # Alpaca Markets (Free tier available)
        self.data_feeds[DataProvider.ALPACA] = DataFeedConfig(
            provider=DataProvider.ALPACA,
            api_key=None,  # Would load from environment
            websocket_url="wss://stream.data.alpaca.markets/v2/iex",
            rest_url="https://data.alpaca.markets/v2",
            symbols=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SPY", "QQQ"],
            update_frequency=100,  # 100ms
            enabled=False  # Disabled for demo - requires API key
        )
        
        # Yahoo Finance (Free, no API key required)
        self.data_feeds[DataProvider.YAHOO_FINANCE] = DataFeedConfig(
            provider=DataProvider.YAHOO_FINANCE,
            api_key=None,
            websocket_url=None,  # Uses REST API
            rest_url="https://query1.finance.yahoo.com/v8/finance/chart/",
            symbols=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SPY", "QQQ", "NVDA", "META"],
            update_frequency=5000,  # 5 seconds (respectful rate)
            enabled=True
        )
        
        # Mock data provider (for development/demo)
        self.data_feeds[DataProvider.MOCK] = DataFeedConfig(
            provider=DataProvider.MOCK,
            api_key=None,
            websocket_url=None,
            rest_url=None,
            symbols=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SPY", "QQQ", "NVDA", "META", "NFLX"],
            update_frequency=250,  # 250ms for realistic simulation
            enabled=True
        )
    
    async def subscribe_symbol(self, symbol: str):
        """Subscribe to market data for a symbol"""
        
        symbol = symbol.upper()
        if symbol not in self.subscribed_symbols:
            self.subscribed_symbols.add(symbol)
            logger.info(f"📊 Subscribed to market data for {symbol}")
            
            # Add to all enabled feeds
            for provider, config in self.data_feeds.items():
                if config.enabled and symbol not in config.symbols:
                    config.symbols.append(symbol)
    
    async def unsubscribe_symbol(self, symbol: str):
        """Unsubscribe from market data for a symbol"""
        
        symbol = symbol.upper()
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol)
            logger.info(f"📊 Unsubscribed from market data for {symbol}")
    
    async def _start_provider_stream(self, provider: DataProvider, config: DataFeedConfig):
        """Start data stream for specific provider"""
        
        retry_count = 0
        
        while retry_count < config.retry_attempts:
            try:
                if provider == DataProvider.MOCK:
                    await self._mock_data_stream(config)
                elif provider == DataProvider.YAHOO_FINANCE:
                    await self._yahoo_finance_stream(config)
                elif provider == DataProvider.ALPACA:
                    await self._alpaca_stream(config)
                else:
                    logger.warning(f"⚠️ Provider {provider} not implemented yet")
                
                retry_count = 0  # Reset on successful connection
                
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ Error in {provider} stream (attempt {retry_count}): {e}")
                
                if retry_count >= config.retry_attempts:
                    logger.error(f"❌ {provider} stream failed after {config.retry_attempts} attempts")
                    break
                
                # Exponential backoff
                await asyncio.sleep(min(2 ** retry_count, 60))
    
    async def _mock_data_stream(self, config: DataFeedConfig):
        """Mock data stream for development/demo"""
        
        logger.info(f"🎭 Starting mock data stream for {len(config.symbols)} symbols")
        
        # Base prices for realistic simulation
        base_prices = {
            "AAPL": 180.00, "MSFT": 340.00, "GOOGL": 135.00, "AMZN": 145.00,
            "TSLA": 220.00, "SPY": 450.00, "QQQ": 380.00, "NVDA": 850.00,
            "META": 320.00, "NFLX": 450.00
        }
        
        # Initialize price tracking
        current_prices = base_prices.copy()
        daily_opens = base_prices.copy()
        daily_highs = base_prices.copy()
        daily_lows = base_prices.copy()
        
        while True:
            try:
                for symbol in config.symbols:
                    if symbol not in self.subscribed_symbols:
                        continue
                    
                    # Generate realistic price movement
                    base_price = current_prices.get(symbol, 100.0)
                    
                    # Random walk with mean reversion
                    volatility = 0.0015  # 0.15% per update
                    drift = 0.0001  # Slight upward drift
                    
                    random_move = np.random.normal(drift, volatility)
                    new_price = base_price * (1 + random_move)
                    
                    # Mean reversion towards daily open
                    reversion_strength = 0.001
                    reversion = (daily_opens[symbol] - new_price) * reversion_strength
                    new_price += reversion
                    
                    # Update tracking
                    current_prices[symbol] = new_price
                    daily_highs[symbol] = max(daily_highs[symbol], new_price)
                    daily_lows[symbol] = min(daily_lows[symbol], new_price)
                    
                    # Calculate metrics
                    change = new_price - daily_opens[symbol]
                    change_percent = (change / daily_opens[symbol]) * 100
                    
                    # Generate volume
                    base_volume = {"AAPL": 50000000, "SPY": 80000000}.get(symbol, 10000000)
                    volume = int(base_volume * np.random.uniform(0.5, 2.0))
                    
                    # Generate bid/ask spread
                    spread_bps = np.random.uniform(1, 5)  # 1-5 basis points
                    spread = new_price * (spread_bps / 10000)
                    
                    bid = new_price - spread / 2
                    ask = new_price + spread / 2
                    
                    # Generate sizes
                    bid_size = int(np.random.uniform(100, 1000))
                    ask_size = int(np.random.uniform(100, 1000))
                    
                    # Calculate VWAP (simplified)
                    vwap = new_price * np.random.uniform(0.999, 1.001)
                    
                    # Create market tick
                    tick = MarketTick(
                        symbol=symbol,
                        price=new_price,
                        volume=volume,
                        timestamp=datetime.utcnow(),
                        bid=bid,
                        ask=ask,
                        bid_size=bid_size,
                        ask_size=ask_size,
                        change=change,
                        change_percent=change_percent,
                        high=daily_highs[symbol],
                        low=daily_lows[symbol],
                        open=daily_opens[symbol],
                        vwap=vwap
                    )
                    
                    # Process the tick
                    await self._process_market_tick(tick, provider=DataProvider.MOCK)
                
                # Wait for next update
                await asyncio.sleep(config.update_frequency / 1000.0)
                
            except Exception as e:
                logger.error(f"❌ Mock data stream error: {e}")
                await asyncio.sleep(1)
    
    async def _yahoo_finance_stream(self, config: DataFeedConfig):
        """Yahoo Finance data stream using REST API"""
        
        logger.info(f"📈 Starting Yahoo Finance stream for {len(config.symbols)} symbols")
        
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config.timeout))
        
        try:
            while True:
                for symbol in config.symbols:
                    if symbol not in self.subscribed_symbols:
                        continue
                    
                    try:
                        # Yahoo Finance API endpoint
                        url = f"{config.rest_url}{symbol}"
                        params = {
                            "interval": "1m",
                            "range": "1d",
                            "includePrePost": "true"
                        }
                        
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                await self._process_yahoo_response(data, symbol)
                            else:
                                logger.warning(f"⚠️ Yahoo Finance API error for {symbol}: {response.status}")
                    
                    except Exception as e:
                        logger.error(f"❌ Yahoo Finance error for {symbol}: {e}")
                
                # Wait before next batch
                await asyncio.sleep(config.update_frequency / 1000.0)
                
        finally:
            await session.close()
    
    async def _process_yahoo_response(self, data: dict, symbol: str):
        """Process Yahoo Finance API response"""
        
        try:
            chart = data.get("chart", {})
            if not chart or "result" not in chart or not chart["result"]:
                return
            
            result = chart["result"][0]
            
            # Get latest data point
            meta = result.get("meta", {})
            current_price = meta.get("regularMarketPrice", 0)
            
            if current_price <= 0:
                return
            
            # Extract other fields
            previous_close = meta.get("previousClose", current_price)
            day_high = meta.get("regularMarketDayHigh", current_price)
            day_low = meta.get("regularMarketDayLow", current_price)
            volume = meta.get("regularMarketVolume", 0)
            
            # Calculate changes
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            # Estimate bid/ask (Yahoo doesn't provide real-time L1)
            spread_estimate = current_price * 0.0001  # 1 basis point estimate
            bid = current_price - spread_estimate / 2
            ask = current_price + spread_estimate / 2
            
            # Create market tick
            tick = MarketTick(
                symbol=symbol,
                price=current_price,
                volume=volume,
                timestamp=datetime.utcnow(),
                bid=bid,
                ask=ask,
                bid_size=100,  # Estimated
                ask_size=100,  # Estimated
                change=change,
                change_percent=change_percent,
                high=day_high,
                low=day_low,
                open=previous_close,  # Using previous close as open estimate
                vwap=current_price  # Simplified
            )
            
            await self._process_market_tick(tick, provider=DataProvider.YAHOO_FINANCE)
            
        except Exception as e:
            logger.error(f"❌ Yahoo response processing error for {symbol}: {e}")
    
    async def _alpaca_stream(self, config: DataFeedConfig):
        """Alpaca Markets WebSocket stream"""
        
        if not config.api_key:
            logger.warning("⚠️ Alpaca API key not configured")
            return
        
        logger.info(f"🦙 Starting Alpaca stream for {len(config.symbols)} symbols")
        
        headers = {
            "APCA-API-KEY-ID": config.api_key,
            "APCA-API-SECRET-KEY": "your_secret_key"  # Would load from env
        }
        
        try:
            async with websockets.connect(config.websocket_url, extra_headers=headers) as websocket:
                # Send subscription message
                subscribe_msg = {
                    "action": "subscribe",
                    "quotes": config.symbols,
                    "trades": config.symbols
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self._process_alpaca_message(data)
                    except Exception as e:
                        logger.error(f"❌ Alpaca message processing error: {e}")
        
        except Exception as e:
            logger.error(f"❌ Alpaca WebSocket error: {e}")
            raise
    
    async def _process_alpaca_message(self, data: dict):
        """Process Alpaca WebSocket message"""
        
        for message in data:
            msg_type = message.get("T")
            
            if msg_type == "t":  # Trade
                await self._process_alpaca_trade(message)
            elif msg_type == "q":  # Quote
                await self._process_alpaca_quote(message)
    
    async def _process_market_tick(self, tick: MarketTick, provider: DataProvider):
        """Process incoming market tick with quality control"""
        
        # Quality control checks
        if not self._validate_tick(tick):
            return
        
        # Update latest tick
        self.latest_ticks[tick.symbol] = tick
        
        # Add to trade history
        self.trade_history[tick.symbol].append({
            "price": tick.price,
            "volume": tick.volume,
            "timestamp": tick.timestamp,
            "provider": provider.value
        })
        
        # Calculate latency
        processing_time = (datetime.utcnow() - tick.timestamp).total_seconds() * 1000
        self.latency_stats[provider].append(processing_time)
        if len(self.latency_stats[provider]) > 1000:
            self.latency_stats[provider] = self.latency_stats[provider][-1000:]
        
        # Update performance metrics
        self.messages_processed += 1
        
        # Execute callbacks
        for callback in self.tick_callbacks:
            try:
                await callback(tick)
            except Exception as e:
                logger.error(f"❌ Tick callback error: {e}")
        
        # Broadcast to WebSocket clients
        await websocket_manager.broadcast_market_tick(tick)
        
        # Log high-volume or unusual activity
        if tick.volume > 1000000 or abs(tick.change_percent) > 5.0:
            logger.info(
                f"📊 {tick.symbol}: ${tick.price:.2f} "
                f"({tick.change_percent:+.2f}%) "
                f"Vol: {tick.volume:,} "
                f"[{provider.value}]"
            )
    
    def _validate_tick(self, tick: MarketTick) -> bool:
        """Validate market tick for suspicious data"""
        
        # Basic sanity checks
        if tick.price <= 0 or tick.volume < 0:
            logger.warning(f"⚠️ Invalid tick data for {tick.symbol}: price={tick.price}, volume={tick.volume}")
            return False
        
        # Check for unrealistic price moves
        if tick.symbol in self.price_validators:
            last_price = self.price_validators[tick.symbol]
            price_change = abs(tick.price - last_price) / last_price
            
            if price_change > self.suspicious_moves_threshold:
                logger.warning(
                    f"⚠️ Suspicious price move for {tick.symbol}: "
                    f"{last_price:.2f} -> {tick.price:.2f} "
                    f"({price_change:.1%})"
                )
                return False
        
        # Update price validator
        self.price_validators[tick.symbol] = tick.price
        
        return True
    
    async def _market_data_aggregator(self):
        """Background task to aggregate and enhance market data"""
        
        while True:
            try:
                # Calculate market-wide metrics
                await self._calculate_market_metrics()
                
                # Generate derived indicators
                await self._calculate_technical_indicators()
                
                # Detect unusual activity
                await self._detect_unusual_activity()
                
                await asyncio.sleep(1)  # Run every second
                
            except Exception as e:
                logger.error(f"❌ Market data aggregation error: {e}")
                await asyncio.sleep(5)
    
    async def _calculate_market_metrics(self):
        """Calculate market-wide metrics"""
        
        if not self.latest_ticks:
            return
        
        # Calculate market breadth
        advancing = sum(1 for tick in self.latest_ticks.values() if tick.change > 0)
        declining = sum(1 for tick in self.latest_ticks.values() if tick.change < 0)
        unchanged = len(self.latest_ticks) - advancing - declining
        
        # Calculate average volume
        avg_volume = np.mean([tick.volume for tick in self.latest_ticks.values()])
        
        # Market metrics could be broadcasted to interested clients
        market_metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "advancing": advancing,
            "declining": declining,
            "unchanged": unchanged,
            "advance_decline_ratio": advancing / max(declining, 1),
            "average_volume": avg_volume,
            "total_symbols": len(self.latest_ticks)
        }
        
        # Could broadcast this to subscribers interested in market-wide data
    
    async def _calculate_technical_indicators(self):
        """Calculate technical indicators for active symbols"""
        
        for symbol, history in self.trade_history.items():
            if len(history) < 20:  # Need minimum data points
                continue
            
            try:
                # Convert to DataFrame for easier calculation
                df = pd.DataFrame(history)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp').sort_index()
                
                # Simple Moving Average
                df['sma_20'] = df['price'].rolling(window=20).mean()
                
                # RSI calculation (simplified)
                delta = df['price'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['rsi'] = 100 - (100 / (1 + rs))
                
                # Update latest tick with indicators
                if symbol in self.latest_ticks:
                    latest_indicators = {
                        'sma_20': df['sma_20'].iloc[-1] if not pd.isna(df['sma_20'].iloc[-1]) else None,
                        'rsi': df['rsi'].iloc[-1] if not pd.isna(df['rsi'].iloc[-1]) else None
                    }
                    
                    # Could add indicators to the tick or broadcast separately
            
            except Exception as e:
                logger.error(f"❌ Technical indicator calculation error for {symbol}: {e}")
    
    async def _detect_unusual_activity(self):
        """Detect unusual trading activity"""
        
        for symbol, tick in self.latest_ticks.items():
            # Volume spike detection
            if len(self.trade_history[symbol]) >= 10:
                recent_volumes = [t['volume'] for t in list(self.trade_history[symbol])[-10:]]
                avg_volume = np.mean(recent_volumes[:-1])  # Exclude current
                
                if tick.volume > avg_volume * 3:  # 3x average volume
                    logger.info(f"📈 Volume spike detected: {symbol} - {tick.volume:,} vs {avg_volume:,.0f} avg")
            
            # Price movement alerts
            if abs(tick.change_percent) > 5.0:
                logger.info(f"📊 Large price move: {symbol} {tick.change_percent:+.2f}%")
    
    async def _performance_monitor(self):
        """Monitor streaming performance"""
        
        last_message_count = 0
        
        while True:
            try:
                await asyncio.sleep(60)  # Report every minute
                
                # Calculate messages per second
                current_count = self.messages_processed
                messages_this_minute = current_count - last_message_count
                self.messages_per_second = messages_this_minute / 60
                last_message_count = current_count
                
                # Calculate average latency by provider
                latency_report = {}
                for provider, latencies in self.latency_stats.items():
                    if latencies:
                        latency_report[provider.value] = {
                            "avg_ms": np.mean(latencies),
                            "p95_ms": np.percentile(latencies, 95),
                            "p99_ms": np.percentile(latencies, 99),
                            "samples": len(latencies)
                        }
                
                # Log performance report
                logger.info(
                    f"📊 Market Data Performance - "
                    f"Messages/sec: {self.messages_per_second:.1f}, "
                    f"Active symbols: {len(self.latest_ticks)}, "
                    f"Total processed: {current_count:,}"
                )
                
                if latency_report:
                    logger.info(f"📡 Latency report: {latency_report}")
                
            except Exception as e:
                logger.error(f"❌ Performance monitoring error: {e}")
    
    def add_tick_callback(self, callback: Callable):
        """Add callback for market tick events"""
        self.tick_callbacks.append(callback)
    
    def get_latest_tick(self, symbol: str) -> Optional[MarketTick]:
        """Get latest tick for symbol"""
        return self.latest_ticks.get(symbol.upper())
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "messages_processed": self.messages_processed,
            "messages_per_second": self.messages_per_second,
            "active_symbols": len(self.latest_ticks),
            "subscribed_symbols": len(self.subscribed_symbols),
            "data_providers": {
                provider.value: {
                    "enabled": config.enabled,
                    "symbols": len(config.symbols)
                }
                for provider, config in self.data_feeds.items()
            },
            "latency_stats": {
                provider.value: {
                    "avg_ms": np.mean(latencies) if latencies else 0,
                    "samples": len(latencies)
                }
                for provider, latencies in self.latency_stats.items()
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown market data stream"""
        
        logger.info("🛑 Shutting down market data stream...")
        
        # Cancel all stream tasks
        for task in self.stream_tasks.values():
            if not task.done():
                task.cancel()
        
        # Cancel monitoring tasks
        if self.aggregation_task and not self.aggregation_task.done():
            self.aggregation_task.cancel()
        
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
        
        logger.info("✅ Market data stream shutdown complete")

# Global instance
market_data_stream = MarketDataStream()