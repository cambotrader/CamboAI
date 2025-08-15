# CamboStation Vision - Mobile App Demo
# Quick demo of the mobile app

Write-Host "📱 CamboStation Vision Mobile App Demo" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Check if mobile directory exists
if (-not (Test-Path "d:\CamboAI\mobile")) {
    Write-Host "❌ Mobile app not found. Run Setup-Free-Everything.ps1 first." -ForegroundColor Red
    exit 1
}

Set-Location "d:\CamboAI\mobile"

Write-Host ""
Write-Host "🚀 Starting mobile app development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📲 To test on your device:" -ForegroundColor Cyan
Write-Host "1. Install 'Expo Go' app from App Store/Play Store" -ForegroundColor White
Write-Host "2. Scan the QR code that appears" -ForegroundColor White
Write-Host "3. App will load instantly on your device!" -ForegroundColor White
Write-Host ""
Write-Host "💻 To test in web browser:" -ForegroundColor Cyan
Write-Host "Press 'w' when the server starts" -ForegroundColor White
Write-Host ""
Write-Host "📱 Features you'll see:" -ForegroundColor Yellow
Write-Host "• Real-time trading dashboard" -ForegroundColor White
Write-Host "• Interactive charts and analytics" -ForegroundColor White
Write-Host "• Portfolio management" -ForegroundColor White
Write-Host "• AI-powered insights" -ForegroundColor White
Write-Host "• Beautiful Material Design UI" -ForegroundColor White
Write-Host ""

# Start the development server
npm start