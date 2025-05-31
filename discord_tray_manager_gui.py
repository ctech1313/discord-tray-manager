#!/usr/bin/env python3
"""
Discord Tray Manager with GUI - System tray version
A lightweight, non-invasive utility for Windows 10
"""

import time
import subprocess
import threading
import logging
import json
import os
from datetime import datetime
import ctypes
from ctypes import wintypes
import winreg
import sys
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item
from tray_icon_helper import TrayIconManager, refresh_notification_area, is_discord_running, get_discord_processes

# Simple icon data (16x16 icon encoded as base64)
ICON_DATA = """
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AAAB2AAAAdgB+lymcgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAE4SURB
VDiNpZM9SwNBEIafgxCwsLGwsLW1tba0sLBYbG0sLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCws
LCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCws
LCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCws
LCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCws
LCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCws
LCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCws
LCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCws
LCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCws
"""

def create_tray_image():
    """Create a simple system tray icon"""
    # Create a simple 64x64 icon
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a simple Discord-style rounded rectangle
    # Blue color similar to Discord
    color = (88, 101, 242, 255)  # Discord blurple
    
    # Draw rounded rectangle
    margin = 8
    draw.rounded_rectangle(
        [margin, margin, width-margin, height-margin], 
        radius=12, 
        fill=color
    )
    
    # Draw a simple "D" in white
    text_color = (255, 255, 255, 255)
    # Draw letter D (simplified)
    draw.rectangle([20, 20, 25, 44], fill=text_color)  # Vertical line
    draw.rectangle([20, 20, 35, 25], fill=text_color)  # Top horizontal
    draw.rectangle([20, 39, 35, 44], fill=text_color)  # Bottom horizontal
    draw.rectangle([35, 25, 40, 39], fill=text_color)  # Right vertical
    
    return image

class SystemTrayApp:
    def __init__(self):
        self.manager = None
        self.running = False
        
        # Load manager
        self.manager = DiscordTrayManager()
        
        # Create tray icon
        self.icon = pystray.Icon(
            "discord_tray_manager",
            create_tray_image(),
            "Discord Tray Manager",
            menu=pystray.Menu(
                item('Discord Tray Manager', self.show_about, default=True),
                item('Status: Monitoring...', self.show_status),
                pystray.Menu.SEPARATOR,
                item('Open Logs', self.open_logs),
                item('Open Config', self.open_config),
                pystray.Menu.SEPARATOR,
                item('Exit', self.quit_application)
            )
        )
        
    def show_about(self, icon, item):
        """Show about dialog"""
        # Use Windows message box
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0, 
            "Discord Tray Manager v1.0\n\nKeeps Discord icon visible in system tray.\nRunning silently in background.\n\nRight-click tray icon for options.",
            "About Discord Tray Manager",
            0x40  # MB_ICONINFORMATION
        )
    
    def show_status(self, icon, item):
        """Show current status"""
        is_discord_running = self.manager.is_discord_running()
        status = "Discord is running" if is_discord_running else "Discord not detected"
        
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Status: {status}\nCheck interval: {self.manager.check_interval}s\nAuto-fix: {'Enabled' if self.manager.enable_auto_fix else 'Disabled'}",
            "Discord Tray Manager Status",
            0x40  # MB_ICONINFORMATION
        )
    
    def open_logs(self, icon, item):
        """Open log file"""
        try:
            log_file = get_log_file_path()
            os.startfile(log_file)
        except Exception as e:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Could not open log file:\n{e}",
                "Error",
                0x10  # MB_ICONERROR
            )
    
    def open_config(self, icon, item):
        """Open config file"""
        try:
            config_file = "config.json"
            if os.path.exists(config_file):
                os.startfile(config_file)
            else:
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "Config file not found. Using default settings.",
                    "Information",
                    0x40  # MB_ICONINFORMATION
                )
        except Exception as e:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Could not open config file:\n{e}",
                "Error",
                0x10  # MB_ICONERROR
            )
    
    def quit_application(self, icon, item):
        """Exit the application"""
        self.stop_monitoring()
        icon.stop()
    
    def start_monitoring(self):
        """Start the Discord monitoring in a separate thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.run_monitor, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring"""
        self.running = False
        if self.manager:
            self.manager.stop()
    
    def run_monitor(self):
        """Run the monitoring loop"""
        if self.manager:
            self.manager.monitor_and_fix()
    
    def run(self):
        """Run the system tray application"""
        self.start_monitoring()
        self.icon.run()

