@echo off
title City ANPR - Launch All
cd /d "%~dp0"
echo ========================================================
echo Launching City-Wide ANPR System Locally
echo ========================================================

echo 1. Starting Backend Server in a new window...
start "City ANPR - Backend" cmd /c "%~dp0run_backend.bat"

echo 2. Waiting 3 seconds for backend initialization...
timeout /t 3 /nobreak >nul

echo 3. Starting Frontend Dashboard in a new window...
start "City ANPR - Frontend" cmd /c "%~dp0run_frontend.bat"

echo 4. Waiting 3 seconds for frontend server...
timeout /t 3 /nobreak >nul

echo 5. Opening dashboard in default browser...
start http://localhost:5173

echo ========================================================
echo All services started!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://localhost:8000/docs
echo Default Login: admin / admin123
echo ========================================================
