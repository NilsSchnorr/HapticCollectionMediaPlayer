#!/usr/bin/env python3
"""
Test script using the EXACT same approach as the working NFC-Player
This should work since we're copying their working implementation
"""
import time
import sys
from PN532_fixed import PN532_UART_Reader

def test_with_working_approach():
    """Test PN532 using the exact same approach as working NFC-Player"""
    print("🔧 TESTING PN532 WITH WORKING NFC-PLAYER APPROACH")
    print("=" * 60)
    print("Using the exact same settings as the working player:")
    print("• Device: /dev/ttyS0 (not /dev/ttyAMA0)")
    print("• Baud rate: 115200")
    print("• Reset pin: GPIO 20")
    print("• Wake-up sequence: Working player's approach")
    print("• Retry mechanism: Same as working player")
    print("=" * 60)
    
    try:
        # Initialize using working player's exact approach
        print("\n📡 Initializing PN532 with working approach...")
        pn532 = PN532_UART_Reader(
            port='/dev/ttyS0',  # Key difference: use ttyS0 not ttyAMA0
            baudrate=115200,
            rst=20,
            debug=True
        )
        
        if not pn532:
            print("❌ Failed to initialize PN532")
            return False
        
        # Get firmware version (like working player)
        print("\n🔍 Getting firmware version...")
        ic, ver, rev, support = pn532.get_firmware_version()
        print(f'🎉 Found PN532 with firmware version: {ver}.{rev}[{ic}.{support}]')
        
        # Test tag reading (like working player)
        print("\n🏷️  Testing tag detection...")
        print("Place an NFC tag on the HAT...")
        
        tag_found = False
        for attempt in range(50):  # Try for 5 seconds
            success, uid = pn532.read_passive_target_ID()
            if success and uid:
                print(f"\n🎯 TAG DETECTED!")
                print(f"   UID: {[hex(i) for i in uid]}")
                
                # Format like working player
                uid_string = "-"
                for i in uid:
                    uid_string = uid_string + hex(i) + "-"
                print(f"   String: {uid_string}")
                
                uid_integer = int.from_bytes(uid, byteorder='big')
                print(f"   Integer: {uid_integer}")
                
                tag_found = True
                break
            else:
                print(".", end="", flush=True)
                time.sleep(0.1)
        
        if not tag_found:
            print("\n⚠️  No tag detected (this is OK if no tag was placed)")
        
        print(f"\n✅ SUCCESS! PN532 is working with the correct approach!")
        print(f"🎯 Your hardware configuration is correct!")
        
        pn532.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 PN532 Test Using Working NFC-Player Approach")
    print("This test uses the EXACT same code as your working NFC player")
    print("")
    
    if test_with_working_approach():
        print("\n" + "="*60)
        print("🎉 SUCCESS! Your PN532 is working!")
        print("="*60)
        print("✅ Hardware configuration is correct")
        print("✅ UART communication is working")
        print("✅ PN532 is responding properly")
        print("")
        print("🔧 TO FIX YOUR MAIN PROJECT:")
        print("1. Use /dev/ttyS0 instead of /dev/serial0 or /dev/ttyAMA0")
        print("2. Use the wake-up sequence from working player")
        print("3. Use the reset timing from working player") 
        print("4. Use the retry mechanism")
        print("")
        print("📝 Next steps:")
        print("• Update your main project to use these settings")
        print("• Your media player should now work!")
    else:
        print("\n" + "="*60)
        print("❌ Still not working")
        print("="*60)
        print("🔧 HARDWARE CHECK NEEDED:")
        print("1. Verify jumper connections with magnifying glass")
        print("2. Check DIP switch settings with tweezers")
        print("3. Ensure HAT is properly seated")
        print("4. Try different HAT orientation (180° flip)")
        print("5. Contact Waveshare support - hardware may be defective")

if __name__ == "__main__":
    main()
