#!/bin/bash
#
# HCMP Kiosk Launcher
# -------------------
# Opens Chromium in fullscreen kiosk mode pointing at the HCMP display
# backend (http://localhost:8080).
#
# This script is referenced by the autostart entries that
# install_autostart.sh creates. Because it may be registered in more than
# one autostart mechanism (LXDE, XDG, labwc), it uses a lock so that only
# ONE kiosk instance ever runs — any additional invocation exits silently.
#
# It is also safe to run manually:  ./kiosk.sh

URL="http://localhost:8080"

# -----------------------------------------
# Guard 1: file lock (race-free single instance)
# The lock file descriptor is inherited by Chromium via exec, so the lock
# stays held for as long as the kiosk browser is running.
# -----------------------------------------
LOCKFILE="/tmp/hcmp-kiosk.lock"
exec 9>"$LOCKFILE"
if ! flock -n 9; then
    echo "HCMP kiosk is already running (lock held). Nothing to do."
    exit 0
fi

# -----------------------------------------
# Guard 2: belt-and-suspenders process check
# -----------------------------------------
if pgrep -f "chromium.*--kiosk.*localhost:8080" > /dev/null; then
    echo "HCMP kiosk browser already running. Nothing to do."
    exit 0
fi

# -----------------------------------------
# Pick the Chromium binary
# (the name differs between Raspberry Pi OS versions)
# -----------------------------------------
if command -v chromium-browser > /dev/null; then
    BROWSER="chromium-browser"
elif command -v chromium > /dev/null; then
    BROWSER="chromium"
else
    echo "ERROR: Chromium not found (tried 'chromium-browser' and 'chromium')." >&2
    exit 1
fi

# -----------------------------------------
# Wait for the display backend to respond (up to 60 seconds)
# instead of a blind sleep. Falls back to a fixed wait if no
# probe tool is available.
# -----------------------------------------
echo "Waiting for HCMP backend at $URL ..."
BACKEND_UP=0
for i in $(seq 1 60); do
    if command -v curl > /dev/null; then
        curl -s -o /dev/null --max-time 2 "$URL" && BACKEND_UP=1
    elif command -v wget > /dev/null; then
        wget -q -O /dev/null -T 2 "$URL" && BACKEND_UP=1
    else
        # No probe tool available: single blind wait, then proceed.
        sleep 10
        BACKEND_UP=1
    fi

    if [ "$BACKEND_UP" -eq 1 ]; then
        echo "Backend is up (waited ${i}s)."
        break
    fi
    sleep 1
done

if [ "$BACKEND_UP" -eq 0 ]; then
    echo "WARNING: Backend not reachable after 60s, starting browser anyway." >&2
    echo "         Check:  sudo systemctl status hcmp-display" >&2
fi

# -----------------------------------------
# Launch Chromium in kiosk mode
# -----------------------------------------
exec "$BROWSER" --kiosk --noerrdialogs --disable-infobars \
    --disable-session-crashed-bubble --disable-restore-session-state \
    "$URL"
