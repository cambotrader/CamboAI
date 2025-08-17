# 🚀 One-Click Cloud Deployment
# Deploy CamboAI to cloud providers with Docker

Write-Host "🚀 CamboAI Cloud Deployment..." -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Create production Docker configurations
Write-Host "`n🐳 Creating Docker configurations..." -ForegroundColor Yellow

# Production Dockerfile for backend
$backendDockerfile = @'
# 🚀 CamboAI Backend - Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
'@

$backendDockerfile | Out-File -FilePath "backend\Dockerfile.prod" -Encoding UTF8

# Production Docker Compose
$dockerComposeProd = @'
# 🚀 CamboAI Production Docker Compose
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: camboai-db
    environment:
      POSTGRES_DB: camboai_prod
      POSTGRES_USER: camboai_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    networks:
      - camboai-network
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: camboai-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - camboai-network
    restart: unless-stopped

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: camboai-backend
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://camboai_user:${DB_PASSWORD}@db:5432/camboai_prod
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ALPACA_API_KEY=${ALPACA_API_KEY}
      - ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
      - ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
      - IEX_API_KEY=${IEX_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    networks:
      - camboai-network
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend-new
      dockerfile: Dockerfile.prod
    container_name: camboai-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - camboai-network
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: camboai-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - camboai-network
    restart: unless-stopped

  # Monitoring - Prometheus
  prometheus:
    image: prom/prometheus
    container_name: camboai-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - camboai-network
    restart: unless-stopped

  # Monitoring - Grafana
  grafana:
    image: grafana/grafana
    container_name: camboai-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - camboai-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  camboai-network:
    driver: bridge
'@

$dockerComposeProd | Out-File -FilePath "docker-compose.production.yml" -Encoding UTF8

# Frontend production Dockerfile
$frontendDockerfileProd = @'
# 🌐 CamboAI Frontend - Production Build
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
'@

$frontendDockerfileProd | Out-File -FilePath "frontend-new\Dockerfile.prod" -Encoding UTF8

# Nginx configuration for frontend
$nginxConfig = @'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket proxy
    location /ws {
        proxy_pass http://backend:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
'@

$nginxConfig | Out-File -FilePath "frontend-new\nginx.conf" -Encoding UTF8

# Production environment template
$envProd = @'
# 🚀 CamboAI Production Environment Variables
# Copy this to .env.production and fill in your values

# Database
DB_PASSWORD=your-secure-database-password

# Redis
REDIS_PASSWORD=your-secure-redis-password

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-super-secure-jwt-secret-key-32-chars-minimum

# Market Data APIs
ALPACA_API_KEY=your-alpaca-api-key
ALPACA_SECRET_KEY=your-alpaca-secret-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
IEX_API_KEY=your-iex-key

# AI Services
OPENAI_API_KEY=your-openai-key

# Monitoring
GRAFANA_PASSWORD=your-grafana-admin-password

# Email (optional)
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
'@

$envProd | Out-File -FilePath ".env.production.template" -Encoding UTF8

# Deployment scripts for different cloud providers

# AWS ECS deployment
$awsEcsTask = @'
{
  "family": "camboai-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "camboai-backend",
      "image": "YOUR_ACCOUNT.dkr.ecr.YOUR_REGION.amazonaws.com/camboai-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:YOUR_REGION:YOUR_ACCOUNT:secret:camboai-db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/camboai",
          "awslogs-region": "YOUR_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
'@

$awsEcsTask | Out-File -FilePath "deploy\aws-ecs-task.json" -Encoding UTF8

# Create deployment scripts
$deployAws = @'
#!/bin/bash
# 🚀 Deploy CamboAI to AWS ECS

echo "🚀 Deploying CamboAI to AWS ECS..."

# Build and push Docker images
docker build -t camboai-backend:latest backend/
docker build -t camboai-frontend:latest frontend-new/

# Tag for ECR
docker tag camboai-backend:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/camboai-backend:latest
docker tag camboai-frontend:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/camboai-frontend:latest

# Push to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/camboai-backend:latest
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/camboai-frontend:latest

# Update ECS service
aws ecs update-service --cluster camboai-cluster --service camboai-service --force-new-deployment

echo "✅ Deployment to AWS ECS complete!"
'@

$deployAws | Out-File -FilePath "deploy\deploy-aws.sh" -Encoding UTF8

# Digital Ocean deployment
$deployDigitalOcean = @'
#!/bin/bash
# 🚀 Deploy CamboAI to Digital Ocean

echo "🚀 Deploying CamboAI to Digital Ocean..."

# Create droplet if not exists
doctl compute droplet create camboai-prod \
    --region nyc1 \
    --image ubuntu-22-04-x64 \
    --size s-2vcpu-4gb \
    --ssh-keys $SSH_KEY_ID

# Wait for droplet to be ready
sleep 60

# Get droplet IP
DROPLET_IP=$(doctl compute droplet get camboai-prod --format PublicIPv4 --no-header)

# Deploy via SSH
scp -r . root@$DROPLET_IP:/root/camboai/
ssh root@$DROPLET_IP "cd /root/camboai && docker-compose -f docker-compose.production.yml up -d"

echo "✅ Deployed to Digital Ocean at http://$DROPLET_IP"
'@

$deployDigitalOcean | Out-File -FilePath "deploy\deploy-digitalocean.sh" -Encoding UTF8

# Local production deployment
$deployLocal = @'
# 🏠 Deploy CamboAI Locally (Production Mode)

Write-Host "🏠 Starting CamboAI in Production Mode..." -ForegroundColor Green

# Check if Docker is running
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop" -ForegroundColor Red
    Write-Host "Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Blue
    exit 1
}

# Check if .env.production exists
if (-not (Test-Path ".env.production")) {
    Write-Host "📝 Creating production environment file..." -ForegroundColor Yellow
    Copy-Item ".env.production.template" ".env.production"
    
    Write-Host "⚠️ Please edit .env.production with your configuration" -ForegroundColor Yellow
    Write-Host "Required: DB_PASSWORD, REDIS_PASSWORD, SECRET_KEY" -ForegroundColor Red
    
    # Generate secure secrets
    $dbPassword = -join ((1..16) | ForEach { [char]((65..90) + (97..122) + (48..57) | Get-Random) })
    $redisPassword = -join ((1..16) | ForEach { [char]((65..90) + (97..122) + (48..57) | Get-Random) })
    $secretKey = -join ((1..32) | ForEach { [char]((65..90) + (97..122) + (48..57) | Get-Random) })
    
    Write-Host "`nGenerated secure passwords:" -ForegroundColor Cyan
    Write-Host "DB_PASSWORD=$dbPassword" -ForegroundColor Gray
    Write-Host "REDIS_PASSWORD=$redisPassword" -ForegroundColor Gray  
    Write-Host "SECRET_KEY=$secretKey" -ForegroundColor Gray
    
    # Update .env.production with generated passwords
    (Get-Content ".env.production") -replace "your-secure-database-password", $dbPassword -replace "your-secure-redis-password", $redisPassword -replace "your-super-secure-jwt-secret-key-32-chars-minimum", $secretKey | Set-Content ".env.production"
}

# Load environment variables
Get-Content ".env.production" | ForEach {
    if ($_ -match "^([^=]+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Create necessary directories
New-Item -ItemType Directory -Path "logs", "monitoring", "nginx" -Force | Out-Null

# Start services
Write-Host "`n🚀 Starting all services..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
Write-Host "`n⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host "`n🔍 Checking service health..." -ForegroundColor Yellow

$services = @("camboai-db", "camboai-redis", "camboai-backend")
foreach ($service in $services) {
    $status = docker inspect --format="{{.State.Health.Status}}" $service 2>$null
    if ($status -eq "healthy" -or $status -eq "") {
        $running = docker inspect --format="{{.State.Running}}" $service
        if ($running -eq "true") {
            Write-Host "✅ $service is running" -ForegroundColor Green
        } else {
            Write-Host "❌ $service is not running" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ $service health: $status" -ForegroundColor Yellow
    }
}

Write-Host "`n🎉 CamboAI Production Deployment Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

Write-Host "`n🌐 Access Points:" -ForegroundColor Cyan
Write-Host "• Main Application: http://localhost" -ForegroundColor White
Write-Host "• API Backend: http://localhost:8000" -ForegroundColor White
Write-Host "• API Docs: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "• Database: localhost:5432" -ForegroundColor White
Write-Host "• Redis: localhost:6379" -ForegroundColor White
Write-Host "• Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "• Grafana: http://localhost:3001" -ForegroundColor White

Write-Host "`n📊 Monitoring:" -ForegroundColor Cyan
Write-Host "• View logs: docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor Gray
Write-Host "• Stop services: docker-compose -f docker-compose.production.yml down" -ForegroundColor Gray
Write-Host "• Restart: docker-compose -f docker-compose.production.yml restart" -ForegroundColor Gray

Write-Host "`n🔐 Security Notes:" -ForegroundColor Yellow
Write-Host "• Change default passwords in .env.production" -ForegroundColor Gray
Write-Host "• Enable SSL/TLS for production use" -ForegroundColor Gray
Write-Host "• Configure firewall rules" -ForegroundColor Gray
Write-Host "• Set up backup procedures" -ForegroundColor Gray

# Open browser
Start-Process "http://localhost"
'@

$deployLocal | Out-File -FilePath "Deploy-Production-Local.ps1" -Encoding UTF8

Write-Host "`n✅ Cloud deployment configurations created!" -ForegroundColor Green

Write-Host "`n🚀 DEPLOYMENT OPTIONS:" -ForegroundColor Cyan

Write-Host "`n1. Local Production (Recommended for testing):" -ForegroundColor White
Write-Host "   .\Deploy-Production-Local.ps1" -ForegroundColor Yellow

Write-Host "`n2. Digital Ocean (Easy cloud deployment):" -ForegroundColor White
Write-Host "   • Sign up: https://digitalocean.com" -ForegroundColor Blue
Write-Host "   • Install doctl CLI" -ForegroundColor Gray
Write-Host "   • Run: .\deploy\deploy-digitalocean.sh" -ForegroundColor Yellow

Write-Host "`n3. AWS ECS (Enterprise scale):" -ForegroundColor White
Write-Host "   • Configure AWS CLI" -ForegroundColor Gray
Write-Host "   • Update deploy\aws-ecs-task.json" -ForegroundColor Gray
Write-Host "   • Run: .\deploy\deploy-aws.sh" -ForegroundColor Yellow

Write-Host "`n4. Docker Compose (Any server):" -ForegroundColor White
Write-Host "   • Copy files to server" -ForegroundColor Gray
Write-Host "   • Edit .env.production" -ForegroundColor Gray
Write-Host "   • Run: docker-compose -f docker-compose.production.yml up -d" -ForegroundColor Yellow

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Choose deployment method above" -ForegroundColor White
Write-Host "2. Configure API keys in .env.production" -ForegroundColor White
Write-Host "3. Deploy and test" -ForegroundColor White
Write-Host "4. Set up monitoring and backups" -ForegroundColor White

Write-Host "`n✅ Production deployment ready!" -ForegroundColor Green