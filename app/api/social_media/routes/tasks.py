"""
Routes for managing background tasks and asynchronous operations.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.models import SocialPage
from app.services import task_queue_service
from app.services.social_media_service import SocialMediaService
from app.services.engagement_service import EngagementService
from app.services.reach_service import ReachService
from app.services.growth_service import GrowthService
from app.services.score_service import ScoreService

# Create blueprint
bp = Blueprint('tasks', __name__)
logger = logging.getLogger(__name__)

# Helper functions for background tasks
def sync_social_page_data(social_page_id, user_id=None):
    """
    Synchronize an social_page's data from social media platforms.
    
    Args:
        social_page_id: The ID of the social_page to sync
        user_id: Optional user ID to use for API auth
        
    Returns:
        dict: Result of the sync operation
    """
    logger.info(f"Starting sync for social_page {social_page_id}")
    
    try:
        # Create minimal Flask app just for database context - no blueprints or routes
        from flask import Flask
        from app.config import config
        from app.extensions import db
        import os
        
        config_name = os.environ.get('FLASK_ENV', 'development')
        minimal_app = Flask('minimal_app')
        minimal_app.config.from_object(config[config_name])
        db.init_app(minimal_app)
        
        # Use app context for database operations
        with minimal_app.app_context():
            # Get the social_page
            from app.models import SocialPage
            social_page = SocialPage.query.get(social_page_id)
            if not social_page:
                logger.error(f"social_page {social_page_id} not found")
                return {"status": "error", "message": f"social_page {social_page_id} not found"}
            
            platform = social_page.platform
            username = social_page.username
        
            logger.info(f"Syncing {platform} data for {username}")
            
            # Fetch profile data from the appropriate platform
            profile_data = None
            from app.services.social_media_service import SocialMediaService
            if platform == 'instagram':
                profile_data = SocialMediaService.fetch_instagram_profile(user_id, username)
            elif platform == 'facebook':
                profile_data = SocialMediaService.fetch_facebook_profile(user_id, username)
            elif platform == 'tiktok':
                profile_data = SocialMediaService.fetch_tiktok_profile(user_id, username)
            else:
                logger.warning(f"Unsupported platform: {platform}")
                return {"status": "error", "message": f"Unsupported platform: {platform}"}
            
            if not profile_data or 'error' in profile_data:
                error_msg = profile_data.get('message', 'Failed to fetch profile data') if profile_data else 'Failed to fetch profile data'
                logger.error(f"Error fetching {platform} data for {username}: {error_msg}")
                return {"status": "error", "message": error_msg}
            
            # Save the updated profile data
            updated_social_page = SocialMediaService.save_social_page_data(profile_data)
            if not updated_social_page:
                logger.error(f"Failed to save profile data for {username}")
                return {"status": "error", "message": "Failed to save profile data"}
            
            # Save posts
            posts_count = 0
            if 'recent_media' in profile_data and profile_data['recent_media']:
                posts_count = SocialMediaService.save_recent_posts(
                    social_page_id,
                    profile_data['recent_media'],
                    platform
                )
                logger.info(f"Saved {posts_count} posts for {username}")
            
            # Update metrics
            metrics_results = {}
            
            try:
                from app.services.engagement_service import EngagementService
                engagement_metrics = EngagementService.calculate_engagement_metrics(social_page_id)
                metrics_results['engagement'] = "success" if engagement_metrics else "failed"
            except Exception as e:
                logger.error(f"Error calculating engagement metrics for {username}: {str(e)}")
                metrics_results['engagement'] = "error"
            
            try:
                from app.services.reach_service import ReachService
                reach_metrics = ReachService.calculate_reach_metrics(social_page_id, user_id)
                metrics_results['reach'] = "success" if reach_metrics else "failed"
            except Exception as e:
                logger.error(f"Error calculating reach metrics for {username}: {str(e)}")
                metrics_results['reach'] = "error"
            
            try:
                from app.services.growth_service import GrowthService
                growth_metrics = GrowthService.calculate_growth_metrics(social_page_id)
                metrics_results['growth'] = "success" if growth_metrics else "failed"
            except Exception as e:
                logger.error(f"Error calculating growth metrics for {username}: {str(e)}")
                metrics_results['growth'] = "error"
            
            try:
                from app.services.score_service import ScoreService
                score = ScoreService.calculate_relevance_score(social_page_id)
                metrics_results['score'] = "success" if score else "failed"
            except Exception as e:
                logger.error(f"Error calculating score metrics for {username}: {str(e)}")
                metrics_results['score'] = "error"
            
            # Fetch the most up-to-date social_page data for the response
            updated_social_page = SocialPage.query.get(social_page_id)
            
            return {
                "status": "success",
                "social_page": {
                    "id": social_page_id,
                    "username": username,
                    "platform": platform,
                    "followers_count": updated_social_page.followers_count,
                    "posts_count": updated_social_page.posts_count,
                    "engagement_rate": updated_social_page.engagement_rate,
                    "social_score": updated_social_page.social_score,
                    "relevance_score": updated_social_page.relevance_score
                },
                "posts_saved": posts_count,
                "metrics_results": metrics_results
            }
    
    except Exception as e:
        logger.error(f"Error syncing social_page {social_page_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}

def sync_all_social_pages(user_id=None, platform=None, limit=None):
    """
    Sync data for all social_page or a filtered subset.
    
    Args:
        user_id: Optional user ID to use for API auth
        platform: Optional platform filter
        limit: Optional limit on number of social_page to process
        
    Returns:
        dict: Results of the sync operation
    """
    logger.info(f"Starting sync for all social_page. Platform: {platform}, Limit: {limit}")
    
    try:
        # Create minimal Flask app just for database context - no blueprints or routes
        from flask import Flask
        from app.config import config
        from app.extensions import db
        import os
        
        config_name = os.environ.get('FLASK_ENV', 'development')
        minimal_app = Flask('minimal_app')
        minimal_app.config.from_object(config[config_name])
        db.init_app(minimal_app)
        
        # Use app context for database operations
        with minimal_app.app_context():
            # Build query to get social_page
            from app.models import SocialPage
            query = SocialPage.query
            
            # Filter by platform if specified
            if platform:
                query = query.filter_by(platform=platform)
            
            # Order by last updated (oldest first)
            query = query.order_by(SocialPage.updated_at.asc())
            
            # Apply limit if specified
            if limit and isinstance(limit, int) and limit > 0:
                query = query.limit(limit)
            
            # Get all matching social_page
            social_pages = query.all()
            
            # Convert to a list of dictionaries to avoid app context issues
            social_page_data = [
                {"id": infl.id, "username": infl.username, "platform": infl.platform}
                for infl in social_pages
            ]
        
        if not social_page_data:
            logger.info("No social_page found matching criteria")
            return {
                "status": "warning", 
                "message": "No social_page found matching criteria"
            }
        
        logger.info(f"Found {len(social_page_data)} social_page to sync")
        
        # Process each social_page_data
        results = {
            "total": len(social_page_data),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for social_page in social_page_data:
            try:
                # Sync individual social_page
                sync_result = sync_social_page_data(social_page["id"], user_id)
                
                # Add result to details
                result_entry = {
                    "social_page_id": social_page["id"],
                    "username": social_page["username"],
                    "platform": social_page["platform"],
                    "status": sync_result.get('status')
                }
                
                if sync_result.get('status') == 'success':
                    result_entry["followers_count"] = sync_result.get('social_page', {}).get('followers_count')
                    result_entry["posts_saved"] = sync_result.get('posts_saved')
                    results["successful"] += 1
                else:
                    result_entry["error"] = sync_result.get('message')
                    results["failed"] += 1
                
                results["details"].append(result_entry)
                
            except Exception as e:
                logger.error(f"Error processing social_page {social_page['id']}: {str(e)}")
                results["details"].append({
                    "social_page_id": social_page["id"],
                    "username": social_page["username"],
                    "platform": social_page["platform"],
                    "status": "error",
                    "error": str(e)
                })
                results["failed"] += 1
        
        return {
            "status": "success",
            "message": f"Processed {results['total']} social_pages: {results['successful']} successful, {results['failed']} failed",
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error in sync_all_social_page: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "status": "error", 
            "message": f"Failed to sync social_page: {str(e)}"
        }

def get_social_page_for_sync(limit=5):
    """
    Get a list of social_page to update, ordered by update time.
    This function creates its own app context for database access.
    
    Args:
        limit: Maximum number of social_page to return
        
    Returns:
        list: List of social_page IDs to update
    """
    # Create minimal Flask app just for database context - no blueprints or routes
    from flask import Flask
    from app.config import config
    from app.extensions import db
    from app.models import SocialPage
    import os
    
    config_name = os.environ.get('FLASK_ENV', 'development')
    minimal_app = Flask('minimal_app')
    minimal_app.config.from_object(config[config_name])
    db.init_app(minimal_app)
    
    # Get social_page ordered by update time (oldest first)
    with minimal_app.app_context():
        social_pages = SocialPage.query.order_by(SocialPage.updated_at.asc()).limit(limit).all()
        return [social_page.id for social_page in social_pages]

def process_login_data_sync(user_id):
    """
    Process data synchronization after user login.
    This function updates social_page data in the background after user login.
    
    Args:
        user_id: The ID of the user who logged in
        
    Returns:
        dict: Summary of the sync operation
    """
    logger.info(f"Processing background data sync after login for user {user_id}")
    
    try:
        # Create minimal Flask app just for database context - no blueprints or routes
        from flask import Flask
        from app.config import config
        from app.extensions import db
        from app.models import SocialPage
        import os
        
        social_page_ids = []
        try:
            # Create minimal app for database access
            config_name = os.environ.get('FLASK_ENV', 'development')
            minimal_app = Flask('minimal_app')
            minimal_app.config.from_object(config[config_name])
            db.init_app(minimal_app)
            
            # Query for social_page
            with minimal_app.app_context():
                social_pages = SocialPage.query.order_by(SocialPage.updated_at.asc()).limit(5).all()
                social_page_ids = [social_page.id for social_page in social_pages]
        except Exception as e:
            logger.error(f"Error querying social_page: {str(e)}")
            social_page_ids = []
        
        if not social_page_ids:
            logger.info("No social_page found to update after login")
            return {
                "status": "success",
                "message": "No social_page found to update",
                "updated": 0
            }
        
        logger.info(f"Found {len(social_page_ids)} social_page to update after login")
        
        updated_count = 0
        for social_page_id in social_page_ids:
            try:
                # Update the social_pages data
                result = sync_social_page_data(social_page_id, user_id)
                if result.get('status') == 'success':
                    updated_count += 1
            except Exception as e:
                logger.error(f"Error updating social_pages {social_page_id} after login: {str(e)}")
                # Continue with other social_page even if this one fails
        
        return {
            "status": "success",
            "message": f"Updated {updated_count} of {len(social_page_ids)} social_page after login",
            "updated": updated_count
        }
    
    except Exception as e:
        logger.error(f"Error in post-login data sync: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Failed to update data after login: {str(e)}"
        }

# API routes
@bp.route('/async/sync-social-page/<int:social_page_id>', methods=['POST'])
@jwt_required()
def async_sync_social_page(social_page_id):
    """
    API endpoint to asynchronously synchronize data for a specific social_page.
    
    This creates a background task and returns immediately with a task ID that
    can be used to check the status later.
    """
    user_id = get_jwt_identity()
    logger.info(f"User {user_id} requested async sync for social_page {social_page_id}")
    
    # Check if social_page exists
    social_page = SocialPage.query.get(social_page_id)
    if not social_page:
        return jsonify({
            "status": "error",
            "message": f"social_page with ID {social_page_id} not found"
        }), 404
    
    # Start background task
    task_id = task_queue_service.enqueue_task(
        sync_social_page_data,
        args=[social_page_id, user_id],
        description=f"Sync {social_page.platform} social_page: {social_page.username}"
    )
    
    return jsonify({
        "status": "accepted",
        "message": "Sync task created and running in background",
        "task_id": task_id,
        "social_page": {
            "id": social_page.id,
            "username": social_page.username,
            "platform": social_page.platform
        }
    }), 202

@bp.route('/async/sync-all', methods=['POST'])
@jwt_required()
def async_sync_all():
    """
    API endpoint to asynchronously synchronize data for all social_page or a filtered subset.
    
    This creates a background task and returns immediately with a task ID that
    can be used to check the status later.
    """
    user_id = get_jwt_identity()
    logger.info(f"User {user_id} requested async sync for all social_page")
    
    # Get filter parameters from request
    data = request.json or {}
    platform = data.get('platform')
    limit = data.get('limit')
    
    # Start background task
    task_id = task_queue_service.enqueue_task(
        sync_all_social_pages,
        args=[user_id, platform, limit],
        description=f"Sync all social_page: platform={platform}, limit={limit}"
    )
    
    return jsonify({
        "status": "accepted",
        "message": "Sync task created and running in background",
        "task_id": task_id,
        "filters": {
            "platform": platform,
            "limit": limit
        }
    }), 202

@bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """
    Get the status of a background task.
    """
    task_status = task_queue_service.get_task_status(task_id)
    
    return jsonify(task_status)

@bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    Get information about all tasks.
    """
    # Get information about the queue
    queue_info = task_queue_service.get_queue_info()
    
    # Get statuses of most recent tasks
    # By default, we only show a limited number of tasks to avoid large responses
    limit = request.args.get('limit', type=int, default=20)
    
    # Get statuses of tasks, sorted by created_at (newest first)
    task_statuses = []
    for task_id in sorted(
        task_queue_service.task_status.keys(), 
        key=lambda x: task_queue_service.task_status[x].created_at if hasattr(task_queue_service.task_status[x], 'created_at') else datetime.min,
        reverse=True
    )[:limit]:
        task_status = task_queue_service.get_task_status(task_id)
        task_statuses.append(task_status)
    
    return jsonify({
        "queue_info": queue_info,
        "tasks": task_statuses
    })

