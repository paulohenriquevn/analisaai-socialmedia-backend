"""Routes for updating influencer data."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging
from datetime import datetime

from app.extensions import db
from app.models.influencer import Influencer, Category, InfluencerMetric
from app.api.social_media import bp
from app.services.engagement_service import EngagementService

logger = logging.getLogger(__name__)

@bp.route('/influencer/<int:influencer_id>', methods=['PUT'])
@jwt_required()
def update_influencer(influencer_id):
    """Update details for an influencer."""
    user_id = get_jwt_identity()
    
    # Find the influencer
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404
    
    # Validate the data
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update the influencer data
    if 'full_name' in data:
        influencer.full_name = data['full_name']
    
    if 'bio' in data:
        influencer.bio = data['bio']
    
    if 'profile_image' in data:
        influencer.profile_image = data['profile_image']
    
    # Track if metrics-related fields were updated
    metrics_updated = False
    
    if 'followers_count' in data:
        influencer.followers_count = data['followers_count']
        metrics_updated = True
    
    if 'following_count' in data:
        influencer.following_count = data['following_count']
        metrics_updated = True
    
    if 'posts_count' in data:
        influencer.posts_count = data['posts_count']
        metrics_updated = True
    
    if 'engagement_rate' in data:
        influencer.engagement_rate = data['engagement_rate']
        metrics_updated = True
    
    # Handle categories
    if 'categories' in data and isinstance(data['categories'], list):
        categories = []
        for category_name in data['categories']:
            # Look up or create each category
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name, description=f"Category for {category_name}")
                db.session.add(category)
            categories.append(category)
        influencer.categories = categories
    
    # Save changes
    db.session.commit()
    logger.info(f"Updated influencer {influencer.id} - {influencer.username}")
    
    # Update metrics if metric-related fields were changed
    engagement_metrics_result = None
    if metrics_updated:
        try:
            # Update the InfluencerMetric record for today
            today = datetime.utcnow().date()
            
            # Check if we already have metrics for today
            existing_metric = InfluencerMetric.query.filter_by(
                influencer_id=influencer.id,
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
                metric = InfluencerMetric(
                    influencer_id=influencer.id,
                    date=today,
                    followers=influencer.followers_count,
                    engagement=influencer.engagement_rate,
                    posts=influencer.posts_count,
                    likes=data.get('likes', 0),
                    comments=data.get('comments', 0),
                    shares=data.get('shares', 0),
                    views=data.get('views', 0)
                )
                db.session.add(metric)
            
            db.session.commit()
            logger.info(f"Updated metrics for influencer {influencer.id} - {influencer.username}")
            
            # Recalculate engagement metrics using EngagementService
            engagement_metrics_result = EngagementService.calculate_engagement_metrics(influencer.id)
            if engagement_metrics_result:
                logger.info(f"Successfully calculated engagement metrics for influencer {influencer.id}")
            else:
                logger.warning(f"Failed to calculate engagement metrics for influencer {influencer.id}")
                
            # Also calculate reach metrics
            reach_metrics_result = None
            try:
                from app.services.reach_service import ReachService
                reach_metrics_result = ReachService.calculate_reach_metrics(influencer.id, user_id)
                if reach_metrics_result:
                    logger.info(f"Successfully calculated reach metrics for influencer {influencer.id}")
                else:
                    logger.warning(f"Failed to calculate reach metrics for influencer {influencer.id}")
            except Exception as e:
                logger.error(f"Error calculating reach metrics for influencer {influencer.id}: {str(e)}")
                
            # Calculate growth metrics
            growth_metrics_result = None
            try:
                from app.services.growth_service import GrowthService
                growth_metrics_result = GrowthService.calculate_growth_metrics(influencer.id)
                if growth_metrics_result:
                    logger.info(f"Successfully calculated growth metrics for influencer {influencer.id}")
                else:
                    logger.warning(f"Failed to calculate growth metrics for influencer {influencer.id}")
            except Exception as e:
                logger.error(f"Error calculating growth metrics for influencer {influencer.id}: {str(e)}")
                
            # Calculate relevance score (after all other metrics)
            score_metrics_result = None
            try:
                from app.services.score_service import ScoreService
                score_metrics_result = ScoreService.calculate_relevance_score(influencer.id)
                if score_metrics_result:
                    logger.info(f"Successfully calculated relevance score for influencer {influencer.id}")
                else:
                    logger.warning(f"Failed to calculate relevance score for influencer {influencer.id}")
            except Exception as e:
                logger.error(f"Error calculating relevance score for influencer {influencer.id}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error updating metrics for influencer {influencer.id}: {str(e)}")
            # Don't block the influencer update if metrics update fails
    
    # Prepare the response
    response = {
        "message": "Influencer updated successfully",
        "influencer": {
            "id": influencer.id,
            "username": influencer.username,
            "full_name": influencer.full_name,
            "platform": influencer.platform,
            "profile_url": influencer.profile_url,
            "profile_image": influencer.profile_image,
            "bio": influencer.bio,
            "followers_count": influencer.followers_count,
            "following_count": influencer.following_count,
            "posts_count": influencer.posts_count,
            "engagement_rate": influencer.engagement_rate,
            "social_score": influencer.social_score,
            "relevance_score": influencer.relevance_score,
            "categories": [c.name for c in influencer.categories]
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
        
        # Also update the influencer's relevance_score in the response
        response["influencer"]["relevance_score"] = influencer.relevance_score
    
    return jsonify(response)