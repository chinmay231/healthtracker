@echo off
cd /d "%~dp0"

if not exist .env (
    echo .env not found. Running setup first...
    call setup.bat
    if errorlevel 1 exit /b 1
)

:: Try python, then py (Windows launcher)
python --version >nul 2>&1
if not errorlevel 1 (
    echo Starting KARE...
    start "" http://localhost:8080
    python server.py
    pause
    exit /b 0
)

py --version >nul 2>&1
if not errorlevel 1 (
    echo Starting KARE...
    start "" http://localhost:8080
    py server.py
    pause
    exit /b 0
)

echo.
echo  Python is not installed. Please run setup.bat first.
echo.
pause
