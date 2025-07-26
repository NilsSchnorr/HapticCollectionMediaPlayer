#!/bin/bash

# Run script that automatically uses virtual environment

echo "========================================="
echo "Starting NFC to HTML Mapping System"
echo "========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    bash setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Start the system
python3 start_nfc_system.py
