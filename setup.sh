#!/bin/bash

echo "========================================="
echo "Setting up NFC to HTML Mapping System"
echo "========================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the system, run:"
echo "  source venv/bin/activate"
echo "  python3 start_nfc_system.py"
echo ""
echo "Or use the automated startup:"
echo "  ./run_nfc_system.sh"
