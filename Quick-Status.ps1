# CAMBOAI TRADERSTATION - Quick Status Check
Write-Host "CAMBOAI TRADERSTATION STATUS CHECK" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check if domain is working now
Write-Host "`nDOMAIN STATUS:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://camboai.com" -Method HEAD -TimeoutSec 10 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   SUCCESS: camboai.com is ONLINE!" -ForegroundColor Green
    }
} catch {
    Write-Host "   PENDING: camboai.com still deploying..." -ForegroundColor Yellow
}

# Check local files
Write-Host "`nLOCAL FILES STATUS:" -ForegroundColor Cyan
$files = @{
    "Frontend" = "web-advanced\app\page.tsx"
    "Backend" = "backend\app\main.py" 
    "Quantum Launcher" = "camboai_traderstation_quantum_launcher.py"
    "Deploy Script" = "Deploy-CamboAI-Quantum.ps1"
}

$foundFiles = 0
foreach ($item in $files.GetEnumerator()) {
    if (Test-Path $item.Value) {
        Write-Host "   OK: $($item.Key)" -ForegroundColor Green
        $foundFiles++
    } else {
        Write-Host "   MISSING: $($item.Key)" -ForegroundColor Red
    }
}

# Check AI modules
Write-Host "`nAI MODULES:" -ForegroundColor Cyan
$aiModules = @(
    "backend\app\modules\live_coaching.py",
    "backend\app\modules\psychology_therapy.py",
    "backend\app\modules\ai_omnipresence.py"
)

$aiCount = 0
foreach ($module in $aiModules) {
    if (Test-Path $module) {
        $lines = (Get-Content $module).Count
        $name = (Split-Path $module -Leaf).Replace('.py', '').Replace('_', ' ')
        Write-Host "   OK: $name ($lines lines)" -ForegroundColor Green
        $aiCount++
    }
}

# Summary
Write-Host "`nSUMMARY:" -ForegroundColor Cyan
Write-Host "   Local Files: $foundFiles/4 ready" -ForegroundColor White
Write-Host "   AI Modules: $aiCount/3 ready" -ForegroundColor White

if ($foundFiles -eq 4 -and $aiCount -eq 3) {
    Write-Host "   STATUS: FULLY READY FOR DEPLOYMENT!" -ForegroundColor Green
} else {
    Write-Host "   STATUS: Some components missing" -ForegroundColor Yellow
}

Write-Host "`nNEXT STEPS:" -ForegroundColor Cyan
Write-Host "   1. Wait for Vercel to finish deploying (2-5 minutes)" -ForegroundColor White
Write-Host "   2. Deploy backend: .\Deploy-Backend-Render.ps1" -ForegroundColor White
Write-Host "   3. Get API keys: OpenAI, Anthropic, Google" -ForegroundColor White

Write-Host "`nCamboAI TraderStation - Trade with Vision, Learn with Purpose, Evolve with AI" -ForegroundColor Cyan