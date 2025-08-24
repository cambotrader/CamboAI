param([string]$newMode)

$targetPath = ".config/$newMode.config.json"
if (-not (Test-Path ".config/config_template.json")) {
    Write-Host "? config_template.json missing"
    exit
}

Copy-Item ".config/config_template.json" $targetPath
Set-Content ".config/.active_mode" -Value $newMode
Start-Process "code" $targetPath
Write-Host "?? New mode [$newMode] initialized and activated"
