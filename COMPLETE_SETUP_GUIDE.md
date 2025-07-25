# 🚀 Complete NFC Media Player Setup Guide
## Fresh Raspberry Pi OS Installation

This guide will take you from a fresh Raspberry Pi OS installation to a working NFC media player.

---

## 📋 **Step 1: Initial System Setup**

### **Update System**
```bash
# Update package lists and system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git python3-pip python3-venv nano wget curl
```

### **Enable Required Interfaces**
```bash
# Open Raspberry Pi configuration
sudo raspi-config
```

**Navigate to:**
1. **Interface Options** → **Serial Port**
   - "Would you like login shell over serial?" → **NO**
   - "Would you like serial hardware enabled?" → **YES**
2. **Interface Options** → **I2C** → **Enable** (just in case)
3. **Interface Options** → **SPI** → **Enable** (just in case)
4. **Finish** → **Reboot when prompted**

---

## 📋 **Step 2: Configure UART for PN532**

### **Edit Boot Configuration**
```bash
# Edit boot config
sudo nano /boot/config.txt
```

**Add these lines at the end:**
```
# PN532 UART Configuration
enable_uart=1
dtoverlay=disable-bt
dtoverlay=pi3-disable-bt
core_freq=250
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

### **Add User to Required Groups**
```bash
# Add user to necessary groups
sudo usermod -a -G dialout,gpio,i2c,spi $USER

# Reboot to apply all changes
sudo reboot
```

---

## 📋 **Step 3: Verify UART Setup**

After reboot, check UART devices:
```bash
# Check available UART devices
ls -la /dev/serial* /dev/tty*0

# Should see devices like:
# /dev/serial0 -> ttyAMA0 (or ttyS0)
# /dev/ttyS0
# /dev/ttyAMA0 (maybe)
```

---

## 📋 **Step 4: Hardware Configuration**

### **Power Off and Configure PN532 HAT**
```bash
sudo shutdown -h now
```

### **Configure Waveshare PN532 HAT Hardware:**

**🔗 Jumper Settings (use small plastic caps):**
- **L0** ↔ **L** (connect with jumper cap)
- **L1** ↔ **L** (connect with jumper cap)
- **RSTPDN** ↔ **D20** (connect with jumper cap)

**🎛️ DIP Switch Settings (use tweezers):**
- **Switch 1 (RX):** ON
- **Switch 2 (TX):** ON  
- **Switch 3:** OFF
- **Switch 4:** OFF

**📐 Physical Installation:**
- Ensure HAT sits flush on ALL 40 GPIO pins
- No bent or misaligned pins
- HAT should not wobble

**Power on after hardware configuration:**
```bash
# Power on your Pi
```

---

## 📋 **Step 5: Download and Setup Project**

### **Create Project Directory**
```bash
# Create project directory
mkdir -p ~/Desktop/HapticCollectionMediaPlayer
cd ~/Desktop/HapticCollectionMediaPlayer

# Clone or download your project files
# (You'll need to copy your files here)
```

### **Create Python Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### **Install Dependencies**
```bash
# Install required Python packages
pip install pyserial==3.5 RPi.GPIO==0.7.1 Flask==2.3.2 Flask-SocketIO==5.3.4

# Verify installation
python3 -c "import serial, RPi.GPIO; print('✅ Dependencies installed')"
```

---

## 📋 **Step 6: Create Project Files**

I'll provide you with the essential files. Create each one:

### **Create config_working.py**
```bash
nano config_working.py
```

**Paste this content:**
```python
#!/usr/bin/env python3
"""
NFC Display System Configuration - Working Version
Based on successful NFC-Player implementation
"""

# Reader Configuration  
READER_TYPE = "PN532_WORKING"

# PN532 Configuration - Working Settings
PN532_UART_PORT = '/dev/ttyS0'      # Key: Use ttyS0, not ttyAMA0
PN532_UART_BAUDRATE = 115200        # Standard baud rate
PN532_RESET_PIN = 20                # GPIO pin for reset

# Display Configuration
HOME_BASE_PAGE = "home_base.html"
UNKNOWN_TAG_PAGE = "unknown_tag.html"

