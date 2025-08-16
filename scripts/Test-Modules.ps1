param(
  [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = 'Stop'

function Assert-Ok($cond, $msg) { if (-not $cond) { throw $msg } }

# 1) Patterns scan
$r1 = Invoke-RestMethod -Uri "$BaseUrl/api/patterns/scan" -Method POST -Body (@{ symbol = "AAPL" } | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 30
Assert-Ok ($r1.symbol -and $r1.detections) "patterns scan failed"

# 2) Strategy register/run
$r2 = Invoke-RestMethod -Uri "$BaseUrl/api/strategy/register" -Method POST -Body (@{ name = "demo"; rules = @(@{ type = "cross"; field = "sma"; op = ">"; value = 50 }) } | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 10
Assert-Ok ($r2.ok) "strategy register failed"
$r3 = Invoke-RestMethod -Uri "$BaseUrl/api/strategy/run" -Method POST -Body (@{ strategy_id = $r2.strategy_id; symbol = "AAPL" } | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 20
Assert-Ok ($r3.metrics) "strategy run failed"

# 3) News / sentiment
$r4 = Invoke-RestMethod -Uri "$BaseUrl/api/news/headlines?symbol=AAPL&limit=5" -Method GET -TimeoutSec 20
Assert-Ok ($r4.items) "news headlines failed"
$r5 = Invoke-RestMethod -Uri "$BaseUrl/api/sentiment/summary?symbol=AAPL&limit=10" -Method GET -TimeoutSec 20
Assert-Ok ($r5.label) "sentiment summary failed"

# 4) Journal
$r6 = Invoke-RestMethod -Uri "$BaseUrl/api/journal/entries" -Method GET -TimeoutSec 10
$r7 = Invoke-RestMethod -Uri "$BaseUrl/api/journal/entries" -Method POST -Body (@{ symbol = "AAPL"; notes = "demo" } | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 10
Assert-Ok ($r7.ok) "journal create failed"

# 5) Alerts
$r8 = Invoke-RestMethod -Uri "$BaseUrl/api/alerts/rules" -Method GET -TimeoutSec 10
$r9 = Invoke-RestMethod -Uri "$BaseUrl/api/alerts/rules" -Method POST -Body (@{ symbol = "AAPL"; above = 100 } | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 10
Assert-Ok ($r9.ok) "alerts create failed"

# 6) Scanner
$r10 = Invoke-RestMethod -Uri "$BaseUrl/api/scanner/run" -Method POST -Body (@{ universe = "stocks" } | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 20
Assert-Ok ($r10.rows) "scanner run failed"

# 7) War-room
$r11 = Invoke-RestMethod -Uri "$BaseUrl/api/war-room/debate/start" -Method POST -Body (@{ topic = "AAPL outlook" } | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 10
Assert-Ok ($r11.id) "war-room start failed"
$r12 = Invoke-RestMethod -Uri "$BaseUrl/api/war-room/debate/$($r11.id)" -Method GET -TimeoutSec 10
Assert-Ok ($r12.consensus) "war-room get failed"

# 8) Progress logs
$r13 = Invoke-RestMethod -Uri "$BaseUrl/api/progress/logs" -Method GET -TimeoutSec 10
Assert-Ok ($r13.items) "progress logs failed"

Write-Host "All module smoke tests passed." -ForegroundColor Green