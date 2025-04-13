from flask import jsonify, request, redirect, url_for, session, current_app, Blueprint
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, create_access_token, create_refresh_token
)
from app import db, jwt
from app.services.security_service import generate_tokens, has_role, get_user_roles
from app.services.oauth_service import oauth, save_token, get_token
from app.services.social_media_service import SocialMediaService
from app.services.analytics_service import AnalyticsService
from app.models import User, Role, Influencer, Organization, Plan, SocialToken, InfluencerMetric, Category
import os
from datetime import datetime, timedelta

# Create blueprint
main = Blueprint('main', __name__)

# Basic routes
@main.route('/')
def index():
    return jsonify({"message": "Welcome to Analisa.ai Social Media API"})

# Authentication routes
@main.route('/api/auth/register', methods=['POST'])
def register():
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

@main.route('/api/auth/login', methods=['POST'])
def login():
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

@main.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    
    # Find user
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Invalid token"}), 401
    
    # Generate new access token
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(hours=1)
    )
    
    return jsonify({
        "access_token": access_token
    })

@main.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
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
@main.route('/api/auth/instagram')
@jwt_required()
def instagram_auth():
    """Initiate Instagram OAuth flow."""
    user_id = get_jwt_identity()
    # Store state for later verification
    session['user_id'] = user_id
    redirect_uri = url_for('main.instagram_callback', _external=True)
    return oauth.instagram.authorize_redirect(redirect_uri)

@main.route('/api/auth/instagram/callback')
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

