#!/usr/bin/env powershell
# Cambo AI Trader Station - Status Monitoring Script

param(
    [switch]$Watch = $false,
    [int]$Interval = 10,
    [switch]$Detailed = $false,
    [switch]$Export = $false
)

function Get-ServiceStatus {
    $services = @()
    
    # Get Docker Compose services
    try {
        $composeServices = docker-compose -f docker-compose.prod.yml ps --format json 2>$null | ConvertFrom-Json
        
        foreach ($service in $composeServices) {
            $status = [PSCustomObject]@{
                Name = $service.Service
                Status = $service.State
                Health = $service.Health
                Ports = $service.Publishers
                Uptime = $service.RunningFor
                Image = $service.Image
            }
            $services += $status
        }
    } catch {
        Write-Host "⚠️ Unable to get Docker Compose status" -ForegroundColor Yellow
    }
    
    return $services
}

function Test-ServiceEndpoints {
    $endpoints = @(
        @{ Name = "Frontend"; URL = "http://localhost:3000"; Expected = 200 },
        @{ Name = "Backend API"; URL = "http://localhost:8000/health"; Expected = 200 },
        @{ Name = "Dashboard"; URL = "http://localhost:8501"; Expected = 200 },
        @{ Name = "API Docs"; URL = "http://localhost:8000/docs"; Expected = 200 },
        @{ Name = "Prometheus"; URL = "http://localhost:9090"; Expected = 200 },
        @{ Name = "Grafana"; URL = "http://localhost:3001"; Expected = 200 }
    )
    
    $results = @()
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.URL -TimeoutSec 5 -UseBasicParsing
            $status = if ($response.StatusCode -eq $endpoint.Expected) { "✅ OK" } else { "⚠️ Unexpected" }
            $responseTime = $response.Headers.'X-Response-Time'
            
            $results += [PSCustomObject]@{
                Service = $endpoint.Name
                Status = $status
                ResponseCode = $response.StatusCode
                ResponseTime = if ($responseTime) { $responseTime } else { "N/A" }
                URL = $endpoint.URL
            }
        } catch {
            $results += [PSCustomObject]@{
                Service = $endpoint.Name
                Status = "❌ Down"
                ResponseCode = "N/A"
                ResponseTime = "N/A"
                URL = $endpoint.URL
            }
        }
    }
    
    return $results
}

function Get-ResourceUsage {
    $resources = @()
    
    try {
        $stats = docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
        $lines = $stats -split "`n" | Select-Object -Skip 1
        
        foreach ($line in $lines) {
            if ($line.Trim()) {
                $parts = $line -split "`t"
                if ($parts.Count -ge 5) {
                    $resources += [PSCustomObject]@{
                        Container = $parts[0]
                        CPU = $parts[1]
                        Memory = $parts[2]
                        Network = $parts[3]
                        BlockIO = $parts[4]
                    }
                }
            }
        }
    } catch {
        Write-Host "⚠️ Unable to get resource usage" -ForegroundColor Yellow
    }
    
    return $resources
}

function Get-SystemMetrics {
    $metrics = @{}
    
    # Database metrics
    try {
        $dbSize = docker-compose -f docker-compose.prod.yml exec -T postgres psql -U cambo_user -d cambo_ai_trader -c "SELECT pg_size_pretty(pg_database_size('cambo_ai_trader'));" -t 2>$null
        $metrics.DatabaseSize = $dbSize.Trim()
        
        $dbConnections = docker-compose -f docker-compose.prod.yml exec -T postgres psql -U cambo_user -d cambo_ai_trader -c "SELECT count(*) FROM pg_stat_activity;" -t 2>$null
        $metrics.DatabaseConnections = $dbConnections.Trim()
    } catch {
        $metrics.DatabaseSize = "N/A"
        $metrics.DatabaseConnections = "N/A"
    }
    
    # Redis metrics
    try {
        $redisInfo = docker-compose -f docker-compose.prod.yml exec -T redis redis-cli info memory 2>$null
        $redisMemory = ($redisInfo | Select-String "used_memory_human:").Line.Split(":")[1]
        $metrics.RedisMemory = $redisMemory
        
        $redisKeys = docker-compose -f docker-compose.prod.yml exec -T redis redis-cli dbsize 2>$null
        $metrics.RedisKeys = $redisKeys.Trim()
    } catch {
        $metrics.RedisMemory = "N/A"
        $metrics.RedisKeys = "N/A"
    }
    
    # Log file sizes
    try {
        if (Test-Path "backend/logs/app.log") {
            $appLogSize = (Get-Item "backend/logs/app.log").Length / 1MB
            $metrics.AppLogSize = "{0:N2} MB" -f $appLogSize
        } else {
            $metrics.AppLogSize = "N/A"
        }
        
        if (Test-Path "backend/logs/error.log") {
            $errorLogSize = (Get-Item "backend/logs/error.log").Length / 1MB
            $metrics.ErrorLogSize = "{0:N2} MB" -f $errorLogSize
        } else {
            $metrics.ErrorLogSize = "N/A"
        }
    } catch {
        $metrics.AppLogSize = "N/A"
        $metrics.ErrorLogSize = "N/A"
    }
    
    return $metrics
}