# Tag Detection Settings
NO_TAG_THRESHOLD = 3
READ_INTERVAL = 0.1

# Browser Configuration
BROWSER_COMMAND = [
    'chromium-browser',
    '--kiosk',
    '--noerrdialogs',
    '--disable-infobars',
    '--disable-session-crashed-bubble',
]

# Development mode
BROWSER_COMMAND_DEV = [
    'chromium-browser',
    '--app={url}',
    '--window-size=800,600',
]

DEV_MODE = False

# Database Configuration  
DATABASE_PATH = "data/nfc_tags.db"

# Logging Configuration
ENABLE_LOGGING = True
LOG_FILE = "logs/nfc_display.log"
LOG_LEVEL = "INFO"

# Performance Settings
CACHE_HTML = True
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

### **Create PN532_working.py**
```bash
nano PN532_working.py
```

**Paste this content:**
```python
#!/usr/bin/env python3
"""
PN532 UART Library - Working Implementation
Based on successful NFC-Player approach
"""

import time
import serial
import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)

class PN532_UART:
    def __init__(self, port='/dev/ttyS0', baudrate=115200, rst=20, debug=False):
        self.uart_port = port
        self.baudrate = baudrate
        self.rst_pin = rst
        self.debug = debug
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.output(self.rst_pin, True)
        
        # Initialize UART
        try:
            self.uart = serial.Serial(port=self.uart_port, baudrate=self.baudrate, timeout=1)
            if not self.uart.is_open:
                raise RuntimeError(f'cannot open {self.uart_port}')
            print(f"✅ UART opened: {port} at {baudrate} baud")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize UART: {e}")
        
        # Reset and initialize
        self.reset()
        try:
            self._wakeup()
            self.get_firmware_version()
            print("✅ PN532 initialized successfully")
        except:
            try:
                self.get_firmware_version()
                print("✅ PN532 initialized on retry")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize PN532: {e}")
    
    def reset(self):
        """Hardware reset with working timing"""
        GPIO.output(self.rst_pin, True)
        time.sleep(0.1)
        GPIO.output(self.rst_pin, False)
        time.sleep(0.5)  # Longer reset time
        GPIO.output(self.rst_pin, True)
        time.sleep(0.1)
    
    def _wakeup(self):
        """Wake up sequence from working player"""
        wake_cmd = b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.uart.write(wake_cmd)
        time.sleep(0.1)
        self.SAM_configuration()
    
    def _wait_ready(self, timeout=0.001):
        timestamp = time.monotonic()
        while (time.monotonic() - timestamp) < timeout:
            if self.uart.in_waiting:
                return True
            time.sleep(0.05)
        return False
    
    def _read_data(self, count):
        frame = self.uart.read(min(self.uart.in_waiting, count))
        if not frame:
            raise RuntimeError("No data read from PN532")
        time.sleep(0.005)
        return frame
    
    def _write_data(self, framebytes):
        self.uart.read(self.uart.in_waiting)  # clear buffer
        self.uart.write(framebytes)
    
    def _write_frame(self, data):
        length = len(data)
        frame = bytearray(length+7)
        frame[0] = 0x00  # PREAMBLE
        frame[1] = 0x00  # STARTCODE1
        frame[2] = 0xFF  # STARTCODE2
        frame[3] = length & 0xFF
        frame[4] = (~length + 1) & 0xFF
        frame[5:-2] = data
        checksum = sum([0xD4] + list(data))
        frame[-2] = ~checksum & 0xFF
        frame[-1] = 0x00  # POSTAMBLE
        self._write_data(bytes(frame))
    
    def _read_frame(self, length):
        response = self._read_data(length+7)
        # Simplified frame parsing
        offset = 0
        while offset < len(response) and response[offset] == 0x00:
            offset += 1
        if offset < len(response) and response[offset] == 0xFF:
            offset += 1
            frame_len = response[offset]
            return response[offset+2:offset+2+frame_len]
        raise RuntimeError('Invalid frame')
    
    def call_function(self, command, response_length=0, params=None, timeout=1):
        if params is None:
            params = []
        data = bytearray([0xD4, command & 0xFF] + params)
        
        try:
            self._write_frame(data)
        except OSError:
            self._wakeup()
            return None
        
        if not self._wait_ready(timeout):
            return None
        
        # Read ACK
        ack = b'\x00\x00\xFF\x00\xFF\x00'
        if self._read_data(len(ack)) != ack:
            raise RuntimeError('No ACK received')
        
        if not self._wait_ready(timeout):
            return None
        
        response = self._read_frame(response_length+2)
        if response[0] == 0xD5 and response[1] == (command+1):
            return response[2:]
        raise RuntimeError('Invalid response')
    
    def get_firmware_version(self):
        response = self.call_function(0x02, 4, timeout=0.5)
        if response is None:
            raise RuntimeError('Failed to detect PN532')
        return tuple(response)
    
    def SAM_configuration(self):
        self.call_function(0x14, params=[0x01, 0x14, 0x01])
        return True
    
    def read_passive_target_ID(self, card_baud=0):
        try:
            self.uart.reset_input_buffer()
            response = self.call_function(0x4A, params=[0x01, card_baud], response_length=19, timeout=0.1)
            
            if response is None or len(response) < 7:
                return False, None
            
            if response[0] != 0x01:
                return False, None
            
            uid_length = response[5]
            if len(response) < 6 + uid_length:
                return False, None
            
            uid = response[6:6 + uid_length]
            return True, uid
        except:
            return False, None
    
    def close(self):
        try:
            self.uart.close()
            GPIO.cleanup()
        except:
            pass

def PN532_UART_Reader(port='/dev/ttyS0', baudrate=115200, rst=20, debug=False):
    try:
        reader = PN532_UART(port=port, baudrate=baudrate, rst=rst, debug=debug)
        firmware = reader.get_firmware_version()
        if firmware:
            ic, ver, rev, support = firmware
            print(f"PN532 Firmware: {ver}.{rev}[{ic}.{support}]")
        return reader
    except Exception as e:
        print(f"Failed to initialize PN532: {e}")
        return None
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 📋 **Step 7: Create Test Script**

```bash
nano test_setup.py
```

**Paste this content:**
```python
#!/usr/bin/env python3
"""
Test script to verify PN532 setup
"""
import time
from PN532_working import PN532_UART_Reader

