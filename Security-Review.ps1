#!/usr/bin/env powershell
# Cambo AI Trader Station - Security Review and Configuration Script

param(
    [string]$Environment = "production",
    [switch]$Fix = $false,
    [switch]$Verbose = $false
)

Write-Host "🔒 Cambo AI Trader Station - Security Review" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow

$securityIssues = @()
$recommendations = @()

function Add-SecurityIssue {
    param($Severity, $Description, $Fix = $null)
    $script:securityIssues += [PSCustomObject]@{
        Severity = $Severity
        Description = $Description
        Fix = $Fix
    }
}

function Add-Recommendation {
    param($Description)
    $script:recommendations += $Description
}

# Load environment variables
if (Test-Path ".env.$Environment") {
    Get-Content ".env.$Environment" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

Write-Host "`n🔍 Performing security audit..." -ForegroundColor Blue

# 1. Environment Variables Security Check
Write-Host "1️⃣ Checking environment variables..." -ForegroundColor Cyan

$secretKey = [Environment]::GetEnvironmentVariable("SECRET_KEY")
if (-not $secretKey) {
    Add-SecurityIssue "HIGH" "SECRET_KEY is not set"
} elseif ($secretKey.Length -lt 32) {
    Add-SecurityIssue "HIGH" "SECRET_KEY is too short (minimum 32 characters)"
} elseif ($secretKey -eq "development_secret_key_not_for_production_use_only") {
    Add-SecurityIssue "CRITICAL" "Using default development SECRET_KEY in production"
}

$jwtSecret = [Environment]::GetEnvironmentVariable("JWT_SECRET_KEY")
if (-not $jwtSecret) {
    Add-SecurityIssue "HIGH" "JWT_SECRET_KEY is not set"
} elseif ($jwtSecret.Length -lt 32) {
    Add-SecurityIssue "HIGH" "JWT_SECRET_KEY is too short (minimum 32 characters)"
}

if ($Environment -eq "production") {
    $debug = [Environment]::GetEnvironmentVariable("DEBUG")
    if ($debug -eq "true") {
        Add-SecurityIssue "HIGH" "DEBUG mode is enabled in production"
    }
    
    $sslRedirect = [Environment]::GetEnvironmentVariable("SECURE_SSL_REDIRECT")
    if ($sslRedirect -ne "true") {
        Add-SecurityIssue "MEDIUM" "SSL redirect is not enforced"
    }
}

# 2. Database Security Check
Write-Host "2️⃣ Checking database security..." -ForegroundColor Cyan

$dbUrl = [Environment]::GetEnvironmentVariable("DATABASE_URL")
if ($dbUrl -and $dbUrl -match "://([^:]+):([^@]+)@") {
    $dbUser = $matches[1]
    $dbPass = $matches[2]
    
    if ($dbUser -eq "postgres" -or $dbUser -eq "root") {
        Add-SecurityIssue "HIGH" "Using default database superuser account"
    }
    
    if ($dbPass.Length -lt 12) {
        Add-SecurityIssue "HIGH" "Database password is too short (minimum 12 characters)"
    }
    
    # Check for common weak passwords
    $weakPasswords = @("password", "123456", "admin", "cambo", "trader")
    if ($dbPass.ToLower() -in $weakPasswords) {
        Add-SecurityIssue "CRITICAL" "Database password is commonly used and weak"
    }
}

# 3. Redis Security Check
Write-Host "3️⃣ Checking Redis security..." -ForegroundColor Cyan

$redisUrl = [Environment]::GetEnvironmentVariable("REDIS_URL")
if ($redisUrl -and $redisUrl -notmatch "password=") {
    Add-SecurityIssue "MEDIUM" "Redis is not password protected"
}

# 4. API Keys Security Check
Write-Host "4️⃣ Checking API keys..." -ForegroundColor Cyan

$alpacaKey = [Environment]::GetEnvironmentVariable("ALPACA_API_KEY")
$alpacaSecret = [Environment]::GetEnvironmentVariable("ALPACA_SECRET_KEY")

if (-not $alpacaKey -or -not $alpacaSecret) {
    Add-SecurityIssue "HIGH" "Alpaca API credentials are not configured"
}

$alpacaUrl = [Environment]::GetEnvironmentVariable("ALPACA_BASE_URL")
if ($Environment -eq "production" -and $alpacaUrl -match "paper-api") {
    Add-SecurityIssue "HIGH" "Using paper trading API in production environment"
}

# 5. Rate Limiting Configuration Check
Write-Host "5️⃣ Checking rate limiting configuration..." -ForegroundColor Cyan

$rateLimitEnabled = [Environment]::GetEnvironmentVariable("RATE_LIMIT_ENABLED")
if ($rateLimitEnabled -ne "true") {
    Add-SecurityIssue "HIGH" "Rate limiting is disabled"
}

# 6. CORS Configuration Check
Write-Host "6️⃣ Checking CORS configuration..." -ForegroundColor Cyan

$corsOrigins = [Environment]::GetEnvironmentVariable("CORS_ORIGINS")
if ($corsOrigins -and $corsOrigins -match "\*") {
    Add-SecurityIssue "HIGH" "CORS allows all origins (*)"
}

# 7. File Permissions Check
Write-Host "7️⃣ Checking file permissions..." -ForegroundColor Cyan

$sensitiveFiles = @(
    ".env.production",
    ".env.development", 
    "redis.conf",
    "backend/logs/",
    "init-db.sql"
)

foreach ($file in $sensitiveFiles) {
    if (Test-Path $file) {
        # On Windows, check if file is readable by everyone
        $acl = Get-Acl $file
        $everyoneAccess = $acl.Access | Where-Object { $_.IdentityReference -eq "Everyone" }
        if ($everyoneAccess) {
            Add-SecurityIssue "MEDIUM" "File $file has permissions for 'Everyone'"
        }
    }
}

# 8. Docker Security Check
Write-Host "8️⃣ Checking Docker security..." -ForegroundColor Cyan

if (Test-Path "docker-compose.prod.yml") {
    $dockerCompose = Get-Content "docker-compose.prod.yml" -Raw
    
    # Check for privileged containers
    if ($dockerCompose -match "privileged:\s*true") {
        Add-SecurityIssue "HIGH" "Docker containers running with privileged access"
    }
    
    # Check for host network mode
    if ($dockerCompose -match "network_mode:\s*host") {
        Add-SecurityIssue "MEDIUM" "Docker containers using host network mode"
    }
    
    # Check for volume mounts to sensitive directories
    if ($dockerCompose -match "/etc:|/var/lib/docker:|/proc:|/sys:") {
        Add-SecurityIssue "HIGH" "Docker containers mounting sensitive host directories"
    }
}

# 9. SSL/TLS Configuration Check
Write-Host "9️⃣ Checking SSL/TLS configuration..." -ForegroundColor Cyan

if ($Environment -eq "production") {
    $secureSession = [Environment]::GetEnvironmentVariable("SESSION_COOKIE_SECURE")
    $secureCsrf = [Environment]::GetEnvironmentVariable("CSRF_COOKIE_SECURE")
    
    if ($secureSession -ne "true") {
        Add-SecurityIssue "HIGH" "Session cookies are not marked as secure"
    }
    
    if ($secureCsrf -ne "true") {
        Add-SecurityIssue "HIGH" "CSRF cookies are not marked as secure"
    }
}

# 10. Logging and Monitoring Check
Write-Host "🔟 Checking logging and monitoring..." -ForegroundColor Cyan

$auditLogging = [Environment]::GetEnvironmentVariable("AUDIT_LOGGING")
if ($auditLogging -ne "true") {
    Add-SecurityIssue "MEDIUM" "Audit logging is disabled"
}

$prometheusEnabled = [Environment]::GetEnvironmentVariable("PROMETHEUS_ENABLED")
if ($prometheusEnabled -ne "true") {
    Add-SecurityIssue "LOW" "Prometheus monitoring is disabled"
}

# Display Results
Write-Host "`n📊 Security Audit Results" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

if ($securityIssues.Count -eq 0) {
    Write-Host "✅ No security issues found!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Found $($securityIssues.Count) security issue(s):" -ForegroundColor Yellow
    
    $criticalIssues = $securityIssues | Where-Object { $_.Severity -eq "CRITICAL" }
    $highIssues = $securityIssues | Where-Object { $_.Severity -eq "HIGH" }
    $mediumIssues = $securityIssues | Where-Object { $_.Severity -eq "MEDIUM" }
    $lowIssues = $securityIssues | Where-Object { $_.Severity -eq "LOW" }
    
    if ($criticalIssues) {
        Write-Host "`n🚨 CRITICAL Issues:" -ForegroundColor Red
        $criticalIssues | ForEach-Object { Write-Host "  - $($_.Description)" -ForegroundColor Red }
    }
    
    if ($highIssues) {
        Write-Host "`n🔴 HIGH Issues:" -ForegroundColor DarkRed
        $highIssues | ForEach-Object { Write-Host "  - $($_.Description)" -ForegroundColor DarkRed }
    }
    
    if ($mediumIssues) {
        Write-Host "`n🟡 MEDIUM Issues:" -ForegroundColor Yellow
        $mediumIssues | ForEach-Object { Write-Host "  - $($_.Description)" -ForegroundColor Yellow }
    }
    
    if ($lowIssues) {
        Write-Host "`n🟢 LOW Issues:" -ForegroundColor Green
        $lowIssues | ForEach-Object { Write-Host "  - $($_.Description)" -ForegroundColor Green }
    }
}

# Security Recommendations
Write-Host "`n💡 Security Recommendations" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

Add-Recommendation "Enable two-factor authentication for admin accounts"
Add-Recommendation "Implement IP whitelisting for administrative endpoints"
Add-Recommendation "Set up automated security scanning in CI/CD pipeline"
Add-Recommendation "Configure log aggregation and monitoring (ELK stack)"
Add-Recommendation "Implement API versioning and deprecation policies"
Add-Recommendation "Set up automated backups with encryption"
Add-Recommendation "Configure fail2ban or similar intrusion prevention"
Add-Recommendation "Implement secrets rotation policies"
Add-Recommendation "Set up vulnerability scanning for Docker images"
Add-Recommendation "Configure database connection pooling and limits"

$recommendations | ForEach-Object { Write-Host "  • $_" -ForegroundColor Gray }

# Rate Limiting Configuration
Write-Host "`n⚡ Current Rate Limiting Configuration" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$rateLimits = @{
    "Authentication" = "10 requests/minute, 50 requests/hour"
    "Trading" = "30 requests/minute, 200 requests/hour"
    "Market Data" = "120 requests/minute, 2000 requests/hour"
    "Default" = "60 requests/minute, 1000 requests/hour"
}

$rateLimits.GetEnumerator() | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)" -ForegroundColor White
}

# Security Score
$totalIssues = $securityIssues.Count
$criticalCount = ($securityIssues | Where-Object { $_.Severity -eq "CRITICAL" }).Count
$highCount = ($securityIssues | Where-Object { $_.Severity -eq "HIGH" }).Count

$securityScore = 100 - ($criticalCount * 25) - ($highCount * 10) - (($totalIssues - $criticalCount - $highCount) * 5)
$securityScore = [Math]::Max(0, $securityScore)

Write-Host "`n🏆 Security Score: $securityScore/100" -ForegroundColor $(
    if ($securityScore -ge 90) { "Green" }
    elseif ($securityScore -ge 70) { "Yellow" }
    else { "Red" }
)

if ($securityScore -lt 70) {
    Write-Host "⚠️ Security score is below 70. Address critical and high issues before production deployment." -ForegroundColor Red
}

Write-Host "`n🔒 Security audit completed!" -ForegroundColor Green
Write-Host "💡 For detailed security hardening guide, refer to the documentation." -ForegroundColor Yellow
