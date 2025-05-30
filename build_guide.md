# Discord Tray Manager - Build Guide

This guide explains how to package the Discord Tray Manager into a standalone executable and Windows installer.

## Prerequisites

### Required Software

1. **Python 3.6+** (with pip)
   - Download from: https://python.org
   - Make sure "Add Python to PATH" is checked during installation

2. **NSIS (Nullsoft Scriptable Install System)** (for installer creation)
   - Download from: https://nsis.sourceforge.io/
   - Add NSIS directory to your system PATH

### Required Python Packages

Run this command to install PyInstaller:
```bash
pip install pyinstaller
```

Optional (for better icon creation):
```bash
pip install pillow
```

## Building Process

### Option 1: Automated Build (Recommended)

Simply run the automated build script:
```bash
build_installer.bat
```

This will:
1. Create the application icon
2. Build the executable with PyInstaller
3. Create a portable version
4. Generate the Windows installer

### Option 2: Manual Build Steps

#### Step 1: Create Icon
```bash
python create_icon.py
```

#### Step 2: Build Executable
```bash
python build_exe.py
```

#### Step 3: Build Installer (requires NSIS)
```bash
makensis installer.nsi
```

## Output Files

After building, you'll have:

### `Discord_Tray_Manager_Setup.exe`
- **Windows Installer** 
- Installs to Program Files
- Adds to Windows startup automatically
- Creates Start Menu shortcuts
- Adds proper uninstaller

### `Discord_Tray_Manager_Portable/`
- **Portable Version**
- No installation required
- Run `DiscordTrayManager.exe` directly
- Perfect for USB drives or temporary use

## Installation Features

The installer provides:

✅ **Automatic Startup** - Runs when Windows starts
✅ **System Tray Icon** - Minimal interface, runs silently
✅ **Start Menu Integration** - Easy access and uninstall
✅ **No Taskbar Pinning** - Stays only in system tray
✅ **Proper Uninstaller** - Clean removal through Control Panel

## Configuration

The application uses `config.json` for settings:

```json
{
    "check_interval": 30,
    "log_level": "INFO",
    "discord_processes": ["Discord.exe", "DiscordPTB.exe", "DiscordCanary.exe"],
    "enable_auto_fix": true,
    "enable_tray_refresh": true,
    "enable_window_simulation": false,
    "startup_delay": 5
}
```

## Deployment Options

### For Personal Use
1. Run `build_installer.bat`
2. Install `Discord_Tray_Manager_Setup.exe`
3. Application starts automatically with Windows

### For Distribution
1. Build both installer and portable versions
2. Test on clean Windows 10 machine
3. Distribute installer for permanent installation
4. Distribute portable version for temporary use

## Troubleshooting Build Issues

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "NSIS not found"
1. Download NSIS from https://nsis.sourceforge.io/
2. Install NSIS
3. Add NSIS folder to Windows PATH
4. Restart command prompt

### "Python not found"
1. Install Python from https://python.org
2. Check "Add Python to PATH" during installation
3. Restart command prompt

### Build fails with import errors
Make sure all Python files are in the same directory:
- `discord_tray_manager.py`
- `discord_tray_manager_gui.py` 
- `tray_icon_helper.py`
- `config.json`

## Application Behavior

### After Installation
- Starts automatically with Windows
- Runs silently in system tray
- No console window visible
- Logs activity to `discord_tray_manager.log`

### System Tray Features
- Right-click for options menu
- Shows application status
- Quick exit option
- About dialog

### Startup Integration
- Added to Windows Registry: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Runs in background without user interaction
- Minimal resource usage

## File Structure

```
Discord Tray Manager/
├── Source Files/
│   ├── discord_tray_manager.py      # Original console version
│   ├── discord_tray_manager_gui.py  # GUI/tray version
│   ├── tray_icon_helper.py          # Windows API helper
│   └── config.json                  # Configuration
├── Build Files/
│   ├── build_exe.py                 # PyInstaller build script
│   ├── create_icon.py               # Icon generator
│   ├── installer.nsi                # NSIS installer script
│   ├── license.txt                  # License for installer
│   └── build_installer.bat          # Automated build script
└── Output/
    ├── Discord_Tray_Manager_Setup.exe    # Windows installer
    └── Discord_Tray_Manager_Portable/    # Portable version
```

## Security Notes

- Application requires no special privileges to run
- Installer requests admin rights only for:
  - Writing to Program Files
  - Adding startup registry entry
  - Creating Start Menu shortcuts
- No network connections made
- No data collection or telemetry
- Source code is fully transparent

## Distribution

The built application can be freely distributed as:
- Standalone installer
- Portable executable
- Source code for compilation

Users can install without concerns about malware as the application:
- Uses only standard Windows APIs
- Has transparent, auditable source code
- Performs only documented Discord tray management functions 