#!/usr/bin/env python3
"""
PN532 Direct Device Test - Bypasses /dev/serial0 mapping issues
Tests PN532 on all available UART devices to find what works
"""

import os
import time
import serial
import RPi.GPIO as GPIO

def test_device(device_path, device_name):
    """Test PN532 on a specific device"""
    print(f"🔍 Testing {device_name}: {device_path}")
    
    if not os.path.exists(device_path):
        print(f"   ❌ Device does not exist")
        return False
    
    try:
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        reset_pin = 20
        GPIO.setup(reset_pin, GPIO.OUT)
        
        # Reset PN532
        GPIO.output(reset_pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(reset_pin, GPIO.HIGH)
        time.sleep(0.5)
        
        # Test UART communication
        ser = serial.Serial(
            port=device_path,
            baudrate=115200,
            timeout=2,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)
        
        # Send firmware version command
        fw_cmd = bytes([0x00, 0x00, 0xFF, 0x02, 0xFE, 0xD4, 0x02, 0x2A, 0x00])
        ser.write(fw_cmd)
        time.sleep(1.0)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"   📥 Response: {response.hex()}")
            
            # Check for valid PN532 response
            if len(response) >= 6 and (response[0:3] == bytes([0x00, 0x00, 0xFF]) or bytes([0x00, 0xFF]) in response):
                print(f"   ✅ PN532 WORKS on {device_name}!")
                ser.close()
                return device_path
            else:
                print(f"   ⚠️  Invalid response format")
        else:
            print(f"   📭 No response")
        
        ser.close()
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        try:
            GPIO.cleanup()
        except:
            pass

def main():
    print("🔍 PN532 DEVICE FINDER")
    print("=" * 40)
    print("Finding which UART device works with your PN532...")
    print()
    
    # Test all possible UART devices
    test_devices = [
        ("/dev/ttyAMA0", "Primary UART"),
        ("/dev/ttyS0", "Mini UART"), 
        ("/dev/serial0", "Serial0 symlink"),
        ("/dev/serial1", "Serial1 symlink"),
        ("/dev/ttyAMA1", "Secondary UART")
    ]
    
    working_device = None
    
    for device_path, device_name in test_devices:
        result = test_device(device_path, device_name)
        if result:
            working_device = result
            break
        print()
    
    print("=" * 40)
    if working_device:
        print(f"🎉 SUCCESS! PN532 works on: {working_device}")
        print()
        print("📝 TO FIX YOUR CODE:")
        print(f"   Edit PN532.py line ~25:")
        print(f"   Change: port='/dev/serial0'")
        print(f"   To:     port='{working_device}'")
        print()
        print("🚀 Then run: python3 test_waveshare.py")
    else:
        print("❌ PN532 not responding on any UART device")
        print()
        print("🔧 HARDWARE CHECK:")
        print("   1. Verify jumper connections with magnifying glass")
        print("   2. Check DIP switch settings with tweezers")
        print("   3. Ensure HAT is properly seated")
        print("   4. Try different HAT orientation")
        print("   5. Test with known-good NFC tag")

if __name__ == "__main__":
    main()
