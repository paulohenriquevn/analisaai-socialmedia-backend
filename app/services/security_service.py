from cryptography.fernet import Fernet
import base64
import os
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from app.models import User, Role

# Generate a valid Fernet key
def get_encryption_key():
    """
    Generate or retrieve a valid Fernet key for encryption.
    Fernet keys must be 32 bytes, URL-safe base64-encoded.
    """
    stored_key = os.getenv('ENCRYPTION_KEY')
    
    # If stored key is provided and is valid format, use it
    if stored_key and len(stored_key) >= 32:
        try:
            # Test if the key is a valid Fernet key
            Fernet(stored_key.encode())
            return stored_key.encode()
        except Exception:
            # If not valid, proceed to generate a key
            pass
    
    # Generate a secure key from the passphrase
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    
    # Use the provided key as a passphrase or use default
    default_key = "analisaai-social-media-default-secure-key-2024"
    passphrase = stored_key or default_key
    
    # Create a secure key from the passphrase
    salt = b'analisaai-salt'  # In production, this should be stored securely
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key_bytes = kdf.derive(passphrase.encode())
    
    # Encode to URL-safe base64
    encoded_key = base64.urlsafe_b64encode(key_bytes)
    return encoded_key

# Create a valid Fernet key for encryption
key = get_encryption_key()
cipher_suite = Fernet(key)

def encrypt_token(token):
    """Encrypts a token for secure storage."""
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(token):
    """Decrypts a stored token."""
    return cipher_suite.decrypt(token.encode()).decode()

def generate_tokens(user_id):
    """
    Generate JWT access and refresh tokens for a user.
    
    Args:
        user_id: The ID of the user to generate tokens for
        
    Returns:
        dict: Dictionary containing access_token and refresh_token
    """
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(hours=1)
    )
    
    refresh_token = create_refresh_token(
        identity=user_id,
        expires_delta=timedelta(days=30)
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

def get_user_roles(user):
    """
    Get role names for a user.
    
    Args:
        user: User object
    
    Returns:
        list: List of role names
    """
    return [role.name for role in user.roles]

def has_role(user, role_name):
    """
    Check if user has a specific role.
    
    Args:
        user: User object
        role_name: Role name to check
    
    Returns:
        bool: True if user has the role, False otherwise
    """
    return any(role.name == role_name for role in user.roles)

def init_roles(db):
    """Initialize default roles in the database."""
    default_roles = ['admin', 'user', 'analyst']
    
    for role_name in default_roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    
    db.session.commit() 