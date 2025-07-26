#!/bin/bash

echo "========================================="
echo "Checking NFC System Status"
echo "========================================="

# Check if web server is running
if pgrep -f "nfc_web_server.py" > /dev/null; then
    echo "✓ Web Server: RUNNING"
    echo "  PID(s): $(pgrep -f 'nfc_web_server.py')"
else
    echo "✗ Web Server: NOT RUNNING"
fi

# Check if NFC player is running
if pgrep -f "nfc_player.py" > /dev/null; then
    echo "✓ NFC Player: RUNNING"
    echo "  PID(s): $(pgrep -f 'nfc_player.py')"
else
    echo "✗ NFC Player: NOT RUNNING"
fi

# Check if port 5000 is in use
echo ""
echo "Port 5000 status:"
if lsof -i:5000 > /dev/null 2>&1; then
    echo "✓ Port 5000 is in use (web server listening)"
else
    echo "✗ Port 5000 is not in use"
fi

# Check for NFC mappings file
echo ""
if [ -f "nfc_mappings.json" ]; then
    echo "✓ Mappings file exists"
    MAPPINGS=$(cat nfc_mappings.json | grep -c '"html_file"')
    echo "  Number of mappings: $MAPPINGS"
else
    echo "✗ No mappings file found"
fi

echo ""
echo "========================================="
echo "To start missing components:"
echo "  Web Server only: python3 nfc_web_server.py"
echo "  NFC Player only: python3 nfc_player.py"
echo "  Both at once:    ./start_both.sh"
echo "========================================="
