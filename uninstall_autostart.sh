#!/bin/bash

echo "========================================="
echo "HCMP Autostart Uninstaller"
echo "========================================="
echo ""
echo "This will remove the autostart setup so"
echo "the HCMP no longer starts on boot."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

CURRENT_USER=$(whoami)

# -----------------------------------------
# Step 1: Remove systemd service
# -----------------------------------------
echo "[1/2] Removing systemd service..."

sudo systemctl stop hcmp-display.service 2>/dev/null
sudo systemctl disable hcmp-display.service 2>/dev/null
sudo rm -f /etc/systemd/system/hcmp-display.service
sudo systemctl daemon-reload
echo "  Service removed."

# -----------------------------------------
# Step 2: Remove LXDE autostart entries
# -----------------------------------------
echo "[2/2] Removing Chromium kiosk autostart..."

AUTOSTART_FILE="/home/$CURRENT_USER/.config/lxsession/LXDE-pi/autostart"

if [ -f "$AUTOSTART_FILE" ]; then
    sed -i '/^# --- HCMP START ---$/,/^# --- HCMP END ---$/d' "$AUTOSTART_FILE"
    echo "  Autostart entries removed."
else
    echo "  No autostart file found, nothing to remove."
fi

echo ""
echo "========================================="
echo "Autostart removed."
echo "========================================="
echo ""
echo "The HCMP will no longer start on boot."
echo "You can still run it manually with:"
echo "  ./start_display.sh"
echo ""
echo "Note: Screen blanking and auto-login"
echo "settings were not changed. Adjust via"
echo "sudo raspi-config if needed."
echo "========================================="
