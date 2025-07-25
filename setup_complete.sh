#!/bin/bash

# Complete Setup Script for Fresh Raspberry Pi
# This script sets up everything needed for the NFC Media Player

echo "🚀 NFC Media Player - Complete Setup"
echo "===================================="

# Check if running as regular user
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run this script as a regular user (not with sudo)"
    echo "The script will ask for sudo when needed"
    exit 1
fi

echo "📋 This script will:"
echo "1. Install system dependencies"
echo "2. Configure UART for PN532"
echo "3. Set up Python environment"
echo "4. Create project files"
echo "5. Test hardware"
echo ""

read -p "Continue with setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 1
fi

# Step 1: Install system dependencies
echo ""
echo "📦 Step 1: Installing system dependencies..."
sudo apt update
sudo apt install -y git python3-pip python3-venv i2c-tools

# Step 2: Configure UART
echo ""
echo "⚙️ Step 2: Configuring UART..."

# Backup config files
sudo cp /boot/config.txt /boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)

# Add UART configuration
if ! grep -q "^enable_uart=1" /boot/config.txt; then
    echo "enable_uart=1" | sudo tee -a /boot/config.txt > /dev/null
    echo "✅ Added enable_uart=1"
else
    echo "✅ enable_uart=1 already present"
fi

if ! grep -q "^dtoverlay=disable-bt" /boot/config.txt; then
    echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt > /dev/null
    echo "✅ Added dtoverlay=disable-bt"
else
    echo "✅ dtoverlay=disable-bt already present"
fi

# Disable Bluetooth services
sudo systemctl disable bluetooth 2>/dev/null || true
sudo systemctl stop bluetooth 2>/dev/null || true
echo "✅ Bluetooth disabled"

# Add user to dialout group
sudo usermod -a -G dialout $USER
echo "✅ User added to dialout group"

# Step 3: Set up Python environment
echo ""
echo "🐍 Step 3: Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install pyserial RPi.GPIO Flask Flask-SocketIO python-socketio
echo "✅ Python dependencies installed"

# Step 4: Create project structure
echo ""
echo "📁 Step 4: Creating project structure..."

# Create directories
mkdir -p data logs html static templates

# Create database directory
mkdir -p data

echo "✅ Project directories created"

# Step 5: Show hardware checklist
echo ""
echo "🔧 Step 5: Hardware Configuration Required"
echo "=========================================="
echo "IMPORTANT: Configure your Waveshare PN532 HAT:"
echo ""
echo "📌 Jumper Settings:"
echo "   • L0 ↔ L (connect with jumper cap)"
echo "   • L1 ↔ L (connect with jumper cap)"
echo "   • RSTPDN ↔ D20 (connect with jumper cap)"
echo ""
echo "📌 DIP Switch Settings (use tweezers):"
echo "   • Switch 1 (RX): ON"
echo "   • Switch 2 (TX): ON"
echo "   • Switch 3: OFF"
echo "   • Switch 4: OFF"
echo ""
echo "📌 Physical Installation:"
echo "   • HAT sits flush on all 40 GPIO pins"
echo "   • Power LED on HAT should be lit"
echo "   • No bent or misaligned pins"
echo ""

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure hardware as shown above"
echo "2. Reboot: sudo reboot"
echo "3. After reboot, test hardware: python3 test_hardware.py"
echo "4. Run media player: ./start_media_player.sh"
echo ""

read -p "Reboot now to apply UART changes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Rebooting..."
    sudo reboot
else
    echo ""
    echo "⚠️  Please reboot manually before testing: sudo reboot"
fi
