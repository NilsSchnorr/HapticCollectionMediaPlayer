#!/bin/bash

echo "========================================="
echo "HCMP Autostart Installer"
echo "========================================="
echo ""
echo "This script sets up the Haptic Collection"
echo "Media Player to start automatically when"
echo "the Raspberry Pi boots."
echo ""
echo "It will:"
echo "  1. Install a systemd service for the"
echo "     NFC display backend"
echo "  2. Set up Chromium to open in kiosk mode"
echo "     when the desktop loads"
echo "  3. Disable screen blanking"
echo "  4. Enable auto-login (if not already)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Get current user and directory
CURRENT_USER=$(whoami)
CURRENT_DIR=$(cd "$(dirname "$0")" && pwd)

echo ""
echo "Detected:"
echo "  User: $CURRENT_USER"
echo "  Project directory: $CURRENT_DIR"
echo ""

# -----------------------------------------
# Step 1: Install systemd service
# -----------------------------------------
echo "[1/4] Installing systemd service..."

# Generate service file with correct paths
sed -e "s|@@USER@@|$CURRENT_USER|g" \
    -e "s|@@WORKDIR@@|$CURRENT_DIR|g" \
    "$CURRENT_DIR/hcmp-display.service" > /tmp/hcmp-display.service

sudo cp /tmp/hcmp-display.service /etc/systemd/system/hcmp-display.service
rm /tmp/hcmp-display.service

sudo systemctl daemon-reload
sudo systemctl enable hcmp-display.service
echo "  Service installed and enabled."

# -----------------------------------------
# Step 2: Set up LXDE autostart for Chromium
# -----------------------------------------
echo "[2/4] Setting up Chromium kiosk autostart..."

AUTOSTART_DIR="/home/$CURRENT_USER/.config/lxsession/LXDE-pi"
AUTOSTART_FILE="$AUTOSTART_DIR/autostart"

# Create directory if it doesn't exist
mkdir -p "$AUTOSTART_DIR"

# If the file exists, remove any previous HCMP entries
if [ -f "$AUTOSTART_FILE" ]; then
    # Remove old HCMP lines (between markers)
    sed -i '/^# --- HCMP START ---$/,/^# --- HCMP END ---$/d' "$AUTOSTART_FILE"
else
    # Create fresh autostart with the default LXDE entries
    cat > "$AUTOSTART_FILE" << 'EOF'
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
EOF
fi

# Append HCMP autostart block
cat >> "$AUTOSTART_FILE" << EOF
# --- HCMP START ---
# Disable screen blanking and DPMS
@xset s off
@xset -dpms
@xset s norestart
# Wait for the display backend to be ready, then open Chromium in kiosk mode
@bash -c 'sleep 10 && chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble --disable-restore-session-state http://localhost:8080'
# --- HCMP END ---
EOF

echo "  Chromium kiosk autostart configured."

# -----------------------------------------
# Step 3: Disable screen blanking
# -----------------------------------------
echo "[3/4] Disabling screen blanking..."

# Use raspi-config non-interactively if available
if command -v raspi-config > /dev/null; then
    sudo raspi-config nonint do_blanking 1 2>/dev/null
    echo "  Screen blanking disabled via raspi-config."
else
    echo "  raspi-config not found, skipping (use xset fallback in autostart)."
fi

# -----------------------------------------
# Step 4: Enable auto-login
# -----------------------------------------
echo "[4/4] Enabling desktop auto-login..."

if command -v raspi-config > /dev/null; then
    # B4 = Desktop Autologin
    sudo raspi-config nonint do_boot_behaviour B4 2>/dev/null
    echo "  Auto-login to desktop enabled."
else
    echo "  raspi-config not found. Please enable auto-login manually:"
    echo "  sudo raspi-config → System Options → Boot / Auto Login → Desktop Autologin"
fi

# -----------------------------------------
# Done
# -----------------------------------------
echo ""
echo "========================================="
echo "Autostart setup complete!"
echo "========================================="
echo ""
echo "On next boot, the Pi will:"
echo "  1. Auto-login to the desktop"
echo "  2. Start the NFC display backend"
echo "  3. Open Chromium in fullscreen kiosk mode"
echo "  4. Keep the screen on indefinitely"
echo ""
echo "Useful commands:"
echo "  Stop display:    sudo systemctl stop hcmp-display"
echo "  Start display:   sudo systemctl start hcmp-display"
echo "  View logs:       sudo journalctl -u hcmp-display -f"
echo "  Disable:         Run ./uninstall_autostart.sh"
echo ""
echo "Reboot now to test? (y/n)"
read -p "" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo reboot
fi
