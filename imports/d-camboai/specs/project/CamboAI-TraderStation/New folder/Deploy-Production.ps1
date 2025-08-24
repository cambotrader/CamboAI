#!/usr/bin/env powershell
# Cambo AI Trader Station - Production Deployment Script

param(
    [string]$Environment = "production",
    [switch]$SkipMigration = $false,
    [switch]$SkipBackup = $false,
    [switch]$Verbose = $false
)

Write-Host "🚀 Deploying Cambo AI Trader Station v2.0.0" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow

# Set error action preference
$ErrorActionPreference = "Stop"

try {
    # Load environment variables
    if (Test-Path ".env.$Environment") {
        Write-Host "📁 Loading environment variables from .env.$Environment" -ForegroundColor Blue
        Get-Content ".env.$Environment" | ForEach-Object {
            if ($_ -match "^([^=]+)=(.*)$") {
                $name = $matches[1]
                $value = $matches[2]
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
                if ($Verbose) {
                    Write-Host "  Set $name" -ForegroundColor Gray
                }
            }
        }
    } else {
        Write-Warning "Environment file .env.$Environment not found!"
        exit 1
    }

    # Validate required environment variables
    Write-Host "🔍 Validating environment variables..." -ForegroundColor Blue
    $requiredVars = @(
        "DATABASE_URL",
        "REDIS_URL", 
        "SECRET_KEY",
        "ALPACA_API_KEY",
        "ALPACA_SECRET_KEY"
    )

    foreach ($var in $requiredVars) {
        if (-not [Environment]::GetEnvironmentVariable($var)) {
            Write-Error "Required environment variable $var is not set!"
            exit 1
        }
    }
    Write-Host "✅ Environment variables validated" -ForegroundColor Green

    # Check if Docker is running
    Write-Host "🐳 Checking Docker status..." -ForegroundColor Blue
    try {
        docker info | Out-Null
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } catch {
        Write-Error "Docker is not running. Please start Docker Desktop."
        exit 1
    }

    # Create backup if not skipped
    if (-not $SkipBackup -and $Environment -eq "production") {
        Write-Host "💾 Creating database backup..." -ForegroundColor Blue
        $backupFile = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
        
        # Extract database connection details
        $dbUrl = [Environment]::GetEnvironmentVariable("DATABASE_URL")
        if ($dbUrl -match "postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)") {
            $dbUser = $matches[1]
            $dbPass = $matches[2]
            $dbHost = $matches[3]
            $dbPort = $matches[4]
            $dbName = $matches[5]
            
            $env:PGPASSWORD = $dbPass
            pg_dump -h $dbHost -p $dbPort -U $dbUser -d $dbName -f "backups/$backupFile"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Database backup created: $backupFile" -ForegroundColor Green
            } else {
                Write-Warning "Database backup failed, but continuing with deployment"
            }
        }
    }

    # Stop existing containers
    Write-Host "🛑 Stopping existing containers..." -ForegroundColor Blue
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    Write-Host "✅ Containers stopped" -ForegroundColor Green

    # Pull latest images
    Write-Host "📥 Pulling latest images..." -ForegroundColor Blue
    docker-compose -f docker-compose.prod.yml pull
    Write-Host "✅ Images updated" -ForegroundColor Green

    # Build and start services
    Write-Host "🏗️ Building and starting services..." -ForegroundColor Blue
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Wait for services to be healthy
    Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Blue
    $maxWaitTime = 300  # 5 minutes
    $waitTime = 0
    
    do {
        Start-Sleep -Seconds 10
        $waitTime += 10
        
        $healthStatus = docker-compose -f docker-compose.prod.yml ps --format json | ConvertFrom-Json
        $unhealthyServices = $healthStatus | Where-Object { $_.Health -ne "healthy" -and $_.Health -ne "" }
        
        if ($unhealthyServices.Count -eq 0) {
            Write-Host "✅ All services are healthy" -ForegroundColor Green
            break
        }
        
        if ($waitTime -ge $maxWaitTime) {
            Write-Warning "Services did not become healthy within $maxWaitTime seconds"
            break
        }
        
        Write-Host "⏳ Waiting for services... ($waitTime/$maxWaitTime seconds)" -ForegroundColor Yellow
    } while ($true)

    # Run database migrations if not skipped
    if (-not $SkipMigration) {
        Write-Host "🗄️ Running database migrations..." -ForegroundColor Blue
        docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database migrations completed" -ForegroundColor Green
        } else {
            Write-Error "Database migrations failed!"
            exit 1
        }
    }

    # Verify deployment
    Write-Host "🔍 Verifying deployment..." -ForegroundColor Blue
    
    # Check backend health
    $maxRetries = 10
    $retryCount = 0
    do {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
            if ($response.status -eq "healthy") {
                Write-Host "✅ Backend is healthy" -ForegroundColor Green
                break
            }
        } catch {
            $retryCount++
            if ($retryCount -ge $maxRetries) {
                Write-Warning "Backend health check failed after $maxRetries attempts"
                break
            }
            Start-Sleep -Seconds 5
        }
    } while ($retryCount -lt $maxRetries)

    # Check frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Frontend is accessible" -ForegroundColor Green
        }
    } catch {
        Write-Warning "Frontend accessibility check failed"
    }

    # Display service URLs
    Write-Host "`n🌐 Service URLs:" -ForegroundColor Cyan
    Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs:    http://localhost:8000/api/docs" -ForegroundColor White
    Write-Host "  Grafana:     http://localhost:3001 (admin/admin123)" -ForegroundColor White
    Write-Host "  Prometheus:  http://localhost:9090" -ForegroundColor White

    # Display container status
    Write-Host "`n📊 Container Status:" -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml ps

    Write-Host "`n🎉 Deployment completed successfully!" -ForegroundColor Green
    Write-Host "💡 Check the logs with: docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Yellow

} catch {
    Write-Host "`n❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Show recent logs for debugging
    Write-Host "`n📋 Recent logs:" -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml logs --tail=50
    
    exit 1
}
