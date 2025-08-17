# 🌐 Setup Live Market Data APIs
# Configures multiple market data providers for real-time trading

Write-Host "🌐 Setting up Live Market Data APIs..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Create enhanced market data configuration
$envFile = @"
# 🚀 CamboAI Trading Platform - Live Configuration
# Copy this to backend/.env and fill in your API keys

# === CORE PLATFORM ===
ENVIRONMENT=production
SECRET_KEY=your-super-secret-jwt-key-change-this
DATABASE_URL=postgresql://user:password@localhost:5432/camboai
REDIS_URL=redis://localhost:6379

# === MARKET DATA PROVIDERS ===

# Alpaca (FREE - Paper Trading + Live Data)
# Sign up: https://alpaca.markets
ALPACA_API_KEY=your-alpaca-key-here
ALPACA_SECRET_KEY=your-alpaca-secret-here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading
# ALPACA_BASE_URL=https://api.alpaca.markets      # Live trading

# Alpha Vantage (FREE - 5 calls/minute, 500/day)
# Sign up: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key-here

# IEX Cloud (FREE tier available)
# Sign up: https://iexcloud.io
IEX_API_KEY=your-iex-key-here

# Polygon.io (FREE - 5 calls/minute)
# Sign up: https://polygon.io
POLYGON_API_KEY=your-polygon-key-here

# Financial Modeling Prep (FREE - 250 calls/day)
# Sign up: https://financialmodelingprep.com
FMP_API_KEY=your-fmp-key-here

# === CRYPTOCURRENCY APIs ===

# CoinGecko (FREE - No key required for basic)
COINGECKO_API_KEY=your-coingecko-pro-key-optional

# Binance (FREE - No key required for market data)
BINANCE_API_KEY=your-binance-key-optional
BINANCE_SECRET_KEY=your-binance-secret-optional

# === EMAIL NOTIFICATIONS ===
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# === AI SERVICES (Optional) ===
OPENAI_API_KEY=your-openai-key-for-ai-features

# === DEPLOYMENT (Optional) ===
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","https://yourdomain.com"]
"@

Write-Host "`n📝 Creating environment configuration..." -ForegroundColor Yellow
$envFile | Out-File -FilePath "backend\.env.example" -Encoding UTF8

Write-Host "`n✅ Configuration template created: backend\.env.example" -ForegroundColor Green

# Create enhanced market data provider
$marketDataProvider = @'
"""
🌐 ENHANCED MARKET DATA PROVIDER WITH LIVE APIs
Multiple provider support with automatic failover
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
import aiohttp
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LiveMarketDataProvider:
    """Enhanced market data with multiple live providers"""
    
    def __init__(self):
        self.providers = {
            "alpaca": AlpacaProvider(),
            "alpha_vantage": AlphaVantageProvider(), 
            "iex": IEXProvider(),
            "polygon": PolygonProvider(),
            "yahoo": YahooProvider(),
        }
        
        # Provider priority order
        self.provider_priority = ["alpaca", "iex", "alpha_vantage", "polygon", "yahoo"]
        self.active_providers = []
        
    async def initialize(self):
        """Initialize all available providers"""
        for name, provider in self.providers.items():
            if await provider.test_connection():
                self.active_providers.append(name)
                logger.info(f"✅ {name} provider online")
            else:
                logger.warning(f"⚠️ {name} provider unavailable")
    
    async def get_real_time_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote with provider failover"""
        for provider_name in self.provider_priority:
            if provider_name in self.active_providers:
                try:
                    data = await self.providers[provider_name].get_quote(symbol)
                    if data:
                        data["provider"] = provider_name
                        return data
                except Exception as e:
                    logger.error(f"❌ {provider_name} failed for {symbol}: {e}")
                    continue
        
        logger.error(f"❌ All providers failed for {symbol}")
        return None

class AlpacaProvider:
    """Alpaca Markets API provider"""
    
    def __init__(self):
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key
        }
    
    async def test_connection(self) -> bool:
        if not self.api_key or not self.secret_key:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/account", headers=self.headers) as response:
                    return response.status == 200
        except:
            return False
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v2/stocks/{symbol}/quotes/latest"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get("quote", {})
                    
                    return {
                        "symbol": symbol,
                        "bid": quote.get("bp", 0),
                        "ask": quote.get("ap", 0),
                        "price": (quote.get("bp", 0) + quote.get("ap", 0)) / 2,
                        "bid_size": quote.get("bs", 0),
                        "ask_size": quote.get("as", 0),
                        "timestamp": datetime.fromisoformat(quote.get("t", "").replace("Z", "+00:00")),
                        "provider": "alpaca"
                    }
        return None

