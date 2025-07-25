#!/bin/bash

# PN532 UART Quick Setup Script
# This script helps configure your Raspberry Pi for UART communication with PN532

echo "=== PN532 UART Setup Script ==="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run this script as a regular user (not with sudo)"
    echo "The script will ask for sudo when needed"
    exit 1
fi

echo "This script will:"
echo "1. Enable UART interface"
echo "2. Disable Bluetooth (to avoid conflicts)"
echo "3. Add user to dialout group"
echo "4. Update system configuration"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 1
fi

echo ""
echo "Step 1: Adding user to dialout group..."
sudo usermod -a -G dialout $USER
echo "✓ User added to dialout group"

echo ""
echo "Step 2: Updating /boot/config.txt..."

# Backup original config
sudo cp /boot/config.txt /boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)

# Check if UART is already enabled
if grep -q "^enable_uart=1" /boot/config.txt; then
    echo "✓ UART already enabled"
else
    echo "enable_uart=1" | sudo tee -a /boot/config.txt > /dev/null
    echo "✓ UART enabled"
fi

# Check if Bluetooth disable is already set
if grep -q "^dtoverlay=disable-bt" /boot/config.txt; then
    echo "✓ Bluetooth disable already set"
else
    echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt > /dev/null
    echo "✓ Bluetooth disabled"
fi

echo ""
echo "Step 3: Checking cmdline.txt for serial console conflicts..."

# Backup cmdline.txt
sudo cp /boot/cmdline.txt /boot/cmdline.txt.backup.$(date +%Y%m%d_%H%M%S)

# Remove serial console parameters that might conflict
if grep -q "console=serial0" /boot/cmdline.txt || grep -q "console=ttyAMA0" /boot/cmdline.txt; then
    echo "Removing serial console parameters from cmdline.txt..."
    sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt
    sudo sed -i 's/console=ttyAMA0,115200 //g' /boot/cmdline.txt
    echo "✓ Serial console parameters removed"
else
    echo "✓ No conflicting serial console parameters found"
fi

echo ""
echo "Step 4: Disabling Bluetooth service..."
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth
echo "✓ Bluetooth service disabled"

echo ""
echo "=== Hardware Configuration Required ==="
echo ""
echo "IMPORTANT: You must physically configure your PN532 HAT:"
echo ""
echo "FOR WAVESHARE PN532 HAT (if you have this specific model):"
echo "1. Power off your Raspberry Pi: sudo shutdown -h now"
echo "2. Configure Jumpers:"
echo "   - Connect L0 to L"
echo "   - Connect L1 to L"
echo "   - Connect RSTPDN to D20"
echo "3. Configure DIP Switches (use tweezers):"
echo "   - Set RX switch to ON"
echo "   - Set TX switch to ON"
echo "   - Set all other switches to OFF"
echo ""
echo "FOR GENERIC PN532 HAT:"
echo "1. Power off your Raspberry Pi: sudo shutdown -h now"
echo "2. Locate the jumpers on your PN532 HAT"
echo "3. Move BOTH jumpers from 'I2C' position to 'UART'/'HSU' position"
echo ""
echo "   Typical jumper layout:"
echo "   [HSU] [I2C] [SPI]"
echo "     ↑     ↑     ↑"
echo "   Move jumpers from I2C to HSU/UART"
echo ""
echo "4. Power on your Raspberry Pi"
echo ""

echo "=== Configuration Complete ==="
echo ""
echo "After changing the jumpers and rebooting:"
echo ""
echo "1. Test the connection:"
echo "   python3 test_presence.py"
echo ""
echo "2. Run the main application:"
echo "   ./start_nfc_display.sh"
echo ""
echo "If you encounter issues, see PN532_UART_SETUP.md for troubleshooting"
echo ""

read -p "Reboot now to apply changes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rebooting..."
    sudo reboot
else
    echo ""
    echo "Please reboot manually when ready:"
    echo "sudo reboot"
fi
