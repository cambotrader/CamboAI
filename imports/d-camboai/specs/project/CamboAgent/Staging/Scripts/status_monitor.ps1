$logDir = "C:\CamboAgent\Logs"
if (!(Test-Path $logDir)) { New-Item -Path $logDir -ItemType Directory | Out-Null }
$logFile = "$logDir\status_monitor_log.txt"
function Write-Log { param([string]$msg); Add-Content -Path $logFile -Value "$(Get-Date -Format u) - $msg" }
Write-Log "Monitor started"
Write-Host "? Cambo Status Monitor running"
