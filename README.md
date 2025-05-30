# Discord Tray Manager

A lightweight, non-invasive utility for Windows 10 that ensures Discord's icon stays visible in your system tray. This addresses the common issue where Discord's tray icon disappears or becomes unpinned, especially during voice calls when the icon changes.

## 🚀 Quick Start

### For End Users (Recommended)

1. **Download** the latest installer: `Discord_Tray_Manager_Setup.exe`
2. **Run the installer** (requires administrator privileges)
3. **Done!** The application automatically:
   - Starts with Windows
   - Runs silently in your system tray
   - Monitors and fixes Discord tray icon issues

### For Developers

1. Clone this repository
2. Run `build_installer.bat` to create your own installer
3. See [Build Guide](build_guide.md) for detailed instructions

## ✨ Features

- **🔧 Automatic Fix** - Detects and fixes Discord tray icon visibility issues
- **🚀 Auto-Startup** - Starts automatically with Windows
- **🔕 Silent Operation** - Runs quietly in system tray, no console windows
- **⚡ Lightweight** - Minimal resource usage (~5MB RAM)
- **🛡️ Non-invasive** - Only acts when Discord tray icon goes missing
- **📝 Comprehensive Logging** - Full activity logs for troubleshooting
- **🎯 Multi-version Support** - Works with Discord, Discord PTB, and Discord Canary
- **🔧 Configurable** - Easy-to-modify JSON configuration
- **🗑️ Clean Uninstall** - Removes all traces when uninstalled

## 🎯 How It Works

The application runs silently in your system tray and:

1. **Monitors** Discord processes every 30 seconds (configurable)
2. **Detects** when Discord is running but the tray icon isn't visible
3. **Fixes** the issue by refreshing the notification area
4. **Logs** all activities for transparency

## 📦 Installation Options

### Option 1: Windows Installer (Recommended)
- **File**: `Discord_Tray_Manager_Setup.exe`
- **Features**: Auto-startup, Start Menu integration, proper uninstaller
- **Requirements**: Administrator privileges for installation

### Option 2: Portable Version
- **File**: `DiscordTrayManager.exe` (in portable folder)
- **Features**: No installation required, perfect for USB drives
- **Requirements**: Manual startup configuration

## 🛠️ Installation Process

The installer will:

✅ **Install** the application to `Program Files\Discord Tray Manager`  
✅ **Add** to Windows startup (runs automatically)  
✅ **Create** Start Menu shortcuts for easy access  
✅ **Register** uninstaller in Control Panel  
✅ **Configure** system tray operation  

**Note**: The application will NOT be pinned to your taskbar - it only appears in the system tray (notification area).

## ⚙️ Configuration

The application uses `config.json` for customization:

```json
{
    "check_interval": 30,              // How often to check (seconds)
    "log_level": "INFO",              // DEBUG, INFO, WARNING, ERROR
    "discord_processes": [            // Discord versions to monitor
        "Discord.exe",
        "DiscordPTB.exe", 
        "DiscordCanary.exe"
    ],
    "enable_auto_fix": true,          // Automatically fix issues
    "enable_tray_refresh": true,      // Enable notification area refresh
    "enable_window_simulation": false, // More invasive fixes (not recommended)
    "startup_delay": 5                // Wait time before starting monitoring
}
```

### Configuration Location
- **Installed version**: `%PROGRAMFILES%\Discord Tray Manager\config.json`
- **Portable version**: Same folder as the executable

## 📊 System Tray Interface

After installation, you'll see a small Discord Tray Manager icon in your system tray:

- **Left-click**: Show status information
- **Right-click**: Access options menu
  - View current status
  - Open configuration
  - View logs
  - About information
  - Exit application

## 📋 Logs

The application creates detailed logs at:
- **Installed**: `%PROGRAMFILES%\Discord Tray Manager\discord_tray_manager.log`
- **Portable**: Same folder as executable

Logs include:
- Discord process detection
- Tray icon status checks
- Fix attempts and results
- Any errors or warnings

## 🔧 Troubleshooting

### Discord icon still not appearing?
1. **Check logs** for specific error messages
2. **Try enabling** `enable_window_simulation` in config.json (warning: more invasive)
3. **Verify Discord settings**: Settings → Windows Settings → Open Discord in the system tray
4. **Restart** the Discord Tray Manager from Start Menu

### High CPU or memory usage?
- **Increase** `check_interval` to check less frequently (e.g., 60 seconds)
- **Set** `log_level` to "WARNING" to reduce logging overhead

### Application not starting automatically?
1. **Check** Windows startup settings: Task Manager → Startup tab
2. **Verify** registry entry exists: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
3. **Reinstall** the application if startup entry is missing

### Can't find the system tray icon?
1. **Check** if it's in the hidden icons area (click the up arrow in system tray)
2. **Configure Windows** to always show the icon: Settings → Personalization → Taskbar → Select which icons appear on the taskbar

## 🔧 Building from Source

For developers who want to build their own version:

### Prerequisites
- Python 3.6+ with pip
- NSIS (Nullsoft Scriptable Install System)

### Quick Build
```bash
# Install dependencies
pip install pyinstaller pillow

# Run automated build
build_installer.bat
```

### Manual Build
```bash
# Create icon
python create_icon.py

# Build executable
python build_exe.py

# Build installer (requires NSIS)
makensis installer.nsi
```

See [Build Guide](build_guide.md) for detailed instructions.

## 📁 File Structure

```
Discord Tray Manager/
├── 📁 Source Files/
│   ├── discord_tray_manager.py          # Original console version
│   ├── discord_tray_manager_gui.py      # System tray version
│   ├── tray_icon_helper.py              # Windows API helper
│   └── config.json                      # Configuration
├── 📁 Build System/
│   ├── build_exe.py                     # PyInstaller build script
│   ├── create_icon.py                   # Icon generator
│   ├── installer.nsi                    # NSIS installer script
│   ├── license.txt                      # License file
│   ├── build_installer.bat              # Automated build script
│   └── build_guide.md                   # Detailed build instructions
└── 📁 Output/
    ├── Discord_Tray_Manager_Setup.exe   # Windows installer
    └── Discord_Tray_Manager_Portable/   # Portable version
```

## 🛡️ Security & Privacy

- **No data collection** - No telemetry or user data transmitted
- **No network access** - Application works entirely offline
- **Open source** - Full source code available for audit
- **Safe operations** - Only uses standard Windows APIs
- **Minimal permissions** - No special privileges required to run

The installer requests administrator privileges only for:
- Writing to Program Files directory
- Adding Windows startup registry entry
- Creating Start Menu shortcuts

## 🔄 Uninstalling

### Through Windows Settings
1. Settings → Apps → Apps & features
2. Search for "Discord Tray Manager"
3. Click "Uninstall"

### Through Control Panel
1. Control Panel → Programs → Programs and Features
2. Find "Discord Tray Manager"
3. Click "Uninstall"

### Through Start Menu
1. Start Menu → Discord Tray Manager → Uninstall

The uninstaller will:
- Stop the running application
- Remove all installed files
- Remove Windows startup entry
- Remove Start Menu shortcuts
- Clean up registry entries

## 📄 License

This software is provided "as is" under a permissive license. See [license.txt](license.txt) for full terms.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs or issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📞 Support

- **Issues**: Create a GitHub issue with detailed information
- **Logs**: Include relevant log entries when reporting problems
- **System Info**: Mention your Windows version and Discord version

---

**Made with ❤️ for the Discord community**

*Keep your Discord always accessible in the system tray!* 