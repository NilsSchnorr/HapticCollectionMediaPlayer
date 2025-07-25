#!/usr/bin/env python3
"""
Waveshare PN532 NFC HAT Library for UART Communication
Simplified version for the media player project
"""

import time
import serial
import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)

# PN532 Commands
PN532_COMMAND_GETFIRMWAREVERSION = 0x02
PN532_COMMAND_SAMCONFIGURATION = 0x14
PN532_COMMAND_INLISTPASSIVETARGET = 0x4A

# Frame format
PN532_PREAMBLE = 0x00
PN532_STARTCODE1 = 0x00
PN532_STARTCODE2 = 0xFF
PN532_POSTAMBLE = 0x00

PN532_HOSTTOPN532 = 0xD4
PN532_PN532TOHOST = 0xD5

class PN532_UART:
    def __init__(self, port='/dev/serial0', baudrate=115200, rst=20, debug=False):
        """
        Initialize PN532 UART communication
        
        Args:
            port: UART port (default: /dev/serial0)
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
        
        # Initialize UART
        try:
            self.uart = serial.Serial(
                port=self.uart_port,
                baudrate=self.baudrate,
                timeout=1
            )
            if self.debug:
                logger.info(f"UART initialized on {port} at {baudrate} baud")
        except Exception as e:
            logger.error(f"Failed to initialize UART: {e}")
            raise
        
        # Reset and initialize PN532
        self.reset()
        time.sleep(0.1)
        
        if self.debug:
            logger.info("PN532 UART initialized")
    
    def reset(self):
        """Hardware reset of PN532"""
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        
        if self.debug:
            logger.debug("PN532 reset")
    
    def _calculate_checksum(self, data):
        """Calculate checksum for PN532 frame"""
        checksum = 0
        for byte in data:
            checksum += byte
        return (~checksum + 1) & 0xFF
    
    def _write_frame(self, data):
        """Write frame to PN532"""
        frame = []
        frame.append(PN532_PREAMBLE)
        frame.append(PN532_STARTCODE1)
        frame.append(PN532_STARTCODE2)
        
        length = len(data) + 1  # +1 for checksum
        frame.append(length)
        frame.append((~length + 1) & 0xFF)  # Length checksum
        
        frame.append(PN532_HOSTTOPN532)
        frame.extend(data)
        
        checksum = self._calculate_checksum([PN532_HOSTTOPN532] + data)
        frame.append(checksum)
        frame.append(PN532_POSTAMBLE)
        
        if self.debug:
            logger.debug(f"Writing frame: {[hex(x) for x in frame]}")
        
        self.uart.write(bytes(frame))
    
    def _read_frame(self, timeout=1.0):
        """Read frame from PN532"""
        start_time = time.time()
        
        # Wait for preamble
        while time.time() - start_time < timeout:
            if self.uart.in_waiting > 0:
                byte = self.uart.read(1)
                if byte and byte[0] == PN532_PREAMBLE:
                    break
        else:
            return None
        
        # Read start codes
        data = self.uart.read(2)
        if len(data) < 2 or data[0] != PN532_STARTCODE1 or data[1] != PN532_STARTCODE2:
            return None
        
        # Read length
        length_data = self.uart.read(2)
        if len(length_data) < 2:
            return None
        
        length = length_data[0]
        length_checksum = length_data[1]
        
        if (length + length_checksum) & 0xFF != 0:
            return None
        
        # Read frame data
        frame_data = self.uart.read(length + 1)  # +1 for postamble
        if len(frame_data) < length + 1:
            return None
        
        # Verify checksum
        checksum = frame_data[length - 1]
        data_to_check = frame_data[:length - 1]
        calculated_checksum = self._calculate_checksum(data_to_check)
        
        if checksum != calculated_checksum:
            return None
        
        if self.debug:
            logger.debug(f"Read frame: {[hex(x) for x in frame_data[:-1]]}")
        
        return frame_data[1:length - 1]  # Return data without TFI and checksum
    
    def SAM_configuration(self):
        """Configure SAM (Security Access Module)"""
        self._write_frame([PN532_COMMAND_SAMCONFIGURATION, 0x01, 0x14, 0x01])
        response = self._read_frame()
        return response is not None
    
    def get_firmware_version(self):
        """Get PN532 firmware version"""
        self._write_frame([PN532_COMMAND_GETFIRMWAREVERSION])
        response = self._read_frame()
        if response and len(response) >= 4:
            return {
                'IC': response[0],
                'Ver': response[1],
                'Rev': response[2],
                'Support': response[3]
            }
        return None
    
    def read_passive_target_ID(self, card_baud=0):
        """
        Read passive target (NFC tag) ID
        
        Args:
            card_baud: Card baud rate (0 = 106kbps Type A)
            
        Returns:
            Tuple of (success, uid_bytes) or (False, None)
        """
        # Clear any pending data
        self.uart.reset_input_buffer()
        
        # Send InListPassiveTarget command
        self._write_frame([PN532_COMMAND_INLISTPASSIVETARGET, 0x01, card_baud])
        
        # Read response
        response = self._read_frame(timeout=0.1)
        
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
def PN532_UART_Reader(port='/dev/serial0', baudrate=115200, rst=20, debug=False):
    """
    Create and initialize PN532 UART reader
    
    Returns:
        PN532_UART instance or None if initialization fails
    """
    try:
        reader = PN532_UART(port=port, baudrate=baudrate, rst=rst, debug=debug)
        
        # Test communication
        if not reader.SAM_configuration():
            logger.error("Failed to configure SAM")
            return None
        
        firmware = reader.get_firmware_version()
        if firmware:
            logger.info(f"PN532 Firmware: IC={firmware['IC']}, Ver={firmware['Ver']}, Rev={firmware['Rev']}")
        else:
            logger.warning("Could not read firmware version")
        
        return reader
    
    except Exception as e:
        logger.error(f"Failed to initialize PN532: {e}")
        return None
