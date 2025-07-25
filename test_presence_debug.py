#!/usr/bin/env python3
"""
Test script to verify NFC tag presence detection - UART Debug Version
"""
import time
import sys
import os
from config import READER_TYPE, NO_TAG_THRESHOLD, READ_INTERVAL, PN532_INTERFACE, PN532_I2C_BUS, PN532_I2C_ADDRESS, PN532_UART_PORT, PN532_UART_BAUDRATE

if READER_TYPE == "PN532":
    import nfc
else:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522

class PresenceTester:
    def __init__(self):
        self.last_tag = None
        self.tag_present = False
        self.no_tag_count = 0
        
        if READER_TYPE == "PN532":
            self.init_pn532()
        else:
            self.init_rc522()
    
    def init_pn532(self):
        """Initialize PN532 NFC reader with debugging"""
        try:
            print(f"Debug: PN532_INTERFACE = {PN532_INTERFACE}")
            print(f"Debug: PN532_UART_PORT = {PN532_UART_PORT}")
            print(f"Debug: PN532_UART_BAUDRATE = {PN532_UART_BAUDRATE}")
            
            # Connection string based on interface type
            if PN532_INTERFACE == 'i2c':
                connection_string = f'i2c:{PN532_I2C_BUS}:{PN532_I2C_ADDRESS}'
            elif PN532_INTERFACE == 'spi':
                connection_string = 'spi:0:0'
            elif PN532_INTERFACE == 'uart':
                # Try different UART connection formats
                potential_devices = [
                    PN532_UART_PORT,
                    '/dev/serial0',
                    '/dev/ttyAMA0', 
                    '/dev/ttyS0'
                ]
                
                # Find first existing device
                uart_device_path = None
                for device in potential_devices:
                    if os.path.exists(device):
                        uart_device_path = device
                        print(f"Debug: Found UART device: {device}")
                        break
                
                if not uart_device_path:
                    print(f"Error: No UART device found! Tried: {potential_devices}")
                    sys.exit(1)
                
                # Extract device name for connection string (just the name, not full path)
                uart_device = uart_device_path.split('/')[-1]
                connection_string = f'tty:{uart_device}:{PN532_UART_BAUDRATE}'
                
            else:  # usb
                connection_string = 'usb'
            
            print(f"Debug: Connection string: '{connection_string}'")
            print(f"Initializing PN532 NFC HAT with {PN532_INTERFACE} interface...")
            
            self.clf = nfc.ContactlessFrontend(connection_string)
            if not self.clf:
                print("No NFC device found!")
                print("Troubleshooting:")
                print("1. Check hardware jumpers are in UART position")
                print("2. Check UART is enabled: sudo raspi-config")
                print("3. Check user permissions: groups $USER")
                print("4. Try with sudo: sudo python3 test_presence.py")
                sys.exit(1)
            print("✓ PN532 NFC HAT initialized for testing")
        except Exception as e:
            print(f"Error initializing PN532: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            print("\nTroubleshooting:")
            print("1. Make sure UART is enabled: sudo raspi-config -> Interface Options -> Serial")
            print("2. Check hardware jumpers are in UART position")
            print("3. Try with sudo: sudo python3 test_presence.py")
            print("4. Check device exists: ls -la /dev/serial*")
            sys.exit(1)
    
    def init_rc522(self):
        """Initialize RC522 NFC reader"""
        self.reader = SimpleMFRC522()
        print("RC522 NFC reader initialized for testing")
    
    def read_tag(self):
        """Read tag and return UID or None"""
        if READER_TYPE == "PN532":
            try:
                tag = self.clf.connect(rdwr={'on-connect': lambda tag: False}, terminate=lambda: True, timeout=0.1)
                if tag:
                    return tag.identifier.hex()
            except:
                pass
        else:
            try:
                id, text = self.reader.read_no_block()
                if id:
                    return hex(id)[2:].upper()
            except:
                pass
        return None
    
    def run_test(self):
        """Run the presence detection test"""
        print("\n" + "="*50)
        print("NFC TAG PRESENCE DETECTION TEST")
        print("="*50)
        print(f"No-tag threshold: {NO_TAG_THRESHOLD} reads")
        print(f"Read interval: {READ_INTERVAL} seconds")
        print("\nPlace and remove tags to test detection...")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                tag_uid = self.read_tag()
                
                if tag_uid:
                    # Tag detected
                    if not self.tag_present or tag_uid != self.last_tag:
                        print(f"[{time.strftime('%H:%M:%S')}] TAG DETECTED: {tag_uid}")
                        if self.last_tag and tag_uid != self.last_tag:
                            print(f"                    ^ Different tag than before ({self.last_tag})")
                        self.tag_present = True
                        self.last_tag = tag_uid
                    self.no_tag_count = 0
                else:
                    # No tag detected
                    if self.tag_present:
                        self.no_tag_count += 1
                        if self.no_tag_count < NO_TAG_THRESHOLD:
                            print(f"[{time.strftime('%H:%M:%S')}] No tag read ({self.no_tag_count}/{NO_TAG_THRESHOLD})")
                        else:
                            print(f"[{time.strftime('%H:%M:%S')}] TAG REMOVED - Threshold reached")
                            self.tag_present = False
                            self.last_tag = None
                
                time.sleep(READ_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\nTest terminated by user")
        finally:
            if READER_TYPE == "PN532":
                try:
                    self.clf.close()
                except:
                    pass
            else:
                GPIO.cleanup()

if __name__ == "__main__":
    print("=== PN532 UART Debug Test ===")
    print("This version provides detailed debugging information")
    print("")
    
    tester = PresenceTester()
    tester.run_test()
