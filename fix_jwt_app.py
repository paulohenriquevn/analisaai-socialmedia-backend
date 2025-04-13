#!/usr/bin/env python3
"""
Script to reset JWT configuration and clear cached data.
"""
import os
import sys
from dotenv import load_dotenv
import requests
import json
import time
import uuid

# Load environment variables from .env file
load_dotenv()

BASE_URL = "http://localhost:5000"

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

def reset_jwt_configuration():
    """Reset JWT configuration by updating .env file."""
    print_colored("\n[FIX] Checking JWT configuration in .env file...", "blue")
    
    # Read current .env file
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        print_colored("✓ Successfully read .env file", "green")
    except Exception as e:
        print_colored(f"✗ Error reading .env file: {str(e)}", "red")
        return False
    
    # Check if JWT keys are present
    current_jwt_key = os.getenv('JWT_SECRET_KEY', '')
    current_secret_key = os.getenv('SECRET_KEY', '')
    
    # Generate new keys if needed
    new_jwt_key = f"analisaai-jwt-key-{uuid.uuid4()}"
    new_secret_key = f"analisaai-secret-key-{uuid.uuid4()}"
    
    # Update the keys in the .env content
    lines = env_content.split('\n')
    updated_lines = []
    jwt_key_updated = False
    secret_key_updated = False
    
    for line in lines:
        if line.startswith('JWT_SECRET_KEY='):
            updated_lines.append(f"JWT_SECRET_KEY={new_jwt_key}")
            jwt_key_updated = True
        elif line.startswith('SECRET_KEY='):
            updated_lines.append(f"SECRET_KEY={new_secret_key}")
            secret_key_updated = True
        else:
            updated_lines.append(line)
    
    # Add keys if they don't exist
    if not jwt_key_updated:
        updated_lines.append(f"JWT_SECRET_KEY={new_jwt_key}")
    
    if not secret_key_updated:
        updated_lines.append(f"SECRET_KEY={new_secret_key}")
    
    # Write updated content back to .env file
    try:
        with open('.env', 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print_colored("✓ Successfully updated JWT keys in .env file", "green")
        print(f"  Old JWT key: {current_jwt_key[:5]}...{current_jwt_key[-5:] if len(current_jwt_key) > 10 else current_jwt_key}")
        print(f"  New JWT key: {new_jwt_key[:5]}...{new_jwt_key[-5:] if len(new_jwt_key) > 10 else new_jwt_key}")
        
        print(f"  Old SECRET key: {current_secret_key[:5]}...{current_secret_key[-5:] if len(current_secret_key) > 10 else current_secret_key}")
        print(f"  New SECRET key: {new_secret_key[:5]}...{new_secret_key[-5:] if len(new_secret_key) > 10 else new_secret_key}")
        return True
    except Exception as e:
        print_colored(f"✗ Error updating .env file: {str(e)}", "red")
        return False

def check_app_running():
    """Check if the Flask app is running."""
    print_colored("\n[CHECK] Verifying if the application is running...", "blue")
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/auth-status")
        if response.status_code == 200:
            print_colored("✓ Application is running", "green")
            data = response.json()
            print(f"  API Version: {data.get('api_version', 'Unknown')}")
            print(f"  Database status: {data.get('db_status', 'Unknown')}")
            return True
        else:
            print_colored(f"✗ Application returned status code: {response.status_code}", "red")
            return False
    except Exception as e:
        print_colored(f"✗ Application is not running or cannot be reached: {str(e)}", "red")
        return False

def create_restart_script():
    """Create a script to restart the Flask application."""
    print_colored("\n[FIX] Creating restart script...", "blue")
    
    script_content = """#!/bin/bash
# Restart the Flask application
echo "Stopping current Flask application..."
pkill -f "python run.py" || echo "No running Flask application found"

# Wait a moment
sleep 2

# Start Flask app in background
echo "Starting Flask application..."
cd "$(dirname "$0")"
python run.py > logs/flask.log 2>&1 &

# Wait for startup
sleep 2
echo "Flask application restarted."
"""
    
    try:
        with open('restart_app.sh', 'w') as f:
            f.write(script_content)
        
        # Make the script executable
        os.chmod('restart_app.sh', 0o755)
        print_colored("✓ Created restart script: restart_app.sh", "green")
        return True
    except Exception as e:
        print_colored(f"✗ Error creating restart script: {str(e)}", "red")
        return False

def fix_cache_config():
    """Create a patch for the cache configuration to ensure it doesn't affect JWT."""
    print_colored("\n[FIX] Creating cache configuration patch...", "blue")
    
    # Check if the extensions.py file exists
    try:
        with open('app/extensions.py', 'r') as f:
            extensions_content = f.read()
        
        print_colored("✓ Found extensions.py file", "green")
        
        # Look for the cache configuration
        if 'cache = Cache()' in extensions_content and 'cache_config =' in extensions_content:
            print_colored("✓ Found cache configuration", "green")
            
            # Updated content with cache configuration after JWT initialization
            new_content = extensions_content.replace(
                '    # Configure cache\n    cache_config = {\n        \'CACHE_TYPE\': \'SimpleCache\',  # Use simple in-memory cache\n        \'CACHE_DEFAULT_TIMEOUT\': 300  # Default timeout is 5 minutes\n    }\n    app.config.from_mapping(cache_config)\n    cache.init_app(app)\n    \n    # Register JWT error handlers',
                
                '    # Register JWT error handlers\n    from app.utils.error_handlers import register_jwt_handlers\n    register_jwt_handlers(jwt)\n    \n    # Configure cache\n    cache_config = {\n        \'CACHE_TYPE\': \'SimpleCache\',  # Use simple in-memory cache\n        \'CACHE_DEFAULT_TIMEOUT\': 300,  # Default timeout is 5 minutes\n        \'CACHE_KEY_PREFIX\': \'analisaai_\',  # Add a prefix to avoid collisions\n    }\n    app.config.from_mapping(cache_config)\n    cache.init_app(app)'
            )
            
            # Check if the content was changed
            if new_content != extensions_content:
                # Save the updated file
                with open('app/extensions.py', 'w') as f:
                    f.write(new_content)
                print_colored("✓ Updated cache configuration in extensions.py", "green")
                print("  - Moved cache initialization after JWT initialization")
                print("  - Added CACHE_KEY_PREFIX to avoid potential collisions")
                return True
            else:
                print_colored("! No changes needed in cache configuration", "yellow")
                return True
        else:
            print_colored("! Cache configuration not found or already updated", "yellow")
            return True
            
    except Exception as e:
        print_colored(f"✗ Error updating cache configuration: {str(e)}", "red")
        return False

def main():
    """Main function to fix JWT authentication issues."""
    print_colored("=== JWT AUTHENTICATION FIX SCRIPT ===", "blue")
    
    # Check if the app is running
    app_running = check_app_running()
    
    # Fix the JWT configuration
    jwt_fixed = reset_jwt_configuration()
    
    # Fix cache configuration to ensure it doesn't interfere with JWT
    cache_fixed = fix_cache_config()
    
    # Create restart script
    restart_script_created = create_restart_script()
    
    # Print summary
    print_colored("\n=== FIX SUMMARY ===", "blue")
    if jwt_fixed and cache_fixed and restart_script_created:
        print_colored("✓ All fixes applied successfully", "green")
        
        if app_running:
            print_colored("\n[ACTION REQUIRED]", "yellow")
            print("To apply the changes, you need to restart the Flask application.")
            print("Run the following command:")
            print("  ./restart_app.sh")
            print("\nAfter restart, you need to log in again to get new tokens.")
        else:
            print_colored("\n[ACTION REQUIRED]", "yellow")
            print("Start the Flask application with:")
            print("  python run.py")
            print("\nAfter starting, you need to log in again to get new tokens.")
    else:
        print_colored("✗ Some fixes could not be applied", "red")
        print("Please check the output above for details.")
    
    print_colored("\n[NEXT STEPS]", "yellow")
    print("1. Restart the application")
    print("2. Log in again to get new tokens with the updated JWT configuration")
    print("3. Run 'python test_jwt.py' to verify the JWT authentication is working")

if __name__ == "__main__":
    main()