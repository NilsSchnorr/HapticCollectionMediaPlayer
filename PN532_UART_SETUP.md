# PN532 NFC HAT UART Setup Guide

This guide covers switching your PN532 NFC HAT from I2C to UART interface.

## Important: Waveshare PN532 HAT Specific Setup

**If you have a Waveshare PN532 HAT**, there are specific jumper and DIP switch configurations required. This guide covers both the Waveshare-specific setup and generic PN532 HAT setup.

## Why Switch to UART?

- Some PN532 HATs have issues with I2C communication
- UART can be more stable in certain configurations  
- Alternative when I2C interface is not working properly
- UART is the **default recommended interface** for Waveshare PN532 HATs

## Hardware Changes Required

### 1. Power Off Raspberry Pi
```bash
sudo shutdown -h now
```
Wait for the Pi to completely shut down before proceeding.

### 2. Configure Hardware Settings

#### For Waveshare PN532 HAT (Specific Model)

The Waveshare PN532 HAT requires specific jumper and DIP switch settings:

**Jumper Configuration:**
- Connect **L0 to L** using a jumper
- Connect **L1 to L** using a jumper  
- Connect **RSTPDN to D20** using a jumper

**DIP Switch Configuration:**
- Set only **RX** and **TX** switches to **ON**
- All other DIP switches should be **OFF**
- Use tweezers for precise DIP switch adjustment

```
DIP Switches: [RX:ON] [TX:ON] [Others:OFF]
Jumpers: L0-L, L1-L, RSTPDN-D20
```

#### For Generic PN532 HAT

**IMPORTANT**: Locate the jumpers on your PN532 HAT. There should be two small jumpers that can be moved between different positions.

**Current Setting (I2C)**:
- Both jumpers should be in the "I2C" position

**New Setting (UART)**:
- Move **both jumpers** to the "UART" position
- The jumpers are usually labeled: HSU (UART), I2C, SPI
- Set both jumpers to **HSU/UART** position

**Jumper Layout** (typical):
```
[HSU] [I2C] [SPI]
  ↑     ↑     ↑
Move jumpers from I2C to HSU position
```

### 3. Physical Connections
The UART interface uses these GPIO pins:
- **GPIO 14** (Pin 8) - TX (Transmit)
- **GPIO 15** (Pin 10) - RX (Receive)
- **GND** - Ground connection
- **3.3V** - Power connection

The HAT should already be connected properly if it was working with I2C.

## Raspberry Pi Configuration Changes

### Method 1: Simple Setup (Core Electronics Method)

For basic UART setup, you can use the simple Raspberry Pi Configuration GUI:

```bash
# Open Raspberry Pi Configuration
sudo raspi-config
```

Navigate to:
- **Interface Options** → **Serial Port** → **Enable**

Then reboot:
```bash
sudo reboot
```

### Method 2: Comprehensive Setup (Recommended)

For a more robust setup that avoids conflicts:

### 1. Enable UART Interface
```bash
sudo raspi-config
```
Navigate to:
- **Interfacing Options** → **Serial** → **Yes** (enable serial interface)
- **Advanced Options** → **Serial** → **No** (disable login shell over serial) → **Yes** (enable serial port hardware)

Or manually edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add or ensure these lines are present and uncommented:
```
# Enable UART
enable_uart=1
dtoverlay=disable-bt

# Disable I2C (since we're not using it anymore)
# dtparam=i2c_arm=on
```

### 2. Disable Bluetooth (Recommended)
UART and Bluetooth can conflict. Add to `/boot/config.txt`:
```
# Disable Bluetooth to free up UART
dtoverlay=disable-bt
```

### 3. Update Boot Command Line
Edit `/boot/cmdline.txt`:
```bash
sudo nano /boot/cmdline.txt
```

Remove any references to `console=serial0,115200` or `console=ttyAMA0,115200` to prevent conflicts.

### 4. Set UART Permissions
```bash
sudo usermod -a -G dialout $USER
```