@bp.route('/tasks/queue-info', methods=['GET'])
@jwt_required()
def get_queue_info():
    """
    Get information about the task queue.
    """
    queue_info = task_queue_service.get_queue_info()
    
    return jsonify(queue_info)

@bp.route('/tasks/cleanup', methods=['POST'])
@jwt_required()
def cleanup_tasks():
    """
    Clean up old completed tasks.
    """
    data = request.json or {}
    max_age_hours = data.get('max_age_hours', 24)
    
    removed_count = task_queue_service.cleanup_old_tasks(max_age_hours)
    
    return jsonify({
        "status": "success",
        "message": f"Removed {removed_count} old tasks",
        "removed_count": removed_count
    })

# Test endpoint that doesn't require authentication for testing
@bp.route('/test', methods=['GET'])
def test_task_queue():
    """
    Test endpoint to verify the task queue is working.
    This endpoint doesn't require authentication for easy testing.
    """
    # Define a simple test task function
    def test_task(name):
        import time
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Running test task for {name}")
        time.sleep(2)  # Simulate work
        logger.info(f"Test task for {name} completed")
        return f"Hello, {name}!"
    
    # Enqueue a test task
    task_id = task_queue_service.enqueue_task(
        test_task,
        args=["World"],
        description="Test task"
    )
    
    # Get queue information
    queue_info = task_queue_service.get_queue_info()
    
    return jsonify({
        "status": "success",
        "message": "Test task enqueued successfully",
        "task_id": task_id,
        "queue_info": queue_info
    })