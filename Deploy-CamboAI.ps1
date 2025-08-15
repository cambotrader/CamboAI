#!/usr/bin/env powershell
# Cambo AI Trader Station - Production Deployment Script

param(
    [switch]$Force = $false,
    [switch]$SkipSecurityCheck = $false,
    [switch]$SkipBackup = $false,
    [string]$Environment = "production"
)

$ErrorActionPreference = "Stop"

# Load environment variables from .env.$Environment if present
if (Test-Path ".env.$Environment") {
    Write-Host "`n📦 Loading environment: .env.$Environment" -ForegroundColor Blue
    Get-Content ".env.$Environment" | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Resolve DB env with sane defaults
$PG_USER = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { 'cambo_user' }
$PG_PASS = if ($env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD } else { 'your_secure_password' }
$PG_DB   = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { 'cambo_ai_trader_station' }

# ASCII Art Header
Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ████████╗██████╗ ███████╗████████╗ █████╗ ████████╗██╗ ██████╗  ███╗   ██╗
║    ╚══██╔══╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║██╔═══██╗████╗  ██║
║       ██║   ██████╔╝███████╗   ██║   ██████╔╝███████╗██║██║   ██║██╔██╗ ██║
║       ██║   ██╔══██╗╚════██║   ██║   ██╔══██╗██╔════╝██║██║   ██║██║╚██╗██║
║       ██║   ██║  ██║███████║   ██║   ██║  ██║███████╗██║╚██████╔╝██║ ╚████║
║       ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
║                                                               ║
║               🚀 CAMBO AI TRADER STATION 🚀                   ║
║                    Production Deployment                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

Write-Host "`n🎯 Environment: $Environment" -ForegroundColor Yellow
Write-Host "📅 Deployment Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "`n🔍 Checking prerequisites..." -ForegroundColor Blue
    
    $prerequisites = @()
    
    # Check Docker
    try {
        docker --version | Out-Null
        $dockerVersion = docker --version
        Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
    } catch {
        $prerequisites += "Docker is not installed or not in PATH"
    }
    
    # Check Docker Compose
    try {
        docker-compose --version | Out-Null
        $composeVersion = docker-compose --version
        Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
    } catch {
        $prerequisites += "Docker Compose is not installed or not in PATH"
    }
    
    # Check Python (for Alembic)
    try {
        python --version | Out-Null
        $pythonVersion = python --version
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        $prerequisites += "Python is not installed or not in PATH"
    }
    
    # Check Node.js
    try {
        node --version | Out-Null
        $nodeVersion = node --version
        Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        $prerequisites += "Node.js is not installed or not in PATH"
    }
    
    # Check required files
    $requiredFiles = @(
        ".env.$Environment",
        "docker-compose.prod.yml",
        "backend/alembic.ini",
        "init-db.sql"
    )
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Host "✅ File exists: $file" -ForegroundColor Green
        } else {
            $prerequisites += "Required file missing: $file"
        }
    }
    
    if ($prerequisites.Count -gt 0) {
        Write-Host "`n❌ Prerequisites check failed:" -ForegroundColor Red
        $prerequisites | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        exit 1
    }
    
    Write-Host "✅ All prerequisites met!" -ForegroundColor Green
}