def test_pn532():
    print("🔧 Testing PN532 Setup")
    print("=" * 40)
    
    try:
        # Test PN532 initialization
        print("📡 Initializing PN532...")
        pn532 = PN532_UART_Reader(port='/dev/ttyS0', baudrate=115200, rst=20, debug=True)
        
        if not pn532:
            print("❌ Failed to initialize PN532")
            return False
        
        print("🏷️  Testing tag detection...")
        print("Place an NFC tag on the HAT (testing for 5 seconds)...")
        
        for i in range(50):
            success, uid = pn532.read_passive_target_ID()
            if success and uid:
                uid_hex = ':'.join([f'{b:02X}' for b in uid])
                print(f"\n🎯 TAG DETECTED: {uid_hex}")
                pn532.close()
                return True
            print(".", end="", flush=True)
            time.sleep(0.1)
        
        print("\n⚠️  No tag detected (this is OK if no tag was placed)")
        print("✅ PN532 hardware is working correctly!")
        
        pn532.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    if test_pn532():
        print("\n🎉 SUCCESS! Your PN532 setup is working!")
        print("Next step: Set up your HTML files and database")
    else:
        print("\n❌ Setup needs fixing")
        print("Check hardware connections and try again")
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 📋 **Step 8: Test the Setup**

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Run the test
sudo python3 test_setup.py
```

**Expected output:**
```
✅ UART opened: /dev/ttyS0 at 115200 baud
✅ PN532 initialized successfully
PN532 Firmware: X.X[X.X]
🏷️  Testing tag detection...
```

**If you place an NFC tag:**
```
🎯 TAG DETECTED: XX:XX:XX:XX
🎉 SUCCESS! Your PN532 setup is working!
```

---

## 📋 **Step 9: Create HTML Files**

```bash
# Create HTML directory
mkdir -p html

