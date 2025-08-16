#!/usr/bin/env pwsh
# CamboAI Full Platform Deployment Script

Write-Host "🚀 CamboAI Full Platform Deployment Starting..." -ForegroundColor Green

# Check requirements
$tools = @("git", "npm", "expo", "gh")
foreach ($tool in $tools) {
    if (!(Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "❌ $tool is required but not installed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All required tools found" -ForegroundColor Green

# 1. BACKEND DEPLOYMENT (Render)
Write-Host "`n📊 Step 1: Preparing Backend for Render..." -ForegroundColor Blue
git add .
git commit -m "feat: prepare for production deployment - all platforms"
git push origin main

Write-Host "✅ Backend pushed to GitHub - Render will auto-deploy" -ForegroundColor Green

# 2. FRONTEND DEPLOYMENT (Vercel)
Write-Host "`n🌐 Step 2: Deploying Frontend to Vercel..." -ForegroundColor Blue
Set-Location "web-advanced"

# Install dependencies
npm install

# Build for production
npm run build

Write-Host "✅ Frontend built successfully" -ForegroundColor Green

# 3. MOBILE APP PREPARATION
Write-Host "`n📱 Step 3: Preparing Mobile Apps..." -ForegroundColor Blue
Set-Location "..\mobile"

# Update API URLs for production
$apiConfig = @"
export const API_CONFIG = {
  BASE_URL: 'https://camboai-api.onrender.com',
  WS_URL: 'wss://camboai-api.onrender.com',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
};

export const APP_CONFIG = {
  NAME: 'CamboAI',
  VERSION: '1.0.0',
  ENVIRONMENT: 'production',
};
"@

$apiConfig | Out-File -FilePath "src/config/api.ts" -Encoding UTF8

# Update app.json for production
$appJson = Get-Content "app.json" | ConvertFrom-Json
$appJson.expo.name = "CamboAI Trading Platform"
$appJson.expo.slug = "camboai"
$appJson.expo.version = "1.0.0"
$appJson.expo.orientation = "portrait"
$appJson.expo.icon = "./assets/icon.png"
$appJson.expo.userInterfaceStyle = "light"
$appJson.expo.splash = @{
    "image" = "./assets/splash.png"
    "resizeMode" = "contain"
    "backgroundColor" = "#ffffff"
}
$appJson.expo.assetBundlePatterns = @("**/*")
$appJson.expo.ios = @{
    "supportsTablet" = $true
    "bundleIdentifier" = "com.camboai.trading"
}
$appJson.expo.android = @{
    "adaptiveIcon" = @{
        "foregroundImage" = "./assets/adaptive-icon.png"
        "backgroundColor" = "#FFFFFF"
    }
    "package" = "com.camboai.trading"
}
$appJson.expo.web = @{
    "favicon" = "./assets/favicon.png"
}

$appJson | ConvertTo-Json -Depth 10 | Out-File -FilePath "app.json" -Encoding UTF8

Write-Host "✅ Mobile app configured for production" -ForegroundColor Green

# Install mobile dependencies
npm install

Write-Host "`n🎉 DEPLOYMENT PREPARATION COMPLETE!" -ForegroundColor Green
Write-Host "`n📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. 🌐 Deploy Frontend: Run 'vercel --prod' in web-advanced/" -ForegroundColor White
Write-Host "2. 📱 Build Android: Run 'eas build --platform android' in mobile/" -ForegroundColor White  
Write-Host "3. 🍎 Build iOS: Run 'eas build --platform ios' in mobile/" -ForegroundColor White
Write-Host "4. 🌍 Setup Cloudflare: Point camboai domain to Vercel" -ForegroundColor White
Write-Host "`n🚀 Your platform will be live across all devices!" -ForegroundColor Green

Set-Location ".."