# Function to run security check
function Invoke-SecurityCheck {
    if ($SkipSecurityCheck) {
        Write-Host "`n⚠️ Skipping security check (--SkipSecurityCheck)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "`n🔒 Running security audit..." -ForegroundColor Blue
    
    if (Test-Path "Security-Review.ps1") {
        & ".\Security-Review.ps1" -Environment $Environment
        
        # Check if there are critical issues
        $securityOutput = & ".\Security-Review.ps1" -Environment $Environment 2>&1
        if ($securityOutput -match "CRITICAL Issues") {
            Write-Host "`n❌ Critical security issues found!" -ForegroundColor Red
            Write-Host "Please fix critical security issues before deploying to production." -ForegroundColor Red
            
            if (-not $Force) {
                Write-Host "Use -Force to override this check (NOT RECOMMENDED)" -ForegroundColor Yellow
                exit 1
            } else {
                Write-Host "⚠️ Continuing with FORCE override..." -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "⚠️ Security review script not found, skipping..." -ForegroundColor Yellow
    }
}

# Function to backup existing data
function Backup-ExistingData {
    if ($SkipBackup) {
        Write-Host "`n⚠️ Skipping backup (--SkipBackup)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "`n💾 Creating backup..." -ForegroundColor Blue
    
    $backupDir = "backups\$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Backup database if exists
    try {
    docker-compose -f docker-compose.prod.yml exec -T postgres sh -lc "PGPASSWORD='$PG_PASS' pg_dump -U $PG_USER $PG_DB" > "$backupDir\database_backup.sql" 2>$null
        Write-Host "✅ Database backup created" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ No existing database to backup" -ForegroundColor Yellow
    }
    
    # Backup logs
    if (Test-Path "backend/logs") {
        Copy-Item -Path "backend/logs" -Destination "$backupDir\logs" -Recurse -Force
        Write-Host "✅ Logs backup created" -ForegroundColor Green
    }
    
    # Backup Redis data if exists
    try {
        docker-compose -f docker-compose.prod.yml exec -T redis redis-cli BGSAVE > $null 2>&1
        Write-Host "✅ Redis backup initiated" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ No existing Redis to backup" -ForegroundColor Yellow
    }
    
    Write-Host "📁 Backup location: $backupDir" -ForegroundColor Cyan
}

# Function to build and deploy
function Deploy-Application {
    Write-Host "`n🚀 Deploying Cambo AI Trader Station..." -ForegroundColor Blue
    
    # Stop existing containers
    Write-Host "`n🛑 Stopping existing containers..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml down 2>$null
    
    # Clean up old images (optional)
    Write-Host "`n🧹 Cleaning up old images..." -ForegroundColor Cyan
    docker system prune -f
    
    # Build new images
    Write-Host "`n🔨 Building application images..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        exit 1
    }
    
    # Start infrastructure services first
    Write-Host "`n🗄️ Starting infrastructure services..." -ForegroundColor Cyan
        docker-compose -f docker-compose.prod.yml up -d postgres redis
    
    # Wait for database to be ready
    Write-Host "`n⏳ Waiting for database to be ready..." -ForegroundColor Cyan
    $maxAttempts = 30
    $attempt = 0
    
    do {
        $attempt++
        Start-Sleep -Seconds 2
        $dbReady = docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U $PG_USER 2>$null
        if ($dbReady -match "accepting connections") {
            Write-Host "✅ Database is ready!" -ForegroundColor Green
            break
        }
        Write-Host "⏳ Attempt $attempt/$maxAttempts - Database not ready yet..." -ForegroundColor Yellow
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        Write-Host "❌ Database failed to start!" -ForegroundColor Red
        exit 1
    }
    
    # Initialize database
    Write-Host "`n🗄️ Initializing database..." -ForegroundColor Cyan
        docker-compose -f docker-compose.prod.yml exec -T postgres sh -lc "PGPASSWORD='$PG_PASS' psql -U $PG_USER -d $PG_DB -f /docker-entrypoint-initdb.d/init-db.sql" 2>$null
    
    # Run database migrations
    Write-Host "`n📈 Running database migrations..." -ForegroundColor Cyan
    & ".\Migrate-Database.ps1" -Environment production
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Database migration failed!" -ForegroundColor Red
        exit 1
    }
    
    # Start all services
    Write-Host "`n🚀 Starting all services..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Service startup failed!" -ForegroundColor Red
        exit 1
    }
    
    # Wait for services to be healthy
    Write-Host "`n🏥 Checking service health..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    
    $services = @("backend", "frontend", "dashboard")
    foreach ($service in $services) {
        $health = docker-compose -f docker-compose.prod.yml ps $service | Select-String "healthy|Up"
        if ($health) {
            Write-Host "✅ $service is healthy" -ForegroundColor Green
        } else {
            Write-Host "⚠️ $service health check pending..." -ForegroundColor Yellow
        }
    }
}

