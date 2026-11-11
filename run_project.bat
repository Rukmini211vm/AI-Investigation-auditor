@echo off
title AI Investigation Auditor Server
cd /d "%~dp0"

echo =======================================================
echo          AI Investigation Auditor - Quick Start
echo =======================================================
echo.
echo Starting backend server on http://127.0.0.1:8000 ...
echo (Keep this black terminal window OPEN while using the app)
echo.

:: Open browser automatically after 2 seconds in the background
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"

:: Start the Python backend server
python app.py

pause
