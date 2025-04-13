"""
OAuth service for social media platform integrations.
"""
import requests
import logging
from datetime import datetime, timedelta
from flask import current_app
from app.extensions import oauth

logger = logging.getLogger(__name__)

def config_oauth(app):
    """Configure OAuth clients for various social media platforms."""
    logger.info("Configuring OAuth clients...")
    
    # Instagram OAuth configuration
    if 'INSTAGRAM_CLIENT_ID' in app.config and app.config['INSTAGRAM_CLIENT_ID']:
        logger.info("Registering Instagram OAuth client")
        oauth.register(
            name='instagram',
            client_id=app.config['INSTAGRAM_CLIENT_ID'],
            client_secret=app.config['INSTAGRAM_CLIENT_SECRET'],
            authorize_url='https://api.instagram.com/oauth/authorize',
            authorize_params=None,
            access_token_url='https://api.instagram.com/oauth/access_token',
            access_token_params=None,
            refresh_token_url=None,
            redirect_uri=app.config['INSTAGRAM_REDIRECT_URI'],
            client_kwargs={'scope': 'user_profile,user_media'},
        )
    else:
        logger.warning("Instagram OAuth client not configured - missing credentials")
    
    # Facebook OAuth configuration
    if 'FACEBOOK_CLIENT_ID' in app.config and app.config['FACEBOOK_CLIENT_ID']:
        logger.info(f"Registering Facebook OAuth client with ID: {app.config['FACEBOOK_CLIENT_ID'][:5]}...")
        oauth.register(
            name='facebook',
            client_id=app.config['FACEBOOK_CLIENT_ID'],
            client_secret=app.config['FACEBOOK_CLIENT_SECRET'],
            authorize_url='https://www.facebook.com/v16.0/dialog/oauth',
            authorize_params=None,
            access_token_url='https://graph.facebook.com/v16.0/oauth/access_token',
            access_token_params=None,
            refresh_token_url=None,
            redirect_uri=app.config['FACEBOOK_REDIRECT_URI'],
            client_kwargs={'scope': 'pages_read_engagement,instagram_basic,instagram_manage_insights'},
        )
    else:
        logger.warning("Facebook OAuth client not configured - missing credentials")
    
    # TikTok OAuth configuration
    if 'TIKTOK_CLIENT_ID' in app.config and app.config['TIKTOK_CLIENT_ID']:
        logger.info("Registering TikTok OAuth client")
        oauth.register(
            name='tiktok',
            client_id=app.config['TIKTOK_CLIENT_ID'],
            client_secret=app.config['TIKTOK_CLIENT_SECRET'],
            authorize_url='https://www.tiktok.com/v2/auth/authorize',
            authorize_params=None,
            access_token_url='https://open.tiktokapis.com/v2/oauth/token',
            access_token_params=None,
            refresh_token_url='https://open.tiktokapis.com/v2/oauth/token',
            redirect_uri=app.config['TIKTOK_REDIRECT_URI'],
            client_kwargs={'scope': 'user.info.basic,video.list'},
        )
    else:
        logger.warning("TikTok OAuth client not configured - missing credentials")
        
    # Log registered clients
    logger.info(f"Registered OAuth clients: {list(oauth._registry.keys())}")


def save_token(user_id, platform, token_data):
    """
    Save OAuth tokens securely in the database.
    
    Args:
        user_id: User ID to associate the token with
        platform: Platform name (instagram, facebook, tiktok)
        token_data: Token data from OAuth provider
    """
    from app.extensions import db
    from app.models import SocialToken
    from app.services.security_service import encrypt_token
    
    # Encrypt sensitive token data before storing
    encrypted_access_token = encrypt_token(token_data['access_token'])
    
    # Handle refresh token if available
    refresh_token = None
    if 'refresh_token' in token_data and token_data['refresh_token']:
        refresh_token = encrypt_token(token_data['refresh_token'])
    
    # Calculate expiration time if available
    expires_at = None
    if 'expires_in' in token_data and token_data['expires_in']:
        expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
    
    # Check if token for this platform already exists
    existing_token = SocialToken.query.filter_by(
        user_id=user_id,
        platform=platform
    ).first()
    
    if existing_token:
        # Update existing token
        existing_token.access_token = encrypted_access_token
        if refresh_token:
            existing_token.refresh_token = refresh_token
        if expires_at:
            existing_token.expires_at = expires_at
        existing_token.updated_at = datetime.utcnow()
    else:
        # Create new token record
        new_token = SocialToken(
            user_id=user_id,
            platform=platform,
            access_token=encrypted_access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        db.session.add(new_token)
    
    db.session.commit()


def get_token(user_id, platform):
    """
    Retrieve a user's token for a specific platform.
    
    Args:
        user_id: User ID
        platform: Platform name
        
    Returns:
        dict: Token data or None if not found
    """
    from app.models import SocialToken
    from app.services.security_service import decrypt_token
    
    token = SocialToken.query.filter_by(
        user_id=user_id,
        platform=platform
    ).first()
    
    if not token:
        return None
    
    # Check if token is expired and needs refresh
    if token.expires_at and token.expires_at < datetime.utcnow() and token.refresh_token:
        try:
            # Refresh the token
            refreshed_token = refresh_social_token(platform, decrypt_token(token.refresh_token))
            if refreshed_token:
                # Update with new token data
                save_token(user_id, platform, refreshed_token)
                return {
                    'access_token': refreshed_token['access_token'],
                    'expires_at': token.expires_at
                }
        except Exception as e:
            current_app.logger.error(f"Error refreshing {platform} token: {str(e)}")
    
    # Return decrypted token
    return {
        'access_token': decrypt_token(token.access_token),
        'expires_at': token.expires_at
    }


def refresh_social_token(platform, refresh_token):
    """
    Refresh an expired OAuth token.
    
    Args:
        platform: Platform name
        refresh_token: Refresh token
        
    Returns:
        dict: New token data or None if refresh failed
    """
    if platform == 'instagram' or platform == 'facebook':
        # Facebook and Instagram use the same token refresh mechanism
        response = requests.get(
            'https://graph.facebook.com/v16.0/oauth/access_token',
            params={
                'grant_type': 'fb_exchange_token',
                'client_id': current_app.config['FACEBOOK_CLIENT_ID'],
                'client_secret': current_app.config['FACEBOOK_CLIENT_SECRET'],
                'fb_exchange_token': refresh_token
            }
        )
        if response.status_code == 200:
            return response.json()
    
    elif platform == 'tiktok':
        response = requests.post(
            'https://open.tiktokapis.com/v2/oauth/token/',
            data={
                'client_key': current_app.config['TIKTOK_CLIENT_ID'],
                'client_secret': current_app.config['TIKTOK_CLIENT_SECRET'],
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        if response.status_code == 200:
            return response.json()
    
    return None