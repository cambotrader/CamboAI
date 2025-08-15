# CamboStation Quick Tunnel helper
param(
  [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'

Write-Host "== CamboStation Quick Tunnel ==" -ForegroundColor Cyan
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

# 1) Ensure frontend is up (nginx serving prebuilt SPA)
Write-Host "Starting frontend container..." -ForegroundColor Yellow
Push-Location $scriptDir
try {
  docker compose -f "$scriptDir\docker-compose.tunnel.yml" up -d frontend | Out-Null
} finally { Pop-Location }

# 2) Ensure backend (FastAPI) is running on the host
Write-Host "Starting backend on port $Port if needed..." -ForegroundColor Yellow
$startBackend = Join-Path $rootDir 'Start-Backend.ps1'
if (Test-Path $startBackend) {
  # Force reclaim of 8000 so nginx proxy works
  & $startBackend -Port $Port -ForceKill | Out-Null
} else {
  Write-Host "Backend start script not found at $startBackend" -ForegroundColor Red
}

# Probe backend health
$healthy = $false
for($i=0;$i -lt 10;$i++){
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 "http://localhost:$Port/health"
    if ($resp.StatusCode -eq 200) { $healthy = $true; break }
  } catch {}
  Start-Sleep -Milliseconds 700
}
if (-not $healthy) {
  Write-Host "Warning: backend did not respond on http://localhost:$Port/health yet. The SPA may show 502 for API calls until it starts." -ForegroundColor Yellow
}

# 3) Start a background Quick Tunnel to the frontend and capture URL
Write-Host "Starting Cloudflare Quick Tunnel..." -ForegroundColor Yellow
# Enable JSON debug logs to make URL detection reliable across versions
$cid = (docker run -d --network deploy_web cloudflare/cloudflared:latest `
  tunnel --no-autoupdate --loglevel debug --logformat json --url http://frontend:80).Trim()

if (-not $cid) {
  Write-Host "Failed to start cloudflared Quick Tunnel container." -ForegroundColor Red
  exit 1
}

# Persist container id for later stop
$cidFile = Join-Path $scriptDir 'LAST_TUNNEL_CID.txt'
Set-Content -Path $cidFile -Value $cid -NoNewline

# Give cloudflared a moment to initialize
Start-Sleep -Seconds 2

# Persist logs for debugging and poll for the trycloudflare.com URL
$url = $null
$logFile = Join-Path $scriptDir ("cloudflared-" + $cid.Substring(0,12) + ".log")
for($i=0;$i -lt 120 -and -not $url;$i++){
  # Merge stderr to stdout to avoid PowerShell NativeCommandError and persist to file
  docker logs $cid --tail=300 2>&1 | Out-File -FilePath $logFile -Encoding UTF8
  $logs = Get-Content $logFile -Raw

  # Try plain regex first
  $m = [regex]::Matches($logs,'https://[A-Za-z0-9-]+\.trycloudflare\.com')
  if ($m.Count -gt 0) { $url = $m[$m.Count-1].Value }

  # Fallback: parse JSON lines and look for a field named 'url' that contains trycloudflare
  if (-not $url) {
    try {
      $jsonLines = $logs -split "\r?\n" | Where-Object { $_ -like '{*}' }
      foreach ($line in $jsonLines) {
        $obj = $null; try { $obj = $line | ConvertFrom-Json } catch {}
        if ($obj -and $obj.url -and ($obj.url -match 'trycloudflare')) { $url = $obj.url; break }
      }
    } catch {}
  }

  if ($url) { break }
  Start-Sleep -Seconds 1
}

if ($url) {
  Write-Host "Public URL: $url" -ForegroundColor Green
  try { Set-Clipboard -Value $url; Write-Host "(Copied to clipboard)" -ForegroundColor DarkGray } catch {}
  Write-Host "Tunnel container id: $cid" -ForegroundColor DarkGray
  Write-Host "To stop the tunnel: docker stop $cid" -ForegroundColor DarkGray
  # Persist URL for convenience
  $urlFile = Join-Path $scriptDir 'LAST_TUNNEL_URL.txt'
  Set-Content -Path $urlFile -Value $url -NoNewline
  # Quick health check through the tunnel (best-effort)
  try {
    $hc = Invoke-RestMethod -Uri ("$url/api/health") -TimeoutSec 8
    Write-Host ("Health: " + ($hc | ConvertTo-Json -Compress)) -ForegroundColor DarkGray
  } catch { Write-Host ("Health check through tunnel failed: " + $_.Exception.Message) -ForegroundColor DarkGray }
  Write-Host "Logs saved to: $logFile" -ForegroundColor DarkGray
} else {
  Write-Host "Could not detect trycloudflare URL in logs yet. Run: docker logs -f $cid" -ForegroundColor Yellow
  Write-Host "Logs saved to: $logFile" -ForegroundColor DarkGray
}
