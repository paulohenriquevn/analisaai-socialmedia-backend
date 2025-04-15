"""
Service for calculating and processing relevance scores for influencers.
"""
import logging
from datetime import datetime, date, timedelta
import numpy as np
from app.extensions import db
from app.models import (
    SocialPage,
    SocialPageEngagement,
    SocialPageReach,
    SocialPageGrowth,
    SocialPageScore,
)

logger = logging.getLogger(__name__)

class ScoreService:
    """Service for calculating and tracking relevance scores."""
    
    @staticmethod
    def calculate_relevance_score(social_page_id):
        """
        Calculate relevance score for a specific influencer.
        
        Args:
            social_page_id: ID of the influencer to calculate score for
            
        Returns:
            dict: The calculated score metrics or None if error
        """
        try:
            logger.info(f"Calculating relevance score for influencer ID: {social_page_id}")
            
            # Get the influencer
            influencer = SocialPage.query.get(social_page_id)
            if not influencer:
                logger.error(f"Influencer with ID {social_page_id} not found")
                return None
            
            # Calculate component scores
            current_date = date.today()
            
            # Calculate engagement score
            engagement_score = ScoreService.calculate_engagement_score(social_page_id, current_date)
            
            # Calculate reach score
            reach_score = ScoreService.calculate_reach_score(social_page_id, current_date)
            
            # Calculate growth score
            growth_score = ScoreService.calculate_growth_score(social_page_id, current_date)
            
            # Calculate consistency score
            consistency_score = ScoreService.calculate_consistency_score(social_page_id, current_date)
            
            # Calculate audience quality score
            audience_quality_score = ScoreService.calculate_audience_quality_score(social_page_id, current_date)
            
            # Define weights for the overall score calculation
            # These weights can be adjusted based on business priorities
            engagement_weight = 0.3
            reach_weight = 0.25
            growth_weight = 0.25
            consistency_weight = 0.1
            audience_quality_weight = 0.1
            
            # Calculate the overall score (weighted average)
            overall_score = (
                engagement_score * engagement_weight +
                reach_score * reach_weight +
                growth_score * growth_weight +
                consistency_score * consistency_weight +
                audience_quality_score * audience_quality_weight
            )
            
            # Ensure the overall score is between 0 and 100
            overall_score = min(max(overall_score, 0), 100)
            
            # Create score metrics data
            score_metrics = {
                'social_page_id': social_page_id,
                'date': current_date,
                'overall_score': overall_score,
                'engagement_score': engagement_score,
                'reach_score': reach_score,
                'growth_score': growth_score,
                'consistency_score': consistency_score,
                'audience_quality_score': audience_quality_score,
                'engagement_weight': engagement_weight,
                'reach_weight': reach_weight,
                'growth_weight': growth_weight,
                'consistency_weight': consistency_weight,
                'audience_quality_weight': audience_quality_weight
            }
            
            # Save the score metrics
            result = ScoreService.save_score_metrics(score_metrics)
            if result:
                # Update the influencer's current relevance score
                influencer.relevance_score = overall_score
                db.session.commit()
                logger.info(f"Updated influencer {social_page_id} with new relevance score: {overall_score}")
                
                logger.info(f"Successfully saved relevance score for influencer {social_page_id}")
                return score_metrics
            else:
                logger.error(f"Failed to save relevance score for influencer {social_page_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error calculating relevance score for influencer {social_page_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def calculate_engagement_score(social_page_id, current_date=None):
        """
        Calculate engagement component score for an influencer.
        
        This score is based on engagement metrics like engagement rate,
        likes, comments, and interaction rates.
        """
        if current_date is None:
            current_date = date.today()
        
        # Get latest engagement metrics
        engagement = SocialPageEngagement.query.filter_by(
            social_page_id=social_page_id
        ).order_by(SocialPageEngagement.date.desc()).first()
        
        if not engagement:
            # No engagement data, return a baseline score
            return 50.0
        
        # Get influencer for followers count
        influencer = SocialPage.query.get(social_page_id)
        if not influencer:
            return 50.0
        
        # Calculate engagement score based on multiple factors
        
        # 1. Engagement rate (0-100)
        # Industry average engagement rates vary by platform:
        # - Instagram: ~1-3%
        # - TikTok: ~5-15%
        # - Facebook: ~0.5-1%
        platform = influencer.platform
        engagement_rate = engagement.engagement_rate or 0
        
        if platform == 'instagram':
            # Scale Instagram engagement (0-10% maps to 0-100)
            normalized_engagement_rate = min(engagement_rate * 10, 100)
        elif platform == 'tiktok':
            # Scale TikTok engagement (0-20% maps to 0-100)
            normalized_engagement_rate = min(engagement_rate * 5, 100)
        elif platform == 'facebook':
            # Scale Facebook engagement (0-5% maps to 0-100)
            normalized_engagement_rate = min(engagement_rate * 20, 100)
        else:
            # Default scaling (0-10% maps to 0-100)
            normalized_engagement_rate = min(engagement_rate * 10, 100)
        
        # 2. Likes per post relative to followers (0-100)
        followers = influencer.followers_count or 1
        avg_likes = engagement.avg_likes_per_post or 0
        likes_to_followers_ratio = (avg_likes / followers) * 100
        
        # Scale this ratio (0-5% maps to 0-100)
        normalized_likes_ratio = min(likes_to_followers_ratio * 20, 100)
        
        # 3. Comments per post relative to followers (0-100)
        avg_comments = engagement.avg_comments_per_post or 0
        comments_to_followers_ratio = (avg_comments / followers) * 100
        
        # Scale this ratio (0-0.5% maps to 0-100 since comments are rarer)
        normalized_comments_ratio = min(comments_to_followers_ratio * 200, 100)
        
        # 4. Content interaction score based on total engagement metrics
        total_engagement = (
            engagement.total_likes or 0 +
            (engagement.total_comments or 0) * 3 +  # Comments weighted higher
            (engagement.total_shares or 0) * 5      # Shares weighted highest
        )
        
        # Scale based on followers (we expect more total engagement for larger accounts)
        follower_scale_factor = np.log10(max(followers, 100)) / np.log10(100000)
        expected_engagement = followers * follower_scale_factor * 0.05
        interaction_score = min((total_engagement / max(expected_engagement, 1)) * 100, 100)
        
        # Final engagement score is a weighted combination of these factors
        engagement_score = (
            normalized_engagement_rate * 0.4 +
            normalized_likes_ratio * 0.2 +
            normalized_comments_ratio * 0.2 +
            interaction_score * 0.2
        )
        
        return engagement_score
    
    @staticmethod
    def calculate_reach_score(social_page_id, current_date=None):
        """
        Calculate reach component score for an influencer.
        
        This score is based on reach metrics like impressions, profile views,
        and story views.
        """
        if current_date is None:
            current_date = date.today()
        
        # Get latest reach metrics
        reach = SocialPageReach.query.filter_by(
            social_page_id=social_page_id
        ).order_by(SocialPageReach.date.desc()).first()
        
        if not reach:
            # No reach data, return a baseline score
            return 50.0
        
        # Get influencer for followers count
        influencer = SocialPage.query.get(social_page_id)
        if not influencer:
            return 50.0
        
        followers = influencer.followers_count or 1
        
        # Calculate reach score based on multiple factors
        
        # 1. Reach to followers ratio (0-100)
        # Reach should be at least equal to followers count, ideally 2-5x
        reach_value = reach.reach or 0
        reach_to_followers_ratio = (reach_value / followers)
        
        # Scale this ratio (0-3x maps to 0-100)
        normalized_reach_ratio = min(reach_to_followers_ratio * 33.33, 100)
        
        # 2. Impressions to followers ratio (0-100)
        # Impressions are typically 1.5-3x reach
        impressions = reach.impressions or 0
        impressions_to_followers_ratio = (impressions / followers)
        
        # Scale this ratio (0-5x maps to 0-100)
        normalized_impressions_ratio = min(impressions_to_followers_ratio * 20, 100)
        
        # 3. Story views to followers ratio (0-100)
        story_views = reach.story_views or 0
        story_views_to_followers_ratio = (story_views / followers)
        
        # Scale this ratio (0-0.5x maps to 0-100)
        normalized_story_views_ratio = min(story_views_to_followers_ratio * 200, 100)
        
        # 4. Profile views to impressions ratio (0-100)
        # This measures how often profile views result from impressions
        profile_views = reach.profile_views or 0
        profile_views_to_impressions_ratio = (profile_views / max(impressions, 1)) * 100
        
        # Scale this ratio (0-10% maps to 0-100)
        normalized_profile_views_ratio = min(profile_views_to_impressions_ratio * 10, 100)
        
        # Final reach score is a weighted combination of these factors
        reach_score = (
            normalized_reach_ratio * 0.3 +
            normalized_impressions_ratio * 0.3 +
            normalized_story_views_ratio * 0.2 +
            normalized_profile_views_ratio * 0.2
        )
        
        return reach_score
    
    @staticmethod
    def calculate_growth_score(social_page_id, current_date=None):
        """
        Calculate growth component score for an influencer.
        
        This score is based on growth metrics like new followers,
        growth rates, and retention.
        """
        if current_date is None:
            current_date = date.today()
        
        # Get latest growth metrics
        growth = SocialPageGrowth.query.filter_by(
            social_page_id=social_page_id
        ).order_by(SocialPageGrowth.date.desc()).first()
        
        if not growth:
            # No growth data, return a baseline score
            return 50.0
        
        # Get influencer for followers count
        influencer = SocialPage.query.get(social_page_id)
        if not influencer:
            return 50.0
        
        followers = influencer.followers_count or 1
        
        # Calculate growth score based on multiple factors
        
        # 1. Daily growth rate (0-100)
        # 1% daily growth is excellent, 0.1% is average
        daily_growth_rate = growth.daily_growth_rate or 0
        
        # Scale this ratio (0-1% maps to 0-100)
        normalized_daily_growth = min(daily_growth_rate * 100, 100)
        
        # 2. Weekly growth rate (0-100)
        # 5% weekly growth is excellent, 0.5% is average
        weekly_growth_rate = growth.weekly_growth_rate or 0
        
        # Scale this ratio (0-5% maps to 0-100)
        normalized_weekly_growth = min(weekly_growth_rate * 20, 100)
        
        # 3. New followers relative to follower base (0-100)
        new_followers_daily = growth.new_followers_daily or 0
        new_followers_ratio = (new_followers_daily / followers) * 100
        
        # Scale this ratio (0-1% maps to 0-100)
        normalized_new_followers = min(new_followers_ratio * 100, 100)
        
        # 4. Retention rate (0-100)
        # 95% retention is average, 99% is excellent
        retention_rate = growth.retention_rate or 0
        
        # Scale this (90-100% maps to 0-100)
        normalized_retention = max(min((retention_rate - 90) * 10, 100), 0)
        
        # 5. Growth velocity and acceleration
        growth_velocity = growth.growth_velocity or 0
        growth_acceleration = growth.growth_acceleration or 0
        
        # Velocity: Higher is better, scale based on followers
        # For smaller accounts, gaining 10 followers/day might be excellent
        # For larger accounts, hundreds/day might be expected
        follower_scale = np.log10(max(followers, 100))
        expected_velocity = follower_scale * 0.01 * followers
        normalized_velocity = min((growth_velocity / max(expected_velocity, 1)) * 100, 100)
        
        # Acceleration: Positive is good (account is growing faster over time)
        normalized_acceleration = 50 + (np.tanh(growth_acceleration * 10) * 50)
        
        # Final growth score is a weighted combination of these factors
        growth_score = (
            normalized_daily_growth * 0.15 +
            normalized_weekly_growth * 0.15 +
            normalized_new_followers * 0.15 +
            normalized_retention * 0.2 +
            normalized_velocity * 0.2 +
            normalized_acceleration * 0.15
        )
        
        return growth_score
    
    @staticmethod
    def calculate_consistency_score(social_page_id, current_date=None):
        """
        Calculate consistency component score for an influencer.
        
        This score is based on posting frequency, consistency over time,
        and content regularity.
        """
        if current_date is None:
            current_date = date.today()
        
        # For a full implementation, we would need to analyze posting patterns
        # over time, which requires post timestamps data
        # As a simplification, we'll estimate based on available data
        
        # Get the influencer
        influencer = SocialPage.query.get(social_page_id)
        if not influencer:
            return 50.0
        
        # Get engagement metrics as they have some post data
        engagements = SocialPageEngagement.query.filter_by(
            social_page_id=social_page_id
        ).order_by(SocialPageEngagement.date.desc()).limit(30).all()
        
        if not engagements:
            # No engagement data, use a simple estimate based on post count
            posts_count = influencer.posts_count or 0
            account_age_days = max((current_date - influencer.created_at.date()).days, 1)
            
            # Average posts per day
            avg_posts_per_day = posts_count / account_age_days
            
            # For most platforms, 1 post/day is considered good consistency
            normalized_posting_frequency = min(avg_posts_per_day * 100, 100)
            
            # Return simple consistency score
            return normalized_posting_frequency
        
        # If we have engagement data, we can do a more sophisticated analysis
        # Check for consistency in posts_count over time
        post_counts = [e.posts_count for e in engagements if e.posts_count is not None]
        if len(post_counts) >= 2:
            # Calculate the average number of new posts per day
            post_diffs = [post_counts[i] - post_counts[i+1] for i in range(len(post_counts)-1)]
            avg_new_posts = sum(max(diff, 0) for diff in post_diffs) / len(post_diffs)
            
            # Calculate consistency score based on variance in posting
            if avg_new_posts > 0:
                variance = np.var(post_diffs) / avg_new_posts
                posting_consistency = 100 * np.exp(-variance)  # Higher variance = lower consistency
            else:
                posting_consistency = 0  # No new posts = no consistency
        else:
            # Not enough data points, use simple estimate
            posts_count = influencer.posts_count or 0
            account_age_days = max((current_date - influencer.created_at.date()).days, 1)
            avg_posts_per_day = posts_count / account_age_days
            posting_consistency = min(avg_posts_per_day * 100, 100)
        
        return posting_consistency
    
    @staticmethod
    def calculate_audience_quality_score(social_page_id, current_date=None):
        """
        Calculate audience quality component score for an influencer.
        
        This score is based on indicators of audience authenticity,
        engagement quality, and demographic relevance.
        """
        if current_date is None:
            current_date = date.today()
        
        # For a full implementation, we would need audience demographic data,
        # authenticity indicators, and engagement quality metrics
        # As a simplification, we'll estimate based on engagement patterns
        
        # Get the influencer
        influencer = SocialPage.query.get(social_page_id)
        if not influencer:
            return 50.0
        
        # Get latest engagement metrics
        engagement = SocialPageEngagement.query.filter_by(
            social_page_id=social_page_id
        ).order_by(SocialPageEngagement.date.desc()).first()
        
        if not engagement:
            # No engagement data, return a baseline score
            return 50.0
        
        # Calculate audience quality based on engagement patterns
        
        followers = influencer.followers_count or 1
        following = influencer.following_count or 0
        
        # 1. Comments to likes ratio (higher ratio = higher quality engagement)
        likes = engagement.total_likes or 1
        comments = engagement.total_comments or 0
        comments_to_likes_ratio = (comments / likes) * 100
        
        # Scale this ratio (0-5% maps to 0-100)
        normalized_comments_ratio = min(comments_to_likes_ratio * 20, 100)
        
        # 2. Followers to following ratio (higher ratio typically = higher quality audience)
        if following > 0:
            followers_to_following_ratio = followers / following
            # Scale this ratio (0-10 maps to 0-100)
            normalized_followers_ratio = min(followers_to_following_ratio * 10, 100)
        else:
            normalized_followers_ratio = 80  # Default for accounts that don't follow others
        
        # 3. Engagement consistency (engagement rate should be consistent for authentic audiences)
        engagement_rate = engagement.engagement_rate or 0
        
        # Get historical engagement rates
        historical_engagements = SocialPageEngagement.query.filter_by(
            social_page_id=social_page_id
        ).order_by(SocialPageEngagement.date.desc()).limit(10).all()
        
        if len(historical_engagements) > 1:
            # Calculate variance in engagement rates
            engagement_rates = [e.engagement_rate for e in historical_engagements if e.engagement_rate is not None]
            if engagement_rates:
                mean_rate = sum(engagement_rates) / len(engagement_rates)
                if mean_rate > 0:
                    variance = sum((rate - mean_rate)**2 for rate in engagement_rates) / len(engagement_rates)
                    normalized_variance = variance / (mean_rate**2)
                    engagement_consistency = 100 * np.exp(-normalized_variance * 10)  # Lower variance = higher consistency
                else:
                    engagement_consistency = 0  # No engagement = no consistency
            else:
                engagement_consistency = 50  # Default
        else:
            engagement_consistency = 50  # Not enough data points
        
        # Final audience quality score is a weighted combination of these factors
        audience_quality_score = (
            normalized_comments_ratio * 0.4 +
            normalized_followers_ratio * 0.3 +
            engagement_consistency * 0.3
        )
        
        return audience_quality_score
    
    @staticmethod
    def save_score_metrics(score_metrics):
        """
        Save score metrics to the database.
        
        Args:
            score_metrics: Dict containing score metrics
            
        Returns:
            InfluencerScore: Saved score metrics record or None if error
        """
        try:
            # Check if metrics for this influencer and date already exist
            existing = SocialPageScore.query.filter_by(
                social_page_id=score_metrics['social_page_id'],
                date=score_metrics['date']
            ).first()
            
            if existing:
                # Update existing metrics
                for key, value in score_metrics.items():
                    if key != 'social_page_id' and key != 'date' and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                score_record = existing
            else:
                # Create new metrics record
                score_record = SocialPageScore(**score_metrics)
                db.session.add(score_record)
            
            db.session.commit()
            return score_record
            
        except Exception as e:
            logger.error(f"Error saving score metrics: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_score_metrics(social_page_id, start_date=None, end_date=None):
        """
        Get score metrics for an influencer within a date range.
        
        Args:
            social_page_id: ID of the influencer
            start_date: Start date for metrics (optional)
            end_date: End date for metrics (optional)
            
        Returns:
            list: List of score metrics or empty list if none found
        """
        query = SocialPageScore.query.filter_by(social_page_id=social_page_id)
        
        if start_date:
            query = query.filter(SocialPageScore.date >= start_date)
        
        if end_date:
            query = query.filter(SocialPageScore.date <= end_date)
        
        # Order by date (most recent first)
        query = query.order_by(SocialPageScore.date.desc())
        
        return query.all()
    
    @staticmethod
    def calculate_all_influencers_scores():
        """
        Calculate relevance scores for all influencers.
        
        Returns:
            dict: Summary of the calculation results
        """
        influencers = SocialPage.query.all()
        results = {
            'total': len(influencers),
            'success': 0,
            'failed': 0
        }
        
        for influencer in influencers:
            try:
                metrics = ScoreService.calculate_relevance_score(influencer.id)
                if metrics:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception:
                results['failed'] += 1
        
        return results