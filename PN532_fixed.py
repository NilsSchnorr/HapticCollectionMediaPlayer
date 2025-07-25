#!/usr/bin/env python3
"""
Waveshare PN532 NFC HAT Library for UART Communication
Fixed version based on working NFC-Player implementation
"""

import time
import serial
import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)

# Based on working NFC-Player - use ttyS0, not ttyAMA0!
DEFAULT_UART_PORT = '/dev/ttyS0'
DEFAULT_BAUDRATE = 115200

# PN532 Commands
PN532_COMMAND_GETFIRMWAREVERSION = 0x02
PN532_COMMAND_SAMCONFIGURATION = 0x14

# Frame format
PN532_PREAMBLE = 0x00
PN532_STARTCODE1 = 0x00
PN532_STARTCODE2 = 0xFF
PN532_POSTAMBLE = 0x00

PN532_HOSTTOPN532 = 0xD4
PN532_PN532TOHOST = 0xD5

class PN532_UART:
    def __init__(self, port=DEFAULT_UART_PORT, baudrate=DEFAULT_BAUDRATE, rst=20, debug=False):
        """
        Initialize PN532 UART communication using working NFC-Player approach
        
        Args:
            port: UART port (default: /dev/ttyS0 - key difference!)
            baudrate: Communication speed (default: 115200)
            rst: Reset pin GPIO number (default: 20)
            debug: Enable debug output
        """
        self.uart_port = port
        self.baudrate = baudrate
        self.rst_pin = rst
        self.debug = debug
        
        # Initialize GPIO for reset
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.output(self.rst_pin, True)  # Start high
        
        # Initialize UART exactly like working player
        try:
            self.uart = serial.Serial(
                port=self.uart_port,
                baudrate=self.baudrate,
                timeout=1
            )
            if not self.uart.is_open:
                raise RuntimeError(f'cannot open {self.uart_port}')
                
            if self.debug:
                logger.info(f"UART initialized on {port} at {baudrate} baud")
        except Exception as e:
            logger.error(f"Failed to initialize UART: {e}")
            raise
        
        # Reset and initialize with retry (like working player)
        if self.debug:
            logger.info("Resetting PN532...")
        self.reset()
        
        try:
            self._wakeup()
            self.get_firmware_version()  # First attempt
            if self.debug:
                logger.info("PN532 initialized successfully on first attempt")
            return
        except Exception as e:
            if self.debug:
                logger.warning(f"First attempt failed: {e}, trying again...")
        
        # Second attempt (retry like working player)
        try:
            self.get_firmware_version()
            if self.debug:
                logger.info("PN532 initialized successfully on second attempt")
        except Exception as e:
            logger.error(f"Both initialization attempts failed: {e}")
            raise RuntimeError("Failed to initialize PN532")
    
    def reset(self):
        """Hardware reset exactly like working player"""
        GPIO.output(self.rst_pin, True)
        time.sleep(0.1)
        GPIO.output(self.rst_pin, False)
        time.sleep(0.5)  # Longer reset time (key difference)
        GPIO.output(self.rst_pin, True)
        time.sleep(0.1)
        
        if self.debug:
            logger.debug("PN532 hardware reset completed")
    
    def _wakeup(self):
        """Wake up sequence exactly like working player"""
        if self.debug:
            logger.debug("Sending wake-up sequence...")
        
        # Exact wake-up sequence from working NFC-Player
        wake_cmd = b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.uart.write(wake_cmd)
        time.sleep(0.1)
        
        # Configure SAM as part of wake-up (like working player)
        self.SAM_configuration()
        
        if self.debug:
            logger.debug("Wake-up sequence completed")
    
    def _wait_ready(self, timeout=0.001):
        """Wait for response frame, exactly like working player"""
        timestamp = time.monotonic()
        while (time.monotonic() - timestamp) < timeout:
            if self.uart.in_waiting:
                return True
            else:
                time.sleep(0.05)
        return False
    
    def _read_data(self, count):
        """Read data exactly like working player"""
        frame = self.uart.read(min(self.uart.in_waiting, count))
        if not frame:
            raise RuntimeError("No data read from PN532")
        if self.debug:
            logger.debug(f"Reading: {[hex(i) for i in frame]}")
        else:
            time.sleep(0.005)
        return frame
    
    def _write_data(self, framebytes):
        """Write data exactly like working player"""
        self.uart.read(self.uart.in_waiting)  # clear FIFO queue
        self.uart.write(framebytes)
    
    def _calculate_checksum(self, data):
        """Calculate checksum for PN532 frame"""
        checksum = 0
        for byte in data:
            checksum += byte
        return (~checksum + 1) & 0xFF
    
    def _write_frame(self, data):
        """Write frame exactly like working player"""
        assert data is not None and 1 < len(data) < 255, 'Data must be array of 1 to 255 bytes.'
        
        length = len(data)
        frame = bytearray(length+7)
        frame[0] = PN532_PREAMBLE
        frame[1] = PN532_STARTCODE1
        frame[2] = PN532_STARTCODE2
        checksum = sum(frame[0:3])
        frame[3] = length & 0xFF
        frame[4] = (~length + 1) & 0xFF
        frame[5:-2] = data
        checksum += sum(data)
        frame[-2] = ~checksum & 0xFF
        frame[-1] = PN532_POSTAMBLE
        
        if self.debug:
            logger.debug(f'Write frame: {[hex(i) for i in frame]}')
        self._write_data(bytes(frame))
    
    def _read_frame(self, length):
        """Read frame exactly like working player"""
        response = self._read_data(length+7)
        if self.debug:
            logger.debug(f'Read frame: {[hex(i) for i in response]}')
        
        # Parse frame
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
        data[0] = PN532_HOSTTOPN532
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
        if not (response[0] == PN532_PN532TOHOST and response[1] == (command+1)):
            raise RuntimeError('Received unexpected command response!')
        
        return response[2:]
    
    def SAM_configuration(self):
        """Configure SAM exactly like working player"""
        try:
            self.call_function(PN532_COMMAND_SAMCONFIGURATION, params=[0x01, 0x14, 0x01])
            return True
        except Exception as e:
            if self.debug:
                logger.error(f"SAM configuration failed: {e}")
            return False
    
    def get_firmware_version(self):
        """Get firmware version exactly like working player"""
        response = self.call_function(PN532_COMMAND_GETFIRMWAREVERSION, 4, timeout=0.5)
        if response is None:
            raise RuntimeError('Failed to detect the PN532')
        return response
    
    def read_passive_target_ID(self, card_baud=0):
        """
        Read passive target (NFC tag) ID - simplified version
        
        Args:
            card_baud: Card baud rate (0 = 106kbps Type A)
            
        Returns:
            Tuple of (success, uid_bytes) or (False, None)
        """
        try:
            # Clear any pending data
            self.uart.reset_input_buffer()
            
            # Send InListPassiveTarget command
            response = self.call_function(0x4A, params=[0x01, card_baud], response_length=19, timeout=0.1)
            
            if response is None or len(response) < 2:
                return False, None
            
            # Check if tag found
            if response[0] != 0x01:  # Number of tags found
                return False, None
            
            # Extract UID
            if len(response) < 7:
                return False, None
            
            uid_length = response[5]
            if len(response) < 6 + uid_length:
                return False, None
            
            uid = response[6:6 + uid_length]
            
            if self.debug:
                uid_hex = ':'.join([f'{b:02X}' for b in uid])
                logger.debug(f"Tag found: {uid_hex}")
            
            return True, uid
            
        except Exception as e:
            if self.debug and "timeout" not in str(e).lower():
                logger.debug(f"Tag read error: {e}")
            return False, None
    
    def close(self):
        """Clean up resources"""
        try:
            self.uart.close()
        except:
            pass
        
        try:
            GPIO.cleanup()
        except:
            pass
        
        if self.debug:
            logger.info("PN532 UART closed")

# Convenience function
def PN532_UART_Reader(port=DEFAULT_UART_PORT, baudrate=DEFAULT_BAUDRATE, rst=20, debug=False):
    """
    Create and initialize PN532 UART reader using working approach
    
    Returns:
        PN532_UART instance or None if initialization fails
    """
    try:
        reader = PN532_UART(port=port, baudrate=baudrate, rst=rst, debug=debug)
        
        # Test communication
        firmware = reader.get_firmware_version()
        if firmware:
            ic, ver, rev, support = firmware
            logger.info(f"PN532 Firmware: IC={ic}, Ver={ver}, Rev={rev}, Support={support}")
        else:
            logger.warning("Could not read firmware version")
        
        return reader
    
    except Exception as e:
        logger.error(f"Failed to initialize PN532: {e}")
        return None
