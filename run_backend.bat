@echo off
title City ANPR - Backend Server
cd /d "%~dp0"
echo ========================================================
echo Starting City-Wide ANPR Backend Server (FastAPI)...
echo ========================================================
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
