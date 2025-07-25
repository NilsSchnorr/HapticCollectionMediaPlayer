#!/usr/bin/env python3
"""
Fixed PN532 UART implementation based on working NFC-Player
Uses the exact same approach as the working player
"""

import time
import serial
import RPi.GPIO as GPIO

# Based on working NFC-Player implementation
DEV_SERIAL = '/dev/ttyS0'  # Key difference: uses ttyS0, not ttyAMA0!
BAUD_RATE = 115200

# PN532 Commands
_COMMAND_GETFIRMWAREVERSION = 0x02
_COMMAND_SAMCONFIGURATION = 0x14
_HOSTTOPN532 = 0xD4
_PN532TOHOST = 0xD5
_PREAMBLE = 0x00
_STARTCODE1 = 0x00
_STARTCODE2 = 0xFF
_POSTAMBLE = 0x00

class BusyError(Exception):
    """Base class for exceptions in this module."""
    pass

class PN532_UART_Working:
    """PN532 UART driver based on working NFC-Player implementation"""
    
    def __init__(self, dev=DEV_SERIAL, baudrate=BAUD_RATE, reset=20, debug=False):
        """Create an instance using the working player's approach"""
        self.debug = debug
        self._gpio_init(reset=reset)
        
        # Open UART (exactly like working player)
        self._uart = serial.Serial(dev, baudrate)
        if not self._uart.is_open:
            raise RuntimeError(f'cannot open {dev}')
        
        print(f"✅ UART opened: {dev} at {baudrate} baud")
        
        # Reset and initialize (with retry like working player)
        if reset:
            if debug:
                print("Resetting PN532...")
            self._reset(reset)
        
        try:
            self._wakeup()
            self.get_firmware_version()  # First try
            print("✅ PN532 initialized successfully on first attempt")
            return
        except (BusyError, RuntimeError) as e:
            print(f"First attempt failed: {e}")
            print("Trying second attempt...")
        
        # Second attempt (like working player)
        try:
            self.get_firmware_version()
            print("✅ PN532 initialized successfully on second attempt")
        except Exception as e:
            print(f"❌ Both attempts failed: {e}")
            raise RuntimeError("Failed to initialize PN532 after 2 attempts")
    
    def _gpio_init(self, reset=None):
        """Initialize GPIO exactly like working player"""
        GPIO.setmode(GPIO.BCM)
        if reset:
            GPIO.setup(reset, GPIO.OUT)
            GPIO.output(reset, True)
    
    def _reset(self, pin):
        """Reset sequence exactly like working player"""
        GPIO.output(pin, True)
        time.sleep(0.1)
        GPIO.output(pin, False)
        time.sleep(0.5)        # Key difference: longer reset time
        GPIO.output(pin, True)
        time.sleep(0.1)
        print("🔄 Hardware reset completed")
    
    def _wakeup(self):
        """Wake up sequence exactly like working player"""
        print("📡 Sending wake-up sequence...")
        # Exact wake-up sequence from working player
        wake_cmd = b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self._uart.write(wake_cmd)
        time.sleep(0.1)
        print("✅ Wake-up sequence sent")
        
        # Configure SAM as part of wake-up
        self.SAM_configuration()
    
    def _wait_ready(self, timeout=0.001):
        """Wait for response frame, up to timeout seconds"""
        timestamp = time.monotonic()
        while (time.monotonic() - timestamp) < timeout:
            if self._uart.in_waiting:
                return True
            else:
                time.sleep(0.05)
        return False
    
    def _read_data(self, count):
        """Read data exactly like working player"""
        frame = self._uart.read(min(self._uart.in_waiting, count))
        if not frame:
            raise BusyError("No data read from PN532")
        if self.debug:
            print("Reading: ", [hex(i) for i in frame])
        else:
            time.sleep(0.005)
        return frame
    
    def _write_data(self, framebytes):
        """Write data exactly like working player"""
        self._uart.read(self._uart.in_waiting)  # clear FIFO queue
        self._uart.write(framebytes)
    
    def _write_frame(self, data):
        """Write frame exactly like working player"""
        assert data is not None and 1 < len(data) < 255, 'Data must be array of 1 to 255 bytes.'
        
        length = len(data)
        frame = bytearray(length+7)
        frame[0] = _PREAMBLE
        frame[1] = _STARTCODE1
        frame[2] = _STARTCODE2
        checksum = sum(frame[0:3])
        frame[3] = length & 0xFF
        frame[4] = (~length + 1) & 0xFF
        frame[5:-2] = data
        checksum += sum(data)
        frame[-2] = ~checksum & 0xFF
        frame[-1] = _POSTAMBLE
        
        if self.debug:
            print('Write frame: ', [hex(i) for i in frame])
        self._write_data(bytes(frame))
    
    def _read_frame(self, length):
        """Read frame exactly like working player"""
        response = self._read_data(length+7)
        if self.debug:
            print('Read frame:', [hex(i) for i in response])
        
        # Parse frame (simplified version)
        offset = 0
        while response[offset] == 0x00:
            offset += 1
            if offset >= len(response):
                raise RuntimeError('Response frame preamble does not contain 0x00FF!')
        if response[offset] != 0xFF:
            raise RuntimeError('Response frame preamble does not contain 0x00FF!')
        offset += 1
        if offset >= len(response):
            raise RuntimeError('Response contains no data!')
        
        frame_len = response[offset]
        if (frame_len + response[offset+1]) & 0xFF != 0:
            raise RuntimeError('Response length checksum did not match length!')
        
        checksum = sum(response[offset+2:offset+2+frame_len+1]) & 0xFF
        if checksum != 0:
            raise RuntimeError('Response checksum did not match expected value: ', checksum)
        
        return response[offset+2:offset+2+frame_len]
    
    def call_function(self, command, response_length=0, params=None, timeout=1):
        """Call function exactly like working player"""
        if params is None:
            params = []
        data = bytearray(2+len(params))
        data[0] = _HOSTTOPN532
        data[1] = command & 0xFF
        for i, val in enumerate(params):
            data[2+i] = val
        
        try:
            self._write_frame(data)
        except OSError:
            self._wakeup()
            return None
        
        if not self._wait_ready(timeout):
            return None
        
        # Read ACK
        ack = b'\x00\x00\xFF\x00\xFF\x00'
        if not ack == self._read_data(len(ack)):
            raise RuntimeError('Did not receive expected ACK from PN532!')
        
        if not self._wait_ready(timeout):
            return None
        
        response = self._read_frame(response_length+2)
        if not (response[0] == _PN532TOHOST and response[1] == (command+1)):
            raise RuntimeError('Received unexpected command response!')
        
        return response[2:]
    
    def get_firmware_version(self):
        """Get firmware version exactly like working player"""
        response = self.call_function(_COMMAND_GETFIRMWAREVERSION, 4, timeout=0.5)
        if response is None:
            raise RuntimeError('Failed to detect the PN532')
        return tuple(response)
    
    def SAM_configuration(self):
        """Configure SAM exactly like working player"""
        self.call_function(_COMMAND_SAMCONFIGURATION, params=[0x01, 0x14, 0x01])
        print("✅ SAM configuration completed")
    
    def close(self):
        """Clean up resources"""
        try:
            self._uart.close()
        except:
            pass
        try:
            GPIO.cleanup()
        except:
            pass

# Test function
def test_working_pn532():
    """Test the working PN532 implementation"""
    print("🔧 Testing PN532 with working player's approach")
    print("=" * 50)
    
    try:
        # Initialize with working player's exact settings
        pn532 = PN532_UART_Working(dev='/dev/ttyS0', baudrate=115200, reset=20, debug=True)
        
        # Get firmware version
        ic, ver, rev, support = pn532.get_firmware_version()
        print(f'🎉 Found PN532 with firmware version: {ver}.{rev}[{ic}.{support}]')
        
        # Test basic functionality
        print("🧪 Testing basic functionality...")
        pn532.SAM_configuration()
        
        print("✅ ALL TESTS PASSED!")
        print("🎯 Your PN532 is working with the correct settings!")
        
        pn532.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_working_pn532()
