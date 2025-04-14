"""
Test script for login and token refresh with background tasks.
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000/api"

def login(username, password):
    """Login to get an access token."""
    login_url = f"{BASE_URL}/auth/login"
    response = requests.post(
        login_url,
        json={"username": username, "password": password}
    )
    
    if response.status_code != 200:
        print(f"Login failed with status {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    return data["tokens"]["access_token"]

def refresh_token(refresh_token):
    """Refresh the access token."""
    refresh_url = f"{BASE_URL}/auth/refresh"
    headers = {"Authorization": f"Bearer {refresh_token}"}
    
    response = requests.post(refresh_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Token refresh failed with status {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    return data["access_token"]

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_login.py <username> <password>")
        return
        
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"Testing login with username: {username}")
    
    # Login to test background tasks
    access_token = login(username, password)
    if not access_token:
        print("Login failed. Exiting.")
        return
    
    print("Login successful!")
    print(f"Access token: {access_token[:10]}...")
    
    # Wait a few seconds for background tasks to run
    print("\nWaiting for background tasks to complete...")
    time.sleep(5)
    
    print("\nLogin test complete. Check the server logs for background task activity.")

if __name__ == "__main__":
    main()