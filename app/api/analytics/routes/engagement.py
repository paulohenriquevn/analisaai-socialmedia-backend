"""
Routes for engagement metrics.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta

from app.models import SocialPage,  SocialPageEngagement
from app.services.engagement_service import EngagementService

# Create blueprint
bp = Blueprint('engagement', __name__)

logger = logging.getLogger(__name__)

@bp.route('/metrics/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_engagement_metrics(social_page_id):
    """
    Get engagement metrics for a specific influencer.
    
    Optional query parameters:
    - start_date: Filter metrics after this date (YYYY-MM-DD)
    - end_date: Filter metrics before this date (YYYY-MM-DD)
    - period: Predefined period (last_week, last_month, last_3_months, last_year)
    """
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if influencer exists
    influencer = SocialPage.query.get(social_page_id)
    if not influencer:
        return jsonify({
            "status": "error",
            "message": f"Influencer with ID {social_page_id} not found"
        }), 404
    
    # Parse date parameters
    start_date = None
    end_date = None
    
    # If period is specified, calculate date range
    period = request.args.get('period')
    if period:
        today = datetime.now().date()
        
        if period == 'last_week':
            start_date = today - timedelta(days=7)
        elif period == 'last_month':
            start_date = today - timedelta(days=30)
        elif period == 'last_3_months':
            start_date = today - timedelta(days=90)
        elif period == 'last_year':
            start_date = today - timedelta(days=365)
    else:
        # Parse custom date range
        if 'start_date' in request.args:
            try:
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid start_date format. Use YYYY-MM-DD"
                }), 400
                
        if 'end_date' in request.args:
            try:
                end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid end_date format. Use YYYY-MM-DD"
                }), 400
    
    # Get metrics from database
    metrics = EngagementService.get_engagement_metrics(social_page_id, start_date, end_date)
    
    # Format response
    result = []
    for metric in metrics:
        result.append({
            "date": metric.date.isoformat() if metric.date else None,
            "engagement_rate": metric.engagement_rate,
            "posts_count": metric.posts_count,
            "avg_likes_per_post": metric.avg_likes_per_post,
            "avg_comments_per_post": metric.avg_comments_per_post,
            "avg_shares_per_post": metric.avg_shares_per_post,
            "total_likes": metric.total_likes,
            "total_comments": metric.total_comments,
            "total_shares": metric.total_shares,
            "growth_rate": metric.growth_rate
        })
    
    return jsonify({
        "status": "success",
        "influencer": {
            "id": influencer.id,
            "username": influencer.username,
            "platform": influencer.platform
        },
        "metrics": result
    })

@bp.route('/calculate/<int:social_page_id>', methods=['POST'])
@jwt_required()
def calculate_engagement(social_page_id):
    """Calculate and save engagement metrics for an influencer."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if influencer exists
    influencer = SocialPage.query.get(social_page_id)
    if not influencer:
        return jsonify({
            "status": "error",
            "message": f"Influencer with ID {social_page_id} not found"
        }), 404
    
    # Calculate metrics
    metrics = EngagementService.calculate_engagement_metrics(social_page_id)
    
    if not metrics:
        return jsonify({
            "status": "error",
            "message": "Failed to calculate engagement metrics"
        }), 500
    
    return jsonify({
        "status": "success",
        "message": "Engagement metrics calculated successfully",
        "metrics": {
            "social_page_id": social_page_id,
            "date": metrics['date'].isoformat() if isinstance(metrics['date'], datetime) else metrics['date'],
            "engagement_rate": metrics['engagement_rate'],
            "posts_count": metrics['posts_count'],
            "avg_likes_per_post": metrics['avg_likes_per_post'],
            "avg_comments_per_post": metrics['avg_comments_per_post'],
            "avg_shares_per_post": metrics['avg_shares_per_post'],
            "total_likes": metrics['total_likes'],
            "total_comments": metrics['total_comments'],
            "total_shares": metrics['total_shares'],
            "growth_rate": metrics['growth_rate']
        }
    })

@bp.route('/calculate-all', methods=['POST'])
@jwt_required()
def calculate_all_engagement():
    """Calculate engagement metrics for all influencers."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Calculate metrics for all influencers
    results = EngagementService.calculate_all_influencers_metrics()
    
    return jsonify({
        "status": "success",
        "message": f"Engagement metrics calculation completed: {results['success']} succeeded, {results['failed']} failed",
        "results": results
    })