# Get user's AppData directory for log file
def get_log_file_path():
    """Get the appropriate log file path in user's AppData directory"""
    appdata_dir = os.path.expandvars(r'%LOCALAPPDATA%\Discord Tray Manager')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'discord_tray_manager.log')

def setup_logging():
    """Set up logging configuration"""
    log_file_path = get_log_file_path()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

class DiscordTrayManager:
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        self.running = True
        self.tray_manager = TrayIconManager()
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            self.check_interval = config.get('check_interval', 30)
            self.discord_processes = config.get('discord_processes', ['Discord.exe', 'DiscordPTB.exe', 'DiscordCanary.exe'])
            self.enable_auto_fix = config.get('enable_auto_fix', True)
            self.enable_tray_refresh = config.get('enable_tray_refresh', True)
            self.enable_window_simulation = config.get('enable_window_simulation', False)
            self.startup_delay = config.get('startup_delay', 5)
            
            # Setup logging with config level
            log_level = config.get('log_level', 'INFO')
            setup_logging()
            
            logger.info(f"Loaded configuration")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.setup_defaults()
    
    def setup_defaults(self):
        """Set up default configuration"""
        self.check_interval = 30
        self.discord_processes = ['Discord.exe', 'DiscordPTB.exe', 'DiscordCanary.exe']
        self.enable_auto_fix = True
        self.enable_tray_refresh = True
        self.enable_window_simulation = False
        self.startup_delay = 5
        setup_logging()
        
    def is_discord_running(self):
        """Check if any Discord process is currently running"""
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
            
            for process_name in self.discord_processes:
                if process_name.lower() in result.stdout.lower():
                    logger.debug(f"Found running Discord process: {process_name}")
                    return True
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking running processes: {e}")
            return False

    def check_discord_tray_status(self):
        """Check if Discord icon is properly visible in system tray"""
        if not self.is_discord_running():
            logger.debug("Discord is not running")
            return False, "Discord not running"
        
        # Check if Discord icon is visible in tray
        is_visible = self.tray_manager.is_discord_icon_visible()
        
        if is_visible:
            logger.debug("Discord icon appears to be in system tray")
            return True, "Icon visible"
        else:
            logger.info("Discord is running but icon may not be visible in tray")
            return False, "Icon not visible"

    def fix_discord_tray_icon(self):
        """Attempt to fix Discord tray icon visibility"""
        if not self.enable_auto_fix:
            logger.debug("Auto-fix is disabled")
            return False
        
        logger.info("Attempting to fix Discord tray icon...")
        
        success = False
        
        # Method 1: Refresh notification area
        if self.enable_tray_refresh:
            logger.debug("Refreshing notification area...")
            if self.tray_manager.refresh_notification_area():
                success = True
                logger.info("Successfully refreshed notification area")
        
        # Method 2: Simulate window actions (more invasive)
        if self.enable_window_simulation and not success:
            logger.debug("Simulating Discord window actions...")
            if self.tray_manager.simulate_discord_tray_action():
                success = True
                logger.info("Successfully simulated Discord tray action")
        
        return success

    def monitor_and_fix(self):
        """Main monitoring loop"""
        logger.info("Discord Tray Manager started")
        logger.info(f"Monitoring every {self.check_interval} seconds")
        
        # Initial startup delay
        if self.startup_delay > 0:
            time.sleep(self.startup_delay)
        
        consecutive_failures = 0
        max_failures = 5
        
        while self.running:
            try:
                is_ok, status = self.check_discord_tray_status()
                
                if not is_ok and self.is_discord_running():
                    logger.warning(f"Discord tray issue detected: {status}")
                    
                    if self.fix_discord_tray_icon():
                        logger.info("Successfully applied fix")
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        logger.warning(f"Fix attempt failed ({consecutive_failures}/{max_failures})")
                        
                        if consecutive_failures >= max_failures:
                            logger.error("Too many consecutive failures, taking a break...")
                            time.sleep(self.check_interval * 3)
                            consecutive_failures = 0
                else:
                    consecutive_failures = 0
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}")
                time.sleep(5)

    def stop(self):
        """Stop the monitoring"""
        self.running = False
        logger.info("Discord Tray Manager stopped")

def main():
    """Main entry point for GUI version"""
    if sys.platform != 'win32':
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            "This application is designed for Windows only.",
            "Error",
            0x10  # MB_ICONERROR
        )
        sys.exit(1)
    
    try:
        # Create and run the tray application
        app = SystemTrayApp()
        app.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f"An error occurred: {e}",
            "Fatal Error",
            0x10  # MB_ICONERROR
        )
        sys.exit(1)

if __name__ == "__main__":
    main() 