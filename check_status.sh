#!/bin/bash
#
# HCMP Status Check
# Shows what parts of the system are currently running.

echo "========================================="
echo "HCMP System Status"
echo "========================================="

# --- systemd service (autostart backend) ---
echo ""
echo "Autostart service (hcmp-display):"
if systemctl list-unit-files hcmp-display.service --no-legend 2>/dev/null | grep -q hcmp-display; then
    STATE=$(systemctl is-active hcmp-display.service 2>/dev/null)
    ENABLED=$(systemctl is-enabled hcmp-display.service 2>/dev/null)
    if [ "$STATE" = "active" ]; then
        echo "  ✓ Service: RUNNING (enabled: $ENABLED)"
    else
        echo "  ✗ Service: $STATE (enabled: $ENABLED)"
    fi
else
    echo "  - Service not installed (run ./install_autostart.sh to set up)"
fi

# --- Display backend (nfc_display.py, port 8080) ---
echo ""
echo "Display backend (nfc_display.py):"
if pgrep -f "nfc_display.py" > /dev/null; then
    echo "  ✓ Process: RUNNING (PID: $(pgrep -f 'nfc_display.py' | tr '\n' ' '))"
else
    echo "  ✗ Process: NOT RUNNING"
fi
if lsof -i:8080 > /dev/null 2>&1; then
    echo "  ✓ Port 8080: in use (display reachable at http://localhost:8080)"
else
    echo "  ✗ Port 8080: not in use"
fi

# --- Kiosk browser ---
echo ""
echo "Kiosk browser (Chromium):"
if pgrep -f "chromium.*--kiosk.*localhost:8080" > /dev/null; then
    echo "  ✓ Kiosk: RUNNING"
else
    echo "  ✗ Kiosk: NOT RUNNING"
fi

# --- Mapping interface (nfc_web_server.py, port 5000) ---
echo ""
echo "Tag mapping interface (nfc_web_server.py):"
if pgrep -f "nfc_web_server.py" > /dev/null; then
    echo "  ✓ Process: RUNNING (PID: $(pgrep -f 'nfc_web_server.py' | tr '\n' ' '))"
    echo "    NOTE: The mapping interface holds the NFC serial port."
    echo "    Stop it before starting the display backend."
else
    echo "  - Not running (normal during exhibition operation)"
fi
if lsof -i:5000 > /dev/null 2>&1; then
    echo "  ✓ Port 5000: in use (interface at http://localhost:5000)"
fi

# --- Mappings file ---
echo ""
if [ -f "nfc_mappings.json" ]; then
    MAPPINGS=$(grep -c '"html_file"' nfc_mappings.json)
    echo "✓ Mappings file exists ($MAPPINGS mapping(s))"
else
    echo "✗ No nfc_mappings.json found!"
    echo "  Note: this file is gitignored - copy it from another unit"
    echo "  or create mappings with: python3 nfc_web_server.py"
fi

echo ""
echo "========================================="
echo "Useful commands:"
echo "  Map new tags (guided):  ./tag_mode.sh"
echo "  Stop display backend:   sudo systemctl stop hcmp-display"
echo "  Start display backend:  sudo systemctl start hcmp-display"
echo "  Backend logs:           sudo journalctl -u hcmp-display -f"
echo "  Launch kiosk manually:  ./kiosk.sh"
echo "========================================="
