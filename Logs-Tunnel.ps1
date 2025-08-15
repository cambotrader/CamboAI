$deployDir = Join-Path $PSScriptRoot 'deploy'
Push-Location $deployDir
try {
    docker compose -f docker-compose.tunnel.yml logs -f
} finally {
    Pop-Location
}
