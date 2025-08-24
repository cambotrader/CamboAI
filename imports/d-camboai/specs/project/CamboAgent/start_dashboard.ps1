# === FUNCTION DEFINITION FIRST ===
function Launch-Frontend {
    $frontendDir = "C:\CamboAgent\Frontend"
    if (Test-Path $frontendDir) {
        try {
            Set-Location $frontendDir
            Start-Process "npm" -ArgumentList "run dev" -NoNewWindow
            Write-Host "✅ React frontend launched."
        } catch {
            Write-Host "❌ React frontend failed: $($_.Exception.Message)"
        }
    } else {
        Write-Host "⛔ Frontend folder not found: $frontendDir"
    }
}

function Launch-Backend {
    $backendDir = "C:\CamboAgent\Backend"
    if (Test-Path $backendDir) {
        try {
            Set-Location $backendDir
            Start-Process "python" -ArgumentList "app.py" -NoNewWindow
            Write-Host "✅ Flask backend launched."
        } catch {
            Write-Host "❌ Flask backend failed: $($_.Exception.Message)"
        }
    } else {
        Write-Host "⛔ Backend folder not found: $backendDir"
    }
}

function Monitor-Logs {
    $logDir = "C:\Logs"
    if (Test-Path $logDir) {
        try {
            Get-Content -Path "$logDir\supervisor_agent_log.txt" -Tail 10
            Write-Host "✅ Logs monitored successfully."
        } catch {
            Write-Host "❌ Log monitoring failed: $($_.Exception.Message)"
        }
    } else {
        Write-Host "⛔ Log directory not found: $logDir"
    }
}

# === THEN CALL THE FUNCTIONS ===
Launch-Frontend
Launch-Backend
Monitor-Logs
```