#!/usr/bin/env python3
"""
Alternative startup script for systems without bash
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Check if Python version is adequate"""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)

def install_dependencies():
    """Install required Python packages"""
    print("Installing/updating dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Warning: Some dependencies might not have installed correctly")
        print("This is normal on non-Raspberry Pi systems")

def start_web_server():
    """Start the NFC web server"""
    print("\nStarting NFC Web Server...")
    try:
        # Start the web server in a subprocess
        process = subprocess.Popen([sys.executable, "nfc_web_server.py"])
        return process
    except Exception as e:
        print(f"Error starting web server: {e}")
        return None

def open_web_interface():
    """Open the web interface in default browser"""
    print("Opening web interface...")
    time.sleep(2)  # Wait for server to start
    try:
        webbrowser.open("http://localhost:5000")
    except:
        print("Please open http://localhost:5000 in your browser")

def start_nfc_player():
    """Start the NFC player"""
    print("\nStarting NFC Player...")
    try:
        # Start the player in a subprocess
        process = subprocess.Popen([sys.executable, "nfc_player.py"])
        return process
    except Exception as e:
        print(f"Error starting NFC player: {e}")
        return None

def main():
    print("=========================================")
    print("NFC to HTML Mapping System")
    print("=========================================")
    
    # Check Python version
    check_python_version()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Install dependencies
    install_dependencies()
    
    # Start web server
    web_process = start_web_server()
    if not web_process:
        print("Failed to start web server")
        sys.exit(1)
    
    # Open web interface
    open_web_interface()
    
    print("\nThe web server is now running at http://localhost:5000")
    
    # Ask if user wants to start the player
    try:
        response = input("\nDo you want to start the NFC Player now? (y/n): ").strip().lower()
        if response == 'y':
            player_process = start_nfc_player()
        else:
            player_process = None
    except:
        player_process = None
    
    print("\nSystem is running. Press Ctrl+C to stop all components.")
    
    # Wait for interruption
    try:
        if web_process:
            web_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        if web_process:
            web_process.terminate()
        if player_process:
            player_process.terminate()
        print("All components stopped.")

if __name__ == "__main__":
    main()
