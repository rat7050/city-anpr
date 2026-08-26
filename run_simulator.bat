@echo off
title City ANPR - Camera Simulator
cd /d "%~dp0"
echo ========================================================
echo Running City-Wide ANPR Camera Simulator...
echo ========================================================
call venv\Scripts\activate.bat
python -m camera_simulator.simulator --mode continuous --api-url http://127.0.0.1:8000 --rate 15
pause
