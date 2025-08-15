Param(
  [int]$Port = 3001,
  [string]$ApiUrl = "http://localhost:8000"
)

Write-Host "Building frontend (API=$ApiUrl) ..." -ForegroundColor Yellow
$env:REACT_APP_API_URL = $ApiUrl
Set-Location $PSScriptRoot/frontend

if (Test-Path ./node_modules -and -not (Test-Path ./node_modules/react)) {
  Write-Host "node_modules incomplete; removing" -ForegroundColor Yellow
  Remove-Item -Recurse -Force ./node_modules
}

if (-not (Test-Path ./node_modules)) {
  Write-Host "Installing dependencies (legacy peer deps)..." -ForegroundColor Yellow
  npm install --legacy-peer-deps
}

npm run build
if ($LASTEXITCODE -ne 0) { Write-Host "Build failed" -ForegroundColor Red; exit 1 }

Write-Host "Serving build on http://localhost:$Port" -ForegroundColor Green
Write-Host "(Ctrl+C to stop)" -ForegroundColor Gray

try {
  npx --yes serve -s build -l $Port
} catch {
  Write-Host "Fallback to simple static server (no SPA routing)" -ForegroundColor Yellow
  npx --yes http-server build -p $Port
}
