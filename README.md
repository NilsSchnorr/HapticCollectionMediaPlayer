# NFC Display System

A Raspberry Pi-based system that displays HTML content when NFC tags are scanned. The system shows a "Home Base" page when idle and automatically switches to tag-specific content when an NFC tag is detected.

## Features

- **Tag Presence Detection**: Continuously monitors for NFC tag presence
- **Automatic Page Switching**: Shows Home Base when no tag is present, tag-specific content when a tag is detected
- **Database Management**: SQLite database for storing tag-to-HTML mappings
- **Multiple Reader Support**: Works with both PN532 (USB) and RC522 (SPI) NFC readers
- **Tag Management Tools**: Command-line utilities for managing tags and viewing access logs
- **Web-Based Management Interface**: Easy-to-use web interface for managing NFC tags
- **Real-time Tag Detection**: Web interface shows tags as they're placed on the reader
- **Auto-start on Boot**: Systemd service for automatic startup
- **Customizable HTML Content**: Each tag can display unique HTML pages with full styling and JavaScript support

## System Requirements

- Raspberry Pi (any model with GPIO support)
- NFC reader:
  - **PN532 NFC HAT** (recommended - connects via GPIO pins)
  - PN532 USB module
  - RC522 module (SPI)
- Python 3.7+
- Chromium browser
- NFC tags (ISO 14443A compatible)

## Installation

### Quick Setup

1. Clone this repository to your Raspberry Pi:
   ```bash
   git clone https://github.com/yourusername/HapticCollectionMediaPlayer.git
   cd HapticCollectionMediaPlayer
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Follow the prompts to:
   - Choose your NFC reader type (PN532 or RC522)
   - Set up auto-start on boot (optional)

### Manual Setup

1. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-venv chromium-browser
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   - For PN532: `pip install nfcpy`
   - For RC522: `pip install mfrc522 RPi.GPIO`

4. Initialize the database:
   ```bash
   python3 setup_db.py
   ```

## Configuration

Edit `config.py` to customize the system:

```python
# Reader type: "PN532" or "RC522"
READER_TYPE = "PN532"

# HTML pages
HOME_BASE_PAGE = "home_base.html"
UNKNOWN_TAG_PAGE = "unknown_tag.html"

# Tag detection settings
NO_TAG_THRESHOLD = 3  # Failed reads before tag is considered removed
READ_INTERVAL = 0.1   # Seconds between reads

# Development mode (windowed browser)
DEV_MODE = False
```

## Usage

### Starting the System

```bash
# Activate virtual environment
source venv/bin/activate

# Run the main program
python3 main.py
```

Or use the launcher script:
```bash
./start_nfc_display.sh
```

### Web-Based Tag Management Interface

The easiest way to manage NFC tags is through the web interface:

```bash
# Start the web interface
./start_web_interface.sh
```

Then open your browser and go to:
- Local access: http://localhost:5000
- Network access: http://[raspberry-pi-ip]:5000

**Web Interface Features:**
- **Real-time Tag Detection**: Place a tag on the reader and it appears instantly
- **Easy Configuration**: Select HTML files from a dropdown menu
- **Visual Feedback**: See which tags are registered and when they were last used
- **Access Logs**: View when each tag was scanned
- **No Command Line**: Everything can be done through the browser

### Managing Tags (Command Line)

List all registered tags:
```bash
python3 manage_tags.py list
```

Add a new tag:
```bash
python3 manage_tags.py add 04:5C:7B:2A:6C:50:80 "Product Info" product.html --description "Product showcase"
```

Interactive tag addition:
```bash
python3 manage_tags.py interactive
```

View access logs:
```bash
python3 manage_tags.py logs --limit 50
```

### Testing Tag Presence

Test the tag detection behavior:
```bash
python3 test_presence.py
```

## Creating Custom HTML Pages

1. Create HTML files in the `html/` directory
2. Register them with specific NFC tags using `manage_tags.py`
3. HTML pages can include:
   - Full CSS styling
   - JavaScript interactivity
   - External resources (fonts, images)
   - Navigation between sections

Example structure:
```
html/
├── home_base.html      # Default page (no tag present)
├── unknown_tag.html    # Shown for unregistered tags
├── welcome.html        # Custom content pages
├── product1.html
└── product_detail.html
```

## How It Works

1. **Idle State**: When no NFC tag is detected, the system displays `home_base.html`
2. **Tag Detection**: When a tag is placed on the reader:
   - The tag UID is read and formatted
   - Database lookup finds the associated HTML file
   - Browser switches to display the tag's HTML page
3. **Tag Presence**: As long as the tag remains on the reader:
   - The page stays active (no refresh)
   - Users can interact with the page (click links, etc.)
4. **Tag Removal**: When the tag is removed:
   - After the threshold is reached (default: 3 failed reads)
   - System automatically returns to `home_base.html`

## Auto-start on Boot

The system can be configured to start automatically when the Raspberry Pi boots:

```bash
# Enable the service
sudo systemctl enable nfc-display.service

# Start the service now
sudo systemctl start nfc-display.service

# Check service status
sudo systemctl status nfc-display.service

# View logs
sudo journalctl -u nfc-display.service -f
```

## Troubleshooting

### NFC Reader Not Detected

#### For PN532 NFC HAT:
1. **Enable I2C interface**:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → I2C → Enable
   ```

2. **Verify I2C connection**:
   ```bash
   sudo i2cdetect -y 1
   # Should show device at address 0x24
   ```

3. **Check HAT installation**:
   - Ensure HAT is firmly connected to GPIO pins
   - Check that no pins are bent or misaligned
   - The HAT should sit flush on the GPIO header

4. **Install I2C tools** (if not already installed):
   ```bash
   sudo apt-get install i2c-tools
   ```

5. **Test with different interface** (if I2C fails):
   - Edit `config.py` and try:
     - `PN532_INTERFACE = 'spi'` (if jumpers set for SPI)
     - `PN532_INTERFACE = 'uart'` (if jumpers set for UART)

#### For PN532 USB:
- Check USB connection
- Verify the reader appears with `lsusb`
- Try different USB ports

For RC522:
- Enable SPI: `sudo raspi-config` → Interface Options → SPI
- Check wiring connections
- Verify GPIO pins in `config.py`

### Browser Issues

- Ensure Chromium is installed: `sudo apt-get install chromium-browser`
- For development, set `DEV_MODE = True` in `config.py`
- Check display permissions if using SSH

### Tag Not Recognized

1. Test with `test_presence.py` to see raw tag reads
2. Verify tag UID format (should be XX:XX:XX:XX:XX:XX:XX)
3. Check if tag is registered: `python3 manage_tags.py list`

## Database Schema

The system uses SQLite with two tables:

**nfc_tags**:
- `tag_uid`: Unique identifier (primary key)
- `tag_name`: Human-readable name
- `html_file`: Associated HTML filename
- `description`: Optional description
- `created_at`: Registration timestamp
- `last_accessed`: Last scan timestamp

**access_log**:
- `id`: Auto-incrementing ID
- `tag_uid`: Foreign key to nfc_tags
- `accessed_at`: Access timestamp

## Additional Documentation

- [Web Interface Guide](WEB_INTERFACE_GUIDE.md) - Detailed guide for using the web management interface
- [System Architecture](ARCHITECTURE.md) - Technical overview of how the system works
- [PN532 HAT Setup](PN532_HAT_SETUP.md) - Specific guide for PN532 NFC HAT users
- [Quick Test Guide](QUICK_TEST_GUIDE.md) - Testing the system with example files

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.
