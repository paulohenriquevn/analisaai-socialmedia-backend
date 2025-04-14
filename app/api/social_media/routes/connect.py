"""Routes for social media connection."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging

from app.extensions import db
from app.models.user import User
from app.api.social_media.schemas.connect import SocialMediaConnectRequest, SocialMediaConnectResponse
from app.services.social_media_service import SocialMediaService

from app.api.social_media import bp

logger = logging.getLogger(__name__)

@bp.route('/connect', methods=['POST'])
@jwt_required()
def connect_social_media():
    """Connect a social media account to the authenticated user."""
    # Get authenticated user
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Validate request data
    schema = SocialMediaConnectRequest()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid request data", "details": err.messages}), 400
    
    platform = data['platform']
    username = data['username']
    
    # Validate platform
    if platform not in ["instagram", "facebook", "tiktok"]:
        return jsonify({"error": "Plataforma não suportada"}), 400
    
    # Check if user already has this platform connected
    platform_id_field = f"{platform}_id"
    if getattr(user, platform_id_field):
        return jsonify({"error": "Rede social já vinculada"}), 409
    
    # Get external_id from request or find it
    if 'external_id' in data and data['external_id']:
        # User provided the external_id
        external_id = data['external_id']
        logger.info(f"Using provided external_id: {external_id}")
    else:
        # Find or generate external_id from username
        logger.info(f"Finding external_id for {platform} username: {username}")
        external_id = SocialMediaService.find_social_media_id(platform, username, user_id)
        logger.info(f"Found/generated external_id: {external_id}")
    
    # Connect the social media account to the user
    setattr(user, platform_id_field, external_id)
    db.session.commit()
    
    # Also create or update an influencer record
    from app.models.influencer import Influencer, Category
    
    # Clean username (remove @ if present)
    clean_username = username.replace('@', '')
    
    # Check if influencer already exists
    influencer = Influencer.query.filter_by(
        username=clean_username,
        platform=platform
    ).first()
    
    if not influencer:
        # Create new influencer record
        logger.info(f"Creating new influencer record for {username} on {platform}")
        
        # Set default values
        influencer_data = {
            "username": clean_username,
            "full_name": clean_username,  # Default to username
            "platform": platform,
            "profile_url": f"https://{platform}.com/{clean_username}",
            "followers_count": 0,
            "following_count": 0,
            "posts_count": 0,
            "engagement_rate": 0.0,
            "social_score": 50.0  # Default middle score
        }
        
        # Try to fetch real profile data based on platform
        logger.info(f"Attempting to fetch real profile data for {clean_username} on {platform}")
        
        try:
            profile_data = None
            
            if platform == "instagram":
                # Try to fetch real Instagram data
                logger.info(f"Fetching Instagram profile data for {clean_username}")
                profile_data = SocialMediaService.fetch_instagram_profile(user_id, clean_username)
                
                if profile_data and isinstance(profile_data, dict):
                    logger.info(f"Successfully fetched Instagram data for {clean_username}")
                    
                    # Update influencer data with real values from API
                    if 'username' in profile_data:
                        influencer_data['username'] = profile_data.get('username', clean_username)
                    
                    if 'full_name' in profile_data:
                        influencer_data['full_name'] = profile_data.get('full_name', clean_username)
                    
                    if 'profile_url' in profile_data:
                        influencer_data['profile_url'] = profile_data.get('profile_url')
                    
                    if 'profile_image' in profile_data:
                        influencer_data['profile_image'] = profile_data.get('profile_image')
                    
                    if 'bio' in profile_data:
                        influencer_data['bio'] = profile_data.get('bio')
                    
                    if 'followers_count' in profile_data:
                        influencer_data['followers_count'] = profile_data.get('followers_count', 0)
                    
                    if 'following_count' in profile_data:
                        influencer_data['following_count'] = profile_data.get('following_count', 0)
                    
                    if 'posts_count' in profile_data:
                        influencer_data['posts_count'] = profile_data.get('posts_count', 0)
                    
                    if 'engagement_rate' in profile_data:
                        influencer_data['engagement_rate'] = profile_data.get('engagement_rate', 0.0)
                    
                    # Calculate social score based on actual data
                    if 'followers_count' in profile_data and 'engagement_rate' in profile_data:
                        influencer_data['social_score'] = SocialMediaService.calculate_social_score(profile_data)
                
            elif platform == "facebook":
                # Similar implementation for Facebook
                logger.info(f"Fetching Facebook profile data for {clean_username}")
                # Use appropriate service method for Facebook
                # profile_data = SocialMediaService.fetch_facebook_profile(user_id, clean_username)
                
            elif platform == "tiktok":
                # Similar implementation for TikTok
                logger.info(f"Fetching TikTok profile data for {clean_username}")
                profile_data = SocialMediaService.fetch_tiktok_profile(user_id, clean_username)
                
                if profile_data and isinstance(profile_data, dict):
                    logger.info(f"Successfully fetched TikTok data for {clean_username}")
                    
                    # Update with real TikTok data
                    for field in ['username', 'full_name', 'profile_url', 'profile_image', 'bio',
                                 'followers_count', 'following_count', 'posts_count', 'engagement_rate']:
                        if field in profile_data:
                            influencer_data[field] = profile_data.get(field, influencer_data.get(field))
                    
                    # Calculate social score
                    influencer_data['social_score'] = SocialMediaService.calculate_social_score(profile_data)
            
            # If we have category information from the API, use it
            if profile_data and 'categories' in profile_data and isinstance(profile_data['categories'], list):
                influencer_data['categories'] = profile_data.get('categories', [])
                
        except Exception as e:
            logger.warning(f"Error fetching profile data from {platform}: {str(e)}")
            logger.warning("Using default values instead")
            # Continue with default values when API fetch fails
        
        # Create and save influencer
        influencer = Influencer(**influencer_data)
        
        # Process categories from profile data if available
        if hasattr(influencer_data, 'categories') and influencer_data.get('categories'):
            for cat_name in influencer_data.get('categories', []):
                # Look up or create each category
                category = Category.query.filter_by(name=cat_name).first()
                if not category:
                    category = Category(name=cat_name, description=f"Category for {cat_name}")
                    db.session.add(category)
                influencer.categories.append(category)
            logger.info(f"Added categories from profile data for {clean_username}")
        
        db.session.add(influencer)
        db.session.commit()
        
        logger.info(f"Created influencer with ID: {influencer.id}")
    else:
        logger.info(f"Influencer already exists with ID: {influencer.id}")
        
        # If the influencer exists but has missing data, try to update it
        if (influencer.followers_count == 0 or 
            influencer.bio is None or 
            len(influencer.categories) == 0):
            
            logger.info(f"Influencer {clean_username} has missing data, attempting to update from API")
            
            try:
                # Try to fetch updated data from API
                updated_data = None
                
                if platform == "instagram":
                    updated_data = SocialMediaService.fetch_instagram_profile(user_id, clean_username)
                elif platform == "tiktok":
                    updated_data = SocialMediaService.fetch_tiktok_profile(user_id, clean_username)
                
                if updated_data and isinstance(updated_data, dict):
                    # Update influencer with real data from API
                    if 'full_name' in updated_data:
                        influencer.full_name = updated_data.get('full_name', influencer.full_name)
                    
                    if 'bio' in updated_data:
                        influencer.bio = updated_data.get('bio', influencer.bio)
                    
                    if 'profile_image' in updated_data:
                        influencer.profile_image = updated_data.get('profile_image', influencer.profile_image)
                    
                    if 'followers_count' in updated_data:
                        influencer.followers_count = updated_data.get('followers_count', influencer.followers_count)
                    
                    if 'following_count' in updated_data:
                        influencer.following_count = updated_data.get('following_count', influencer.following_count)
                    
                    if 'posts_count' in updated_data:
                        influencer.posts_count = updated_data.get('posts_count', influencer.posts_count)
                    
                    if 'engagement_rate' in updated_data:
                        influencer.engagement_rate = updated_data.get('engagement_rate', influencer.engagement_rate)
                    
                    # Update social score
                    if 'followers_count' in updated_data and 'engagement_rate' in updated_data:
                        influencer.social_score = SocialMediaService.calculate_social_score(updated_data)
                    
                    # Update categories if available
                    if 'categories' in updated_data and isinstance(updated_data['categories'], list) and len(influencer.categories) == 0:
                        for cat_name in updated_data['categories']:
                            category = Category.query.filter_by(name=cat_name).first()
                            if not category:
                                category = Category(name=cat_name, description=f"Category for {cat_name}")
                                db.session.add(category)
                            influencer.categories.append(category)
                    
                    db.session.commit()
                    logger.info(f"Updated {clean_username}'s data from API")
                else:
                    logger.warning(f"Could not fetch updated data for {clean_username}")
            except Exception as e:
                logger.warning(f"Error updating {clean_username}'s data: {str(e)}")
    
    # Prepare response
    response = {
        "id": user.id,
        "user_id": user.id,
        "platform": platform,
        "external_id": external_id,
        "username": username,
        "created_at": user.updated_at,
        "influencer_id": influencer.id if influencer else None
    }
    
    return jsonify(SocialMediaConnectResponse().dump(response)), 201