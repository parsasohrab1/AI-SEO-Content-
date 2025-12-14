@echo off
echo Starting Backend Server...
cd /d %~dp0backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing dependencies...
pip install -q -r requirements.txt
echo.
echo Starting Backend on http://localhost:8000
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8002
pause

