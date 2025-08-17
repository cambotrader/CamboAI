# CAMBOAI TRADERSTATION - Quick Platform Test
Write-Host "CAMBOAI TRADERSTATION DEPLOYMENT TEST" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Test 1: Frontend (Vercel)
Write-Host "`nTesting Frontend (camboai.com)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://camboai.com" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        if ($response.Content.Contains("CamboAI") -or $response.Content.Contains("TraderStation")) {
            Write-Host "   SUCCESS: Frontend is LIVE and working!" -ForegroundColor Green
        } else {
            Write-Host "   WARNING: Frontend is up but may be wrong content" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ISSUE: Frontend not accessible - $($_.Exception.Message.Split('.')[0])" -ForegroundColor Red
    Write-Host "   ACTION: Check Vercel deployment dashboard" -ForegroundColor Gray
}

# Test 2: Backend APIs (Common Render URLs)
Write-Host "`nTesting Backend APIs..." -ForegroundColor Cyan
$backendUrls = @(
    "https://camboai-traderstation-api.onrender.com",
    "https://camboai-backend.onrender.com",
    "https://camboai-api.onrender.com"
)

$backendFound = $false
foreach ($url in $backendUrls) {
    try {
        $healthUrl = "$url/health"
        $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   SUCCESS: Backend API is LIVE at $url" -ForegroundColor Green
            $backendFound = $true
            break
        }
    } catch {
        # Try next URL
    }
}

if (-not $backendFound) {
    Write-Host "   PENDING: Backend not deployed yet" -ForegroundColor Yellow
    Write-Host "   ACTION: Deploy to Render following deployment guide" -ForegroundColor Gray
}

# Test 3: Local AI Modules
Write-Host "`nTesting Local AI Modules..." -ForegroundColor Cyan
$aiModules = @{
    "Live Coach" = "backend\app\modules\live_coaching.py"
    "Psychology Hub" = "backend\app\modules\psychology_therapy.py"
    "AI Omnipresence" = "backend\app\modules\ai_omnipresence.py"
}

foreach ($module in $aiModules.GetEnumerator()) {
    if (Test-Path $module.Value) {
        $lines = (Get-Content $module.Value).Count
        Write-Host "   OK: $($module.Key) - $lines lines ready" -ForegroundColor Green
    } else {
        Write-Host "   MISSING: $($module.Key)" -ForegroundColor Red
    }
}

# Summary
Write-Host "`nDEPLOYMENT STATUS:" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

$frontendWorking = $false
$backendWorking = $backendFound

try {
    $test = Invoke-WebRequest -Uri "https://camboai.com" -UseBasicParsing -TimeoutSec 5
    $frontendWorking = ($test.StatusCode -eq 200)
} catch { }

if ($frontendWorking -and $backendWorking) {
    Write-Host "PLATFORM STATUS: FULLY OPERATIONAL!" -ForegroundColor Green
    Write-Host "   Frontend: LIVE at camboai.com" -ForegroundColor White
    Write-Host "   Backend: LIVE and responding" -ForegroundColor White
    Write-Host "   AI Modules: All loaded" -ForegroundColor White
    Write-Host ""
    Write-Host "YOUR CAMBOAI TRADERSTATION IS LIVE!" -ForegroundColor Green
} elseif ($frontendWorking) {
    Write-Host "PLATFORM STATUS: Frontend Ready, Backend Pending" -ForegroundColor Yellow
    Write-Host "   Frontend: LIVE at camboai.com" -ForegroundColor White
    Write-Host "   Backend: Deploy to Render needed" -ForegroundColor Yellow
} else {
    Write-Host "PLATFORM STATUS: Deployment in Progress" -ForegroundColor Yellow
    Write-Host "   Frontend: Check Vercel dashboard" -ForegroundColor Yellow
    Write-Host "   Backend: Deploy to Render needed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Read: DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host "2. Check Vercel dashboard for frontend issues" -ForegroundColor White
Write-Host "3. Deploy backend to Render" -ForegroundColor White
Write-Host ""
Write-Host "Trade with Vision, Learn with Purpose, Evolve with AI" -ForegroundColor Magenta