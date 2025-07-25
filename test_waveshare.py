#!/usr/bin/env python3
"""
Test script for Waveshare PN532 NFC HAT
"""
import time
import sys
from config_waveshare import *

# Import Waveshare PN532 library
from PN532 import PN532_UART_Reader
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WavesharePresenceTester:
    def __init__(self):
        self.last_tag = None
        self.tag_present = False
        self.no_tag_count = 0
        
        self.init_pn532()
    
    def init_pn532(self):
        """Initialize Waveshare PN532 NFC reader"""
        try:
            print("Initializing Waveshare PN532 NFC HAT with UART...")
            print("Hardware requirements:")
            print("- Jumpers: L0->L, L1->L, RSTPDN->D20") 
            print("- DIP switches: RX=ON, TX=ON, others=OFF")
            print("")
            
            # Initialize reader with debug enabled
            self.pn532 = PN532_UART_Reader(
                port='/dev/serial0',
                baudrate=115200,
                rst=PN532_RESET_PIN,
                debug=True
            )
            
            if not self.pn532:
                print("❌ Failed to initialize PN532!")
                print("\nTroubleshooting:")
                print("1. Check hardware jumpers and DIP switches")
                print("2. Ensure UART is enabled: sudo raspi-config")
                print("3. Check permissions: sudo usermod -a -G dialout $USER")
                print("4. Try running with sudo")
                sys.exit(1)
            
            print("✅ Waveshare PN532 NFC HAT initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing PN532: {e}")
            print("\nTroubleshooting:")
            print("1. Check hardware connections and jumper settings")
            print("2. Ensure UART is enabled in raspi-config")
            print("3. Check user is in dialout group")
            print("4. Try running with sudo")
            sys.exit(1)
    
    def read_tag(self):
        """Read NFC tag and return UID string or None"""
        try:
            success, uid_bytes = self.pn532.read_passive_target_ID()
            if success and uid_bytes:
                # Convert bytes to hex string with colons
                uid_hex = ':'.join([f'{b:02X}' for b in uid_bytes])
                return uid_hex
        except Exception as e:
            if "timeout" not in str(e).lower():
                logger.debug(f"Tag read error: {e}")
        return None
    
    def handle_tag_detected(self, tag_uid):
        """Handle when a tag is detected"""
        # If it's a different tag than what's currently displayed
        if tag_uid != self.last_tag:
            print(f"\n[{time.strftime('%H:%M:%S')}] 🏷️  NEW TAG DETECTED: {tag_uid}")
            if self.last_tag:
                print(f"                     (Previous: {self.last_tag})")
            self.last_tag = tag_uid
        
        # Reset the no-tag counter
        self.no_tag_count = 0
        self.tag_present = True
    
    def handle_tag_removed(self):
        """Handle when no tag is detected"""
        if self.tag_present:
            self.no_tag_count += 1
            
            if self.no_tag_count < NO_TAG_THRESHOLD:
                print(f"[{time.strftime('%H:%M:%S')}] 📖 No tag read ({self.no_tag_count}/{NO_TAG_THRESHOLD})")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] 🚫 TAG REMOVED - Threshold reached")
                self.tag_present = False
                self.last_tag = None
    
    def run_test(self):
        """Run the presence detection test"""
        print("\n" + "="*60)
        print("🔍 WAVESHARE PN532 NFC TAG PRESENCE TEST")
        print("="*60)
        print(f"📊 Settings:")
        print(f"   • No-tag threshold: {NO_TAG_THRESHOLD} reads")
        print(f"   • Read interval: {READ_INTERVAL} seconds")
        print(f"   • Reset pin: GPIO {PN532_RESET_PIN}")
        print("\n📋 Instructions:")
        print("   • Place NFC tags on the HAT antenna")
        print("   • Try different tag types and orientations")
        print("   • Press Ctrl+C to exit")
        print("\n🏃 Starting detection loop...\n")
        
        try:
            while True:
                tag_uid = self.read_tag()
                
                if tag_uid:
                    # Tag is present
                    self.handle_tag_detected(tag_uid)
                else:
                    # No tag detected
                    self.handle_tag_removed()
                
                # Small delay to prevent CPU overload
                time.sleep(READ_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Test terminated by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if hasattr(self, 'pn532') and self.pn532:
                self.pn532.close()
            print("🧹 Cleanup complete")

if __name__ == "__main__":
    print("🚀 Waveshare PN532 NFC HAT Test")
    print("📌 Make sure your hardware is configured for UART mode!")
    print("")
    
    tester = WavesharePresenceTester()
    tester.run_test()
