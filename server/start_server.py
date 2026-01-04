#!/usr/bin/env python3
"""
Startup script for VitaFuel server.
This script will start the FastAPI server with proper configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=1000)
        client.server_info()
        print("✅ MongoDB is running")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("Please make sure MongoDB is installed and running.")
        print("You can start MongoDB with: mongod")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting VitaFuel server...")
    try:
        # Change to the server directory
        os.chdir(Path(__file__).parent)
        
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8005", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    print("🏥 VitaFuel Server Startup")
    print("=" * 40)
    
    # Check MongoDB
    if not check_mongodb():
        print("\nPlease start MongoDB and try again.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\nFailed to install dependencies.")
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
