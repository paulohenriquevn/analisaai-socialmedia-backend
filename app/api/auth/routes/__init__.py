"""
Authentication routes.
"""
from flask import Blueprint, jsonify, request, session, redirect, url_for, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt_identity
)
import os
import uuid
import logging

from app.extensions import db, oauth
from app.models import User, Role, SocialToken
from app.services.security_service import generate_tokens, get_user_roles
from app.services.oauth_service import save_token, get_token

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('auth', __name__)

# Debug route for OAuth clients
@bp.route('/debug/oauth-clients')
def debug_oauth_clients():
    """Debug endpoint to check registered OAuth clients."""
    clients = list(oauth._registry.keys())
    config = {k: bool(v) for k, v in {
        'FACEBOOK_CLIENT_ID': current_app.config.get('FACEBOOK_CLIENT_ID'),
        'FACEBOOK_CLIENT_SECRET': current_app.config.get('FACEBOOK_CLIENT_SECRET'),
        'FACEBOOK_REDIRECT_URI': current_app.config.get('FACEBOOK_REDIRECT_URI')
    }.items()}
    
    return jsonify({
        "registered_clients": clients,
        "config": config
    })

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

# Facebook authentication routes
@bp.route('/facebook')
def facebook_auth():
    """Initiate Facebook OAuth flow."""
    # Store state and action in session
    session['oauth_state'] = str(uuid.uuid4())
    # Check if this is a login/register request or just a connection request
    action = request.args.get('action', 'connect')
    session['oauth_action'] = action
    
    # If user is logged in and just connecting their account, store user_id
    if action == 'connect' and 'user_id' in request.args:
        session['user_id'] = request.args.get('user_id')
    
    redirect_uri = url_for('api.auth.facebook_callback', _external=True)
    try:
        return oauth.facebook.authorize_redirect(redirect_uri)
    except AttributeError as e:
        # Handle case where Facebook client is not registered
        logger.error(f"OAuth error: {str(e)}")
        if "No such client: facebook" in str(e):
            clients = list(oauth._registry.keys())
            logger.error(f"Available OAuth clients: {clients}")
            return jsonify({
                "error": "Facebook OAuth not configured",
                "details": "The Facebook OAuth client is not registered. Check environment variables.",
                "available_clients": clients
            }), 500
        raise


@bp.route('/facebook/callback')
def facebook_callback():
    """Handle Facebook OAuth callback."""
    try:
        # Get token from Facebook
        token = oauth.facebook.authorize_access_token()
        if not token:
            return jsonify({"error": "Failed to get token"}), 400
        
        # Get user info from Facebook
        resp = oauth.facebook.get(
            'https://graph.facebook.com/me?fields=id,name,email,picture'
        )
        facebook_user_info = resp.json()
        
        # Check what action we're performing
        action = session.get('oauth_action', 'connect')
        
        if action == 'connect':
            # User is already logged in and connecting Facebook
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({"error": "No user ID in session"}), 400
            
            # Save token to the user's account
            save_token(user_id, 'facebook', token)
            
            # Redirect to frontend with success message
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
            return redirect(f"{frontend_url}/settings/connected-accounts?status=success&platform=facebook")
        
        elif action == 'login' or action == 'register':
            # User is logging in or registering with Facebook
            # Check if user with this Facebook ID or email exists
            email = facebook_user_info.get('email')
            facebook_id = facebook_user_info.get('id')
            
            if not email:
                return jsonify({"error": "Facebook account doesn't have an email"}), 400
            
            # Look up user by email
            user = User.query.filter_by(email=email).first()
            
            if action == 'login' and not user:
                # User tried to login with Facebook but doesn't have an account
                return redirect(f"{os.environ.get('FRONTEND_URL', 'http://localhost:4200')}/auth/signup?error=no_account&facebook=true")
            
            if not user and action == 'register':
                # Create new user with Facebook data
                username = facebook_user_info.get('name', '').replace(' ', '_').lower() 
                
                # Check if username exists and append a number if it does
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User(
                    username=username,
                    email=email,
                    facebook_id=facebook_id,
                    profile_image=facebook_user_info.get('picture', {}).get('data', {}).get('url')
                )
                
                # Set a temporary password (user can change it later)
                temp_password = str(uuid.uuid4())
                user.set_password(temp_password)
                
                # Assign default role
                default_role = Role.query.filter_by(name='user').first()
                if default_role:
                    user.roles.append(default_role)
                
                db.session.add(user)
                db.session.commit()
            
            # Save/update Facebook token
            save_token(user.id, 'facebook', token)
            
            # Generate tokens for the user
            tokens = generate_tokens(user.id)
            
            # Redirect to frontend with tokens
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
            token_param = f"access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
            
            if action == 'register':
                return redirect(f"{frontend_url}/auth/welcome?{token_param}")
            else:
                return redirect(f"{frontend_url}/dashboard?{token_param}")
        
        else:
            return jsonify({"error": "Invalid action"}), 400
    
    except Exception as e:
        logger.error(f"Facebook callback error: {str(e)}")
        return jsonify({"error": "Authentication failed", "details": str(e)}), 500


# Instagram OAuth routes
@bp.route('/instagram')
@jwt_required()
def instagram_auth():
    """Initiate Instagram OAuth flow."""
    user_id = get_jwt_identity()
    # Store state for later verification
    session['user_id'] = user_id
    redirect_uri = url_for('api.auth.instagram_callback', _external=True)
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


# TikTok OAuth routes
@bp.route('/tiktok')
@jwt_required()
def tiktok_auth():
    """Initiate TikTok OAuth flow."""
    user_id = get_jwt_identity()
    # Store state for later verification
    session['user_id'] = user_id
    redirect_uri = url_for('api.auth.tiktok_callback', _external=True)
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