Param(
    [switch]$Rebuild
)

$deployDir = Join-Path $PSScriptRoot 'deploy'
$envFile = Join-Path $deployDir '.env'
$envExample = Join-Path $deployDir '.env.example'

if (-not (Test-Path $envFile)) {
    Write-Host "deploy/.env not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile -Force
        Write-Host "Please edit deploy/.env and set DOMAIN and CLOUDFLARE_TUNNEL_TOKEN, then re-run this script." -ForegroundColor Yellow
    } else {
        Write-Host "deploy/.env.example not found. Please create deploy/.env manually." -ForegroundColor Red
    }
    exit 1
}

$composeArgs = @('-f','docker-compose.tunnel.yml','up')
if ($Rebuild) { $composeArgs += '--build' }
$composeArgs += '-d'

Push-Location $deployDir
try {
    docker compose @composeArgs
} finally {
    Pop-Location
}
