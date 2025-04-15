"""
Search-related routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import SocialPage, SocialPageCategory

# Create blueprint
bp = Blueprint('search', __name__)

@bp.route('/social_pages', methods=['GET'])
@jwt_required()
def search_social_pages():
    """Search for social_pages with various filters."""
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
    social_page_query = SocialPage.query
    
    # Apply text search
    if query:
        social_page_query = social_page_query.filter(
            (SocialPage.username.ilike(f'%{query}%')) |
            (SocialPage.full_name.ilike(f'%{query}%')) |
            (SocialPage.bio.ilike(f'%{query}%'))
        )
    
    # Apply filters
    if platform:
        social_page_query = social_page_query.filter_by(platform=platform)
    
    if category:
        social_page_query = social_page_query.join(SocialPage.categories).filter(Category.name == category)
    
    if min_followers:
        social_page_query = social_page_query.filter(SocialPage.followers_count >= min_followers)
    
    if max_followers:
        social_page_query = social_page_query.filter(SocialPage.followers_count <= max_followers)
    
    if min_engagement:
        social_page_query = social_page_query.filter(SocialPage.engagement_rate >= min_engagement)
    
    # Apply sorting
    if sort_by == 'followers':
        order_col = SocialPage.followers_count
    elif sort_by == 'engagement':
        order_col = SocialPage.engagement_rate
    elif sort_by == 'score':
        order_col = SocialPage.social_score
    else:
        order_col = SocialPage.followers_count
    
    if sort_order == 'asc':
        social_page_query = social_page_query.order_by(order_col.asc())
    else:
        social_page_query = social_page_query.order_by(order_col.desc())
    
    # Paginate results
    social_pages = social_page_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Format response
    return jsonify({
        "social_pages": [
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
            for i in social_pages.items
        ],
        "meta": {
            "page": social_pages.page,
            "per_page": social_pages.per_page,
            "total": social_pages.total,
            "pages": social_pages.pages
        }
    })


@bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all social_pages categories."""
    categories = SocialPageCategory.query.all()
    
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