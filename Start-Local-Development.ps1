# 🚀 CamboAI TraderStation Local Development Starter
Write-Host "🔥 Starting CamboAI TraderStation Locally..." -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "D:\CamboAI")) {
    Write-Host "❌ Please run this from D:\CamboAI directory" -ForegroundColor Red
    exit 1
}

Set-Location "D:\CamboAI"

Write-Host "📁 Current Directory: $(Get-Location)" -ForegroundColor Green

# Start Backend
Write-Host "`n🔧 Starting Backend Server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "D:\CamboAI\backend"
    $env:ENVIRONMENT = "development"
    python simple_server.py
}

# Wait for backend to start
Start-Sleep -Seconds 3

# Test backend
try {
    $healthCheck = Invoke-WebRequest "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ Backend started successfully on http://localhost:8000" -ForegroundColor Green
    Write-Host "   Status: $($healthCheck.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend failed to start" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    return
}

# Start Frontend
Write-Host "`n🎨 Starting Frontend..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "D:\CamboAI\frontend"
    if (Test-Path "build") {
        Write-Host "Serving from build directory..."
        python -m http.server 3000 --directory build
    } else {
        Write-Host "Build directory not found, starting development server..."
        npm start
    }
}

# Wait for frontend
Start-Sleep -Seconds 3

# Test frontend
try {
    $frontendCheck = Invoke-WebRequest "http://localhost:3000" -TimeoutSec 5
    Write-Host "✅ Frontend started successfully on http://localhost:3000" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend failed to start" -ForegroundColor Red
}

Write-Host "`n🎉 CamboAI is running locally!" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "⚡ Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n⏹️  Press Ctrl+C to stop servers" -ForegroundColor Yellow

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`n🛑 Stopping servers..." -ForegroundColor Red
    $backendJob | Stop-Job -PassThru | Remove-Job
    $frontendJob | Stop-Job -PassThru | Remove-Job
    Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force -ErrorAction SilentlyContinue
}