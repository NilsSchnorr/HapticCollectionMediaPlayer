#!/bin/bash

echo "========================================="
echo "Installing System Packages for NFC System"
echo "========================================="

# This script installs packages using apt instead of pip
# Useful for avoiding virtual environment on Raspberry Pi

echo "Updating package list..."
sudo apt update

echo "Installing Python packages via apt..."
sudo apt install -y python3-flask python3-serial python3-spidev

echo "Installing RPi.GPIO if not already installed..."
sudo apt install -y python3-rpi.gpio

# Note: PN532 library might not be available via apt
# In that case, we'll need to use pip with --break-system-packages
echo ""
echo "Some packages might not be available via apt."
echo "Installing remaining packages with pip..."

# Create a list of packages that might need pip
pip3 install --break-system-packages adafruit-circuitpython-pn532

echo ""
echo "✅ System packages installed!"
echo ""
echo "You can now run the system directly with:"
echo "  python3 nfc_web_server.py  (in one terminal)"
echo "  python3 nfc_player.py      (in another terminal)"
