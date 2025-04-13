"""
Authentication routes.
"""
from flask import Blueprint, jsonify, request, session, redirect, url_for
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt_identity
)
import os

from app.extensions import db, oauth
from app.models import User, Role
from app.services.security_service import generate_tokens, get_user_roles
from app.services.oauth_service import save_token, get_token

# Create blueprint
bp = Blueprint('auth', __name__)

# Basic authentication routes
@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.json
    
    # Validate required fields
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    # Assign default role
    default_role = Role.query.filter_by(name='user').first()
    if default_role:
        user.roles.append(default_role)
    
    db.session.add(user)
    db.session.commit()
    
    # Generate tokens
    tokens = generate_tokens(user.id)
    
    return jsonify({
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
def login():
    """Log in a user."""
    data = request.json
    
    # Validate required fields
    if not all(k in data for k in ('username', 'password')):
        return jsonify({"error": "Missing username or password"}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    # Verify password
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    
    # Generate tokens
    tokens = generate_tokens(user.id)
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": get_user_roles(user)
        },
        "tokens": tokens
    })


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh JWT token."""
    user_id = get_jwt_identity()
    
    # Find user
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Invalid token"}), 401
    
    # Generate new access token
    access_token = create_access_token(
        identity=user_id
    )
    
    return jsonify({
        "access_token": access_token
    })


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    user_id = get_jwt_identity()
    
    # Find user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get user's organizations
    organizations = [{
        "id": org.id,
        "name": org.name,
        "plan": org.plan.name if org.plan else None
    } for org in user.organizations]
    
    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": get_user_roles(user),
            "created_at": user.created_at.isoformat(),
            "organizations": organizations
        }
    })

# Social media OAuth routes
@bp.route('/instagram')
@jwt_required()
def instagram_auth():
    """Initiate Instagram OAuth flow."""
    user_id = get_jwt_identity()
    # Store state for later verification
    session['user_id'] = user_id
    redirect_uri = url_for('auth.instagram_callback', _external=True)
    return oauth.instagram.authorize_redirect(redirect_uri)


@bp.route('/instagram/callback')
def instagram_callback():
    """Handle Instagram OAuth callback."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Invalid session"}), 401
    
    # Get token from Instagram
    token = oauth.instagram.authorize_access_token()
    if not token:
        return jsonify({"error": "Failed to get token"}), 400
    
    # Save token to database
    save_token(user_id, 'instagram', token)
    
    # Redirect to frontend with success message
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
    return redirect(f"{frontend_url}/settings/connected-accounts?status=success&platform=instagram")


@bp.route('/facebook')
@jwt_required()
def facebook_auth():
    """Initiate Facebook OAuth flow."""
    user_id = get_jwt_identity()
    # Store state for later verification
    session['user_id'] = user_id
    redirect_uri = url_for('auth.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)


@bp.route('/facebook/callback')
def facebook_callback():
    """Handle Facebook OAuth callback."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Invalid session"}), 401
    
    # Get token from Facebook
    token = oauth.facebook.authorize_access_token()
    if not token:
        return jsonify({"error": "Failed to get token"}), 400
    
    # Save token to database
    save_token(user_id, 'facebook', token)
    
    # Redirect to frontend with success message
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
    return redirect(f"{frontend_url}/settings/connected-accounts?status=success&platform=facebook")


@bp.route('/tiktok')
@jwt_required()
def tiktok_auth():
    """Initiate TikTok OAuth flow."""
    user_id = get_jwt_identity()
    # Store state for later verification
    session['user_id'] = user_id
    redirect_uri = url_for('auth.tiktok_callback', _external=True)
    return oauth.tiktok.authorize_redirect(redirect_uri)


@bp.route('/tiktok/callback')
def tiktok_callback():
    """Handle TikTok OAuth callback."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Invalid session"}), 401
    
    # Get token from TikTok
    token = oauth.tiktok.authorize_access_token()
    if not token:
        return jsonify({"error": "Failed to get token"}), 400
    
    # Save token to database
    save_token(user_id, 'tiktok', token)
    
    # Redirect to frontend with success message
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
    return redirect(f"{frontend_url}/settings/connected-accounts?status=success&platform=tiktok")