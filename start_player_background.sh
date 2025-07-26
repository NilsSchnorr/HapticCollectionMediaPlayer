#!/bin/bash

echo "========================================="
echo "Starting NFC Player in Background"
echo "========================================="

# Check if already running
if pgrep -f "nfc_player.py" > /dev/null; then
    echo "NFC Player is already running!"
    echo "PID(s): $(pgrep -f 'nfc_player.py')"
    echo ""
    echo "To stop it: pkill -f nfc_player.py"
    exit 1
fi

# Start in background with logging
echo "Starting NFC Player..."
nohup python3 nfc_player.py > nfc_player.log 2>&1 &
PLAYER_PID=$!

echo "✓ NFC Player started in background"
echo "  PID: $PLAYER_PID"
echo "  Log file: nfc_player.log"
echo ""
echo "The player will continue running even if you close this terminal."
echo ""
echo "To monitor logs: tail -f nfc_player.log"
echo "To stop player: pkill -f nfc_player.py"
echo "To check status: ./check_status.sh"
