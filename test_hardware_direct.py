#!/usr/bin/env python3
"""
Hardware-specific PN532 test using direct device access
This bypasses the serial0 mapping and tests both UARTs directly
"""

import time
import serial
import RPi.GPIO as GPIO

def test_pn532_direct(device_path, device_name):
    """Test PN532 directly on specified UART device"""
    print(f"🔍 Testing PN532 on {device_name} ({device_path})")
    print("-" * 50)
    
    try:
        # Setup GPIO reset
        GPIO.setmode(GPIO.BCM)
        reset_pin = 20
        GPIO.setup(reset_pin, GPIO.OUT)
        
        # Hardware reset sequence
        print("🔄 Performing hardware reset...")
        GPIO.output(reset_pin, GPIO.LOW)
        time.sleep(0.1)  # Longer reset
        GPIO.output(reset_pin, GPIO.HIGH)
        time.sleep(0.5)  # Longer startup time
        
        # Test multiple baud rates
        baud_rates = [115200, 57600, 38400, 19200, 9600]
        
        for baud in baud_rates:
            print(f"📡 Testing {baud} baud...")
            
            try:
                # Open serial with specific settings for PN532
                ser = serial.Serial(
                    port=device_path,
                    baudrate=baud,
                    timeout=2,  # Longer timeout
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False
                )
                
                # Clear any existing data
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                time.sleep(0.1)
                
                # Send wake-up sequence (sometimes needed)
                print("   📤 Sending wake-up...")
                ser.write(b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x03\xFD\xD4\x14\x01\x17\x00')
                time.sleep(0.5)
                
                # Clear buffer again
                ser.reset_input_buffer()
                time.sleep(0.1)
                
                # Send firmware version command
                # Frame format: PREAMBLE(00) + START(00FF) + LEN(02) + LCS(FE) + TFI(D4) + CMD(02) + DCS(2A) + POSTAMBLE(00)
                fw_cmd = bytes([0x00, 0x00, 0xFF, 0x02, 0xFE, 0xD4, 0x02, 0x2A, 0x00])
                
                print("   📤 Sending firmware version command...")
                ser.write(fw_cmd)
                time.sleep(1.0)  # Wait longer for response
                
                # Check for response
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting)
                    print(f"   📥 Response ({len(response)} bytes): {response.hex()}")
                    
                    # Check if it looks like a valid PN532 response
                    if len(response) >= 6:
                        # Look for response pattern
                        if response[0:3] == bytes([0x00, 0x00, 0xFF]) or bytes([0x00, 0xFF]) in response:
                            print(f"   ✅ VALID PN532 RESPONSE at {baud} baud!")
                            print(f"   🎉 PN532 is working on {device_name}!")
                            ser.close()
                            return True
                        else:
                            print(f"   ⚠️  Response received but format unexpected")
                    else:
                        print(f"   ⚠️  Response too short")
                else:
                    print(f"   📭 No response at {baud} baud")
                
                ser.close()
                
            except Exception as e:
                print(f"   ❌ Error at {baud} baud: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Failed to test {device_name}: {e}")
        return False
    finally:
        try:
            GPIO.cleanup()
        except:
            pass

def main():
    print("🔧 DIRECT PN532 HARDWARE TEST")
    print("=" * 60)
    print("Testing PN532 directly on both UART devices")
    print("This bypasses the /dev/serial0 mapping issue")
    print("=" * 60)
    print()
    
    # Test devices in order of preference
    test_devices = [
        ("/dev/ttyAMA0", "Primary UART (preferred)"),
        ("/dev/ttyS0", "Mini UART (backup)"),
        ("/dev/serial0", "Serial0 symlink")
    ]
    
    success = False
    
    for device_path, device_name in test_devices:
        if os.path.exists(device_path):
            if test_pn532_direct(device_path, device_name):
                print(f"\n🎉 SUCCESS! PN532 working on {device_name}")
                print(f"📝 Use this device in your config: {device_path}")
                success = True
                break
            print()
        else:
            print(f"⚠️  {device_name} ({device_path}) not found")
            print()
    
    if not success:
        print("❌ NO WORKING PN532 FOUND")
        print("\n🔧 HARDWARE TROUBLESHOOTING:")
        print("1. 📸 Take a photo of your jumper settings and DIP switches")
        print("2. 🔍 Verify with magnifying glass:")
        print("   • L0 and L jumper pins are physically connected")
        print("   • L1 and L jumper pins are physically connected") 
        print("   • RSTPDN and D20 jumper pins are physically connected")
        print("3. 🎛️  DIP switches (use tweezers to verify):")
        print("   • RX switch is pushed to ON position")
        print("   • TX switch is pushed to ON position")
        print("   • All other switches are in OFF position")
        print("4. 🔌 Physical connections:")
        print("   • HAT sits flush on ALL GPIO pins")
        print("   • No bent or misaligned pins")
        print("   • Power LED on HAT is lit")
        print("5. 🔄 Try different HAT orientation (flip 180°)")
        print("6. 🧪 Test with different NFC tag types")
        
        print("\n📞 If still not working:")
        print("   • Hardware may be defective")
        print("   • Contact Waveshare support")
        print("   • Consider RMA/replacement")

if __name__ == "__main__":
    import os
    main()
