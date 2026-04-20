@echo off
:: KARE — Windows first-time setup
setlocal

echo.
echo  KARE — Setup
echo  ==========================
echo.

:: Check Python — try both "python" and "py" (Windows launcher)
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo  Python is not installed.
        echo.
        echo  This script will download and install Python automatically.
        echo  Press any key to open the Python installer download page,
        echo  OR close this window and install it manually from:
        echo    https://www.python.org/downloads/
        echo.
        echo  IMPORTANT during install: CHECK the box "Add Python to PATH"
        pause
        start "" "https://www.python.org/downloads/"
        echo.
        echo  After Python is installed, run this setup.bat again.
        pause
        exit /b 1
    ) else (
        set PYTHON=py
    )
) else (
    set PYTHON=python
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  Found: %PYVER%
echo.

:: Create .env if missing
if exist .env (
    echo  .env already exists — skipping.
) else (
    echo  Setting up WhatsApp reminders...
    echo.
    echo  Step 1: Save this number in your WhatsApp contacts: +34 644 51 68 88
    echo  Step 2: Send it this exact message:  I allow callmebot to send me messages
    echo  Step 3: You will receive your API key. Enter it below.
    echo.
    set /p WA_PHONE="  Your WhatsApp number (with country code, no + sign, e.g. 919876543210): "
    set /p WA_KEY="  Your CallMeBot API key (press Enter to skip for now): "
    set /p WA_PORT="  Port (press Enter for default 8084): "
    if "%WA_PORT%"=="" set WA_PORT=8084
    (
        echo WHATSAPP_PHONE=%WA_PHONE%
        echo CALLMEBOT_APIKEY=%WA_KEY%
        echo PORT=%WA_PORT%
    ) > .env
    echo.
    echo  .env created.
)

echo.
echo  Setup complete!
echo  Run start.bat to launch the tracker.
echo.
pause