function Get-TradingMetrics {
    $metrics = @{}
    
    try {
        # This would typically come from your backend API
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics" -TimeoutSec 5 2>$null
        
        $metrics.ActivePositions = if ($response.active_positions) { $response.active_positions } else { "N/A" }
        $metrics.DailyPnL = if ($response.daily_pnl) { $response.daily_pnl } else { "N/A" }
        $metrics.TotalTrades = if ($response.total_trades) { $response.total_trades } else { "N/A" }
        $metrics.WinRate = if ($response.win_rate) { "$($response.win_rate)%" } else { "N/A" }
    } catch {
        $metrics.ActivePositions = "API Down"
        $metrics.DailyPnL = "API Down"
        $metrics.TotalTrades = "API Down"
        $metrics.WinRate = "API Down"
    }
    
    return $metrics
}

function Show-Status {
    Clear-Host
    
    Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                       🚀 CAMBO AI TRADER STATION 🚀                         ║
║                              Status Dashboard                                ║
║                        $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

    # Service Status
    Write-Host "`n🔧 Service Status" -ForegroundColor Cyan
    Write-Host "=================" -ForegroundColor Cyan
    
    $services = Get-ServiceStatus
    if ($services.Count -gt 0) {
        $services | Format-Table -Property Name, Status, Health, Uptime -AutoSize
    } else {
        Write-Host "⚠️ No services running" -ForegroundColor Yellow
    }
    
    # Endpoint Status
    Write-Host "`n🌐 Endpoint Status" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    
    $endpoints = Test-ServiceEndpoints
    $endpoints | Format-Table -Property Service, Status, ResponseCode, ResponseTime -AutoSize
    
    # Resource Usage
    if ($Detailed) {
        Write-Host "`n📊 Resource Usage" -ForegroundColor Cyan
        Write-Host "==================" -ForegroundColor Cyan
        
        $resources = Get-ResourceUsage
        if ($resources.Count -gt 0) {
            $resources | Format-Table -Property Container, CPU, Memory, Network -AutoSize
        } else {
            Write-Host "⚠️ Unable to get resource usage" -ForegroundColor Yellow
        }
    }
    
    # System Metrics
    Write-Host "`n📈 System Metrics" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    
    $systemMetrics = Get-SystemMetrics
    Write-Host "Database Size:      $($systemMetrics.DatabaseSize)" -ForegroundColor White
    Write-Host "DB Connections:     $($systemMetrics.DatabaseConnections)" -ForegroundColor White
    Write-Host "Redis Memory:       $($systemMetrics.RedisMemory)" -ForegroundColor White
    Write-Host "Redis Keys:         $($systemMetrics.RedisKeys)" -ForegroundColor White
    Write-Host "App Log Size:       $($systemMetrics.AppLogSize)" -ForegroundColor White
    Write-Host "Error Log Size:     $($systemMetrics.ErrorLogSize)" -ForegroundColor White
    
    # Trading Metrics
    Write-Host "`n💹 Trading Metrics" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    
    $tradingMetrics = Get-TradingMetrics
    Write-Host "Active Positions:   $($tradingMetrics.ActivePositions)" -ForegroundColor White
    Write-Host "Daily P&L:          $($tradingMetrics.DailyPnL)" -ForegroundColor White
    Write-Host "Total Trades:       $($tradingMetrics.TotalTrades)" -ForegroundColor White
    Write-Host "Win Rate:           $($tradingMetrics.WinRate)" -ForegroundColor White
    
    # Recent Logs
    if ($Detailed) {
        Write-Host "`n📝 Recent Error Logs" -ForegroundColor Cyan
        Write-Host "=====================" -ForegroundColor Cyan
        
        try {
            if (Test-Path "backend/logs/error.log") {
                $recentErrors = Get-Content "backend/logs/error.log" -Tail 5
                if ($recentErrors) {
                    $recentErrors | ForEach-Object { Write-Host $_ -ForegroundColor Red }
                } else {
                    Write-Host "✅ No recent errors" -ForegroundColor Green
                }
            } else {
                Write-Host "⚠️ Error log file not found" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️ Unable to read error logs" -ForegroundColor Yellow
        }
    }
    
    # Quick Actions
    Write-Host "`n🛠️ Quick Actions" -ForegroundColor Yellow
    Write-Host "=================" -ForegroundColor Yellow
    Write-Host "View logs:          docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Gray
    Write-Host "Restart backend:    docker-compose -f docker-compose.prod.yml restart backend" -ForegroundColor Gray
    Write-Host "Stop all:           docker-compose -f docker-compose.prod.yml down" -ForegroundColor Gray
    Write-Host "Security check:     .\Security-Review.ps1" -ForegroundColor Gray
    
    if ($Watch) {
        Write-Host "`n⏰ Refreshing in $Interval seconds... (Press Ctrl+C to exit)" -ForegroundColor Yellow
    }
}

function Export-StatusReport {
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $reportFile = "status_report_$timestamp.json"
    
    $report = @{
        Timestamp = Get-Date
        Services = Get-ServiceStatus
        Endpoints = Test-ServiceEndpoints
        SystemMetrics = Get-SystemMetrics
        TradingMetrics = Get-TradingMetrics
    }
    
    if ($Detailed) {
        $report.ResourceUsage = Get-ResourceUsage
    }
    
    $report | ConvertTo-Json -Depth 3 | Out-File $reportFile
    Write-Host "📊 Status report exported to: $reportFile" -ForegroundColor Green
}

# Main execution
if ($Export) {
    Export-StatusReport
    exit 0
}

if ($Watch) {
    while ($true) {
        Show-Status
        Start-Sleep -Seconds $Interval
    }
} else {
    Show-Status
}
