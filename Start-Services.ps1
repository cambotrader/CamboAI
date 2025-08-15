$ErrorActionPreference = 'Continue'

Write-Host "Starting CamboStation Vision Services..." -ForegroundColor Green

# Function to check if a port is in use
function Test-PortInUse {
    param($port)
    $inUse = $false
    $listener = $null
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, $port)
        $listener.Start()
        $inUse = $false
    }
    catch {
        $inUse = $true
    }
    finally {
        if ($listener) {
            $listener.Stop()
        }
    }
    return $inUse
}

# Kill any processes using our ports
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
$portsToCheck = @(3000, 8000, 8501)
foreach ($port in $portsToCheck) {
    if (Test-PortInUse $port) {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connections) {
            Stop-Process -Id $connections.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "Starting backend (helper script)..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    & "$using:PSScriptRoot\Start-Backend.ps1" -Port 8000 -ForceKill
}

# Start frontend
Write-Host "Setting up frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendPath
npm install --legacy-peer-deps

Write-Host "Starting frontend server..." -ForegroundColor Yellow
$env:BROWSER = "none"
$env:REACT_APP_API_URL = "http://localhost:8000"
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:frontendPath
    npm start
}

# Dashboard optional (disabled by default). Set $env:ENABLE_DASHBOARD=1 to enable.
$dashboardJob = $null
if ($env:ENABLE_DASHBOARD -eq "1") {
    Write-Host "Setting up dashboard..." -ForegroundColor Yellow
    $dashboardPath = Join-Path $PSScriptRoot "dashboard"
    if (-not (Test-Path (Join-Path $dashboardPath "venv"))) {
        Set-Location $dashboardPath
        python -m venv venv
    }
    & "$dashboardPath\venv\Scripts\activate.ps1"
    $dashPython = Join-Path $dashboardPath "venv\Scripts\python.exe"
    & $dashPython -m pip install -r requirements.txt

    Write-Host "Starting dashboard server..." -ForegroundColor Yellow
    $dashboardJob = Start-Job -ScriptBlock {
        Set-Location $using:dashboardPath
        & "$using:dashboardPath\venv\Scripts\streamlit" run app.py
    }
}

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
Write-Host "Checking service status..." -ForegroundColor Yellow

$maxAttempts = 5
$attempt = 0
$success = $false

while ($attempt -lt $maxAttempts -and -not $success) {
    $attempt++
    try {
        $backendHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
        $frontendHealth = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
        $success = $true
        Write-Host "`nAll services are running!" -ForegroundColor Green
        Write-Host "Access your services at:"
        Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Dashboard: http://localhost:8501" -ForegroundColor Cyan
    }
    catch {
        if ($attempt -lt $maxAttempts) {
            Write-Host "Waiting for services to be ready... (Attempt $attempt of $maxAttempts)" -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    }
}

if (-not $success) {
    Write-Host "`nWarning: Some services might not have started properly." -ForegroundColor Red
    Write-Host "Check the individual terminal windows for error messages." -ForegroundColor Yellow
}

# Keep the script running and show logs
Write-Host "`nShowing service logs (Press Ctrl+C to exit)..." -ForegroundColor Yellow
try {
    while ($true) {
        if ($dashboardJob) {
            Receive-Job -Job $backendJob, $frontendJob, $dashboardJob
        } else {
            Receive-Job -Job $backendJob, $frontendJob
        }
        Start-Sleep -Seconds 1
    }
}
finally {
    # Cleanup on script exit
    if ($dashboardJob) {
        Stop-Job -Job $backendJob, $frontendJob, $dashboardJob
        Remove-Job -Job $backendJob, $frontendJob, $dashboardJob
    } else {
        Stop-Job -Job $backendJob, $frontendJob
        Remove-Job -Job $backendJob, $frontendJob
    }
}
