# AI Content Factory Pro - Backend Startup Script
# راه‌اندازی Backend Server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Content Factory Pro - Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# تنظیم مسیر
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $scriptPath "backend"

if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Backend directory not found: $backendPath" -ForegroundColor Red
    exit 1
}

Set-Location $backendPath

# بررسی Virtual Environment
$venvPython = Join-Path $backendPath "venv\Scripts\python.exe"
$venvActivate = Join-Path $backendPath "venv\Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $venvActivate
    
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & $venvPython -m pip install -q -r requirements.txt 2>&1 | Out-Null
} else {
    Write-Host "⚠️  Virtual environment not found, using system Python" -ForegroundColor Yellow
    $venvPython = "python"
    python -m pip install -q -r requirements.txt 2>&1 | Out-Null
}

Write-Host ""
Write-Host "Starting Backend on http://localhost:8002" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8002/api/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8002/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# راه‌اندازی Uvicorn
& $venvPython -m uvicorn main:app --reload --host 0.0.0.0 --port 8002

