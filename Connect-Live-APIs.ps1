# 🔌 Connect Live APIs - One-Click Setup
# Automatically configures multiple live market data providers

Write-Host "🔌 Connecting Live Market Data APIs..." -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check if backend exists
if (-not (Test-Path "backend")) {
    Write-Host "❌ Backend directory not found. Run from CamboAI root directory." -ForegroundColor Red
    exit 1
}

# Create environment file if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Creating environment configuration..." -ForegroundColor Yellow
    
    $envContent = @"
# 🚀 CamboAI Trading Platform - Live Configuration
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-for-production
DATABASE_URL=sqlite:///./cambo_ai_trader.db

# === LIVE MARKET DATA APIs ===
# Get FREE API keys from these providers:

# Alpaca (FREE Paper Trading + Live Data)
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Alpha Vantage (FREE 500 calls/day)
ALPHA_VANTAGE_API_KEY=

# IEX Cloud (FREE tier available)
IEX_API_KEY=

# Polygon.io (FREE 5 calls/minute)
POLYGON_API_KEY=

# === EMAIL NOTIFICATIONS ===
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# === AI FEATURES (Optional) ===
OPENAI_API_KEY=
"@
    
    $envContent | Out-File -FilePath "backend\.env" -Encoding UTF8
    Write-Host "✅ Environment file created: backend\.env" -ForegroundColor Green
}

# Update market data stream to use live providers
Write-Host "`n📡 Updating market data stream for live APIs..." -ForegroundColor Yellow

$liveDataIntegration = @'
# Add this to your backend/app/core/market_data_stream.py

async def initialize_live_providers(self):
    """Initialize live market data providers"""
    
    # Check for API keys and initialize providers
    providers_config = {
        "alpaca": {
            "key": os.getenv("ALPACA_API_KEY"),
            "secret": os.getenv("ALPACA_SECRET_KEY"),
            "enabled": bool(os.getenv("ALPACA_API_KEY"))
        },
        "alpha_vantage": {
            "key": os.getenv("ALPHA_VANTAGE_API_KEY"),
            "enabled": bool(os.getenv("ALPHA_VANTAGE_API_KEY"))
        },
        "iex": {
            "key": os.getenv("IEX_API_KEY"), 
            "enabled": bool(os.getenv("IEX_API_KEY"))
        },
        "polygon": {
            "key": os.getenv("POLYGON_API_KEY"),
            "enabled": bool(os.getenv("POLYGON_API_KEY"))
        }
    }
    
    enabled_providers = [name for name, config in providers_config.items() if config["enabled"]]
    
    if enabled_providers:
        logger.info(f"🌐 Live providers enabled: {', '.join(enabled_providers)}")
        # Initialize live providers here
    else:
        logger.info("📊 Using mock data providers (no API keys configured)")

# Add live WebSocket streaming
async def start_live_websocket_feeds(self):
    """Start live WebSocket feeds from providers"""
    
    # Alpaca WebSocket
    if os.getenv("ALPACA_API_KEY"):
        asyncio.create_task(self._alpaca_websocket_stream())
    
    # IEX WebSocket  
    if os.getenv("IEX_API_KEY"):
        asyncio.create_task(self._iex_websocket_stream())

async def _alpaca_websocket_stream(self):
    """Alpaca WebSocket stream for real-time data"""
    import websockets
    import json
    
    uri = "wss://stream.data.alpaca.markets/v2/iex"
    auth_data = {
        "action": "auth",
        "key": os.getenv("ALPACA_API_KEY"),
        "secret": os.getenv("ALPACA_SECRET_KEY")
    }
    
    try:
        async with websockets.connect(uri) as websocket:
            # Authenticate
            await websocket.send(json.dumps(auth_data))
            auth_response = await websocket.recv()
            
            # Subscribe to symbols
            subscribe_data = {
                "action": "subscribe",
                "quotes": list(self.subscribed_symbols),
                "trades": list(self.subscribed_symbols)
            }
            await websocket.send(json.dumps(subscribe_data))
            
            # Process live data
            async for message in websocket:
                data = json.loads(message)
                await self._process_alpaca_message(data)
                
    except Exception as e:
        logger.error(f"❌ Alpaca WebSocket error: {e}")

