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

#### Disabling Screen Blanking (Important for Exhibitions)

By default, Raspberry Pi OS will blank the screen after a period of inactivity. Since the HCMP runs without keyboard or mouse input, the OS thinks it's idle and may turn off the display. The `start_display.sh` script already attempts to disable this via `xset` and `setterm` commands, but you should **also** disable it at the OS level to be safe:

```bash
sudo raspi-config
```
Navigate to **Display Options → Screen Blanking → No**.

This ensures the display stays on indefinitely, even across reboots.

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

### Autostart (Museum / Exhibition Mode)

For unattended installations where the Pi should boot directly into display mode — for example in a museum where staff simply turn on the power each morning — you can set up autostart. This makes the HCMP launch automatically every time the Pi boots, with no keyboard or mouse interaction required.

#### What It Does

The autostart installer sets up two things:

1. **A systemd service** that starts the NFC display backend (`nfc_display.py`) early in the boot process. This is the Python server that talks to the NFC reader and serves content on port 8080.
2. **A desktop autostart entry** that opens Chromium in fullscreen kiosk mode once the graphical desktop is ready, pointed at `http://localhost:8080`. It also disables screen blanking at the X11 level.

Additionally, it enables desktop auto-login and disables screen blanking via `raspi-config`.

#### Installing Autostart

```bash
./install_autostart.sh
```

The script will ask for confirmation, then set everything up. At the end it offers to reboot so you can test it immediately.

After a reboot, the boot sequence is:

1. Pi powers on and boots the OS
2. Auto-login to the desktop (no password prompt)
3. systemd starts the NFC display backend
4. Chromium opens in fullscreen kiosk mode
5. The "Place an object on the reader" home screen appears

No user interaction needed at any point.

#### Making Changes While Autostart Is Active

When the Pi boots into display mode and you need to make changes (edit mappings, update HTML files, etc.), you don't need to uninstall autostart. Just open a terminal and stop the service:

```bash
sudo systemctl stop hcmp-display
```

Then close Chromium (Alt+F4) and do your thing. When you're done, either reboot (autostart takes over) or restart manually:

```bash
sudo systemctl start hcmp-display
```

#### Removing Autostart

To go back to normal boot behavior:

```bash
./uninstall_autostart.sh
```

This removes the systemd service and the Chromium autostart entry. It does not change auto-login or screen blanking settings — adjust those via `sudo raspi-config` if needed.

#### Useful Commands

```bash
sudo systemctl stop hcmp-display      # Stop the display backend
sudo systemctl start hcmp-display     # Start the display backend
sudo systemctl status hcmp-display    # Check if it's running
sudo journalctl -u hcmp-display -f    # View live logs
```

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

### Screen Goes Black After a While
The display turning off is caused by Raspberry Pi OS screen blanking. Make sure you have disabled it:
1. Run `sudo raspi-config` → **Display Options** → **Screen Blanking** → **No**
2. Use `start_display.sh` (not `start_display_simple.sh`) — it includes `xset` and `setterm` commands that disable screen blanking at the X11 level.
3. If using autostart, this is handled automatically by `install_autostart.sh`.

### NFC Not Detecting
1. Check hardware connections
2. Verify reader with: `cd python && python3 example_get_uid.py`
3. Try `sudo` if permission errors
4. If you recently closed the web server or another NFC script, the serial port may still be locked. Wait a few seconds and try again — the display script will attempt to flush the serial port on startup.

### NFC Works in Web Server But Not in Display Mode
This can happen if the web server (`nfc_web_server.py`) wasn't shut down cleanly, leaving the serial port or PN532 in a bad state. Both scripts now clean up on exit and flush the serial port on startup, but if the issue persists, a reboot will always resolve it.

### Port Already in Use
- Management interface uses port 5000
- Display system uses port 8080
- Kill existing processes: `pkill -f "8080"`

### View Logs
```bash
# If running via autostart service
sudo journalctl -u hcmp-display -f

# If running in background
tail -f nfc_player.log
```

## 📁 Project Structure

```
HapticCollectionMediaPlayer/
├── Core System
│   ├── nfc_display.py            # Main display system
│   ├── nfc_web_server.py         # Management interface
│   └── web_interface/            # Web UI files
│
├── Startup Scripts
│   ├── start_display.sh          # Manual kiosk mode
│   ├── start_display_simple.sh   # Manual window mode
│   ├── start_both.sh             # Management tools
│   └── start_demo.sh             # Demo mode
│
├── Autostart
│   ├── install_autostart.sh      # Set up boot-to-display
│   ├── uninstall_autostart.sh    # Remove autostart
│   └── hcmp-display.service      # systemd service template
│
├── Content & Data
│   ├── html_content/             # Your HTML files
│   └── nfc_mappings.json         # Saved mappings
│
└── Libraries
    └── python/                   # PN532 drivers
```

## 🎯 Common Use Cases

### Museum Exhibition
1. Create HTML pages for each exhibit
2. Attach NFC tags to physical objects
3. Map tags to relevant content
4. Run `./install_autostart.sh` for hands-free operation
5. Staff just need to turn on the power each day

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
- **Disable screen blanking**: Run `sudo raspi-config` → Display Options → Screen Blanking → No (see [Disabling Screen Blanking](#disabling-screen-blanking-important-for-exhibitions))
- **Museum setup**: Use `./install_autostart.sh` so the display starts automatically on power-on (see [Autostart](#autostart-museum--exhibition-mode))

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
