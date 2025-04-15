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
    """
    Search for social_pages with various filters.
    ---
    tags:
      - Search
    security:
      - BearerAuth: []
    parameters:
      - name: q
        in: query
        description: "Free text search (username, full_name, bio)"
        required: false
        schema:
          type: string
      - name: platform
        in: query
        description: "Platform to filter (e.g. instagram, tiktok)"
        required: false
        schema:
          type: string
      - name: category
        in: query
        description: "Category to filter"
        required: false
        schema:
          type: string
      - name: min_followers
        in: query
        description: "Minimum number of followers"
        required: false
        schema:
          type: integer
      - name: max_followers
        in: query
        description: "Maximum number of followers"
        required: false
        schema:
          type: integer
      - name: min_engagement
        in: query
        description: "Minimum engagement rate"
        required: false
        schema:
          type: number
      - name: sort_by
        in: query
        description: "Sort by field (followers, engagement, score)"
        required: false
        schema:
          type: string
      - name: sort_order
        in: query
        description: "Sort order (asc or desc)"
        required: false
        schema:
          type: string
      - name: page
        in: query
        description: "Page number"
        required: false
        schema:
          type: integer
      - name: per_page
        in: query
        description: "Results per page"
        required: false
        schema:
          type: integer
    responses:
      200:
        description: "List of social pages and pagination meta"
        content:
          application/json:
            schema:
              type: object
              properties:
                social_pages:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      username:
                        type: string
                      full_name:
                        type: string
                      platform:
                        type: string
                      followers_count:
                        type: integer
                      engagement_rate:
                        type: number
                      social_score:
                        type: number
                      profile_image:
                        type: string
                meta:
                  type: object
                  properties:
                    page:
                      type: integer
                    per_page:
                      type: integer
                    total:
                      type: integer
                    pages:
                      type: integer
      401:
        description: "Not authenticated"
    """
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
    """
    Get all social_pages categories.
    ---
    tags:
      - Search
    security:
      - BearerAuth: []
    responses:
      200:
        description: "List of categories"
        content:
          application/json:
            schema:
              type: object
              properties:
                categories:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      description:
                        type: string
      401:
        description: "Not authenticated"
    """
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