#!/usr/bin/env python3
import time
import subprocess
import os
import sys
import logging
from datetime import datetime
from database import NFCDatabase
from config_waveshare import *

# Import fixed PN532 library based on working NFC-Player
from PN532_fixed import PN532_UART_Reader

# Setup logging
if ENABLE_LOGGING:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.INFO)

class NFCDisplayFixed:
    def __init__(self):
        self.db = NFCDatabase(DATABASE_PATH)
        self.html_dir = os.path.join(os.path.dirname(__file__), 'html')
        self.current_browser = None
        self.current_page = None
        self.current_tag = None
        self.home_base_page = HOME_BASE_PAGE
        self.unknown_tag_page = UNKNOWN_TAG_PAGE
        
        # Tag presence detection settings
        self.tag_present = False
        self.no_tag_count = 0
        self.no_tag_threshold = NO_TAG_THRESHOLD
        
        # HTML cache
        self.html_cache = {} if CACHE_HTML else None
        
        logging.info("NFC Display System initializing (Fixed PN532 - Working Approach)...")
        
        # Initialize PN532 reader using working approach
        self.init_pn532()
    
    def init_pn532(self):
        """Initialize PN532 NFC reader using working NFC-Player approach"""
        try:
            logging.info("Initializing PN532 NFC HAT using working NFC-Player approach...")
            logging.info("Device: /dev/ttyS0 (not /dev/ttyAMA0)")
            logging.info("Hardware: Jumpers L0->L, L1->L, RSTPDN->D20")
            logging.info("Hardware: DIP switches RX=ON, TX=ON, others=OFF")
            
            self.pn532 = PN532_UART_Reader(
                port='/dev/ttyS0',  # Use working player's device
                baudrate=115200,
                rst=PN532_RESET_PIN,
                debug=False  # Set to True for debugging
            )
            
            if not self.pn532:
                logging.error("Failed to initialize PN532!")
                sys.exit(1)
            
            # Get firmware info
            try:
                ic, ver, rev, support = self.pn532.get_firmware_version()
                logging.info(f"PN532 Firmware: {ver}.{rev}[{ic}.{support}]")
            except:
                logging.info("PN532 firmware version not available")
            
            logging.info("Fixed PN532 NFC reader initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing PN532: {e}")
            logging.error("Troubleshooting:")
            logging.error("1. Check hardware jumpers and DIP switches")
            logging.error("2. Ensure UART is enabled: sudo raspi-config")
            logging.error("3. Check user permissions: sudo usermod -a -G dialout $USER")
            logging.error("4. Try running with sudo")
            sys.exit(1)
    
    def read_tag(self):
        """Read NFC tag using fixed library based on working player"""
        try:
            success, uid_bytes = self.pn532.read_passive_target_ID()
            if success and uid_bytes:
                # Convert bytes to hex string with colons
                uid_hex = ':'.join([f'{b:02X}' for b in uid_bytes])
                return uid_hex
        except Exception as e:
            if "timeout" not in str(e).lower():
                logging.debug(f"Tag read error: {e}")
        return None
    
    def format_tag_uid(self, uid):
        """Format tag UID to standard format (already formatted by read_tag)"""
        return uid.upper()
    
    def open_browser(self, html_file):
        """Open HTML file in browser - only if different from current page"""
        # Don't re-open the same page
        if html_file == self.current_page:
            return
        
        # Kill any existing browser instance
        if self.current_browser:
            try:
                subprocess.run(['pkill', 'chromium'], capture_output=True)
                time.sleep(0.5)
            except:
                pass
        
        # Construct full path to HTML file
        html_path = os.path.join(self.html_dir, html_file)
        
        # Check if HTML file exists
        if not os.path.exists(html_path):
            logging.warning(f"HTML file not found: {html_path}")
            # Try to fall back to home base
            html_path = os.path.join(self.html_dir, self.home_base_page)
            if not os.path.exists(html_path):
                logging.error("Home base HTML file not found either!")
                return
        
        # Choose browser command based on dev mode
        if DEV_MODE:
            cmd = [c.replace('{url}', f'file://{html_path}') for c in BROWSER_COMMAND_DEV]
        else:
            cmd = BROWSER_COMMAND + [f'file://{html_path}']
        
        try:
            self.current_browser = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.current_page = html_file
            logging.info(f"Opened: {html_file}")
        except Exception as e:
            logging.error(f"Error opening browser: {e}")
    
    def handle_tag_detected(self, tag_uid):
        """Handle when a tag is detected"""
        # Format UID
        tag_uid = self.format_tag_uid(tag_uid)
        
        # If it's a different tag than what's currently displayed
        if tag_uid != self.current_tag:
            print(f"\nNew tag detected: {tag_uid}")
            self.current_tag = tag_uid
            
            # Look up tag in database
            html_file, tag_name = self.db.get_html_file(tag_uid)
            
            if html_file:
                print(f"Tag name: {tag_name}")
                print(f"Opening: {html_file}")
                self.open_browser(html_file)
            else:
                print("Unknown tag! Opening unknown tag page...")
                self.open_browser('unknown_tag.html')
        
        # Reset the no-tag counter
        self.no_tag_count = 0
        self.tag_present = True
    
    def handle_tag_removed(self):
        """Handle when no tag is detected"""
        if self.tag_present:
            self.no_tag_count += 1
            
            # Only consider tag removed after threshold is reached
            if self.no_tag_count >= self.no_tag_threshold:
                print("\nTag removed - returning to Home Base")
                self.tag_present = False
                self.current_tag = None
                self.open_browser(self.home_base_page)
    
    def run(self):
        """Main loop with continuous tag presence monitoring"""
        logging.info("NFC Display System Started (Fixed PN532 - Working Approach)")
        logging.info(f"Reader Type: PN532_FIXED")
        logging.info(f"Device: /dev/ttyS0")
        logging.info(f"Reset Pin: GPIO {PN532_RESET_PIN}")
        logging.info(f"Tag Presence Mode: Active")
        logging.info(f"Home Base: {self.home_base_page}")
        logging.info("Waiting for NFC tags...")
        
        # Open home base page on startup
        self.open_browser(self.home_base_page)
        
        try:
            while True:
                # Read tag using fixed library
                tag_uid = self.read_tag()
                
                if tag_uid:
                    # Tag is present
                    self.handle_tag_detected(tag_uid)
                else:
                    # No tag detected
                    self.handle_tag_removed()
                
                # Small delay to prevent CPU overload
                time.sleep(READ_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            if hasattr(self, 'pn532') and self.pn532:
                self.pn532.close()
            
            # Close browser
            if self.current_browser:
                subprocess.run(['pkill', 'chromium'], capture_output=True)
            
            print("System shutdown complete")

if __name__ == "__main__":
    # Check if running as root (may be required for GPIO access)
    if os.geteuid() != 0:
        print("Note: This may require root privileges for GPIO access.")
        print("If you encounter permission errors, try running with sudo.")
    
    nfc_display = NFCDisplayFixed()
    nfc_display.run()
