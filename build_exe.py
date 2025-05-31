#!/usr/bin/env python3
"""
Build script for Discord Tray Manager
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """Install PyInstaller if not present"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_pyinstaller_spec():
    """Create PyInstaller spec file for building Windows executable"""
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['discord_tray_manager_gui.py'],  # Use GUI version as main
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('README.md', '.'),
        ('tray_icon.ico', '.'),
    ],
    hiddenimports=[
        'pystray',
        'pystray._base',
        'pystray._win32', 
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'ctypes.wintypes',
        'winreg',
        'subprocess',
        'threading',
        'json',
        'logging',
        'time',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy'],  # Exclude unnecessary modules
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DiscordTrayManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI version
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='tray_icon.ico'
)
'''
    
    with open('discord_tray_manager.spec', 'w') as f:
        f.write(spec_content.strip())
    
    print("Created PyInstaller spec file")

def create_version_info():
    """Create version information file"""
    version_content = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Discord Tray Manager'),
        StringStruct(u'FileDescription', u'Discord System Tray Icon Manager'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'DiscordTrayManager'),
        StringStruct(u'LegalCopyright', u'Free Software'),
        StringStruct(u'OriginalFilename', u'DiscordTrayManager.exe'),
        StringStruct(u'ProductName', u'Discord Tray Manager'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w') as f:
        f.write(version_content.strip())
    
    print("Created version info file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Run PyInstaller
    cmd = [sys.executable, '-m', 'PyInstaller', 'discord_tray_manager.spec']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Executable built successfully!")
        if os.path.exists('dist/DiscordTrayManager.exe'):
            print("Executable location: dist/DiscordTrayManager.exe")
            return True
        else:
            print("Executable not found at expected location")
            return False
    else:
        print("Build failed!")
        print("Error:", result.stderr)
        return False

def create_build_directory():
    """Create a complete build directory with all files"""
    build_dir = "Discord_Tray_Manager_Portable"
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    os.makedirs(build_dir)
    
    # Copy executable
    if os.path.exists('dist/DiscordTrayManager.exe'):
        shutil.copy2('dist/DiscordTrayManager.exe', build_dir)
    
    # Copy configuration and documentation
    files_to_copy = ['config.json', 'README.md']
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, build_dir)
    
    print(f"Created portable build directory: {build_dir}")

def main():
    print("Discord Tray Manager - Build Script")
    print("=" * 40)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create necessary files
    create_pyinstaller_spec()
    create_version_info()
    
    # Build executable
    if build_executable():
        create_build_directory()
        print("\nBuild completed successfully!")
        print("You can find the portable version in: Discord_Tray_Manager_Portable/")
    else:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 