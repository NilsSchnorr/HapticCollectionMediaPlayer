#!/usr/bin/env python3
"""
NFC Display System - Shows home base and switches to mapped HTML when chip detected
"""

from flask import Flask, render_template_string, jsonify, send_from_directory
import json
import os
import sys
import time
from datetime import datetime
import threading

# Add the python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

# Initialize NFC reader
nfc_reader = None
nfc_available = False
current_uid = None
current_html = None

print("Initializing NFC Display System...")
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

# Flask app
app = Flask(__name__)

# Load mappings
def load_mappings():
    if os.path.exists('nfc_mappings.json'):
        with open('nfc_mappings.json', 'r') as f:
            return json.load(f)
    return {}

# NFC reading thread
def nfc_reader_thread():
    global current_uid, current_html
    
    if not nfc_available:
        return
    
    print("NFC monitoring started...")
    mappings = load_mappings()
    last_reload = time.time()
    
    while True:
        try:
            # Reload mappings every 10 seconds
            if time.time() - last_reload > 10:
                mappings = load_mappings()
                last_reload = time.time()
            
            # Read NFC
            uid = nfc_reader.read_passive_target(timeout=0.5)
            
            if uid:
                uid_hex = ''.join([format(i, '02x') for i in uid])
                if uid_hex != current_uid:
                    current_uid = uid_hex
                    print(f"Chip detected: {uid_hex}")
                    
                    # Check mapping
                    if uid_hex in mappings:
                        current_html = mappings[uid_hex]['html_file']
                        print(f"Mapped to: {current_html}")
                    else:
                        current_html = None
                        print("No mapping found")
            else:
                if current_uid:
                    print("Chip removed")
                current_uid = None
                current_html = None
                
        except Exception as e:
            print(f"Error in NFC thread: {e}")
            time.sleep(1)

# Main display page
DISPLAY_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haptic Collection Media Player</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #0a0a0a;
            color: #ffffff;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
        }
        
        #homeBase {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background: radial-gradient(ellipse at center, #1a1a2e 0%, #0a0a0a 100%);
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .title {
            font-size: clamp(2rem, 6vw, 4rem);
            font-weight: 300;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 3rem;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .prompt {
            font-size: 1.5rem;
            opacity: 0.8;
            margin-bottom: 4rem;
            text-align: center;
        }
        
        .nfc-icon {
            width: 120px;
            height: 120px;
            position: relative;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.8; }
            50% { transform: scale(1.1); opacity: 1; }
        }
        
        .nfc-icon svg {
            width: 100%;
            height: 100%;
        }
        
        .status {
            margin-top: 2rem;
            font-size: 1.1rem;
            opacity: 0.6;
        }
        
        #contentFrame {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
            display: none;
            background: white;
        }
        
        .loading {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            display: none;
            z-index: 1000;
            background: rgba(0,0,0,0.8);
            padding: 2rem;
            border-radius: 10px;
        }
        
        .debug {
            position: fixed;
            bottom: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.8rem;
            opacity: 0.5;
        }
    </style>
</head>
<body>
    <div id="homeBase">
        <h1 class="title">Haptic Collection<br>Media Player</h1>
        <p class="prompt">Place an object on the reader to begin</p>
        <div class="nfc-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="currentColor" opacity="0.3"/>
                <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" fill="currentColor" opacity="0.5"/>
                <path d="M12 10c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" fill="currentColor"/>
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1" fill="none" opacity="0.2">
                    <animate attributeName="r" values="10;12;10" dur="2s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.2;0.4;0.2" dur="2s" repeatCount="indefinite"/>
                </circle>
            </svg>
        </div>
        <p class="status" id="status">Waiting for NFC chip...</p>
    </div>
    
    <iframe id="contentFrame" src=""></iframe>
    <div class="loading" id="loading">Loading content...</div>
    <div class="debug" id="debug"></div>
    
    <script>
        let currentUID = null;
        let checkInterval;
        let isShowingContent = false;
        
        async function checkNFC() {
            try {
                const response = await fetch('/api/nfc_status');
                const data = await response.json();
                
                document.getElementById('debug').textContent = `NFC: ${data.uid || 'none'} | HTML: ${data.html || 'none'}`;
                
                if (data.uid && data.html && data.uid !== currentUID) {
                    // New chip detected with mapping
                    currentUID = data.uid;
                    showContent(data.html);
                } else if (!data.uid && isShowingContent) {
                    // Chip removed
                    currentUID = null;
                    showHomeBase();
                } else if (data.uid && !data.html) {
                    // Unmapped chip
                    document.getElementById('status').textContent = `Unknown chip: ${data.uid}`;
                } else if (!data.uid) {
                    document.getElementById('status').textContent = 'Waiting for NFC chip...';
                }
            } catch (error) {
                console.error('Error checking NFC:', error);
            }
        }
        
        function showContent(htmlFile) {
            console.log('Showing content:', htmlFile);
            isShowingContent = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('homeBase').style.display = 'none';
            
            const iframe = document.getElementById('contentFrame');
            iframe.src = `/content/${htmlFile}`;
            iframe.style.display = 'block';
            
            iframe.onload = () => {
                document.getElementById('loading').style.display = 'none';
            };
        }
        
        function showHomeBase() {
            console.log('Returning to home base');
            isShowingContent = false;
            document.getElementById('homeBase').style.display = 'flex';
            document.getElementById('contentFrame').style.display = 'none';
            document.getElementById('contentFrame').src = '';
            document.getElementById('loading').style.display = 'none';
        }
        
        // Start checking for NFC
        checkInterval = setInterval(checkNFC, 500);
        
        // Handle visibility change to stop/start polling
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                clearInterval(checkInterval);
            } else {
                checkInterval = setInterval(checkNFC, 500);
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(DISPLAY_HTML)

@app.route('/api/nfc_status')
def nfc_status():
    """Return current NFC status"""
    return jsonify({
        'uid': current_uid,
        'html': current_html,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/content/<path:filename>')
def serve_content(filename):
    """Serve HTML content files"""
    return send_from_directory('html_content', filename)

if __name__ == '__main__':
    # Start NFC reader thread if available
    if nfc_available:
        reader_thread = threading.Thread(target=nfc_reader_thread, daemon=True)
        reader_thread.start()
    
    print("\n" + "="*50)
    print("NFC Display System Started")
    print("="*50)
    print("Access at: http://localhost:8080")
    print("This runs on port 8080 (not 5000)")
    print("="*50)
    
    # Run on different port to avoid conflict with management interface
    app.run(host='0.0.0.0', port=8080, debug=False)
