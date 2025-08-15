$deployDir = Join-Path $PSScriptRoot 'deploy'
Push-Location $deployDir
try {
    docker compose -f docker-compose.tunnel.yml down
} finally {
    Pop-Location
}