### 5. Reboot
```bash
sudo reboot
```

## Software Configuration

The code has already been updated, but verify these settings in `config.py`:

```python
# Set interface to UART
PN532_INTERFACE = 'uart'

# UART configuration
PN532_UART_PORT = '/dev/serial0'  # UART port
PN532_UART_BAUDRATE = 115200      # Baud rate
```

## Testing the UART Setup

### 1. Check UART Device
```bash
ls -la /dev/serial*
```
You should see `/dev/serial0` linked to `/dev/ttyAMA0` or `/dev/ttyS0`.

### 2. Test NFC Communication
```bash
cd ~/HapticCollectionMediaPlayer
source venv/bin/activate  # if using virtual environment
python3 test_presence.py
```

Place an NFC tag on the HAT. You should see:
```
Waiting for NFC tag...
Tag detected: XX:XX:XX:XX
```

### 3. Run Main Application
```bash
./start_nfc_display.sh
```

## Troubleshooting

### "No NFC device found" Error

1. **Check jumper positions** - Ensure both jumpers are in UART position
2. **Verify UART is enabled**:
   ```bash
   dmesg | grep tty
   # Should show UART devices
   ```
3. **Check permissions**:
   ```bash
   groups $USER
   # Should include 'dialout'
   ```
4. **Try running with sudo**:
   ```bash
   sudo python3 main.py
   ```

### Bluetooth Conflicts
If you're getting serial port conflicts:
```bash
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth
```

### Connection String Issues
The UART connection uses this format: `tty:serial0:115200`

If `/dev/serial0` doesn't exist, try:
- `/dev/ttyAMA0` (on older Pi models)
- `/dev/ttyS0` (on some configurations)

Update `config.py` accordingly:
```python
PN532_UART_PORT = '/dev/ttyAMA0'  # or /dev/ttyS0
```

### Baud Rate Issues
If communication is unstable, try different baud rates:
```python
PN532_UART_BAUDRATE = 57600   # Half speed
# or
PN532_UART_BAUDRATE = 9600    # Slower but more reliable
```

## Switching Back to I2C

If you need to switch back:

1. **Hardware**: Move jumpers back to I2C position
2. **Software**: Change `config.py`:
   ```python
   PN532_INTERFACE = 'i2c'
   ```
3. **Pi Config**: Re-enable I2C in `raspi-config`

## Performance Notes

- UART may have slightly different performance characteristics than I2C
- Tag detection range and speed should be similar
- If you experience issues, try adjusting `READ_INTERVAL` in `config.py`

## Differences from Other Guides

### Core Electronics vs Our Implementation

**Core Electronics Guide** uses:
- Waveshare-specific example code
- Simple raspi-config Serial Port enable
- No Bluetooth disabling
- Proprietary Waveshare library

**Our Implementation** uses:
- Industry-standard `nfcpy` library
- More robust UART configuration
- Bluetooth conflict prevention
- Comprehensive error handling
- Support for multiple PN532 HAT variants

### Library Differences

**Waveshare Code Example:**
```python
# Their approach (Waveshare specific)
import PN532
pn532 = PN532.PN532_UART(Debug=False, rst=20)
```

**Our Code (nfcpy):**
```python
# Our approach (industry standard)
import nfc
clf = nfc.ContactlessFrontend('tty:serial0:115200')
```

### Advantages of Our Approach

1. **Better Compatibility**: Works with various PN532 modules, not just Waveshare
2. **More Stable**: Bluetooth disabling prevents UART conflicts
3. **Industry Standard**: nfcpy is widely used and well-maintained
4. **Error Handling**: Better debugging and error messages
5. **Flexible Configuration**: Easy to switch between interfaces

### When to Use Each Approach

**Use Core Electronics method if:**
- You have the exact Waveshare PN532 HAT
- You want the simplest possible setup
- You're following their specific examples

**Use our method if:**
- You want maximum compatibility
- You need robust error handling
- You plan to use advanced NFC features
- You want to avoid potential conflicts
