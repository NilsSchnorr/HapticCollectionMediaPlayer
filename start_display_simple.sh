#!/bin/bash

echo "========================================="
echo "NFC Display System - Simple Mode"
echo "========================================="

# Start the display system
echo "Starting display system..."
python3 nfc_display.py &
DISPLAY_PID=$!

# Wait for startup
sleep 2

# Open in regular browser window
echo "Opening in browser..."
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:8080
elif command -v open > /dev/null; then
    open http://localhost:8080
else
    echo "Please open http://localhost:8080 in your browser"
fi

echo ""
echo "Display system is running!"
echo ""
echo "To stop: Press Ctrl+C"
echo ""

# Wait and handle Ctrl+C
trap "kill $DISPLAY_PID 2>/dev/null; echo 'Stopped.'; exit 0" INT
wait $DISPLAY_PID
