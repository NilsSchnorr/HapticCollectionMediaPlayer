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
echo "[1/4] Removing systemd service..."

sudo systemctl stop hcmp-display.service 2>/dev/null
sudo systemctl disable hcmp-display.service 2>/dev/null
sudo rm -f /etc/systemd/system/hcmp-display.service
sudo systemctl daemon-reload
echo "  Service removed."

# -----------------------------------------
# Step 2: Remove LXDE autostart entries
# -----------------------------------------
echo "[2/4] Removing LXDE autostart entries..."

AUTOSTART_FILE="/home/$CURRENT_USER/.config/lxsession/LXDE-pi/autostart"

if [ -f "$AUTOSTART_FILE" ]; then
    sed -i '/^# --- HCMP START ---$/,/^# --- HCMP END ---$/d' "$AUTOSTART_FILE"
    echo "  LXDE autostart entries removed."
else
    echo "  No LXDE autostart file found, nothing to remove."
fi

# -----------------------------------------
# Step 3: Remove XDG autostart entry
# -----------------------------------------
echo "[3/4] Removing XDG autostart entry..."

XDG_DESKTOP_FILE="/home/$CURRENT_USER/.config/autostart/hcmp-kiosk.desktop"

if [ -f "$XDG_DESKTOP_FILE" ]; then
    rm -f "$XDG_DESKTOP_FILE"
    echo "  XDG autostart entry removed."
else
    echo "  No XDG autostart entry found, nothing to remove."
fi

# -----------------------------------------
# Step 4: Remove labwc autostart entries
# -----------------------------------------
echo "[4/4] Removing labwc autostart entries..."

LABWC_FILE="/home/$CURRENT_USER/.config/labwc/autostart"

if [ -f "$LABWC_FILE" ]; then
    sed -i '/^# --- HCMP START ---$/,/^# --- HCMP END ---$/d' "$LABWC_FILE"
    # Remove the file entirely if nothing else is left in it
    if [ ! -s "$LABWC_FILE" ]; then
        rm -f "$LABWC_FILE"
    fi
    echo "  labwc autostart entries removed."
else
    echo "  No labwc autostart file found, nothing to remove."
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
