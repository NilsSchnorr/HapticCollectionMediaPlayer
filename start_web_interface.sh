#!/bin/bash
# Launcher script for NFC Tag Management Web Interface
# Make executable with: chmod +x start_web_interface.sh

cd "$(dirname "$0")"
source venv/bin/activate

echo "========================================"
echo "Starting NFC Tag Management Interface"
echo "========================================"
echo ""
echo "The interface will be available at:"
echo "  http://localhost:5000"
echo ""
echo "From other devices on your network:"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 web_interface.py
