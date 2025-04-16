from flask import Blueprint, jsonify, request, session, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity, get_jwt
)
from app.utils.jwt_blacklist import add_token_to_blacklist
import logging

from app.extensions import db
from common.user import User, Role
from app.services.security_service import generate_tokens, get_user_roles

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('auth', __name__)
from flask import current_app
limiter = None

def get_limiter():
    global limiter
    if limiter is None:
        limiter = current_app.limiter
    return limiter


@bp.route('/register', methods=['POST'])
@get_limiter().limit("3 per minute")
def register():
    from app.schemas.auth import RegisterSchema
    data = request.json or {}
    errors = RegisterSchema().validate(data)
    if errors:
        return jsonify({"error": "Validation error", "messages": errors}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    default_role = Role.query.filter_by(name='user').first()
    if default_role:
        user.roles.append(default_role)
    
    db.session.add(user)
    db.session.commit()
    
    # Generate tokens
    tokens = generate_tokens(user.id)
    
    return jsonify({
        "status": "ok",
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": get_user_roles(user)
        },
        "tokens": tokens
    }), 201


@bp.route('/login', methods=['POST'])
@get_limiter().limit("5 per minute")
def login():
    from app.schemas.auth import LoginSchema
    data = request.json or {}
    errors = LoginSchema().validate(data)
    if errors:
        return jsonify({"error": "Validation error", "messages": errors}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    
    tokens = generate_tokens(user.id)
    return jsonify({
        "status": "ok",
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": get_user_roles(user)
        },
        "tokens": tokens
    }), 200


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    add_token_to_blacklist(jti)
    return jsonify({
        "status": "ok",
        "message": "Logout successful. Token revoked."
    }), 200


@bp.route('/status')
def status():
    clients = list(oauth._registry.keys())
    
    import os
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:4200')
    
    db_status = "ok"
    try:
        User.query.limit(1).all()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "success": True,
        "message": "Status retrieved successfully",
        "oauth_clients": clients,
        "facebook_configured": 'facebook' in clients,
        "frontend_url": frontend_url,
        "db_status": db_status,
        "api_version": "1.0.0",
        "session_enabled": session.get('test_session', True)
    }), 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    user_id = int(get_jwt_identity())
    
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Token inválido"}), 401
    
    access_token = create_access_token(
        identity=user_id
    )
    
    return jsonify({
        "success": True,
        "message": "Token refreshed successfully",
        "access_token": access_token
    }), 200
