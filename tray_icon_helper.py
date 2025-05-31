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
            # Simple approach: just check if Discord is promoted in registry
            # If not promoted, we need to fix it
            return self.is_discord_promoted_in_registry()
            
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
                discord_found = False
                promoted_found = False
                
                while True:
                    try:
                        subkey_name = winreg.EnumKey(main_key, i)
                        
                        # Look for Discord with more specific matching
                        if ('discord' in subkey_name.lower() and 
                            ('exe' in subkey_name.lower() or 'app' in subkey_name.lower())):
                            
                            discord_found = True
                            subkey_path = f"{registry_path}\\{subkey_name}"
                            
                            try:
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path) as discord_key:
                                    is_promoted, _ = winreg.QueryValueEx(discord_key, "IsPromoted")
                                    if is_promoted == 1:
                                        logger.debug(f"Discord is promoted in registry: {subkey_name}")
                                        promoted_found = True
                                    else:
                                        logger.debug(f"Discord is not promoted in registry: {subkey_name} (value={is_promoted})")
                            except FileNotFoundError:
                                logger.debug(f"IsPromoted value not found for: {subkey_name}")
                        
                        i += 1
                    except OSError:
                        break
                
                if not discord_found:
                    logger.debug("No Discord entries found in registry")
                    return True  # If no entries, assume it's fine (might be first run)
                
                return promoted_found
                        
        except Exception as e:
            logger.debug(f"Error checking Discord registry promotion: {e}")
            return True  # If we can't check, assume it's fine
    
    def find_startallback_tray(self):
        """Find StartAllBack tray windows if present"""
        try:
            startallback_windows = []
            
            def enum_windows_proc(hwnd, lparam):
                # Get window class name
                class_name = ctypes.create_unicode_buffer(256)
                self.user32.GetClassNameW(hwnd, class_name, 256)
                
                # Get window title
                title_length = self.user32.GetWindowTextLengthW(hwnd)
                title = ""
                if title_length > 0:
                    title_buffer = ctypes.create_unicode_buffer(title_length + 1)
                    self.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
                    title = title_buffer.value
                
                # Check for StartAllBack tray windows
                class_lower = class_name.value.lower()
                if ('startallback' in class_lower or 
                    'shell_traywnd' in class_lower or
                    'traynotifywnd' in class_lower):
                    startallback_windows.append({
                        'hwnd': hwnd,
                        'class': class_name.value,
                        'title': title
                    })
                
                return True
            
            # Define the callback type
            EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            
            # Enumerate all windows
            self.user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)
            
            return startallback_windows
            
        except Exception as e:
            logger.debug(f"Error finding StartAllBack windows: {e}")
            return []

    def promote_discord_to_main_tray(self):
        """Promote Discord icon to main system tray area using multiple methods"""
        try:
            success = False
            
            # Method 1: Check for StartAllBack and use alternative approach
            startallback_windows = self.find_startallback_tray()
            if startallback_windows:
                logger.info("StartAllBack detected, using alternative tray approach")
                success = self.promote_discord_startallback_compatible()
            
            # Method 2: Standard Windows Shell API
            if not success:
                success = self.promote_discord_shell_api()
            
            # Method 3: Registry approach as fallback
            if not success:
                success = self.registry_promote_discord()
                
            return success
            
        except Exception as e:
            logger.error(f"Error promoting Discord to main tray: {e}")
            return False
    
    def promote_discord_startallback_compatible(self):
        """StartAllBack-compatible Discord promotion"""
        try:
            # For StartAllBack, we need to use a different approach
            # Try to force Discord to recreate its tray icon
            
            discord_windows = self.find_discord_windows()
            if not discord_windows:
                logger.debug("No Discord windows found")
                return False
            
            success = False
            
            # Method 1: Send Explorer restart simulation to Discord
            for window in discord_windows:
                hwnd = window['hwnd']
                if 'discord' in window['title'].lower():
                    # Send messages that simulate explorer restart
                    WM_SETTINGCHANGE = 0x001A
                    self.user32.SendMessageW(hwnd, WM_SETTINGCHANGE, 0, 0)
                    
                    # Also try the taskbar created message
                    WM_TASKBARCREATED = self.user32.RegisterWindowMessageW("TaskbarCreated")
                    self.user32.SendMessageW(hwnd, WM_TASKBARCREATED, 0, 0)
                    
                    logger.debug(f"Sent StartAllBack-compatible messages to Discord: {window['title']}")
                    success = True
            
            # Method 2: Try to refresh all tray icons via broadcast
            if success:
                # Broadcast to all windows that taskbar was recreated
                HWND_BROADCAST = 0xFFFF
                WM_TASKBARCREATED = self.user32.RegisterWindowMessageW("TaskbarCreated")
                self.user32.SendMessageW(HWND_BROADCAST, WM_TASKBARCREATED, 0, 0)
                logger.info("Broadcasted taskbar recreation message for StartAllBack")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in StartAllBack-compatible promotion: {e}")
            return False
    
    def promote_discord_shell_api(self):
        """Standard Windows Shell API approach"""
        try:
            # Find Discord windows first
            discord_windows = self.find_discord_windows()
            if not discord_windows:
                logger.debug("No Discord windows found for promotion")
                return False
            
            success = False
            
            # Send WM_TASKBARCREATED to Discord to refresh its tray icon
            WM_TASKBARCREATED = self.user32.RegisterWindowMessageW("TaskbarCreated")
            
            for window in discord_windows:
                hwnd = window['hwnd']
                if 'discord' in window['title'].lower():
                    # Send taskbar created message to force tray icon refresh
                    self.user32.SendMessageW(hwnd, WM_TASKBARCREATED, 0, 0)
                    logger.debug(f"Sent TaskbarCreated message to Discord window: {window['title']}")
                    success = True
                    
            return success
            
        except Exception as e:
            logger.error(f"Error in Shell API promotion: {e}")
            return False
    
    def registry_promote_discord(self):
        """Fallback registry method to promote Discord"""
        try:
            import winreg
            
            # Registry path for notification icon settings
            registry_path = r"Control Panel\NotifyIconSettings"
            
            promoted_count = 0
            
            # Open the main registry key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as main_key:
                # Enumerate all subkeys (each represents a tray icon)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(main_key, i)
                        
                        # Check if this subkey is related to Discord (more specific matching)
                        if ('discord' in subkey_name.lower() and 
                            ('exe' in subkey_name.lower() or 'app' in subkey_name.lower())):
                            
                            subkey_path = f"{registry_path}\\{subkey_name}"
                            
                            try:
                                # Open the Discord-related subkey
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as discord_key:
                                    # Check current promotion status
                                    try:
                                        current_value, _ = winreg.QueryValueEx(discord_key, "IsPromoted")
                                        if current_value == 1:
                                            logger.debug(f"Discord already promoted: {subkey_name}")
                                            continue
                                    except FileNotFoundError:
                                        # IsPromoted doesn't exist, will create it
                                        pass
                                    
                                    # Set IsPromoted to 1 to show in main tray
                                    winreg.SetValueEx(discord_key, "IsPromoted", 0, winreg.REG_DWORD, 1)
                                    logger.info(f"Promoted Discord icon to main tray: {subkey_name}")
                                    promoted_count += 1
                                    
                            except (FileNotFoundError, PermissionError) as e:
                                logger.debug(f"Could not access Discord registry key {subkey_name}: {e}")
                        
                        i += 1
                    except OSError:
                        # No more subkeys
                        break
                        
            if promoted_count > 0:
                logger.info(f"Successfully promoted {promoted_count} Discord icon(s) via registry")
                return True
            else:
                logger.debug("No Discord icons found to promote in registry")
                return False
            
        except Exception as e:
            logger.error(f"Error promoting Discord via registry: {e}")
            return False
    
    def refresh_notification_area(self):
        """Force refresh of the notification area and promote Discord"""
        try:
            # Promote Discord to main tray via the improved method
            promoted = self.promote_discord_to_main_tray()
            
            if promoted:
                # Check if StartAllBack is running for compatible refresh
                startallback_windows = self.find_startallback_tray()
                
                if startallback_windows:
                    # StartAllBack-specific refresh
                    logger.info("Refreshing StartAllBack tray area")
                    for sb_window in startallback_windows:
                        hwnd = sb_window['hwnd']
                        # Refresh StartAllBack tray windows
                        self.user32.InvalidateRect(hwnd, None, True)
                        self.user32.UpdateWindow(hwnd)
                        # Send refresh message
                        WM_COMMAND = 0x0111
                        self.user32.SendMessageW(hwnd, WM_COMMAND, 419, 0)
                else:
                    # Standard Windows tray refresh
                    tray_wnd = self.user32.FindWindowW("Shell_TrayWnd", None)
                    if tray_wnd:
                        notify_wnd = self.user32.FindWindowExW(tray_wnd, None, "TrayNotifyWnd", None)
                        if notify_wnd:
                            self.user32.InvalidateRect(notify_wnd, None, True)
                            self.user32.UpdateWindow(notify_wnd)
                        
                            # Also try overflow area
                            overflow_wnd = self.user32.FindWindowExW(None, None, "NotifyIconOverflowWindow", None)
                            if overflow_wnd:
                                self.user32.InvalidateRect(overflow_wnd, None, True)
                                self.user32.UpdateWindow(overflow_wnd)
                
                logger.info("Promoted Discord and refreshed tray area")
                return True
                
            return promoted
            
        except Exception as e:
            logger.error(f"Error refreshing notification area: {e}")
            return False
    
    def simulate_discord_tray_action(self):
        """Simulate actions that might make Discord appear in tray - DISABLED"""
        # This method is disabled as it causes unwanted window minimization
        logger.debug("Window simulation is disabled to prevent unwanted minimization")
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
        # Hide console window for subprocess
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        result = subprocess.run(
            ['tasklist', '/FO', 'CSV'], 
            capture_output=True, 
            text=True, 
            check=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
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
        # Hide console window for subprocess
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        result = subprocess.run(
            ['tasklist', '/FO', 'CSV'], 
            capture_output=True, 
            text=True, 
            check=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        discord_processes = ['Discord.exe', 'DiscordPTB.exe', 'DiscordCanary.exe']
        for process_name in discord_processes:
            if process_name.lower() in result.stdout.lower():
                processes.append(process_name)
        
        return processes
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting Discord processes: {e}")
        return [] 