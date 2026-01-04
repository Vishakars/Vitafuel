#!/usr/bin/env python3
"""
Script to automatically open VitaFuel in the correct URL
"""

import webbrowser
import time
import subprocess
import sys

def check_server_status():
    """Check if the frontend server is running on port 3000"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:3000", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_frontend_server():
    """Start the frontend server if it's not running"""
    try:
        print("Starting frontend server on port 3000...")
        subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd="client", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Frontend server started!")
        return True
    except Exception as e:
        print(f"Error starting frontend server: {e}")
        return False

def main():
    print("VitaFuel Auto-Launcher")
    print("=" * 40)
    
    # Check if frontend server is running
    if not check_server_status():
        print("Frontend server not running. Starting it...")
        if not start_frontend_server():
            print("[ERROR] Failed to start frontend server")
            return
        
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)
    
    # Open the correct URL
    correct_url = "http://127.0.0.1:3000/dashboard.html"
    print(f"Opening VitaFuel at: {correct_url}")
    
    try:
        webbrowser.open(correct_url)
        print("[SUCCESS] VitaFuel opened successfully!")
        print("\nNote: Make sure your backend is running on port 8005")
        print("   If not, run: cd server && python -m uvicorn main:app --host 127.0.0.1 --port 8005 --reload")
    except Exception as e:
        print(f"[ERROR] Error opening browser: {e}")
        print(f"Please manually open: {correct_url}")

if __name__ == "__main__":
    main()
