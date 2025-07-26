#!/bin/bash

# Make all shell scripts executable
echo "Making shell scripts executable..."
chmod +x setup.sh
chmod +x run_nfc_system.sh
chmod +x setup_system_packages.sh
chmod +x start_nfc_system.sh
chmod +x run_from_python_dir.sh
chmod +x start_both.sh
chmod +x check_status.sh
chmod +x install_service.sh
chmod +x start_player_background.sh
chmod +x start_display.sh
chmod +x start_display_simple.sh
chmod +x start_demo.sh

# Make Python scripts executable
echo "Making Python scripts executable..."
chmod +x nfc_web_server.py
chmod +x nfc_player.py
chmod +x start_nfc_system.py
chmod +x test_nfc.py
chmod +x debug_nfc.py
chmod +x simple_nfc_server.py
chmod +x diagnose_nfc.py
chmod +x nfc_display.py
chmod +x nfc_display_demo.py

echo "All scripts are now executable!"
