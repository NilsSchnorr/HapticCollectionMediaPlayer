#!/bin/bash
#
# HCMP Tag Mode
# -------------
# One-command switch from exhibition (kiosk) mode into the tag mapping
# interface — and back again, no reboot needed.
#
# What it does on start:
#   1. Closes the kiosk browser (pressing Alt+F4 first also works,
#      but is not required)
#   2. Stops the hcmp-display backend to free the NFC reader (/dev/ttyS0)
#   3. Starts the tag mapping interface (nfc_web_server.py)
#   4. Opens a normal browser window at http://localhost:5000
#
# When you are done mapping tags: press Ctrl+C in this terminal.
# The script then asks whether to return to exhibition mode.
#   y -> restarts the backend service and relaunches the kiosk
#   n -> stays on the desktop (backend remains stopped)
#
# NOTE on sudo: this script calls sudo systemctl stop/start. On a
# standard Raspberry Pi OS image the main user has passwordless sudo,
# so this just works. If your setup prompts for a password, either
# type it, or add a sudoers rule scoped to exactly these commands:
#   hcmp ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop hcmp-display, /usr/bin/systemctl start hcmp-display

cd "$(dirname "$0")"

URL="http://localhost:5000"

echo "========================================="
echo "HCMP - Tag Mapping Mode"
echo "========================================="

# -----------------------------------------
# Step 1: Close the kiosk browser (if running).
# kiosk.sh waits on the browser process, so it exits and releases
# its single-instance lock as soon as the browser is gone.
# -----------------------------------------
if pgrep -f "chromium.*--kiosk.*localhost:8080" > /dev/null; then
    echo "[1/4] Closing kiosk browser..."
    pkill -f "chromium.*--kiosk.*localhost:8080"
    sleep 2
else
    echo "[1/4] Kiosk browser not running, nothing to close."
fi

# -----------------------------------------
# Step 2: Stop the display backend to free the NFC reader.
# The backend holds /dev/ttyS0 exclusively — the mapping interface
# cannot initialize the reader while it runs.
# -----------------------------------------
echo "[2/4] Stopping display backend (frees the NFC reader)..."
sudo systemctl stop hcmp-display 2>/dev/null
# Also catch a manually started backend (running without the service)
pkill -f "python3.*nfc_display.py" 2>/dev/null
sleep 1

# -----------------------------------------
# Step 3: Start the tag mapping interface.
# Runs as a background child of this script; its log output stays
# visible in this terminal (watch for "NFC reader initialized
# successfully!" — if it says "development mode without NFC reader",
# the serial port was not free).
# -----------------------------------------
echo "[3/4] Starting tag mapping interface..."
python3 nfc_web_server.py &
WEB_PID=$!

# Wait for it to answer on port 5000 (up to 30 seconds)
UP=0
for i in $(seq 1 30); do
    if ! kill -0 "$WEB_PID" 2>/dev/null; then
        break   # process exited early
    fi
    if command -v curl > /dev/null; then
        curl -s -o /dev/null --max-time 2 "$URL" && UP=1
    elif command -v wget > /dev/null; then
        wget -q -O /dev/null -T 2 "$URL" && UP=1
    else
        sleep 5
        UP=1
    fi
    [ "$UP" -eq 1 ] && break
    sleep 1
done

if ! kill -0 "$WEB_PID" 2>/dev/null; then
    echo ""
    echo "ERROR: The mapping interface exited unexpectedly."
    echo "Check the messages above, then ./check_status.sh."
    echo "The display backend is currently STOPPED. Restore with:"
    echo "  sudo systemctl start hcmp-display && ./kiosk.sh"
    exit 1
fi

if [ "$UP" -eq 1 ]; then
    echo "      Interface is up."
else
    echo "      WARNING: No response on port 5000 yet - opening browser anyway."
fi

# -----------------------------------------
# Step 4: Open a normal (non-kiosk) browser window.
# -----------------------------------------
echo "[4/4] Opening browser at $URL ..."
if command -v chromium-browser > /dev/null; then
    chromium-browser "$URL" > /dev/null 2>&1 &
elif command -v chromium > /dev/null; then
    chromium "$URL" > /dev/null 2>&1 &
elif command -v xdg-open > /dev/null; then
    xdg-open "$URL" > /dev/null 2>&1 &
else
    echo "      No browser found - please open $URL manually."
fi

echo ""
echo "========================================="
echo "Tag mapping mode is ACTIVE."
echo "  Map your chips at: $URL"
echo "  When done: press Ctrl+C here."
echo "========================================="
echo ""

# -----------------------------------------
# Wait for Ctrl+C (or for the interface to exit on its own).
# Background children ignore SIGINT in scripts, so the trap forwards
# it as SIGTERM — which triggers the web server's own cleanup handler
# (closes the serial port, releases GPIO).
# -----------------------------------------
trap 'echo ""; echo "Stopping tag mapping interface..."; kill -TERM "$WEB_PID" 2>/dev/null' INT TERM

while kill -0 "$WEB_PID" 2>/dev/null; do
    wait "$WEB_PID" 2>/dev/null
done
trap - INT TERM

echo "Tag mapping interface stopped."
echo ""

# -----------------------------------------
# Offer the way back to exhibition mode.
# -----------------------------------------
read -p "Return to exhibition mode now (restart backend + kiosk)? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Restarting display backend..."
    sudo systemctl start hcmp-display

    # Close any remaining browser windows first: Chromium ignores
    # kiosk flags when joining an already-running instance, so the
    # kiosk must start from a fresh browser process.
    if pgrep -f chromium > /dev/null; then
        echo "Closing remaining browser windows..."
        pkill -f chromium 2>/dev/null
        sleep 2
    fi

    echo "Launching kiosk..."
    nohup ./kiosk.sh > /dev/null 2>&1 &
    disown
    echo ""
    echo "Exhibition mode restored. You can close this terminal."
else
    echo ""
    echo "Staying on the desktop. The display backend is STOPPED."
    echo "To return to exhibition mode later, either reboot or run:"
    echo "  sudo systemctl start hcmp-display && ./kiosk.sh"
fi
