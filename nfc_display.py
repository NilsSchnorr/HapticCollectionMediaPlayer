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
import signal
import atexit

# Add the python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

# ---------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------
def load_config():
    """Read config.json from the working directory. Returns {} on any problem."""
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Could not read config.json: {e}")
    return {}

CONFIG = load_config()

# How many consecutive failed reads before the chip counts as removed.
# One read cycle takes ~0.5s, so 3 reads = roughly 1.5s grace period.
# This keeps short read blips (marginal coupling, a visitor nudging the
# object) from interrupting the content, while a deliberate removal
# still registers quickly.
REMOVAL_GRACE_READS = max(1, int(CONFIG.get('removal_grace_reads', 3)))

# Startup / recovery tuning
INIT_MAX_ATTEMPTS = 5        # PN532 init attempts at startup
INIT_RETRY_DELAY = 3         # seconds between startup init attempts
REINIT_ERROR_THRESHOLD = 10  # consecutive read errors before re-init
REINIT_MAX_ATTEMPTS = 3      # re-init attempts before giving up
REINIT_RETRY_DELAY = 2       # seconds between re-init attempts

# ---------------------------------------------------------------
# NFC reader state
# ---------------------------------------------------------------
nfc_reader = None
nfc_available = False
current_uid = None
current_html = None
is_reading = False
last_successful_read = None   # time.time() of the last error-free read cycle
consecutive_read_errors = 0   # updated by the reader thread
_cleanup_done = False

# Hardware libraries are only present on the Pi. If they are missing we
# are on a development machine: run web-only and never exit because of
# the missing reader.
ON_PI = False
try:
    import RPi.GPIO as GPIO
    from pn532 import *
    import serial
    ON_PI = True
except Exception as e:
    print(f"Hardware libraries not available ({e}).")
    print("Running in development mode without NFC reader.")

def cleanup_nfc():
    """Clean up NFC reader, serial port, and GPIO on exit."""
    global nfc_reader, nfc_available, is_reading, _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True

    print("Cleaning up NFC reader...")
    is_reading = False

    if nfc_reader is not None:
        try:
            if hasattr(nfc_reader, '_uart') and nfc_reader._uart is not None:
                if nfc_reader._uart.is_open:
                    nfc_reader._uart.close()
                    print("Serial port closed.")
        except Exception as e:
            print(f"Error closing serial port: {e}")
        nfc_reader = None
        nfc_available = False

    try:
        import RPi.GPIO as GPIO
        GPIO.cleanup()
        print("GPIO cleaned up.")
    except Exception:
        pass

def signal_handler(signum, frame):
    """Handle termination signals for clean shutdown."""
    print(f"\nReceived signal {signum}, shutting down...")
    cleanup_nfc()
    sys.exit(0)

# Register cleanup handlers
atexit.register(cleanup_nfc)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# ---------------------------------------------------------------
# NFC reader initialization (with retries and runtime recovery)
# ---------------------------------------------------------------
def _close_reader():
    """Close the current reader's serial port, if any."""
    global nfc_reader
    if nfc_reader is not None:
        try:
            if hasattr(nfc_reader, '_uart') and nfc_reader._uart is not None:
                if nfc_reader._uart.is_open:
                    nfc_reader._uart.close()
        except Exception:
            pass
    nfc_reader = None

def _hw_init_once():
    """One attempt to open and configure the PN532. Raises on failure."""
    global nfc_reader

    # Force-close any leftover serial connection from a previous run
    try:
        _tmp_serial = serial.Serial('/dev/ttyS0', 115200)
        _tmp_serial.reset_input_buffer()
        _tmp_serial.reset_output_buffer()
        _tmp_serial.close()
        time.sleep(0.1)
        print("Cleared previous serial connection.")
    except Exception:
        pass

    nfc_reader = PN532_UART(debug=False, reset=20)
    ic, ver, rev, support = nfc_reader.get_firmware_version()
    print(f'Found PN532 with firmware version: {ver}.{rev}')
    nfc_reader.SAM_configuration()

def init_nfc(max_attempts=INIT_MAX_ATTEMPTS, delay=INIT_RETRY_DELAY):
    """Initialize the PN532 with retries. Returns True on success.

    Used both at startup and for runtime recovery after repeated
    read errors.
    """
    global nfc_available
    for attempt in range(1, max_attempts + 1):
        try:
            _close_reader()
            _hw_init_once()
            nfc_available = True
            print("NFC reader initialized successfully!")
            return True
        except Exception as e:
            print(f"NFC init attempt {attempt}/{max_attempts} failed: {e}")
            if attempt < max_attempts:
                time.sleep(delay)
    nfc_available = False
    return False

print("Initializing NFC Display System...")
if ON_PI:
    if not init_nfc():
        # On the Pi a missing reader is a hard failure: exit non-zero so
        # systemd (Restart=always, RestartSec=10) keeps retrying until
        # the reader is available - e.g. after a cold boot where the
        # reader powers up slowly, or after nfc_web_server.py releases
        # the serial port.
        print(f"FATAL: Could not initialize NFC reader after {INIT_MAX_ATTEMPTS} attempts.")
        print("Exiting so systemd can restart the service.")
        print("If you are running manually, check that the reader is connected")
        print("and that nothing else holds /dev/ttyS0 (e.g. nfc_web_server.py).")
        cleanup_nfc()
        sys.exit(1)

