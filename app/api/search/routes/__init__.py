"""
Search-related routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import Influencer, Category

# Create blueprint
bp = Blueprint('search', __name__)

@bp.route('/influencers', methods=['GET'])
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


@bp.route('/categories', methods=['GET'])
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