#!/usr/bin/env python3
"""
Test script to verify the backend works locally.
Run this to test: python test_local.py
"""

import requests
import json
import time
import subprocess
import sys
import os

def test_local_server():
    """Test the local server by running it and making a request"""
    print("Starting local server test...")
    
    # Start the server in a subprocess
    process = subprocess.Popen([
        sys.executable, "src/api/main.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a moment for the server to start
    time.sleep(3)
    
    try:
        # Test the health check endpoint
        response = requests.get("http://127.0.0.1:8000/")
        print(f"Health check response: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        # Test the chat endpoint
        chat_data = {
            "session_id": "test_session",
            "message": "Hello, how are you?"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json=chat_data
        )
        print(f"Chat response status: {response.status_code}")
        if response.status_code == 200:
            print(f"Chat response: {response.json()}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        # Clean up
        process.terminate()
        process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    test_local_server() 