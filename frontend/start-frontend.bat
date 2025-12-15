@echo off
cd /d "%~dp0"
echo Starting Frontend Server on Port 3002...
echo.
call npm run dev -- -p 3002
pause

