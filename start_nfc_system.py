#!/usr/bin/env python3
"""
Fixed startup script that properly starts both components
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

def start_web_server():
    """Start the NFC web server in background"""
    print("\nStarting NFC Web Server in background...")
    try:
        # Start the web server in a subprocess (background)
        process = subprocess.Popen([sys.executable, "nfc_web_server.py"])
        time.sleep(3)  # Give it time to start
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ Web server started successfully")
            return process
        else:
            print("✗ Web server failed to start")
            return None
    except Exception as e:
        print(f"Error starting web server: {e}")
        return None

def start_nfc_player():
    """Start the NFC player in background"""
    print("\nStarting NFC Player in background...")
    try:
        # Start the player in a subprocess (background)
        process = subprocess.Popen([sys.executable, "nfc_player.py"])
        time.sleep(2)  # Give it time to start
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ NFC Player started successfully")
            return process
        else:
            print("✗ NFC Player failed to start")
            return None
    except Exception as e:
        print(f"Error starting NFC player: {e}")
        return None

def open_web_interface():
    """Open the web interface in default browser"""
    print("\nOpening web interface...")
    try:
        webbrowser.open("http://localhost:5000")
        print("✓ Web interface opened")
    except:
        print("Please open http://localhost:5000 in your browser")

def main():
    print("=========================================")
    print("NFC to HTML Mapping System")
    print("=========================================")
    
    # Check Python version
    check_python_version()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Start web server
    web_process = start_web_server()
    if not web_process:
        print("\nFailed to start web server. Exiting.")
        sys.exit(1)
    
    # Start NFC player
    player_process = start_nfc_player()
    if not player_process:
        print("\nFailed to start NFC player.")
        print("You can start it manually later with: python3 nfc_player.py")
    
    # Open web interface
    open_web_interface()
    
    print("\n" + "="*50)
    print("SYSTEM STATUS")
    print("="*50)
    print("✓ Web Server: Running at http://localhost:5000")
    if player_process and player_process.poll() is None:
        print("✓ NFC Player: Running (will open HTML files when chips are detected)")
    else:
        print("✗ NFC Player: Not running (start with: python3 nfc_player.py)")
    print("\nPress Ctrl+C to stop all components")
    print("="*50)
    
    # Monitor processes
    try:
        while True:
            # Check if processes are still running
            web_running = web_process and web_process.poll() is None
            player_running = player_process and player_process.poll() is None
            
            if not web_running:
                print("\n⚠️  Web server stopped unexpectedly!")
                break
                
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        
        # Terminate processes
        if web_process and web_process.poll() is None:
            web_process.terminate()
            print("✓ Web server stopped")
            
        if player_process and player_process.poll() is None:
            player_process.terminate()
            print("✓ NFC player stopped")
            
        print("\nAll components stopped.")

if __name__ == "__main__":
    main()
