"""
Analytics-related routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.analytics_service import AnalyticsService

# Create blueprint
bp = Blueprint('analytics', __name__)

@bp.route('/influencer/<int:influencer_id>/growth', methods=['GET'])
@jwt_required()
def get_influencer_growth(influencer_id):
    """Get growth metrics for an influencer."""
    # Parse time range from query parameters (default to 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get growth metrics
    growth_data = AnalyticsService.get_influencer_growth(influencer_id, time_range)
    
    if not growth_data:
        return jsonify({"error": "Failed to calculate growth metrics"}), 400
    
    return jsonify({
        "growth": growth_data
    })


@bp.route('/benchmarks', methods=['GET'])
@jwt_required()
def get_benchmarks():
    """Get benchmark metrics for a platform and optional category."""
    # Parse parameters
    platform = request.args.get('platform', 'instagram')
    category = request.args.get('category')
    
    # Get benchmark data
    benchmark_data = AnalyticsService.get_platform_benchmarks(platform, category)
    
    if not benchmark_data:
        return jsonify({"error": "Failed to calculate benchmarks"}), 400
    
    return jsonify({
        "benchmarks": benchmark_data
    })


@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get influencer recommendations based on filters."""
    user_id = get_jwt_identity()
    
    # Parse filters from query parameters
    filters = {}
    if 'platform' in request.args:
        filters['platform'] = request.args.get('platform')
    if 'category' in request.args:
        filters['category'] = request.args.get('category')
    if 'min_followers' in request.args:
        filters['min_followers'] = int(request.args.get('min_followers'))
    if 'min_engagement' in request.args:
        filters['min_engagement'] = float(request.args.get('min_engagement'))
    
    # Get recommendations
    recommendations = AnalyticsService.get_influencer_recommendations(user_id, filters)
    
    return jsonify({
        "recommendations": recommendations
    })