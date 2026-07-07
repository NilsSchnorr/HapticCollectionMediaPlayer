#!/bin/bash

echo "========================================="
echo "NFC Display System - DEMO MODE"
echo "========================================="
echo "This runs without NFC hardware!"
echo ""

# Start demo
python3 nfc_display_demo.py &
DEMO_PID=$!

sleep 2

# Open browser
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:8080
elif command -v open > /dev/null; then
    open http://localhost:8080
else
    echo "Please open http://localhost:8080"
fi

echo ""
echo "Demo is running!"
echo "Use buttons or keyboard keys 1-3 to simulate chips"
echo "Press 0 or ESC to remove chip"
echo ""
echo "Ctrl+C to stop"

trap "kill $DEMO_PID 2>/dev/null; echo 'Demo stopped.'; exit 0" INT
wait $DEMO_PID
