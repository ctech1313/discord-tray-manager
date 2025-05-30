#!/usr/bin/env python3
"""
Discord Tray Manager - Ensures Discord icon stays visible in system tray
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
from tray_icon_helper import TrayIconManager, refresh_notification_area, is_discord_running, get_discord_processes

# Import our helper module
from tray_icon_helper import TrayIconManager

# Get user's AppData directory for log file
def get_log_file_path():
    """Get the appropriate log file path in user's AppData directory"""
    appdata_dir = os.path.expandvars(r'%LOCALAPPDATA%\Discord Tray Manager')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'discord_tray_manager.log')

# Setup logging
def setup_logging(log_level):
    """Set up logging configuration"""
    log_file_path = get_log_file_path()
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
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
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.check_interval = config.get('check_interval', 30)
            self.discord_processes = config.get('discord_processes', ['Discord.exe'])
            self.enable_auto_fix = config.get('enable_auto_fix', True)
            self.enable_tray_refresh = config.get('enable_tray_refresh', True)
            self.enable_window_simulation = config.get('enable_window_simulation', False)
            self.startup_delay = config.get('startup_delay', 5)
            
            # Setup logging with config level
            log_level = config.get('log_level', 'INFO')
            setup_logging(log_level)
            
            logger.info(f"Loaded configuration from {config_path}")
            
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            self.setup_defaults()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            self.setup_defaults()
    
    def setup_defaults(self):
        """Set up default configuration"""
        self.check_interval = 30
        self.discord_processes = ['Discord.exe', 'DiscordPTB.exe', 'DiscordCanary.exe']
        self.enable_auto_fix = True
        self.enable_tray_refresh = True
        self.enable_window_simulation = False
        self.startup_delay = 5
        setup_logging('INFO')
        
    def is_discord_running(self):
        """Check if any Discord process is currently running"""
        try:
            result = subprocess.run(['tasklist', '/FO', 'CSV'], 
                                  capture_output=True, text=True, check=True)
            
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
        
        # Method 3: Registry-based approach for notification settings
        if not success:
            logger.debug("Attempting registry-based notification fix...")
            self.ensure_discord_notifications_enabled()
        
        return success

    def ensure_discord_notifications_enabled(self):
        """Ensure Discord notifications are enabled in Windows settings"""
        try:
            # PowerShell script to check and enable Discord notifications
            powershell_script = '''
            $ErrorActionPreference = "SilentlyContinue"
            
            # Check if Discord notifications are enabled
            $notificationSettings = Get-ChildItem "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings" -ErrorAction SilentlyContinue
            
            foreach ($setting in $notificationSettings) {
                $appId = Split-Path $setting.Name -Leaf
                if ($appId -like "*Discord*") {
                    $currentValue = Get-ItemProperty -Path $setting.PSPath -Name "Enabled" -ErrorAction SilentlyContinue
                    if ($currentValue.Enabled -eq 0) {
                        Write-Output "Enabling notifications for $appId"
                        Set-ItemProperty -Path $setting.PSPath -Name "Enabled" -Value 1
                    }
                }
            }
            '''
            
            result = subprocess.run(['powershell', '-Command', powershell_script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.debug("Checked Discord notification settings")
            else:
                logger.warning("Could not modify notification settings")
                
        except Exception as e:
            logger.error(f"Error ensuring Discord notifications: {e}")

    def monitor_and_fix(self):
        """Main monitoring loop"""
        logger.info("Discord Tray Manager started")
        logger.info(f"Monitoring every {self.check_interval} seconds")
        logger.info(f"Startup delay: {self.startup_delay} seconds")
        
        # Initial startup delay to let system settle
        if self.startup_delay > 0:
            logger.info(f"Waiting {self.startup_delay} seconds before starting monitoring...")
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
                            time.sleep(self.check_interval * 3)  # Longer pause
                            consecutive_failures = 0
                else:
                    consecutive_failures = 0
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping...")
                self.running = False
            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying

    def stop(self):
        """Stop the monitoring"""
        self.running = False
        logger.info("Discord Tray Manager stopped")

def main():
    """Main entry point"""
    if sys.platform != 'win32':
        print("This application is designed for Windows only.")
        sys.exit(1)
    
    print("Discord Tray Manager")
    print("=" * 50)
    print("- Monitors Discord system tray icon")
    print("- Automatically fixes missing tray icons")
    print(f"- Checking every {check_interval} seconds")
    print(f"- Log all activities to {get_log_file_path()}")
    print("- Press Ctrl+C to stop")
    print("=" * 50)
    
    manager = DiscordTrayManager()
    
    try:
        manager.monitor_and_fix()
    except KeyboardInterrupt:
        print("\nStopping Discord Tray Manager...")
        manager.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 