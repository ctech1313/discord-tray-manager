@echo off
echo Discord Tray Manager - Complete Build Script
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Step 1: Creating application icon...
python create_icon.py
if errorlevel 1 (
    echo WARNING: Could not create icon, continuing without it...
)
echo.

echo Step 2: Building executable with PyInstaller...
python build_exe.py
if errorlevel 1 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)
echo.

echo Step 3: Copying files for installer...
if not exist "dist\DiscordTrayManager.exe" (
    echo ERROR: Executable not found in dist folder
    pause
    exit /b 1
)

REM Copy necessary files to root for NSIS
copy "dist\DiscordTrayManager.exe" .
copy "config.json" .
copy "README.md" .

echo Step 4: Building installer with NSIS...
REM Check if NSIS is installed
where makensis >nul 2>&1
if errorlevel 1 (
    echo ERROR: NSIS (Nullsoft Scriptable Install System) is not installed
    echo Please download and install NSIS from: https://nsis.sourceforge.io/
    echo Then add the NSIS directory to your PATH
    pause
    exit /b 1
)

makensis installer.nsi
if errorlevel 1 (
    echo ERROR: Failed to build installer
    pause
    exit /b 1
)

echo.
echo ============================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ============================================
echo.
echo Created files:
echo - Discord_Tray_Manager_Setup.exe (Windows Installer)
echo - Discord_Tray_Manager_Portable\ (Portable version)
echo.
echo The installer will:
echo - Install the application to Program Files
echo - Add it to Windows startup
echo - Create Start Menu shortcuts
echo - Add uninstaller to Control Panel
echo.
echo The application will run in the system tray (notification area)
echo and automatically manage Discord's tray icon visibility.
echo.

REM Clean up temporary files
del "DiscordTrayManager.exe" 2>nul
echo Cleaned up temporary build files.
echo.
echo Build process complete!
pause 