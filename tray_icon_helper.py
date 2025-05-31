"""
Tray Icon Helper - Windows API functions for managing system tray icons
"""

import ctypes
from ctypes import wintypes, Structure, POINTER, byref
import struct
import logging
import winreg

logger = logging.getLogger(__name__)

# Windows API constants
NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002
NIM_SETFOCUS = 0x00000003
NIM_SETVERSION = 0x00000004

NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NIF_STATE = 0x00000008
NIF_INFO = 0x00000010
NIF_GUID = 0x00000020

NIS_HIDDEN = 0x00000001
NIS_SHAREDICON = 0x00000002

# Windows structures
class NOTIFYICONDATA(Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
    ]

class TrayIconManager:
    def __init__(self):
        self.shell32 = ctypes.windll.shell32
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
    def find_discord_windows(self):
        """Find all Discord application windows"""
        discord_windows = []
        
        def enum_windows_proc(hwnd, lparam):
            # Get window class name
            class_name = ctypes.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd, class_name, 256)
            
            # Get window title
            title_length = self.user32.GetWindowTextLengthW(hwnd)
            if title_length > 0:
                title = ctypes.create_unicode_buffer(title_length + 1)
                self.user32.GetWindowTextW(hwnd, title, title_length + 1)
                
                # Check if this is a Discord window
                if ('discord' in title.value.lower() or 
                    'discord' in class_name.value.lower()):
                    discord_windows.append({
                        'hwnd': hwnd,
                        'title': title.value,
                        'class': class_name.value
                    })
            
            return True
        
        # Define the callback type
        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        
        # Enumerate all windows
        self.user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)
        
        return discord_windows
    
    def get_notification_area_icons(self):
        """Get information about current notification area icons"""
        try:
            # Find the notification area
            tray_wnd = self.user32.FindWindowW("Shell_TrayWnd", None)
            if not tray_wnd:
                logger.error("Could not find system tray window")
                return []
            
            notify_wnd = self.user32.FindWindowExW(tray_wnd, None, "TrayNotifyWnd", None)
            if not notify_wnd:
                logger.error("Could not find notification area window")
                return []
            
            # This is a complex operation that requires reading the notification area's internal data
            # For now, we'll use a simpler approach
            logger.debug("Found notification area window")
            return []
            
        except Exception as e:
            logger.error(f"Error getting notification area icons: {e}")
            return []
    
    def is_discord_icon_visible(self):
        """Check if Discord icon is currently visible in the system tray"""
        try:
            # Find Discord windows
            discord_windows = self.find_discord_windows()
            
            if not discord_windows:
                logger.debug("No Discord windows found")
                return False
            
            # Check if Discord is promoted in registry (Windows 11 specific)
            if not self.is_discord_promoted_in_registry():
                logger.info("Discord is not promoted to main tray area")
                return False
            
            # Check if any Discord window is in the tray (not visible but exists)
            has_main_window = False
            has_hidden_window = False
            
            for window in discord_windows:
                hwnd = window['hwnd']
                
                # Check if this is the main Discord window (not a popup/dialog)
                if 'discord' in window['title'].lower() and len(window['title']) > 10:
                    has_main_window = True
                    
                    # Check if window is minimized/hidden (likely in tray)
                    if not self.user32.IsWindowVisible(hwnd):
                        has_hidden_window = True
                        logger.debug(f"Discord window {window['title']} is hidden (likely in tray)")
                    else:
                        # Window is visible, so Discord icon might not be in tray
                        logger.debug(f"Discord window {window['title']} is visible")
            
            # If we have a main Discord window and it's hidden, assume icon is in tray
            if has_main_window and has_hidden_window:
                return True
            
            # If Discord is running but no hidden windows, icon might be missing from tray
            return False
            
        except Exception as e:
            logger.error(f"Error checking Discord icon visibility: {e}")
            return False
    
    def is_discord_promoted_in_registry(self):
        """Check if Discord is promoted to main tray in Windows registry"""
        try:
            import winreg
            
            registry_path = r"Control Panel\NotifyIconSettings"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as main_key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(main_key, i)
                        
                        if 'discord' in subkey_name.lower():
                            subkey_path = f"{registry_path}\\{subkey_name}"
                            
                            try:
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path) as discord_key:
                                    is_promoted, _ = winreg.QueryValueEx(discord_key, "IsPromoted")
                                    if is_promoted == 1:
                                        logger.debug(f"Discord is promoted in registry: {subkey_name}")
                                        return True
                                    else:
                                        logger.debug(f"Discord is not promoted in registry: {subkey_name}")
                                        return False
                            except FileNotFoundError:
                                logger.debug(f"IsPromoted value not found for: {subkey_name}")
                        
                        i += 1
                    except OSError:
                        break
                        
            return False
            
        except Exception as e:
            logger.debug(f"Error checking Discord registry promotion: {e}")
            return False
    
    def promote_discord_to_main_tray(self):
        """Promote Discord icon to main system tray area (Windows 11 fix)"""
        try:
            # Registry path for notification icon settings
            registry_path = r"Control Panel\NotifyIconSettings"
            
            # Open the main registry key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as main_key:
                # Enumerate all subkeys (each represents a tray icon)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(main_key, i)
                        
                        # Check if this subkey is related to Discord
                        if 'discord' in subkey_name.lower():
                            subkey_path = f"{registry_path}\\{subkey_name}"
                            
                            try:
                                # Open the Discord-related subkey
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path, 0, winreg.KEY_SET_VALUE) as discord_key:
                                    # Set IsPromoted to 1 to show in main tray
                                    winreg.SetValueEx(discord_key, "IsPromoted", 0, winreg.REG_DWORD, 1)
                                    logger.info(f"Promoted Discord icon to main tray: {subkey_name}")
                                    
                            except FileNotFoundError:
                                logger.debug(f"Could not open Discord registry key: {subkey_name}")
                            except PermissionError:
                                logger.warning(f"Permission denied accessing registry key: {subkey_name}")
                        
                        i += 1
                    except OSError:
                        # No more subkeys
                        break
                        
            return True
            
        except Exception as e:
            logger.error(f"Error promoting Discord to main tray: {e}")
            return False
    
    def refresh_notification_area(self):
        """Force refresh of the notification area and promote Discord"""
        try:
            # First, promote Discord to main tray
            self.promote_discord_to_main_tray()
            
            # Find the notification area
            tray_wnd = self.user32.FindWindowW("Shell_TrayWnd", None)
            if tray_wnd:
                notify_wnd = self.user32.FindWindowExW(tray_wnd, None, "TrayNotifyWnd", None)
                if notify_wnd:
                    # Force a redraw
                    self.user32.InvalidateRect(notify_wnd, None, True)
                    self.user32.UpdateWindow(notify_wnd)
                    
                    # Also refresh the overflow area
                    overflow_wnd = self.user32.FindWindowExW(None, None, "NotifyIconOverflowWindow", None)
                    if overflow_wnd:
                        self.user32.InvalidateRect(overflow_wnd, None, True)
                        self.user32.UpdateWindow(overflow_wnd)
                    
                    # Send a message to refresh the entire tray
                    WM_COMMAND = 0x0111
                    self.user32.SendMessageW(tray_wnd, WM_COMMAND, 419, 0)  # Refresh tray
                    
                    logger.debug("Refreshed notification area and promoted Discord")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error refreshing notification area: {e}")
            return False
    
    def simulate_discord_tray_action(self):
        """Simulate actions that might make Discord appear in tray"""
        try:
            discord_windows = self.find_discord_windows()
            
            for window in discord_windows:
                hwnd = window['hwnd']
                
                # Try to minimize and restore the window
                # This sometimes triggers tray icon appearance
                if self.user32.IsWindowVisible(hwnd):
                    logger.debug(f"Minimizing Discord window: {window['title']}")
                    self.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
                    
                    # Wait a moment then restore
                    import time
                    time.sleep(0.5)
                    
                    self.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    
            return True
            
        except Exception as e:
            logger.error(f"Error simulating Discord tray action: {e}")
            return False 

# Standalone function wrappers for backward compatibility
def refresh_notification_area():
    """Standalone function to refresh notification area"""
    manager = TrayIconManager()
    return manager.refresh_notification_area()

def is_discord_running():
    """Check if Discord is running by looking for Discord processes"""
    import subprocess
    try:
        result = subprocess.run(['tasklist', '/FO', 'CSV'], 
                              capture_output=True, text=True, check=True)
        
        discord_processes = ['Discord.exe', 'DiscordPTB.exe', 'DiscordCanary.exe']
        for process_name in discord_processes:
            if process_name.lower() in result.stdout.lower():
                logger.debug(f"Found running Discord process: {process_name}")
                return True
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking running processes: {e}")
        return False

def get_discord_processes():
    """Get list of running Discord processes"""
    import subprocess
    processes = []
    try:
        result = subprocess.run(['tasklist', '/FO', 'CSV'], 
                              capture_output=True, text=True, check=True)
        
        discord_processes = ['Discord.exe', 'DiscordPTB.exe', 'DiscordCanary.exe']
        for process_name in discord_processes:
            if process_name.lower() in result.stdout.lower():
                processes.append(process_name)
        
        return processes
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting Discord processes: {e}")
        return [] 