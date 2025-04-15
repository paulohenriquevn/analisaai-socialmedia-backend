"""Routes for syncing social media data."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.services.social_media_service import SocialMediaService
from app.models import SocialPage

# Create a separate blueprint for sync routes
bp_sync = Blueprint('social_media_sync', __name__)

# Import the main blueprint to register this blueprint
from app.api.social_media import bp

# Register this blueprint with the main blueprint
bp.register_blueprint(bp_sync)

logger = logging.getLogger(__name__)

@bp_sync.route('/sync-social-pages', methods=['POST'])
@jwt_required()
def sync_social_pages():
    """
    Manually trigger a sync of social_page data using Apify.
    This endpoint allows refreshing data for all or selected social_pages.
    """
    current_user_id = get_jwt_identity()
    
    # Get request parameters
    data = request.json or {}
    social_page_ids = data.get('social_page_ids', [])  # Optional list of specific social_page IDs to sync
    limit = data.get('limit', 100)  # Maximum number of social_pages to sync
    
    try:
        # Get social_pages to sync
        query = SocialPage.query
        
        # Filter by specific IDs if provided
        if social_page_ids:
            query = query.filter(SocialPage.id.in_(social_page_ids))
            
        # Order by last updated time (oldest first)
        query = query.order_by(SocialPage.updated_at.asc())
        
        # Apply limit
        social_pages = query.limit(limit).all()
        
        if not social_pages:
            return jsonify({
                "status": "error",
                "message": "No social_pages found to sync"
            }), 404
        
        # Track results
        results = {
            "total": len(social_pages),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        # Process all selected social_pages
        for social_page in social_pages:
            platform = social_page.platform
            username = social_page.username
            
            if not platform or not username:
                results["failed"] += 1
                results["details"].append({
                    "social_page_id": social_page.id,
                    "status": "failed",
                    "message": "Missing platform or username"
                })
                continue
                
            try:
                # Use Apify to fetch updated profile data
                profile_data = None
                
                if platform == 'instagram':
                    profile_data = SocialMediaService.fetch_instagram_profile(current_user_id, username)
                elif platform == 'facebook':
                    profile_data = SocialMediaService.fetch_facebook_profile(current_user_id, username)
                elif platform == 'tiktok':
                    profile_data = SocialMediaService.fetch_tiktok_profile(current_user_id, username)
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "social_page_id": social_page.id,
                        "platform": platform,
                        "username": username,
                        "status": "failed",
                        "message": f"Unsupported platform: {platform}"
                    })
                    continue
                    
                # Update the social_page data if successful
                if profile_data and 'error' not in profile_data:
                    updated_social_page = SocialMediaService.save_social_page_data(profile_data, current_user_id)
                    
                    # Calculate engagement and reach metrics
                    if updated_social_page:
                        try:
                            # Calculate engagement metrics
                            from app.services.engagement_service import EngagementService
                            engagement_metrics = EngagementService.calculate_engagement_metrics(updated_social_page.id)
                            logger.info(f"Calculated engagement metrics for {username} after sync")
                            
                            # Calculate reach metrics
                            from app.services.reach_service import ReachService
                            reach_metrics = ReachService.calculate_reach_metrics(updated_social_page.id, current_user_id)
                            logger.info(f"Calculated reach metrics for {username} after sync")
                            
                            # Calculate growth metrics
                            from app.services.growth_service import GrowthService
                            growth_metrics = GrowthService.calculate_growth_metrics(updated_social_page.id)
                            logger.info(f"Calculated growth metrics for {username} after sync")
                            
                            # Calculate relevance score (after all other metrics)
                            from app.services.score_service import ScoreService
                            score_metrics = ScoreService.calculate_relevance_score(updated_social_page.id)
                            logger.info(f"Calculated relevance score for {username} after sync")
                        except Exception as e:
                            logger.error(f"Error calculating metrics for {username}: {str(e)}")
                    
                    results["success"] += 1
                    results["details"].append({
                        "social_page_id": social_page.id,
                        "platform": platform,
                        "username": username,
                        "status": "success",
                        "followers": profile_data.get('followers_count', 0),
                        "engagement": profile_data.get('engagement_rate', 0)
                    })
                else:
                    error_msg = profile_data.get('message', 'Unknown error') if profile_data else 'Failed to fetch data'
                    results["failed"] += 1
                    results["details"].append({
                        "social_page_id": social_page.id,
                        "platform": platform,
                        "username": username,
                        "status": "failed",
                        "message": error_msg
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "social_page_id": social_page.id,
                    "platform": platform,
                    "username": username,
                    "status": "failed",
                    "message": str(e)
                })
        
        return jsonify({
            "status": "success",
            "message": f"Sync completed. {results['success']} succeeded, {results['failed']} failed",
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error syncing social_page: {str(e)}"
        }), 500

@bp_sync.route('/sync-social-page/<int:social_page_id>', methods=['POST'])
@jwt_required()
def sync_single_social_page(social_page_id):
    """
    Sync a single social_page by ID.
    """
    current_user_id = get_jwt_identity()
    
    try:
        # Get the social_page
        social_page = SocialPage.query.get(social_page_id)
        
        if not social_page:
            return jsonify({
                "status": "error",
                "message": f"social_page with ID {social_page_id} not found"
            }), 404
        
        platform = social_page.platform
        username = social_page.username
        
        if not platform or not username:
            return jsonify({
                "status": "error",
                "message": "social_page missing platform or username"
            }), 400
        
        # Use Apify to fetch updated profile data
        profile_data = None
        
        if platform == 'instagram':
            profile_data = SocialMediaService.fetch_instagram_profile(current_user_id, username)
        elif platform == 'facebook':
            profile_data = SocialMediaService.fetch_facebook_profile(current_user_id, username)
        elif platform == 'tiktok':
            profile_data = SocialMediaService.fetch_tiktok_profile(current_user_id, username)
        else:
            return jsonify({
                "status": "error",
                "message": f"Unsupported platform: {platform}"
            }), 400
        
        # Update the social_page data if successful
        if profile_data and 'error' not in profile_data:
            updated_social_page = SocialMediaService.save_social_page_data(profile_data, current_user_id)
            
            # Calculate metrics
            engagement_metrics_result = None
            reach_metrics_result = None
            
            if updated_social_page:
                try:
                    # Calculate engagement metrics
                    from app.services.engagement_service import EngagementService
                    engagement_metrics_result = EngagementService.calculate_engagement_metrics(updated_social_page.id)
                    logger.info(f"Calculated engagement metrics for {username} after sync")
                    
                    # Calculate reach metrics
                    from app.services.reach_service import ReachService
                    reach_metrics_result = ReachService.calculate_reach_metrics(updated_social_page.id, current_user_id)
                    logger.info(f"Calculated reach metrics for {username} after sync")
                    
                    # Calculate growth metrics
                    from app.services.growth_service import GrowthService
                    growth_metrics_result = GrowthService.calculate_growth_metrics(updated_social_page.id)
                    logger.info(f"Calculated growth metrics for {username} after sync")
                    
                    # Calculate relevance score (after all other metrics)
                    from app.services.score_service import ScoreService
                    score_metrics_result = ScoreService.calculate_relevance_score(updated_social_page.id)
                    logger.info(f"Calculated relevance score for {username} after sync")
                except Exception as e:
                    logger.error(f"Error calculating metrics for {username}: {str(e)}")
            
            # Prepare response
            response = {
                "status": "success",
                "message": f"Successfully synced {platform} data for {username}",
                "social_page": {
                    "id": updated_social_page.id,
                    "username": updated_social_page.username,
                    "platform": updated_social_page.platform,
                    "followers_count": updated_social_page.followers_count,
                    "engagement_rate": updated_social_page.engagement_rate,
                    "relevance_score": updated_social_page.relevance_score,
                    "updated_at": updated_social_page.updated_at.isoformat() if updated_social_page.updated_at else None
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
                
                # Update relevance score in social_page data
                response["social_page"]["relevance_score"] = updated_social_page.relevance_score
            
            return jsonify(response)
        else:
            error_msg = profile_data.get('message', 'Unknown error') if profile_data else 'Failed to fetch data'
            return jsonify({
                "status": "error",
                "message": f"Failed to sync social_page: {error_msg}"
            }), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error syncing social_page: {str(e)}"
        }), 500