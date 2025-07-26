#!/bin/bash

echo "========================================="
echo "Setting up NFC Player as System Service"
echo "========================================="

# Get current user and directory
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

# Create service file with correct paths
cat > nfc-player.service << EOF
[Unit]
Description=NFC HTML Player Service
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/nfc_player.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created with:"
echo "  User: $CURRENT_USER"
echo "  Directory: $CURRENT_DIR"

# Copy to systemd
echo ""
echo "Installing service (requires sudo)..."
sudo cp nfc-player.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
echo "Enabling service to start on boot..."
sudo systemctl enable nfc-player.service

# Start service
echo "Starting service..."
sudo systemctl start nfc-player.service

# Check status
echo ""
echo "Checking service status..."
sudo systemctl status nfc-player.service

echo ""
echo "========================================="
echo "Service Commands:"
echo "  Start:   sudo systemctl start nfc-player"
echo "  Stop:    sudo systemctl stop nfc-player"
echo "  Status:  sudo systemctl status nfc-player"
echo "  Logs:    sudo journalctl -u nfc-player -f"
echo "  Disable: sudo systemctl disable nfc-player"
echo "========================================="