@main.route('/api/auth/facebook')
@jwt_required()
def facebook_auth():
    """Initiate Facebook OAuth flow."""
    user_id = get_jwt_identity()
    # Store state for later verification
    session['user_id'] = user_id
    redirect_uri = url_for('main.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@main.route('/api/auth/facebook/callback')
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

@main.route('/api/auth/tiktok')
@jwt_required()
def tiktok_auth():
    """Initiate TikTok OAuth flow."""
    user_id = get_jwt_identity()
    # Store state for later verification
    session['user_id'] = user_id
    redirect_uri = url_for('main.tiktok_callback', _external=True)
    return oauth.tiktok.authorize_redirect(redirect_uri)

@main.route('/api/auth/tiktok/callback')
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

# Protected routes that require authentication
@main.route('/api/users/me/connected-accounts', methods=['GET'])
@jwt_required()
def get_connected_accounts():
    """Get all connected social media accounts for the current user."""
    user_id = get_jwt_identity()
    
    # Query all tokens for this user
    tokens = db.session.query(SocialToken.platform, SocialToken.updated_at).filter_by(user_id=user_id).all()
    
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

# Influencer routes
@main.route('/api/influencers', methods=['GET'])
@jwt_required()
def get_influencers():
    """Get all influencers with pagination."""
    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    platform = request.args.get('platform')
    
    # Build query
    query = Influencer.query
    
    # Apply filters
    if platform:
        query = query.filter_by(platform=platform)
    
    # Get paginated results
    influencers = query.order_by(Influencer.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Format response
    return jsonify({
        "influencers": [
            {
                "id": i.id,
                "username": i.username,
                "full_name": i.full_name,
                "platform": i.platform,
                "followers_count": i.followers_count,
                "engagement_rate": i.engagement_rate,
                "social_score": i.social_score,
                "profile_image": i.profile_image
            }
            for i in influencers.items
        ],
        "meta": {
            "page": influencers.page,
            "per_page": influencers.per_page,
            "total": influencers.total,
            "pages": influencers.pages
        }
    })

@main.route('/api/influencers/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_influencer(influencer_id):
    """Get detailed information about a specific influencer."""
    influencer = Influencer.query.get(influencer_id)
    
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404
    
    # Get latest metrics
    latest_metrics = influencer.metrics.order_by(InfluencerMetric.date.desc()).first()
    
    # Format categories
    categories = [{"id": c.id, "name": c.name} for c in influencer.categories]
    
    return jsonify({
        "influencer": {
            "id": influencer.id,
            "username": influencer.username,
            "full_name": influencer.full_name,
            "platform": influencer.platform,
            "profile_url": influencer.profile_url,
            "profile_image": influencer.profile_image,
            "bio": influencer.bio,
            "followers_count": influencer.followers_count,
            "following_count": influencer.following_count,
            "posts_count": influencer.posts_count,
            "engagement_rate": influencer.engagement_rate,
            "social_score": influencer.social_score,
            "categories": categories,
            "latest_metrics": {
                "date": latest_metrics.date.isoformat() if latest_metrics else None,
                "followers": latest_metrics.followers if latest_metrics else None,
                "engagement": latest_metrics.engagement if latest_metrics else None,
                "posts": latest_metrics.posts if latest_metrics else None,
                "likes": latest_metrics.likes if latest_metrics else None,
                "comments": latest_metrics.comments if latest_metrics else None,
                "shares": latest_metrics.shares if latest_metrics else None,
                "views": latest_metrics.views if latest_metrics else None
            } if latest_metrics else None
        }
    })

# Analytics routes
@main.route('/api/analytics/influencer/<int:influencer_id>/growth', methods=['GET'])
@jwt_required()
def get_influencer_growth(influencer_id):
    """Get growth metrics for an influencer."""
    # Parse time range from query parameters (default to 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get growth metrics
    growth_data = AnalyticsService.get_influencer_growth(influencer_id, time_range)
    
    if not growth_data:
        return jsonify({"error": "Failed to calculate growth metrics"}), 400
    
    return jsonify({
        "growth": growth_data
    })

@main.route('/api/analytics/benchmarks', methods=['GET'])
@jwt_required()
def get_benchmarks():
    """Get benchmark metrics for a platform and optional category."""
    # Parse parameters
    platform = request.args.get('platform', 'instagram')
    category = request.args.get('category')
    
    # Get benchmark data
    benchmark_data = AnalyticsService.get_platform_benchmarks(platform, category)
    
    if not benchmark_data:
        return jsonify({"error": "Failed to calculate benchmarks"}), 400
    
    return jsonify({
        "benchmarks": benchmark_data
    })

@main.route('/api/analytics/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get influencer recommendations based on filters."""
    user_id = get_jwt_identity()
    
    # Parse filters from query parameters
    filters = {}
    if 'platform' in request.args:
        filters['platform'] = request.args.get('platform')
    if 'category' in request.args:
        filters['category'] = request.args.get('category')
    if 'min_followers' in request.args:
        filters['min_followers'] = int(request.args.get('min_followers'))
    if 'min_engagement' in request.args:
        filters['min_engagement'] = float(request.args.get('min_engagement'))
    
    # Get recommendations
    recommendations = AnalyticsService.get_influencer_recommendations(user_id, filters)
    
    return jsonify({
        "recommendations": recommendations
    })

# Search and discovery routes
@main.route('/api/search/influencers', methods=['GET'])
@jwt_required()
def search_influencers():
    """Search for influencers with various filters."""
    # Parse query parameters
    query = request.args.get('q', '')
    platform = request.args.get('platform')
    category = request.args.get('category')
    min_followers = request.args.get('min_followers', type=int)
    max_followers = request.args.get('max_followers', type=int)
    min_engagement = request.args.get('min_engagement', type=float)
    sort_by = request.args.get('sort_by', 'followers')
    sort_order = request.args.get('sort_order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    influencer_query = Influencer.query
    
    # Apply text search
    if query:
        influencer_query = influencer_query.filter(
            (Influencer.username.ilike(f'%{query}%')) |
            (Influencer.full_name.ilike(f'%{query}%')) |
            (Influencer.bio.ilike(f'%{query}%'))
        )
    
    # Apply filters
    if platform:
        influencer_query = influencer_query.filter_by(platform=platform)
    
    if category:
        influencer_query = influencer_query.join(Influencer.categories).filter(Category.name == category)
    
    if min_followers:
        influencer_query = influencer_query.filter(Influencer.followers_count >= min_followers)
    
    if max_followers:
        influencer_query = influencer_query.filter(Influencer.followers_count <= max_followers)
    
    if min_engagement:
        influencer_query = influencer_query.filter(Influencer.engagement_rate >= min_engagement)
    
    # Apply sorting
    if sort_by == 'followers':
        order_col = Influencer.followers_count
    elif sort_by == 'engagement':
        order_col = Influencer.engagement_rate
    elif sort_by == 'score':
        order_col = Influencer.social_score
    else:
        order_col = Influencer.followers_count
    
    if sort_order == 'asc':
        influencer_query = influencer_query.order_by(order_col.asc())
    else:
        influencer_query = influencer_query.order_by(order_col.desc())
    
    # Paginate results
    influencers = influencer_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Format response
    return jsonify({
        "influencers": [
            {
                "id": i.id,
                "username": i.username,
                "full_name": i.full_name,
                "platform": i.platform,
                "followers_count": i.followers_count,
                "engagement_rate": i.engagement_rate,
                "social_score": i.social_score,
                "profile_image": i.profile_image
            }
            for i in influencers.items
        ],
        "meta": {
            "page": influencers.page,
            "per_page": influencers.per_page,
            "total": influencers.total,
            "pages": influencers.pages
        }
    })

@main.route('/api/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all influencer categories."""
    categories = Category.query.all()
    
    return jsonify({
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description
            }
            for c in categories
        ]
    })

@main.route('/api/influencers/lookup', methods=['POST'])
@jwt_required()
def lookup_influencer():
    """Look up an influencer by username and platform, fetch latest data."""
    user_id = get_jwt_identity()
    data = request.json
    
    # Validate required fields
    if not all(k in data for k in ('username', 'platform')):
        return jsonify({"error": "Missing required fields"}), 400
    
    username = data['username']
    platform = data['platform'].lower()
    
    # Check if we have a valid token for this platform
    token = get_token(user_id, platform)
    if not token:
        return jsonify({
            "error": f"No {platform} account connected",
            "connect_url": f"/api/auth/{platform}"
        }), 400
    
    # Fetch profile data from the appropriate platform
    profile_data = None
    if platform == 'instagram':
        profile_data = SocialMediaService.fetch_instagram_profile(user_id, username)
    elif platform == 'tiktok':
        profile_data = SocialMediaService.fetch_tiktok_profile(user_id, username)
    else:
        return jsonify({"error": f"Unsupported platform: {platform}"}), 400
    
    if not profile_data:
        return jsonify({"error": f"Failed to fetch {platform} profile for {username}"}), 400
    
    # Save influencer data to database
    influencer = SocialMediaService.save_influencer_data(profile_data)
    
    if not influencer:
        return jsonify({"error": "Failed to save influencer data"}), 500
    
    # Format response
    categories = [{"id": c.id, "name": c.name} for c in influencer.categories]
    
    return jsonify({
        "influencer": {
            "id": influencer.id,
            "username": influencer.username,
            "full_name": influencer.full_name,
            "platform": influencer.platform,
            "profile_url": influencer.profile_url,
            "profile_image": influencer.profile_image,
            "bio": influencer.bio,
            "followers_count": influencer.followers_count,
            "engagement_rate": influencer.engagement_rate,
            "social_score": influencer.social_score,
            "categories": categories
        }
    })

# Error handlers - These will be registered in the app context
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401 