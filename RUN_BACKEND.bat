@echo off
chcp 65001 >nul
echo ========================================
echo Starting Backend Server
echo ========================================
echo.
cd /d %~dp0backend
echo Activating virtual environment...
call venv\Scripts\activate
echo.
echo Installing/updating dependencies...
pip install -q fastapi uvicorn[standard] pydantic httpx beautifulsoup4 lxml
echo.
echo ========================================
echo Backend Server Starting...
echo URL: http://localhost:8002
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8002
pause