class AlphaVantageProvider:
    """Alpha Vantage API provider"""
    
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
    
    async def test_connection(self) -> bool:
        return bool(self.api_key)
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get("Global Quote", {})
                    
                    if quote:
                        price = float(quote.get("05. price", 0))
                        return {
                            "symbol": symbol,
                            "price": price,
                            "change": float(quote.get("09. change", 0)),
                            "change_percent": quote.get("10. change percent", "0%").replace("%", ""),
                            "open": float(quote.get("02. open", 0)),
                            "high": float(quote.get("03. high", 0)),
                            "low": float(quote.get("04. low", 0)),
                            "volume": int(quote.get("06. volume", 0)),
                            "timestamp": datetime.now(),
                            "provider": "alpha_vantage"
                        }
        return None

class IEXProvider:
    """IEX Cloud API provider"""
    
    def __init__(self):
        self.api_key = os.getenv("IEX_API_KEY")
        self.base_url = "https://cloud.iexapis.com/stable"
    
    async def test_connection(self) -> bool:
        return bool(self.api_key)
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        url = f"{self.base_url}/stock/{symbol}/quote?token={self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "symbol": symbol,
                        "price": data.get("latestPrice", 0),
                        "change": data.get("change", 0),
                        "change_percent": data.get("changePercent", 0) * 100,
                        "open": data.get("open", 0),
                        "high": data.get("high", 0),
                        "low": data.get("low", 0),
                        "volume": data.get("volume", 0),
                        "market_cap": data.get("marketCap", 0),
                        "timestamp": datetime.now(),
                        "provider": "iex"
                    }
        return None

class PolygonProvider:
    """Polygon.io API provider"""
    
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.base_url = "https://api.polygon.io"
    
    async def test_connection(self) -> bool:
        return bool(self.api_key)
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}?apiKey={self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    ticker = data.get("results", {})
                    quote = ticker.get("lastQuote", {})
                    trade = ticker.get("lastTrade", {})
                    
                    return {
                        "symbol": symbol,
                        "price": trade.get("p", 0),
                        "bid": quote.get("p", 0),
                        "ask": quote.get("P", 0),
                        "bid_size": quote.get("s", 0),
                        "ask_size": quote.get("S", 0),
                        "volume": ticker.get("day", {}).get("v", 0),
                        "timestamp": datetime.now(),
                        "provider": "polygon"
                    }
        return None

class YahooProvider:
    """Yahoo Finance fallback provider"""
    
    async def test_connection(self) -> bool:
        return True  # Always available as fallback
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        # Use existing Yahoo Finance logic as fallback
        import yfinance as yf
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0) * 100,
                "open": info.get("regularMarketOpen", 0),
                "high": info.get("regularMarketDayHigh", 0),
                "low": info.get("regularMarketDayLow", 0),
                "volume": info.get("regularMarketVolume", 0),
                "timestamp": datetime.now(),
                "provider": "yahoo"
            }
        except:
            return None

# Global instance
live_market_data = LiveMarketDataProvider()
'@

$marketDataProvider | Out-File -FilePath "backend\app\services\live_market_data.py" -Encoding UTF8

Write-Host "`n📊 Created enhanced market data provider" -ForegroundColor Green

Write-Host "`n🎯 NEXT STEPS TO GET LIVE DATA:" -ForegroundColor Cyan
Write-Host "1. Copy backend\.env.example to backend\.env" -ForegroundColor White
Write-Host "2. Sign up for FREE API keys:" -ForegroundColor White
Write-Host "   • Alpaca Markets: https://alpaca.markets (FREE paper trading)" -ForegroundColor Yellow
Write-Host "   • Alpha Vantage: https://www.alphavantage.co (FREE 500 calls/day)" -ForegroundColor Yellow  
Write-Host "   • IEX Cloud: https://iexcloud.io (FREE tier)" -ForegroundColor Yellow
Write-Host "3. Fill in your API keys in backend\.env" -ForegroundColor White
Write-Host "4. Restart the platform to use live data" -ForegroundColor White

