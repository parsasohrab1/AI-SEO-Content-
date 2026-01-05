# AI Content Factory Pro - Stop All Servers
# متوقف کردن Backend و Frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stopping AI Content Factory Pro Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# متوقف کردن فرآیندهای Python (Backend)
Write-Host "Stopping Backend (Python/Uvicorn)..." -ForegroundColor Yellow
$pythonProcesses = Get-Process | Where-Object {
    $_.ProcessName -eq "python" -or $_.ProcessName -eq "pythonw"
} | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*main:app*"
}

if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Write-Host "  Stopping process: $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Backend stopped" -ForegroundColor Green
} else {
    Write-Host "  No Backend processes found" -ForegroundColor Gray
}

# متوقف کردن فرآیندهای Node (Frontend)
Write-Host ""
Write-Host "Stopping Frontend (Node/Next.js)..." -ForegroundColor Yellow
$nodeProcesses = Get-Process | Where-Object {
    $_.ProcessName -eq "node"
} | Where-Object {
    $_.CommandLine -like "*next*" -or $_.CommandLine -like "*dev*"
}

if ($nodeProcesses) {
    $nodeProcesses | ForEach-Object {
        Write-Host "  Stopping process: $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Frontend stopped" -ForegroundColor Green
} else {
    Write-Host "  No Frontend processes found" -ForegroundColor Gray
}

# متوقف کردن فرآیندهای روی پورت‌های مشخص
Write-Host ""
Write-Host "Checking ports 8002 and 3002..." -ForegroundColor Yellow

$port8002 = Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue
if ($port8002) {
    $pid8002 = $port8002.OwningProcess | Select-Object -Unique
    $pid8002 | ForEach-Object {
        Write-Host "  Stopping process on port 8002 (PID: $_)" -ForegroundColor Gray
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
}

$port3002 = Get-NetTCPConnection -LocalPort 3002 -ErrorAction SilentlyContinue
if ($port3002) {
    $pid3002 = $port3002.OwningProcess | Select-Object -Unique
    $pid3002 | ForEach-Object {
        Write-Host "  Stopping process on port 3002 (PID: $_)" -ForegroundColor Gray
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "✅ All servers stopped" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

