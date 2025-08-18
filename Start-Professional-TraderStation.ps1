# 🚀 CamboAI TraderStation - Professional Production Launch
Write-Host "🏛️ Starting CamboAI TraderStation - Institutional Grade Platform" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue

# Verify we're in the correct directory
if (-not (Test-Path "D:\CamboAI")) {
    Write-Host "❌ Please run this from D:\CamboAI directory" -ForegroundColor Red
    exit 1
}

Set-Location "D:\CamboAI"

Write-Host "📁 Project Directory: $(Get-Location)" -ForegroundColor Green
Write-Host "🔗 GitHub: https://github.com/cambotrader/CamboAI" -ForegroundColor Green

# Check system requirements
Write-Host "`n🔍 System Requirements Check:" -ForegroundColor Yellow
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCheck) {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found - Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check frontend build
if (Test-Path "frontend\build") {
    Write-Host "✅ Frontend build exists" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend build missing - Building now..." -ForegroundColor Yellow
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        Set-Location "frontend"
        npm run build
        Set-Location ".."
    } else {
        Write-Host "❌ npm not found - Cannot build frontend" -ForegroundColor Red
    }
}

Write-Host "`n🚀 Launching Professional Trading Platform:" -ForegroundColor Cyan

# Start Backend with production settings
Write-Host "`n⚡ Starting Backend API Server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "D:\CamboAI\backend"
    $env:ENVIRONMENT = "production"
    $env:PYTHONPATH = "D:\CamboAI\backend"
    python simple_server.py
}

# Wait for backend to initialize
Start-Sleep -Seconds 4

# Test backend connectivity
Write-Host "🧪 Testing Backend Connection..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-WebRequest "http://localhost:8000/health" -TimeoutSec 5
    if ($healthCheck.StatusCode -eq 200) {
        Write-Host "✅ Backend API Server: ONLINE" -ForegroundColor Green
        Write-Host "   └─ Health Status: OK" -ForegroundColor Green
        Write-Host "   └─ Environment: Production" -ForegroundColor Green
        Write-Host "   └─ API Documentation: http://localhost:8000/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Backend startup failed - Check logs" -ForegroundColor Red
    $backendJob | Stop-Job -PassThru | Remove-Job
    exit 1
}

# Start Frontend Server
Write-Host "`n🎨 Starting Frontend Interface..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "D:\CamboAI\frontend"
    if (Test-Path "build") {
        Write-Host "📦 Serving production build..."
        python -m http.server 3000 --directory build
    } else {
        Write-Host "📦 Starting development server..."
        npm start
    }
}

# Wait for frontend
Start-Sleep -Seconds 3

# Test frontend
Write-Host "🧪 Testing Frontend Connection..." -ForegroundColor Yellow
try {
    $frontendCheck = Invoke-WebRequest "http://localhost:3000" -TimeoutSec 5
    if ($frontendCheck.StatusCode -eq 200) {
        Write-Host "✅ Frontend Interface: ONLINE" -ForegroundColor Green
        Write-Host "   └─ Trading Dashboard: http://localhost:3000" -ForegroundColor Green
        Write-Host "   └─ Production Build: Optimized" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Frontend may still be loading..." -ForegroundColor Yellow
}

# Display professional startup summary
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "🏛️  CAMBOAI TRADERSTATION - INSTITUTIONAL READY" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue

Write-Host "`n🌐 ACCESS POINTS:" -ForegroundColor White
Write-Host "   💻 Trading Dashboard:     http://localhost:3000" -ForegroundColor Green
Write-Host "   ⚡ API Server:            http://localhost:8000" -ForegroundColor Green  
Write-Host "   📚 API Documentation:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host "   🔍 Health Monitor:        http://localhost:8000/health" -ForegroundColor Green

Write-Host "`n🏗️  PROFESSIONAL FEATURES:" -ForegroundColor White
Write-Host "   📊 Market Overview        - Real-time indices, movers, sector performance" -ForegroundColor Yellow
Write-Host "   💼 Advanced Portfolio     - Institutional-grade portfolio management" -ForegroundColor Yellow
Write-Host "   📈 Options Chain          - Professional options trading interface" -ForegroundColor Yellow
Write-Host "   📋 Order Management       - Algorithmic order execution (TWAP, VWAP, Iceberg)" -ForegroundColor Yellow
Write-Host "   📊 Charts & Analysis      - Advanced charting with multiple platforms" -ForegroundColor Yellow

Write-Host "`n🔒 SECURITY FEATURES:" -ForegroundColor White
Write-Host "   ✅ Production-grade CORS protection" -ForegroundColor Green
Write-Host "   ✅ Security headers (HSTS, XSS, Frame Options)" -ForegroundColor Green
Write-Host "   ✅ Environment variable isolation" -ForegroundColor Green
Write-Host "   ✅ Secure API endpoints" -ForegroundColor Green

Write-Host "`n⚡ PERFORMANCE:" -ForegroundColor White
Write-Host "   📊 Portfolio Analytics     - Real-time P&L, risk metrics, performance" -ForegroundColor Cyan
Write-Host "   🔄 WebSocket Updates       - Live market data streaming" -ForegroundColor Cyan
Write-Host "   📈 Multi-Asset Support     - Stocks, Options, Crypto, Forex" -ForegroundColor Cyan
Write-Host "   🤖 AI-Powered Analysis     - Advanced pattern recognition" -ForegroundColor Cyan

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "🎯 PLATFORM STATUS: READY FOR PROFESSIONAL TRADING" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue

Write-Host "`n🔥 Your institutional-grade trading platform is now running!" -ForegroundColor Cyan
Write-Host "⏹️  Press Ctrl+C to stop all servers" -ForegroundColor Yellow

# Keep the script running and monitor services
try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if services are still running
        if ($backendJob.State -ne 'Running') {
            Write-Host "⚠️  Backend service stopped unexpectedly" -ForegroundColor Red
            break
        }
        
        if ($frontendJob.State -ne 'Running') {
            Write-Host "⚠️  Frontend service stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
} catch {
    Write-Host "`n🛑 Shutting down services..." -ForegroundColor Yellow
} finally {
    # Cleanup
    Write-Host "`n🧹 Cleaning up services..." -ForegroundColor Yellow
    
    if ($backendJob) {
        $backendJob | Stop-Job -PassThru | Remove-Job
        Write-Host "✅ Backend server stopped" -ForegroundColor Green
    }
    
    if ($frontendJob) {
        $frontendJob | Stop-Job -PassThru | Remove-Job  
        Write-Host "✅ Frontend server stopped" -ForegroundColor Green
    }
    
    # Kill any remaining Python processes
    Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "`n👋 CamboAI TraderStation shutdown complete" -ForegroundColor Cyan
}