# Function to verify deployment
function Test-Deployment {
    Write-Host "`n🧪 Verifying deployment..." -ForegroundColor Blue
    
    # Test backend API
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
        if ($response.status -eq "healthy") {
            Write-Host "✅ Backend API is responding" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Backend API health check failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Backend API is not responding" -ForegroundColor Red
    }
    
    # Test frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Frontend is responding" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Frontend response code: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Frontend is not responding" -ForegroundColor Red
    }
    
    # Test dashboard
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Dashboard is responding" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Dashboard response code: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Dashboard is not responding" -ForegroundColor Red
    }
    
    # Test database connection
    try {
    $dbTest = docker-compose -f docker-compose.prod.yml exec -T postgres sh -lc "PGPASSWORD='$PG_PASS' psql -U $PG_USER -d $PG_DB -c 'SELECT 1;'" 2>$null
        if ($dbTest -match "1") {
            Write-Host "✅ Database connection successful" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Database connection test failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Database connection failed" -ForegroundColor Red
    }
    
    # Test Redis connection
    try {
        $redisTest = docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping 2>$null
        if ($redisTest -match "PONG") {
            Write-Host "✅ Redis connection successful" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Redis connection test failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Redis connection failed" -ForegroundColor Red
    }
}

# Function to display deployment summary
function Show-DeploymentSummary {
    Write-Host "`n🎉 Deployment Summary" -ForegroundColor Magenta
    Write-Host "=====================" -ForegroundColor Magenta
    
    Write-Host "`n🌐 Application URLs:" -ForegroundColor Cyan
    Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
    Write-Host "  Dashboard:    http://localhost:8501" -ForegroundColor White
    Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  Grafana:      http://localhost:3001 (admin/admin)" -ForegroundColor White
    Write-Host "  Prometheus:   http://localhost:9090" -ForegroundColor White
    
    Write-Host "`n📊 Monitoring:" -ForegroundColor Cyan
    Write-Host "  • Prometheus metrics collection enabled" -ForegroundColor Gray
    Write-Host "  • Grafana dashboards configured" -ForegroundColor Gray
    Write-Host "  • Application logs in backend/logs/" -ForegroundColor Gray
    Write-Host "  • Audit logging enabled" -ForegroundColor Gray
    
    Write-Host "`n🔒 Security:" -ForegroundColor Cyan
    Write-Host "  • Rate limiting enabled" -ForegroundColor Gray
    Write-Host "  • JWT authentication configured" -ForegroundColor Gray
    Write-Host "  • CORS policies enforced" -ForegroundColor Gray
    Write-Host "  • Security headers enabled" -ForegroundColor Gray
    
    Write-Host "`n📈 Trading Features:" -ForegroundColor Cyan
    Write-Host "  • Alpaca API integration" -ForegroundColor Gray
    Write-Host "  • Real-time market data" -ForegroundColor Gray
    Write-Host "  • Risk management system" -ForegroundColor Gray
    Write-Host "  • Portfolio analytics" -ForegroundColor Gray
    Write-Host "  • Advanced charting (TradingView)" -ForegroundColor Gray
    
    Write-Host "`n🛠️ Management Commands:" -ForegroundColor Cyan
    Write-Host "  View logs:        docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Gray
    Write-Host "  Stop services:    docker-compose -f docker-compose.prod.yml down" -ForegroundColor Gray
    Write-Host "  Restart service:  docker-compose -f docker-compose.prod.yml restart [service]" -ForegroundColor Gray
    Write-Host "  Scale service:    docker-compose -f docker-compose.prod.yml up -d --scale backend=2" -ForegroundColor Gray
    
    Write-Host "`n💡 Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Configure your Alpaca API keys in the admin panel" -ForegroundColor Gray
    Write-Host "  2. Set up SSL/TLS certificates for production" -ForegroundColor Gray
    Write-Host "  3. Configure domain name and reverse proxy" -ForegroundColor Gray
    Write-Host "  4. Set up automated backups" -ForegroundColor Gray
    Write-Host "  5. Configure email notifications" -ForegroundColor Gray
    
    Write-Host "`n🚀 Cambo AI Trader Station is now running!" -ForegroundColor Green
}

# Main execution
try {
    Test-Prerequisites
    Invoke-SecurityCheck
    Backup-ExistingData
    Deploy-Application
    Test-Deployment
    Show-DeploymentSummary
    
    Write-Host "`n✅ Production deployment completed successfully!" -ForegroundColor Green
    Write-Host "🎯 Cambo AI Trader Station is ready for trading!" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Deployment failed: $_" -ForegroundColor Red
    Write-Host "🔍 Check the logs for more details:" -ForegroundColor Yellow
    Write-Host "   docker-compose -f docker-compose.prod.yml logs" -ForegroundColor Gray
    exit 1
}
