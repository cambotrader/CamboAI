# 🚀 CamboAI Platform Quick Test Script
# Tests all core functionality to ensure everything works

Write-Host "🚀 Testing CamboAI Trading Platform..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend\app\main.py")) {
    Write-Host "❌ Please run this from the CamboAI root directory" -ForegroundColor Red
    exit 1
}

# Step 1: Install Python dependencies
Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow
Set-Location "backend"

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Blue
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Blue
& "venv\Scripts\Activate.ps1"

Write-Host "Installing requirements..." -ForegroundColor Blue
pip install -r requirements.txt

# Step 2: Setup database
Write-Host "`n🗄️ Setting up database..." -ForegroundColor Yellow
if (-not (Test-Path "cambo_ai_trader.db")) {
    Write-Host "Creating database tables..." -ForegroundColor Blue
    python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"
}

# Step 3: Test imports
Write-Host "`n🔍 Testing core imports..." -ForegroundColor Yellow
python -c "
try:
    from app.main import app
    from app.core.market_data_stream import market_data_stream
    from app.core.paper_trading_engine import paper_trading_engine
    from app.core.risk_manager import risk_manager
    from app.core.order_manager import order_manager
    from app.core.websocket_manager import websocket_manager
    print('✅ All core modules imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Step 4: Start the platform
Write-Host "`n🚀 Starting CamboAI Platform..." -ForegroundColor Yellow
Write-Host "This will open your browser automatically..." -ForegroundColor Blue
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Blue

Set-Location ".."
python run_camboai.py

Write-Host "`n✅ Platform test complete!" -ForegroundColor Green