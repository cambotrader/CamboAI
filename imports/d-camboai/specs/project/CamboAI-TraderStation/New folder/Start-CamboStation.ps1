$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $scriptPath "backend"
$frontendPath = Join-Path $scriptPath "frontend"

function Start-Backend {
    Write-Host "Starting backend server..." -ForegroundColor Green
    Set-Location $backendPath
    
    # Create and activate venv if it doesn't exist
    if (-not (Test-Path "venv")) {
        python -m venv venv
    }
    & ".\venv\Scripts\activate"
    # Update pip first
    python -m pip install --upgrade pip
    # Install wheel and setuptools first
    pip install --upgrade wheel setuptools
    # Install specific version of psycopg2-binary that's compatible with Python 3.11
    pip install psycopg2-binary==2.9.9
    # Install remaining requirements (excluding psycopg2-binary which we installed above)
    pip install -r requirements.txt

    # Start the backend server
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {Set-Location '$backendPath'; .\venv\Scripts\activate; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000}"
}

function Start-Frontend {
    Write-Host "Starting frontend server..." -ForegroundColor Green
    Set-Location $frontendPath
    
    # Install dependencies including plotly
    npm install
    npm install --save plotly.js @types/plotly.js
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {Set-Location '$frontendPath'; $env:BROWSER='none'; $env:REACT_APP_API_URL='http://localhost:8000'; npm start}"
}

function Start-Dashboard {
    Write-Host "Starting dashboard..." -ForegroundColor Green
    Set-Location $dashboardPath
    
    # Create and activate venv if it doesn't exist
    if (-not (Test-Path "venv")) {
        python -m venv venv
    }
    & ".\venv\Scripts\activate"
    # Update pip and install build tools
    python -m pip install --upgrade pip
    pip install --upgrade wheel setuptools
    # Install numpy first
    pip install numpy==1.24.3
    # Install pandas with a compatible version
    pip install pandas==2.0.3
    # Install remaining requirements
    pip install -r requirements.txt

    # Start the dashboard
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {Set-Location '$dashboardPath'; .\venv\Scripts\activate; streamlit run app.py}"
}

# Kill any existing processes on the ports
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000,8000,8501 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force

# Start all services
Start-Backend
Start-Sleep -Seconds 5
Start-Frontend
Start-Sleep -Seconds 5
Start-Dashboard

Write-Host "`nAll services started! Access them at:" -ForegroundColor Green
Write-Host "Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "Dashboard: http://localhost:8501" -ForegroundColor Cyan
