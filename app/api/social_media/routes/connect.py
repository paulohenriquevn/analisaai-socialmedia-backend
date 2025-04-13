"""Routes for social media connection."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.user import User
from app.api.social_media.schemas.connect import SocialMediaConnectRequest, SocialMediaConnectResponse

from app.api.social_media import bp

@bp.route('/connect', methods=['POST'])
@jwt_required()
def connect_social_media():
    """Connect a social media account to the authenticated user."""
    # Get authenticated user
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Validate request data
    schema = SocialMediaConnectRequest()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid request data", "details": err.messages}), 400
    
    platform = data['platform']
    external_id = data['external_id']
    username = data['username']
    
    # Validate platform
    if platform not in ["instagram", "facebook", "tiktok"]:
        return jsonify({"error": "Plataforma não suportada"}), 400
    
    # Check if user already has this platform connected
    platform_id_field = f"{platform}_id"
    if getattr(user, platform_id_field):
        return jsonify({"error": "Rede social já vinculada"}), 409
    
    # Connect the social media account to the user
    setattr(user, platform_id_field, external_id)
    db.session.commit()
    
    # Prepare response
    response = {
        "id": user.id,
        "user_id": user.id,
        "platform": platform,
        "external_id": external_id,
        "username": username,
        "created_at": user.updated_at
    }
    
    return jsonify(SocialMediaConnectResponse().dump(response)), 201