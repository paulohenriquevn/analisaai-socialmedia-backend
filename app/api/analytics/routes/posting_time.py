"""
Posting time optimization routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.posting_time_service import PostingTimeService
from app.api.analytics.schemas.posting_time import (
    PostingTimeRequestSchema,
    PostingTimeResponseSchema,
    ContentTypeAnalysisResponseSchema,
    DayOfWeekAnalysisResponseSchema,
    IndustryBenchmarksResponseSchema
)

# Create blueprint
bp = Blueprint('posting_time', __name__)


@bp.route('/best-times', methods=['GET'])
@jwt_required()
def get_best_posting_times():
    """Get best posting times based on historical engagement data."""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate request parameters
        schema = PostingTimeRequestSchema()
        params = schema.load(request.args)
        
        # Get parameters
        platform = params.get('platform')
        content_type = params.get('content_type')
        days = params.get('days', 90)
        
        # Get best posting times
        result = PostingTimeService.get_best_posting_times(user_id, platform, content_type, days)
        
        # Check for errors
        if 'error' in result:
            return jsonify(result), 400
        
        # Validate and serialize response
        response_schema = PostingTimeResponseSchema()
        return jsonify(response_schema.dump(result))
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/content-types', methods=['GET'])
@jwt_required()
def get_content_type_performance():
    """Get performance analysis for different content types."""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate request parameters
        schema = PostingTimeRequestSchema()
        params = schema.load(request.args)
        
        # Get parameters
        platform = params.get('platform')
        days = params.get('days', 90)
        
        # Get content type performance
        result = PostingTimeService.get_content_type_performance(user_id, platform, days)
        
        # Check for errors
        if 'error' in result:
            return jsonify(result), 400
        
        # Validate and serialize response
        response_schema = ContentTypeAnalysisResponseSchema()
        return jsonify(response_schema.dump(result))
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/days-of-week', methods=['GET'])
@jwt_required()
def get_day_of_week_analysis():
    """Get performance analysis by day of week."""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate request parameters
        schema = PostingTimeRequestSchema()
        params = schema.load(request.args)
        
        # Get parameters
        platform = params.get('platform')
        days = params.get('days', 90)
        
        # Get day of week analysis
        result = PostingTimeService.get_day_of_week_analysis(user_id, platform, days)
        
        # Check for errors
        if 'error' in result:
            return jsonify(result), 400
        
        # Validate and serialize response
        response_schema = DayOfWeekAnalysisResponseSchema()
        return jsonify(response_schema.dump(result))
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/benchmarks', methods=['GET'])
@jwt_required()
def get_industry_benchmarks():
    """Get industry benchmarks for posting times."""
    try:
        # Validate request parameters
        schema = PostingTimeRequestSchema()
        params = schema.load(request.args)
        
        # Get parameters
        platform = params.get('platform')
        category = request.args.get('category')  # Optional category parameter
        
        # Get industry benchmarks
        result = PostingTimeService.get_industry_benchmarks(category, platform)
        
        # Check for errors
        if 'error' in result:
            return jsonify(result), 400
        
        # Validate and serialize response
        response_schema = IndustryBenchmarksResponseSchema()
        return jsonify(response_schema.dump(result))
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_personalized_recommendations():
    """Get personalized posting time recommendations."""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate request parameters
        schema = PostingTimeRequestSchema()
        params = schema.load(request.args)
        
        # Get parameters
        platform = params.get('platform')
        content_type = params.get('content_type')
        
        # Get personalized recommendations
        result = PostingTimeService.get_personalized_recommendations(user_id, platform, content_type)
        
        # Check for errors
        if 'error' in result:
            return jsonify(result), 400
        
        # Validate and serialize response
        response_schema = PostingTimeResponseSchema()
        return jsonify(response_schema.dump(result))
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500