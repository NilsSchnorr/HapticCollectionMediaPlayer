#!/usr/bin/env python3
"""
PN532 UART Library - Working Implementation
Based on successful NFC-Player that actually works
Uses /dev/ttyS0, proper wake-up sequence, and retry mechanism
"""

import time
import serial
import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)

# Working configuration from successful NFC-Player
DEFAULT_UART_PORT = '/dev/ttyS0'  # Key: use ttyS0, not ttyAMA0
DEFAULT_BAUDRATE = 115200
DEFAULT_RESET_PIN = 20

# PN532 Commands
CMD_GETFIRMWAREVERSION = 0x02
CMD_SAMCONFIGURATION = 0x14
CMD_INLISTPASSIVETARGET = 0x4A

# Frame constants
PREAMBLE = 0x00
STARTCODE1 = 0x00
STARTCODE2 = 0xFF
POSTAMBLE = 0x00
HOSTTOPN532 = 0xD4
PN532TOHOST = 0xD5

class PN532WorkingUART:
    """PN532 UART implementation using working NFC-Player approach"""
    
    def __init__(self, port=DEFAULT_UART_PORT, baudrate=DEFAULT_BAUDRATE, 
                 reset_pin=DEFAULT_RESET_PIN, debug=False):
        """Initialize PN532 using working approach"""
        self.port = port
        self.baudrate = baudrate
        self.reset_pin = reset_pin
        self.debug = debug
        self.uart = None
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.reset_pin, GPIO.OUT)
        GPIO.output(self.reset_pin, True)
        
        # Initialize UART
        self._init_uart()
        
        # Reset and wake up (with retry like working player)
        self._reset_and_init()
    
    def _init_uart(self):
        """Initialize UART connection"""
        try:
            self.uart = serial.Serial(self.port, self.baudrate, timeout=1)
            if not self.uart.is_open:
                raise RuntimeError(f'Cannot open {self.port}')
            if self.debug:
                logger.info(f"UART opened: {self.port} at {self.baudrate} baud")
        except Exception as e:
            logger.error(f"Failed to initialize UART: {e}")
            raise
    
    def _reset_and_init(self):
        """Reset and initialize with retry (like working player)"""
        if self.debug:
            logger.info("Resetting and initializing PN532...")
        
        # Hardware reset with working timing
        self._hardware_reset()
        
        # Try initialization twice (like working player)
        for attempt in range(2):
            try:
                self._wakeup()
                self.get_firmware_version()
                if self.debug:
                    logger.info(f"PN532 initialized successfully (attempt {attempt + 1})")
                return
            except Exception as e:
                if attempt == 0:
                    if self.debug:
                        logger.warning(f"First attempt failed: {e}, retrying...")
                    continue
                else:
                    logger.error(f"Both initialization attempts failed: {e}")
                    raise RuntimeError("Failed to initialize PN532")
    
    def _hardware_reset(self):
        """Hardware reset with working player's timing"""
        GPIO.output(self.reset_pin, True)
        time.sleep(0.1)
        GPIO.output(self.reset_pin, False)
        time.sleep(0.5)  # Longer reset (key difference)
        GPIO.output(self.reset_pin, True)
        time.sleep(0.1)
        
        if self.debug:
            logger.debug("Hardware reset completed")
    
    def _wakeup(self):
        """Send wake-up sequence exactly like working player"""
        if self.debug:
            logger.debug("Sending wake-up sequence...")
        
        # Exact wake-up from working NFC-Player
        wake_sequence = b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.uart.write(wake_sequence)
        time.sleep(0.1)
        
        # Configure SAM as part of wake-up
        self.sam_configuration()
    
    def _wait_ready(self, timeout=0.001):
        """Wait for response"""
        start_time = time.monotonic()
        while (time.monotonic() - start_time) < timeout:
            if self.uart.in_waiting:
                return True
            time.sleep(0.05)
        return False
    
    def _read_data(self, count):
        """Read data from UART"""
        data = self.uart.read(min(self.uart.in_waiting, count))
        if not data:
            raise RuntimeError("No data read from PN532")
        if self.debug:
            logger.debug(f"Read: {[hex(i) for i in data]}")
        else:
            time.sleep(0.005)
        return data
    
    def _write_data(self, data):
        """Write data to UART (clear buffer first like working player)"""
        self.uart.read(self.uart.in_waiting)  # Clear FIFO
        self.uart.write(data)
    
    def _write_frame(self, data):
        """Write PN532 frame"""
        if len(data) < 1 or len(data) > 254:
            raise ValueError('Data must be 1-254 bytes')
        
        length = len(data)
        frame = bytearray(length + 7)
        
        # Build frame
        frame[0] = PREAMBLE
        frame[1] = STARTCODE1
        frame[2] = STARTCODE2
        frame[3] = length & 0xFF
        frame[4] = (~length + 1) & 0xFF
        frame[5:-2] = data
        
        # Calculate checksum
        checksum = sum(data)
        frame[-2] = ~checksum & 0xFF
        frame[-1] = POSTAMBLE
        
        if self.debug:
            logger.debug(f"Write frame: {[hex(i) for i in frame]}")
        
        self._write_data(bytes(frame))
    
    def _read_frame(self, expected_length):
        """Read PN532 response frame"""
        response = self._read_data(expected_length + 7)
        
        if self.debug:
            logger.debug(f"Read frame: {[hex(i) for i in response]}")
        
        # Find frame start
        offset = 0
        while offset < len(response) and response[offset] == 0x00:
            offset += 1
        
        if offset >= len(response) or response[offset] != 0xFF:
            raise RuntimeError('Invalid frame preamble')
        
        offset += 1
        if offset >= len(response):
            raise RuntimeError('Frame too short')
        
        # Get length and verify checksum
        frame_len = response[offset]
        if (frame_len + response[offset + 1]) & 0xFF != 0:
            raise RuntimeError('Length checksum error')
        
        # Verify data checksum
        checksum = sum(response[offset + 2:offset + 2 + frame_len + 1]) & 0xFF
        if checksum != 0:
            raise RuntimeError('Data checksum error')
        
        return response[offset + 2:offset + 2 + frame_len]
    
    def call_function(self, command, params=None, response_length=0, timeout=1):
        """Call PN532 function"""
        if params is None:
            params = []
        
        # Build command
        data = bytearray(2 + len(params))
        data[0] = HOSTTOPN532
        data[1] = command & 0xFF
        for i, param in enumerate(params):
            data[2 + i] = param
        
        # Send command
        try:
            self._write_frame(data)
        except OSError:
            self._wakeup()
            return None
        
        # Wait for response
        if not self._wait_ready(timeout):
            return None
        
        # Read ACK
        ack = b'\x00\x00\xFF\x00\xFF\x00'
        if self._read_data(len(ack)) != ack:
            raise RuntimeError('No ACK received')
        
        if not self._wait_ready(timeout):
            return None
        
        # Read response
        response = self._read_frame(response_length + 2)
        
        # Verify response
        if len(response) < 2 or response[0] != PN532TOHOST or response[1] != (command + 1):
            raise RuntimeError('Invalid response')
        
        return response[2:]
    
    def get_firmware_version(self):
        """Get firmware version"""
        response = self.call_function(CMD_GETFIRMWAREVERSION, response_length=4, timeout=0.5)
        if response is None:
            raise RuntimeError('Failed to get firmware version')
        return tuple(response)
    
    def sam_configuration(self):
        """Configure SAM"""
        self.call_function(CMD_SAMCONFIGURATION, params=[0x01, 0x14, 0x01])
        if self.debug:
            logger.debug("SAM configuration completed")
    
    def read_passive_target(self, timeout=0.1):
        """Read passive target (NFC tag)"""
        try:
            # Clear input buffer
            self.uart.reset_input_buffer()
            
            # Send command
            response = self.call_function(
                CMD_INLISTPASSIVETARGET,
                params=[0x01, 0x00],  # 1 card, 106kbps Type A
                response_length=19,
                timeout=timeout
            )
            
            if not response or len(response) < 2:
                return None
            
            # Check if tag found
            if response[0] != 0x01:
                return None
            
            # Extract UID
            if len(response) < 7:
                return None
            
            uid_length = response[5]
            if len(response) < 6 + uid_length:
                return None
            
            uid = response[6:6 + uid_length]
            
            if self.debug:
                uid_hex = ':'.join([f'{b:02X}' for b in uid])
                logger.debug(f"Tag detected: {uid_hex}")
            
            return uid
            
        except Exception as e:
            if "timeout" not in str(e).lower() and self.debug:
                logger.debug(f"Read error: {e}")
            return None
    
    def close(self):
        """Clean up resources"""
        try:
            if self.uart:
                self.uart.close()
        except:
            pass
        
        try:
            GPIO.cleanup()
        except:
            pass
        
        if self.debug:
            logger.info("PN532 closed")

def create_pn532_reader(port=DEFAULT_UART_PORT, baudrate=DEFAULT_BAUDRATE, 
                       reset_pin=DEFAULT_RESET_PIN, debug=False):
    """Factory function to create PN532 reader"""
    try:
        reader = PN532WorkingUART(port=port, baudrate=baudrate, 
                                 reset_pin=reset_pin, debug=debug)
        
        # Test by getting firmware version
        firmware = reader.get_firmware_version()
        ic, ver, rev, support = firmware
        logger.info(f"PN532 Firmware: {ver}.{rev}[{ic}.{support}]")
        
        return reader
        
    except Exception as e:
        logger.error(f"Failed to create PN532 reader: {e}")
        return None
