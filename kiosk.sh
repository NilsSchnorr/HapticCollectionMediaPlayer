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
# The lock file descriptor (9) stays open for the lifetime of this
# script, and the script waits on the browser at the end — so the lock
# is held for as long as the kiosk browser is running.
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

# Give the desktop session a moment to finish compositing before the
# browser makes its first paint (reduces the white-screen race).
sleep 3

# -----------------------------------------
# Launch Chromium in kiosk mode.
# Launched in the background (not exec) so we can trigger the
# first-load refresh below; the script waits on the browser at the
# end, keeping the single-instance lock held while it runs.
# -----------------------------------------
"$BROWSER" --kiosk --noerrdialogs --disable-infobars \
    --disable-session-crashed-bubble --disable-restore-session-state \
    "$URL" &
BROWSER_PID=$!

# -----------------------------------------
# Automatic first-load refresh (X11 only).
# On a cold boot, Chromium's very first paint can come up blank/white
# because the renderer starts before the desktop is fully ready. A
# single reload fixes it — this automates the manual Ctrl+R:
# wait for the kiosk window to appear, give the (possibly blank)
# first paint a moment, then send one F5 keypress.
# -----------------------------------------
if command -v xdotool > /dev/null && [ -n "$DISPLAY" ]; then
    (
        WID=$(timeout 30 xdotool search --sync --onlyvisible --class chromium 2>/dev/null | head -1)
        if [ -n "$WID" ]; then
            sleep 5
            xdotool windowactivate --sync "$WID" 2>/dev/null
            xdotool key --clearmodifiers F5 2>/dev/null
            echo "First-load refresh sent."
        fi
    ) &
else
    echo "NOTE: xdotool not available - skipping automatic first-load refresh."
    echo "      If the kiosk shows a white screen after boot, press F5 once,"
    echo "      and install the helper for next time:  sudo apt install xdotool"
fi

# Keep the script (and the lock) alive for the browser's lifetime.
wait "$BROWSER_PID"
