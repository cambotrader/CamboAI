# === Paths ===
$root = "C:\CamboAI"
$logDir = "$root\logs"
$scriptDir = "$root\scripts"
$telemetryLog = "$logDir\telemetry.log"
$maxRetries = 3

# === Supervisor Actions ===
$tasks = @("cambo_utilities.ps1")  # Add more scripts if modularized

foreach ($task in $tasks) {
    $taskPath = Join-Path $scriptDir $task
    $retryCount = 0
    $success = $false

    while ($retryCount -lt $maxRetries -and -not $success) {
        try {
            Write-Host "Executing $taskPath (Attempt $($retryCount + 1))"
            & $taskPath
            $success = $true
            Add-Content $telemetryLog "$(Get-Date) SUCCESS: $taskPath"
        } catch {
            $retryCount++
            Add-Content $telemetryLog "$(Get-Date) ERROR in $taskPath: $($_.Exception.Message)"
            Start-Sleep -Seconds 5
        }
    }

    if (-not $success) {
        Write-Host "Max retries reached for $taskPath"
        Add-Content $telemetryLog "$(Get-Date) FAIL: $taskPath after $maxRetries attempts"
    }
}

# === Cleanup Old Logs ===
Get-ChildItem $logDir | Where-Object {
    ($_.LastWriteTime -lt (Get-Date).AddDays(-7))
} | Remove-Item -Force
