# Stop the last started Quick Tunnel container
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$cidFile = Join-Path $scriptDir 'LAST_TUNNEL_CID.txt'
if (-not (Test-Path $cidFile)) { Write-Host "No CID file found: $cidFile" -ForegroundColor Yellow; exit 0 }
$cid = Get-Content -Raw -Path $cidFile
if (-not $cid) { Write-Host "CID file empty." -ForegroundColor Yellow; exit 0 }
Write-Host "Stopping tunnel container $cid ..." -ForegroundColor Cyan
try { docker stop $cid | Out-Null; Write-Host "Stopped." -ForegroundColor Green } catch { Write-Host "Failed to stop container $cid" -ForegroundColor Red }
