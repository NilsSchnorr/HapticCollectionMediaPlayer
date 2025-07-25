#!/usr/bin/env python3
import time
import subprocess
import os
import sys
import logging
from datetime import datetime
from database import NFCDatabase
from config import *

# Import reader libraries based on configuration
if READER_TYPE == "PN532":
    import nfc
else:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522

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

class NFCDisplay:
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
        
        logging.info("NFC Display System initializing...")
        
        # Initialize reader based on type
        if READER_TYPE == "PN532":
            self.init_pn532()
        else:
            self.init_rc522()
    
    def init_pn532(self):
        """Initialize PN532 NFC reader"""
        try:
            # Connection string based on interface type
            if PN532_INTERFACE == 'i2c':
                # For PN532 NFC HAT using I2C
                connection_string = f'i2c:{PN532_I2C_BUS}:{PN532_I2C_ADDRESS}'
            elif PN532_INTERFACE == 'spi':
                connection_string = 'spi:0:0'  # SPI bus 0, chip select 0
            elif PN532_INTERFACE == 'uart':
                connection_string = 'tty:serial0:115200'  # UART on GPIO pins
            else:  # usb
                connection_string = 'usb'
            
            logging.info(f"Initializing PN532 with interface: {PN532_INTERFACE}")
            logging.info(f"Connection string: {connection_string}")
            
            self.clf = nfc.ContactlessFrontend(connection_string)
            if not self.clf:
                logging.error("No NFC device found!")
                sys.exit(1)
            logging.info("PN532 NFC reader initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing PN532: {e}")
            logging.error("Make sure I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
            sys.exit(1)
    
    def init_rc522(self):
        """Initialize RC522 NFC reader"""
        self.reader = SimpleMFRC522()
        print("RC522 NFC reader initialized")
    
    def read_tag_pn532(self):
        """Read NFC tag using PN532 with non-blocking approach"""
        try:
            # Use a very short timeout for continuous polling
            tag = self.clf.connect(rdwr={'on-connect': lambda tag: False}, terminate=lambda: True, timeout=0.1)
            if tag:
                return tag.identifier.hex()
        except Exception as e:
            if "timeout" not in str(e).lower():
                print(f"Error reading tag: {e}")
        return None
    
    def read_tag_rc522(self):
        """Read NFC tag using RC522"""
        try:
            id, text = self.reader.read_no_block()
            if id:
                return hex(id)[2:].upper()
        except Exception as e:
            print(f"Error reading tag: {e}")
        return None
    
    def format_tag_uid(self, uid):
        """Format tag UID to standard format"""
        # Convert to uppercase and add colons every 2 characters
        uid = uid.upper()
        return ':'.join([uid[i:i+2] for i in range(0, len(uid), 2)])
    
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
        logging.info("NFC Display System Started")
        logging.info(f"Reader Type: {READER_TYPE}")
        logging.info(f"Tag Presence Mode: Active")
        logging.info(f"Home Base: {self.home_base_page}")
        logging.info("Waiting for NFC tags...")
        
        # Open home base page on startup
        self.open_browser(self.home_base_page)
        
        try:
            while True:
                # Read tag based on reader type
                if READER_TYPE == "PN532":
                    tag_uid = self.read_tag_pn532()
                else:
                    tag_uid = self.read_tag_rc522()
                
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
            if READER_TYPE == "PN532":
                try:
                    self.clf.close()
                except:
                    pass
            else:
                GPIO.cleanup()
            
            # Close browser
            if self.current_browser:
                subprocess.run(['pkill', 'chromium'], capture_output=True)
            
            print("System shutdown complete")

if __name__ == "__main__":
    # Check if running as root (required for some NFC readers)
    if READER_TYPE == "RC522" and os.geteuid() != 0:
        print("RC522 reader requires root privileges. Please run with sudo.")
        sys.exit(1)
    
    nfc_display = NFCDisplay()
    nfc_display.run()
