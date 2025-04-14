"""
Service for calculating and processing reach metrics for influencers.
"""
import logging
from datetime import datetime, date, timedelta
from app.extensions import db
from app.models.influencer import Influencer
from app.models.reach import InfluencerReach
from app.services.oauth_service import get_token

logger = logging.getLogger(__name__)

class ReachService:
    """Service for calculating and tracking reach metrics."""
    
    @staticmethod
    def calculate_reach_metrics(influencer_id, user_id=None):
        """
        Calculate reach metrics for a specific influencer.
        
        Args:
            influencer_id: ID of the influencer to calculate metrics for
            user_id: Optional user ID to get account tokens
            
        Returns:
            dict: The calculated reach metrics or None if error
        """
        try:
            logger.info(f"Calculating reach metrics for influencer ID: {influencer_id}")
            
            # Get the influencer
            influencer = Influencer.query.get(influencer_id)
            if not influencer:
                logger.error(f"Influencer with ID {influencer_id} not found")
                return None
            
            # Metrics structure to be populated
            metrics = {
                'influencer_id': influencer_id,
                'date': date.today(),
                'timestamp': datetime.utcnow(),
                'impressions': 0,
                'reach': 0,
                'story_views': 0,
                'profile_views': 0,
                'stories_count': 0,
                'story_engagement_rate': 0.0,
                'story_exit_rate': 0.0,
                'story_completion_rate': 0.0,
                'avg_watch_time': 0.0,
                'audience_growth': 0.0
            }
            
            # Try to get reach metrics based on platform
            platform = influencer.platform
            username = influencer.username
            
            # Platform-specific data collection
            if platform == 'instagram':
                instagram_metrics = ReachService._fetch_instagram_reach_metrics(influencer_id, username, user_id)
                if instagram_metrics:
                    metrics.update(instagram_metrics)
            elif platform == 'facebook':
                facebook_metrics = ReachService._fetch_facebook_reach_metrics(influencer_id, username, user_id)
                if facebook_metrics:
                    metrics.update(facebook_metrics)
            elif platform == 'tiktok':
                tiktok_metrics = ReachService._fetch_tiktok_reach_metrics(influencer_id, username, user_id)
                if tiktok_metrics:
                    metrics.update(tiktok_metrics)
            else:
                logger.warning(f"Unsupported platform: {platform}")
            
            # Calculate audience growth if we have previous metrics
            previous_reach = InfluencerReach.query.filter(
                InfluencerReach.influencer_id == influencer_id,
                InfluencerReach.date < metrics['date']
            ).order_by(InfluencerReach.date.desc()).first()
            
            if previous_reach and previous_reach.reach > 0:
                current_reach = metrics['reach'] or 0
                metrics['audience_growth'] = ((current_reach - previous_reach.reach) / previous_reach.reach) * 100 if previous_reach.reach > 0 else 0
            
            # Save the metrics
            result = ReachService.save_reach_metrics(metrics)
            if result:
                logger.info(f"Successfully saved reach metrics for influencer {influencer_id}")
                return metrics
            else:
                logger.error(f"Failed to save reach metrics for influencer {influencer_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error calculating reach metrics for influencer {influencer_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def _fetch_instagram_reach_metrics(influencer_id, username, user_id=None):
        """
        Fetch reach metrics from Instagram API.
        
        This method tries to use official Instagram API first, and falls back to 
        estimates based on available data if API access is not available.
        """
        # Get the influencer first
        influencer = Influencer.query.get(influencer_id)
        if not influencer:
            logger.error(f"Influencer with ID {influencer_id} not found")
            return None
        try:
            # Try to use official API if we have user_id and tokens
            if user_id:
                from app.services.oauth_service import get_token
                token_data = get_token(user_id, 'instagram')
                
                if token_data:
                    # Use Instagram Insights API to get reach data
                    import requests
                    
                    # First get the Instagram business account ID
                    access_token = token_data['access_token']
                    
                    # Get user's Instagram business accounts through Facebook Graph API
                    accounts_url = "https://graph.facebook.com/v16.0/me/accounts"
                    params = {
                        'access_token': access_token,
                        'fields': 'instagram_business_account,name,id'
                    }
                    
                    response = requests.get(accounts_url, params=params, timeout=10)
                    if response.status_code != 200:
                        logger.warning(f"Failed to get Instagram business accounts: {response.text}")
                        return None
                    
                    accounts_data = response.json()
                    
                    # Find Instagram business account associated with this username
                    instagram_account_id = None
                    for page in accounts_data.get('data', []):
                        if 'instagram_business_account' in page:
                            ig_id = page['instagram_business_account']['id']
                            
                            # Check if this is the right account
                            ig_url = f"https://graph.facebook.com/v16.0/{ig_id}"
                            params = {
                                'fields': 'username',
                                'access_token': access_token
                            }
                            
                            ig_response = requests.get(ig_url, params=params, timeout=10)
                            if ig_response.status_code == 200:
                                ig_data = ig_response.json()
                                if ig_data.get('username') == username:
                                    instagram_account_id = ig_id
                                    break
                    
                    if not instagram_account_id:
                        logger.warning(f"Could not find Instagram business account for username: {username}")
                        return None
                    
                    # Now get insights data for the account
                    insights_url = f"https://graph.facebook.com/v16.0/{instagram_account_id}/insights"
                    params = {
                        'metric': 'impressions,reach,profile_views',
                        'period': 'day',
                        'access_token': access_token
                    }
                    
                    insights_response = requests.get(insights_url, params=params, timeout=10)
                    if insights_response.status_code != 200:
                        logger.warning(f"Failed to get Instagram insights: {insights_response.text}")
                        return None
                    
                    insights_data = insights_response.json()
                    
                    # Extract metrics
                    impressions = 0
                    reach = 0
                    profile_views = 0
                    
                    for metric in insights_data.get('data', []):
                        if metric.get('name') == 'impressions':
                            impressions = metric.get('values', [{}])[0].get('value', 0)
                        elif metric.get('name') == 'reach':
                            reach = metric.get('values', [{}])[0].get('value', 0)
                        elif metric.get('name') == 'profile_views':
                            profile_views = metric.get('values', [{}])[0].get('value', 0)
                    
                    # Now get story insights
                    stories_url = f"https://graph.facebook.com/v16.0/{instagram_account_id}/stories"
                    params = {
                        'access_token': access_token,
                        'fields': 'id,media_type,media_url,timestamp'
                    }
                    
                    stories_response = requests.get(stories_url, params=params, timeout=10)
                    stories_data = stories_response.json() if stories_response.status_code == 200 else {'data': []}
                    
                    stories_count = len(stories_data.get('data', []))
                    story_views = 0
                    total_exits = 0
                    total_completions = 0
                    
                    # Get insights for each story
                    for story in stories_data.get('data', []):
                        story_id = story.get('id')
                        if story_id:
                            story_insights_url = f"https://graph.facebook.com/v16.0/{story_id}/insights"
                            params = {
                                'metric': 'exits,replies,impressions',
                                'access_token': access_token
                            }
                            
                            story_insights_response = requests.get(story_insights_url, params=params, timeout=10)
                            if story_insights_response.status_code == 200:
                                story_insights = story_insights_response.json()
                                
                                for metric in story_insights.get('data', []):
                                    if metric.get('name') == 'impressions':
                                        story_views += metric.get('values', [{}])[0].get('value', 0)
                                    elif metric.get('name') == 'exits':
                                        total_exits += metric.get('values', [{}])[0].get('value', 0)
                    
                    # Calculate rates
                    story_exit_rate = (total_exits / story_views) * 100 if story_views > 0 else 0
                    story_completion_rate = ((story_views - total_exits) / story_views) * 100 if story_views > 0 else 0
                    story_engagement_rate = 0  # Need replies and taps data to calculate this accurately
                    
                    return {
                        'impressions': impressions,
                        'reach': reach,
                        'story_views': story_views,
                        'profile_views': profile_views,
                        'stories_count': stories_count,
                        'story_exit_rate': story_exit_rate,
                        'story_completion_rate': story_completion_rate,
                        'story_engagement_rate': story_engagement_rate
                    }
            
            # Fallback: Estimate reach based on followers and engagement
            # This is a simplified estimation and not as accurate as API data
            from app.models.engagement import InfluencerEngagement
            
            # Get latest engagement metrics
            engagement = InfluencerEngagement.query.filter_by(
                influencer_id=influencer_id
            ).order_by(InfluencerEngagement.date.desc()).first()
            
            if engagement and influencer.followers_count > 0:
                # Estimate reach as a percentage of followers 
                # (typically 20-30% of followers see a post)
                estimated_reach = int(influencer.followers_count * 0.25)
                
                # Estimate impressions (typically 1.5-2x reach)
                estimated_impressions = int(estimated_reach * 1.8)
                
                # Estimate story views (typically 10-15% of followers)
                estimated_story_views = int(influencer.followers_count * 0.12)
                
                # Estimate profile views (typically 5-10% of impressions)
                estimated_profile_views = int(estimated_impressions * 0.08)
                
                return {
                    'impressions': estimated_impressions,
                    'reach': estimated_reach,
                    'story_views': estimated_story_views,
                    'profile_views': estimated_profile_views,
                    'stories_count': 0,  # We don't know how many stories were posted
                    'story_exit_rate': 0.0,
                    'story_completion_rate': 0.0,
                    'story_engagement_rate': 0.0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Instagram reach metrics: {str(e)}")
            return None
    
    @staticmethod
    def _fetch_facebook_reach_metrics(influencer_id, username, user_id=None):
        """
        Fetch reach metrics from Facebook API or estimate them.
        """
        # Get the influencer first
        influencer = Influencer.query.get(influencer_id)
        if not influencer:
            logger.error(f"Influencer with ID {influencer_id} not found")
            return None
        try:
            # Try to use official API if we have user_id and tokens
            if user_id:
                from app.services.oauth_service import get_token
                token_data = get_token(user_id, 'facebook')
                
                if token_data:
                    # Implement Facebook API calls for reach metrics
                    # This would be similar to the Instagram implementation but using
                    # Facebook-specific endpoints
                    pass
            
            # Fallback: Estimate reach based on followers and engagement
            # This is a simplified estimation and not as accurate as API data
            from app.models.engagement import InfluencerEngagement
            
            # Get latest engagement metrics
            engagement = InfluencerEngagement.query.filter_by(
                influencer_id=influencer_id
            ).order_by(InfluencerEngagement.date.desc()).first()
            
            if engagement and influencer.followers_count > 0:
                # Facebook typically has lower organic reach than Instagram
                # Estimate reach as a percentage of followers (typically 5-10% of followers see a post)
                estimated_reach = int(influencer.followers_count * 0.08)
                
                # Estimate impressions (typically 1.3-1.5x reach)
                estimated_impressions = int(estimated_reach * 1.4)
                
                # Facebook doesn't have stories in the same way, but we can estimate story-like metrics
                # based on video views or other temporary content
                estimated_story_views = int(influencer.followers_count * 0.05)
                
                # Estimate profile views (typically 2-5% of impressions)
                estimated_profile_views = int(estimated_impressions * 0.03)
                
                return {
                    'impressions': estimated_impressions,
                    'reach': estimated_reach,
                    'story_views': estimated_story_views,
                    'profile_views': estimated_profile_views,
                    'stories_count': 0,
                    'story_exit_rate': 0.0,
                    'story_completion_rate': 0.0,
                    'story_engagement_rate': 0.0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Facebook reach metrics: {str(e)}")
            return None
    
    @staticmethod
    def _fetch_tiktok_reach_metrics(influencer_id, username, user_id=None):
        """
        Fetch reach metrics from TikTok API or estimate them.
        """
        # Get the influencer first
        influencer = Influencer.query.get(influencer_id)
        if not influencer:
            logger.error(f"Influencer with ID {influencer_id} not found")
            return None
        try:
            # Try to use official API if we have user_id and tokens
            if user_id:
                from app.services.oauth_service import get_token
                token_data = get_token(user_id, 'tiktok')
                
                if token_data:
                    # Implement TikTok API calls for reach metrics
                    # TikTok's API is more limited than Facebook/Instagram
                    pass
            
            # Fallback: Estimate reach based on followers and engagement
            # This is a simplified estimation and not as accurate as API data
            from app.models.engagement import InfluencerEngagement
            
            # Get latest engagement metrics
            engagement = InfluencerEngagement.query.filter_by(
                influencer_id=influencer_id
            ).order_by(InfluencerEngagement.date.desc()).first()
            
            if engagement and influencer.followers_count > 0:
                # TikTok has higher reach due to the For You Page algorithm
                # Estimate reach as a percentage of followers (typically 30-100% of followers + additional)
                follower_base = influencer.followers_count
                estimated_reach = int(follower_base * 0.8)  # 80% of followers
                
                # Add estimated non-follower reach from FYP
                non_follower_reach = int(follower_base * 0.5)  # 50% additional reach
                total_estimated_reach = estimated_reach + non_follower_reach
                
                # Estimate impressions (typically 1.2-1.5x reach on TikTok)
                estimated_impressions = int(total_estimated_reach * 1.3)
                
                # TikTok doesn't have stories, but we can use video views as an analog
                video_views = engagement.video_views if hasattr(engagement, 'video_views') else 0
                if video_views == 0:
                    video_views = int(total_estimated_reach * 0.7)  # 70% of reach watch videos
                
                # Estimate profile views (typically 5-15% of impressions)
                estimated_profile_views = int(estimated_impressions * 0.1)
                
                return {
                    'impressions': estimated_impressions,
                    'reach': total_estimated_reach,
                    'story_views': video_views,  # Using video views instead of story views
                    'profile_views': estimated_profile_views,
                    'stories_count': 0,  # TikTok doesn't have stories
                    'story_exit_rate': 0.0,
                    'story_completion_rate': 0.0,
                    'story_engagement_rate': 0.0,
                    'avg_watch_time': engagement.avg_watch_time if hasattr(engagement, 'avg_watch_time') else 15.0  # Default 15 seconds
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching TikTok reach metrics: {str(e)}")
            return None
    
    @staticmethod
    def save_reach_metrics(metrics_data):
        """
        Save reach metrics to the database.
        
        Args:
            metrics_data: Dict containing reach metrics
            
        Returns:
            InfluencerReach: Saved reach metrics record or None if error
        """
        try:
            # Check if metrics for this influencer and date already exist
            existing = InfluencerReach.query.filter_by(
                influencer_id=metrics_data['influencer_id'],
                date=metrics_data['date']
            ).first()
            
            if existing:
                # Update existing metrics
                for key, value in metrics_data.items():
                    if key != 'influencer_id' and key != 'date' and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                reach_record = existing
            else:
                # Create new metrics record
                reach_record = InfluencerReach(**metrics_data)
                db.session.add(reach_record)
            
            db.session.commit()
            return reach_record
            
        except Exception as e:
            logger.error(f"Error saving reach metrics: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_reach_metrics(influencer_id, start_date=None, end_date=None):
        """
        Get reach metrics for an influencer within a date range.
        
        Args:
            influencer_id: ID of the influencer
            start_date: Start date for metrics (optional)
            end_date: End date for metrics (optional)
            
        Returns:
            list: List of reach metrics or empty list if none found
        """
        query = InfluencerReach.query.filter_by(influencer_id=influencer_id)
        
        if start_date:
            query = query.filter(InfluencerReach.date >= start_date)
        
        if end_date:
            query = query.filter(InfluencerReach.date <= end_date)
        
        # Order by date (most recent first)
        query = query.order_by(InfluencerReach.date.desc())
        
        return query.all()
    
    @staticmethod
    def calculate_all_influencers_reach():
        """
        Calculate reach metrics for all influencers.
        
        Returns:
            dict: Summary of the calculation results
        """
        influencers = Influencer.query.all()
        results = {
            'total': len(influencers),
            'success': 0,
            'failed': 0
        }
        
        for influencer in influencers:
            try:
                metrics = ReachService.calculate_reach_metrics(influencer.id)
                if metrics:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception:
                results['failed'] += 1
        
        return results