# Flask app
app = Flask(__name__)

# Load mappings
def load_mappings():
    if os.path.exists('nfc_mappings.json'):
        with open('nfc_mappings.json', 'r') as f:
            return json.load(f)
    return {}

# Resolve which idle/home screen this installation shows.
# Order: HCMP_HOME_SCREEN env var -> config.json "home_screen" -> built-in default.
# Falls back to the built-in screen if the configured file is missing.
def resolve_home_screen():
    candidate = os.environ.get('HCMP_HOME_SCREEN')
    if not candidate:
        candidate = CONFIG.get('home_screen')
    candidate = (candidate or '').strip()
    if candidate and os.path.exists(os.path.join('html_content', candidate)):
        print(f"Home screen: {candidate}")
        return candidate
    if candidate:
        print(f"Configured home screen '{candidate}' not found in html_content/, using built-in default.")
    else:
        print("No custom home screen configured, using built-in default.")
    return None

HOME_FILE = resolve_home_screen()

# NFC reading thread
def nfc_reader_thread():
    global current_uid, current_html, is_reading
    global last_successful_read, consecutive_read_errors

    if not nfc_available:
        return

    print(f"NFC monitoring started (removal grace: {REMOVAL_GRACE_READS} reads)...")
    is_reading = True
    mappings = load_mappings()
    last_reload = time.time()
    missed_reads = 0

    while is_reading:
        try:
            # Reload mappings every 10 seconds
            if time.time() - last_reload > 10:
                mappings = load_mappings()
                last_reload = time.time()

            # Read NFC
            uid = nfc_reader.read_passive_target(timeout=0.5)

            # The read cycle itself worked (whether or not a chip is present)
            consecutive_read_errors = 0
            last_successful_read = time.time()

            if uid:
                missed_reads = 0
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
                # No chip seen this cycle. Only treat the chip as removed
                # after REMOVAL_GRACE_READS consecutive misses, so short
                # read blips don't interrupt the content.
                if current_uid:
                    missed_reads += 1
                    if missed_reads >= REMOVAL_GRACE_READS:
                        print("Chip removed")
                        current_uid = None
                        current_html = None
                        missed_reads = 0
                else:
                    missed_reads = 0

        except Exception as e:
            consecutive_read_errors += 1
            print(f"Error in NFC thread ({consecutive_read_errors} in a row): {e}")

            if consecutive_read_errors >= REINIT_ERROR_THRESHOLD:
                print("Too many consecutive read errors - attempting to re-initialize the NFC reader...")
                if init_nfc(max_attempts=REINIT_MAX_ATTEMPTS, delay=REINIT_RETRY_DELAY):
                    print("NFC reader recovered.")
                    consecutive_read_errors = 0
                    # Re-init interrupts reading; start fresh.
                    current_uid = None
                    current_html = None
                    missed_reads = 0
                else:
                    # Recovery failed: exit the whole process (non-zero) so
                    # systemd restarts the service cleanly.
                    print("FATAL: NFC reader re-initialization failed.")
                    print("Exiting so systemd can restart the service.")
                    cleanup_nfc()
                    os._exit(1)
            else:
                time.sleep(1)

    print("NFC reader thread stopped.")

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
            left: 10px;
            background: rgba(0,0,0,0.8);
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.8rem;
            opacity: 0.5;
            pointer-events: none;
            transition: opacity 0.8s ease;
        }
        
        .debug.hidden {
            opacity: 0;
        }
    </style>
</head>
<body>
    <div id="homeBase"{% if home_file %} style="display: none;"{% endif %}>
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
    
    <iframe id="contentFrame" src="{% if home_file %}/content/{{ home_file }}{% endif %}"{% if home_file %} style="display: block;"{% endif %}></iframe>
    <div class="loading" id="loading">Loading content...</div>
    <div class="debug" id="debug"></div>
    
    <script>
        let currentUID = null;
        let checkInterval;
        let isShowingContent = false;
        let debugHideTimer = null;
        const HOME_FILE = {{ home_file | tojson }};
        
        function showDebugBanner() {
            const debugEl = document.getElementById('debug');
            debugEl.classList.remove('hidden');
            if (debugHideTimer) clearTimeout(debugHideTimer);
            debugHideTimer = setTimeout(() => {
                debugEl.classList.add('hidden');
            }, 10000);
        }
        
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
            showDebugBanner();
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
            showDebugBanner();
            const iframe = document.getElementById('contentFrame');
            if (HOME_FILE) {
                document.getElementById('homeBase').style.display = 'none';
                const homeSrc = '/content/' + HOME_FILE;
                if (!iframe.src.endsWith(homeSrc)) iframe.src = homeSrc;
                iframe.style.display = 'block';
            } else {
                document.getElementById('homeBase').style.display = 'flex';
                iframe.style.display = 'none';
                iframe.src = '';
            }
            document.getElementById('loading').style.display = 'none';
        }
        
        // Start checking for NFC
        showDebugBanner();
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
    return render_template_string(DISPLAY_HTML, home_file=HOME_FILE)

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
