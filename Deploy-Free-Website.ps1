# CamboStation Vision - Free Website Deployment
# Deploy your website completely free using Vercel

Write-Host "🌐 Deploying CamboStation Vision Website (100% Free)" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "d:\CamboAI\web")) {
    Write-Host "❌ Web directory not found. Make sure you're in the CamboAI project root." -ForegroundColor Red
    exit 1
}

# Navigate to web directory
Set-Location "d:\CamboAI\web"

# Check if Node.js is installed
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

# Install Vercel CLI (free)
Write-Host "🔧 Installing Vercel CLI (free)..." -ForegroundColor Yellow
npm install -g vercel

# Build the project
Write-Host "🏗️ Building the project..." -ForegroundColor Yellow
npm run build

Write-Host ""
Write-Host "🎉 Ready to deploy! Choose your free option:" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Option 1: Vercel (Recommended - Best for Next.js)" -ForegroundColor Cyan
Write-Host "1. Run: vercel" -ForegroundColor White
Write-Host "2. Follow the prompts" -ForegroundColor White
Write-Host "3. Get free subdomain: your-app.vercel.app" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: Netlify" -ForegroundColor Cyan
Write-Host "1. Install: npm install -g netlify-cli" -ForegroundColor White
Write-Host "2. Run: netlify deploy --prod --dir=.next" -ForegroundColor White
Write-Host ""
Write-Host "Option 3: GitHub Pages" -ForegroundColor Cyan
Write-Host "1. Push code to GitHub" -ForegroundColor White
Write-Host "2. Enable GitHub Pages in repo settings" -ForegroundColor White
Write-Host ""
Write-Host "💡 All options are 100% FREE with generous limits!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Quick deploy with Vercel:" -ForegroundColor Yellow
Write-Host "vercel --prod" -ForegroundColor Cyan