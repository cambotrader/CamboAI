#!/usr/bin/env powershell
# Cambo AI Trader Station - Database Migration Script

param(
    [string]$Action = "upgrade",  # upgrade, downgrade, current, history
    [string]$Revision = "head",   # head, base, or specific revision
    [string]$Environment = "development",
    [switch]$AutoGenerate = $false,
    [string]$Message = "",
    [switch]$Verbose = $false
)

Write-Host "🗄️ Cambo AI Trader Station - Database Migration" -ForegroundColor Green
Write-Host "Action: $Action | Revision: $Revision | Environment: $Environment" -ForegroundColor Yellow

# Set error action preference
$ErrorActionPreference = "Stop"

try {
    # Load environment variables
    if (Test-Path ".env.$Environment") {
        Write-Host "📁 Loading environment variables..." -ForegroundColor Blue
        Get-Content ".env.$Environment" | ForEach-Object {
            if ($_ -match "^([^=]+)=(.*)$") {
                $name = $matches[1]
                $value = $matches[2]
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }

    # Change to backend directory
    Set-Location "backend"

    # Validate database connection
    Write-Host "🔍 Validating database connection..." -ForegroundColor Blue
    $dbUrl = [Environment]::GetEnvironmentVariable("DATABASE_URL")
    if (-not $dbUrl) {
        Write-Error "DATABASE_URL environment variable is not set!"
        exit 1
    }
    Write-Host "✅ Database URL configured" -ForegroundColor Green

    # Execute the requested action
    switch ($Action.ToLower()) {
        "upgrade" {
            Write-Host "⬆️ Running database upgrade to $Revision..." -ForegroundColor Blue
            alembic upgrade $Revision
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Database upgrade completed successfully" -ForegroundColor Green
            } else {
                Write-Error "Database upgrade failed!"
                exit 1
            }
        }
        
        "downgrade" {
            Write-Host "⬇️ Running database downgrade to $Revision..." -ForegroundColor Blue
            $confirmation = Read-Host "Are you sure you want to downgrade? This may cause data loss. (y/N)"
            if ($confirmation -eq "y" -or $confirmation -eq "Y") {
                alembic downgrade $Revision
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Database downgrade completed" -ForegroundColor Green
                } else {
                    Write-Error "Database downgrade failed!"
                    exit 1
                }
            } else {
                Write-Host "❌ Downgrade cancelled" -ForegroundColor Yellow
            }
        }
        
        "current" {
            Write-Host "📍 Current database revision:" -ForegroundColor Blue
            alembic current
        }
        
        "history" {
            Write-Host "📜 Migration history:" -ForegroundColor Blue
            alembic history --verbose
        }
        
        "autogenerate" {
            if (-not $AutoGenerate) {
                Write-Error "Use -AutoGenerate flag to create new migration"
                exit 1
            }
            
            if (-not $Message) {
                $Message = Read-Host "Enter migration message"
            }
            
            Write-Host "🔧 Generating new migration: $Message" -ForegroundColor Blue
            alembic revision --autogenerate -m $Message
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Migration file generated successfully" -ForegroundColor Green
                Write-Host "💡 Review the generated migration file before running upgrade" -ForegroundColor Yellow
            } else {
                Write-Error "Migration generation failed!"
                exit 1
            }
        }
        
        "init" {
            Write-Host "🏗️ Initializing Alembic..." -ForegroundColor Blue
            if (Test-Path "alembic") {
                Write-Warning "Alembic directory already exists. Use 'reset' to reinitialize."
            } else {
                alembic init alembic
                Write-Host "✅ Alembic initialized" -ForegroundColor Green
            }
        }
        
        "reset" {
            Write-Host "🔄 Resetting migration environment..." -ForegroundColor Blue
            $confirmation = Read-Host "This will delete all migration files. Are you sure? (y/N)"
            if ($confirmation -eq "y" -or $confirmation -eq "Y") {
                Remove-Item -Recurse -Force "alembic" -ErrorAction SilentlyContinue
                alembic init alembic
                Write-Host "✅ Migration environment reset" -ForegroundColor Green
            }
        }
        
        "status" {
            Write-Host "📊 Database migration status:" -ForegroundColor Blue
            
            # Check if database exists and is accessible
            try {
                alembic current
                Write-Host "✅ Database is accessible" -ForegroundColor Green
            } catch {
                Write-Host "❌ Database connection failed" -ForegroundColor Red
            }
            
            # Show pending migrations
            Write-Host "`n📋 Checking for pending migrations..." -ForegroundColor Blue
            $currentRev = (alembic current) -replace ".*\((.+)\).*", '$1'
            $headRev = (alembic heads) -replace ".*\((.+)\).*", '$1'
            
            if ($currentRev -eq $headRev) {
                Write-Host "✅ Database is up to date" -ForegroundColor Green
            } else {
                Write-Host "⚠️ Database needs migration from $currentRev to $headRev" -ForegroundColor Yellow
            }
        }
        
        default {
            Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
            Write-Host "Available actions: upgrade, downgrade, current, history, autogenerate, init, reset, status" -ForegroundColor Yellow
            exit 1
        }
    }

    # Show final status
    if ($Action -in @("upgrade", "downgrade")) {
        Write-Host "`n📊 Final database status:" -ForegroundColor Cyan
        alembic current
    }

} catch {
    Write-Host "`n❌ Migration operation failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    # Return to original directory
    Set-Location ".."
}

Write-Host "`n🎉 Migration operation completed!" -ForegroundColor Green
