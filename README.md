# Haptic Collection Media Player
By Lucas Latzel and Nils Schnorr

An interactive NFC-based media display system that presents HTML content when physical objects are placed on a reader. Perfect for museums, exhibitions, interactive art installations, and educational displays.


## 🌟 Overview

This system allows you to:
- **Map NFC chips to HTML content** using a web interface
- **Display content automatically** when objects are placed on the reader
- **Return to home screen** when objects are removed
- **Run in kiosk mode** for public exhibitions

## 🚀 Quick Start

```bash
# 1. Make scripts executable
chmod +x make_executable.sh
./make_executable.sh

# 2. Create NFC mappings
./start_both.sh
# Open http://localhost:5000 to map your NFC chips

# 3. Run the display
./start_display_simple.sh
```

## 📋 Requirements

### Hardware
- Raspberry Pi (tested on Pi 3/4)
- PN532 NFC/RFID reader (UART connection)
- NFC tags/chips (NTAG, Mifare, etc.)
- HDMI display

### Software
- Raspberry Pi OS (or similar Linux)
- Python 3.6+
- Web browser (Chromium recommended)

## 🔧 Installation

### 1. Clone the Repository
```bash
cd ~/Documents/GitHub
git clone https://github.com/NilsSchnorr/HapticCollectionMediaPlayer
cd HapticCollectionMediaPlayer
```

### 2. Install Dependencies

#### Option A: Virtual Environment (Recommended)
```bash
./setup.sh
```

#### Option B: System Packages
```bash
./setup_system_packages.sh
```

### 3. Connect NFC Reader
Connect your PN532 to the Raspberry Pi:
- VCC → 3.3V
- GND → GND
- TX → RX (GPIO 15)
- RX → TX (GPIO 14)

### 4. Test NFC Reader
```bash
cd python
python3 example_get_uid.py
```
Place an NFC chip on the reader - you should see its UID.

## 📖 User Guide

### Tag Management Interface

The tag management interface allows you to create mappings between NFC chips and HTML files.

#### Starting the Management Interface
```bash
./start_both.sh
```
Open http://localhost:5000 in your browser.

#### Creating Mappings
1. **Place an NFC chip** on the reader
2. The UID will automatically appear in the form
3. **Select an HTML file** from the dropdown
4. **Add a description** (optional)
5. Click **Save Mapping**

#### Managing Content
- **Add HTML files**: Place them in the `html_content/` directory
- **View mappings**: See all existing mappings in the table
- **Delete mappings**: Click the Delete button next to any mapping
- **Test detection**: Use "Test with Random UID" for development

Your mappings are saved in `nfc_mappings.json` and persist across restarts.

### Display System

The display system shows a home screen and automatically displays content when NFC chips are detected.

#### Starting the Display

**For Development/Testing:**
```bash
./start_display_simple.sh
```
Opens in a regular browser window (easy to close).

**For Exhibitions/Kiosk Mode:**
```bash
./start_display.sh
```
Opens in fullscreen kiosk mode (ESC to exit).

**Demo Mode (No NFC Hardware):**
```bash
./start_demo.sh
```
Use buttons or keys 1-3 to simulate chips.

#### How It Works
1. **Home Screen**: Shows "Haptic Collection Media Player" with animated NFC icon
2. **Chip Detected**: Instantly displays the mapped HTML content
3. **Chip Removed**: Returns to the home screen
4. **Unknown Chips**: Shows "Unknown chip" message

#### Display Features
- Smooth transitions between content
- Full-screen HTML display
- Animated home screen
- Real-time chip detection
- No user interaction needed

#### Exiting Kiosk Mode
- **ESC** or **F11** - Exit fullscreen
- **Alt + F4** - Close window
- **Ctrl + C** - Stop from terminal

## 🎨 Customization

### Home Screen Appearance
Edit `nfc_display.py` to customize:
- Title text and messages
- Colors and gradients
- Animation effects
- NFC icon design

### HTML Content
- Place files in `html_content/` directory
- Full HTML/CSS/JavaScript support
- Content displays edge-to-edge
- Can include images, videos, interactive elements

### Example Content Structure
```
html_content/
├── welcome.html      # Introduction screen
├── gallery.html      # Image gallery
├── video.html        # Video player
├── interactive.html  # Interactive elements
└── assets/           # Images, CSS, JS files
```

## 🛠️ Troubleshooting

### Check System Status
```bash
./check_status.sh
```
Shows what's running and port status.

### NFC Not Detecting
1. Check hardware connections
2. Verify reader with: `cd python && python3 example_get_uid.py`
3. Try `sudo` if permission errors

### Port Already in Use
- Management interface uses port 5000
- Display system uses port 8080
- Kill existing processes: `pkill -f "8080"`

### View Logs
```bash
# If running in background
tail -f nfc_player.log
```

## 📁 Project Structure

```
HapticCollectionMediaPlayer/
├── Core System
│   ├── nfc_display.py         # Main display system
│   ├── nfc_web_server.py      # Management interface
│   └── web_interface/         # Web UI files
│
├── Startup Scripts
│   ├── start_display.sh       # Kiosk mode
│   ├── start_display_simple.sh # Window mode
│   ├── start_both.sh          # Management tools
│   └── start_demo.sh          # Demo mode
│
├── Content & Data
│   ├── html_content/          # Your HTML files
│   └── nfc_mappings.json      # Saved mappings
│
└── Libraries
    └── python/                # PN532 drivers
```

## 🎯 Common Use Cases

### Museum Exhibition
1. Create HTML pages for each exhibit
2. Attach NFC tags to physical objects
3. Map tags to relevant content
4. Run in kiosk mode on exhibition screen

### Interactive Art Installation
1. Embed NFC chips in art pieces
2. Create immersive HTML experiences
3. Hide the reader under a surface
4. Let visitors discover content naturally

### Educational Display
1. Tag learning materials
2. Create educational HTML content
3. Students tap objects to learn more
4. Track which content is most popular

## 💡 Tips

- **Backup your mappings**: Copy `nfc_mappings.json` regularly
- **Test content first**: Use demo mode to preview
- **Optimize for display**: Design HTML for your screen resolution
- **Use unique chips**: Each NFC chip needs a unique UID
- **Hide the reader**: Can work through thin materials

## 🔒 Security Note

This system is designed for local networks and trusted environments. For public installations:
- Run on isolated network
- Restrict file system access
- Use read-only file system
- Disable unnecessary services

## 📄 License

This project is licensed under a Modified MIT License (Non-Commercial) - see the [LICENSE.txt](LICENSE.txt) file for details.

**Key points:**
- ✅ Free to use, modify, and share for non-commercial purposes
- ✅ Attribution required (Lucas Latzel and Nils Schnorr)
- ❌ Commercial use prohibited
- 📚 Please cite our work if used in research (see LICENSE.txt)

## Acknowledgments

Built with:
- Flask web framework
- PN532 NFC library by Waveshare/Yehui ([Wiki](https://www.waveshare.com/wiki/PN532_NFC_HAT))
- Threejs-gltf-import from dgreenheck (https://github.com/dgreenheck/threejs-gltf-import/tree/main)

**Special thanks to:**
- Jürgen Schnorr for providing us with the required hardware and helping us with the first iteration of code

---

**Repository:** https://github.com/NilsSchnorr/HapticCollectionMediaPlayer

For issues, questions, or contributions, please visit the project repository.
