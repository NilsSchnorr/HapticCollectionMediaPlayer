#!/bin/bash

# Start NFC Display System with Fixed PN532 (Working NFC-Player Approach)
# This script uses the exact same approach as the working NFC-Player

cd "$(dirname "$0")"

echo "🚀 Starting NFC Display System (Fixed PN532 - Working Approach)"
echo "📍 Project Directory: $(pwd)"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Check if required files exist
if [ ! -f "main_fixed.py" ]; then
    echo "❌ Error: main_fixed.py not found!"
    exit 1
fi

if [ ! -f "PN532_fixed.py" ]; then
    echo "❌ Error: PN532_fixed.py not found!"
    exit 1
fi

# Check if database directory exists
mkdir -p data logs

echo "🏷️  Starting NFC tag detection with WORKING approach..."
echo "📋 Key differences from previous attempts:"
echo "   • Using /dev/ttyS0 instead of /dev/ttyAMA0"
echo "   • Using working NFC-Player's wake-up sequence"
echo "   • Using working NFC-Player's reset timing"
echo "   • Using working NFC-Player's retry mechanism"
echo ""
echo "📋 Hardware checklist:"
echo "   • Jumpers: L0->L, L1->L, RSTPDN->D20"
echo "   • DIP switches: RX=ON, TX=ON, others=OFF"
echo "   • UART enabled in raspi-config"
echo ""
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run the fixed main application
python3 main_fixed.py
