#!/bin/bash
#
# HCMP Dependency Installer (Raspberry Pi)
# ----------------------------------------
# Installs everything the HCMP needs into the SYSTEM Python.
#
# IMPORTANT: Do NOT use a virtual environment on the Pi. The systemd
# service (hcmp-display.service) runs /usr/bin/python3, so dependencies
# installed only inside a venv will not be found at boot.
#
# This script needs an internet connection. Run it BEFORE the Pi is
# deployed offline in the exhibition.

set -e

echo "========================================="
echo "HCMP - Installing Dependencies"
echo "========================================="

# Make sure we run from the repo directory (so requirements-rpi.txt is found)
cd "$(dirname "$0")"

echo ""
echo "[1/3] Updating package list..."
sudo apt update

echo ""
echo "[2/3] Installing system packages (pip, xdotool)..."
# xdotool is used by kiosk.sh for the automatic first-load refresh
sudo apt install -y python3-pip xdotool

echo ""
echo "[3/3] Installing Python packages into system Python..."
sudo pip3 install --break-system-packages -r requirements-rpi.txt

echo ""
echo "========================================="
echo "Dependencies installed."
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Test the NFC reader:"
echo "       cd python && python3 example_get_uid.py"
echo "  2. Map your NFC chips (if needed):"
echo "       python3 nfc_web_server.py   ->  http://localhost:5000"
echo "  3. Set up boot-to-display mode:"
echo "       ./install_autostart.sh"
echo "========================================="
