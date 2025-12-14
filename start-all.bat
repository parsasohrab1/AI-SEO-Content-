@echo off
chcp 65001 >nul
echo ========================================
echo AI Content Factory Pro - Quick Start
echo ========================================
echo.

echo [1/2] Starting Backend on Port 8002...
cd /d %~dp0backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing dependencies (this may take a few minutes)...
pip install -q fastapi uvicorn[standard] pydantic httpx beautifulsoup4 lxml >nul 2>&1
start "Backend Server - Port 8002" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && echo Backend starting on http://localhost:8002 && uvicorn main:app --reload --host 0.0.0.0 --port 8002"

echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo [2/2] Starting Frontend on Port 3002...
cd /d %~dp0frontend
if not exist node_modules (
    echo Installing npm dependencies (this may take a few minutes)...
    call npm install >nul 2>&1
)
start "Frontend Server - Port 3002" cmd /k "cd /d %~dp0frontend && echo Frontend starting on http://localhost:3002 && npm run dev -- -p 3002"

echo.
echo ========================================
echo Servers are starting in separate windows
echo ========================================
echo.
echo Backend:  http://localhost:8002
echo Frontend: http://localhost:3002
echo.
echo Please wait 10-15 seconds for servers to start...
echo Then open http://localhost:3002 in your browser
echo.
echo Press any key to exit this window (servers will keep running)...
pause >nul
