@echo off
:: Installs KARE as a Windows Task Scheduler task that starts on login
:: and runs hidden (no console window). Run once as Administrator.
cd /d "%~dp0"

set TASK=KARE Health Tracker
set VBS="%~dp0run_hidden.vbs"

echo.
echo  Installing KARE as a startup service...
echo.

schtasks /create /tn "%TASK%" /tr "wscript.exe %VBS%" /sc onlogon /rl highest /f >nul 2>&1
if errorlevel 1 (
    echo  Failed. Try running this as Administrator.
    pause
    exit /b 1
)

echo  Done! KARE will now start automatically on login.
echo  To start it now without rebooting, run: wscript.exe %VBS%
echo  To remove it: run uninstall_service.bat
echo.
pause
