# 🚀 Waveshare PN532 Quick Setup Guide

This guide uses the **Waveshare proprietary library** instead of nfcpy for better compatibility with Waveshare PN532 HATs.

## ✅ **Advantages of Waveshare Library:**
- **Designed specifically** for Waveshare PN532 HATs
- **More reliable** UART communication
- **Better error handling** for hardware issues
- **No version conflicts** with system packages

## 📋 **Prerequisites**
- Waveshare PN532 NFC HAT
- Raspberry Pi with UART enabled
- Python virtual environment (recommended)

## 🔧 **Step 1: Install Dependencies**

```bash
# Navigate to your project
cd ~/HapticCollectionMediaPlayer
source venv/bin/activate  # If using virtual environment

# Install Waveshare requirements
pip install -r requirements_waveshare.txt

# Or install individually:
pip install pyserial RPi.GPIO Flask Flask-SocketIO
```

## ⚙️ **Step 2: Hardware Configuration**

### **Jumper Settings:**
- **L0** → **L** (connect with jumper)
- **L1** → **L** (connect with jumper)  
- **RSTPDN** → **D20** (connect with jumper)

### **DIP Switch Settings:**
- **RX switch:** ON
- **TX switch:** ON
- **All other switches:** OFF

```
DIP Switches: [RX:ON] [TX:ON] [Others:OFF]
Jumpers: L0-L, L1-L, RSTPDN-D20
```

## 🔌 **Step 3: Enable UART**

```bash
# Enable UART interface
sudo raspi-config
# Interface Options → Serial Port → Enable

# Add user to dialout group
sudo usermod -a -G dialout $USER

# Reboot to apply changes
sudo reboot
```

## 🧪 **Step 4: Test the Setup**

```bash
# Test Waveshare PN532 communication
source venv/bin/activate  # If using venv
python3 test_waveshare.py
```

**Expected output:**
```
🚀 Waveshare PN532 NFC HAT Test
✅ Waveshare PN532 NFC HAT initialized successfully!
🔍 WAVESHARE PN532 NFC TAG PRESENCE TEST
```

**Place an NFC tag** and you should see:
```
🏷️  NEW TAG DETECTED: A1:B2:C3:D4:E5:F6
```

## 🎮 **Step 5: Run Your Media Player**

```bash
# Make script executable
chmod +x start_waveshare.sh

# Start the NFC display system
./start_waveshare.sh
```

## 📁 **New Files Created:**

- **`config_waveshare.py`** - Waveshare-specific configuration
- **`PN532.py`** - Waveshare PN532 UART library
- **`main_waveshare.py`** - Main application using Waveshare library
- **`test_waveshare.py`** - Test script for Waveshare PN532
- **`requirements_waveshare.txt`** - Waveshare-specific dependencies
- **`start_waveshare.sh`** - Startup script for Waveshare version

## 🔧 **Troubleshooting**

### **"Failed to initialize PN532!"**
```bash
# 1. Check hardware jumpers and DIP switches
# 2. Verify UART is enabled
sudo raspi-config  # Interface Options → Serial → Enable

# 3. Check user permissions
groups $USER  # Should include 'dialout'

# 4. Try with sudo
sudo python3 test_waveshare.py
```

### **"Permission denied: '/dev/serial0'"**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, or reboot
sudo reboot
```

### **"No such file or directory: '/dev/serial0'"**
```bash
# Check available UART devices
ls -la /dev/serial* /dev/tty*0

# Update config_waveshare.py if needed:
# Edit the port in PN532.py or pass different port to PN532_UART_Reader()
```

### **Communication Issues**
```bash
# Try different baud rates by editing PN532.py:
# Change baudrate=115200 to baudrate=57600 or baudrate=9600
```

## 🆚 **Waveshare vs nfcpy Comparison**

| Feature | Waveshare Library | nfcpy Library |
|---------|-------------------|---------------|
| **Compatibility** | Waveshare PN532 HATs | Universal PN532 |
| **Setup Complexity** | Simple | More complex |
| **Dependencies** | Minimal | More system deps |
| **Error Messages** | Hardware-specific | Generic |
| **Performance** | Optimized for HAT | General purpose |

## 🎯 **Next Steps**

1. **Test tag detection** with `test_waveshare.py`
2. **Configure your tags** using the web interface
3. **Run your media player** with `start_waveshare.sh`

## 💡 **Pro Tips**

- **Remove metal keychains** from NFC tags during testing
- **Place tags flat** on the HAT antenna area
- **Use tweezers** for DIP switch adjustments
- **Take photos** of jumper settings before changes

The Waveshare library should give you much more reliable communication with your specific hardware! 🎉
