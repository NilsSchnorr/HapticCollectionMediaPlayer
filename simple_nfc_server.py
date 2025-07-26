#!/usr/bin/env python3
"""
Simple NFC Web Server - No threading version for debugging
"""

from flask import Flask, jsonify
import json
import os
import sys
import time
from datetime import datetime

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the python directory to the path
sys.path.append(os.path.join(BASE_DIR, 'python'))

# Initialize Flask app
app = Flask(__name__)

# Global variables
nfc_reader = None
last_uid = None
last_read_time = None
nfc_available = False

# Try to initialize NFC reader
print("Attempting to initialize NFC reader...")
try:
    import RPi.GPIO as GPIO
    from pn532 import *
    
    nfc_reader = PN532_UART(debug=False, reset=20)
    ic, ver, rev, support = nfc_reader.get_firmware_version()
    print(f'Found PN532 with firmware version: {ver}.{rev}')
    nfc_reader.SAM_configuration()
    nfc_available = True
    print("NFC reader initialized successfully!")
except Exception as e:
    print(f"Could not initialize NFC reader: {e}")
    nfc_available = False

@app.route('/')
def index():
    return '''
    <html>
    <head><title>NFC Test</title></head>
    <body>
        <h1>Simple NFC Test Server</h1>
        <p>NFC Available: <span id="nfc-status">checking...</span></p>
        <p>Last UID: <span id="last-uid">none</span></p>
        <p>Last Read: <span id="last-time">never</span></p>
        <button onclick="checkNFC()">Check NFC Now</button>
        <script>
            function updateStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('nfc-status').textContent = data.nfc_available;
                        document.getElementById('last-uid').textContent = data.last_uid || 'none';
                        document.getElementById('last-time').textContent = data.last_read_time || 'never';
                    });
            }
            
            function checkNFC() {
                fetch('/api/read_once')
                    .then(r => r.json())
                    .then(data => {
                        alert(data.status + (data.uid ? ': ' + data.uid : ''));
                        updateStatus();
                    });
            }
            
            setInterval(updateStatus, 2000);
            updateStatus();
        </script>
    </body>
    </html>
    '''

@app.route('/api/status')
def get_status():
    """Get current NFC status"""
    return jsonify({
        'nfc_available': nfc_available,
        'last_uid': last_uid,
        'last_read_time': last_read_time
    })

@app.route('/api/read_once')
def read_once():
    """Try to read NFC once"""
    global last_uid, last_read_time
    
    if not nfc_available:
        return jsonify({'status': 'NFC not available', 'uid': None})
    
    try:
        # Try to read for up to 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            uid = nfc_reader.read_passive_target(timeout=0.5)
            if uid:
                uid_hex = ''.join([format(b, '02x') for b in uid])
                last_uid = uid_hex
                last_read_time = datetime.now().isoformat()
                return jsonify({'status': 'Card detected', 'uid': uid_hex})
        
        return jsonify({'status': 'No card detected', 'uid': None})
    except Exception as e:
        return jsonify({'status': f'Error: {str(e)}', 'uid': None})

if __name__ == '__main__':
    print("\nStarting Simple NFC Test Server...")
    print("Access at: http://localhost:5000")
    print("This version does NOT use threading\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
