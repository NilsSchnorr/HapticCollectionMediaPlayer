#!/usr/bin/env python3
"""
Demo version of NFC Display - Works without NFC hardware
Use keyboard keys 1-5 to simulate different NFC chips
"""

from flask import Flask, render_template_string, jsonify, send_from_directory
import json
import os
import sys
from datetime import datetime
import threading

# Flask app
app = Flask(__name__)

# Simulated NFC state
current_uid = None
current_html = None
demo_mappings = {
    "demo_chip_1": {"html_file": "welcome.html", "description": "Welcome Card"},
    "demo_chip_2": {"html_file": "gallery.html", "description": "Gallery Card"},
    "demo_chip_3": {"html_file": "sample.html", "description": "Sample Card"}
}

# Save demo mappings if no mappings exist
if not os.path.exists('nfc_mappings.json'):
    with open('nfc_mappings.json', 'w') as f:
        json.dump(demo_mappings, f, indent=2)
    print("Created demo mappings")

# Load mappings
def load_mappings():
    if os.path.exists('nfc_mappings.json'):
        with open('nfc_mappings.json', 'r') as f:
            return json.load(f)
    return {}

# Main display page (same as nfc_display.py but with demo controls)
DISPLAY_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haptic Collection Media Player - Demo Mode</title>
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
        
        .demo-controls {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            padding: 15px 20px;
            border-radius: 10px;
            display: flex;
            gap: 10px;
            z-index: 1001;
        }
        
        .demo-btn {
            padding: 8px 16px;
            background: #4a5568;
            border: none;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s;
        }
        
        .demo-btn:hover {
            background: #667eea;
            transform: translateY(-2px);
        }
        
        .demo-btn.active {
            background: #667eea;
        }
        
        .demo-info {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(255,165,0,0.9);
            color: black;
            padding: 8px 16px;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="demo-info">DEMO MODE</div>
    
    <div id="homeBase">
        <h1 class="title">Haptic Collection<br>Media Player</h1>
        <p class="prompt">Demo Mode - Click buttons below to simulate NFC chips</p>
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
        <p class="status" id="status">Click a demo chip button below</p>
    </div>
    
    <iframe id="contentFrame" src=""></iframe>
    <div class="loading" id="loading">Loading content...</div>
    
    <div class="demo-controls" id="demoControls">
        <button class="demo-btn" onclick="simulateChip('demo_chip_1')">Chip 1</button>
        <button class="demo-btn" onclick="simulateChip('demo_chip_2')">Chip 2</button>
        <button class="demo-btn" onclick="simulateChip('demo_chip_3')">Chip 3</button>
        <button class="demo-btn" onclick="removeChip()">Remove Chip</button>
    </div>
    
    <script>
        let currentUID = null;
        let checkInterval;
        let isShowingContent = false;
        
        async function checkNFC() {
            try {
                const response = await fetch('/api/nfc_status');
                const data = await response.json();
                
                if (data.uid && data.html && data.uid !== currentUID) {
                    // New chip detected with mapping
                    currentUID = data.uid;
                    showContent(data.html);
                    highlightButton(data.uid);
                } else if (!data.uid && isShowingContent) {
                    // Chip removed
                    currentUID = null;
                    showHomeBase();
                    highlightButton(null);
                } else if (data.uid && !data.html) {
                    // Unmapped chip
                    document.getElementById('status').textContent = `Unknown chip: ${data.uid}`;
                } else if (!data.uid) {
                    document.getElementById('status').textContent = 'Click a demo chip button below';
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
            document.getElementById('demoControls').style.opacity = '0.5';
            
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
            document.getElementById('demoControls').style.opacity = '1';
        }
        
        function simulateChip(chipId) {
            fetch(`/api/simulate/${chipId}`, { method: 'POST' });
        }
        
        function removeChip() {
            fetch('/api/simulate/remove', { method: 'POST' });
        }
        
        function highlightButton(chipId) {
            document.querySelectorAll('.demo-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            if (chipId) {
                const buttons = document.querySelectorAll('.demo-btn');
                if (chipId === 'demo_chip_1') buttons[0].classList.add('active');
                else if (chipId === 'demo_chip_2') buttons[1].classList.add('active');
                else if (chipId === 'demo_chip_3') buttons[2].classList.add('active');
            }
        }
        
        // Start checking for NFC
        checkInterval = setInterval(checkNFC, 500);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === '1') simulateChip('demo_chip_1');
            else if (e.key === '2') simulateChip('demo_chip_2');
            else if (e.key === '3') simulateChip('demo_chip_3');
            else if (e.key === '0' || e.key === 'Escape') removeChip();
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
    global current_uid, current_html
    
    # In demo mode, check mappings each time
    if current_uid:
        mappings = load_mappings()
        if current_uid in mappings:
            current_html = mappings[current_uid]['html_file']
        else:
            current_html = None
    
    return jsonify({
        'uid': current_uid,
        'html': current_html,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/simulate/<chip_id>', methods=['POST'])
def simulate_chip(chip_id):
    """Simulate placing an NFC chip"""
    global current_uid
    current_uid = chip_id
    print(f"Simulated chip placed: {chip_id}")
    return jsonify({'success': True})

@app.route('/api/simulate/remove', methods=['POST'])
def simulate_remove():
    """Simulate removing NFC chip"""
    global current_uid, current_html
    current_uid = None
    current_html = None
    print("Simulated chip removed")
    return jsonify({'success': True})

@app.route('/content/<path:filename>')
def serve_content(filename):
    """Serve HTML content files"""
    return send_from_directory('html_content', filename)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("NFC Display System - DEMO MODE")
    print("="*50)
    print("No NFC hardware required!")
    print("")
    print("Access at: http://localhost:8080")
    print("")
    print("Controls:")
    print("  Click buttons or use keyboard:")
    print("  1 = Chip 1 (Welcome)")
    print("  2 = Chip 2 (Gallery)")  
    print("  3 = Chip 3 (Sample)")
    print("  0/ESC = Remove chip")
    print("="*50)
    
    # Ensure html_content directory exists
    os.makedirs('html_content', exist_ok=True)
    
    # Run on port 8080
    app.run(host='0.0.0.0', port=8080, debug=False)
