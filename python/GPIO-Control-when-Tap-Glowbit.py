"""
This example shows connecting to the PN532 with I2C (requires clock
stretching support), SPI, or UART. SPI is best, it uses the most pins but
is the most reliable and universally supported.
After initialization, try waving various 13.56MHz RFID cards over it and watch it Control the GPIO!
"""

import glowbit

from pn532 import *

import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

matrix = glowbit.matrix4x4()

if __name__ == '__main__':
    try:
        #pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        #pn532 = PN532_I2C(debug=False, reset=20, req=16)
        pn532 = PN532_UART(debug=False, reset=20)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card...')
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=2)
            print('.', end="")
            
            # Try again if no card is available.
            if uid is None:
                
                #Make matrix glow happy lights
                matrix.circularRainbow()
                
                continue
            
            #print('Found card with UID:', [hex(i) for i in uid])
            
            print(uid)
            
            if uid == (b'\x01#Eg'):
            
                #Light Turns On with line dance!
                matrix.lineDemo()
                
            if uid == (b'\x04m\xd3\xd2\xedl\x80'):
            
                #Light Turns On with firework dance!
                matrix.fireworks()     
                
                
           
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()