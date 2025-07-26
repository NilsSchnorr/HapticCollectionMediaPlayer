#!/usr/bin/env python3
"""
NFC HTML Player for HapticCollectionMediaPlayer
This script continuously monitors for NFC chips and opens the associated HTML files
"""

import json
import os
import time
import webbrowser
import subprocess
import platform
import sys

# Add the python directory to the path so we can import pn532
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

try:
    from pn532 import PN532_UART
    import RPi.GPIO as GPIO
except ImportError:
    print("Warning: Running without Raspberry Pi GPIO/PN532 support")
    print("This script requires a Raspberry Pi with PN532 NFC reader")
    sys.exit(1)

# Configuration
MAPPINGS_FILE = "nfc_mappings.json"
HTML_CONTENT_DIR = "html_content"
SCAN_INTERVAL = 0.5  # Time between NFC scans in seconds
DEBOUNCE_TIME = 3    # Time to wait before reading the same chip again

class NFCPlayer:
    def __init__(self):
        self.last_uid = None
        self.last_read_time = 0
        self.pn532 = None
        self.mappings = {}
        
    def initialize_nfc_reader(self):
        """Initialize the PN532 NFC reader"""
        try:
            self.pn532 = PN532_UART(debug=False, reset=20)
            ic, ver, rev, support = self.pn532.get_firmware_version()
            print(f'Found PN532 with firmware version: {ver}.{rev}')
            self.pn532.SAM_configuration()
            return True
        except Exception as e:
            print(f"Error initializing NFC reader: {e}")
            return False
    
    def load_mappings(self):
        """Load NFC to HTML mappings from JSON file"""
        if os.path.exists(MAPPINGS_FILE):
            try:
                with open(MAPPINGS_FILE, 'r') as f:
                    self.mappings = json.load(f)
                print(f"Loaded {len(self.mappings)} NFC mappings")
            except Exception as e:
                print(f"Error loading mappings: {e}")
                self.mappings = {}
        else:
            print("No mappings file found")
            self.mappings = {}
    
    def open_html_file(self, html_file):
        """Open an HTML file in the default browser"""
        file_path = os.path.join(HTML_CONTENT_DIR, html_file)
        
        if not os.path.exists(file_path):
            print(f"HTML file not found: {file_path}")
            return False
        
        try:
            # Get absolute path
            abs_path = os.path.abspath(file_path)
            file_url = f"file://{abs_path}"
            
            # Open in browser based on platform
            if platform.system() == 'Linux':
                # On Raspberry Pi, use chromium-browser if available
                try:
                    subprocess.run(['chromium-browser', '--noerrdialogs', '--kiosk', file_url])
                except:
                    # Fallback to default browser
                    webbrowser.open(file_url)
            else:
                webbrowser.open(file_url)
            
            print(f"Opened HTML file: {html_file}")
            return True
            
        except Exception as e:
            print(f"Error opening HTML file: {e}")
            return False
    
    def run(self):
        """Main loop to continuously monitor for NFC chips"""
        print("\n" + "="*50)
        print("NFC HTML Player Started")
        print("="*50)
        print("Place an NFC chip on the reader to open associated HTML content")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                # Reload mappings periodically to catch updates
                if int(time.time()) % 10 == 0:  # Every 10 seconds
                    self.load_mappings()
                
                # Try to read NFC chip
                uid = self.pn532.read_passive_target(timeout=SCAN_INTERVAL)
                
                if uid is not None:
                    # Convert UID to hex string
                    uid_hex = ''.join([format(i, '02x') for i in uid])
                    current_time = time.time()
                    
                    # Check if this is a new chip or enough time has passed
                    if (uid_hex != self.last_uid or 
                        current_time - self.last_read_time > DEBOUNCE_TIME):
                        
                        print(f"\nDetected NFC chip: {uid_hex}")
                        
                        # Check if we have a mapping for this UID
                        if uid_hex in self.mappings:
                            mapping = self.mappings[uid_hex]
                            html_file = mapping.get('html_file')
                            description = mapping.get('description', 'No description')
                            
                            print(f"Found mapping: {html_file}")
                            print(f"Description: {description}")
                            
                            # Open the HTML file
                            if self.open_html_file(html_file):
                                print("✓ Successfully opened HTML content")
                            else:
                                print("✗ Failed to open HTML content")
                        else:
                            print("No mapping found for this NFC chip")
                            print("Use the web interface to create a mapping")
                        
                        # Update last read info
                        self.last_uid = uid_hex
                        self.last_read_time = current_time
                else:
                    # No chip detected, reset last UID if enough time has passed
                    if time.time() - self.last_read_time > DEBOUNCE_TIME:
                        self.last_uid = None
                
                # Small delay to prevent CPU overuse
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\nShutting down NFC player...")
        except Exception as e:
            print(f"\nError in main loop: {e}")
        finally:
            GPIO.cleanup()

def main():
    # Create necessary directories
    os.makedirs(HTML_CONTENT_DIR, exist_ok=True)
    
    # Initialize and run player
    player = NFCPlayer()
    
    # Initialize NFC reader
    if not player.initialize_nfc_reader():
        print("Failed to initialize NFC reader. Exiting.")
        sys.exit(1)
    
    # Load mappings
    player.load_mappings()
    
    # Run the player
    player.run()

if __name__ == '__main__':
    main()
