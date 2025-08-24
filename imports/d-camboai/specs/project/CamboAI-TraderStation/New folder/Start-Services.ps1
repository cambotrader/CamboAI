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

# Activate Python virtual environment
Write-Host "Setting up Python environment..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path (Join-Path $backendPath "venv"))) {
    Set-Location $backendPath
    python -m venv venv
}
& "$backendPath\venv\Scripts\activate.ps1"

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
Set-Location $backendPath
pip install -r requirements.txt

# Start backend server
Write-Host "Starting backend server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:backendPath
    & "$using:backendPath\venv\Scripts\uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000
}

# Start frontend
Write-Host "Setting up frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendPath
npm install

Write-Host "Starting frontend server..." -ForegroundColor Yellow
$env:BROWSER = "none"
$env:REACT_APP_API_URL = "http://localhost:8000"
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:frontendPath
    npm start
}

# Start dashboard
Write-Host "Setting up dashboard..." -ForegroundColor Yellow
$dashboardPath = Join-Path $PSScriptRoot "dashboard"
if (-not (Test-Path (Join-Path $dashboardPath "venv"))) {
    Set-Location $dashboardPath
    python -m venv venv
}
& "$dashboardPath\venv\Scripts\activate.ps1"
pip install -r requirements.txt

Write-Host "Starting dashboard server..." -ForegroundColor Yellow
$dashboardJob = Start-Job -ScriptBlock {
    Set-Location $using:dashboardPath
    & "$using:dashboardPath\venv\Scripts\streamlit" run app.py
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
        Receive-Job -Job $backendJob, $frontendJob, $dashboardJob
        Start-Sleep -Seconds 1
    }
}
finally {
    # Cleanup on script exit
    Stop-Job -Job $backendJob, $frontendJob, $dashboardJob
    Remove-Job -Job $backendJob, $frontendJob, $dashboardJob
}
