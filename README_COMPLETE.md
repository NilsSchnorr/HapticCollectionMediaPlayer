# 🎭 Haptic Collection Media Player - Complete System

A complete NFC-to-HTML display system for interactive exhibitions and installations.

## 🚀 Quick Start

### First Time Setup
```bash
# Make scripts executable
chmod +x make_executable.sh
./make_executable.sh

# Create NFC mappings
./start_both.sh
```
Open http://localhost:5000 and map your NFC chips to HTML files.

### Run the Display
```bash
# Simple mode (regular window)
./start_display_simple.sh

# OR Kiosk mode (fullscreen)
./start_display.sh
```

## 📦 System Components

### 1. **NFC Display** (`nfc_display.py`)
- Shows elegant home screen
- Detects NFC chips and displays mapped content
- Returns to home when chip removed
- Runs on port 8080

### 2. **Management Interface** (`nfc_web_server.py`)
- Create/delete NFC-to-HTML mappings
- Test NFC detection
- Runs on port 5000

### 3. **NFC Player** (`nfc_player.py`)
- Alternative mode: opens HTML in new browser tabs
- For multi-window displays

## 🎯 Typical Workflow

1. **Setup Phase** (one time)
   ```bash
   ./start_both.sh
   ```
   - Place NFC chips on reader
   - Select HTML files to map
   - Save mappings

2. **Display Phase** (daily use)
   ```bash
   ./start_display.sh
   ```
   - System shows home screen
   - Visitors place objects → see content
   - Remove objects → return to home

## 📁 Project Structure

```
HapticCollectionMediaPlayer/
├── nfc_display.py         # Main display system
├── nfc_web_server.py      # Management interface
├── nfc_mappings.json      # Saved mappings
├── html_content/          # Your HTML files
│   ├── welcome.html
│   ├── gallery.html
│   └── (your content)
├── start_display.sh       # Run display (kiosk)
├── start_display_simple.sh # Run display (window)
└── start_both.sh         # Run management tools
```

## 🎨 Customization

### Home Screen
Edit `nfc_display.py` to customize:
- Title text
- Colors and gradients
- Animation effects
- Prompt messages

### Content
Add HTML files to `html_content/` directory. Full HTML/CSS/JS supported.

## 🖥️ Display Modes

### Development/Testing
```bash
./start_display_simple.sh
```
Opens in regular browser window

### Exhibition/Kiosk
```bash
./start_display.sh
```
- Fullscreen mode
- No browser UI
- ESC to exit

### Auto-start on Boot
Add to `/etc/rc.local` or use systemd:
```bash
cd /home/pi/Documents/GitHub/HapticCollectionMediaPlayer
./start_display.sh &
```

## 🔧 Troubleshooting

### Check System Status
```bash
./check_status.sh
```

### View Saved Mappings
```bash
cat nfc_mappings.json
```

### Test NFC Reader
```bash
python3 test_nfc.py
```

## 📋 Requirements

- Raspberry Pi with PN532 NFC reader
- Python 3.6+
- Flask
- Web browser (Chromium recommended)

## 🎯 Use Cases

- Museum exhibitions
- Interactive art installations  
- Product demonstrations
- Educational displays
- Escape rooms
- Smart home interfaces

## 📝 Notes

- Mappings persist in `nfc_mappings.json`
- Display runs on port 8080
- Management runs on port 5000
- Supports multiple chips with different content
- Instant switching between contents

---

Enjoy your interactive NFC display system! 🎉
