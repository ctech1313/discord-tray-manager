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
        
        logger.debug("Starting Discord window enumeration...")
        
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
                    
                    window_info = {
                        'hwnd': hwnd,
                        'title': title.value,
                        'class': class_name.value
                    }
                    discord_windows.append(window_info)
                    logger.debug(f"Found Discord window: hwnd={hwnd}, title='{title.value}', class='{class_name.value}'")
            
            return True
        
        # Define the callback type
        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        
        # Enumerate all windows
        try:
            self.user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)
            logger.debug(f"Discord window enumeration complete. Found {len(discord_windows)} Discord windows")
        except Exception as e:
            logger.error(f"Error during window enumeration: {e}")
        
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
            
            logger.debug("Checking Discord promotion status in Windows registry...")
            
            registry_path = r"Control Panel\NotifyIconSettings"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as main_key:
                i = 0
                discord_found = False
                promoted_found = False
                
                logger.debug(f"Enumerating registry keys in {registry_path}...")
                
                while True:
                    try:
                        subkey_name = winreg.EnumKey(main_key, i)
                        logger.debug(f"Registry subkey [{i}]: {subkey_name}")
                        
                        # Look for Discord with more specific matching
                        if ('discord' in subkey_name.lower() and 
                            ('exe' in subkey_name.lower() or 'app' in subkey_name.lower())):
                            
                            discord_found = True
                            subkey_path = f"{registry_path}\\{subkey_name}"
                            logger.info(f"Found Discord registry entry: {subkey_name}")
                            
                            try:
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path) as discord_key:
                                    try:
                                        is_promoted, reg_type = winreg.QueryValueEx(discord_key, "IsPromoted")
                                        logger.debug(f"IsPromoted value for {subkey_name}: {is_promoted} (type: {reg_type})")
                                        if is_promoted == 1:
                                            logger.info(f"Discord is promoted in registry: {subkey_name}")
                                            promoted_found = True
                                        else:
                                            logger.warning(f"Discord is not promoted in registry: {subkey_name} (value={is_promoted})")
                                    except FileNotFoundError:
                                        logger.warning(f"IsPromoted value not found for: {subkey_name}")
                                        # List all values in this key for debugging
                                        try:
                                            value_count = winreg.QueryInfoKey(discord_key)[1]
                                            logger.debug(f"Registry key {subkey_name} has {value_count} values:")
                                            for j in range(value_count):
                                                value_name, value_data, value_type = winreg.EnumValue(discord_key, j)
                                                logger.debug(f"  {value_name} = {value_data} (type: {value_type})")
                                        except Exception as enum_e:
                                            logger.debug(f"Could not enumerate values in {subkey_name}: {enum_e}")
                            except Exception as key_e:
                                logger.error(f"Could not open Discord registry key {subkey_name}: {key_e}")
                        else:
                            logger.debug(f"Skipping non-Discord key: {subkey_name}")
                        
                        i += 1
                    except OSError:
                        logger.debug(f"Registry enumeration complete. Checked {i} keys total.")
                        break
                
                if not discord_found:
                    logger.warning("No Discord entries found in registry")
                    return True  # If no entries, assume it's fine (might be first run)
                
                logger.info(f"Discord registry check result: found={discord_found}, promoted={promoted_found}")
                return promoted_found
                        
        except Exception as e:
            logger.error(f"Error checking Discord registry promotion: {e}")
            return True  # If we can't check, assume it's fine
    
    def find_startallback_tray(self):
        """Find StartAllBack tray windows if present"""
        try:
            startallback_windows = []
            
            logger.debug("Scanning for StartAllBack tray windows...")
            
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
                    
                    window_info = {
                        'hwnd': hwnd,
                        'class': class_name.value,
                        'title': title
                    }
                    startallback_windows.append(window_info)
                    logger.debug(f"Found potential StartAllBack window: hwnd={hwnd}, class='{class_name.value}', title='{title}'")
                
                return True
            
            # Define the callback type
            EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            
            # Enumerate all windows
            self.user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)
            
            logger.info(f"StartAllBack scan complete. Found {len(startallback_windows)} potential StartAllBack windows")
            for window in startallback_windows:
                logger.info(f"StartAllBack window: {window['class']} - {window['title']}")
            
            return startallback_windows
            
        except Exception as e:
            logger.error(f"Error finding StartAllBack windows: {e}")
            return []

    def promote_discord_to_main_tray(self):
        """Promote Discord icon to main system tray area using multiple methods"""
        try:
            logger.info("======= STARTING DISCORD TRAY PROMOTION PROCESS =======")
            success = False
            
            # Method 1: Check for StartAllBack and use alternative approach
            logger.info("Step 1: Checking for StartAllBack...")
            startallback_windows = self.find_startallback_tray()
            if startallback_windows:
                logger.info(f"StartAllBack detected with {len(startallback_windows)} windows, using alternative tray approach")
                success = self.promote_discord_startallback_compatible()
                logger.info(f"StartAllBack promotion result: {success}")
            else:
                logger.info("No StartAllBack windows detected, will use standard Windows API")
            
            # Method 2: Standard Windows Shell API
            if not success:
                logger.info("Step 2: Trying standard Windows Shell API approach...")
                success = self.promote_discord_shell_api()
                logger.info(f"Shell API promotion result: {success}")
            
            # Method 3: Registry approach as fallback
            if not success:
                logger.info("Step 3: Trying registry-based approach as fallback...")
                success = self.registry_promote_discord()
                logger.info(f"Registry promotion result: {success}")
                
            logger.info(f"======= DISCORD TRAY PROMOTION PROCESS COMPLETE: {success} =======")
            return success
            
        except Exception as e:
            logger.error(f"Error promoting Discord to main tray: {e}")
            return False
    
    def promote_discord_startallback_compatible(self):
        """StartAllBack-compatible Discord promotion"""
        try:
            logger.info("=== Starting StartAllBack-compatible Discord promotion ===")
            
            # For StartAllBack, we need to use a different approach
            # Try to force Discord to recreate its tray icon
            
            discord_windows = self.find_discord_windows()
            if not discord_windows:
                logger.warning("No Discord windows found for StartAllBack promotion")
                return False
            
            success = False
            
            logger.info(f"Found {len(discord_windows)} Discord windows for StartAllBack promotion")
            
            # Method 1: Send Explorer restart simulation to Discord
            for window in discord_windows:
                hwnd = window['hwnd']
                if 'discord' in window['title'].lower():
                    logger.debug(f"Sending StartAllBack messages to Discord window: {window['title']} (hwnd={hwnd})")
                    
                    # Send messages that simulate explorer restart
                    WM_SETTINGCHANGE = 0x001A
                    result1 = self.user32.SendMessageW(hwnd, WM_SETTINGCHANGE, 0, 0)
                    logger.debug(f"WM_SETTINGCHANGE result: {result1}")
                    
                    # Also try the taskbar created message
                    WM_TASKBARCREATED = self.user32.RegisterWindowMessageW("TaskbarCreated")
                    logger.debug(f"Registered WM_TASKBARCREATED message ID: {WM_TASKBARCREATED}")
                    result2 = self.user32.SendMessageW(hwnd, WM_TASKBARCREATED, 0, 0)
                    logger.debug(f"WM_TASKBARCREATED result: {result2}")
                    
                    logger.info(f"Sent StartAllBack-compatible messages to Discord: {window['title']}")
                    success = True
                else:
                    logger.debug(f"Skipping non-main Discord window: {window['title']}")
            
            # Method 2: Try to refresh all tray icons via broadcast
            if success:
                logger.debug("Broadcasting taskbar recreation message system-wide...")
                # Broadcast to all windows that taskbar was recreated
                HWND_BROADCAST = 0xFFFF
                WM_TASKBARCREATED = self.user32.RegisterWindowMessageW("TaskbarCreated")
                broadcast_result = self.user32.SendMessageW(HWND_BROADCAST, WM_TASKBARCREATED, 0, 0)
                logger.debug(f"Broadcast WM_TASKBARCREATED result: {broadcast_result}")
                logger.info("Broadcasted taskbar recreation message for StartAllBack")
            
            logger.info(f"StartAllBack promotion result: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Error in StartAllBack-compatible promotion: {e}")
            return False
    
    def promote_discord_shell_api(self):
        """Standard Windows Shell API approach"""
        try:
            logger.info("=== Starting standard Windows Shell API promotion ===")
            
            # Find Discord windows first
            discord_windows = self.find_discord_windows()
            if not discord_windows:
                logger.warning("No Discord windows found for Shell API promotion")
                return False
            
            success = False
            
            logger.info(f"Found {len(discord_windows)} Discord windows for Shell API promotion")
            
            # Send WM_TASKBARCREATED to Discord to refresh its tray icon
            WM_TASKBARCREATED = self.user32.RegisterWindowMessageW("TaskbarCreated")
            logger.debug(f"Registered WM_TASKBARCREATED message ID: {WM_TASKBARCREATED}")
            
            for window in discord_windows:
                hwnd = window['hwnd']
                if 'discord' in window['title'].lower():
                    logger.debug(f"Sending TaskbarCreated to Discord window: {window['title']} (hwnd={hwnd})")
                    
                    # Send taskbar created message to force tray icon refresh
                    result = self.user32.SendMessageW(hwnd, WM_TASKBARCREATED, 0, 0)
                    logger.debug(f"WM_TASKBARCREATED result: {result}")
                    logger.info(f"Sent TaskbarCreated message to Discord window: {window['title']}")
                    success = True
                else:
                    logger.debug(f"Skipping non-main Discord window: {window['title']}")
                    
            logger.info(f"Shell API promotion result: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Error in Shell API promotion: {e}")
            return False
    
    def registry_promote_discord(self):
        """Fallback registry method to promote Discord"""
        try:
            logger.info("=== Starting registry-based Discord promotion ===")
            
            import winreg
            
            # Registry path for notification icon settings
            registry_path = r"Control Panel\NotifyIconSettings"
            
            promoted_count = 0
            
            logger.debug(f"Opening registry path: HKEY_CURRENT_USER\\{registry_path}")
            
            # Open the main registry key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as main_key:
                # Enumerate all subkeys (each represents a tray icon)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(main_key, i)
                        logger.debug(f"Checking registry key [{i}]: {subkey_name}")
                        
                        # Check if this subkey is related to Discord (more specific matching)
                        if ('discord' in subkey_name.lower() and 
                            ('exe' in subkey_name.lower() or 'app' in subkey_name.lower())):
                            
                            subkey_path = f"{registry_path}\\{subkey_name}"
                            logger.info(f"Found Discord registry entry for promotion: {subkey_name}")
                            
                            try:
                                # Open the Discord-related subkey
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as discord_key:
                                    # Check current promotion status
                                    try:
                                        current_value, reg_type = winreg.QueryValueEx(discord_key, "IsPromoted")
                                        logger.debug(f"Current IsPromoted value: {current_value} (type: {reg_type})")
                                        if current_value == 1:
                                            logger.info(f"Discord already promoted: {subkey_name}")
                                            continue
                                    except FileNotFoundError:
                                        logger.debug(f"IsPromoted doesn't exist for {subkey_name}, will create it")
                                    
                                    # Set IsPromoted to 1 to show in main tray
                                    logger.debug(f"Setting IsPromoted=1 for {subkey_name}")
                                    winreg.SetValueEx(discord_key, "IsPromoted", 0, winreg.REG_DWORD, 1)
                                    logger.info(f"Successfully promoted Discord icon to main tray: {subkey_name}")
                                    promoted_count += 1
                                    
                            except (FileNotFoundError, PermissionError) as e:
                                logger.error(f"Could not access Discord registry key {subkey_name}: {e}")
                        else:
                            logger.debug(f"Skipping non-Discord registry key: {subkey_name}")
                        
                        i += 1
                    except OSError:
                        logger.debug(f"Registry enumeration complete. Processed {i} keys total.")
                        break
                        
            if promoted_count > 0:
                logger.info(f"Successfully promoted {promoted_count} Discord icon(s) via registry")
                return True
            else:
                logger.warning("No Discord icons found to promote in registry")
                return False
            
        except Exception as e:
            logger.error(f"Error promoting Discord via registry: {e}")
            return False
    
    def refresh_notification_area(self):
        """Force refresh of the notification area and promote Discord"""
        try:
            logger.info("======= STARTING NOTIFICATION AREA REFRESH =======")
            
            # Promote Discord to main tray via the improved method
            promoted = self.promote_discord_to_main_tray()
            
            if promoted:
                logger.info("Discord promotion successful, now refreshing tray areas...")
                
                # Check if StartAllBack is running for compatible refresh
                startallback_windows = self.find_startallback_tray()
                
                if startallback_windows:
                    # StartAllBack-specific refresh
                    logger.info(f"Refreshing {len(startallback_windows)} StartAllBack tray areas")
                    refresh_count = 0
                    for sb_window in startallback_windows:
                        hwnd = sb_window['hwnd']
                        logger.debug(f"Refreshing StartAllBack window: {sb_window['class']} (hwnd={hwnd})")
                        
                        # Refresh StartAllBack tray windows
                        invalidate_result = self.user32.InvalidateRect(hwnd, None, True)
                        update_result = self.user32.UpdateWindow(hwnd)
                        logger.debug(f"InvalidateRect result: {invalidate_result}, UpdateWindow result: {update_result}")
                        
                        # Send refresh message
                        WM_COMMAND = 0x0111
                        command_result = self.user32.SendMessageW(hwnd, WM_COMMAND, 419, 0)
                        logger.debug(f"WM_COMMAND refresh result: {command_result}")
                        refresh_count += 1
                    
                    logger.info(f"Refreshed {refresh_count} StartAllBack tray windows")
                else:
                    # Standard Windows tray refresh
                    logger.info("Refreshing standard Windows tray areas")
                    
                    tray_wnd = self.user32.FindWindowW("Shell_TrayWnd", None)
                    if tray_wnd:
                        logger.debug(f"Found Shell_TrayWnd: {tray_wnd}")
                        
                        notify_wnd = self.user32.FindWindowExW(tray_wnd, None, "TrayNotifyWnd", None)
                        if notify_wnd:
                            logger.debug(f"Found TrayNotifyWnd: {notify_wnd}")
                            invalidate_result = self.user32.InvalidateRect(notify_wnd, None, True)
                            update_result = self.user32.UpdateWindow(notify_wnd)
                            logger.debug(f"TrayNotifyWnd refresh - InvalidateRect: {invalidate_result}, UpdateWindow: {update_result}")
                        else:
                            logger.warning("Could not find TrayNotifyWnd")
                        
                        # Also try overflow area
                        overflow_wnd = self.user32.FindWindowExW(None, None, "NotifyIconOverflowWindow", None)
                        if overflow_wnd:
                            logger.debug(f"Found NotifyIconOverflowWindow: {overflow_wnd}")
                            overflow_invalidate = self.user32.InvalidateRect(overflow_wnd, None, True)
                            overflow_update = self.user32.UpdateWindow(overflow_wnd)
                            logger.debug(f"Overflow refresh - InvalidateRect: {overflow_invalidate}, UpdateWindow: {overflow_update}")
                        else:
                            logger.debug("No NotifyIconOverflowWindow found")
                    else:
                        logger.error("Could not find Shell_TrayWnd - Windows tray may not be available")
                
                logger.info("======= NOTIFICATION AREA REFRESH COMPLETE: SUCCESS =======")
                return True
            else:
                logger.warning("Discord promotion failed, skipping tray refresh")
                logger.info("======= NOTIFICATION AREA REFRESH COMPLETE: FAILED =======")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing notification area: {e}")
            logger.info("======= NOTIFICATION AREA REFRESH COMPLETE: ERROR =======")
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
        logger.debug("Checking if Discord is running...")
        
        # Hide console window for subprocess
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        logger.debug("Running tasklist command to check for Discord processes...")
        result = subprocess.run(
            ['tasklist', '/FO', 'CSV'], 
            capture_output=True, 
            text=True, 
            check=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        logger.debug(f"Tasklist command completed, output length: {len(result.stdout)} chars")
        
        discord_processes = ['Discord.exe', 'DiscordPTB.exe', 'DiscordCanary.exe']
        found_processes = []
        
        for process_name in discord_processes:
            if process_name.lower() in result.stdout.lower():
                logger.info(f"Found running Discord process: {process_name}")
                found_processes.append(process_name)
        
        if found_processes:
            logger.info(f"Discord is running - found processes: {', '.join(found_processes)}")
            return True
        else:
            logger.debug("No Discord processes found running")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking running processes: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking Discord processes: {e}")
        return False

def get_discord_processes():
    """Get list of running Discord processes"""
    import subprocess
    processes = []
    try:
        logger.debug("Getting detailed list of Discord processes...")
        
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
                logger.debug(f"Added Discord process to list: {process_name}")
        
        logger.info(f"Found {len(processes)} Discord processes: {', '.join(processes) if processes else 'none'}")
        return processes
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting Discord processes: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting Discord processes: {e}")
        return [] 