Write-Host "`n✅ Live data setup complete!" -ForegroundColor Green# 🌐 Setup Live Market Data APIs
# Configures multiple market data providers for real-time trading

Write-Host "🌐 Setting up Live Market Data APIs..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Create enhanced market data configuration
$envFile = @"
# 🚀 CamboAI Trading Platform - Live Configuration
# Copy this to backend/.env and fill in your API keys

# === CORE PLATFORM ===
ENVIRONMENT=production
SECRET_KEY=your-super-secret-jwt-key-change-this
DATABASE_URL=postgresql://user:password@localhost:5432/camboai
REDIS_URL=redis://localhost:6379

# === MARKET DATA PROVIDERS ===

# Alpaca (FREE - Paper Trading + Live Data)
# Sign up: https://alpaca.markets
ALPACA_API_KEY=your-alpaca-key-here
ALPACA_SECRET_KEY=your-alpaca-secret-here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading
# ALPACA_BASE_URL=https://api.alpaca.markets      # Live trading

# Alpha Vantage (FREE - 5 calls/minute, 500/day)
# Sign up: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key-here

# IEX Cloud (FREE tier available)
# Sign up: https://iexcloud.io
IEX_API_KEY=your-iex-key-here

# Polygon.io (FREE - 5 calls/minute)
# Sign up: https://polygon.io
POLYGON_API_KEY=your-polygon-key-here

# Financial Modeling Prep (FREE - 250 calls/day)
# Sign up: https://financialmodelingprep.com
FMP_API_KEY=your-fmp-key-here

# === CRYPTOCURRENCY APIs ===

# CoinGecko (FREE - No key required for basic)
COINGECKO_API_KEY=your-coingecko-pro-key-optional

# Binance (FREE - No key required for market data)
BINANCE_API_KEY=your-binance-key-optional
BINANCE_SECRET_KEY=your-binance-secret-optional

# === EMAIL NOTIFICATIONS ===
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# === AI SERVICES (Optional) ===
OPENAI_API_KEY=your-openai-key-for-ai-features

# === DEPLOYMENT (Optional) ===
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","https://yourdomain.com"]
"@

Write-Host "`n📝 Creating environment configuration..." -ForegroundColor Yellow
$envFile | Out-File -FilePath "backend\.env.example" -Encoding UTF8

Write-Host "`n✅ Configuration template created: backend\.env.example" -ForegroundColor Green

# Create enhanced market data provider
$marketDataProvider = @'
"""
🌐 ENHANCED MARKET DATA PROVIDER WITH LIVE APIs
Multiple provider support with automatic failover
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
import aiohttp
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LiveMarketDataProvider:
    """Enhanced market data with multiple live providers"""
    
    def __init__(self):
        self.providers = {
            "alpaca": AlpacaProvider(),
            "alpha_vantage": AlphaVantageProvider(), 
            "iex": IEXProvider(),
            "polygon": PolygonProvider(),
            "yahoo": YahooProvider(),
        }
        
        # Provider priority order
        self.provider_priority = ["alpaca", "iex", "alpha_vantage", "polygon", "yahoo"]
        self.active_providers = []
        
    async def initialize(self):
        """Initialize all available providers"""
        for name, provider in self.providers.items():
            if await provider.test_connection():
                self.active_providers.append(name)
                logger.info(f"✅ {name} provider online")
            else:
                logger.warning(f"⚠️ {name} provider unavailable")
    
    async def get_real_time_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote with provider failover"""
        for provider_name in self.provider_priority:
            if provider_name in self.active_providers:
                try:
                    data = await self.providers[provider_name].get_quote(symbol)
                    if data:
                        data["provider"] = provider_name
                        return data
                except Exception as e:
                    logger.error(f"❌ {provider_name} failed for {symbol}: {e}")
                    continue
        
        logger.error(f"❌ All providers failed for {symbol}")
        return None

class AlpacaProvider:
    """Alpaca Markets API provider"""
    
    def __init__(self):
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key
        }
    
    async def test_connection(self) -> bool:
        if not self.api_key or not self.secret_key:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/account", headers=self.headers) as response:
                    return response.status == 200
        except:
            return False
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v2/stocks/{symbol}/quotes/latest"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get("quote", {})
                    
                    return {
                        "symbol": symbol,
                        "bid": quote.get("bp", 0),
                        "ask": quote.get("ap", 0),
                        "price": (quote.get("bp", 0) + quote.get("ap", 0)) / 2,
                        "bid_size": quote.get("bs", 0),
                        "ask_size": quote.get("as", 0),
                        "timestamp": datetime.fromisoformat(quote.get("t", "").replace("Z", "+00:00")),
                        "provider": "alpaca"
                    }
        return None

