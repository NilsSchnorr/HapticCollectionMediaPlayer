# PN532 NFC HAT - Quick Start Guide

## Prerequisites
- PN532 NFC HAT installed on Raspberry Pi GPIO pins
- Fresh copy of the HapticCollectionMediaPlayer repository

## Step 1: Initial Setup (One Time Only)

```bash
cd ~/HapticCollectionMediaPlayer
chmod +x *.sh
./setup.sh
```

When prompted:
- Choose **1** for "PN532 NFC HAT"
- Choose **Y** for auto-start (optional)

This will:
- Enable I2C interface
- Install nfcpy library
- Configure system for PN532 HAT

## Step 2: Verify NFC HAT Connection

```bash
# Check I2C is working
sudo i2cdetect -y 1
# You should see "24" in the grid

# Test NFC detection
source venv/bin/activate
python3 test_presence.py
```

Place an NFC tag on the HAT - you should see it detected.

## Step 3: Configure Your NFC Tags

### Start the Web Interface:
```bash
./start_web_interface.sh
```

### Open Browser:
- On Pi: http://localhost:5000
- From laptop: http://[pi-ip-address]:5000

### Add Tags:
1. Place NFC tag on the HAT
2. Web interface shows "New tag detected!"
3. Enter a name (e.g., "Blue Test")
4. Select HTML file (e.g., "test1.html")
5. Click "Save Tag"
6. Repeat for each tag

### Stop Web Interface:
Press `Ctrl+C` when done

## Step 4: Run the Display System

```bash
./start_nfc_display.sh
```

Now:
- **No tag** = Purple "Ready to Scan" screen
- **Place tag** = Shows assigned HTML page
- **Remove tag** = Returns to "Ready to Scan"

## Common Issues & Solutions

### "No NFC device found!"
```bash
# Ensure I2C is enabled
sudo raspi-config
# Interface Options → I2C → Enable

# Add user to i2c group
sudo usermod -a -G i2c $USER
# Log out and back in

# Or run with sudo
sudo ./start_nfc_display.sh
```

### Tag Not Reading
- Place tag flat on the HAT
- Center it over the antenna area
- Try different orientations
- Remove metal objects nearby

### Web Interface Connection Issues
```bash
# Check your Pi's IP
hostname -I

# Ensure Flask is installed
source venv/bin/activate
pip install Flask Flask-SocketIO
```

## Test Tags Included

The system includes test pages:
- **test1.html** - Blue screen "TEST 1"
- **test2.html** - Red screen "TEST 2"  
- **test_interactive.html** - Green with counter

Perfect for quick testing!

## Summary Commands

```bash
# Configure tags (do this first)
./start_web_interface.sh

# Run display (after tags configured)
./start_nfc_display.sh

# Stop either program
Ctrl+C
```

That's it! Your NFC display system should now be working with the PN532 HAT.
