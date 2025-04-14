"""
Routes for reach metrics.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta, date

from app.models.influencer import Influencer
from app.models.reach import InfluencerReach
from app.services.reach_service import ReachService

# Create blueprint
bp = Blueprint('reach', __name__)

logger = logging.getLogger(__name__)

@bp.route('/metrics/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_reach_metrics(influencer_id):
    """
    Get reach metrics for a specific influencer.
    
    Optional query parameters:
    - start_date: Filter metrics after this date (YYYY-MM-DD)
    - end_date: Filter metrics before this date (YYYY-MM-DD)
    - period: Predefined period (last_week, last_month, last_3_months, last_year)
    """
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if influencer exists
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return jsonify({
            "status": "error",
            "message": f"Influencer with ID {influencer_id} not found"
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
    metrics = ReachService.get_reach_metrics(influencer_id, start_date, end_date)
    
    # Format response
    result = []
    for metric in metrics:
        result.append({
            "date": metric.date.isoformat() if metric.date else None,
            "timestamp": metric.timestamp.isoformat() if metric.timestamp else None,
            "impressions": metric.impressions,
            "reach": metric.reach,
            "story_views": metric.story_views,
            "profile_views": metric.profile_views,
            "stories_count": metric.stories_count,
            "story_engagement_rate": metric.story_engagement_rate,
            "story_exit_rate": metric.story_exit_rate,
            "story_completion_rate": metric.story_completion_rate,
            "avg_watch_time": metric.avg_watch_time,
            "audience_growth": metric.audience_growth
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

@bp.route('/calculate/<int:influencer_id>', methods=['POST'])
@jwt_required()
def calculate_reach(influencer_id):
    """Calculate and save reach metrics for an influencer."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if influencer exists
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return jsonify({
            "status": "error",
            "message": f"Influencer with ID {influencer_id} not found"
        }), 404
    
    # Calculate metrics
    metrics = ReachService.calculate_reach_metrics(influencer_id, current_user_id)
    
    if not metrics:
        return jsonify({
            "status": "error",
            "message": "Failed to calculate reach metrics"
        }), 500
    
    # Format date/datetime for response
    formatted_metrics = {k: v.isoformat() if isinstance(v, (datetime, date)) else v for k, v in metrics.items()}
    
    return jsonify({
        "status": "success",
        "message": "Reach metrics calculated successfully",
        "metrics": formatted_metrics
    })

@bp.route('/calculate-all', methods=['POST'])
@jwt_required()
def calculate_all_reach():
    """Calculate reach metrics for all influencers."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Calculate metrics for all influencers
    results = ReachService.calculate_all_influencers_reach()
    
    return jsonify({
        "status": "success",
        "message": f"Reach metrics calculation completed: {results['success']} succeeded, {results['failed']} failed",
        "results": results
    })