class AlphaVantageProvider:
    """Alpha Vantage API provider"""
    
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
    
    async def test_connection(self) -> bool:
        return bool(self.api_key)
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get("Global Quote", {})
                    
                    if quote:
                        price = float(quote.get("05. price", 0))
                        return {
                            "symbol": symbol,
                            "price": price,
                            "change": float(quote.get("09. change", 0)),
                            "change_percent": quote.get("10. change percent", "0%").replace("%", ""),
                            "open": float(quote.get("02. open", 0)),
                            "high": float(quote.get("03. high", 0)),
                            "low": float(quote.get("04. low", 0)),
                            "volume": int(quote.get("06. volume", 0)),
                            "timestamp": datetime.now(),
                            "provider": "alpha_vantage"
                        }
        return None

class IEXProvider:
    """IEX Cloud API provider"""
    
    def __init__(self):
        self.api_key = os.getenv("IEX_API_KEY")
        self.base_url = "https://cloud.iexapis.com/stable"
    
    async def test_connection(self) -> bool:
        return bool(self.api_key)
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        url = f"{self.base_url}/stock/{symbol}/quote?token={self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "symbol": symbol,
                        "price": data.get("latestPrice", 0),
                        "change": data.get("change", 0),
                        "change_percent": data.get("changePercent", 0) * 100,
                        "open": data.get("open", 0),
                        "high": data.get("high", 0),
                        "low": data.get("low", 0),
                        "volume": data.get("volume", 0),
                        "market_cap": data.get("marketCap", 0),
                        "timestamp": datetime.now(),
                        "provider": "iex"
                    }
        return None

class PolygonProvider:
    """Polygon.io API provider"""
    
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.base_url = "https://api.polygon.io"
    
    async def test_connection(self) -> bool:
        return bool(self.api_key)
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}?apiKey={self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    ticker = data.get("results", {})
                    quote = ticker.get("lastQuote", {})
                    trade = ticker.get("lastTrade", {})
                    
                    return {
                        "symbol": symbol,
                        "price": trade.get("p", 0),
                        "bid": quote.get("p", 0),
                        "ask": quote.get("P", 0),
                        "bid_size": quote.get("s", 0),
                        "ask_size": quote.get("S", 0),
                        "volume": ticker.get("day", {}).get("v", 0),
                        "timestamp": datetime.now(),
                        "provider": "polygon"
                    }
        return None

class YahooProvider:
    """Yahoo Finance fallback provider"""
    
    async def test_connection(self) -> bool:
        return True  # Always available as fallback
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        # Use existing Yahoo Finance logic as fallback
        import yfinance as yf
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0) * 100,
                "open": info.get("regularMarketOpen", 0),
                "high": info.get("regularMarketDayHigh", 0),
                "low": info.get("regularMarketDayLow", 0),
                "volume": info.get("regularMarketVolume", 0),
                "timestamp": datetime.now(),
                "provider": "yahoo"
            }
        except:
            return None

# Global instance
live_market_data = LiveMarketDataProvider()
'@

$marketDataProvider | Out-File -FilePath "backend\app\services\live_market_data.py" -Encoding UTF8

Write-Host "`n📊 Created enhanced market data provider" -ForegroundColor Green

Write-Host "`n🎯 NEXT STEPS TO GET LIVE DATA:" -ForegroundColor Cyan
Write-Host "1. Copy backend\.env.example to backend\.env" -ForegroundColor White
Write-Host "2. Sign up for FREE API keys:" -ForegroundColor White
Write-Host "   • Alpaca Markets: https://alpaca.markets (FREE paper trading)" -ForegroundColor Yellow
Write-Host "   • Alpha Vantage: https://www.alphavantage.co (FREE 500 calls/day)" -ForegroundColor Yellow  
Write-Host "   • IEX Cloud: https://iexcloud.io (FREE tier)" -ForegroundColor Yellow
Write-Host "3. Fill in your API keys in backend\.env" -ForegroundColor White
Write-Host "4. Restart the platform to use live data" -ForegroundColor White

Write-Host "`n✅ Live data setup complete!" -ForegroundColor Green