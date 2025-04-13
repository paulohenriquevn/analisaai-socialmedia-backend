"""
Analytics service for calculating metrics and insights.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.extensions import db
from app.models import Influencer, InfluencerMetric
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for calculating and analyzing social media metrics."""
    
    @staticmethod
    def get_influencer_growth(influencer_id, time_range=30):
        """
        Calculate growth metrics for an influencer over a specified time range.
        
        Args:
            influencer_id: ID of the influencer
            time_range: Number of days to analyze (default: 30)
            
        Returns:
            dict: Growth metrics
        """
        try:
            # Get influencer
            influencer = Influencer.query.get(influencer_id)
            if not influencer:
                return None
            
            # Get metrics for the time range
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=time_range)
            
            metrics = InfluencerMetric.query.filter(
                InfluencerMetric.influencer_id == influencer_id,
                InfluencerMetric.date >= start_date,
                InfluencerMetric.date <= end_date
            ).order_by(InfluencerMetric.date).all()
            
            if not metrics or len(metrics) < 2:
                return {
                    'followers_growth': 0,
                    'followers_growth_percent': 0,
                    'engagement_growth': 0,
                    'engagement_growth_percent': 0,
                    'posts_growth': 0,
                    'insufficient_data': True
                }
            
            # Get first and last metrics
            first_metric = metrics[0]
            last_metric = metrics[-1]
            
            # Calculate growth
            followers_growth = last_metric.followers - first_metric.followers
            followers_growth_percent = (followers_growth / first_metric.followers * 100) if first_metric.followers else 0
            
            engagement_growth = last_metric.engagement - first_metric.engagement
            engagement_growth_percent = (engagement_growth / first_metric.engagement * 100) if first_metric.engagement else 0
            
            posts_growth = last_metric.posts - first_metric.posts
            
            # Calculate daily metrics for the chart
            dates = [(start_date + timedelta(days=i)).isoformat() for i in range(time_range + 1)]
            followers_data = []
            engagement_data = []
            
            # Create a dict for quick lookup
            metrics_by_date = {metric.date.isoformat(): metric for metric in metrics}
            
            # Fill in the data points, using the previous value for missing dates
            last_followers = first_metric.followers
            last_engagement = first_metric.engagement
            
            for date in dates:
                if date in metrics_by_date:
                    metric = metrics_by_date[date]
                    last_followers = metric.followers
                    last_engagement = metric.engagement
                
                followers_data.append({
                    'date': date,
                    'value': last_followers
                })
                
                engagement_data.append({
                    'date': date,
                    'value': last_engagement
                })
            
            return {
                'followers_growth': followers_growth,
                'followers_growth_percent': followers_growth_percent,
                'engagement_growth': engagement_growth,
                'engagement_growth_percent': engagement_growth_percent,
                'posts_growth': posts_growth,
                'followers_chart': followers_data,
                'engagement_chart': engagement_data,
                'insufficient_data': False
            }
            
        except Exception as e:
            logger.error(f"Error calculating influencer growth: {str(e)}")
            return None
    
    @staticmethod
    def get_platform_benchmarks(platform, category=None):
        """
        Calculate benchmark metrics for a specific platform and category.
        
        Args:
            platform: Platform to analyze (instagram, tiktok, facebook)
            category: Optional category filter
            
        Returns:
            dict: Benchmark metrics
        """
        try:
            # Build query
            query = Influencer.query.filter_by(platform=platform)
            
            # Apply category filter if provided
            if category:
                query = query.join(Influencer.categories).filter_by(name=category)
            
            # Get influencers
            influencers = query.all()
            
            if not influencers:
                return {
                    'average_followers': 0,
                    'average_engagement': 0,
                    'percentiles': {
                        'followers': {
                            'p10': 0, 'p25': 0, 'p50': 0, 'p75': 0, 'p90': 0
                        },
                        'engagement': {
                            'p10': 0, 'p25': 0, 'p50': 0, 'p75': 0, 'p90': 0
                        }
                    }
                }
            
            # Extract metrics
            followers = np.array([i.followers_count for i in influencers])
            engagement = np.array([i.engagement_rate for i in influencers])
            
            # Calculate averages
            avg_followers = np.mean(followers)
            avg_engagement = np.mean(engagement)
            
            # Calculate percentiles
            followers_percentiles = {
                'p10': np.percentile(followers, 10),
                'p25': np.percentile(followers, 25),
                'p50': np.percentile(followers, 50),
                'p75': np.percentile(followers, 75),
                'p90': np.percentile(followers, 90)
            }
            
            engagement_percentiles = {
                'p10': np.percentile(engagement, 10),
                'p25': np.percentile(engagement, 25),
                'p50': np.percentile(engagement, 50),
                'p75': np.percentile(engagement, 75),
                'p90': np.percentile(engagement, 90)
            }
            
            return {
                'average_followers': avg_followers,
                'average_engagement': avg_engagement,
                'percentiles': {
                    'followers': followers_percentiles,
                    'engagement': engagement_percentiles
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating platform benchmarks: {str(e)}")
            return None
    
    @staticmethod
    def get_influencer_recommendations(user_id, filters=None):
        """
        Get influencer recommendations based on user preferences and filters.
        
        Args:
            user_id: User ID to get recommendations for
            filters: Optional filters (platform, category, min_followers, etc.)
            
        Returns:
            list: Recommended influencers
        """
        try:
            # Build query
            query = Influencer.query
            
            # Apply filters if provided
            if filters:
                if 'platform' in filters:
                    query = query.filter_by(platform=filters['platform'])
                
                if 'category' in filters:
                    query = query.join(Influencer.categories).filter_by(name=filters['category'])
                
                if 'min_followers' in filters:
                    query = query.filter(Influencer.followers_count >= filters['min_followers'])
                
                if 'min_engagement' in filters:
                    query = query.filter(Influencer.engagement_rate >= filters['min_engagement'])
            
            # Order by social score and limit to top 10
            influencers = query.order_by(Influencer.social_score.desc()).limit(10).all()
            
            # Format response
            recommendations = []
            for influencer in influencers:
                categories = [category.name for category in influencer.categories]
                
                recommendations.append({
                    'id': influencer.id,
                    'username': influencer.username,
                    'full_name': influencer.full_name,
                    'platform': influencer.platform,
                    'profile_image': influencer.profile_image,
                    'followers_count': influencer.followers_count,
                    'engagement_rate': influencer.engagement_rate,
                    'social_score': influencer.social_score,
                    'categories': categories
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting influencer recommendations: {str(e)}")
            return []