async def _process_alpaca_message(self, data):
    """Process Alpaca WebSocket message"""
    
    for item in data:
        if item.get("T") == "q":  # Quote
            symbol = item.get("S")
            tick = MarketTick(
                symbol=symbol,
                price=(item.get("bp", 0) + item.get("ap", 0)) / 2,
                bid=item.get("bp", 0),
                ask=item.get("ap", 0),
                bid_size=item.get("bs", 0),
                ask_size=item.get("as", 0),
                timestamp=datetime.now(),
                volume=0,  # Will be updated from trade data
                provider="alpaca_live"
            )
            
            await self._process_tick(tick)
'@

$liveDataIntegration | Out-File -FilePath "backend\live_data_integration_snippet.py" -Encoding UTF8

# Show API signup links
Write-Host "`n🎯 GET FREE API KEYS:" -ForegroundColor Cyan
Write-Host "1. Alpaca Markets (Paper Trading + Live Data):" -ForegroundColor White
Write-Host "   https://alpaca.markets" -ForegroundColor Blue
Write-Host "   • Sign up for free account" -ForegroundColor Gray
Write-Host "   • Get API Key + Secret Key" -ForegroundColor Gray
Write-Host "   • Use paper trading URL for testing" -ForegroundColor Gray

Write-Host "`n2. Alpha Vantage (500 free calls/day):" -ForegroundColor White  
Write-Host "   https://www.alphavantage.co/support/#api-key" -ForegroundColor Blue
Write-Host "   • Free tier: 5 calls/minute, 500/day" -ForegroundColor Gray

Write-Host "`n3. IEX Cloud (Free tier available):" -ForegroundColor White
Write-Host "   https://iexcloud.io" -ForegroundColor Blue
Write-Host "   • Free tier with 50,000 credits/month" -ForegroundColor Gray

Write-Host "`n4. Polygon.io (5 free calls/minute):" -ForegroundColor White
Write-Host "   https://polygon.io" -ForegroundColor Blue
Write-Host "   • Free tier for testing" -ForegroundColor Gray

# Create quick test script
$testScript = @'
"""
🔬 Live API Connection Test
Tests all configured market data APIs
"""

import os
import asyncio
import aiohttp
from datetime import datetime

async def test_alpaca():
    """Test Alpaca API connection"""
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("⚠️ Alpaca API keys not configured")
        return False
    
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://paper-api.alpaca.markets/v2/account", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Alpaca connected - Account: {data.get('account_number')}")
                    return True
                else:
                    print(f"❌ Alpaca failed - Status: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Alpaca error: {e}")
        return False

async def test_alpha_vantage():
    """Test Alpha Vantage API connection"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    if not api_key:
        print("⚠️ Alpha Vantage API key not configured")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Global Quote" in data:
                        quote = data["Global Quote"]
                        print(f"✅ Alpha Vantage connected - AAPL: ${quote.get('05. price', 'N/A')}")
                        return True
                    else:
                        print(f"❌ Alpha Vantage failed - Response: {data}")
                        return False
    except Exception as e:
        print(f"❌ Alpha Vantage error: {e}")
        return False

async def test_iex():
    """Test IEX Cloud API connection"""
    api_key = os.getenv("IEX_API_KEY")
    
    if not api_key:
        print("⚠️ IEX API key not configured")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://cloud.iexapis.com/stable/stock/AAPL/quote?token={api_key}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ IEX connected - AAPL: ${data.get('latestPrice', 'N/A')}")
                    return True
                else:
                    print(f"❌ IEX failed - Status: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ IEX error: {e}")
        return False

async def main():
    """Test all configured APIs"""
    print("🔬 Testing Live Market Data APIs...")
    print("=" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    results = []
    results.append(await test_alpaca())
    results.append(await test_alpha_vantage())
    results.append(await test_iex())
    
    connected = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {connected}/{total} providers connected")
    
    if connected == 0:
        print("\n💡 To connect live APIs:")
        print("1. Edit backend/.env file")
        print("2. Add your API keys")
        print("3. Run this test again")
    else:
        print(f"\n🚀 Ready to trade with {connected} live data provider(s)!")

if __name__ == "__main__":
    asyncio.run(main())
'@

$testScript | Out-File -FilePath "backend\test_live_apis.py" -Encoding UTF8

Write-Host "`n📝 WHAT TO DO NEXT:" -ForegroundColor Cyan
Write-Host "1. Edit backend\.env and add your API keys" -ForegroundColor White
Write-Host "2. Run: cd backend && python test_live_apis.py" -ForegroundColor Yellow
Write-Host "3. Test with: python run_camboai.py" -ForegroundColor Yellow

Write-Host "`n✅ Live API setup complete!" -ForegroundColor Green
Write-Host "   Edit backend\.env to add your keys" -ForegroundColor Gray