param(
  [switch]$NoFrontend
)

# Simple startup script for Cambo AI Trader Station
Write-Host "Starting Cambo AI Trader Station (simple mode)..." -ForegroundColor Green

$Root = $PSScriptRoot
$BackendDir = Join-Path $Root 'backend'
$FrontendDir = Join-Path $Root 'frontend'
$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
$PythonExe = if (Test-Path $VenvPython) { $VenvPython } else { 'python' }

# Start Backend
Write-Host "`nStarting Backend..." -ForegroundColor Yellow
try {
    $backendJob = Start-Job -ScriptBlock {
        param($dir, $py)
        Set-Location $dir
        & $py '.\simple_server.py'
    } -ArgumentList $BackendDir, $PythonExe
    Write-Host "Backend job started with ID: $($backendJob.Id)" -ForegroundColor Green
} catch {
    Write-Host "Error starting backend: $_" -ForegroundColor Red
}

if (-not $NoFrontend) {
  # Start Frontend
  Write-Host "`nStarting Frontend..." -ForegroundColor Yellow
  try {
      $frontendJob = Start-Job -ScriptBlock {
          param($dir)
          Set-Location $dir
          $env:PORT = "3002"
          $env:BROWSER = "none"
          npm run start
      } -ArgumentList $FrontendDir
      Write-Host "Frontend job started with ID: $($frontendJob.Id)" -ForegroundColor Green
  } catch {
      Write-Host "Error starting frontend: $_" -ForegroundColor Red
  }
}

Write-Host "`nWaiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host "`nChecking ports..." -ForegroundColor Cyan
try { Get-NetTCPConnection -LocalPort 8000 -ErrorAction Stop | Select-Object -First 1 | ForEach-Object { "Backend PID: $($_.OwningProcess)" } } catch { Write-Host "Backend not listening yet" }
try { Get-NetTCPConnection -LocalPort 3002 -ErrorAction Stop | Select-Object -First 1 | ForEach-Object { "Frontend PID: $($_.OwningProcess)" } } catch { if (-not $NoFrontend) { Write-Host "Frontend not listening yet" } }

# Show backend job state and any immediate errors
Write-Host "`nBackend job state: $($backendJob.State)" -ForegroundColor Cyan
if ($backendJob.State -eq 'Failed') {
    Write-Host "Backend failed to start:" -ForegroundColor Red
    Receive-Job -Job $backendJob -Keep | Out-Host
}

# Optional quick health check
try {
    $resp = Invoke-WebRequest -UseBasicParsing http://localhost:8000/health -TimeoutSec 3
    Write-Host "Health: $($resp.StatusCode) $($resp.Content)" -ForegroundColor Green
} catch { Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Yellow }

Write-Host "`nServices:" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000/health" -ForegroundColor White
if (-not $NoFrontend) { Write-Host "Frontend: http://localhost:3002" -ForegroundColor White }
