#!/bin/bash

# Startup script for NFC to HTML Mapping System

echo "========================================="
echo "NFC to HTML Mapping System"
echo "========================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python 3 is installed
if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if we're on a Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    MODEL=$(tr -d '\0' < /proc/device-tree/model)
    if [[ $MODEL == *"Raspberry Pi"* ]]; then
        echo "Running on: $MODEL"
    fi
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Function to run a component in a new terminal
run_component() {
    local component=$1
    local title=$2
    
    if command_exists gnome-terminal; then
        gnome-terminal --title="$title" -- bash -c "source venv/bin/activate; python3 $component; exec bash"
    elif command_exists xterm; then
        xterm -title "$title" -e "source venv/bin/activate; python3 $component; bash" &
    elif command_exists lxterminal; then
        lxterminal --title="$title" -e "source venv/bin/activate; python3 $component; bash" &
    else
        echo "Starting $title in background..."
        source venv/bin/activate && python3 $component &
    fi
}

# Start the web server
echo "Starting NFC Web Server..."
run_component "nfc_web_server.py" "NFC Web Server"

# Wait a moment for the server to start
sleep 3

# Open the web interface
echo "Opening web interface..."
if command_exists chromium-browser; then
    chromium-browser http://localhost:5000 &
elif command_exists firefox; then
    firefox http://localhost:5000 &
elif command_exists xdg-open; then
    xdg-open http://localhost:5000 &
fi

# Ask user if they want to start the player
echo ""
echo "The web server is now running at http://localhost:5000"
echo ""
read -p "Do you want to start the NFC Player now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting NFC Player..."
    run_component "nfc_player.py" "NFC Player"
fi

echo ""
echo "System is running. Press Ctrl+C to stop all components."
echo ""

# Wait for user to stop
wait
