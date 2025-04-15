"""
Sentiment analysis routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.sentiment_service import SentimentService
from app.api.analytics.schemas import (
    SentimentAnalysisRequestSchema, 
    SentimentAnalysisResponseSchema,
    PostSentimentAnalysisSchema,
)
from app.models import  SocialPagePost, SocialPagePostComment
from app.services.oauth_service import get_token

# Create blueprint
bp = Blueprint('sentiment', __name__)


@bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_sentiment():
    """Analyze sentiment of provided text."""
    try:
        # Validate request data
        schema = SentimentAnalysisRequestSchema()
        data = schema.load(request.get_json())
        
        # Analyze sentiment
        text = data['text']
        result = SentimentService.analyze_sentiment(text)
        
        # Prepare response
        response = {
            'text': text,
            'sentiment': result['sentiment'],
            'score': result['score'],
            'is_critical': result['is_critical']
        }
        
        # Validate and serialize response
        response_schema = SentimentAnalysisResponseSchema()
        return jsonify(response_schema.dump(response))
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/post/<int:post_id>/comments', methods=['GET'])
@jwt_required()
def get_post_comments(post_id):
    """Get all comments for a post with sentiment analysis."""
    try:
        post = SocialPagePost.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Get all comments
        comments = SocialPagePostComment.query.filter_by(post_id=post.id).all()
        
        # Format comments
        formatted_comments = []
        for comment in comments:
            formatted_comments.append({
                'id': comment.id,
                'comment_id': comment.comment_id,
                'author_username': comment.author_username,
                'author_display_name': comment.author_display_name,
                'author_picture': comment.author_picture,
                'content': comment.content,
                'posted_at': comment.posted_at.isoformat() if comment.posted_at else None,
                'likes_count': comment.likes_count,
                'sentiment': comment.sentiment,
                'sentiment_score': comment.sentiment_score,
                'is_critical': comment.is_critical
            })
        
        return jsonify({
            "post_id": post_id,
            "comments": formatted_comments
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/post/<int:post_id>/sentiment', methods=['GET'])
@jwt_required()
def get_post_sentiment(post_id):
    """Get sentiment analysis for a specific post."""
    try:
        # Get sentiment analysis for the post
        analysis = SentimentService.get_post_sentiment_analysis(post_id)
        
        # Check for errors
        if 'error' in analysis and analysis.get('error') != "Post not found":
            error_status = 500
            error_code = analysis.get('error')
            
            # Map error codes to appropriate HTTP status codes
            if error_code in ['auth_error', 'token_expired']:
                error_status = 401
            elif error_code in ['permission_denied', 'forbidden']:
                error_status = 403
            elif error_code in ['account_not_found', 'profile_not_found']:
                error_status = 404
            elif error_code in ['rate_limit']:
                error_status = 429
            
            return jsonify({"error": error_code, "message": analysis.get('message', '')}), error_status
            
        # Validate and serialize response
        response_schema = PostSentimentAnalysisSchema()
        return jsonify(response_schema.dump(analysis))
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/social_page/<int:social_page_id>/sentiment', methods=['GET'])
@jwt_required()
def get_social_page_sentiment(social_page_id):
    """Get sentiment analysis for an social_page across all posts."""
    try:
        # Parse time range from query parameters (default to 30 days)
        time_range = request.args.get('time_range', 30, type=int)
        
        # Get sentiment analysis for the social_page
        analysis = SentimentService.get_social_page_sentiment_analysis(social_page_id, time_range)
        
        # Check for errors
        if 'error' in analysis:
            error_status = 500
            error_code = analysis.get('error')
            
            # Map error codes to appropriate HTTP status codes
            if error_code in ['auth_error', 'token_expired']:
                error_status = 401
            elif error_code in ['permission_denied', 'forbidden']:
                error_status = 403
            elif error_code in ['not_found', 'social_page_not_found', 'profile_not_found']:
                error_status = 404
            elif error_code in ['rate_limit']:
                error_status = 429
            
            return jsonify({"error": error_code, "message": analysis.get('message', '')}), error_status
            
        # Validate and serialize response
        return analysis
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/post/<int:post_id>/comments/fetch', methods=['POST'])
@jwt_required()
def fetch_post_comments(post_id):
    """Fetch and analyze comments for a specific post."""
    try:
        user_id = int(get_jwt_identity())
        
        # Get the post
        post = SocialPagePost.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
            
        # Get token for the platform
        token_data = get_token(user_id, post.platform)
        if not token_data:
            return jsonify({"error": f"No {post.platform} token found"}), 400
            
        access_token = token_data['access_token']
        
        # Fetch comments
        comments_data = SentimentService.fetch_comments(post.platform, post.post_id, access_token)
        
        if not comments_data:
            return jsonify({
                "post_id": post_id,
                "comments_fetched": 0,
                "message": "No comments found or failed to fetch comments"
            })
            
        # Save comments
        comments_saved = SentimentService.save_comments(post, comments_data)
        
        return jsonify({
            "post_id": post_id,
            "comments_fetched": len(comments_data),
            "comments_saved": comments_saved,
            "message": f"Successfully fetched and analyzed {len(comments_data)} comments"
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/batch-analyze', methods=['POST'])
@jwt_required()
def batch_analyze():
    """Analyze sentiment for a batch of text inputs."""
    try:
        # Validate request data
        data = request.get_json()
        if not data or not isinstance(data.get('texts', []), list):
            return jsonify({"error": "Invalid request format. Expected a list of texts."}), 400
            
        texts = data['texts']
        if not texts:
            return jsonify({"results": []})
            
        # Analyze all texts
        results = SentimentService.analyze_comment_batch(texts)
        
        return jsonify({"results": results})
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500