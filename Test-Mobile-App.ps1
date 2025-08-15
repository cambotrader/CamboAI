# CamboAI - Test Mobile App
# Quick test of the mobile app setup

Write-Host ""
Write-Host "📱 Testing CamboAI Mobile App" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

# Check if mobile directory exists
if (-not (Test-Path "D:\CamboAI\mobile")) {
    Write-Host "❌ Mobile app directory not found!" -ForegroundColor Red
    Write-Host "Run Setup-Free-Everything.ps1 first." -ForegroundColor Yellow
    exit 1
}

Set-Location "D:\CamboAI\mobile"

# Check if dependencies are installed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "🔍 Checking mobile app components..." -ForegroundColor Yellow

# Check key files
$files = @(
    "package.json",
    "App.tsx",
    "app.json",
    "src\screens\HomeScreen.tsx",
    "src\screens\TradingScreen.tsx",
    "src\screens\AnalyticsScreen.tsx",
    "src\screens\PortfolioScreen.tsx",
    "src\services\apiService.ts",
    "src\config\api.ts"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🚀 Starting mobile app..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📲 To test on your device:" -ForegroundColor Cyan
Write-Host "1. Install 'Expo Go' app from App Store/Play Store" -ForegroundColor White
Write-Host "2. Scan the QR code that will appear" -ForegroundColor White
Write-Host "3. App will load instantly!" -ForegroundColor White
Write-Host ""
Write-Host "💻 To test in web browser:" -ForegroundColor Cyan
Write-Host "Press 'w' when the server starts" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop: Press Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Start the development server
npm start