# Build Next.js app in web-advanced
Set-Location "d:\CamboAI\web-advanced"

# Pin Node via Volta if available, otherwise rely on engines
if (Get-Command volta -ErrorAction SilentlyContinue) {
  volta install node@20
  volta run npm --version | Out-Null
}

# Resilient install
$env:NPM_CONFIG_LEGACY_PEER_DEPS = "true"
if (Test-Path package-lock.json) {
  npm ci
} else {
  npm install
}

npm run build
Write-Host "Frontend build succeeded." -ForegroundColor Green