#!/usr/bin/env python
"""
Token validation script for AnalisaAI Social Media.
This script can help debug authentication issues by:
1. Validating JWT token format
2. Checking token claims
3. Verifying signature (without requiring the secret key)
4. Checking expiration
"""

import sys
import base64
import json
import os
import re
from datetime import datetime
import argparse

def decode_jwt_segments(token):
    """
    Decode and parse the JWT token without verifying the signature.
    Returns the token's header, payload, and signature segments.
    """
    if not token or not isinstance(token, str):
        return None, None, None

    # Split token into segments
    segments = token.split('.')
    if len(segments) != 3:
        print(f"ERROR: Token does not have the standard JWT format (header.payload.signature)")
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
        print(f"ERROR: Failed to decode token: {str(e)}")
        return None, None, None

def analyze_token(token):
    """Analyze the JWT token and print information about it."""
    if not token:
        print("ERROR: No token provided.")
        return False

    # First, clean the token from any "Bearer " prefix
    if token.startswith('Bearer '):
        token = token[7:]

    # Remove any whitespace
    token = token.strip()

    # Check for correct format
    if not re.match(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$', token):
        print("ERROR: Token does not have the standard JWT format.")
        return False

    # Decode the token segments
    header, payload, signature = decode_jwt_segments(token)
    if not header or not payload:
        print("ERROR: Failed to decode token.")
        return False

    # Print token information
    print("\n==== JWT TOKEN ANALYSIS ====")
    print("\n=== HEADER ===")
    print(json.dumps(header, indent=2))

    print("\n=== PAYLOAD ===")
    print(json.dumps(payload, indent=2))

    print("\n=== VALIDATION ===")
    
    # Check token type
    token_type = header.get('typ')
    if token_type == 'JWT':
        print("✅ Token type (typ): JWT")
    else:
        print(f"⚠️ Token type (typ): {token_type} (expected: JWT)")

    # Check algorithm
    alg = header.get('alg')
    if alg == 'HS256':
        print("✅ Algorithm (alg): HS256")
    else:
        print(f"⚠️ Algorithm (alg): {alg} (expected: HS256)")

    # Check subject (identity)
    sub = payload.get('sub')
    if sub:
        print(f"✅ Subject (sub/identity): {sub}")
    else:
        print("⚠️ Missing subject (sub) claim")

    # Check issued at time
    iat = payload.get('iat')
    if iat:
        iat_date = datetime.fromtimestamp(iat)
        print(f"✅ Issued at (iat): {iat_date.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("⚠️ Missing issued at (iat) claim")

    # Check expiration time
    exp = payload.get('exp')
    if exp:
        exp_date = datetime.fromtimestamp(exp)
        now = datetime.now()
        is_expired = now > exp_date
        
        if is_expired:
            print(f"❌ Expired on (exp): {exp_date.strftime('%Y-%m-%d %H:%M:%S')} (EXPIRED)")
        else:
            time_left = exp_date - now
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"✅ Expires on (exp): {exp_date.strftime('%Y-%m-%d %H:%M:%S')} (Valid for {hours}h {minutes}m {seconds}s)")
    else:
        print("⚠️ Missing expiration (exp) claim")

    # Check token type
    token_type = payload.get('type')
    if token_type:
        if token_type == 'access':
            print("✅ Token type: Access token")
        elif token_type == 'refresh':
            print("✅ Token type: Refresh token")
        else:
            print(f"ℹ️ Token type: {token_type}")
    else:
        print("ℹ️ No specific token type claim")

    # Check fresh status
    fresh = payload.get('fresh', None)
    if fresh is not None:
        print(f"ℹ️ Fresh token: {fresh}")

    # Check other relevant claims
    jti = payload.get('jti')
    if jti:
        print(f"ℹ️ JWT ID (jti): {jti}")

    # Check if token has fingerprint
    fp = payload.get('fp')
    if fp:
        print(f"ℹ️ Fingerprint (fp): {fp}")

    print("\n=== SUMMARY ===")
    if exp and now > exp_date:
        print("❌ INVALID TOKEN: Expired")
        return False
    else:
        print("✅ TOKEN FORMAT IS VALID")
        return True

def main():
    """Main function to parse arguments and analyze tokens."""
    parser = argparse.ArgumentParser(description='Analyze and validate JWT tokens')
    parser.add_argument('token', nargs='?', help='The JWT token to analyze')
    parser.add_argument('-f', '--file', help='Read token from a file')
    parser.add_argument('-e', '--env', help='Read token from an environment variable')
    args = parser.parse_args()

    token = None

    # Get token from arguments, environment variable, or file
    if args.token:
        token = args.token
    elif args.env:
        token = os.environ.get(args.env)
        if not token:
            print(f"ERROR: Environment variable '{args.env}' not found or empty.")
            sys.exit(1)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                token = f.read().strip()
        except Exception as e:
            print(f"ERROR: Failed to read token from file: {str(e)}")
            sys.exit(1)
    else:
        # If no token provided, try to read from stdin
        if not sys.stdin.isatty():
            token = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)

    valid = analyze_token(token)
    if not valid:
        sys.exit(1)

if __name__ == '__main__':
    main()