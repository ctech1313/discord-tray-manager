"""
Tray Icon Helper - Windows API functions for managing system tray icons
"""

import ctypes
from ctypes import wintypes, Structure, POINTER, byref
import struct
import logging

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
            
            # For each Discord window, check if it has a tray icon
            for window in discord_windows:
                hwnd = window['hwnd']
                
                # Check if window is minimized to tray
                if not self.user32.IsWindowVisible(hwnd):
                    logger.debug(f"Discord window {window['title']} is hidden (likely in tray)")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking Discord icon visibility: {e}")
            return False
    
    def refresh_notification_area(self):
        """Force refresh of the notification area"""
        try:
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
                    
                    logger.debug("Refreshed notification area")
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