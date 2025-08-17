#!/usr/bin/env pwsh
# 🚀 FAST PRODUCTION SERVER LAUNCHER (No Docker)

Write-Host "🚀 Starting CamboAI Production Server..." -ForegroundColor Green

# Set production environment
$env:ENVIRONMENT = "production"
$env:FRONTEND_ORIGIN = "https://your-frontend-domain.com"  # Update this

# Navigate to backend
Set-Location backend

Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install --no-cache-dir -r requirements.simple.txt

Write-Host "🔥 Starting production server..." -ForegroundColor Green
Write-Host "✅ Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "✅ API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "✅ Health check: http://localhost:8000/health" -ForegroundColor Cyan

# Start the server
python simple_server.py