#!/bin/bash

echo "========================================="
echo "Starting NFC System Components"
echo "========================================="

# Start web server in background
echo "Starting NFC Web Server..."
python3 nfc_web_server.py &
WEB_PID=$!
echo "Web server started with PID: $WEB_PID"

# Wait a moment for server to initialize
sleep 3

# Start NFC player in background
echo ""
echo "Starting NFC Player..."
python3 nfc_player.py &
PLAYER_PID=$!
echo "NFC Player started with PID: $PLAYER_PID"

# Open browser
sleep 2
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000
elif command -v open > /dev/null; then
    open http://localhost:5000
fi

echo ""
echo "========================================="
echo "SYSTEM RUNNING"
echo "========================================="
echo "Web Interface: http://localhost:5000"
echo "NFC Player: Active (watching for chips)"
echo ""
echo "To stop: Press Ctrl+C or close this terminal"
echo "========================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $WEB_PID 2>/dev/null
    kill $PLAYER_PID 2>/dev/null
    echo "All components stopped."
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup INT

# Keep script running and monitor processes
while true; do
    # Check if processes are still running
    if ! kill -0 $WEB_PID 2>/dev/null; then
        echo "Web server stopped unexpectedly!"
        cleanup
    fi
    if ! kill -0 $PLAYER_PID 2>/dev/null; then
        echo "NFC Player stopped unexpectedly!"
        # Optionally restart it
        echo "Restarting NFC Player..."
        python3 nfc_player.py &
        PLAYER_PID=$!
    fi
    sleep 5
done
