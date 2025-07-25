#!/bin/bash

# Fix Raspberry Pi UART mapping for PN532
# This script ensures /dev/serial0 points to the primary UART (ttyAMA0)

echo "🔧 Fixing Raspberry Pi UART mapping for PN532"
echo "=============================================="

# Backup current config
sudo cp /boot/config.txt /boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up /boot/config.txt"

# Remove conflicting UART settings
echo "🧹 Removing conflicting UART settings..."
sudo sed -i '/^dtoverlay=pi3-miniuart-bt/d' /boot/config.txt
sudo sed -i '/^dtoverlay=miniuart-bt/d' /boot/config.txt

# Add proper UART configuration
echo "📝 Adding correct UART configuration..."

# Check if enable_uart=1 exists, if not add it
if ! grep -q "^enable_uart=1" /boot/config.txt; then
    echo "enable_uart=1" | sudo tee -a /boot/config.txt > /dev/null
    echo "✅ Added enable_uart=1"
else
    echo "✅ enable_uart=1 already present"
fi

# Check if disable-bt exists, if not add it
if ! grep -q "^dtoverlay=disable-bt" /boot/config.txt; then
    echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt > /dev/null
    echo "✅ Added dtoverlay=disable-bt"
else
    echo "✅ dtoverlay=disable-bt already present"
fi

# Force primary UART for serial0
if ! grep -q "^dtoverlay=pi3-disable-bt" /boot/config.txt; then
    echo "dtoverlay=pi3-disable-bt" | sudo tee -a /boot/config.txt > /dev/null
    echo "✅ Added dtoverlay=pi3-disable-bt"
else
    echo "✅ dtoverlay=pi3-disable-bt already present"
fi

# Check for serial console conflicts in cmdline.txt
echo "🔍 Checking for serial console conflicts..."
if grep -q "console=serial0\|console=ttyAMA0" /boot/cmdline.txt; then
    echo "⚠️  Found serial console in cmdline.txt, removing..."
    sudo cp /boot/cmdline.txt /boot/cmdline.txt.backup.$(date +%Y%m%d_%H%M%S)
    sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt
    sudo sed -i 's/console=ttyAMA0,115200 //g' /boot/cmdline.txt
    echo "✅ Removed serial console conflicts"
else
    echo "✅ No serial console conflicts found"
fi

# Show final configuration
echo ""
echo "📋 Final UART configuration in /boot/config.txt:"
echo "------------------------------------------------"
grep -E "(uart|bluetooth|serial)" /boot/config.txt | grep -v "^#"

echo ""
echo "🔄 Changes made. System needs to reboot for changes to take effect."
echo ""
echo "After reboot, /dev/serial0 should point to ttyAMA0"
echo ""

read -p "Reboot now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Rebooting..."
    sudo reboot
else
    echo "🔄 Please reboot manually: sudo reboot"
fi
