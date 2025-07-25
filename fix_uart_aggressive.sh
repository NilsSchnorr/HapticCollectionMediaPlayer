#!/bin/bash

# Aggressive UART fix for stubborn Raspberry Pi models
# Forces primary UART to be available as /dev/serial0

echo "🔧 AGGRESSIVE UART FIX for Raspberry Pi"
echo "======================================="

# Check Pi model
echo "📋 Pi Model Information:"
cat /proc/device-tree/model && echo
echo ""

# Backup current config
sudo cp /boot/config.txt /boot/config.txt.backup.aggressive.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up /boot/config.txt"

# Remove ALL conflicting UART/Bluetooth settings
echo "🧹 Removing ALL conflicting settings..."
sudo sed -i '/dtoverlay=pi3-miniuart-bt/d' /boot/config.txt
sudo sed -i '/dtoverlay=miniuart-bt/d' /boot/config.txt
sudo sed -i '/dtoverlay=pi3-disable-bt/d' /boot/config.txt
sudo sed -i '/dtoverlay=disable-bt/d' /boot/config.txt
sudo sed -i '/enable_uart/d' /boot/config.txt
sudo sed -i '/dtparam=uart/d' /boot/config.txt

# Add comprehensive UART configuration
echo "📝 Adding comprehensive UART configuration..."

# Add at the end of the file
{
    echo ""
    echo "# PN532 UART Configuration - Aggressive"
    echo "enable_uart=1"
    echo "dtparam=uart0=on" 
    echo "dtoverlay=disable-bt"
    echo "dtoverlay=pi3-disable-bt"
    echo "core_freq=250"
} | sudo tee -a /boot/config.txt > /dev/null

echo "✅ Added comprehensive UART settings"

# Also disable Bluetooth services completely
echo "🔇 Disabling Bluetooth services..."
sudo systemctl disable bluetooth
sudo systemctl disable hciuart

# Check for firmware config that might override
if [ -f /boot/firmware/config.txt ]; then
    echo "⚠️  Found /boot/firmware/config.txt (newer Pi OS)"
    echo "   Also updating firmware config..."
    sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d_%H%M%S)
    
    # Apply same changes to firmware config
    sudo sed -i '/dtoverlay=pi3-miniuart-bt/d' /boot/firmware/config.txt
    sudo sed -i '/dtoverlay=miniuart-bt/d' /boot/firmware/config.txt
    sudo sed -i '/dtoverlay=pi3-disable-bt/d' /boot/firmware/config.txt
    sudo sed -i '/dtoverlay=disable-bt/d' /boot/firmware/config.txt
    sudo sed -i '/enable_uart/d' /boot/firmware/config.txt
    
    {
        echo ""
        echo "# PN532 UART Configuration - Aggressive"
        echo "enable_uart=1"
        echo "dtparam=uart0=on"
        echo "dtoverlay=disable-bt" 
        echo "dtoverlay=pi3-disable-bt"
        echo "core_freq=250"
    } | sudo tee -a /boot/firmware/config.txt > /dev/null
    
    echo "✅ Updated firmware config as well"
fi

# Show what we added
echo ""
echo "📋 UART Configuration added:"
echo "----------------------------"
echo "enable_uart=1"
echo "dtparam=uart0=on"
echo "dtoverlay=disable-bt"
echo "dtoverlay=pi3-disable-bt" 
echo "core_freq=250"

echo ""
echo "🔄 System must reboot for changes to take effect"
echo ""

read -p "Reboot now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Rebooting..."
    sudo reboot
else
    echo "🔄 Please reboot manually: sudo reboot"
fi
