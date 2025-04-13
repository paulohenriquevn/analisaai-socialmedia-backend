"""
User-related routes.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import SocialToken

# Create blueprint
bp = Blueprint('users', __name__)

@bp.route('/me/connected-accounts', methods=['GET'])
@jwt_required()
def get_connected_accounts():
    """Get all connected social media accounts for the current user."""
    user_id = get_jwt_identity()
    
    # Query all tokens for this user
    tokens = SocialToken.query.filter_by(user_id=user_id).all()
    
    # Format response
    connected_accounts = [
        {
            "platform": token.platform,
            "connected_at": token.updated_at.isoformat()
        }
        for token in tokens
    ]
    
    return jsonify({
        "connected_accounts": connected_accounts
    })