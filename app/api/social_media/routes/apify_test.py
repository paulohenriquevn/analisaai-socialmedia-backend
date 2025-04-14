"""
Routes for testing Apify integration
"""
from flask import Blueprint, jsonify, request, current_app
from app.services.apify_service import ApifyService
from app.services.social_media_service import SocialMediaService
from flask_jwt_extended import jwt_required, get_jwt_identity

apify_test_bp = Blueprint('apify_test', __name__)

@apify_test_bp.route('/instagram', methods=['GET'])
@jwt_required()
def test_instagram_apify():
    """Test Apify integration for Instagram."""
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username parameter is required'}), 400
    
    # Get current user ID
    current_user_id = get_jwt_identity()
    
    # Use social media service to fetch profile
    profile_data = SocialMediaService.fetch_instagram_profile(current_user_id, username)
    
    if not profile_data or 'error' in profile_data:
        return jsonify({
            'error': 'Failed to fetch Instagram profile',
            'details': profile_data.get('message') if profile_data else 'Unknown error'
        }), 404
    
    return jsonify(profile_data), 200

@apify_test_bp.route('/tiktok', methods=['GET'])
@jwt_required()
def test_tiktok_apify():
    """Test Apify integration for TikTok."""
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username parameter is required'}), 400
    
    # Get current user ID
    current_user_id = get_jwt_identity()
    
    # Use social media service to fetch profile
    profile_data = SocialMediaService.fetch_tiktok_profile(current_user_id, username)
    
    if not profile_data or 'error' in profile_data:
        return jsonify({
            'error': 'Failed to fetch TikTok profile',
            'details': profile_data.get('message') if profile_data else 'Unknown error'
        }), 404
    
    return jsonify(profile_data), 200

@apify_test_bp.route('/facebook', methods=['GET'])
@jwt_required()
def test_facebook_apify():
    """Test Apify integration for Facebook."""
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username parameter is required'}), 400
    
    # Get current user ID
    current_user_id = get_jwt_identity()
    
    # Use social media service to fetch profile
    profile_data = SocialMediaService.fetch_facebook_profile(current_user_id, username)
    
    if not profile_data or 'error' in profile_data:
        return jsonify({
            'error': 'Failed to fetch Facebook profile',
            'details': profile_data.get('message') if profile_data else 'Unknown error'
        }), 404
    
    return jsonify(profile_data), 200