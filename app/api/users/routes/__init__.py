"""
User-related routes.
"""
import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone

from app.models import SocialToken, User
from app.services.social_media_service import SocialMediaService
from app.services.oauth_service import get_token

# Create blueprint
bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)

@bp.route('/me/connected-accounts', methods=['GET'])
@jwt_required()
def get_connected_accounts():
    """Get all connected social media accounts for the current user."""
    user_id = int(get_jwt_identity())
    
    # Query all tokens for this user
    tokens = SocialToken.query.filter_by(user_id=user_id).all()
    
    # Format response
    connected_accounts = [
        {
            "platform": token.platform,
            "connected_at": token.updated_at.isoformat(),
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
            "is_expired": token.expires_at < datetime.now(timezone.utc) if token.expires_at else False
        }
        for token in tokens
    ]
    
    return jsonify({
        "connected_accounts": connected_accounts
    })

@bp.route('/me/instagram-accounts', methods=['GET'])
@jwt_required()
def get_instagram_accounts():
    """Get connected Instagram business accounts for the current user."""
    user_id = int(get_jwt_identity())
    
    # Check if user has an Instagram token
    token = SocialToken.query.filter_by(user_id=user_id, platform='instagram').first()
    if not token:
        logger.info(f"User {user_id} has no Instagram account connected")
        return jsonify({
            "error": "no_instagram_account",
            "message": "No Instagram account connected",
            "accounts": []
        }), 404
    
    try:
        # Try to fetch profile data
        profile_data = SocialMediaService.fetch_instagram_profile(user_id)
        
        if not profile_data:
            logger.warning(f"Failed to fetch Instagram profile for user {user_id}")
            return jsonify({
                "error": "failed_to_fetch",
                "message": "Failed to fetch Instagram profile data",
                "accounts": []
            }), 400
        
        # Check if there's an error message in the response
        if 'error' in profile_data:
            logger.warning(f"Instagram error for user {user_id}: {profile_data.get('error')}")
            return jsonify({
                "error": profile_data.get('error'),
                "message": profile_data.get('message', 'Error fetching Instagram account'),
                "accounts": []
            }), 400
            
        # Create a simplified response
        accounts = [{
            "username": profile_data.get('username'),
            "full_name": profile_data.get('full_name'),
            "profile_image": profile_data.get('profile_image'),
            "followers_count": profile_data.get('followers_count'),
            "account_type": profile_data.get('account_type', 'business'),
            "facebook_page_name": profile_data.get('facebook_page_name'),
            "profile_url": profile_data.get('profile_url')
        }]
        
        return jsonify({
            "accounts": accounts
        })
        
    except Exception as e:
        logger.error(f"Error getting Instagram accounts: {str(e)}")
        return jsonify({
            "error": "internal_error",
            "message": "An error occurred while getting Instagram accounts",
            "accounts": []
        }), 500

@bp.route('/me/instagram-profile', methods=['GET'])
@jwt_required()
def get_instagram_profile():
    """Get detailed Instagram profile data including metrics."""
    user_id = int(get_jwt_identity())
    
    # Optional username parameter
    username = request.args.get('username')
    
    # Check if user has an Instagram token
    token = SocialToken.query.filter_by(user_id=user_id, platform='instagram').first()
    if not token:
        return jsonify({
            "error": "no_instagram_account",
            "message": "No Instagram account connected"
        }), 404
    
    try:
        # Try to fetch profile data
        profile_data = SocialMediaService.fetch_instagram_profile(user_id, username)
        
        if not profile_data:
            return jsonify({
                "error": "failed_to_fetch",
                "message": "Failed to fetch Instagram profile data"
            }), 400
        
        # Check if there's an error message in the response
        if 'error' in profile_data:
            return jsonify({
                "error": profile_data.get('error'),
                "message": profile_data.get('message', 'Error fetching Instagram account')
            }), 400
            
        return jsonify(profile_data)
        
    except Exception as e:
        logger.error(f"Error getting Instagram profile: {str(e)}")
        return jsonify({
            "error": "internal_error",
            "message": "An error occurred while getting Instagram profile"
        }), 500
        
@bp.route('/me/connected-accounts/<platform>', methods=['DELETE'])
@jwt_required()
def disconnect_account(platform):
    """Disconnect a social media account."""
    user_id = int(get_jwt_identity())
    
    # Validate platform
    valid_platforms = ['instagram', 'facebook', 'tiktok']
    if platform not in valid_platforms:
        return jsonify({
            "error": "invalid_platform",
            "message": f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        }), 400
    
    # Find the token
    token = SocialToken.query.filter_by(user_id=user_id, platform=platform).first()
    if not token:
        return jsonify({
            "error": "not_connected",
            "message": f"No {platform} account connected"
        }), 404
    
    try:
        # Delete the token
        from app.extensions import db
        db.session.delete(token)
        db.session.commit()
        
        # Also clear the social ID if applicable
        user = User.query.get(user_id)
        if platform == 'facebook':
            user.facebook_id = None
        elif platform == 'instagram':
            user.instagram_id = None
        elif platform == 'tiktok':
            user.tiktok_id = None
        
        db.session.commit()
        
        return jsonify({
            "message": f"{platform.capitalize()} account disconnected successfully"
        })
        
    except Exception as e:
        logger.error(f"Error disconnecting {platform} account: {str(e)}")
        return jsonify({
            "error": "internal_error",
            "message": f"An error occurred while disconnecting {platform} account"
        }), 500