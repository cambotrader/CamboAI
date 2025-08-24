# mode_bootloader.ps1
$activeMode = (Get-Content ".config/.active_mode").Trim()
$configPath = ".config/$($activeMode).config.json"

if (-not (Test-Path $configPath)) {
    Write-Host "? Config [$configPath] missing. Check .active_mode or generate via New-Mode.ps1"
    exit
}

$configJson = Get-Content $configPath -Raw | ConvertFrom-Json

foreach ($module in $configJson.modules) {
    Write-Host "?? Loading [$module]..."
    switch ($module) {
        "chart_engine" { & ".\Modules\ChartEngine.ps1"; Write-Host "? chart_engine loaded" }
        "sentiment_panel" { & ".\Modules\SentimentPanel.ps1"; Write-Host "? sentiment_panel loaded" }
        "strategy_sim" { & ".\Modules\StrategySim.ps1"; Write-Host "? strategy_sim loaded" }
        default { Write-Host "? Unknown module: $module" }
    }
}

if ($configJson.langChainEnabled -eq $true) {
    Write-Host "?? LangChain routing active..."
    & ".\Modules\LangChainLoader.ps1"
}

Write-Host "?? Bootloader complete for [$activeMode] mode"
$activeMode = (Get-Content ".config/.active_mode").Trim()
$configPath = ".config/$($activeMode).config.json"

if (-not (Test-Path $configPath)) {
    Write-Host "? Config [$configPath] missing. Run New-Mode.ps1 '<mode>' or check .active_mode."
    exit
}

$configJson = Get-Content $configPath -Raw | ConvertFrom-Json

foreach ($module in $configJson.modules) {
    Write-Host "?? Loading [$module]..."
    switch ($module) {
        "chart_engine" { & ".\Modules\ChartEngine.ps1"; Write-Host "? chart_engine loaded" }
        "sentiment_panel" { & ".\Modules\SentimentPanel.ps1"; Write-Host "? sentiment_panel loaded" }
        "strategy_sim" { & ".\Modules\StrategySim.ps1"; Write-Host "? strategy_sim loaded" }
        default { Write-Host "? Unknown module: $module" }
    }
}

if ($configJson.langChainEnabled -eq $true) {
    Write-Host "?? LangChain routing active..."
    & ".\Modules\LangChainLoader.ps1"
}

$logLine = "$(Get-Date): Bootloader for [$activeMode] – modules loaded: $($configJson.modules -join ', ')"
Add-Content "logs/bootloader_log.txt" $logLine
Write-Host "?? Bootloader complete for [$activeMode] mode"
