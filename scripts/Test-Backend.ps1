param(
  [string]$BaseUrl = "http://localhost:8000"
)

# Health
try {
  $health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET -TimeoutSec 10
  if ($health.status -ne "healthy") { throw "Health not OK" }
} catch { Write-Error "Health check failed: $_"; exit 1 }

# Patterns scan stub
try {
  $resp = Invoke-RestMethod -Uri "$BaseUrl/api/patterns/scan" -Method POST -Body (@{ symbol = "AAPL"; timeframe = "1D" } | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 20
  if (-not $resp.symbol) { throw "No symbol in response" }
} catch { Write-Error "Pattern scan failed: $_"; exit 1 }

# News headlines
try {
  $resp2 = Invoke-RestMethod -Uri "$BaseUrl/api/news/headlines?symbol=AAPL&limit=5" -Method GET -TimeoutSec 20
  if (-not $resp2.items) { throw "No items in headlines" }
} catch { Write-Error "Headlines failed: $_"; exit 1 }

# Progress logs
try {
  $resp3 = Invoke-RestMethod -Uri "$BaseUrl/api/progress/logs" -Method GET -TimeoutSec 10
  if (-not $resp3.items) { throw "No items in progress logs" }
} catch { Write-Error "Progress logs failed: $_"; exit 1 }

Write-Host "All backend smoke tests passed." -ForegroundColor Green