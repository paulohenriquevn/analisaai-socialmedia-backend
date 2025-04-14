"""
Routes for relevance score metrics.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta

from app.models.influencer import Influencer
from app.models.score import InfluencerScore
from app.services.score_service import ScoreService

# Create blueprint
bp = Blueprint('score', __name__)

logger = logging.getLogger(__name__)

@bp.route('/metrics/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_score_metrics(influencer_id):
    """
    Get relevance score metrics for a specific influencer.
    
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
    metrics = ScoreService.get_score_metrics(influencer_id, start_date, end_date)
    
    # Format response
    result = []
    for metric in metrics:
        result.append({
            "date": metric.date.isoformat() if metric.date else None,
            "overall_score": metric.overall_score,
            "engagement_score": metric.engagement_score,
            "reach_score": metric.reach_score,
            "growth_score": metric.growth_score,
            "consistency_score": metric.consistency_score,
            "audience_quality_score": metric.audience_quality_score,
            "engagement_weight": metric.engagement_weight,
            "reach_weight": metric.reach_weight,
            "growth_weight": metric.growth_weight,
            "consistency_weight": metric.consistency_weight,
            "audience_quality_weight": metric.audience_quality_weight
        })
    
    return jsonify({
        "status": "success",
        "influencer": {
            "id": influencer.id,
            "username": influencer.username,
            "platform": influencer.platform,
            "relevance_score": influencer.relevance_score
        },
        "metrics": result
    })

@bp.route('/calculate/<int:influencer_id>', methods=['POST'])
@jwt_required()
def calculate_score(influencer_id):
    """Calculate and save relevance score for an influencer."""
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
    metrics = ScoreService.calculate_relevance_score(influencer_id)
    
    if not metrics:
        return jsonify({
            "status": "error",
            "message": "Failed to calculate relevance score"
        }), 500
    
    # Format date for response
    if 'date' in metrics and hasattr(metrics['date'], 'isoformat'):
        metrics['date'] = metrics['date'].isoformat()
    
    return jsonify({
        "status": "success",
        "message": "Relevance score calculated successfully",
        "score": {
            "overall_score": metrics['overall_score'],
            "engagement_score": metrics['engagement_score'],
            "reach_score": metrics['reach_score'],
            "growth_score": metrics['growth_score'],
            "consistency_score": metrics['consistency_score'],
            "audience_quality_score": metrics['audience_quality_score']
        },
        "current_relevance_score": influencer.relevance_score
    })

@bp.route('/calculate-all', methods=['POST'])
@jwt_required()
def calculate_all_scores():
    """Calculate relevance scores for all influencers."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Calculate metrics for all influencers
    results = ScoreService.calculate_all_influencers_scores()
    
    return jsonify({
        "status": "success",
        "message": f"Relevance score calculation completed: {results['success']} succeeded, {results['failed']} failed",
        "results": results
    })

@bp.route('/compare', methods=['GET'])
@jwt_required()
def compare_scores():
    """
    Compare relevance scores of multiple influencers.
    
    Required query parameters:
    - influencer_ids: Comma-separated list of influencer IDs to compare
    """
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Get influencer IDs from request
    influencer_ids_param = request.args.get('influencer_ids')
    if not influencer_ids_param:
        return jsonify({
            "status": "error",
            "message": "Missing required parameter: influencer_ids"
        }), 400
    
    # Parse influencer IDs
    try:
        influencer_ids = [int(id_str) for id_str in influencer_ids_param.split(',')]
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid influencer_ids format. Must be comma-separated integers."
        }), 400
    
    # Get influencers with their scores
    influencers = Influencer.query.filter(Influencer.id.in_(influencer_ids)).all()
    
    # Format response
    result = []
    for influencer in influencers:
        # Get most recent score metrics (returns already ordered by date descending)
        score_metrics = ScoreService.get_score_metrics(influencer.id)
        # Take only the most recent entry if available
        if score_metrics:
            score_metrics = score_metrics[:1]
        score_details = None
        
        if score_metrics:
            metric = score_metrics[0]
            score_details = {
                "overall_score": metric.overall_score,
                "engagement_score": metric.engagement_score,
                "reach_score": metric.reach_score,
                "growth_score": metric.growth_score,
                "consistency_score": metric.consistency_score,
                "audience_quality_score": metric.audience_quality_score,
                "last_calculated": metric.date.isoformat() if metric.date else None
            }
        
        result.append({
            "id": influencer.id,
            "username": influencer.username,
            "platform": influencer.platform,
            "relevance_score": influencer.relevance_score,
            "score_details": score_details
        })
    
    # Sort by overall score (highest first)
    result.sort(key=lambda x: x['relevance_score'] if x['relevance_score'] is not None else 0, reverse=True)
    
    return jsonify({
        "status": "success",
        "comparison": result
    })