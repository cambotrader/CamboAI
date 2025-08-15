param(
  [int]$Port = 8000,
  [switch]$ForceKill
)

Write-Host "Starting backend on port $Port..." -ForegroundColor Green

$Root = $PSScriptRoot
$BackendDir = Join-Path $Root 'backend'
$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
$PipExe = Join-Path $Root '.venv\Scripts\pip.exe'
$UvicornExe = Join-Path $Root '.venv\Scripts\uvicorn.exe'
$PythonExe = if (Test-Path $VenvPython) { $VenvPython } else { 'python' }
$UvicornCmd = $null  # Force module launch to avoid stale wrappers

# Ensure virtual environment exists
if (-not (Test-Path $VenvPython)) {
  Write-Host "Creating virtual environment at .venv..." -ForegroundColor Yellow
  & $PythonExe -m venv (Join-Path $Root '.venv') | Out-Null
  if (-not (Test-Path $VenvPython)) { Write-Host "Failed to create virtual env; falling back to system Python." -ForegroundColor Yellow }
}

# Ensure dependencies (uvicorn/fastapi) are available
function Ensure-Dependency {
  param([string]$ModuleName, [string]$InstallName)
  $rc = 0
  try {
    & $VenvPython -c "import importlib; importlib.import_module('$ModuleName')" | Out-Null
    $rc = $LASTEXITCODE
  } catch { $rc = 1 }
  if ($rc -ne 0) {
    Write-Host "Installing $InstallName..." -ForegroundColor Yellow
    & $VenvPython -m pip install --upgrade pip | Out-Null
    & $VenvPython -m pip install $InstallName | Out-Null
  }
}

Ensure-Dependency -ModuleName 'uvicorn' -InstallName 'uvicorn==0.15.0'
Ensure-Dependency -ModuleName 'fastapi' -InstallName 'fastapi==0.68.0'
Ensure-Dependency -ModuleName 'jwt' -InstallName 'PyJWT==2.4.0'
Write-Host "Backend deps verified in venv: $VenvPython" -ForegroundColor Cyan

# Ensure Python can import backend modules and optional app.* modules
$env:PYTHONPATH = $BackendDir

function Test-PortInUse([int]$p){
  try { return [bool](Get-NetTCPConnection -LocalPort $p -ErrorAction Stop) } catch { return $false }
}

if ($ForceKill -and (Test-PortInUse $Port)){
  try {
    $pid = (Get-NetTCPConnection -LocalPort $Port | Select-Object -First 1 -ExpandProperty OwningProcess)
    if ($pid) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue; Start-Sleep -Milliseconds 700 }
  } catch {}
}

if (Test-PortInUse $Port){
  Write-Host "Port $Port is busy, trying next free port..." -ForegroundColor Yellow
  for($p=$Port+1; $p -lt ($Port+10); $p++){
    if (-not (Test-PortInUse $p)) { $Port = $p; break }
  }
}

Push-Location $BackendDir
try {
  $logDir = Join-Path $BackendDir 'logs'
  if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
  $outLog = Join-Path $logDir 'backend.out.log'
  $errLog = Join-Path $logDir 'backend.err.log'
  # Always use venv python -m uvicorn to avoid stale wrappers
  Start-Process -FilePath $VenvPython -ArgumentList "-m","uvicorn","simple_server:app","--host","127.0.0.1","--port","$Port","--log-level","info" -RedirectStandardOutput $outLog -RedirectStandardError $errLog -WindowStyle Hidden | Out-Null
} finally {
  Pop-Location
}

# Probe health
$ok = $false
for ($i=0; $i -lt 12; $i++){
  try {
    $resp = Invoke-WebRequest -UseBasicParsing "http://localhost:$Port/health" -TimeoutSec 2
    if ($resp.StatusCode -eq 200) { Write-Host "Backend UP at http://localhost:$Port" -ForegroundColor Green; $ok = $true; break }
  } catch {}
  Start-Sleep -Milliseconds 600
}

if (-not $ok){
  Write-Host "Backend did not respond on http://localhost:$Port/health" -ForegroundColor Red
  Write-Host "Tip: try running in a console to see logs:" -ForegroundColor Yellow
  Write-Host "  cd $BackendDir; $VenvPython -m uvicorn simple_server:app --host 0.0.0.0 --port $Port" -ForegroundColor DarkGray
  Write-Host "  Logs: $BackendDir\logs\backend.out.log and backend.err.log" -ForegroundColor DarkGray
}

Write-Host "Try auth endpoints:" -ForegroundColor Cyan
Write-Host "POST http://localhost:$Port/api/auth/login" -ForegroundColor White
Write-Host "GET  http://localhost:$Port/api/auth/me (Bearer demo-token)" -ForegroundColor White
