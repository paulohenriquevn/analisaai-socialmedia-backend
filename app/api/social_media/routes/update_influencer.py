"""Routes for updating influencer data."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging

from app.extensions import db
from app.models.influencer import Influencer, Category
from app.api.social_media import bp

logger = logging.getLogger(__name__)

@bp.route('/influencer/<int:influencer_id>', methods=['PUT'])
@jwt_required()
def update_influencer(influencer_id):
    """Update details for an influencer."""
    user_id = get_jwt_identity()
    
    # Find the influencer
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404
    
    # Validate the data
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update the influencer data
    if 'full_name' in data:
        influencer.full_name = data['full_name']
    
    if 'bio' in data:
        influencer.bio = data['bio']
    
    if 'profile_image' in data:
        influencer.profile_image = data['profile_image']
    
    if 'followers_count' in data:
        influencer.followers_count = data['followers_count']
    
    if 'following_count' in data:
        influencer.following_count = data['following_count']
    
    if 'posts_count' in data:
        influencer.posts_count = data['posts_count']
    
    if 'engagement_rate' in data:
        influencer.engagement_rate = data['engagement_rate']
    
    # Handle categories
    if 'categories' in data and isinstance(data['categories'], list):
        categories = []
        for category_name in data['categories']:
            # Look up or create each category
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name, description=f"Category for {category_name}")
                db.session.add(category)
            categories.append(category)
        influencer.categories = categories
    
    # Save changes
    db.session.commit()
    logger.info(f"Updated influencer {influencer.id} - {influencer.username}")
    
    # Return the updated influencer
    return jsonify({
        "message": "Influencer updated successfully",
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
            "categories": [c.name for c in influencer.categories]
        }
    })