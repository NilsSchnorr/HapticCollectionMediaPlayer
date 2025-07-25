#!/bin/bash

# Start NFC Display System with Waveshare PN532 HAT
# This script runs the main NFC display application

cd "$(dirname "$0")"

echo "🚀 Starting NFC Display System (Waveshare PN532)"
echo "📍 Project Directory: $(pwd)"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Check if required files exist
if [ ! -f "main_waveshare.py" ]; then
    echo "❌ Error: main_waveshare.py not found!"
    exit 1
fi

if [ ! -f "config_waveshare.py" ]; then
    echo "❌ Error: config_waveshare.py not found!"
    exit 1
fi

# Check if database directory exists
mkdir -p data logs

echo "🏷️  Starting NFC tag detection..."
echo "📋 Hardware checklist:"
echo "   • Jumpers: L0->L, L1->L, RSTPDN->D20"
echo "   • DIP switches: RX=ON, TX=ON, others=OFF"
echo "   • UART enabled in raspi-config"
echo ""
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run the main application
python3 main_waveshare.py
