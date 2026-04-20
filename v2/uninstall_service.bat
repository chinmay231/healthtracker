@echo off
cd /d "%~dp0"

set TASK=KARE Health Tracker

schtasks /delete /tn "%TASK%" /f >nul 2>&1
if errorlevel 1 (
    echo  Task not found or already removed.
) else (
    echo  KARE startup task removed.
)

:: Also kill any running instance
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8084"') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo  Done.
pause
