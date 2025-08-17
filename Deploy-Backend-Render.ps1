# 🚀 DEPLOY CAMBOAI TRADERSTATION BACKEND TO RENDER
# Trade with Vision, Learn with Purpose, Evolve with AI

Write-Host "🚀 DEPLOYING BACKEND TO RENDER..." -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Create render.yaml if it doesn't exist
$renderConfig = @"
services:
  - type: web
    name: camboai-traderstation-api
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: DATABASE_URL
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY  
        sync: false
      - key: GOOGLE_AI_API_KEY
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
        
  - type: postgresql
    name: camboai-traderstation-db
    databaseName: camboai_db
    user: camboai_user
    plan: starter

  - type: redis
    name: camboai-traderstation-cache
    plan: starter
"@

Write-Host "📝 Creating render.yaml..." -ForegroundColor Yellow
$renderConfig | Out-File -FilePath "render.yaml" -Encoding UTF8

# Create Dockerfile for Render
$dockerfile = @"
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"@

Write-Host "🐳 Creating Dockerfile..." -ForegroundColor Yellow
$dockerfile | Out-File -FilePath "Dockerfile" -Encoding UTF8

Write-Host "`n✅ RENDER DEPLOYMENT FILES CREATED:" -ForegroundColor Green
Write-Host "   📝 render.yaml - Service configuration" -ForegroundColor White  
Write-Host "   🐳 Dockerfile - Container setup" -ForegroundColor White

Write-Host "`n🌐 MANUAL RENDER SETUP REQUIRED:" -ForegroundColor Cyan
Write-Host "1. Go to: https://render.com" -ForegroundColor White
Write-Host "2. Connect your GitHub repository" -ForegroundColor White
Write-Host "3. Create new Web Service" -ForegroundColor White
Write-Host "4. Select your CamboAI repo" -ForegroundColor White
Write-Host "5. Use these settings:" -ForegroundColor White
Write-Host "   - Build Command: pip install -r backend/requirements.txt" -ForegroundColor Gray
Write-Host "   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port `$PORT" -ForegroundColor Gray
Write-Host "   - Root Directory: backend/" -ForegroundColor Gray

Write-Host "`n🔑 ENVIRONMENT VARIABLES TO SET:" -ForegroundColor Yellow
Write-Host "   OPENAI_API_KEY=your_openai_key" -ForegroundColor Gray
Write-Host "   ANTHROPIC_API_KEY=your_claude_key" -ForegroundColor Gray
Write-Host "   GOOGLE_AI_API_KEY=your_gemini_key" -ForegroundColor Gray
Write-Host "   JWT_SECRET_KEY=your_jwt_secret" -ForegroundColor Gray
Write-Host "   DATABASE_URL=postgresql://..." -ForegroundColor Gray

Write-Host "`n🎉 CAMBOAI TRADERSTATION BACKEND READY!" -ForegroundColor Green
Write-Host "Trade with Vision, Learn with Purpose, Evolve with AI ✨" -ForegroundColor Cyan