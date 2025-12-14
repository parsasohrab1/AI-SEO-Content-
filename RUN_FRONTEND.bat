@echo off
chcp 65001 >nul
echo ========================================
echo Starting Frontend Server
echo ========================================
echo.
cd /d %~dp0frontend
if not exist node_modules (
    echo Installing dependencies (this may take a few minutes)...
    call npm install
    echo.
)
echo ========================================
echo Frontend Server Starting...
echo URL: http://localhost:3002
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.
npm run dev -- -p 3002
pause

