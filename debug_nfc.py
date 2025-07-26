#!/usr/bin/env python3
"""
Debug version of NFC web server - simplified to diagnose issues
"""

import sys
import os
import time

# Add the python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

# Test imports first
print("Testing imports...")
try:
    import RPi.GPIO as GPIO
    print("✓ GPIO imported successfully")
except Exception as e:
    print(f"✗ GPIO import failed: {e}")

try:
    from pn532 import *
    print("✓ pn532 imported successfully")
except Exception as e:
    print(f"✗ pn532 import failed: {e}")

# Try to initialize NFC reader
print("\nInitializing NFC reader...")
try:
    pn532 = PN532_UART(debug=False, reset=20)
    print("✓ PN532_UART created")
    
    ic, ver, rev, support = pn532.get_firmware_version()
    print(f"✓ Found PN532 with firmware version: {ver}.{rev}")
    
    pn532.SAM_configuration()
    print("✓ SAM configuration complete")
    
    print("\nNFC reader initialized successfully!")
    print("Now testing reading in a simple loop...")
    
    # Simple reading loop
    for i in range(30):  # Try for 30 seconds
        uid = pn532.read_passive_target(timeout=0.5)
        if uid:
            uid_hex = ''.join([format(b, '02x') for b in uid])
            print(f"\n✓ Detected NFC chip: {uid_hex}")
            break
        else:
            print(".", end="", flush=True)
        time.sleep(0.5)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        GPIO.cleanup()
        print("\nGPIO cleaned up")
    except:
        pass

print("\nDebug test complete.")
