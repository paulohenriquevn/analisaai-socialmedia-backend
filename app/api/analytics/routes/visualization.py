"""
Routes for visualization data.
"""
from flask import Blueprint, jsonify, request
from app.models import SocialPage
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

@bp.route('/engagement/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_engagement_visualization(social_page_id):
    """Get engagement metrics visualization data for a specific social_page."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if social_page exists and belongs to the current user
    social_page = SocialPage.query.filter_by(id=social_page_id, user_id=current_user_id).first()
    if not social_page:
        return jsonify({
            "status": "error",
            "message": f"Social page with ID {social_page_id} not found or you don't have permission to access it"
        }), 404
    
    # Get time range parameter (default: 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get visualization data from service
    visualization_data = VisualizationService.get_engagement_visualization(social_page_id, time_range)
    
    if not visualization_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get engagement visualization data for social page {social_page_id}"
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

@bp.route('/reach/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_reach_visualization(social_page_id):
    """Get reach metrics visualization data for a specific social_page."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if social_page exists and belongs to the current user
    social_page = SocialPage.query.filter_by(id=social_page_id, user_id=current_user_id).first()
    if not social_page:
        return jsonify({
            "status": "error",
            "message": f"Social page with ID {social_page_id} not found or you don't have permission to access it"
        }), 404
    
    # Get time range parameter (default: 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get visualization data from service
    visualization_data = VisualizationService.get_reach_visualization(social_page_id, time_range)
    
    if not visualization_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get reach visualization data for social page {social_page_id}"
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

@bp.route('/growth/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_growth_visualization(social_page_id):
    """Get growth metrics visualization data for a specific social_page."""
    # Get time range parameter (default: 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get visualization data from service
    visualization_data = VisualizationService.get_growth_visualization(social_page_id, time_range)
    
    if not visualization_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get growth visualization data for social_page {social_page_id}"
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

@bp.route('/score/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_score_visualization(social_page_id):
    """Get score metrics visualization data for a specific social_page."""
    # Get time range parameter (default: 30 days)
    time_range = request.args.get('time_range', 30, type=int)
    
    # Get visualization data from service
    visualization_data = VisualizationService.get_score_visualization(social_page_id, time_range)
    
    if not visualization_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get score visualization data for social_page {social_page_id}"
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

@bp.route('/dashboard/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_dashboard_overview(social_page_id):
    """Get dashboard overview with all metrics for a specific social_page."""
    # Get visualization data from service
    dashboard_data = VisualizationService.get_dashboard_overview(social_page_id)
    
    if not dashboard_data:
        return jsonify({
            "status": "error",
            "message": f"Failed to get dashboard overview for social_page {social_page_id}"
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
    """Get comparison visualization for multiple social_pages."""
    # Parse social_page IDs from query parameters
    social_page_ids_param = request.args.get('social_page_ids', '')
    
    try:
        social_page_ids = [int(id_str) for id_str in social_page_ids_param.split(',') if id_str]
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid social_page_ids format. Use comma-separated IDs (e.g., 1,2,3)"
        }), 400
    
    if not social_page_ids:
        return jsonify({
            "status": "error",
            "message": "No social_page IDs provided"
        }), 400
    
    # Get comparison data from service
    comparison_data = VisualizationService.get_comparison_visualization(social_page_ids)
    
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