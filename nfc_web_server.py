#!/usr/bin/env python3
"""
NFC Web Server for HapticCollectionMediaPlayer
This server provides a web interface to map NFC chips to HTML files
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
import threading
import time
from datetime import datetime
import sys

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the python directory to the path so we can import pn532
sys.path.append(os.path.join(BASE_DIR, 'python'))

# Initialize NFC reader at module level (like the working simple server)
nfc_reader = None
nfc_available = False

print("Attempting to initialize NFC reader...")
try:
    import RPi.GPIO as GPIO
    from pn532 import *  # Use same import as working example
    
    nfc_reader = PN532_UART(debug=False, reset=20)
    ic, ver, rev, support = nfc_reader.get_firmware_version()
    print(f'Found PN532 with firmware version: {ver}.{rev}')
    nfc_reader.SAM_configuration()
    nfc_available = True
    print("NFC reader initialized successfully!")
except Exception as e:
    print(f"Could not initialize NFC reader: {e}")
    print("Running in development mode without NFC reader")
    nfc_available = False

# Initialize Flask app
app = Flask(__name__, static_folder='web_interface', template_folder='web_interface')

# Global variables
current_uid = None
is_reading = False
mappings_file = os.path.join(BASE_DIR, "nfc_mappings.json")

# Load or create mappings file
def load_mappings():
    if os.path.exists(mappings_file):
        with open(mappings_file, 'r') as f:
            return json.load(f)
    return {}

def save_mappings(mappings):
    with open(mappings_file, 'w') as f:
        json.dump(mappings, f, indent=2)

# Background thread to continuously read NFC tags
def nfc_reader_thread():
    global current_uid, is_reading
    
    if not nfc_available:
        print("NFC reader not available, skipping reader thread")
        return
    
    print("Starting NFC reader thread...")
    is_reading = True
    read_count = 0
    
    while is_reading:
        try:
            # Print debug every 10 reads
            read_count += 1
            if read_count % 10 == 0:
                print(f"NFC reader thread active, attempts: {read_count}")
            
            # Check if a card is available to read
            uid = nfc_reader.read_passive_target(timeout=0.5)
            
            if uid is not None:
                # Convert UID to hex string
                uid_hex = ''.join([format(i, '02x') for i in uid])
                current_uid = uid_hex
                print(f"Detected NFC chip with UID: {uid_hex}")
                # Wait a bit before reading again to avoid multiple reads
                time.sleep(2)
            else:
                current_uid = None
                
        except Exception as e:
            print(f"Error reading NFC: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(1)

# Routes
@app.route('/')
def index():
    return send_from_directory('web_interface', 'index.html')

@app.route('/api/current_nfc')
def get_current_nfc():
    """Get the currently detected NFC chip UID"""
    return jsonify({
        'uid': current_uid,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/mappings')
def get_mappings():
    """Get all NFC to HTML mappings"""
    mappings = load_mappings()
    return jsonify(mappings)

@app.route('/api/mapping', methods=['POST'])
def save_mapping():
    """Save a new NFC to HTML mapping"""
    data = request.json
    uid = data.get('uid')
    html_file = data.get('html_file')
    description = data.get('description', '')
    
    if not uid or not html_file:
        return jsonify({'error': 'UID and HTML file are required'}), 400
    
    mappings = load_mappings()
    mappings[uid] = {
        'html_file': html_file,
        'description': description,
        'created': datetime.now().isoformat()
    }
    save_mappings(mappings)
    
    return jsonify({'success': True, 'message': 'Mapping saved successfully'})

@app.route('/api/mapping/<uid>', methods=['DELETE'])
def delete_mapping(uid):
    """Delete an NFC to HTML mapping"""
    mappings = load_mappings()
    if uid in mappings:
        del mappings[uid]
        save_mappings(mappings)
        return jsonify({'success': True, 'message': 'Mapping deleted successfully'})
    return jsonify({'error': 'Mapping not found'}), 404

@app.route('/api/html_files')
def list_html_files():
    """List all HTML files in the html_content directory"""
    html_dir = os.path.join(BASE_DIR, 'html_content')
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
        # Create a sample HTML file
        sample_path = os.path.join(html_dir, 'sample.html')
        with open(sample_path, 'w') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Sample Content</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Sample Content</h1>
    <p>This is a sample HTML file that can be associated with an NFC chip.</p>
    <p>Place your custom HTML files in the 'html_content' directory.</p>
</body>
</html>""")
    
    html_files = []
    for file in os.listdir(html_dir):
        if file.endswith('.html'):
            html_files.append(file)
    
    return jsonify(html_files)

@app.route('/api/test_nfc/<uid>')
def test_nfc(uid):
    """Test endpoint to simulate NFC detection (for development)"""
    global current_uid
    current_uid = uid
    return jsonify({'success': True, 'uid': uid})

if __name__ == '__main__':
    # Start NFC reader thread if available
    if nfc_available:
        reader_thread = threading.Thread(target=nfc_reader_thread, daemon=True)
        reader_thread.start()
    
    # Create necessary directories
    os.makedirs(os.path.join(BASE_DIR, 'html_content'), exist_ok=True)
    
    print("Starting NFC Web Server...")
    print("Access the interface at: http://localhost:5000")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
