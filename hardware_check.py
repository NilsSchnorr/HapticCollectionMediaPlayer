#!/usr/bin/env python3
"""
PN532 Hardware Verification Script
Visual step-by-step hardware debugging for Waveshare PN532 HAT
"""

import time
import serial
import RPi.GPIO as GPIO
import os

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def print_step(step_num, title):
    print(f"\n📋 STEP {step_num}: {title}")
    print("-" * 40)

def wait_for_confirmation(message):
    input(f"✋ {message} (Press Enter when done)")

def test_gpio_control():
    """Test GPIO control of the reset pin"""
    print_step(1, "GPIO RESET PIN TEST")
    
    try:
        GPIO.setmode(GPIO.BCM)
        reset_pin = 20
        GPIO.setup(reset_pin, GPIO.OUT)
        
        print("🔌 Testing GPIO reset control...")
        print("   Watch for LED changes on the HAT (if any)")
        
        for i in range(3):
            print(f"   Reset cycle {i+1}/3...")
            GPIO.output(reset_pin, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(reset_pin, GPIO.HIGH) 
            time.sleep(0.5)
        
        GPIO.cleanup()
        print("✅ GPIO reset test completed")
        
    except Exception as e:
        print(f"❌ GPIO test failed: {e}")

def test_uart_loopback():
    """Test UART with different configurations"""
    print_step(2, "UART COMMUNICATION TEST")
    
    devices = ['/dev/ttyAMA0', '/dev/serial0']
    baud_rates = [115200, 57600, 38400, 19200, 9600]
    
    for device in devices:
        if not os.path.exists(device):
            continue
            
        print(f"\n🔍 Testing {device}")
        
        for baud in baud_rates:
            try:
                print(f"   Testing {baud} baud...")
                
                ser = serial.Serial(
                    port=device,
                    baudrate=baud,
                    timeout=1,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False
                )
                
                # Test with different PN532 commands
                test_commands = [
                    # Wake up command
                    bytes([0x55] * 16 + [0x00, 0x00, 0xFF, 0x02, 0xFE, 0xD4, 0x14, 0x01, 0x17, 0x00]),
                    # Firmware version
                    bytes([0x00, 0x00, 0xFF, 0x02, 0xFE, 0xD4, 0x02, 0x2A, 0x00]),
                    # SAM configuration  
                    bytes([0x00, 0x00, 0xFF, 0x05, 0xFB, 0xD4, 0x14, 0x01, 0x14, 0x01, 0x02, 0x00])
                ]
                
                for cmd_idx, cmd in enumerate(test_commands):
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    time.sleep(0.1)
                    
                    ser.write(cmd)
                    time.sleep(0.5)
                    
                    if ser.in_waiting > 0:
                        response = ser.read(ser.in_waiting)
                        print(f"      📥 Command {cmd_idx+1} response: {response.hex()}")
                        if len(response) > 3:
                            print(f"      ✅ Got response at {baud} baud!")
                            ser.close()
                            return device, baud
                
                ser.close()
                
            except Exception as e:
                print(f"      ❌ {baud} baud failed: {e}")
    
    print("❌ No UART response received")
    return None, None

def hardware_checklist():
    """Interactive hardware verification checklist"""
    print_header("HARDWARE VERIFICATION CHECKLIST")
    
    print("🔍 We'll verify each hardware setting step by step...")
    print("   Have a magnifying glass and tweezers ready!")
    
    wait_for_confirmation("Get magnifying glass and tweezers ready")
    
    # Check power
    print("\n1️⃣ POWER CHECK")
    print("   Look at your PN532 HAT")
    print("   ✅ Is there a power LED lit up?")
    print("   ✅ Does the HAT look powered?")
    wait_for_confirmation("Confirm power LED is ON")
    
    # Check physical seating
    print("\n2️⃣ PHYSICAL CONNECTION CHECK")
    print("   ✅ HAT sits flush on ALL 40 GPIO pins")
    print("   ✅ No bent or misaligned pins") 
    print("   ✅ HAT doesn't wobble or move")
    wait_for_confirmation("Confirm HAT is properly seated")
    
    # Check jumpers with magnifying glass
    print("\n3️⃣ JUMPER VERIFICATION (Use magnifying glass!)")
    print("   Look at the jumper area on your HAT")
    print("   You should see small pins with plastic jumper caps")
    print("")
    print("   🔍 L0 and L pins:")
    print("      Are they connected by a small plastic jumper cap?")
    wait_for_confirmation("Verify L0-L jumper is connected")
    
    print("   🔍 L1 and L pins:")
    print("      Are they connected by a small plastic jumper cap?")
    wait_for_confirmation("Verify L1-L jumper is connected")
    
    print("   🔍 RSTPDN and D20 pins:")
    print("      Are they connected by a small plastic jumper cap?")
    wait_for_confirmation("Verify RSTPDN-D20 jumper is connected")
    
    # Check DIP switches with tweezers
    print("\n4️⃣ DIP SWITCH VERIFICATION (Use tweezers!)")
    print("   Find the tiny DIP switches (usually 4 small switches)")
    print("   They should be labeled or numbered")
    print("")
    print("   🎛️ Switch 1 (RX):")
    print("      Should be pushed toward 'ON' position")
    wait_for_confirmation("Verify RX switch is ON")
    
    print("   🎛️ Switch 2 (TX):")
    print("      Should be pushed toward 'ON' position") 
    wait_for_confirmation("Verify TX switch is ON")
    
    print("   🎛️ All other switches (3, 4, etc.):")
    print("      Should be pushed toward 'OFF' position")
    wait_for_confirmation("Verify other switches are OFF")
    
    # Alternative orientations
    print("\n5️⃣ ALTERNATIVE TESTS")
    print("   Some HATs work better in different orientations")
    print("   ⚠️ ONLY if confident with hardware:")
    response = input("   Try rotating HAT 180°? (y/N): ")
    
    if response.lower() == 'y':
        print("   Power off Pi, flip HAT, power on, test again")
        print("   If it doesn't work, flip back!")

def run_comprehensive_test():
    """Run all tests"""
    print_header("PN532 COMPREHENSIVE HARDWARE TEST")
    print("This script will help identify hardware configuration issues")
    
    # Hardware checklist first
    hardware_checklist()
    
    # GPIO test
    test_gpio_control()
    
    # UART test
    device, baud = test_uart_loopback()
    
    if device and baud:
        print(f"\n🎉 SUCCESS! PN532 responds on {device} at {baud} baud")
        print("\n📝 TO FIX YOUR CONFIG:")
        print(f"   Edit PN532.py:")
        print(f"   - Change port='{device}'")
        print(f"   - Change baudrate={baud}")
    else:
        print(f"\n❌ HARDWARE ISSUE CONFIRMED")
        print("\n🔧 NEXT STEPS:")
        print("1. 📸 Take close-up photos of:")
        print("   - Jumper settings")
        print("   - DIP switch positions") 
        print("   - HAT seating on GPIO")
        print("2. 🔄 Try different HAT orientation")
        print("3. 🧪 Test with different Pi (if available)")
        print("4. 📞 Contact Waveshare support")
        print("5. 🔄 Consider RMA/replacement")
        
        print("\n💡 POSSIBLE CAUSES:")
        print("   • Incorrect jumper/DIP switch settings")
        print("   • Defective HAT")
        print("   • Damaged GPIO pins")
        print("   • Incompatible HAT revision")

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        try:
            GPIO.cleanup()
        except:
            pass
