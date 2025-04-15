"""
Influencer-related routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import SocialPage, SocialPageCategory, SocialPageMetric
from app.services.oauth_service import get_token
from app.services.social_media_service import SocialMediaService

# Create blueprint
bp = Blueprint('influencers', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_influencers():
    """Get all influencers with pagination."""
    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    platform = request.args.get('platform')
    user_id = int(get_jwt_identity())
    
    # Build query
    query = SocialPage.query.filter_by(user_id=user_id)
    
    # Get paginated results
    total = query.count()
    influencers = query.order_by(SocialPage.created_at.desc()).limit(per_page).offset((page - 1) * per_page).all()
    
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
            for i in influencers
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": 0
        }
    })


@bp.route('/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_influencer(influencer_id):
    """Get detailed information about a specific influencer."""
    influencer = SocialPage.query.get(influencer_id)
    
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404
    
    # Get latest metrics
    latest_metrics = influencer.metrics.order_by(SocialPageMetric.date.desc()).first()
    
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


@bp.route('/lookup', methods=['POST'])
@jwt_required()
def lookup_influencer():
    """Look up an influencer by username and platform, fetch latest data."""
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