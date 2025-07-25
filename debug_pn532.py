#!/usr/bin/env python3
"""
Comprehensive PN532 Hardware Debugging Script
This script checks everything step by step to find the issue
"""

import os
import sys
import time
import serial
import subprocess

def check_system_info():
    """Check basic system information"""
    print("🔍 SYSTEM INFORMATION")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if running as root
    if os.geteuid() == 0:
        print("✅ Running as root (good for GPIO access)")
    else:
        print(f"ℹ️  Running as user: {os.getenv('USER', 'unknown')}")
    
    # Check groups
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        groups = result.stdout.strip()
        print(f"User groups: {groups}")
        if 'dialout' in groups:
            print("✅ User is in dialout group")
        else:
            print("❌ User NOT in dialout group - run: sudo usermod -a -G dialout $USER")
    except:
        print("⚠️  Could not check user groups")
    
    print()

def check_uart_devices():
    """Check available UART devices"""
    print("🔌 UART DEVICE CHECK")
    print("=" * 50)
    
    # Check for common UART devices
    uart_devices = [
        '/dev/serial0',
        '/dev/serial1', 
        '/dev/ttyAMA0',
        '/dev/ttyAMA1',
        '/dev/ttyS0',
        '/dev/ttyS1'
    ]
    
    found_devices = []
    for device in uart_devices:
        if os.path.exists(device):
            found_devices.append(device)
            try:
                # Check permissions
                stat_info = os.stat(device)
                print(f"✅ Found: {device}")
                print(f"   Permissions: {oct(stat_info.st_mode)[-3:]}")
                
                # Check if it's a symlink
                if os.path.islink(device):
                    real_path = os.readlink(device)
                    print(f"   Links to: {real_path}")
                    
            except Exception as e:
                print(f"⚠️  Found {device} but error checking: {e}")
        else:
            print(f"❌ Not found: {device}")
    
    if not found_devices:
        print("❌ No UART devices found!")
        print("📋 To fix:")
        print("   1. Enable UART: sudo raspi-config -> Interface Options -> Serial")
        print("   2. Add to /boot/config.txt: enable_uart=1")
        print("   3. Reboot")
        return None
    
    print(f"\n📊 Found {len(found_devices)} UART device(s)")
    print()
    return found_devices

def check_uart_config():
    """Check UART configuration in system files"""
    print("⚙️  UART CONFIGURATION CHECK")
    print("=" * 50)
    
    # Check /boot/config.txt
    config_path = '/boot/config.txt'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                content = f.read()
                if 'enable_uart=1' in content and not content.find('enable_uart=1') == content.find('#enable_uart=1'):
                    print("✅ enable_uart=1 found in /boot/config.txt")
                else:
                    print("❌ enable_uart=1 NOT found or commented out in /boot/config.txt")
                    print("   Add: enable_uart=1")
                
                if 'dtoverlay=disable-bt' in content:
                    print("✅ Bluetooth disabled (good)")
                else:
                    print("⚠️  Bluetooth not disabled (may cause conflicts)")
                    print("   Consider adding: dtoverlay=disable-bt")
        except Exception as e:
            print(f"❌ Error reading /boot/config.txt: {e}")
    else:
        print("❌ /boot/config.txt not found")
    
    # Check cmdline.txt for serial console conflicts
    cmdline_path = '/boot/cmdline.txt'
    if os.path.exists(cmdline_path):
        try:
            with open(cmdline_path, 'r') as f:
                content = f.read()
                if 'console=serial0' in content or 'console=ttyAMA0' in content:
                    print("⚠️  Serial console found in /boot/cmdline.txt (may interfere)")
                    print("   Consider removing console=serial0 or console=ttyAMA0")
                else:
                    print("✅ No serial console conflicts in /boot/cmdline.txt")
        except Exception as e:
            print(f"❌ Error reading /boot/cmdline.txt: {e}")
    
    print()

def test_uart_communication(device_path):
    """Test basic UART communication"""
    print(f"📡 TESTING UART COMMUNICATION: {device_path}")
    print("=" * 50)
    
    # Test different baud rates
    baud_rates = [115200, 57600, 38400, 19200, 9600]
    
    for baud in baud_rates:
        print(f"Testing {device_path} at {baud} baud...")
        try:
            # Try to open serial port
            ser = serial.Serial(
                port=device_path,
                baudrate=baud,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            print(f"✅ Successfully opened {device_path} at {baud} baud")
            
            # Test basic read/write
            try:
                ser.write(b'\x00\x00\xFF\x02\xFE\xD4\x02\x2A\x00')  # Simple PN532 command
                time.sleep(0.1)
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting)
                    print(f"   📥 Received {len(response)} bytes: {response.hex()}")
                else:
                    print(f"   📭 No response received")
            except Exception as e:
                print(f"   ⚠️  Communication test failed: {e}")
            
            ser.close()
            print(f"   🔒 Closed {device_path}")
            
        except serial.SerialException as e:
            print(f"❌ Failed to open {device_path} at {baud}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error with {device_path} at {baud}: {e}")
    
    print()

