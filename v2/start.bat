@echo off
cd /d "%~dp0"

if not exist .env (
    echo .env not found. Running setup first...
    call setup.bat
    if errorlevel 1 exit /b 1
)

:: Read PORT from .env (default 8084)
set PORT=8084
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if /i "%%a"=="PORT" set PORT=%%b
)

echo Starting KARE on port %PORT%...
start "" http://localhost:%PORT%

python --version >nul 2>&1
if not errorlevel 1 (
    python server.py
    pause
    exit /b 0
)

py --version >nul 2>&1
if not errorlevel 1 (
    py server.py
    pause
    exit /b 0
)

echo.
echo  Python is not installed. Please run setup.bat first.
echo.
pause
