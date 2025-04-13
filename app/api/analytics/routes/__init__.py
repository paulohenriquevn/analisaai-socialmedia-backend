"""
Analytics-related routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from marshmallow import ValidationError

from app.services.analytics_service import AnalyticsService
from app.api.analytics.schemas import MetricsRequestSchema, DashboardResponseSchema

# Create blueprint
bp = Blueprint('analytics', __name__)

# Import and register sub-routes
from app.api.analytics.routes.sentiment import bp as sentiment_bp
from app.api.analytics.routes.posting_time import bp as posting_time_bp

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


@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get consolidated dashboard metrics for all platforms."""
    user_id = get_jwt_identity()
    
    try:
        # Validate request parameters
        schema = MetricsRequestSchema()
        params = schema.load(request.args)
        
        timeframe = params.get('timeframe', 'month')
        
        # Get consolidated metrics with cache
        metrics = AnalyticsService.get_consolidated_metrics(user_id, timeframe)
        
        # Get platform distribution (cached)
        distribution = AnalyticsService.get_platform_distribution()
        
        # Get category insights (cached)
        insights = AnalyticsService.get_category_insights()
        
        # Validate and serialize response
        response_data = {
            "metrics": metrics,
            "distribution": distribution,
            "insights": insights
        }
        
        response_schema = DashboardResponseSchema()
        validated_data = response_schema.dump(response_data)
        
        return jsonify(validated_data)
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@bp.route('/dashboard/refresh', methods=['POST'])
@jwt_required()
def refresh_dashboard():
    """Force refresh of dashboard metrics."""
    user_id = get_jwt_identity()
    
    try:
        # Validate request parameters
        schema = MetricsRequestSchema()
        params = schema.load(request.args)
        
        timeframe = params.get('timeframe', 'month')
        
        # Get metrics without cache by first invalidating the cache key
        from app.extensions import cache
        
        # Clear multiple caches
        cache.delete_memoized(AnalyticsService.get_consolidated_metrics, user_id, timeframe)
        cache.delete_memoized(AnalyticsService.get_platform_distribution)
        cache.delete_memoized(AnalyticsService.get_category_insights)
        
        # Get fresh metrics
        metrics = AnalyticsService.get_consolidated_metrics(user_id, timeframe)
        distribution = AnalyticsService.get_platform_distribution()
        insights = AnalyticsService.get_category_insights()
        
        # Validate and serialize response
        response_data = {
            "metrics": metrics,
            "distribution": distribution,
            "insights": insights,
            "refreshed_at": datetime.utcnow().isoformat()
        }
        
        # We're not using the schema here since we added a custom field
        return jsonify(response_data)
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400