def check_gpio_setup():
    """Check GPIO setup"""
    print("🔌 GPIO SETUP CHECK")
    print("=" * 50)
    
    try:
        import RPi.GPIO as GPIO
        print("✅ RPi.GPIO imported successfully")
        
        # Test GPIO setup
        GPIO.setmode(GPIO.BCM)
        
        # Test reset pin (20)
        reset_pin = 20
        try:
            GPIO.setup(reset_pin, GPIO.OUT)
            print(f"✅ GPIO {reset_pin} (reset pin) configured as output")
            
            # Test reset sequence
            GPIO.output(reset_pin, GPIO.LOW)
            time.sleep(0.01)
            GPIO.output(reset_pin, GPIO.HIGH)
            print(f"✅ Reset sequence completed on GPIO {reset_pin}")
            
        except Exception as e:
            print(f"❌ Error with GPIO {reset_pin}: {e}")
        
        GPIO.cleanup()
        print("✅ GPIO cleanup completed")
        
    except ImportError:
        print("❌ RPi.GPIO not available")
        print("   Install with: pip install RPi.GPIO")
    except Exception as e:
        print(f"❌ GPIO error: {e}")
    
    print()

def check_hardware_connections():
    """Provide hardware connection checklist"""
    print("🔧 HARDWARE CONNECTION CHECKLIST")
    print("=" * 50)
    print("📋 For Waveshare PN532 HAT, verify:")
    print("   🔗 Jumpers:")
    print("      • L0 connected to L")
    print("      • L1 connected to L") 
    print("      • RSTPDN connected to D20")
    print("   🎛️  DIP Switches:")
    print("      • RX switch: ON")
    print("      • TX switch: ON")
    print("      • All other switches: OFF")
    print("   📐 Physical:")
    print("      • HAT properly seated on GPIO pins")
    print("      • No bent pins")
    print("      • Power LED on HAT should be lit")
    print("   🚫 Remove:")
    print("      • Metal objects near antenna")
    print("      • Metal keychains from NFC tags")
    print()

def test_minimal_pn532():
    """Test minimal PN532 communication"""
    print("🏷️  MINIMAL PN532 TEST")
    print("=" * 50)
    
    devices_to_test = ['/dev/serial0', '/dev/ttyAMA0', '/dev/ttyS0']
    
    for device in devices_to_test:
        if not os.path.exists(device):
            continue
            
        print(f"Testing PN532 on {device}...")
        
        try:
            import RPi.GPIO as GPIO
            
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            reset_pin = 20
            GPIO.setup(reset_pin, GPIO.OUT)
            
            # Reset PN532
            GPIO.output(reset_pin, GPIO.LOW)
            time.sleep(0.01)
            GPIO.output(reset_pin, GPIO.HIGH)
            time.sleep(0.1)
            
            # Open serial port
            ser = serial.Serial(device, 115200, timeout=1)
            time.sleep(0.1)
            
            # Send firmware version command
            # Frame: PREAMBLE + START + LEN + LEN_CHK + TFI + CMD + CHK + POSTAMBLE
            cmd = bytes([0x00, 0x00, 0xFF, 0x02, 0xFE, 0xD4, 0x02, 0x2A, 0x00])
            
            print(f"   📤 Sending firmware version command...")
            ser.write(cmd)
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"   📥 Response: {response.hex()}")
                if len(response) >= 6:
                    print(f"   ✅ PN532 responded! Device appears functional.")
                    ser.close()
                    GPIO.cleanup()
                    return True
                else:
                    print(f"   ⚠️  Short response, may indicate issues")
            else:
                print(f"   📭 No response from PN532")
            
            ser.close()
            GPIO.cleanup()
            
        except Exception as e:
            print(f"   ❌ Error testing {device}: {e}")
            try:
                GPIO.cleanup()
            except:
                pass
    
    print("❌ No working PN532 found on any device")
    return False

def main():
    """Run all diagnostic checks"""
    print("🔍 PN532 COMPREHENSIVE DIAGNOSTIC")
    print("=" * 60)
    print("This script will check everything needed for PN532 UART communication")
    print("=" * 60)
    print()
    
    # Run all checks
    check_system_info()
    uart_devices = check_uart_devices()
    check_uart_config()
    check_gpio_setup()
    check_hardware_connections()
    
    if uart_devices:
        print("🧪 COMMUNICATION TESTS")
        print("=" * 50)
        for device in uart_devices[:2]:  # Test first 2 devices
            test_uart_communication(device)
    
    # Final PN532 test
    if test_minimal_pn532():
        print("🎉 SUCCESS! PN532 is responding.")
        print("   Your hardware appears to be working correctly.")
        print("   The issue may be in the software configuration.")
    else:
        print("❌ HARDWARE ISSUE DETECTED")
        print("   📋 Next steps:")
        print("   1. Double-check all jumper and DIP switch settings")
        print("   2. Ensure HAT is properly seated")
        print("   3. Try different UART settings in raspi-config")
        print("   4. Check for hardware defects")
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnostic script error: {e}")
        import traceback
        traceback.print_exc()