# Create basic home page
nano html/home_base.html
```

**Paste this content:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>NFC Media Player</title>
    <style>
        body { 
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white; 
            font-family: Arial; 
            text-align: center; 
            padding: 50px;
            margin: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        h1 { font-size: 3em; margin-bottom: 30px; }
        p { font-size: 1.5em; }
    </style>
</head>
<body>
    <h1>🎵 NFC Media Player</h1>
    <p>Ready to scan NFC tags...</p>
    <p>Place an NFC tag on the reader</p>
</body>
</html>
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

```bash
# Create unknown tag page
nano html/unknown_tag.html
```

**Paste this content:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Unknown Tag</title>
    <style>
        body { 
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white; 
            font-family: Arial; 
            text-align: center; 
            padding: 50px;
            margin: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        h1 { font-size: 3em; margin-bottom: 30px; }
        p { font-size: 1.5em; }
    </style>
</head>
<body>
    <h1>❓ Unknown NFC Tag</h1>
    <p>This tag is not registered</p>
    <p>Please configure it first</p>
</body>
</html>
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 📋 **Step 10: Create Database Module**

```bash
nano database.py
```

**Paste this content:**
```python
#!/usr/bin/env python3
"""
Simple NFC Tag Database
"""
import sqlite3
import os

class NFCDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database with tags table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS nfc_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    html_file TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def add_tag(self, uid, name, html_file):
        """Add a new NFC tag"""
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    'INSERT INTO nfc_tags (uid, name, html_file) VALUES (?, ?, ?)',
                    (uid, name, html_file)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_html_file(self, uid):
        """Get HTML file for a given UID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT html_file, name FROM nfc_tags WHERE uid = ?',
                (uid,)
            )
            result = cursor.fetchone()
            if result:
                return result[0], result[1]  # html_file, name
            return None, None
    
    def list_tags(self):
        """List all registered tags"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT uid, name, html_file FROM nfc_tags')
            return cursor.fetchall()
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 📋 **Step 11: Create Main Application**

```bash
nano main_app.py
```

**Paste this content:**
```python
#!/usr/bin/env python3
"""
NFC Media Player - Main Application
"""
import time
import subprocess
import os
import logging
from database import NFCDatabase
from config_working import *
from PN532_working import PN532_UART_Reader

# Setup logging
if ENABLE_LOGGING:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))

class NFCMediaPlayer:
    def __init__(self):
        self.db = NFCDatabase(DATABASE_PATH)
        self.html_dir = os.path.join(os.path.dirname(__file__), 'html')
        self.current_browser = None
        self.current_page = None
        self.current_tag = None
        
        # Tag presence detection
        self.tag_present = False
        self.no_tag_count = 0
        
        print("🎵 NFC Media Player Starting...")
        self.init_pn532()
    
    def init_pn532(self):
        """Initialize PN532"""
        try:
            print("📡 Initializing PN532...")
            self.pn532 = PN532_UART_Reader(
                port=PN532_UART_PORT,
                baudrate=PN532_UART_BAUDRATE,
                rst=PN532_RESET_PIN,
                debug=False
            )
            
            if not self.pn532:
                raise RuntimeError("Failed to initialize PN532")
            
            print("✅ PN532 ready!")
            
        except Exception as e:
            print(f"❌ PN532 initialization failed: {e}")
            print("Check hardware connections and try again")
            exit(1)
    
    def read_tag(self):
        """Read NFC tag"""
        try:
            success, uid_bytes = self.pn532.read_passive_target_ID()
            if success and uid_bytes:
                uid_hex = ':'.join([f'{b:02X}' for b in uid_bytes])
                return uid_hex
        except:
            pass
        return None
    
    def open_browser(self, html_file):
        """Open HTML file in browser"""
        if html_file == self.current_page:
            return
        
        # Close existing browser
        if self.current_browser:
            try:
                subprocess.run(['pkill', 'chromium'], capture_output=True)
                time.sleep(0.5)
            except:
                pass
        
        # Open new page
        html_path = os.path.join(self.html_dir, html_file)
        
        if not os.path.exists(html_path):
            print(f"⚠️  HTML file not found: {html_path}")
            return
        
        cmd = BROWSER_COMMAND + [f'file://{html_path}']
        
        try:
            self.current_browser = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.current_page = html_file
            print(f"🌐 Opened: {html_file}")
        except Exception as e:
            print(f"❌ Browser error: {e}")
    
    def handle_tag_detected(self, tag_uid):
        """Handle tag detection"""
        if tag_uid != self.current_tag:
            print(f"\n🏷️  Tag detected: {tag_uid}")
            self.current_tag = tag_uid
            
            # Look up in database
            html_file, tag_name = self.db.get_html_file(tag_uid)
            
            if html_file:
                print(f"📝 Tag name: {tag_name}")
                self.open_browser(html_file)
            else:
                print("❓ Unknown tag")
                self.open_browser(UNKNOWN_TAG_PAGE)
        
        self.no_tag_count = 0
        self.tag_present = True
    
    def handle_tag_removed(self):
        """Handle tag removal"""
        if self.tag_present:
            self.no_tag_count += 1
            
            if self.no_tag_count >= NO_TAG_THRESHOLD:
                print("\n🏠 Returning to home base")
                self.tag_present = False
                self.current_tag = None
                self.open_browser(HOME_BASE_PAGE)
    
    def run(self):
        """Main loop"""
        print("🎵 NFC Media Player Started!")
        print("🏠 Opening home page...")
        print("👋 Place NFC tags on the reader")
        print("🛑 Press Ctrl+C to stop")
        
        # Open home page
        self.open_browser(HOME_BASE_PAGE)
        
        try:
            while True:
                tag_uid = self.read_tag()
                
                if tag_uid:
                    self.handle_tag_detected(tag_uid)
                else:
                    self.handle_tag_removed()
                
                time.sleep(READ_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            if self.pn532:
                self.pn532.close()
            if self.current_browser:
                subprocess.run(['pkill', 'chromium'], capture_output=True)
            print("👋 Goodbye!")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("⚠️  May need root privileges. If errors occur, try: sudo python3 main_app.py")
    
    player = NFCMediaPlayer()
    player.run()
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 📋 **Step 12: Create Startup Script**

```bash
nano start.sh
```

**Paste this content:**
```bash
#!/bin/bash

