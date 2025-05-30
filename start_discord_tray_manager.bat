@echo off
echo Starting Discord Tray Manager...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if the script exists
if not exist "discord_tray_manager.py" (
    echo ERROR: discord_tray_manager.py not found
    echo Make sure you're running this from the correct directory
    pause
    exit /b 1
)

echo Python found, starting Discord Tray Manager...
echo.

REM Run the Python script
python discord_tray_manager.py

echo.
echo Discord Tray Manager has stopped.
pause 