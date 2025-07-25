#!/bin/bash

# Update service files with correct paths

echo "Updating service files for Desktop installation..."

# Get the current user and directory
CURRENT_USER=$(whoami)
PROJECT_DIR=$(pwd)

# Update nfc-display.service
cat > nfc-display.service << EOF
[Unit]
Description=NFC Display Service
After=multi-user.target graphical.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/$CURRENT_USER/.Xauthority"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

# Update nfc-web-interface.service
cat > nfc-web-interface.service << EOF
[Unit]
Description=NFC Tag Management Web Interface
After=multi-user.target network.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/web_interface.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Service files updated with current paths!"
echo "Current user: $CURRENT_USER"
echo "Project directory: $PROJECT_DIR"
