#!/usr/bin/env powershell
# Cambo AI Trader Station - Native Deployment (No Docker)

Write-Host "🚀 CAMBO AI TRADER STATION - NATIVE DEPLOYMENT" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

$originalPath = Get-Location
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $scriptPath "backend"
$frontendPath = Join-Path $scriptPath "frontend"
$dashboardPath = Join-Path $scriptPath "dashboard"

# Function to start backend
function Start-Backend {
    Write-Host "`n🔧 Starting Backend API..." -ForegroundColor Cyan
    Set-Location $backendPath
    
    # Activate virtual environment
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".\.venv\Scripts\Activate.ps1"
    } elseif (Test-Path "venv\Scripts\Activate.ps1") {
        & ".\venv\Scripts\Activate.ps1"
    } else {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        python -m venv .venv
        & ".\.venv\Scripts\Activate.ps1"
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    }
    
    # Set environment variables
    $env:ENVIRONMENT = "development"
    $env:DATABASE_URL = "postgresql://cambo_user:cambo_pass@localhost:5432/cambo_ai_trader"
    $env:REDIS_URL = "redis://localhost:6379"
    $env:SECRET_KEY = "development_secret_key_please_change_in_production"
    $env:JWT_SECRET_KEY = "jwt_secret_key_please_change_in_production"
    $env:ALPACA_API_KEY = "your_alpaca_api_key"
    $env:ALPACA_SECRET_KEY = "your_alpaca_secret_key"
    $env:ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
    
    # Start backend server in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
        Set-Location '$backendPath'
        if (Test-Path '.venv\Scripts\Activate.ps1') { & '.\.venv\Scripts\Activate.ps1' } else { & '.\venv\Scripts\Activate.ps1' }
        `$env:ENVIRONMENT = 'development'
        `$env:DATABASE_URL = 'sqlite:///./cambo_ai_trader.db'
        `$env:SECRET_KEY = 'development_secret_key_please_change_in_production'
        `$env:JWT_SECRET_KEY = 'jwt_secret_key_please_change_in_production'
        `$env:ALPACA_API_KEY = 'your_alpaca_api_key'
        `$env:ALPACA_SECRET_KEY = 'your_alpaca_secret_key'
        `$env:ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'
        Write-Host 'Starting FastAPI backend server...' -ForegroundColor Green
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    }" -WindowStyle Normal
    
    Write-Host "✅ Backend API starting on http://localhost:8000" -ForegroundColor Green
}

# Function to start frontend
function Start-Frontend {
    Write-Host "`n⚛️ Starting Frontend..." -ForegroundColor Cyan
    Set-Location $frontendPath
    
    # Install dependencies if needed
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    # Start frontend in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
        Set-Location '$frontendPath'
        `$env:REACT_APP_API_URL = 'http://localhost:8000'
        `$env:BROWSER = 'none'
        Write-Host 'Starting React frontend...' -ForegroundColor Green
        npm start
    }" -WindowStyle Normal
    
    Write-Host "✅ Frontend starting on http://localhost:3000" -ForegroundColor Green
}

# Function to start dashboard
function Start-Dashboard {
    Write-Host "`n📊 Starting Dashboard..." -ForegroundColor Cyan
    Set-Location $dashboardPath
    
    # Create virtual environment if needed
    if (-not (Test-Path "venv")) {
        Write-Host "Creating dashboard virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        & ".\venv\Scripts\Activate.ps1"
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    }
    
    # Start dashboard in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
        Set-Location '$dashboardPath'
        & '.\venv\Scripts\Activate.ps1'
        `$env:API_URL = 'http://localhost:8000'
        Write-Host 'Starting Streamlit dashboard...' -ForegroundColor Green
        streamlit run app.py --server.port 8501
    }" -WindowStyle Normal
    
    Write-Host "✅ Dashboard starting on http://localhost:8501" -ForegroundColor Green
}

# Main execution
try {
    Write-Host "`n🚀 Starting all services..." -ForegroundColor Blue
    
    Start-Backend
    Start-Sleep -Seconds 3
    
    Start-Frontend
    Start-Sleep -Seconds 2
    
    Start-Dashboard
    Start-Sleep -Seconds 2
    
    Set-Location $originalPath
    
    Write-Host "`n🎉 CAMBO AI TRADER STATION IS RUNNING!" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green
    
    Write-Host "`n🌐 Access URLs:" -ForegroundColor Yellow
    Write-Host "  Frontend (React):     http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend API:          http://localhost:8000" -ForegroundColor White
    Write-Host "  Dashboard (Streamlit): http://localhost:8501" -ForegroundColor White
    Write-Host "  API Documentation:    http://localhost:8000/docs" -ForegroundColor White
    
    Write-Host "`n📝 Notes:" -ForegroundColor Cyan
    Write-Host "  • Using SQLite database (no PostgreSQL required)" -ForegroundColor Gray
    Write-Host "  • Configure your Alpaca API keys in the environment" -ForegroundColor Gray
    Write-Host "  • Each service runs in a separate PowerShell window" -ForegroundColor Gray
    Write-Host "  • Close the PowerShell windows to stop services" -ForegroundColor Gray
    
    Write-Host "`n💡 Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Open http://localhost:3000 in your browser" -ForegroundColor Gray
    Write-Host "  2. Configure your Alpaca API credentials" -ForegroundColor Gray
    Write-Host "  3. Start trading with Cambo AI Trader Station!" -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ Deployment failed: $_" -ForegroundColor Red
    Set-Location $originalPath
    exit 1
}
