"""Routes for social media connection."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging

from app.extensions import db
from app.models.user import User
from app.api.social_media.schemas.connect import SocialMediaConnectRequest, SocialMediaConnectResponse, EngagementMetricsSchema
from app.services.social_media_service import SocialMediaService

# Create a separate blueprint for connect routes
bp_connect = Blueprint('social_media_connect', __name__)

# Import the main blueprint to register this blueprint
from app.api.social_media import bp

# Register this blueprint with the main blueprint
bp.register_blueprint(bp_connect)

logger = logging.getLogger(__name__)

@bp_connect.route('/connect', methods=['POST'])
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
    
    # Also create or update an socialpage record
    from app.models import SocialPage, SocialPageCategory
    
    # Clean username (remove @ if present)
    clean_username = username.replace('@', '')
    
    # Check if social_page already exists
    social_page = SocialPage.query.filter_by(
        username=clean_username,
        platform=platform
    ).first()
    
    if not social_page:
        # Create new social_page record
        logger.info(f"Creating new social_page record for {username} on {platform}")
        
        # Set default values
        social_page_data = {
            "username": clean_username,
            "full_name": clean_username,  # Default to username
            "platform": platform,
            "user_id": user_id,
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
                    
                    # Update social_page data with real values from API
                    if 'username' in profile_data:
                        social_page_data['username'] = profile_data.get('username', clean_username)
                    
                    if 'full_name' in profile_data:
                        social_page_data['full_name'] = profile_data.get('full_name', clean_username)
                    
                    if 'profile_url' in profile_data:
                        social_page_data['profile_url'] = profile_data.get('profile_url')
                    
                    if 'profile_image' in profile_data:
                        social_page_data['profile_image'] = profile_data.get('profile_image')
                    
                    if 'bio' in profile_data:
                        social_page_data['bio'] = profile_data.get('bio')
                    
                    if 'followers_count' in profile_data:
                        social_page_data['followers_count'] = profile_data.get('followers_count', 0)
                    
                    if 'following_count' in profile_data:
                        social_page_data['following_count'] = profile_data.get('following_count', 0)
                    
                    if 'posts_count' in profile_data:
                        social_page_data['posts_count'] = profile_data.get('posts_count', 0)
                    
                    if 'engagement_rate' in profile_data:
                        social_page_data['engagement_rate'] = profile_data.get('engagement_rate', 0.0)
                    
                    # Calculate social score based on actual data
                    if 'followers_count' in profile_data and 'engagement_rate' in profile_data:
                        social_page_data['social_score'] = SocialMediaService.calculate_social_score(profile_data)
                
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
                            social_page_data[field] = profile_data.get(field, social_page_data.get(field))
                    
                    # Calculate social score
                    social_page_data['social_score'] = SocialMediaService.calculate_social_score(profile_data)
            
            # If we have category information from the API, use it
            if profile_data and 'categories' in profile_data and isinstance(profile_data['categories'], list):
                social_page_data['categories'] = profile_data.get('categories', [])
                
        except Exception as e:
            logger.warning(f"Error fetching profile data from {platform}: {str(e)}")
            logger.warning("Using default values instead")
            # Continue with default values when API fetch fails
        
        # Create and save social_page
        social_page = SocialPage(**social_page_data)
        
        # Process categories from profile data if available
        if hasattr(social_page_data, 'categories') and social_page_data.get('categories'):
            for cat_name in social_page_data.get('categories', []):
                # Look up or create each category
                category = SocialPageCategory.query.filter_by(name=cat_name).first()
                if not category:
                    category = SocialPageCategory(name=cat_name, description=f"Category for {cat_name}")
                    db.session.add(category)
                social_page.categories.append(category)
            logger.info(f"Added categories from profile data for {clean_username}")
        
        db.session.add(social_page)
        db.session.commit()
        
        logger.info(f"Created social_page with ID: {social_page.id}")
    else:
        logger.info(f"social_page already exists with ID: {social_page.id}")
        
        # If the social_page exists but has missing data, try to update it
        if (social_page.followers_count == 0 or 
            social_page.bio is None or 
            len(social_page.categories) == 0):
            
            logger.info(f"social_page {clean_username} has missing data, attempting to update from API")
            
            try:
                # Try to fetch updated data from API
                updated_data = None
                
                if platform == "instagram":
                    updated_data = SocialMediaService.fetch_instagram_profile(user_id, clean_username)
                elif platform == "tiktok":
                    updated_data = SocialMediaService.fetch_tiktok_profile(user_id, clean_username)
                
                if updated_data and isinstance(updated_data, dict):
                    # Update social_page with real data from API
                    if 'full_name' in updated_data:
                        social_page.full_name = updated_data.get('full_name', social_page.full_name)
                    
                    if 'bio' in updated_data:
                        social_page.bio = updated_data.get('bio', social_page.bio)
                    
                    if 'profile_image' in updated_data:
                        social_page.profile_image = updated_data.get('profile_image', social_page.profile_image)
                    
                    if 'followers_count' in updated_data:
                        social_page.followers_count = updated_data.get('followers_count', social_page.followers_count)
                    
                    if 'following_count' in updated_data:
                        social_page.following_count = updated_data.get('following_count', social_page.following_count)
                    
                    if 'posts_count' in updated_data:
                        social_page.posts_count = updated_data.get('posts_count', social_page.posts_count)
                    
                    if 'engagement_rate' in updated_data:
                        social_page.engagement_rate = updated_data.get('engagement_rate', social_page.engagement_rate)
                    
                    # Update social score
                    if 'followers_count' in updated_data and 'engagement_rate' in updated_data:
                        social_page.social_score = SocialMediaService.calculate_social_score(updated_data)
                    
                    # Update categories if available
                    if 'categories' in updated_data and isinstance(updated_data['categories'], list) and len(social_page.categories) == 0:
                        for cat_name in updated_data['categories']:
                            category = SocialPageCategory.query.filter_by(name=cat_name).first()
                            if not category:
                                category = SocialPageCategory(name=cat_name, description=f"Category for {cat_name}")
                                db.session.add(category)
                            social_page.categories.append(category)
                    
                    db.session.commit()
                    logger.info(f"Updated {clean_username}'s data from API")
                else:
                    logger.warning(f"Could not fetch updated data for {clean_username}")
            except Exception as e:
                logger.warning(f"Error updating {clean_username}'s data: {str(e)}")
    
    # Calculate metrics for the new/updated social_page
    engagement_metrics_result = None
    reach_metrics_result = None
    growth_metrics_result = None
    score_metrics_result = None
    
    try:
        if social_page:
            # Calculate engagement metrics
            from app.services.engagement_service import EngagementService
            logger.info(f"Calculating engagement metrics for newly connected social_page {social_page.id}")
            
            engagement_metrics_result = EngagementService.calculate_engagement_metrics(social_page.id)
            if engagement_metrics_result:
                logger.info(f"Successfully calculated engagement metrics for social_page {social_page.id}")
            else:
                logger.warning(f"Failed to calculate engagement metrics for social_page {social_page.id}")
                
            # Calculate reach metrics
            from app.services.reach_service import ReachService
            logger.info(f"Calculating reach metrics for newly connected social_page {social_page.id}")
            
            reach_metrics_result = ReachService.calculate_reach_metrics(social_page.id, user_id)
            if reach_metrics_result:
                logger.info(f"Successfully calculated reach metrics for social_page {social_page.id}")
            else:
                logger.warning(f"Failed to calculate reach metrics for social_page {social_page.id}")
                
            # Calculate growth metrics
            from app.services.growth_service import GrowthService
            logger.info(f"Calculating growth metrics for newly connected social_page {social_page.id}")
            
            growth_metrics_result = GrowthService.calculate_growth_metrics(social_page.id)
            if growth_metrics_result:
                logger.info(f"Successfully calculated growth metrics for social_page {social_page.id}")
            else:
                logger.warning(f"Failed to calculate growth metrics for social_page {social_page.id}")
                
            # Calculate relevance score (after all other metrics)
            from app.services.score_service import ScoreService
            logger.info(f"Calculating relevance score for newly connected social_page {social_page.id}")
            
            score_metrics_result = ScoreService.calculate_relevance_score(social_page.id)
            if score_metrics_result:
                logger.info(f"Successfully calculated relevance score for social_page {social_page.id}")
            else:
                logger.warning(f"Failed to calculate relevance score for social_page {social_page.id}")
    except Exception as e:
        logger.error(f"Error calculating metrics for connected account: {str(e)}")
        # Don't block the main flow if metrics calculation fails
    
    # Prepare response
    response = {
        "id": user.id,
        "user_id": user.id,
        "platform": platform,
        "external_id": external_id,
        "username": username,
        "created_at": user.updated_at,
        "social_page_id": social_page.id if social_page else None
    }
    
    # Add engagement metrics to the response if they were calculated
    if engagement_metrics_result:
        # Format the date if it's a datetime object
        if 'date' in engagement_metrics_result and hasattr(engagement_metrics_result['date'], 'isoformat'):
            engagement_metrics_result['date'] = engagement_metrics_result['date'].isoformat()
            
        response["engagement_metrics"] = {
            "date": engagement_metrics_result.get('date'),
            "posts_count": engagement_metrics_result.get('posts_count'),
            "engagement_rate": engagement_metrics_result.get('engagement_rate'),
            "avg_likes_per_post": engagement_metrics_result.get('avg_likes_per_post'),
            "avg_comments_per_post": engagement_metrics_result.get('avg_comments_per_post'),
            "avg_shares_per_post": engagement_metrics_result.get('avg_shares_per_post'),
            "total_likes": engagement_metrics_result.get('total_likes'),
            "total_comments": engagement_metrics_result.get('total_comments'),
            "total_shares": engagement_metrics_result.get('total_shares'),
            "growth_rate": engagement_metrics_result.get('growth_rate')
        }
    
    # Add reach metrics to the response if they were calculated
    if reach_metrics_result:
        # Format date/datetime fields
        if 'date' in reach_metrics_result and hasattr(reach_metrics_result['date'], 'isoformat'):
            reach_metrics_result['date'] = reach_metrics_result['date'].isoformat()
        if 'timestamp' in reach_metrics_result and hasattr(reach_metrics_result['timestamp'], 'isoformat'):
            reach_metrics_result['timestamp'] = reach_metrics_result['timestamp'].isoformat()
            
        response["reach_metrics"] = {
            "date": reach_metrics_result.get('date'),
            "impressions": reach_metrics_result.get('impressions'),
            "reach": reach_metrics_result.get('reach'),
            "story_views": reach_metrics_result.get('story_views'),
            "profile_views": reach_metrics_result.get('profile_views'),
            "stories_count": reach_metrics_result.get('stories_count'),
            "story_engagement_rate": reach_metrics_result.get('story_engagement_rate'),
            "story_completion_rate": reach_metrics_result.get('story_completion_rate'),
            "audience_growth": reach_metrics_result.get('audience_growth')
        }
    
    # Add growth metrics to the response if they were calculated
    if growth_metrics_result:
        # Format date field
        if 'date' in growth_metrics_result and hasattr(growth_metrics_result['date'], 'isoformat'):
            growth_metrics_result['date'] = growth_metrics_result['date'].isoformat()
            
        response["growth_metrics"] = {
            "date": growth_metrics_result.get('date'),
            "followers_count": growth_metrics_result.get('followers_count'),
            "new_followers_daily": growth_metrics_result.get('new_followers_daily'),
            "new_followers_weekly": growth_metrics_result.get('new_followers_weekly'),
            "new_followers_monthly": growth_metrics_result.get('new_followers_monthly'),
            "retention_rate": growth_metrics_result.get('retention_rate'),
            "churn_rate": growth_metrics_result.get('churn_rate'),
            "daily_growth_rate": growth_metrics_result.get('daily_growth_rate'),
            "weekly_growth_rate": growth_metrics_result.get('weekly_growth_rate'),
            "monthly_growth_rate": growth_metrics_result.get('monthly_growth_rate'),
            "growth_velocity": growth_metrics_result.get('growth_velocity'),
            "growth_acceleration": growth_metrics_result.get('growth_acceleration'),
            "projected_followers_30d": growth_metrics_result.get('projected_followers_30d'),
            "projected_followers_90d": growth_metrics_result.get('projected_followers_90d')
        }
    
    # Add score metrics to the response if they were calculated
    if score_metrics_result:
        # Format date field
        if 'date' in score_metrics_result and hasattr(score_metrics_result['date'], 'isoformat'):
            score_metrics_result['date'] = score_metrics_result['date'].isoformat()
            
        response["score_metrics"] = {
            "date": score_metrics_result.get('date'),
            "overall_score": score_metrics_result.get('overall_score'),
            "engagement_score": score_metrics_result.get('engagement_score'),
            "reach_score": score_metrics_result.get('reach_score'),
            "growth_score": score_metrics_result.get('growth_score'),
            "consistency_score": score_metrics_result.get('consistency_score'),
            "audience_quality_score": score_metrics_result.get('audience_quality_score')
        }
        
        if social_page:
            # Also add the current relevance score
            response["relevance_score"] = social_page.relevance_score
    
    return jsonify(SocialMediaConnectResponse().dump(response)), 201