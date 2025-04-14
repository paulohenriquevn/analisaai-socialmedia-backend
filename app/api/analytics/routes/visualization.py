"""
Routes for visualization data.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from marshmallow import ValidationError

from app.services.visualization_service import VisualizationService
from app.api.analytics.schemas import (
    EngagementVisualizationSchema,
    ReachVisualizationSchema,
    GrowthVisualizationSchema,
    ScoreVisualizationSchema,
    DashboardOverviewSchema,
    ComparisonVisualizationSchema
)

# Create blueprint
bp = Blueprint('visualization', __name__)

logger = logging.getLogger(__name__)

@bp.route('/engagement/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_engagement_visualization(influencer_id):
    """Get engagement metrics visualization data for a specific influencer."""
    # Get time range parameter (default: 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get visualization data from service
    visualization_data = VisualizationService.get_engagement_visualization(influencer_id, time_range)
    
    if not visualization_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get engagement visualization data for influencer {influencer_id}"
        }), 404
    
    try:
        return jsonify({
            "status": "success",
            "visualization": visualization_data
        })
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Data validation failed",
            "errors": str(e)
        }), 400

@bp.route('/reach/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_reach_visualization(influencer_id):
    """Get reach metrics visualization data for a specific influencer."""
    # Get time range parameter (default: 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get visualization data from service
    visualization_data = VisualizationService.get_reach_visualization(influencer_id, time_range)
    
    if not visualization_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get reach visualization data for influencer {influencer_id}"
        }), 404
    
    try:
        return jsonify({
            "status": "success",
            "visualization": visualization_data
        })
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Data validation failed",
            "errors": str(e)
        }), 400

@bp.route('/growth/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_growth_visualization(influencer_id):
    """Get growth metrics visualization data for a specific influencer."""
    # Get time range parameter (default: 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get visualization data from service
    visualization_data = VisualizationService.get_growth_visualization(influencer_id, time_range)
    
    if not visualization_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get growth visualization data for influencer {influencer_id}"
        }), 404
    
    try:
        # Validate with schema before returning
        return jsonify({
            "status": "success",
            "visualization": visualization_data
        })
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Data validation failed",
            "errors": str(e)
        }), 400

@bp.route('/score/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_score_visualization(influencer_id):
    """Get score metrics visualization data for a specific influencer."""
    # Get time range parameter (default: 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get visualization data from service
    visualization_data = VisualizationService.get_score_visualization(influencer_id, time_range)
    
    if not visualization_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get score visualization data for influencer {influencer_id}"
        }), 404
    
    try:
        # Validate with schema before returning
        return jsonify({
            "status": "success",
            "visualization": visualization_data
        })
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Data validation failed",
            "errors": str(e)
        }), 400

@bp.route('/dashboard/<int:influencer_id>', methods=['GET'])
@jwt_required()
def get_dashboard_overview(influencer_id):
    """Get dashboard overview with all metrics for a specific influencer."""
    # Get visualization data from service
    dashboard_data = VisualizationService.get_dashboard_overview(influencer_id)
    
    if not dashboard_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get dashboard overview for influencer {influencer_id}"
        }), 404
    
    try:
        # Validate with schema before returning
        return jsonify({
            "status": "success",
            "dashboard": dashboard_data
        })
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Data validation failed",
            "errors": str(e)
        }), 400

@bp.route('/compare', methods=['GET'])
@jwt_required()
def get_comparison_visualization():
    """Get comparison visualization for multiple influencers."""
    # Parse influencer IDs from query parameters
    influencer_ids_param = request.args.get('influencer_ids', '')
    
    try:
        influencer_ids = [int(id_str) for id_str in influencer_ids_param.split(',') if id_str]
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid influencer_ids format. Use comma-separated IDs (e.g., 1,2,3)"
        }), 400
    
    if not influencer_ids:
        return jsonify({
            "status": "error",
            "message": "No influencer IDs provided"
        }), 400
    
    # Get comparison data from service
    comparison_data = VisualizationService.get_comparison_visualization(influencer_ids)
    
    if not comparison_data:
        return jsonify({
            "status": "error",
            "message": "Failed to get comparison visualization data"
        }), 404
    
    try:
        # Validate with schema before returning
        schema = ComparisonVisualizationSchema()
        validated_data = schema.dump(comparison_data)
        
        return jsonify({
            "status": "success",
            "comparison": validated_data
        })
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Data validation failed",
            "errors": str(e)
        }), 400