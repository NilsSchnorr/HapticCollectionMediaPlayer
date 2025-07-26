#!/usr/bin/env python3
"""
Test script to verify NFC reader works with our setup
This closely matches the working example_get_uid.py
"""

import sys
import os

# Add the python directory to the path so we can import pn532
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

import RPi.GPIO as GPIO
from pn532 import *

if __name__ == '__main__':
    print("Testing NFC reader setup...")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path includes: {sys.path}")
    
    try:
        # Use exact same initialization as the working example
        pn532 = PN532_UART(debug=False, reset=20)
        
        ic, ver, rev, support = pn532.get_firmware_version()
        print(f'Found PN532 with firmware version: {ver}.{rev}')
        
        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()
        
        print('Waiting for RFID/NFC card...')
        print('This should work exactly like example_get_uid.py')
        
        attempts = 0
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)
            attempts += 1
            
            if attempts % 10 == 0:
                print(f'\nAttempts: {attempts}', end='')
            else:
                print('.', end='', flush=True)
            
            # Try again if no card is available.
            if uid is None:
                continue
                
            print(f'\nFound card with UID: {[hex(i) for i in uid]}')
            # Also print as hex string like our web server
            uid_hex = ''.join([format(i, '02x') for i in uid])
            print(f'UID as hex string: {uid_hex}')
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        GPIO.cleanup()
        print("\nTest complete.")
