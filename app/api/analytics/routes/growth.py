"""
Routes for growth metrics.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta

from app.models import SocialPage, SocialPageGrowth
from app.services.growth_service import GrowthService

# Create blueprint
bp = Blueprint('growth', __name__)

logger = logging.getLogger(__name__)

@bp.route('/metrics/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_growth_metrics(social_page_id):
    """
    Get growth metrics for a specific social_page.
    
    Optional query parameters:
    - start_date: Filter metrics after this date (YYYY-MM-DD)
    - end_date: Filter metrics before this date (YYYY-MM-DD)
    - period: Predefined period (last_week, last_month, last_3_months, last_year)
    """
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if social_page exists
    social_page = SocialPage.query.get(social_page_id)
    if not social_page:
        return jsonify({
            "status": "error",
            "message": f"social_page with ID {social_page_id} not found"
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
    metrics = GrowthService.get_growth_metrics(social_page_id, start_date, end_date)
    
    # Format response
    result = []
    for metric in metrics:
        result.append({
            "date": metric.date.isoformat() if metric.date else None,
            "followers_count": metric.followers_count,
            "new_followers_daily": metric.new_followers_daily,
            "new_followers_weekly": metric.new_followers_weekly,
            "new_followers_monthly": metric.new_followers_monthly,
            "retention_rate": metric.retention_rate,
            "churn_rate": metric.churn_rate,
            "daily_growth_rate": metric.daily_growth_rate,
            "weekly_growth_rate": metric.weekly_growth_rate,
            "monthly_growth_rate": metric.monthly_growth_rate,
            "growth_velocity": metric.growth_velocity,
            "growth_acceleration": metric.growth_acceleration,
            "projected_followers_30d": metric.projected_followers_30d,
            "projected_followers_90d": metric.projected_followers_90d
        })
    
    return jsonify({
        "status": "success",
        "social_page": {
            "id": social_page.id,
            "username": social_page.username,
            "platform": social_page.platform,
            "followers_count": social_page.followers_count
        },
        "metrics": result
    })

@bp.route('/calculate/<int:social_page_id>', methods=['POST'])
@jwt_required()
def calculate_growth(social_page_id):
    """Calculate and save growth metrics for an social_page."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if social_page exists
    social_page = SocialPage.query.get(social_page_id)
    if not social_page:
        return jsonify({
            "status": "error",
            "message": f"social_page with ID {social_page_id} not found"
        }), 404
    
    # Calculate metrics
    metrics = GrowthService.calculate_growth_metrics(social_page_id)
    
    if not metrics:
        return jsonify({
            "status": "error",
            "message": "Failed to calculate growth metrics"
        }), 500
    
    # Format date for response
    if 'date' in metrics and hasattr(metrics['date'], 'isoformat'):
        metrics['date'] = metrics['date'].isoformat()
    
    return jsonify({
        "status": "success",
        "message": "Growth metrics calculated successfully",
        "metrics": metrics
    })

@bp.route('/calculate-all', methods=['POST'])
@jwt_required()
def calculate_all_growth():
    """Calculate growth metrics for all social_page."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Calculate metrics for all social_page
    results = GrowthService.calculate_all_social_pages_growth()
    
    return jsonify({
        "status": "success",
        "message": f"Growth metrics calculation completed: {results['success']} succeeded, {results['failed']} failed",
        "results": results
    })