#!/bin/bash

echo "================================"
echo "NFC Display System Setup"
echo "================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    chromium-browser \
    git

# Create project directory
PROJECT_DIR="$HOME/nfc-display"
echo "Creating project directory at $PROJECT_DIR..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create directory structure
mkdir -p html static data logs

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies based on reader type
echo "Which NFC reader are you using?"
echo "1) PN532 NFC HAT (connected to GPIO pins via I2C/SPI/UART)"
echo "2) PN532 USB module"
echo "3) RC522 (SPI)"
read -p "Enter choice (1, 2, or 3): " reader_choice

if [ "$reader_choice" = "1" ]; then
    echo "Installing PN532 NFC HAT dependencies..."
    pip install nfcpy
    
    # Enable I2C for PN532 HAT
    echo "Enabling I2C interface for PN532 NFC HAT..."
    sudo raspi-config nonint do_i2c 0
    
    # Install I2C tools
    echo "Installing I2C tools..."
    sudo apt-get install -y i2c-tools
    
    # Add user to i2c group
    sudo usermod -a -G i2c $USER
    echo "Added $USER to i2c group (you may need to log out and back in)"
    
    # Update config.py to use PN532 with I2C
    sed -i 's/READER_TYPE = ".*"/READER_TYPE = "PN532"/' config.py 2>/dev/null
    sed -i 's/PN532_INTERFACE = ".*"/PN532_INTERFACE = "i2c"/' config.py 2>/dev/null
    
    echo ""
    echo "PN532 NFC HAT setup complete!"
    echo "Note: The HAT is configured for I2C by default."
    echo "If you need SPI or UART, edit config.py and change PN532_INTERFACE"
    
elif [ "$reader_choice" = "2" ]; then
    echo "Installing PN532 USB dependencies..."
    pip install nfcpy
    
    # Update config.py to use PN532 with USB
    sed -i 's/READER_TYPE = ".*"/READER_TYPE = "PN532"/' config.py 2>/dev/null
    sed -i 's/PN532_INTERFACE = ".*"/PN532_INTERFACE = "usb"/' config.py 2>/dev/null
    
elif [ "$reader_choice" = "3" ]; then
    echo "Installing RC522 dependencies..."
    pip install mfrc522 RPi.GPIO
    # Enable SPI
    sudo raspi-config nonint do_spi 0
    # Update config.py to use RC522
    sed -i 's/READER_TYPE = ".*"/READER_TYPE = "RC522"/' config.py 2>/dev/null || echo "Note: Update READER_TYPE in config.py to RC522"
else
    echo "Invalid choice. Please run setup again."
    exit 1
fi

# Install web interface dependencies
echo "Installing web interface dependencies..."
pip install Flask Flask-SocketIO python-socketio

# Create default HTML files
echo "Creating default HTML files..."

# Create home_base.html if it doesn't exist
if [ ! -f "html/home_base.html" ]; then
    echo "Creating home_base.html..."
    cat > html/home_base.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFC Display - Ready</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        h1 { font-size: 3rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ready to Scan</h1>
        <p>Place an NFC tag on the reader</p>
    </div>
</body>
</html>
EOF
fi

# Create unknown_tag.html if it doesn't exist
if [ ! -f "html/unknown_tag.html" ]; then
    echo "Creating unknown_tag.html..."
    cat > html/unknown_tag.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unknown Tag</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #e74c3c;
            color: white;
        }
    </style>
</head>
<body>
    <div>
        <h1>Unknown Tag</h1>
        <p>This tag is not registered in the system</p>
    </div>
</body>
</html>
EOF
fi

# Initialize database
echo "Initializing database..."
python3 setup_db.py

# Set up auto-start
read -p "Set up auto-start on boot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting up systemd service..."
    
    # Create service file
    sudo tee /etc/systemd/system/nfc-display.service > /dev/null << EOF
[Unit]
Description=NFC Display Service
After=multi-user.target graphical.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="DISPLAY=:0"
Environment="XAUTHORITY=$HOME/.Xauthority"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

    # Enable service
    sudo systemctl daemon-reload
    sudo systemctl enable nfc-display.service
    echo "Auto-start enabled. The service will start on next boot."
    echo "To start now: sudo systemctl start nfc-display.service"
fi

# Create a simple launcher script
cat > start_nfc_display.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 main.py
EOF
chmod +x start_nfc_display.sh

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Copy your Python scripts (main.py, database.py, config.py, etc.) to $PROJECT_DIR"
echo "2. Add your custom HTML files to $PROJECT_DIR/html/"
echo "3. Run the test script: python3 test_presence.py"
echo "4. Start the system: ./start_nfc_display.sh"
echo ""
echo "To manage tags:"
echo "  python3 manage_tags.py list"
echo "  python3 manage_tags.py add <UID> <name> <HTML-file>"
echo "  python3 manage_tags.py interactive"
echo ""
