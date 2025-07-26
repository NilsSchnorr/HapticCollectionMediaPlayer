# NFC to HTML Mapping System

This system allows you to associate NFC chips with HTML files and automatically display the content when an NFC chip is detected.

## Components

1. **Web Interface** (`nfc_web_server.py`) - A Flask-based web application for managing NFC mappings
2. **NFC Player** (`nfc_player.py`) - Continuously monitors for NFC chips and opens associated HTML files
3. **HTML Content** (`html_content/`) - Directory containing your HTML files

## Installation

### Method 1: Using Virtual Environment (Recommended)

1. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

2. The setup script will create a virtual environment and install all dependencies.

### Method 2: Using System Packages (Raspberry Pi)

1. Run the system package setup:
```bash
chmod +x setup_system_packages.sh
./setup_system_packages.sh
```

### Method 3: Manual Virtual Environment

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements-rpi.txt  # On Raspberry Pi
# OR
pip install -r requirements.txt      # On development machine
```

### Hardware Setup

Ensure your PN532 NFC reader is connected to your Raspberry Pi via UART

## Usage

### Quick Start (After Installation)

```bash
chmod +x run_nfc_system.sh
./run_nfc_system.sh
```

This will start both the web server and prompt you to start the NFC player.

### Manual Start

#### Step 1: Start the Web Server

If using virtual environment:
```bash
source venv/bin/activate
python3 nfc_web_server.py
```

Or without virtual environment:
```bash
python3 nfc_web_server.py
```

The web interface will be available at `http://localhost:5000` (or `http://[raspberry-pi-ip]:5000` from another device).

### Step 2: Add HTML Content

Place your HTML files in the `html_content/` directory. These files will be available for mapping to NFC chips.

### Step 3: Create Mappings

Using the web interface:
1. Place an NFC chip on the reader - the UID will be automatically detected
2. Select an HTML file from the dropdown
3. Optionally add a description
4. Click "Save Mapping"

### Step 4: Run the Player

In a separate terminal, run the NFC player:

```bash
python3 nfc_player.py
```

Now when you place a mapped NFC chip on the reader, the associated HTML file will open automatically.

## File Structure

```
HapticCollectionMediaPlayer/
├── nfc_web_server.py      # Web interface server
├── nfc_player.py          # NFC detection and HTML launcher
├── nfc_mappings.json      # Stores NFC to HTML mappings
├── requirements.txt       # Python dependencies
├── web_interface/         # Web interface files
│   └── index.html        # Main web interface
├── html_content/          # Your HTML files go here
│   └── sample.html       # Example HTML file
└── python/               # Existing PN532 library files
```

## Features

- **Auto-detection**: NFC chips are automatically detected when placed on the reader
- **Web-based Management**: Easy-to-use interface for creating and managing mappings
- **Real-time Updates**: The player automatically loads new mappings
- **Multiple File Support**: Map different NFC chips to different HTML files
- **Kiosk Mode**: On Raspberry Pi, HTML files open in fullscreen kiosk mode

## Troubleshooting

### NFC Not Detecting Cards

If the web interface opens but doesn't detect NFC cards:

1. **Test with the debug script:**
   ```bash
   python3 test_nfc.py
   ```
   This uses the exact same pattern as the working example.

2. **Try the simple server (no threading):**
   ```bash
   python3 simple_nfc_server.py
   ```
   This removes threading complications.

3. **Run the debug script:**
   ```bash
   python3 debug_nfc.py
   ```
   This will show detailed import and initialization information.

4. **Check console output** for error messages when starting `nfc_web_server.py`

5. **Verify the working example still works:**
   ```bash
   cd python
   python3 example_get_uid.py
   ```

### Common Issues

- **NFC Reader Not Found**: Ensure the PN532 is properly connected and powered
- **Permission Errors**: Run with `sudo` if you encounter GPIO permission issues
- **Port Already in Use**: Change the port in `nfc_web_server.py` if 5000 is occupied
- **Import Errors**: Make sure you're running from the HapticCollectionMediaPlayer directory

## Development Mode

The web interface includes a "Test with Random UID" button for testing without an actual NFC reader.
