param(
  [string]$BaseUrl = "http://localhost:8000",
  [int]$Concurrency = 10,
  [int]$Requests = 100
)

# Simple parallel GET bombardment for /health and /api/news/headlines
$script:fail = $false
$jobs = @()
for ($i=0; $i -lt $Requests; $i++) {
  $jobs += Start-Job -ScriptBlock {
    param($BaseUrl)
    try {
      Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET -TimeoutSec 10 | Out-Null
      Invoke-RestMethod -Uri "$BaseUrl/api/news/headlines?limit=5" -Method GET -TimeoutSec 20 | Out-Null
    } catch { $_ }
  } -ArgumentList $BaseUrl
  if (($i+1) % $Concurrency -eq 0) { Wait-Job -Job $jobs | Out-Null; $jobs | Receive-Job | ForEach-Object { if ($_ -is [System.Management.Automation.ErrorRecord]) { $script:fail = $true } }; $jobs | Remove-Job; $jobs = @() }
}
Wait-Job -Job $jobs | Out-Null
$jobs | Receive-Job | ForEach-Object { if ($_ -is [System.Management.Automation.ErrorRecord]) { $script:fail = $true } }
$jobs | Remove-Job

if ($script:fail) { Write-Error "Load test had failures"; exit 1 }
Write-Host "Load test completed without errors." -ForegroundColor Green