# NFC Media Player Startup Script

cd "$(dirname "$0")"

echo "🚀 Starting NFC Media Player"
echo "📍 Directory: $(pwd)"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Create directories
mkdir -p data logs

echo "🎵 Starting NFC Media Player..."
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run the application
python3 main_app.py
```

**Make executable:**
```bash
chmod +x start.sh
```

---

## 📋 **Step 13: Final Test**

```bash
# Test the complete setup
sudo ./start.sh
```

**Expected output:**
```
🚀 Starting NFC Media Player
✅ UART opened: /dev/ttyS0 at 115200 baud
✅ PN532 initialized successfully
PN532 Firmware: X.X[X.X]
🎵 NFC Media Player Started!
🏠 Opening home page...
```

**The browser should open showing your home page!**

---

## 📋 **Step 14: Add Your First NFC Tag**

```bash
# In another terminal, add a test tag to database
source venv/bin/activate

python3 -c "
from database import NFCDatabase
db = NFCDatabase('data/nfc_tags.db')
db.add_tag('AA:BB:CC:DD', 'Test Tag', 'home_base.html')
print('✅ Test tag added')
"
```

Now when you place a tag with UID `AA:BB:CC:DD`, it will show the home page.

---

## 🎉 **Success Checklist**

- ✅ System updated and configured
- ✅ UART enabled and working
- ✅ Hardware properly configured
- ✅ Python environment set up
- ✅ PN532 responding to commands
- ✅ Browser opening HTML pages
- ✅ Database working
- ✅ NFC tags being detected

## 🔧 **If Something Doesn't Work**

1. **PN532 not detected:**
   - Check jumper and DIP switch settings
   - Try with `sudo`
   - Verify hardware connections

2. **No UART devices:**
   - Run `sudo raspi-config` again
   - Check `/boot/config.txt` settings
   - Reboot

3. **Permission errors:**
   - Run with `sudo`
   - Check user groups: `groups $USER`

## 🚀 **Next Steps**

Once everything is working:
1. Create more HTML files for different media
2. Add more NFC tags to the database
3. Customize the browser display
4. Set up auto-start on boot

Your NFC media player should now be fully functional! 🎉
