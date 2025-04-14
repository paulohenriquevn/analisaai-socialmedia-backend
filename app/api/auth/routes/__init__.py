"""
Authentication routes.
"""
from flask import Blueprint, jsonify, request, session, redirect, url_for, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt_identity
)
import os
import uuid
import json
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
    import os
    
    config = {
        'FACEBOOK_CLIENT_ID': bool(os.getenv('FACEBOOK_CLIENT_ID')),
        'FACEBOOK_CLIENT_SECRET': bool(os.getenv('FACEBOOK_CLIENT_SECRET')),
        'FACEBOOK_REDIRECT_URI': os.getenv('FACEBOOK_REDIRECT_URI', 'http://localhost:5000/api/auth/facebook/callback'),
        'FRONTEND_URL': os.getenv('FRONTEND_URL', 'http://localhost:4200')
    }
    
    return jsonify({
        "registered_clients": clients,
        "config": config,
        "facebook_client_configured": 'facebook' in oauth._registry,
        "session_supported": bool(session.get('test', True))
    })

@bp.route('/auth-status')
def auth_status():
    """Check authentication status and configuration."""
    # Check if OAuth clients are registered
    clients = list(oauth._registry.keys())
    
    # Check environment variables
    import os
    
    # Calculate frontend URL to be used in redirects
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:4200')
    
    # Check database connection
    db_status = "ok"
    try:
        # Try a simple query to check database connection
        User.query.limit(1).all()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "ok",
        "oauth_clients": clients,
        "facebook_configured": 'facebook' in clients,
        "frontend_url": frontend_url,
        "db_status": db_status,
        "api_version": "1.0.0",
        "session_enabled": session.get('test_session', True)
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
    
    # Start process to sync influencer data and calculate all metrics
    try:
        # Import required modules
        from app.services.social_media_service import SocialMediaService
        from app.services.engagement_service import EngagementService
        from app.services.reach_service import ReachService
        from app.services.growth_service import GrowthService
        from app.services.score_service import ScoreService
        from app.models.influencer import Influencer
        
        logger.info(f"Starting automatic metrics update on login for user {user.id}")
        
        # Get all influencers from the database to sync 
        # Order by updated_at to prioritize oldest entries
        influencers = Influencer.query.order_by(Influencer.updated_at.asc()).all()
        
        if influencers:
            logger.info(f"Found {len(influencers)} influencers to update")
            
            # Process a limited number of influencers (to avoid long login times)
            for influencer in influencers[:5]:  # Limit to 5 influencers per login
                platform = influencer.platform
                username = influencer.username
                influencer_id = influencer.id
                
                if platform and username:
                    logger.info(f"Updating metrics for {platform} influencer {username} (ID: {influencer_id})")
                    
                    try:
                        # Step 1: Update profile data from social media APIs
                        # Use Apify to fetch updated profile data
                        if platform == 'instagram':
                            profile_data = SocialMediaService.fetch_instagram_profile(user.id, username)
                        elif platform == 'facebook':
                            profile_data = SocialMediaService.fetch_facebook_profile(user.id, username)
                        elif platform == 'tiktok':
                            profile_data = SocialMediaService.fetch_tiktok_profile(user.id, username)
                        else:
                            logger.warning(f"Unsupported platform: {platform}")
                            continue
                            
                        # Update the influencer data if successful
                        updated_influencer = None
                        if profile_data and 'error' not in profile_data:
                            updated_influencer = SocialMediaService.save_influencer_data(profile_data)
                            logger.info(f"Successfully synced {platform} data for influencer {username}")
                        else:
                            logger.warning(f"Failed to fetch data for {platform} influencer {username}")
                            # Continue with existing data even if fetch fails
                            updated_influencer = influencer
                        
                        # Step 2: Calculate and store all metrics
                        if updated_influencer:
                            try:
                                # Calculate engagement metrics
                                logger.info(f"Calculating engagement metrics for influencer {username}")
                                engagement_metrics = EngagementService.calculate_engagement_metrics(updated_influencer.id)
                                if engagement_metrics:
                                    logger.info(f"Successfully calculated engagement metrics for influencer {username}")
                            except Exception as metric_error:
                                logger.error(f"Error calculating engagement metrics: {str(metric_error)}")
                            
                            try:
                                # Calculate reach metrics
                                logger.info(f"Calculating reach metrics for influencer {username}")
                                reach_metrics = ReachService.calculate_reach_metrics(updated_influencer.id, user.id)
                                if reach_metrics:
                                    logger.info(f"Successfully calculated reach metrics for influencer {username}")
                            except Exception as metric_error:
                                logger.error(f"Error calculating reach metrics: {str(metric_error)}")
                            
                            try:
                                # Calculate growth metrics
                                logger.info(f"Calculating growth metrics for influencer {username}")
                                growth_metrics = GrowthService.calculate_growth_metrics(updated_influencer.id)
                                if growth_metrics:
                                    logger.info(f"Successfully calculated growth metrics for influencer {username}")
                            except Exception as metric_error:
                                logger.error(f"Error calculating growth metrics: {str(metric_error)}")
                            
                            try:
                                # Calculate relevance score (depends on other metrics being calculated first)
                                logger.info(f"Calculating relevance score for influencer {username}")
                                score = ScoreService.calculate_relevance_score(updated_influencer.id)
                                if score:
                                    logger.info(f"Successfully calculated relevance score for influencer {username}")
                            except Exception as metric_error:
                                logger.error(f"Error calculating relevance score: {str(metric_error)}")
                            
                            logger.info(f"Metrics update process completed for influencer {username}")
                            
                    except Exception as e:
                        logger.error(f"Error updating metrics for {platform} influencer {username}: {str(e)}")
        else:
            logger.info("No influencers found to update")
            
    except Exception as e:
        logger.error(f"Error performing automatic metrics update: {str(e)}")
        # Don't block login if update fails
    
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
    user_id = int(get_jwt_identity())
    
    # Find user
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Token inválido"}), 401
    
    # Generate new access token
    access_token = create_access_token(
        identity=user_id
    )
    
    # Schedule metrics update in background
    # This is done asynchronously to not block the token refresh
    try:
        # Import necessary services
        from app.services.engagement_service import EngagementService
        from app.services.reach_service import ReachService
        from app.services.growth_service import GrowthService
        from app.services.score_service import ScoreService
        from app.models.influencer import Influencer
        import threading
        
        # Define a function to run in a separate thread
        def update_metrics_in_background():
            try:
                logger.info(f"Starting metrics update in background during token refresh for user {user_id}")
                
                # Get one oldest updated influencer to refresh
                influencer = Influencer.query.order_by(Influencer.updated_at.asc()).first()
                
                if influencer:
                    influencer_id = influencer.id
                    username = influencer.username
                    
                    logger.info(f"Updating metrics for influencer {username} (ID: {influencer_id})")
                    
                    # Calculate all metrics with individual error handling for each step
                    try:
                        engagement_metrics = EngagementService.calculate_engagement_metrics(influencer_id)
                        logger.info(f"Successfully calculated engagement metrics for influencer {username}")
                    except Exception as e:
                        logger.error(f"Error calculating engagement metrics: {str(e)}")
                    
                    try:
                        reach_metrics = ReachService.calculate_reach_metrics(influencer_id, user_id)
                        logger.info(f"Successfully calculated reach metrics for influencer {username}")
                    except Exception as e:
                        logger.error(f"Error calculating reach metrics: {str(e)}")
                    
                    try:
                        growth_metrics = GrowthService.calculate_growth_metrics(influencer_id)
                        logger.info(f"Successfully calculated growth metrics for influencer {username}")
                    except Exception as e:
                        logger.error(f"Error calculating growth metrics: {str(e)}")
                    
                    # Calculate score last since it depends on other metrics
                    try:
                        score = ScoreService.calculate_relevance_score(influencer_id)
                        logger.info(f"Successfully calculated relevance score for influencer {username}")
                    except Exception as e:
                        logger.error(f"Error calculating relevance score: {str(e)}")
                    
                    logger.info(f"Completed background metrics update for influencer {username}")
                else:
                    logger.info("No influencers found to update")
                    
            except Exception as e:
                logger.error(f"Error in background metrics update: {str(e)}")
        
        # Start background thread for metrics update
        metrics_thread = threading.Thread(target=update_metrics_in_background)
        metrics_thread.daemon = True  # Thread will exit when main thread exits
        metrics_thread.start()
        logger.info("Started background metrics update thread")
        
    except Exception as e:
        logger.error(f"Error starting background metrics update: {str(e)}")
        # Don't block token refresh if update setup fails
    
    return jsonify({
        "access_token": access_token
    })


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    user_id = int(get_jwt_identity())
    
    # Find user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get user's organizations
    organizations = []
    if hasattr(user, 'organizations'):
        organizations = [{
            "id": org.id,
            "name": org.name,
            "plan": org.plan.name if hasattr(org, 'plan') and org.plan else None
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
    session.clear()  # Clear any previous session data to avoid conflicts
    session['oauth_state'] = str(uuid.uuid4())
    
    # Check if this is a login/register request or just a connection request
    action = request.args.get('action', 'connect')
    session['oauth_action'] = action
    logger.info(f"Starting Facebook OAuth flow with action: {action}")
    
    # Handle user_id for connection
    if action == 'connect' and 'user_id' in request.args:
        user_id = request.args.get('user_id')
        session['user_id'] = user_id
        logger.info(f"Connecting Facebook to existing user ID: {user_id}")
    elif action == 'login':
        logger.info("User is logging in with Facebook")
    elif action == 'register':
        logger.info("User is registering with Facebook")
    
    # Generate the redirect URI
    redirect_uri = url_for('api.auth.facebook_callback', _external=True)
    logger.info(f"Facebook OAuth redirect URI: {redirect_uri}")
    
    try:
        # Check if Facebook client is registered
        if 'facebook' not in oauth._registry:
            logger.error("Facebook OAuth client is not registered in the OAuth registry")
            available_clients = list(oauth._registry.keys())
            logger.error(f"Available OAuth clients: {available_clients}")
            return jsonify({
                "error": "Facebook OAuth not configured",
                "details": "The Facebook OAuth client is not registered. Check environment variables.",
                "available_clients": available_clients
            }), 500
        
        # Redirect to Facebook for authentication
        return oauth.facebook.authorize_redirect(redirect_uri)
    except Exception as e:
        # Handle any errors
        logger.error(f"Error starting Facebook OAuth flow: {str(e)}")
        return jsonify({
            "error": "Failed to start Facebook authentication",
            "details": str(e)
        }), 500


@bp.route('/facebook/callback')
def facebook_callback():
    """Handle Facebook OAuth callback."""
    try:
        # Check for error parameter from Facebook
        if 'error' in request.args:
            error = request.args.get('error')
            error_description = request.args.get('error_description', 'Unknown error')
            logger.error(f"Facebook OAuth error: {error} - {error_description}")
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
            return redirect(f"{frontend_url}/auth/login?error=facebook_auth_error&message={error_description}")
        
        # Get token from Facebook
        logger.info("Attempting to get Facebook access token...")
        token = oauth.facebook.authorize_access_token()
        if not token:
            logger.error("Failed to get Facebook access token")
            return jsonify({"error": "Failed to get token from Facebook"}), 400
        
        logger.info("Successfully obtained Facebook access token")
        
        # Get user info from Facebook
        logger.info("Fetching user info from Facebook...")
        resp = oauth.facebook.get(
            'https://graph.facebook.com/me?fields=id,name,email,picture'
        )
        facebook_user_info = resp.json()
        logger.info(f"Received Facebook user info: {json.dumps(facebook_user_info)}")
        
        # Check what action we're performing
        action = session.get('oauth_action', 'connect')
        logger.info(f"Performing action: {action}")
        
        if action == 'connect':
            # User is already logged in and connecting Facebook
            user_id = session.get('user_id')
            if not user_id:
                logger.error("No user ID found in session for 'connect' action")
                return jsonify({"error": "No user ID in session"}), 400
            
            # Save token to the user's account
            save_token(user_id, 'facebook', token)
            logger.info(f"Facebook account connected to user {user_id}")
            
            # Update user with Facebook username and ID if available
            user = User.query.get(user_id)
            if user:
                update_needed = False
                facebook_id = facebook_user_info.get('id')
                if facebook_id and not user.facebook_id:
                    user.facebook_id = facebook_id
                    update_needed = True
                
                facebook_username = facebook_user_info.get('name')
                if facebook_username and not user.facebook_username:
                    user.facebook_username = facebook_username
                    update_needed = True
                
                if update_needed:
                    db.session.commit()
                    logger.info(f"Updated user {user_id} with Facebook data: ID={facebook_id}, username={facebook_username}")
            
            # Try to fetch full profile with the Apify service
            try:
                from app.services.social_media_service import SocialMediaService
                if facebook_username:
                    profile_data = SocialMediaService.fetch_facebook_profile(user_id, facebook_username)
                    if profile_data and 'error' not in profile_data:
                        SocialMediaService.save_influencer_data(profile_data)
                        logger.info(f"Successfully fetched and saved Facebook profile data for user {user_id}")
            except Exception as e:
                logger.error(f"Error fetching Facebook profile data: {str(e)}")
            
            # Redirect to frontend with success message
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
            return redirect(f"{frontend_url}/settings/connected-accounts?status=success&platform=facebook")
        
        elif action == 'login' or action == 'register':
            # User is logging in or registering with Facebook
            email = facebook_user_info.get('email')
            facebook_id = facebook_user_info.get('id')
            logger.info(f"Facebook ID: {facebook_id}, Email: {email}")
            
            # First, try to find a user with this Facebook ID
            user_by_fb_id = User.query.filter_by(facebook_id=facebook_id).first()
            if user_by_fb_id:
                logger.info(f"Found existing user with Facebook ID: {user_by_fb_id.id}")
                user = user_by_fb_id
                # Update the email if it's provided and different
                if email and email != user.email:
                    logger.info(f"Updating user email from {user.email} to {email}")
                    user.email = email
                    db.session.commit()
            
            # If user not found by Facebook ID, check by email (if available)
            elif email:
                user = User.query.filter_by(email=email).first()
                if user:
                    logger.info(f"Found existing user by email: {user.id}")
                    # Update the Facebook ID and username if not set
                    update_needed = False
                    if not user.facebook_id:
                        logger.info(f"Updating user {user.id} with Facebook ID: {facebook_id}")
                        user.facebook_id = facebook_id
                        update_needed = True
                    
                    # Store Facebook username if available
                    facebook_username = facebook_user_info.get('name')
                    if facebook_username and not user.facebook_username:
                        user.facebook_username = facebook_username
                        logger.info(f"Updating user {user.id} with Facebook username: {facebook_username}")
                        update_needed = True
                    
                    if update_needed:
                        db.session.commit()
                else:
                    logger.info(f"No user found with email: {email}")
                    user = None
            else:
                # No Facebook ID match and no email provided
                logger.info("No email provided by Facebook and no user found by Facebook ID")
                user = None
                
                # Handle missing email
                if action == 'register':
                    # For registration without email, save token temporarily in session
                    session['temp_facebook_token'] = json.dumps(token)
                    session['facebook_id'] = facebook_id
                    
                    # Get profile picture and name if available
                    profile_pic = ""
                    name = ""
                    if 'picture' in facebook_user_info and 'data' in facebook_user_info['picture']:
                        profile_pic = facebook_user_info['picture']['data'].get('url', '')
                    if 'name' in facebook_user_info:
                        name = facebook_user_info['name']
                    
                    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
                    logger.info(f"Redirecting to complete profile form for registration with missing email")
                    return redirect(f"{frontend_url}/auth/complete-profile?facebook_id={facebook_id}&missing=email&name={name}&profile_pic={profile_pic}")
                else:
                    # For login without email, return an error
                    logger.error("Login attempt with Facebook account that doesn't have an email")
                    return jsonify({
                        "error": "Could not retrieve email from Facebook",
                        "message": "Your Facebook account doesn't provide an email address. Please try logging in with your email and password."
                    }), 400
            
            # Create new user for registration if none exists
            if not user and action == 'register' and email:
                logger.info(f"Creating new user for registration with email: {email}")
                # Create new user with Facebook data
                username = facebook_user_info.get('name', '').replace(' ', '_').lower() 
                
                # Check if username exists and append a number if it does
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Get profile picture from Facebook data
                profile_image = None
                if 'picture' in facebook_user_info and 'data' in facebook_user_info['picture']:
                    profile_image = facebook_user_info['picture']['data'].get('url')
                
                user = User(
                    username=username,
                    email=email,
                    facebook_id=facebook_id,
                    profile_image=profile_image
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
                
                logger.info(f"Created new user from Facebook: {user.id} - {user.username}")
            
            # Handle login case but no user found
            if action == 'login' and not user:
                # User tried to login with Facebook but doesn't have an account
                logger.info("Login attempt with Facebook, but no matching user found. Redirecting to signup.")
                frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
                return redirect(f"{frontend_url}/auth/signup?error=no_account&facebook=true")
            
            # At this point, we should have a valid user
            if user:
                # Save/update Facebook token
                save_token(user.id, 'facebook', token)
                logger.info(f"Saved Facebook token for user {user.id}")
                
                # Generate tokens for the user
                tokens = generate_tokens(user.id)
                logger.info(f"Generated auth tokens for user {user.id}")
                
                # Redirect to frontend with tokens
                frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
                token_param = f"access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}&user_id={user.id}"
                
                if action == 'register':
                    logger.info(f"Redirecting new user to welcome page")
                    return redirect(f"{frontend_url}/auth/welcome?{token_param}")
                else:
                    logger.info(f"Redirecting existing user to dashboard")
                    return redirect(f"{frontend_url}/dashboard?{token_param}")
            else:
                # This should not happen, but just in case
                logger.error("Failed to find or create user during Facebook authentication")
                return jsonify({"error": "Authentication failed"}), 500
        
        else:
            logger.error(f"Invalid OAuth action: {action}")
            return jsonify({"error": "Invalid action"}), 400
    
    except Exception as e:
        import traceback
        logger.error(f"Facebook callback error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Try to provide a more user-friendly error
        error_message = str(e)
        if "No such client: facebook" in error_message:
            error_message = "Facebook OAuth client is not configured"
        
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
        return redirect(f"{frontend_url}/auth/login?error=facebook_auth_error&message={error_message}")


# Instagram OAuth routes
@bp.route('/instagram')
@jwt_required()
def instagram_auth():
    """Initiate Instagram OAuth flow."""
    user_id = int(get_jwt_identity())
    logger.info(f"Starting Instagram OAuth flow for user {user_id}")
    
    # Clear any previous session data and store user ID
    session.clear()
    session['user_id'] = user_id
    session['oauth_state'] = str(uuid.uuid4())
    
    # Generate the redirect URI
    redirect_uri = url_for('api.auth.instagram_callback', _external=True)
    logger.info(f"Instagram OAuth redirect URI: {redirect_uri}")
    
    try:
        # Check if Instagram client is registered
        if 'instagram' not in oauth._registry:
            logger.error("Instagram OAuth client is not registered in the OAuth registry")
            available_clients = list(oauth._registry.keys())
            logger.error(f"Available OAuth clients: {available_clients}")
            return jsonify({
                "error": "Instagram OAuth not configured",
                "details": "The Instagram OAuth client is not registered. Check environment variables.",
                "available_clients": available_clients
            }), 500
        
        # Redirect to Facebook for Instagram authentication
        return oauth.instagram.authorize_redirect(redirect_uri)
    except Exception as e:
        # Handle any errors
        logger.error(f"Error starting Instagram OAuth flow: {str(e)}")
        return jsonify({
            "error": "Failed to start Instagram authentication",
            "details": str(e)
        }), 500


@bp.route('/instagram/callback')
def instagram_callback():
    """Handle Instagram OAuth callback."""
    try:
        # Check for error parameter from Facebook
        if 'error' in request.args:
            error = request.args.get('error')
            error_description = request.args.get('error_description', 'Unknown error')
            logger.error(f"Instagram OAuth error: {error} - {error_description}")
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
            return redirect(f"{frontend_url}/settings/connected-accounts?error=instagram_auth_error&message={error_description}")
        
        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
            logger.error("No user ID found in session for Instagram callback")
            return jsonify({"error": "Invalid session. Please try again."}), 401
        
        # Get token from Instagram/Facebook
        logger.info("Attempting to get Instagram access token...")
        token = oauth.instagram.authorize_access_token()
        if not token:
            logger.error("Failed to get Instagram access token")
            return jsonify({"error": "Failed to get Instagram access token"}), 400
        
        logger.info(f"Successfully obtained Instagram access token")
        
        # Save token to database
        save_token(user_id, 'instagram', token)
        logger.info(f"Saved Instagram token for user {user_id}")
        
        # Check if the account is a business/creator account
        try:
            # Get Instagram account information to verify it's a business account
            from app.services.social_media_service import SocialMediaService
            profile_data = SocialMediaService.fetch_instagram_profile(user_id)
            
            if profile_data:
                logger.info(f"Successfully retrieved Instagram profile for user {user_id}: {profile_data['username']}")
                
                # Store profile data for immediate access
                SocialMediaService.save_influencer_data(profile_data)
                logger.info(f"Saved Instagram profile data for user {user_id}")
                
                # Update user with Instagram username
                if 'username' in profile_data:
                    user = User.query.get(user_id)
                    if user:
                        user.instagram_username = profile_data['username']
                        db.session.commit()
                        logger.info(f"Updated user {user_id} with Instagram username: {profile_data['username']}")
            else:
                logger.warning(f"Could not verify Instagram business account status for user {user_id}")
                # We continue anyway since the token was obtained
        except Exception as e:
            logger.error(f"Error checking Instagram account type: {str(e)}")
            # Continue despite error, as we have the access token
        
        # Redirect to frontend with success message
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
        return redirect(f"{frontend_url}/settings/connected-accounts?status=success&platform=instagram")
        
    except Exception as e:
        import traceback
        logger.error(f"Instagram callback error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Try to provide a more user-friendly error
        error_message = str(e)
        if "No such client: instagram" in error_message:
            error_message = "Instagram OAuth client is not configured"
        
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
        return redirect(f"{frontend_url}/settings/connected-accounts?error=instagram_auth_error&message={error_message}")


# Complete profile after social login
@bp.route('/complete-profile', methods=['POST'])
def complete_profile():
    """Complete user registration when required fields are missing from social login."""
    try:
        data = request.json
        logger.info(f"Completing profile with data: {json.dumps(data)}")
        
        # Check required fields
        if not all(k in data for k in ('facebook_id', 'email')):
            logger.error(f"Missing required fields in complete-profile request")
            return jsonify({"error": "Missing required fields", "required": ["facebook_id", "email"]}), 400
        
        facebook_id = data['facebook_id']
        email = data['email']
        name = data.get('name', '')
        profile_image = data.get('profile_image', '')
        
        # Validate email format
        if '@' not in email or '.' not in email:
            logger.error(f"Invalid email format: {email}")
            return jsonify({"error": "Invalid email format"}), 400
        
        # Check if a user with this Facebook ID already exists
        existing_user = User.query.filter_by(facebook_id=facebook_id).first()
        if existing_user:
            logger.info(f"Found existing user with Facebook ID {facebook_id}")
            # Update the email if it's not set
            if not existing_user.email:
                existing_user.email = email
                db.session.commit()
                logger.info(f"Updated existing user {existing_user.id} with email {email}")
            user = existing_user
        else:
            # Check if email already exists
            email_user = User.query.filter_by(email=email).first()
            if email_user:
                logger.error(f"Email {email} already exists for user {email_user.id}")
                return jsonify({
                    "error": "Email already exists",
                    "message": "This email is already associated with an account. Please log in instead."
                }), 409
            
            logger.info(f"Creating new user with Facebook ID {facebook_id} and email {email}")
            # Create username from name or email
            if name:
                base_username = name.replace(' ', '_').lower()
            else:
                base_username = email.split('@')[0].lower()
            
            username = base_username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create new user
            user = User(
                username=username,
                email=email,
                facebook_id=facebook_id,
                profile_image=profile_image
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
            logger.info(f"Created new user: {user.id} - {user.username}")
        
        # Save Facebook token if it exists in session
        temp_facebook_token = session.get('temp_facebook_token')
        if temp_facebook_token:
            try:
                token_data = json.loads(temp_facebook_token)
                save_token(user.id, 'facebook', token_data)
                # Clear the temporary token
                session.pop('temp_facebook_token', None)
                logger.info(f"Saved Facebook token for user {user.id} from temporary session storage")
            except Exception as e:
                logger.error(f"Error saving temporary Facebook token: {str(e)}")
        else:
            # Check if we stored the Facebook ID in the session
            session_facebook_id = session.get('facebook_id')
            if session_facebook_id and session_facebook_id == facebook_id:
                logger.info(f"Found matching Facebook ID in session, but no token")
            else:
                logger.warning(f"No Facebook token found in session and Facebook ID mismatch")
        
        # Generate tokens for the user
        tokens = generate_tokens(user.id)
        logger.info(f"Generated tokens for user {user.id}")
        
        # Return user data and tokens
        return jsonify({
            "message": "Profile completed successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": get_user_roles(user)
            },
            "tokens": tokens
        }), 201
    
    except Exception as e:
        import traceback
        logger.error(f"Error completing profile: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to complete profile", "details": str(e)}), 500

# TikTok OAuth routes
@bp.route('/tiktok')
@jwt_required()
def tiktok_auth():
    """Initiate TikTok OAuth flow."""
    user_id = int(get_jwt_identity())
    
    # Check if TikTok client is registered
    if 'tiktok' not in oauth._registry:
        logger.error("TikTok OAuth client is not registered in the OAuth registry")
        available_clients = list(oauth._registry.keys())
        logger.error(f"Available OAuth clients: {available_clients}")
        return jsonify({
            "error": "TikTok OAuth not configured",
            "details": "The TikTok OAuth client is not registered. Check environment variables.",
            "available_clients": available_clients
        }), 500
    
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
    
    # Check if TikTok client is registered
    if 'tiktok' not in oauth._registry:
        logger.error("TikTok OAuth client is not registered in the OAuth registry")
        return jsonify({
            "error": "TikTok OAuth not configured",
            "details": "The TikTok OAuth client is not registered. Check environment variables."
        }), 500
    
    # Get token from TikTok
    token = oauth.tiktok.authorize_access_token()
    if not token:
        return jsonify({"error": "Failed to get token"}), 400
    
    # Save token to database
    save_token(user_id, 'tiktok', token)
    logger.info(f"Saved TikTok token for user {user_id}")
    
    # Try to get user info from TikTok API
    try:
        # Get basic user info using the token
        user_info_response = oauth.tiktok.get('https://open.tiktokapis.com/v2/user/info/')
        tiktok_user_info = user_info_response.json()
        
        if 'data' in tiktok_user_info and 'user' in tiktok_user_info['data']:
            tiktok_user = tiktok_user_info['data']['user']
            tiktok_username = tiktok_user.get('display_name')
            tiktok_id = tiktok_user.get('open_id')
            
            # Update user with TikTok info
            user = User.query.get(user_id)
            if user:
                update_needed = False
                if tiktok_id and not user.tiktok_id:
                    user.tiktok_id = tiktok_id
                    update_needed = True
                
                if tiktok_username and not user.tiktok_username:
                    user.tiktok_username = tiktok_username
                    update_needed = True
                
                if update_needed:
                    db.session.commit()
                    logger.info(f"Updated user {user_id} with TikTok data: ID={tiktok_id}, username={tiktok_username}")
            
            # Try to fetch full profile with the Apify service
            try:
                from app.services.social_media_service import SocialMediaService
                if tiktok_username:
                    profile_data = SocialMediaService.fetch_tiktok_profile(user_id, tiktok_username)
                    if profile_data and 'error' not in profile_data:
                        SocialMediaService.save_influencer_data(profile_data)
                        logger.info(f"Successfully fetched and saved TikTok profile data for user {user_id}")
            except Exception as e:
                logger.error(f"Error fetching TikTok profile data: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting TikTok user info: {str(e)}")
    
    # Redirect to frontend with success message
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
    return redirect(f"{frontend_url}/settings/connected-accounts?status=success&platform=tiktok")