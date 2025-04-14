#!/usr/bin/env python3
"""
JWT Token Troubleshooting Script for AnalisaAI Social Media.

This utility helps identify and fix common JWT authentication issues in the AnalisaAI system.
It uses a step-by-step diagnostic approach based on common JWT authentication problems.
"""

import os
import sys
import re
import json
import time
import base64
import argparse
import subprocess
import requests
from datetime import datetime, timedelta
from uuid import uuid4
from pathlib import Path

# Constants
DEFAULT_BASE_URL = "http://localhost:5000"
TOKEN_EXPIRY_THRESHOLD = 300  # 5 minutes in seconds


def print_colored(text, color):
    """Print colored text to the terminal."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def decode_jwt_segments(token):
    """
    Decode and parse the JWT token without verifying the signature.
    Returns the token's header, payload, and signature segments.
    """
    if not token or not isinstance(token, str):
        return None, None, None

    # Remove Bearer prefix if present
    if token.startswith('Bearer '):
        token = token[7:].strip()

    # Split token into segments
    segments = token.split('.')
    if len(segments) != 3:
        print_colored(f"ERROR: Token does not have the standard JWT format (header.payload.signature)", "red")
        return None, None, None

    header_segment, payload_segment, signature_segment = segments

    # Decode header and payload
    try:
        # Add padding for base64 if needed
        def add_padding(s):
            # Add padding if needed
            padding = len(s) % 4
            if padding:
                s += '=' * (4 - padding)
            return s

        # Decode header
        header_bytes = base64.urlsafe_b64decode(add_padding(header_segment))
        header = json.loads(header_bytes.decode('utf-8'))

        # Decode payload
        payload_bytes = base64.urlsafe_b64decode(add_padding(payload_segment))
        payload = json.loads(payload_bytes.decode('utf-8'))

        return header, payload, signature_segment
    except Exception as e:
        print_colored(f"ERROR: Failed to decode token: {str(e)}", "red")
        return None, None, None


def analyze_token(token):
    """Analyze the JWT token and print information about it."""
    if not token:
        print_colored("ERROR: No token provided.", "red")
        return None

    # First, clean the token from any "Bearer " prefix
    if token.startswith('Bearer '):
        token = token[7:]

    # Remove any whitespace
    token = token.strip()

    # Check for correct format
    if not re.match(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$', token):
        print_colored("ERROR: Token does not have the standard JWT format.", "red")
        return None

    # Decode the token segments
    header, payload, signature = decode_jwt_segments(token)
    if not header or not payload:
        print_colored("ERROR: Failed to decode token.", "red")
        return None

    # Print token information
    print_colored("\n==== JWT TOKEN ANALYSIS ====", "blue")
    
    print_colored("\n=== HEADER ===", "cyan")
    print(json.dumps(header, indent=2))

    print_colored("\n=== PAYLOAD ===", "cyan")
    print(json.dumps(payload, indent=2))

    print_colored("\n=== VALIDATION ===", "cyan")
    
    # Check token type
    token_type = header.get('typ')
    if token_type == 'JWT':
        print_colored("✅ Token type (typ): JWT", "green")
    else:
        print_colored(f"⚠️ Token type (typ): {token_type} (expected: JWT)", "yellow")

    # Check algorithm
    alg = header.get('alg')
    if alg == 'HS256':
        print_colored("✅ Algorithm (alg): HS256", "green")
    else:
        print_colored(f"⚠️ Algorithm (alg): {alg} (expected: HS256)", "yellow")

    # Check subject (identity)
    sub = payload.get('sub')
    if sub:
        print_colored(f"✅ Subject (sub/identity): {sub}", "green")
    else:
        print_colored("⚠️ Missing subject (sub) claim", "yellow")

    # Check issued at time
    iat = payload.get('iat')
    if iat:
        iat_date = datetime.fromtimestamp(iat)
        print_colored(f"✅ Issued at (iat): {iat_date.strftime('%Y-%m-%d %H:%M:%S')}", "green")
    else:
        print_colored("⚠️ Missing issued at (iat) claim", "yellow")

    # Check expiration time
    exp = payload.get('exp')
    if exp:
        exp_date = datetime.fromtimestamp(exp)
        now = datetime.now()
        is_expired = now > exp_date
        
        if is_expired:
            print_colored(f"❌ Expired on (exp): {exp_date.strftime('%Y-%m-%d %H:%M:%S')} (EXPIRED)", "red")
        else:
            time_left = exp_date - now
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if time_left.total_seconds() < TOKEN_EXPIRY_THRESHOLD:
                print_colored(f"⚠️ Expires on (exp): {exp_date.strftime('%Y-%m-%d %H:%M:%S')} (Expiring soon! Only {minutes}m {seconds}s left)", "yellow")
            else:
                print_colored(f"✅ Expires on (exp): {exp_date.strftime('%Y-%m-%d %H:%M:%S')} (Valid for {hours}h {minutes}m {seconds}s)", "green")
    else:
        print_colored("⚠️ Missing expiration (exp) claim", "yellow")

    # Check token type
    token_type = payload.get('type')
    if token_type:
        if token_type == 'access':
            print_colored("✅ Token type: Access token", "green")
        elif token_type == 'refresh':
            print_colored("✅ Token type: Refresh token", "green")
        else:
            print_colored(f"ℹ️ Token type: {token_type}", "blue")
    else:
        print_colored("ℹ️ No specific token type claim", "blue")

    # Check fresh status
    fresh = payload.get('fresh', None)
    if fresh is not None:
        print_colored(f"ℹ️ Fresh token: {fresh}", "blue")

    # Check other relevant claims
    jti = payload.get('jti')
    if jti:
        print_colored(f"ℹ️ JWT ID (jti): {jti}", "blue")

    # Check if token has fingerprint
    fp = payload.get('fp')
    if fp:
        print_colored(f"ℹ️ Fingerprint (fp): {fp}", "blue")

    print_colored("\n=== SUMMARY ===", "blue")
    
    # Check for issues
    issues = []
    
    if exp and datetime.now() > exp_date:
        issues.append("Token is expired")
    
    if exp and datetime.now() + timedelta(seconds=TOKEN_EXPIRY_THRESHOLD) > exp_date:
        issues.append("Token is about to expire")
    
    # Return token info with issues
    return {
        "header": header,
        "payload": payload,
        "is_valid": len(issues) == 0,
        "is_expired": exp and datetime.now() > exp_date,
        "expires_soon": exp and datetime.now() + timedelta(seconds=TOKEN_EXPIRY_THRESHOLD) > exp_date,
        "issues": issues,
        "token": token
    }


def check_environment_variables():
    """Check for environment variables related to JWT."""
    print_colored("\n==== Checking Environment Variables ====", "blue")
    
    env_issues = []
    
    # Check for JWT_SECRET_KEY
    jwt_secret = os.environ.get('JWT_SECRET_KEY')
    if jwt_secret:
        masked_key = jwt_secret[:4] + '*' * (len(jwt_secret) - 8) + jwt_secret[-4:]
        print_colored(f"✅ JWT_SECRET_KEY is set: {masked_key}", "green")
    else:
        print_colored("❌ JWT_SECRET_KEY is not set", "red")
        env_issues.append("JWT_SECRET_KEY is missing")
    
    # Check for SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY')
    if secret_key:
        masked_key = secret_key[:4] + '*' * (len(secret_key) - 8) + secret_key[-4:]
        print_colored(f"✅ SECRET_KEY is set: {masked_key}", "green")
    else:
        print_colored("⚠️ SECRET_KEY is not set (this may be intentional)", "yellow")
    
    # Check for FLASK_APP and FLASK_ENV
    flask_app = os.environ.get('FLASK_APP')
    if flask_app:
        print_colored(f"✅ FLASK_APP is set to: {flask_app}", "green")
    else:
        print_colored("ℹ️ FLASK_APP is not set (using default)", "blue")
    
    flask_env = os.environ.get('FLASK_ENV', 'production')
    if flask_env == 'development':
        print_colored(f"ℹ️ FLASK_ENV is set to: {flask_env} (development mode)", "blue")
    else:
        print_colored(f"ℹ️ FLASK_ENV is set to: {flask_env}", "blue")
    
    return env_issues


def check_server_status(base_url):
    """Check if the server is running and get its status."""
    print_colored("\n==== Checking Server Status ====", "blue")
    
    try:
        response = requests.get(f"{base_url}/api/auth/auth-status", timeout=5)
        if response.status_code == 200:
            print_colored("✅ Server is running and authentication endpoint is accessible", "green")
            
            # Parse response
            try:
                data = response.json()
                print_colored("\nServer Information:", "cyan")
                print(f"API Version: {data.get('api_version', 'Unknown')}")
                print(f"Database Status: {data.get('db_status', 'Unknown')}")
                print(f"JWT Status: {data.get('jwt_status', 'Unknown')}")
                
                # Check JWT configuration if available
                jwt_status = data.get('jwt_status')
                if jwt_status == 'configured':
                    print_colored("✅ JWT is properly configured on the server", "green")
                    return []
                elif jwt_status == 'not_configured':
                    print_colored("❌ JWT is not properly configured on the server", "red")
                    return ["JWT is not properly configured on the server"]
                else:
                    print_colored("⚠️ JWT status is unknown", "yellow")
                    return ["JWT status is unknown"]
                
            except json.JSONDecodeError:
                print_colored("⚠️ Could not parse server response", "yellow")
                return ["Could not parse server response"]
        else:
            print_colored(f"❌ Server returned unexpected status code: {response.status_code}", "red")
            return [f"Server returned unexpected status code: {response.status_code}"]
    except requests.RequestException as e:
        print_colored(f"❌ Could not connect to server: {str(e)}", "red")
        return [f"Could not connect to server: {str(e)}"]


def try_login(base_url, username, password):
    """Try to login with given credentials and get tokens."""
    print_colored("\n==== Testing Login Functionality ====", "blue")
    
    print(f"Attempting to login with username: {username}")
    
    try:
        login_url = f"{base_url}/api/auth/login"
        response = requests.post(
            login_url,
            json={"username": username, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            print_colored("✅ Login successful", "green")
            
            # Parse response
            try:
                data = response.json()
                if 'tokens' in data and 'access_token' in data['tokens']:
                    print_colored("✅ Access token received", "green")
                    
                    if 'refresh_token' in data['tokens']:
                        print_colored("✅ Refresh token received", "green")
                    else:
                        print_colored("❌ Refresh token not found in response", "red")
                    
                    return {
                        "access_token": data['tokens']['access_token'],
                        "refresh_token": data['tokens'].get('refresh_token'),
                        "user": data.get('user', {})
                    }
                else:
                    print_colored("❌ No access token in response", "red")
                    return None
            except json.JSONDecodeError:
                print_colored("❌ Could not parse login response", "red")
                return None
        else:
            print_colored(f"❌ Login failed with status code: {response.status_code}", "red")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('error', 'Unknown')}")
                print(f"Details: {error_data.get('message', 'No details provided')}")
            except:
                print(f"Response text: {response.text[:100]}...")
            return None
    except requests.RequestException as e:
        print_colored(f"❌ Error connecting to login endpoint: {str(e)}", "red")
        return None


def test_profile_endpoint(base_url, access_token):
    """Test the profile endpoint with the access token."""
    print_colored("\n==== Testing Profile Endpoint ====", "blue")
    
    try:
        profile_url = f"{base_url}/api/auth/profile"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(profile_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print_colored("✅ Profile endpoint accessible with token", "green")
            
            # Parse response
            try:
                data = response.json()
                print_colored("\nProfile Information:", "cyan")
                user_data = data.get('user', {})
                print(f"User ID: {user_data.get('id', 'Unknown')}")
                print(f"Username: {user_data.get('username', 'Unknown')}")
                print(f"Email: {user_data.get('email', 'Unknown')}")
                return True
            except json.JSONDecodeError:
                print_colored("⚠️ Could not parse profile response", "yellow")
                return False
        else:
            print_colored(f"❌ Profile request failed with status code: {response.status_code}", "red")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('error', 'Unknown')}")
                print(f"Details: {error_data.get('message', 'No details provided')}")
            except:
                print(f"Response text: {response.text[:100]}...")
            return False
    except requests.RequestException as e:
        print_colored(f"❌ Error connecting to profile endpoint: {str(e)}", "red")
        return False


def test_refresh_token(base_url, refresh_token):
    """Test the refresh token endpoint."""
    print_colored("\n==== Testing Refresh Token Endpoint ====", "blue")
    
    try:
        refresh_url = f"{base_url}/api/auth/refresh"
        headers = {"Authorization": f"Bearer {refresh_token}"}
        
        response = requests.post(refresh_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print_colored("✅ Refresh token endpoint working", "green")
            
            # Parse response
            try:
                data = response.json()
                if 'access_token' in data:
                    print_colored("✅ New access token received", "green")
                    return data['access_token']
                else:
                    print_colored("❌ No new access token in response", "red")
                    return None
            except json.JSONDecodeError:
                print_colored("⚠️ Could not parse refresh response", "yellow")
                return None
        else:
            print_colored(f"❌ Refresh request failed with status code: {response.status_code}", "red")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('error', 'Unknown')}")
                print(f"Details: {error_data.get('message', 'No details provided')}")
            except:
                print(f"Response text: {response.text[:100]}...")
            return None
    except requests.RequestException as e:
        print_colored(f"❌ Error connecting to refresh endpoint: {str(e)}", "red")
        return None


def suggest_fixes(issues):
    """Suggest fixes based on identified issues."""
    print_colored("\n==== Suggested Fixes ====", "blue")
    
    if not issues:
        print_colored("✅ No issues to fix!", "green")
        return
    
    for issue in issues:
        if "JWT_SECRET_KEY is missing" in issue:
            print_colored("❌ Issue: JWT_SECRET_KEY is missing", "red")
            print_colored("   Fix: Set the JWT_SECRET_KEY environment variable or in .env file", "yellow")
            print("       You can generate a secure key with the following command:")
            print("       python -c 'import secrets; print(secrets.token_hex(32))'")
        
        elif "JWT is not properly configured" in issue:
            print_colored("❌ Issue: JWT is not properly configured on the server", "red")
            print_colored("   Fix: Check the server configuration in app/extensions.py", "yellow")
            print("       Ensure that JWT initialization is correct:")
            print("       - Correct import of flask_jwt_extended")
            print("       - Proper initialization of JWTManager")
            print("       - JWT_SECRET_KEY is set in the app configuration")
        
        elif "Token is expired" in issue:
            print_colored("❌ Issue: Your token is expired", "red")
            print_colored("   Fix: Use the refresh token to get a new access token", "yellow")
            print("       - Use the /api/auth/refresh endpoint")
            print("       - Or login again to get new tokens")
        
        elif "Token is about to expire" in issue:
            print_colored("⚠️ Issue: Your token is about to expire", "yellow")
            print_colored("   Fix: Get a new token before it expires", "yellow")
            print("       - Use the /api/auth/refresh endpoint")
            print("       - Or login again to get new tokens")
        
        elif "Could not connect to server" in issue:
            print_colored("❌ Issue: Could not connect to the server", "red")
            print_colored("   Fix: Check if the server is running", "yellow")
            print("       - Run python run.py in the project directory")
            print("       - Check if the server URL is correct")
            print("       - Make sure there are no firewall issues")
        
        else:
            print_colored(f"⚠️ Issue: {issue}", "yellow")
            print_colored("   Fix: Consult the documentation for more details", "yellow")


def fix_jwt_configuration():
    """Try to fix JWT configuration by updating .env file."""
    print_colored("\n==== Attempting to Fix JWT Configuration ====", "blue")
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        print_colored("✅ Found .env file", "green")
        
        # Read current contents
        env_content = env_file.read_text()
        
        # Check if JWT_SECRET_KEY is present
        new_content = env_content
        jwt_key_present = re.search(r'^JWT_SECRET_KEY\s*=', env_content, re.MULTILINE) is not None
        
        # Generate a new key
        new_jwt_key = f"analisaai-jwt-{uuid4().hex}"
        
        if jwt_key_present:
            print_colored("✅ JWT_SECRET_KEY found in .env file", "green")
            # Update existing key
            new_content = re.sub(
                r'^JWT_SECRET_KEY\s*=.*$',
                f'JWT_SECRET_KEY={new_jwt_key}',
                new_content,
                flags=re.MULTILINE
            )
            print_colored("✅ Updated JWT_SECRET_KEY with new value", "green")
        else:
            print_colored("⚠️ JWT_SECRET_KEY not found in .env file", "yellow")
            # Add new key
            new_content += f"\nJWT_SECRET_KEY={new_jwt_key}\n"
            print_colored("✅ Added JWT_SECRET_KEY with new value", "green")
        
        # Write updated content
        env_file.write_text(new_content)
        
        print_colored(f"✅ JWT configuration updated in .env file", "green")
        print(f"New JWT_SECRET_KEY: {new_jwt_key[:4]}...{new_jwt_key[-4:]}")
        
        # Update environment variable in current process
        os.environ['JWT_SECRET_KEY'] = new_jwt_key
        
        return True
    else:
        print_colored("❌ .env file not found", "red")
        
        # Create new .env file
        new_jwt_key = f"analisaai-jwt-{uuid4().hex}"
        env_file.write_text(f"JWT_SECRET_KEY={new_jwt_key}\n")
        
        print_colored("✅ Created new .env file with JWT_SECRET_KEY", "green")
        print(f"New JWT_SECRET_KEY: {new_jwt_key[:4]}...{new_jwt_key[-4:]}")
        
        # Update environment variable in current process
        os.environ['JWT_SECRET_KEY'] = new_jwt_key
        
        return True


def restart_server():
    """Restart the Flask server to apply configuration changes."""
    print_colored("\n==== Restarting Server ====", "blue")
    
    # Check if there's a restart script
    restart_script = Path('./restart_app.sh')
    
    if restart_script.exists() and os.access(restart_script, os.X_OK):
        print_colored("✅ Found restart script", "green")
        
        try:
            subprocess.run(['./restart_app.sh'], check=True)
            print_colored("✅ Server restart initiated", "green")
            
            # Wait for server to come back up
            print("Waiting for server to restart...")
            time.sleep(5)
            
            return True
        except subprocess.CalledProcessError as e:
            print_colored(f"❌ Error executing restart script: {str(e)}", "red")
            return False
    else:
        print_colored("⚠️ No restart script found or not executable", "yellow")
        print("You need to restart the server manually to apply changes:")
        print("1. Stop the current Flask application")
        print("2. Start it again with 'python run.py'")
        return False


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="JWT Token Troubleshooting Tool for AnalisaAI")
    parser.add_argument('--server', '-s', default=DEFAULT_BASE_URL, help='Server URL (default: http://localhost:5000)')
    parser.add_argument('--token', '-t', help='JWT token to analyze')
    parser.add_argument('--username', '-u', help='Username for testing login')
    parser.add_argument('--password', '-p', help='Password for testing login')
    parser.add_argument('--fix', '-f', action='store_true', help='Attempt to fix identified issues')
    parser.add_argument('--restart', '-r', action='store_true', help='Restart server after applying fixes')
    
    args = parser.parse_args()
    
    # Start the diagnostic process
    print_colored("===== AnalisaAI JWT Troubleshooting Tool =====", "blue")
    print(f"Server URL: {args.server}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==============================================")
    
    issues = []
    token_info = None
    
    # Step 1: Check environment variables
    env_issues = check_environment_variables()
    issues.extend(env_issues)
    
    # Step 2: Check server status
    server_issues = check_server_status(args.server)
    issues.extend(server_issues)
    
    # Step 3: Test login functionality
    if args.username and args.password:
        tokens = try_login(args.server, args.username, args.password)
        
        if tokens:
            # Analyze the access token
            access_token = tokens['access_token']
            token_info = analyze_token(access_token)
            
            if token_info:
                if not token_info['is_valid']:
                    issues.extend(token_info['issues'])
                
                # Test profile endpoint
                profile_result = test_profile_endpoint(args.server, access_token)
                
                if not profile_result:
                    issues.append("Could not access profile endpoint with token")
                
                # Test refresh token if available
                if tokens['refresh_token']:
                    refresh_result = test_refresh_token(args.server, tokens['refresh_token'])
                    
                    if not refresh_result:
                        issues.append("Could not refresh access token")
    
    # Test provided token if any
    elif args.token:
        token_info = analyze_token(args.token)
        
        if token_info:
            if not token_info['is_valid']:
                issues.extend(token_info['issues'])
            
            # Test profile endpoint with the token
            profile_result = test_profile_endpoint(args.server, args.token)
            
            if not profile_result:
                issues.append("Could not access profile endpoint with provided token")
    
    # Suggest fixes for identified issues
    suggest_fixes(issues)
    
    # Fix issues if requested
    if args.fix and issues:
        print_colored("\n==== Applying Fixes ====", "blue")
        
        # Fix JWT configuration
        if any("JWT_SECRET_KEY is missing" in issue for issue in issues) or \
           any("JWT is not properly configured" in issue for issue in issues):
            fix_jwt_configuration()
        
        # Restart server if requested
        if args.restart:
            restart_server()
    
    # Final summary
    print_colored("\n==== Troubleshooting Summary ====", "blue")
    
    if not issues:
        print_colored("✅ No JWT issues detected! Authentication should be working correctly.", "green")
    else:
        print_colored(f"⚠️ Found {len(issues)} potential issues:", "yellow")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        
        if args.fix:
            print_colored("\nFixes were applied. Please test authentication again.", "cyan")
            if args.restart:
                print("Server was restarted with new configuration.")
            else:
                print("You may need to restart the server for changes to take effect.")
        else:
            print_colored("\nRun with --fix flag to attempt automatic fixes:", "cyan")
            print("python scripts/fix_jwt_issues.py --fix")
            print("Add --restart to also restart the server after applying fixes.")
    
    # Help message
    print_colored("\n==== Next Steps ====", "blue")
    print("To test JWT authentication with a token:")
    print("  python scripts/test_token.py YOUR_TOKEN")
    print("\nTo test login and JWT flows:")
    print("  python test_jwt.py [username] [password]")
    print("\nFor detailed troubleshooting steps, refer to:")
    print("  docs/token_troubleshooting_steps.md")


if __name__ == "__main__":
    main()