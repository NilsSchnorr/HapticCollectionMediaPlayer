#!/bin/bash
# Script to run the NFC system from the python directory
# This matches the working example's environment

cd "$(dirname "$0")/python"
echo "Changed to python directory: $(pwd)"
echo "Running NFC web server..."
python3 ../nfc_web_server.py
