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
# (TrayIconManager already imported above)

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
            self.enable_registry_check = config.get('enable_registry_check', False)
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
        self.enable_registry_check = False
        self.startup_delay = 5
        setup_logging('INFO')
        
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

def check_and_fix_discord_tray():
    """Check if Discord tray icon is visible and fix if needed"""
    try:
        logger.debug("=== Starting Discord tray check cycle ===")
        
        # Check if Discord is running
        if not is_discord_running():
            logger.debug("Discord is not running, skipping tray check")
            return
        
        logger.info("Discord is running, checking tray icon status...")
        
        # Check if Discord icon is visible in tray
        manager = TrayIconManager()
        is_visible = manager.is_discord_icon_visible()
        
        logger.info(f"Discord tray icon visibility check result: {is_visible}")
        
        if not is_visible:
            logger.warning("Discord icon is not visible in main tray, attempting to fix...")
            
            # Try to fix the tray icon
            success = refresh_notification_area()
            
            if success:
                logger.info("Successfully fixed Discord tray icon visibility")
            else:
                logger.error("Failed to fix Discord tray icon visibility")
        else:
            logger.debug("Discord icon is already visible in main tray")
            
        logger.debug("=== Discord tray check cycle complete ===")
        
    except Exception as e:
        logger.error(f"Error in Discord tray check: {e}")

def main():
    try:
        logger.info("===== DISCORD TRAY MANAGER STARTING =====")
        logger.info(f"Process ID: {os.getpid()}")
        logger.info(f"Log level: {logger.level}")
        
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info(f"Configuration loaded: check_interval={config.get('check_interval', 30)}s, auto_fix={config.get('enable_auto_fix', True)}")
        
        check_interval = config.get('check_interval', 30)
        enable_auto_fix = config.get('enable_auto_fix', True)
        startup_delay = config.get('startup_delay', 5)
        
        if not enable_auto_fix:
            logger.warning("Auto-fix is disabled in configuration - will only monitor, not fix")
        
        # Startup delay
        if startup_delay > 0:
            logger.info(f"Startup delay: waiting {startup_delay} seconds before beginning checks...")
            time.sleep(startup_delay)
        
        # Create system tray icon
        logger.info("Creating system tray icon...")
        create_tray_icon()
        
        logger.info(f"===== DISCORD TRAY MANAGER READY - CHECK INTERVAL: {check_interval}s =====")
        
        # Main loop
        while True:
            try:
                if enable_auto_fix:
                    check_and_fix_discord_tray()
                else:
                    logger.debug("Auto-fix disabled, skipping Discord tray check")
                
                logger.debug(f"Sleeping for {check_interval} seconds until next check...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.info(f"Continuing after error, next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
    except Exception as e:
        logger.error(f"Fatal error in Discord Tray Manager: {e}")
    finally:
        logger.info("===== DISCORD TRAY MANAGER SHUTTING DOWN =====")

if __name__ == "__main__":
    main() 