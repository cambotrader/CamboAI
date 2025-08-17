# CAMBOAI TRADERSTATION - Backend Deployment to Render
Write-Host "DEPLOYING BACKEND TO RENDER..." -ForegroundColor Green

# Create render.yaml configuration
$renderConfig = @'
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
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GOOGLE_AI_API_KEY
        sync: false
        
  - type: postgresql
    name: camboai-traderstation-db
    databaseName: camboai_db
    user: camboai_user
    plan: starter
'@

Write-Host "Creating render.yaml..." -ForegroundColor Yellow
$renderConfig | Out-File -FilePath "render.yaml" -Encoding UTF8

# Create simple Dockerfile
$dockerfile = @'
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'@

Write-Host "Creating Dockerfile..." -ForegroundColor Yellow
$dockerfile | Out-File -FilePath "Dockerfile" -Encoding UTF8

Write-Host "RENDER DEPLOYMENT FILES CREATED!" -ForegroundColor Green
Write-Host ""
Write-Host "MANUAL RENDER SETUP REQUIRED:" -ForegroundColor Cyan
Write-Host "1. Go to: https://render.com" -ForegroundColor White
Write-Host "2. Connect your GitHub repository" -ForegroundColor White
Write-Host "3. Create new Web Service" -ForegroundColor White
Write-Host "4. Select your CamboAI repo" -ForegroundColor White
Write-Host "5. Use these settings:" -ForegroundColor White
Write-Host "   Build Command: pip install -r backend/requirements.txt" -ForegroundColor Gray
Write-Host "   Start Command: uvicorn app.main:app --host 0.0.0.0 --port `$PORT" -ForegroundColor Gray
Write-Host "   Root Directory: backend/" -ForegroundColor Gray
Write-Host ""
Write-Host "ENVIRONMENT VARIABLES TO ADD:" -ForegroundColor Yellow
Write-Host "   OPENAI_API_KEY=your_key_here" -ForegroundColor Gray
Write-Host "   ANTHROPIC_API_KEY=your_key_here" -ForegroundColor Gray
Write-Host "   GOOGLE_AI_API_KEY=your_key_here" -ForegroundColor Gray
Write-Host ""
Write-Host "CamboAI TraderStation Backend Ready for Render!" -ForegroundColor Green