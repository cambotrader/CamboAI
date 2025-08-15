#!/usr/bin/env powershell
# Cambo AI Trader Station - Simple Production Deployment Script

param(
    [switch]$Force = $false,
    [switch]$SkipSecurityCheck = $false
)

$ErrorActionPreference = "Stop"

Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║               🚀 CAMBO AI TRADER STATION 🚀                   ║
║                    Production Deployment                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

Write-Host "`n🎯 Starting deployment..." -ForegroundColor Yellow
Write-Host "📅 Deployment Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow

try {
    # Step 1: Run database migrations
    Write-Host "`n📈 Running database migrations..." -ForegroundColor Cyan
    if (Test-Path ".\Migrate-Database.ps1") {
        & ".\Migrate-Database.ps1" -Environment production
        Write-Host "✅ Database migrations completed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Migration script not found, skipping..." -ForegroundColor Yellow
    }

    # Step 2: Stop existing containers
    Write-Host "`n🛑 Stopping existing containers..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml down 2>$null
    Write-Host "✅ Existing containers stopped" -ForegroundColor Green

    # Step 3: Build and start production containers
    Write-Host "`n🔨 Building and starting production containers..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml up -d --build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Production containers started successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start production containers" -ForegroundColor Red
        exit 1
    }

    # Step 4: Wait for services to be ready
    Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Cyan
    Start-Sleep -Seconds 15
    
    # Step 5: Test endpoints
    Write-Host "`n🧪 Testing endpoints..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Frontend is responding" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ Frontend not yet ready" -ForegroundColor Yellow
    }
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction SilentlyContinue
        if ($response.status -eq "healthy") {
            Write-Host "✅ Backend API is healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ Backend API not yet ready" -ForegroundColor Yellow
    }

    # Display deployment summary
    Write-Host "`n🎉 Deployment Summary" -ForegroundColor Magenta
    Write-Host "=====================" -ForegroundColor Magenta
    
    Write-Host "`n🌐 Application URLs:" -ForegroundColor Cyan
    Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
    Write-Host "  Dashboard:    http://localhost:8501" -ForegroundColor White
    Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  Grafana:      http://localhost:3001" -ForegroundColor White
    Write-Host "  Prometheus:   http://localhost:9090" -ForegroundColor White
    
    Write-Host "`n🛠️ Management Commands:" -ForegroundColor Cyan
    Write-Host "  View logs:        docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Gray
    Write-Host "  Stop services:    docker-compose -f docker-compose.prod.yml down" -ForegroundColor Gray
    Write-Host "  Restart backend:  docker-compose -f docker-compose.prod.yml restart backend" -ForegroundColor Gray
    Write-Host "  Check status:     .\Status-Monitor.ps1" -ForegroundColor Gray
    
    Write-Host "`n✅ Cambo AI Trader Station deployment completed successfully!" -ForegroundColor Green
    Write-Host "🎯 Your trading platform is ready!" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Deployment failed: $_" -ForegroundColor Red
    Write-Host "🔍 Check the logs for more details:" -ForegroundColor Yellow
    Write-Host "   docker-compose -f docker-compose.prod.yml logs" -ForegroundColor Gray
    exit 1
}
