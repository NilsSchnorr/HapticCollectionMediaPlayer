#!/usr/bin/env python3
"""
Test script to verify NFC tag presence detection
"""
import time
import sys
from config import READER_TYPE, NO_TAG_THRESHOLD, READ_INTERVAL, PN532_INTERFACE, PN532_I2C_BUS, PN532_I2C_ADDRESS

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
        """Initialize PN532 NFC reader"""
        try:
            # Connection string based on interface type
            if PN532_INTERFACE == 'i2c':
                connection_string = f'i2c:{PN532_I2C_BUS}:{PN532_I2C_ADDRESS}'
            elif PN532_INTERFACE == 'spi':
                connection_string = 'spi:0:0'
            elif PN532_INTERFACE == 'uart':
                connection_string = 'tty:serial0:115200'
            else:  # usb
                connection_string = 'usb'
            
            print(f"Initializing PN532 NFC HAT with {PN532_INTERFACE} interface...")
            self.clf = nfc.ContactlessFrontend(connection_string)
            if not self.clf:
                print("No NFC device found!")
                sys.exit(1)
            print("PN532 NFC HAT initialized for testing")
        except Exception as e:
            print(f"Error initializing PN532: {e}")
            print("\nMake sure I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
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
                self.clf.close()
            else:
                GPIO.cleanup()

if __name__ == "__main__":
    tester = PresenceTester()
    tester.run_test()
