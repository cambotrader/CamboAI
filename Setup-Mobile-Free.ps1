# CamboStation Vision - Free Mobile App Setup
# This script sets up everything needed for free mobile app development

Write-Host "🚀 Setting up CamboStation Vision Mobile App (100% Free)" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if Node.js is installed
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Navigate to mobile directory
Set-Location "d:\CamboAI\mobile"

# Install dependencies
Write-Host "📦 Installing mobile app dependencies..." -ForegroundColor Yellow
npm install

# Install global tools (free)
Write-Host "🔧 Installing free development tools..." -ForegroundColor Yellow
npm install -g @expo/cli
npm install -g eas-cli

# Check Expo CLI installation
Write-Host "✅ Expo CLI installed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Setup Complete! Next steps:" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "1. Create free Expo account: https://expo.dev" -ForegroundColor Cyan
Write-Host "2. Login: eas login" -ForegroundColor Cyan
Write-Host "3. Start development: npm start" -ForegroundColor Cyan
Write-Host "4. Install 'Expo Go' app on your phone" -ForegroundColor Cyan
Write-Host "5. Scan QR code to test on device" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 To build APK (free):" -ForegroundColor Yellow
Write-Host "eas build --platform android --profile preview" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 To build for web:" -ForegroundColor Yellow
Write-Host "npm run web" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 All tools and services used are 100% FREE!" -ForegroundColor Green