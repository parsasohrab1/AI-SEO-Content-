# AI Content Factory Pro - PowerShell Startup Script
# راه‌اندازی Backend و Frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Content Factory Pro - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# تنظیم مسیرها
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $scriptPath "backend"
$frontendPath = Join-Path $scriptPath "frontend"

# بررسی وجود مسیرها
if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Backend directory not found: $backendPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ Frontend directory not found: $frontendPath" -ForegroundColor Red
    exit 1
}

# ============================================
# راه‌اندازی Backend
# ============================================
Write-Host "[1/2] Starting Backend on Port 8002..." -ForegroundColor Yellow
Write-Host ""

Set-Location $backendPath

# بررسی و ایجاد Virtual Environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# فعال‌سازی Virtual Environment
$venvPython = Join-Path $backendPath "venv\Scripts\python.exe"
$venvActivate = Join-Path $backendPath "venv\Scripts\Activate.ps1"

if (Test-Path $venvPython) {
    Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
    & $venvPython -m pip install -q fastapi uvicorn[standard] pydantic httpx beautifulsoup4 lxml 2>&1 | Out-Null
} else {
    Write-Host "⚠️  Virtual environment Python not found, using system Python" -ForegroundColor Yellow
    $venvPython = "python"
    python -m pip install -q fastapi uvicorn[standard] pydantic httpx beautifulsoup4 lxml 2>&1 | Out-Null
}

# راه‌اندازی Backend در پنجره جدید
Write-Host "Starting Backend server..." -ForegroundColor Green
$backendScript = @"
`$ErrorActionPreference = 'Stop'
Set-Location '$backendPath'
if (Test-Path '$venvActivate') {
    & '$venvActivate'
    & '$venvPython' -m uvicorn main:app --reload --host 0.0.0.0 --port 8002
} else {
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002
}
"@

$backendScriptPath = Join-Path $env:TEMP "start-backend.ps1"
$backendScript | Out-File -FilePath $backendScriptPath -Encoding UTF8

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "& '$backendScriptPath'" -WindowStyle Normal

Write-Host "✅ Backend starting in new window..." -ForegroundColor Green
Write-Host ""

# انتظار برای راه‌اندازی Backend
Write-Host "Waiting 5 seconds for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# ============================================
# راه‌اندازی Frontend
# ============================================
Write-Host "[2/2] Starting Frontend on Port 3002..." -ForegroundColor Yellow
Write-Host ""

Set-Location $frontendPath

# بررسی و نصب Dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  npm install had warnings, but continuing..." -ForegroundColor Yellow
    }
}

# راه‌اندازی Frontend در پنجره جدید
Write-Host "Starting Frontend server..." -ForegroundColor Green
$frontendScript = @"
`$ErrorActionPreference = 'Stop'
Set-Location '$frontendPath'
npm run dev -- -p 3002
"@

$frontendScriptPath = Join-Path $env:TEMP "start-frontend.ps1"
$frontendScript | Out-File -FilePath $frontendScriptPath -Encoding UTF8

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "& '$frontendScriptPath'" -WindowStyle Normal

Write-Host "✅ Frontend starting in new window..." -ForegroundColor Green
Write-Host ""

# ============================================
# خلاصه
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Servers are starting in separate windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Backend:  http://localhost:8002" -ForegroundColor Green
Write-Host "📍 Frontend: http://localhost:3002" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Please wait 10-15 seconds for servers to start..." -ForegroundColor Yellow
Write-Host "🌐 Then open http://localhost:3002 in your browser" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

