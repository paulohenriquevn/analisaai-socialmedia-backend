"""
social_page-related routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import SocialPage, SocialPageCategory, SocialPageMetric
from app.services.oauth_service import get_token
from app.services.social_media_service import SocialMediaService

# Create blueprint
bp = Blueprint('social_page', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_social_page():
    """Get all social_page with pagination."""
    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    platform = request.args.get('platform')
    user_id = int(get_jwt_identity())
    
    # Build query
    query = SocialPage.query.filter_by(user_id=user_id)
    
    # Get paginated results
    total = query.count()
    social_page = query.order_by(SocialPage.created_at.desc()).limit(per_page).offset((page - 1) * per_page).all()
    
    # Format response
    return jsonify({
        "social_page": [
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
            for i in social_page
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": 0
        }
    })


@bp.route('/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_social_page_by_id(social_page_id):
    """Get detailed information about a specific social_page."""
    social_page = SocialPage.query.get(social_page_id)
    
    if not social_page:
        return jsonify({"error": "social_page not found"}), 404
    
    # Get latest metrics
    latest_metrics = social_page.metrics.order_by(SocialPageMetric.date.desc()).first()
    
    # Format categories
    categories = [{"id": c.id, "name": c.name} for c in social_page.categories]
    
    return jsonify({
        "social_page": {
            "id": social_page.id,
            "username": social_page.username,
            "full_name": social_page.full_name,
            "platform": social_page.platform,
            "profile_url": social_page.profile_url,
            "profile_image": social_page.profile_image,
            "bio": social_page.bio,
            "followers_count": social_page.followers_count,
            "following_count": social_page.following_count,
            "posts_count": social_page.posts_count,
            "engagement_rate": social_page.engagement_rate,
            "social_score": social_page.social_score,
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


@bp.route('/lookup', methods=['POST'])
@jwt_required()
def lookup_social_page():
    """Look up an social_page by username and platform, fetch latest data."""
    user_id = int(get_jwt_identity())
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
    
    # Save social_page data to database with the current user as owner
    social_page = SocialMediaService.save_social_page_data(profile_data, user_id)
    
    if not social_page:
        return jsonify({"error": "Failed to save social_page data"}), 500
    
    # Format response
    categories = [{"id": c.id, "name": c.name} for c in social_page.categories]
    
    return jsonify({
        "social_page": {
            "id": social_page.id,
            "username": social_page.username,
            "full_name": social_page.full_name,
            "platform": social_page.platform,
            "profile_url": social_page.profile_url,
            "profile_image": social_page.profile_image,
            "bio": social_page.bio,
            "followers_count": social_page.followers_count,
            "engagement_rate": social_page.engagement_rate,
            "social_score": social_page.social_score,
            "categories": categories
        }
    })