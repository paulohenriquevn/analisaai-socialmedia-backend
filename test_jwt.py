#!/usr/bin/env python3
"""
Test script to verify JWT authentication is working properly.
"""
import sys
import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
REFRESH_URL = f"{BASE_URL}/api/auth/refresh"
PROFILE_URL = f"{BASE_URL}/api/auth/profile"

def print_colored(text, color):
    """Print colored text to the terminal."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def check_jwt_environment():
    """Check the JWT environment configuration."""
    print_colored("\n[TEST] Checking JWT environment configuration...", "blue")
    
    # Check environment variables
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    secret_key = os.getenv("SECRET_KEY")
    
    if jwt_secret:
        print_colored(f"✓ JWT_SECRET_KEY is set: {jwt_secret[:5]}...{jwt_secret[-5:] if len(jwt_secret) > 10 else jwt_secret}", "green")
    else:
        print_colored("✗ JWT_SECRET_KEY is not set in environment", "red")
    
    if secret_key:
        print_colored(f"✓ SECRET_KEY is set: {secret_key[:5]}...{secret_key[-5:] if len(secret_key) > 10 else secret_key}", "green")
    else:
        print_colored("✗ SECRET_KEY is not set in environment", "red")
    
    # Check Flask environment
    flask_env = os.getenv("FLASK_ENV", "development")
    print_colored(f"✓ FLASK_ENV is set to: {flask_env}", "green")
    
    # Check if the application is running
    try:
        response = requests.get(f"{BASE_URL}/api/auth/auth-status")
        if response.status_code == 200:
            print_colored("✓ Server is running and auth status endpoint is accessible", "green")
            data = response.json()
            print(f"  API Version: {data.get('api_version', 'Unknown')}")
            print(f"  Database status: {data.get('db_status', 'Unknown')}")
            print(f"  Frontend URL: {data.get('frontend_url', 'Unknown')}")
        else:
            print_colored(f"✗ Server is running but auth status returned {response.status_code}", "red")
    except Exception as e:
        print_colored(f"✗ Could not connect to server: {str(e)}", "red")
    
    # Print test run information
    print_colored("\n[INFO] Test execution information:", "blue")
    print(f"  Current directory: {os.getcwd()}")
    print(f"  Python version: {sys.version}")

def login_test(username, password):
    """Test the login endpoint."""
    print_colored("\n[TEST] Logging in...", "blue")
    login_data = {"username": username, "password": password}
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        response_data = response.json()
        
        if response.status_code == 200:
            print_colored("✓ Login successful", "green")
            print(f"  User ID: {response_data['user']['id']}")
            print(f"  Username: {response_data['user']['username']}")
            print(f"  Roles: {', '.join(response_data['user']['roles'])}")
            return response_data.get("tokens", {})
        else:
            print_colored(f"✗ Login failed: {response.status_code}", "red")
            print(f"  Error: {response_data.get('error')}")
            print(f"  Message: {response_data.get('message', 'No message')}")
            return None
    except Exception as e:
        print_colored(f"✗ Error connecting to login endpoint: {str(e)}", "red")
        return None

def profile_test(access_token):
    """Test the profile endpoint with the access token."""
    print_colored("\n[TEST] Getting user profile...", "blue")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(PROFILE_URL, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            print_colored("✓ Profile retrieval successful", "green")
            print(f"  User ID: {response_data['user']['id']}")
            print(f"  Username: {response_data['user']['username']}")
            print(f"  Email: {response_data['user']['email']}")
            return True
        else:
            print_colored(f"✗ Profile retrieval failed: {response.status_code}", "red")
            print(f"  Error: {response_data.get('error')}")
            print(f"  Message: {response_data.get('message', 'No message')}")
            
            # Verify JWT_SECRET_KEY in .env and app
            jwt_key = os.getenv("JWT_SECRET_KEY")
            if jwt_key:
                print_colored(f"  JWT Secret Key (.env): {jwt_key[:5]}...{jwt_key[-5:] if len(jwt_key) > 10 else jwt_key}", "yellow")
            else:
                print_colored("  JWT Secret Key (.env): Not found", "yellow")
            
            return False
    except Exception as e:
        print_colored(f"✗ Error connecting to profile endpoint: {str(e)}", "red")
        return False

def refresh_test(refresh_token):
    """Test the refresh token endpoint."""
    print_colored("\n[TEST] Refreshing access token...", "blue")
    headers = {"Authorization": f"Bearer {refresh_token}"}
    
    try:
        response = requests.post(REFRESH_URL, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            print_colored("✓ Token refresh successful", "green")
            print(f"  New access token: {response_data['access_token'][:15]}...")
            return response_data.get("access_token")
        else:
            print_colored(f"✗ Token refresh failed: {response.status_code}", "red")
            print(f"  Error: {response_data.get('error')}")
            print(f"  Message: {response_data.get('message', 'No message')}")
            return None
    except Exception as e:
        print_colored(f"✗ Error connecting to refresh endpoint: {str(e)}", "red")
        return None

def delayed_profile_test(access_token, delay=5):
    """Test the profile endpoint after a delay to check token expiration."""
    print_colored(f"\n[TEST] Waiting {delay} seconds to test token...", "blue")
    time.sleep(delay)
    return profile_test(access_token)

def run_tests():
    """Run all JWT authentication tests."""
    print_colored("=== JWT AUTHENTICATION TEST ===", "blue")
    
    # Check environment configuration
    check_jwt_environment()
    
    # Get username and password from command line arguments or use defaults
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    
    # Test login
    tokens = login_test(username, password)
    if not tokens:
        print_colored("\n✗ Login failed. Cannot continue with other tests.", "red")
        return
    
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    
    # Test profile endpoint with access token
    profile_result = profile_test(access_token)
    
    # Test refresh endpoint with refresh token
    new_access_token = refresh_test(refresh_token)
    
    # Test profile endpoint with new access token
    if new_access_token:
        profile_test(new_access_token)
    
    # Final test summary
    print_colored("\n=== TEST SUMMARY ===", "blue")
    if profile_result and new_access_token:
        print_colored("✓ All tests passed successfully", "green")
    else:
        print_colored("✗ Some tests failed", "red")
        
        print_colored("\n[TROUBLESHOOTING]", "yellow")
        print("1. Verify that the secret keys in .env match those used by the application")
        print("2. Check if the JWT token format is valid")
        print("3. Ensure the same JWT_SECRET_KEY is used for signing and verifying tokens")
        print("4. Check if the access token has expired")
        print("5. Make sure CORS settings allow the Authorization header")

if __name__ == "__main__":
    run_tests()