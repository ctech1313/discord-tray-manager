# Building Windows Executable

This project is developed on Linux but targets Windows users. Here's how to get Windows executables:

## 📦 Option 1: Download Pre-built (Easiest)

Check the [Releases](../../releases) page for pre-built Windows installers:
- `Discord_Tray_Manager_Setup.exe` - Windows installer
- `Discord_Tray_Manager_Portable.zip` - Portable version

## 🔧 Option 2: Build on Windows

If you want to build from source:

### Prerequisites
1. **Windows 10/11**
2. **Python 3.6+** from [python.org](https://python.org)
3. **NSIS** from [nsis.sourceforge.io](https://nsis.sourceforge.io/)

### Build Steps
```cmd
# Clone the repository
git clone https://github.com/your-username/discord-tray-manager.git
cd discord-tray-manager

# Install Python dependencies
pip install pyinstaller pillow

# Run the build
build_installer.bat
```

### Output
- `Discord_Tray_Manager_Setup.exe` - Windows installer
- `Discord_Tray_Manager_Portable/` - Portable version

## 🐧 Option 3: Cross-compile from Linux (Advanced)

If you're on Linux and want to build Windows executables:

### Using GitHub Actions (Recommended)
1. Fork this repository
2. Push your changes
3. GitHub Actions will automatically build Windows executables
4. Download from Actions artifacts

### Using Docker
```bash
# Build using Windows container
docker run --rm -v $(pwd):/app -w /app mcr.microsoft.com/windows:latest powershell -c "
  # Install build tools and build
"
```

## 📝 Current Development Status

- ✅ **Source code**: Ready and tested
- ✅ **Linux build**: Works for development/testing  
- ⏳ **Windows build**: Requires Windows environment
- ✅ **GitHub Actions**: Automated Windows builds available

## 🚀 For End Users

**Just download the pre-built installer** - it's the easiest option and guarantees compatibility with your Windows system.

## 🔧 For Developers

**Use GitHub Actions** - push your code and let the cloud build Windows executables automatically.

---

*Having trouble? Open an issue with your build environment details.* 