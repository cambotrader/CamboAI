# === CAMBO SUPERVISOR SCRIPT ===

# Paths
$root        = "C:\CamboAI"
$logDir      = "$root\logs"
$scriptDir   = "$root\scripts"
$telemetry   = "$logDir\telemetry.log"
$maxRetries  = 3

# Ensure log directory exists
if (!(Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory -Force
}

# Task list
$tasks = @("cambo_utilities.ps1")  # Add more script names if needed

foreach ($taskName in $tasks) {
    $taskPath = Join-Path $scriptDir $taskName
    $attempt  = 0
    $success  = $false

    while ($attempt -lt $maxRetries -and -not $success) {
        try {
            Write-Host "Running: $taskName (Attempt $($attempt + 1))"
            & $taskPath
            $success = $true
            Add-Content $telemetry "$(Get-Date) SUCCESS: $taskName"
        }
        catch {
            $attempt++
            Add-Content $telemetry "$(Get-Date) ERROR: $taskName — $($_.Exception.Message)"
            Start-Sleep -Seconds 5
        }
    }

    if (-not $success) {
        Write-Host "Max retries reached for $taskName"
        Add-Content $telemetry "$(Get-Date) FAIL: $taskName after $maxRetries attempts"
    }
}

# Cleanup old logs
Get-ChildItem $logDir | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-7)
} | Remove-Item -Force
