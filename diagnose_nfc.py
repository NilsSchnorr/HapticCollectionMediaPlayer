#!/usr/bin/env python3
"""
Run diagnostics to identify NFC detection issues
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("NFC System Diagnostic Tool")
    print("This will help identify why NFC detection isn't working")
    
    # Get current directory
    current_dir = os.getcwd()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\nCurrent directory: {current_dir}")
    print(f"Script directory: {base_dir}")
    
    # Test 1: Original example
    print("\n" + "="*60)
    print("TEST 1: Running original example (should work)")
    os.chdir(os.path.join(base_dir, 'python'))
    success1 = run_command("timeout 10 python3 example_get_uid.py", "Original example_get_uid.py")
    os.chdir(base_dir)
    
    # Test 2: Our test script
    success2 = run_command("timeout 10 python3 test_nfc.py", "Our test_nfc.py (uses same imports)")
    
    # Test 3: Debug script
    success3 = run_command("timeout 10 python3 debug_nfc.py", "Debug script with detailed output")
    
    # Test 4: Simple server
    print("\n" + "="*60)
    print("TEST 4: Simple server (no threading)")
    print("Starting server for 5 seconds...")
    print("Please try placing an NFC card on the reader")
    print("="*60)
    
    # Start simple server in background
    proc = subprocess.Popen(["python3", "simple_nfc_server.py"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          text=True)
    
    # Let it run for 5 seconds
    import time
    time.sleep(5)
    
    # Check if still running
    if proc.poll() is None:
        print("Server is running successfully")
        proc.terminate()
        proc.wait()
    else:
        stdout, stderr = proc.communicate()
        print("Server stopped unexpectedly:")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"Original example works: {'YES' if success1 else 'NO'}")
    print(f"Test script works: {'YES' if success2 else 'NO'}")
    print(f"Debug script works: {'YES' if success3 else 'NO'}")
    
    if success1 and not success2:
        print("\nDIAGNOSIS: Path or import issue")
        print("The original works but our scripts don't.")
        print("Try running from the python directory:")
        print("  cd python && python3 ../test_nfc.py")
    elif not success1:
        print("\nDIAGNOSIS: Hardware or system issue")
        print("Even the original example isn't working.")
        print("Check your hardware connections and permissions.")
    
    print("\nNext steps:")
    print("1. Check the output above for error messages")
    print("2. Try running the simple_nfc_server.py manually")
    print("3. Share the output of this diagnostic with support")

if __name__ == "__main__":
    main()
