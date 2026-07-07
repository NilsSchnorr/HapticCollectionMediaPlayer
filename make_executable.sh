#!/bin/bash

# Make all shell scripts executable
echo "Making shell scripts executable..."
chmod +x setup_system_packages.sh
chmod +x check_status.sh
chmod +x install_autostart.sh
chmod +x uninstall_autostart.sh
chmod +x kiosk.sh
chmod +x tag_mode.sh
chmod +x start_display_simple.sh
chmod +x start_demo.sh
chmod +x make_executable.sh

# Make Python scripts executable
echo "Making Python scripts executable..."
chmod +x nfc_display.py
chmod +x nfc_web_server.py
chmod +x nfc_display_demo.py

echo "All scripts are now executable!"
