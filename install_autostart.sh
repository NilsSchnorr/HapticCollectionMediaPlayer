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
echo "  2. Set up the Chromium kiosk launcher"
echo "     (works on X11/LXDE and Wayland/labwc)"
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
KIOSK_SCRIPT="$CURRENT_DIR/kiosk.sh"

echo ""
echo "Detected:"
echo "  User: $CURRENT_USER"
echo "  Project directory: $CURRENT_DIR"
echo "  Session type: ${XDG_SESSION_TYPE:-unknown}"
echo ""

# -----------------------------------------
# Step 1: Install systemd service
# -----------------------------------------
echo "[1/6] Installing systemd service..."

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
# Step 2: Prepare the kiosk launcher script
# -----------------------------------------
echo "[2/6] Preparing kiosk launcher..."

if [ ! -f "$KIOSK_SCRIPT" ]; then
    echo "  ERROR: kiosk.sh not found in $CURRENT_DIR"
    echo "  Did the git pull complete? Aborting."
    exit 1
fi
chmod +x "$KIOSK_SCRIPT"
echo "  kiosk.sh is executable."

# -----------------------------------------
# Step 3: LXDE autostart (X11 sessions)
#
# NOTE: lxsession's autostart parser cannot handle complex quoted
# commands like  @bash -c '...'  — such lines fail silently.
# That is why we reference a plain script path here.
# -----------------------------------------
echo "[3/6] Setting up LXDE autostart (X11)..."

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

# Append HCMP autostart block.
# The xset lines disable screen blanking on X11; on Wayland they are
# simply ignored. The kiosk launcher itself guards against double
# launches, so overlapping autostart mechanisms are safe.
cat >> "$AUTOSTART_FILE" << EOF
# --- HCMP START ---
@xset s off
@xset -dpms
@xset s norestart
@$KIOSK_SCRIPT
# --- HCMP END ---
EOF

echo "  LXDE autostart configured."

# -----------------------------------------
# Step 4: XDG autostart + labwc autostart (Wayland-proof)
#
# The XDG .desktop entry is honored by lxsession (X11) and most
# desktop environments. The labwc autostart file covers Raspberry
# Pi OS images (late 2024+) that boot into Wayland/labwc, which
# ignores both mechanisms above.
# kiosk.sh's lock guarantees only one kiosk ever starts, even if
# several of these mechanisms fire on the same system.
# -----------------------------------------
echo "[4/6] Setting up XDG and labwc autostart (Wayland)..."

# XDG autostart entry
XDG_AUTOSTART_DIR="/home/$CURRENT_USER/.config/autostart"
mkdir -p "$XDG_AUTOSTART_DIR"
cat > "$XDG_AUTOSTART_DIR/hcmp-kiosk.desktop" << EOF
[Desktop Entry]
Type=Application
Name=HCMP Kiosk
Comment=Haptic Collection Media Player fullscreen display
Exec=$KIOSK_SCRIPT
X-GNOME-Autostart-enabled=true
EOF
echo "  XDG autostart entry written."

# labwc autostart file (plain shell script run by labwc at session start)
LABWC_DIR="/home/$CURRENT_USER/.config/labwc"
LABWC_FILE="$LABWC_DIR/autostart"
mkdir -p "$LABWC_DIR"
if [ -f "$LABWC_FILE" ]; then
    sed -i '/^# --- HCMP START ---$/,/^# --- HCMP END ---$/d' "$LABWC_FILE"
fi
cat >> "$LABWC_FILE" << EOF
# --- HCMP START ---
$KIOSK_SCRIPT &
# --- HCMP END ---
EOF
echo "  labwc autostart entry written."

# -----------------------------------------
# Step 5: Disable screen blanking
# -----------------------------------------
echo "[5/6] Disabling screen blanking..."

# Use raspi-config non-interactively if available
if command -v raspi-config > /dev/null; then
    sudo raspi-config nonint do_blanking 1 2>/dev/null
    echo "  Screen blanking disabled via raspi-config."
else
    echo "  raspi-config not found, skipping (xset fallback in LXDE autostart)."
fi

# -----------------------------------------
# Step 6: Enable auto-login
# -----------------------------------------
echo "[6/6] Enabling desktop auto-login..."

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
echo "  Test kiosk now:  ./kiosk.sh"
echo "  Disable:         Run ./uninstall_autostart.sh"
echo ""
echo "Reboot now to test? (y/n)"
read -p "" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo reboot
fi
