param (
    [ValidateSet("dev", "plugin-test", "prod")]
    [string]$Mode
)

$ConfigMap = @{
    "dev"         = "config/dev.config.json"
    "plugin-test" = "config/plugin-test.config.json"
    "prod"        = "config/prod.config.json"
}

if ($ConfigMap.ContainsKey($Mode)) {
    Copy-Item -Path $ConfigMap[$Mode] -Destination "config/active.config.json" -Force
    Write-Host "Switched to $Mode mode successfully."
} else {
    Write-Host "Invalid mode. Use: dev, plugin-test, or prod."
}
