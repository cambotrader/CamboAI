#!/usr/bin/env powershell
# Cambo AI Trader Station - Status Check

Write-Host "🔍 CAMBO AI TRADER STATION - STATUS CHECK" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

Write-Host "`n📊 Checking services..." -ForegroundColor Cyan

# Check if backend is running
Write-Host "`n🔧 Backend API (Port 8000):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Backend is running - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not responding" -ForegroundColor Red
}

# Check if frontend is running
Write-Host "`n⚛️ Frontend (Port 3000):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Frontend is running - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend is not responding" -ForegroundColor Red
}

# Check running processes
Write-Host "`n🔍 Related Processes:" -ForegroundColor Yellow
$processes = Get-Process | Where-Object { $_.ProcessName -match "uvicorn|node|python" }
if ($processes) {
    Write-Host "Found running processes:" -ForegroundColor Green
    $processes | Select-Object ProcessName, Id | Format-Table -AutoSize
} else {
    Write-Host "❌ No related processes found" -ForegroundColor Red
}

# Check listening ports
Write-Host "`n🌐 Listening Ports:" -ForegroundColor Yellow
$ports = @(3000, 8000)
foreach ($port in $ports) {
    try {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Host "✅ Port $port is in use" -ForegroundColor Green
        } else {
            Write-Host "❌ Port $port is not in use" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Port $port is not in use" -ForegroundColor Red
    }
}

Write-Host "`n🌟 Access URLs:" -ForegroundColor Cyan
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n💡 Quick Start Commands:" -ForegroundColor Yellow
Write-Host "  Backend:  cd backend; uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host "  Frontend: cd frontend; npm start" -ForegroundColor Gray
