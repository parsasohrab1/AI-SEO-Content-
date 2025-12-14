@echo off
echo Starting Frontend Server...
cd /d %~dp0frontend
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)
echo.
echo Starting Frontend on http://localhost:3002
echo.
npm run dev -- -p 3002
pause

