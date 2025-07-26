#!/bin/bash

echo "========================================="
echo "Starting NFC Display System"
echo "========================================="

# Check if management server is running on port 5000
if lsof -i:5000 > /dev/null 2>&1; then
    echo "Note: Management interface is running on port 5000"
fi

# Check if display is already running
if lsof -i:8080 > /dev/null 2>&1; then
    echo "Error: Port 8080 is already in use!"
    echo "The display system may already be running."
    exit 1
fi

# Start the display system
echo "Starting display system on port 8080..."
python3 nfc_display.py &
DISPLAY_PID=$!

# Wait for it to start
sleep 3

# Open in browser (fullscreen if possible)
echo "Opening display interface..."
if command -v chromium-browser > /dev/null; then
    # Raspberry Pi with Chromium
    chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble http://localhost:8080 &
elif command -v chromium > /dev/null; then
    # Alternative Chromium command
    chromium --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble http://localhost:8080 &
elif command -v firefox > /dev/null; then
    # Firefox
    firefox --kiosk http://localhost:8080 &
else
    # Default browser
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:8080
    elif command -v open > /dev/null; then
        open http://localhost:8080
    fi
fi

echo ""
echo "========================================="
echo "Display System Running"
echo "========================================="
echo "Display URL: http://localhost:8080"
echo ""
echo "Instructions:"
echo "1. Place an NFC chip on the reader"
echo "2. The mapped HTML content will display"
echo "3. Remove the chip to return to home"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================="

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down display system..."
    kill $DISPLAY_PID 2>/dev/null
    # Kill browser if in kiosk mode
    pkill -f "chromium.*--kiosk.*8080" 2>/dev/null
    pkill -f "firefox.*--kiosk.*8080" 2>/dev/null
    echo "Display system stopped."
    exit 0
}

# Set trap for cleanup
trap cleanup INT

# Keep running
wait $DISPLAY_PID
