"""Routes for updating social_page data."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging
from datetime import datetime

from app.extensions import db
from app.models import SocialPage, SocialPageCategory, SocialPageMetric
from app.api.social_media import bp
from app.services.engagement_service import EngagementService
from app.services.social_media_service import SocialMediaService
from app.services.apify_service import ApifyService

logger = logging.getLogger(__name__)

@bp.route('/social_page/<int:social_page_id>', methods=['PUT'])
@jwt_required()
def update_social_page(social_page_id):
    """
    Update details for a social page.
    ---
    tags:
      - SocialMedia
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: social_page_id
        schema:
          type: integer
        required: true
        description: "ID of the social page to update"
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              full_name:
                type: string
                description: "Full name of the social page"
              bio:
                type: string
                description: "Biography or description"
              profile_image:
                type: string
                description: "Profile image URL"
              followers_count:
                type: integer
                description: "Number of followers"
              following_count:
                type: integer
                description: "Number of following"
              posts_count:
                type: integer
                description: 'Number of posts'
              engagement_rate:
                type: number
                description: 'Engagement rate'
              categories:
                type: array
                items:
                  type: string
                description: 'List of category names'
              likes:
                type: integer
                description: 'Likes count (optional)'
              comments:
                type: integer
                description: 'Comments count (optional)'
              shares:
                type: integer
                description: 'Shares count (optional)'
              views:
                type: integer
                description: 'Views count (optional)'
    responses:
      200:
        description: 'Social page updated successfully'
        content:
          application/json:
            schema:
              type: object
      400:
        description: 'No data provided or invalid data'
      404:
        description: 'Social page not found'
      401:
        description: 'Not authenticated'
    """
    user_id = get_jwt_identity()
    
    # Find the social_page
    social_page = SocialPage.query.get(social_page_id)
    if not social_page:
        return jsonify({"error": "social_page not found"}), 404
    
    # Validate the data
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update the social_page data
    if 'full_name' in data:
        social_page.full_name = data['full_name']
    
    if 'bio' in data:
        social_page.bio = data['bio']
    
    if 'profile_image' in data:
        social_page.profile_image = data['profile_image']
    
    # Track if metrics-related fields were updated
    metrics_updated = False
    
    if 'followers_count' in data:
        social_page.followers_count = data['followers_count']
        metrics_updated = True
    
    if 'following_count' in data:
        social_page.following_count = data['following_count']
        metrics_updated = True
    
    if 'posts_count' in data:
        social_page.posts_count = data['posts_count']
        metrics_updated = True
    
    if 'engagement_rate' in data:
        social_page.engagement_rate = data['engagement_rate']
        metrics_updated = True
    
    # Handle categories
    if 'categories' in data and isinstance(data['categories'], list):
        categories = []
        for category_name in data['categories']:
            # Look up or create each category
            category = SocialPageCategory.query.filter_by(name=category_name).first()
            if not category:
                category = SocialPageCategory(name=category_name, description=f"Category for {category_name}")
                db.session.add(category)
            categories.append(category)
        social_page.categories = categories
    
    # Save changes
    db.session.commit()
    logger.info(f"Updated social_page {social_page.id} - {social_page.username}")
    
    # Update metrics if metric-related fields were changed
    engagement_metrics_result = None
    if metrics_updated:
        try:
            # Update the social_pageMetric record for today
            today = datetime.utcnow().date()
            
            # Check if we already have metrics for today
            existing_metric = SocialPageMetric.query.filter_by(
                social_page_id=social_page.id,
                date=today
            ).first()
            
            if existing_metric:
                # Update existing metric
                if 'followers_count' in data:
                    existing_metric.followers = data['followers_count']
                if 'engagement_rate' in data:
                    existing_metric.engagement = data['engagement_rate']
                if 'posts_count' in data:
                    existing_metric.posts = data['posts_count']
                # For likes, comments, shares, and views, only update if provided
                if 'likes' in data:
                    existing_metric.likes = data['likes']
                if 'comments' in data:
                    existing_metric.comments = data['comments']
                if 'shares' in data:
                    existing_metric.shares = data['shares']
                if 'views' in data:
                    existing_metric.views = data['views']
            else:
                # Create new metric with whatever data we have
                metric = SocialPageMetric(
                    social_page_id=social_page.id,
                    date=today,
                    followers=social_page.followers_count,
                    engagement=social_page.engagement_rate,
                    posts=social_page.posts_count,
                    likes=data.get('likes', 0),
                    comments=data.get('comments', 0),
                    shares=data.get('shares', 0),
                    views=data.get('views', 0)
                )
                db.session.add(metric)
            
            db.session.commit()
            logger.info(f"Updated metrics for social_page {social_page.id} - {social_page.username}")
            
            # Recalculate engagement metrics using EngagementService
            engagement_metrics_result = EngagementService.calculate_engagement_metrics(social_page.id)
            if engagement_metrics_result:
                logger.info(f"Successfully calculated engagement metrics for social_page {social_page.id}")
            else:
                logger.warning(f"Failed to calculate engagement metrics for social_page {social_page.id}")
                
            # Also calculate reach metrics
            reach_metrics_result = None
            try:
                from app.services.reach_service import ReachService
                reach_metrics_result = ReachService.calculate_reach_metrics(social_page.id, user_id)
                if reach_metrics_result:
                    logger.info(f"Successfully calculated reach metrics for social_page {social_page.id}")
                else:
                    logger.warning(f"Failed to calculate reach metrics for social_page {social_page.id}")
            except Exception as e:
                logger.error(f"Error calculating reach metrics for social_page {social_page.id}: {str(e)}")
                
            # Calculate growth metrics
            growth_metrics_result = None
            try:
                from app.services.growth_service import GrowthService
                growth_metrics_result = GrowthService.calculate_growth_metrics(social_page.id)
                if growth_metrics_result:
                    logger.info(f"Successfully calculated growth metrics for social_page {social_page.id}")
                else:
                    logger.warning(f"Failed to calculate growth metrics for social_page {social_page.id}")
            except Exception as e:
                logger.error(f"Error calculating growth metrics for social_page {social_page.id}: {str(e)}")
                
            # Calculate relevance score (after all other metrics)
            score_metrics_result = None
            try:
                from app.services.score_service import ScoreService
                score_metrics_result = ScoreService.calculate_relevance_score(social_page.id)
                if score_metrics_result:
                    logger.info(f"Successfully calculated relevance score for social_page {social_page.id}")
                else:
                    logger.warning(f"Failed to calculate relevance score for social_page {social_page.id}")
            except Exception as e:
                logger.error(f"Error calculating relevance score for social_page {social_page.id}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error updating metrics for social_page {social_page.id}: {str(e)}")
            # Don't block the social_page update if metrics update fails
    
    # Prepare the response
    response = {
        "message": "social_page updated successfully",
        "social_page": {
            "id": social_page.id,
            "username": social_page.username,
            "full_name": social_page.full_name,
            "platform": social_page.platform,
            "profile_url": social_page.profile_url,
            "profile_image": social_page.profile_image,
            "bio": social_page.bio,
            "followers_count": social_page.followers_count,
            "following_count": social_page.following_count,
            "posts_count": social_page.posts_count,
            "engagement_rate": social_page.engagement_rate,
            "social_score": social_page.social_score,
            "relevance_score": social_page.relevance_score,
            "categories": [c.name for c in social_page.categories]
        }
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
        
        # Also update the social_page's relevance_score in the response
        response["social_page"]["relevance_score"] = social_page.relevance_score
    
    return jsonify(response)


@bp.route('/social_page/<int:social_page_id>/refresh', methods=['POST'])
@jwt_required()
def refresh_social_page_data(social_page_id):
    """
    Refresh social page data and fetch recent posts.
    ---
    tags:
      - SocialMedia
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: social_page_id
        schema:
          type: integer
        required: true
        description: "ID of the social page to refresh"
    responses:
      200:
        description: "Social page data refreshed successfully"
        content:
          application/json:
            schema:
              type: object
      404:
        description: "Social page not found"
      400:
        description: "Failed to fetch or save data"
      401:
        description: "Not authenticated"
    """
    user_id = get_jwt_identity()
    logger.info(f"User {user_id} requested refresh of social_page {social_page_id}")
    
    # Check if social_page exists
    social_page = SocialPage.query.get(social_page_id)
    if not social_page:
        return jsonify({"error": f"social_page with ID {social_page_id} not found"}), 404
    
    # Get refresh options from request
    refresh_options = request.json or {}
    fetch_posts = refresh_options.get('fetch_posts', True)
    
    try:
        # Fetch the latest profile data
        if social_page.platform == 'instagram':
            profile_data = ApifyService.fetch_instagram_profile(social_page.username)
        elif social_page.platform == 'tiktok':
            profile_data = ApifyService.fetch_tiktok_profile(social_page.username)
        elif social_page.platform == 'facebook':
            profile_data = ApifyService.fetch_facebook_profile(social_page.username)
        else:
            return jsonify({"error": f"Unsupported platform: {social_page.platform}"}), 400
        
        if not profile_data or 'error' in profile_data:
            error_msg = profile_data.get('message', 'Unknown error') if profile_data else 'Failed to fetch profile data'
            return jsonify({"error": error_msg}), 500
        
        # Save the updated data to the database
        updated_social_page = SocialMediaService.save_social_page_data(profile_data)
        
        if not updated_social_page:
            return jsonify({"error": "Failed to update social_page data"}), 500
        
        # If fetch_posts is True and we don't have the last week of posts, get more posts
        posts_count = 0
        if fetch_posts:
            # Check if we have recent posts
            recent_posts = SocialMediaService.fetch_social_page_recent_posts(social_page_id, days=7)
            
            # If we have fewer posts than expected or post fetching is explicitly requested
            if len(recent_posts) < 5 or refresh_options.get('force_fetch_posts', False):
                # Get more posts from the API
                if 'recent_media' in profile_data and profile_data['recent_media']:
                    posts_count = SocialMediaService.save_recent_posts(
                        social_page_id, 
                        profile_data['recent_media'], 
                        social_page.platform
                    )
        
        # Prepare response data
        response_data = {
            "status": "success",
            "message": f"Successfully refreshed data for {social_page.username}",
            "social_page": {
                "id": updated_social_page.id,
                "username": updated_social_page.username,
                "platform": updated_social_page.platform,
                "followers_count": updated_social_page.followers_count,
                "engagement_rate": updated_social_page.engagement_rate,
                "social_score": updated_social_page.social_score,
                "posts_count": updated_social_page.posts_count,
                "updated_at": updated_social_page.updated_at.isoformat() if updated_social_page.updated_at else None
            },
            "posts": {
                "fetched": posts_count,
                "total_recent": len(recent_posts) if 'recent_posts' in locals() else 0
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error refreshing social_page {social_page_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@bp.route('/social_page/<int:social_page_id>/fetch-posts', methods=['POST'])
@jwt_required()
def fetch_posts(social_page_id):
    """
    Fetch and save recent posts for a social page.
    ---
    tags:
      - SocialMedia
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: social_page_id
        schema:
          type: integer
        required: true
        description: "ID of the social page to fetch posts for"
    responses:
      200:
        description: "Recent posts fetched and saved successfully"
        content:
          application/json:
            schema:
              type: object
      404:
        description: "Social page not found"
      400:
        description: "Failed to fetch or save posts"
      401:
        description: "Not authenticated"
    """
    user_id = get_jwt_identity()
    logger.info(f"User {user_id} requested post fetch for social_page {social_page_id}")
    
    # Check if social_page exists
    social_page = SocialPage.query.get(social_page_id)
    if not social_page:
        return jsonify({"error": f"social_page with ID {social_page_id} not found"}), 404
    
    try:
        # Fetch the latest profile data to get recent posts
        if social_page.platform == 'instagram':
            profile_data = ApifyService.fetch_instagram_profile(social_page.username)
        elif social_page.platform == 'tiktok':
            profile_data = ApifyService.fetch_tiktok_profile(social_page.username)
        elif social_page.platform == 'facebook':
            profile_data = ApifyService.fetch_facebook_profile(social_page.username)
        else:
            return jsonify({"error": f"Unsupported platform: {social_page.platform}"}), 400
        
        if not profile_data or 'error' in profile_data:
            error_msg = profile_data.get('message', 'Unknown error') if profile_data else 'Failed to fetch profile data'
            return jsonify({"error": error_msg}), 500
        
        # Extract and save recent posts
        posts_count = 0
        if 'recent_media' in profile_data and profile_data['recent_media']:
            posts_count = SocialMediaService.save_recent_posts(
                social_page_id, 
                profile_data['recent_media'], 
                social_page.platform
            )
        
        return jsonify({
            "status": "success",
            "message": f"Successfully fetched posts for {social_page.username}",
            "posts_fetched": posts_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching posts for social_page {social_page_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@bp.route('/fetch-posts-for-all', methods=['POST'])
@jwt_required()
def fetch_posts_for_all():
    """
    Fetch and save recent posts for all social pages or a filtered subset.
    ---
    tags:
      - SocialMedia
    security:
      - BearerAuth: []
    requestBody:
      required: false
      content:
        application/json:
          schema:
            type: object
            properties:
              platform:
                type: string
                description: "Filter by platform (optional)"
              limit:
                type: integer
                description: "Maximum number of social pages to process (optional)"
    responses:
      200:
        description: "Batch posts fetched and saved successfully"
        content:
          application/json:
            schema:
              type: object
      400:
        description: "Failed to fetch or save posts"
      401:
        description: "Not authenticated"
    """
    user_id = get_jwt_identity()
    logger.info(f"User {user_id} requested batch post fetch for social_pages")
    
    # Get filter parameters from request
    data = request.json or {}
    platform = data.get('platform', None)
    limit = data.get('limit', None)
    days_history = data.get('days', 7)  # Default to 7 days of post history
    
    try:
        # Build query to get social_pages
        query = SocialPage.query
        
        # Filter by platform if specified
        if platform:
            query = query.filter_by(platform=platform)
        
        # Order by last updated (oldest first)
        query = query.order_by(SocialPage.updated_at.asc())
        
        # Apply limit if specified
        if limit and isinstance(limit, int) and limit > 0:
            query = query.limit(limit)
            
        # Get the social_pages
        social_pages = query.all()
        
        if not social_pages:
            return jsonify({
                "status": "warning",
                "message": "No social_pages found matching the criteria"
            }), 200
            
        logger.info(f"Found {len(social_pages)} social_pages to process")
        
        # Process each social_page
        results = {
            "total": len(social_pages),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for social_page in social_pages:
            try:
                # Fetch the profile data to get recent posts
                if social_page.platform == 'instagram':
                    profile_data = ApifyService.fetch_instagram_profile(social_page.username)
                elif social_page.platform == 'tiktok':
                    profile_data = ApifyService.fetch_tiktok_profile(social_page.username)
                elif social_page.platform == 'facebook':
                    profile_data = ApifyService.fetch_facebook_profile(social_page.username)
                else:
                    results["details"].append({
                        "social_page_id": social_page.id,
                        "username": social_page.username,
                        "platform": social_page.platform,
                        "status": "error",
                        "message": f"Unsupported platform: {social_page.platform}"
                    })
                    results["failed"] += 1
                    continue
                
                if not profile_data or 'error' in profile_data:
                    error_msg = profile_data.get('message', 'Unknown error') if profile_data else 'Failed to fetch profile data'
                    results["details"].append({
                        "social_page_id": social_page.id,
                        "username": social_page.username,
                        "platform": social_page.platform,
                        "status": "error",
                        "message": error_msg
                    })
                    results["failed"] += 1
                    continue
                
                # Extract and save recent posts
                posts_count = 0
                if 'recent_media' in profile_data and profile_data['recent_media']:
                    posts_count = SocialMediaService.save_recent_posts(
                        social_page.id, 
                        profile_data['recent_media'], 
                        social_page.platform
                    )
                
                # Update the social_page data too
                updated_social_page = SocialMediaService.save_social_page_data(profile_data)
                
                if posts_count > 0:
                    results["details"].append({
                        "social_page_id": social_page.id,
                        "username": social_page.username,
                        "platform": social_page.platform,
                        "status": "success",
                        "posts_fetched": posts_count
                    })
                    results["successful"] += 1
                else:
                    results["details"].append({
                        "social_page_id": social_page.id,
                        "username": social_page.username,
                        "platform": social_page.platform,
                        "status": "warning",
                        "message": "No posts were found or saved"
                    })
                    results["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing social_page {social_page.id}: {str(e)}")
                results["details"].append({
                    "social_page_id": social_page.id,
                    "username": social_page.username,
                    "platform": social_page.platform,
                    "status": "error",
                    "message": str(e)
                })
                results["failed"] += 1
                continue
                
        # Return summary of results
        return jsonify({
            "status": "success",
            "message": f"Processed {len(social_pages)} social_pages: {results['successful']} successful, {results['failed']} failed",
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in batch fetch posts: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return jsonify({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500