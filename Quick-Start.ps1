#!/usr/bin/env powershell
# Simple Cambo AI Trader Station Startup

Write-Host "🚀 CAMBO AI TRADER STATION" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

Write-Host "`n1. Stopping existing containers..." -ForegroundColor Cyan
docker-compose -f docker-compose.prod.yml down 2>$null

Write-Host "`n2. Starting production environment..." -ForegroundColor Cyan
docker-compose -f docker-compose.prod.yml up -d --build

Write-Host "`n3. Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

Write-Host "`n🎉 CAMBO AI TRADER STATION IS RUNNING!" -ForegroundColor Green
Write-Host "`nAccess URLs:" -ForegroundColor Yellow
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  Dashboard:    http://localhost:8501" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White

Write-Host "`nManagement Commands:" -ForegroundColor Yellow
Write-Host "  View logs:    docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Gray
Write-Host "  Stop all:     docker-compose -f docker-compose.prod.yml down" -ForegroundColor Gray
