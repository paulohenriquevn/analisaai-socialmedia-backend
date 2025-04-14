"""
Routes for managing background tasks and asynchronous operations.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.models import Influencer
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
def sync_influencer_data(influencer_id, user_id=None):
    """
    Synchronize an influencer's data from social media platforms.
    
    Args:
        influencer_id: The ID of the influencer to sync
        user_id: Optional user ID to use for API auth
        
    Returns:
        dict: Result of the sync operation
    """
    logger.info(f"Starting sync for influencer {influencer_id}")
    
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
            # Get the influencer
            from app.models import Influencer
            influencer = Influencer.query.get(influencer_id)
            if not influencer:
                logger.error(f"Influencer {influencer_id} not found")
                return {"status": "error", "message": f"Influencer {influencer_id} not found"}
            
            platform = influencer.platform
            username = influencer.username
        
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
            updated_influencer = SocialMediaService.save_influencer_data(profile_data)
            if not updated_influencer:
                logger.error(f"Failed to save profile data for {username}")
                return {"status": "error", "message": "Failed to save profile data"}
            
            # Save posts
            posts_count = 0
            if 'recent_media' in profile_data and profile_data['recent_media']:
                posts_count = SocialMediaService.save_recent_posts(
                    influencer_id,
                    profile_data['recent_media'],
                    platform
                )
                logger.info(f"Saved {posts_count} posts for {username}")
            
            # Update metrics
            metrics_results = {}
            
            try:
                from app.services.engagement_service import EngagementService
                engagement_metrics = EngagementService.calculate_engagement_metrics(influencer_id)
                metrics_results['engagement'] = "success" if engagement_metrics else "failed"
            except Exception as e:
                logger.error(f"Error calculating engagement metrics for {username}: {str(e)}")
                metrics_results['engagement'] = "error"
            
            try:
                from app.services.reach_service import ReachService
                reach_metrics = ReachService.calculate_reach_metrics(influencer_id, user_id)
                metrics_results['reach'] = "success" if reach_metrics else "failed"
            except Exception as e:
                logger.error(f"Error calculating reach metrics for {username}: {str(e)}")
                metrics_results['reach'] = "error"
            
            try:
                from app.services.growth_service import GrowthService
                growth_metrics = GrowthService.calculate_growth_metrics(influencer_id)
                metrics_results['growth'] = "success" if growth_metrics else "failed"
            except Exception as e:
                logger.error(f"Error calculating growth metrics for {username}: {str(e)}")
                metrics_results['growth'] = "error"
            
            try:
                from app.services.score_service import ScoreService
                score = ScoreService.calculate_relevance_score(influencer_id)
                metrics_results['score'] = "success" if score else "failed"
            except Exception as e:
                logger.error(f"Error calculating score metrics for {username}: {str(e)}")
                metrics_results['score'] = "error"
            
            # Fetch the most up-to-date influencer data for the response
            updated_influencer = Influencer.query.get(influencer_id)
            
            return {
                "status": "success",
                "influencer": {
                    "id": influencer_id,
                    "username": username,
                    "platform": platform,
                    "followers_count": updated_influencer.followers_count,
                    "posts_count": updated_influencer.posts_count,
                    "engagement_rate": updated_influencer.engagement_rate,
                    "social_score": updated_influencer.social_score,
                    "relevance_score": updated_influencer.relevance_score
                },
                "posts_saved": posts_count,
                "metrics_results": metrics_results
            }
    
    except Exception as e:
        logger.error(f"Error syncing influencer {influencer_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}

def sync_all_influencers(user_id=None, platform=None, limit=None):
    """
    Sync data for all influencers or a filtered subset.
    
    Args:
        user_id: Optional user ID to use for API auth
        platform: Optional platform filter
        limit: Optional limit on number of influencers to process
        
    Returns:
        dict: Results of the sync operation
    """
    logger.info(f"Starting sync for all influencers. Platform: {platform}, Limit: {limit}")
    
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
            # Build query to get influencers
            from app.models import Influencer
            query = Influencer.query
            
            # Filter by platform if specified
            if platform:
                query = query.filter_by(platform=platform)
            
            # Order by last updated (oldest first)
            query = query.order_by(Influencer.updated_at.asc())
            
            # Apply limit if specified
            if limit and isinstance(limit, int) and limit > 0:
                query = query.limit(limit)
            
            # Get all matching influencers
            influencers = query.all()
            
            # Convert to a list of dictionaries to avoid app context issues
            influencer_data = [
                {"id": infl.id, "username": infl.username, "platform": infl.platform}
                for infl in influencers
            ]
        
        if not influencer_data:
            logger.info("No influencers found matching criteria")
            return {
                "status": "warning", 
                "message": "No influencers found matching criteria"
            }
        
        logger.info(f"Found {len(influencer_data)} influencers to sync")
        
        # Process each influencer
        results = {
            "total": len(influencer_data),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for influencer in influencer_data:
            try:
                # Sync individual influencer
                sync_result = sync_influencer_data(influencer["id"], user_id)
                
                # Add result to details
                result_entry = {
                    "influencer_id": influencer["id"],
                    "username": influencer["username"],
                    "platform": influencer["platform"],
                    "status": sync_result.get('status')
                }
                
                if sync_result.get('status') == 'success':
                    result_entry["followers_count"] = sync_result.get('influencer', {}).get('followers_count')
                    result_entry["posts_saved"] = sync_result.get('posts_saved')
                    results["successful"] += 1
                else:
                    result_entry["error"] = sync_result.get('message')
                    results["failed"] += 1
                
                results["details"].append(result_entry)
                
            except Exception as e:
                logger.error(f"Error processing influencer {influencer['id']}: {str(e)}")
                results["details"].append({
                    "influencer_id": influencer["id"],
                    "username": influencer["username"],
                    "platform": influencer["platform"],
                    "status": "error",
                    "error": str(e)
                })
                results["failed"] += 1
        
        return {
            "status": "success",
            "message": f"Processed {results['total']} influencers: {results['successful']} successful, {results['failed']} failed",
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error in sync_all_influencers: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "status": "error", 
            "message": f"Failed to sync influencers: {str(e)}"
        }

def get_influencers_for_sync(limit=5):
    """
    Get a list of influencers to update, ordered by update time.
    This function creates its own app context for database access.
    
    Args:
        limit: Maximum number of influencers to return
        
    Returns:
        list: List of influencer IDs to update
    """
    # Create minimal Flask app just for database context - no blueprints or routes
    from flask import Flask
    from app.config import config
    from app.extensions import db
    from app.models import Influencer
    import os
    
    config_name = os.environ.get('FLASK_ENV', 'development')
    minimal_app = Flask('minimal_app')
    minimal_app.config.from_object(config[config_name])
    db.init_app(minimal_app)
    
    # Get influencers ordered by update time (oldest first)
    with minimal_app.app_context():
        influencers = Influencer.query.order_by(Influencer.updated_at.asc()).limit(limit).all()
        return [influencer.id for influencer in influencers]

def process_login_data_sync(user_id):
    """
    Process data synchronization after user login.
    This function updates influencer data in the background after user login.
    
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
        from app.models import Influencer
        import os
        
        influencer_ids = []
        try:
            # Create minimal app for database access
            config_name = os.environ.get('FLASK_ENV', 'development')
            minimal_app = Flask('minimal_app')
            minimal_app.config.from_object(config[config_name])
            db.init_app(minimal_app)
            
            # Query for influencers
            with minimal_app.app_context():
                influencers = Influencer.query.order_by(Influencer.updated_at.asc()).limit(5).all()
                influencer_ids = [influencer.id for influencer in influencers]
        except Exception as e:
            logger.error(f"Error querying influencers: {str(e)}")
            influencer_ids = []
        
        if not influencer_ids:
            logger.info("No influencers found to update after login")
            return {
                "status": "success",
                "message": "No influencers found to update",
                "updated": 0
            }
        
        logger.info(f"Found {len(influencer_ids)} influencers to update after login")
        
        updated_count = 0
        for influencer_id in influencer_ids:
            try:
                # Update the influencer data
                result = sync_influencer_data(influencer_id, user_id)
                if result.get('status') == 'success':
                    updated_count += 1
            except Exception as e:
                logger.error(f"Error updating influencer {influencer_id} after login: {str(e)}")
                # Continue with other influencers even if this one fails
        
        return {
            "status": "success",
            "message": f"Updated {updated_count} of {len(influencer_ids)} influencers after login",
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
@bp.route('/async/sync-influencer/<int:influencer_id>', methods=['POST'])
@jwt_required()
def async_sync_influencer(influencer_id):
    """
    API endpoint to asynchronously synchronize data for a specific influencer.
    
    This creates a background task and returns immediately with a task ID that
    can be used to check the status later.
    """
    user_id = get_jwt_identity()
    logger.info(f"User {user_id} requested async sync for influencer {influencer_id}")
    
    # Check if influencer exists
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return jsonify({
            "status": "error",
            "message": f"Influencer with ID {influencer_id} not found"
        }), 404
    
    # Start background task
    task_id = task_queue_service.enqueue_task(
        sync_influencer_data,
        args=[influencer_id, user_id],
        description=f"Sync {influencer.platform} influencer: {influencer.username}"
    )
    
    return jsonify({
        "status": "accepted",
        "message": "Sync task created and running in background",
        "task_id": task_id,
        "influencer": {
            "id": influencer.id,
            "username": influencer.username,
            "platform": influencer.platform
        }
    }), 202

@bp.route('/async/sync-all', methods=['POST'])
@jwt_required()
def async_sync_all():
    """
    API endpoint to asynchronously synchronize data for all influencers or a filtered subset.
    
    This creates a background task and returns immediately with a task ID that
    can be used to check the status later.
    """
    user_id = get_jwt_identity()
    logger.info(f"User {user_id} requested async sync for all influencers")
    
    # Get filter parameters from request
    data = request.json or {}
    platform = data.get('platform')
    limit = data.get('limit')
    
    # Start background task
    task_id = task_queue_service.enqueue_task(
        sync_all_influencers,
        args=[user_id, platform, limit],
        description=f"Sync all influencers: platform={platform}, limit={limit}"
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