# Test script to verify system setup
Write-Host "=== CamboStation Setup Test ===" -ForegroundColor Cyan

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found!" -ForegroundColor Red
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found!" -ForegroundColor Red
}

# Check NPM
Write-Host "Checking NPM..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>&1
    Write-Host "NPM: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "NPM not found!" -ForegroundColor Red
}

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker not found!" -ForegroundColor Red
}

# Check current directory
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Blue

# Check if backend venv exists
if (Test-Path "backend\venv") {
    Write-Host "Backend virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "Backend virtual environment NOT found" -ForegroundColor Red
}

# Check if frontend node_modules exists
if (Test-Path "frontend\node_modules") {
    Write-Host "Frontend node_modules exists" -ForegroundColor Green
} else {
    Write-Host "Frontend node_modules NOT found" -ForegroundColor Red
}

Write-Host "=== Test Complete ===" -ForegroundColor Cyan
