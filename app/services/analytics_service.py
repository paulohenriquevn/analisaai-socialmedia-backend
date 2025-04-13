"""
Analytics service for calculating metrics and insights.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.extensions import db, cache
from app.models import Influencer, InfluencerMetric, SocialToken, User, Organization, Category
from sqlalchemy import func, desc
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
            
    @staticmethod
    @cache.memoize(timeout=300)  # Cache for 5 minutes
    def get_consolidated_metrics(user_id, timeframe='month'):
        """
        Get consolidated metrics across all social media platforms for a user.
        
        Args:
            user_id: User ID to get metrics for
            timeframe: Timeframe for metrics ('day', 'week', 'month', 'year')
            
        Returns:
            dict: Consolidated metrics with last update timestamp
        """
        try:
            # Calculate date range based on timeframe
            now = datetime.utcnow()
            if timeframe == 'day':
                start_date = now - timedelta(days=1)
            elif timeframe == 'week':
                start_date = now - timedelta(days=7)
            elif timeframe == 'year':
                start_date = now - timedelta(days=365)
            else:  # default to month
                start_date = now - timedelta(days=30)
            
            # Get user's social media connections
            user = User.query.get(user_id)
            if not user:
                return {
                    'error': 'User not found',
                    'last_updated': now.isoformat()
                }
            
            connected_platforms = []
            if user.facebook_id:
                connected_platforms.append('facebook')
            if user.instagram_id:
                connected_platforms.append('instagram')
            if user.tiktok_id:
                connected_platforms.append('tiktok')
                
            if not connected_platforms:
                return {
                    'platforms': [],
                    'total_followers': 0,
                    'total_engagement': 0,
                    'average_engagement_rate': 0,
                    'platform_metrics': {},
                    'top_performing_posts': [],
                    'growth_trend': [],
                    'last_updated': now.isoformat()
                }
            
            # Get metrics for each platform
            platform_metrics = {}
            total_followers = 0
            total_engagement = 0
            engagement_rates = []
            top_posts = []
            growth_data = []
            
            for platform in connected_platforms:
                # Query metrics data for this platform
                metrics = InfluencerMetric.query.join(Influencer).filter(
                    Influencer.platform == platform,
                    InfluencerMetric.date >= start_date.date()
                ).order_by(InfluencerMetric.date).all()
                
                if not metrics:
                    platform_metrics[platform] = {
                        'followers': 0,
                        'engagement': 0,
                        'engagement_rate': 0,
                        'posts': 0,
                        'likes': 0,
                        'comments': 0,
                        'shares': 0,
                        'views': 0
                    }
                    continue
                
                # Get the latest metrics
                latest_metric = metrics[-1]
                platform_followers = latest_metric.followers or 0
                platform_engagement = latest_metric.engagement or 0
                platform_posts = latest_metric.posts or 0
                platform_likes = latest_metric.likes or 0
                platform_comments = latest_metric.comments or 0
                platform_shares = latest_metric.shares or 0
                platform_views = latest_metric.views or 0
                
                # Calculate engagement rate
                engagement_rate = 0
                if platform_followers > 0:
                    engagement_rate = (platform_engagement / platform_followers) * 100
                    engagement_rates.append(engagement_rate)
                
                # Add to totals
                total_followers += platform_followers
                total_engagement += platform_engagement
                
                # Store platform metrics
                platform_metrics[platform] = {
                    'followers': platform_followers,
                    'engagement': platform_engagement,
                    'engagement_rate': engagement_rate,
                    'posts': platform_posts,
                    'likes': platform_likes,
                    'comments': platform_comments,
                    'shares': platform_shares,
                    'views': platform_views
                }
                
                # Add growth data points (weekly or monthly intervals)
                interval = max(1, len(metrics) // 5)  # At most 5 data points
                for i in range(0, len(metrics), interval):
                    if i + interval < len(metrics):
                        metric = metrics[i]
                        growth_data.append({
                            'date': metric.date.isoformat(),
                            'platform': platform,
                            'followers': metric.followers or 0,
                            'engagement': metric.engagement or 0
                        })
                
                # Add latest data point
                growth_data.append({
                    'date': latest_metric.date.isoformat(),
                    'platform': platform,
                    'followers': latest_metric.followers or 0,
                    'engagement': latest_metric.engagement or 0
                })
                
                # Add to top posts (simplified - would normally use actual post data)
                top_posts.append({
                    'platform': platform,
                    'post_id': f"post_{platform}_{now.strftime('%Y%m%d')}",
                    'date': latest_metric.date.isoformat(),
                    'engagement': platform_engagement,
                    'likes': platform_likes,
                    'comments': platform_comments,
                    'shares': platform_shares,
                    'views': platform_views
                })
            
            # Calculate average engagement rate
            avg_engagement_rate = 0
            if engagement_rates:
                avg_engagement_rate = sum(engagement_rates) / len(engagement_rates)
            
            # Sort top posts by engagement
            top_posts.sort(key=lambda x: x['engagement'], reverse=True)
            top_posts = top_posts[:5]  # Limit to top 5
            
            return {
                'platforms': connected_platforms,
                'total_followers': total_followers,
                'total_engagement': total_engagement,
                'average_engagement_rate': avg_engagement_rate,
                'platform_metrics': platform_metrics,
                'top_performing_posts': top_posts,
                'growth_trend': growth_data,
                'last_updated': now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting consolidated metrics: {str(e)}")
            return {
                'error': f"Failed to calculate consolidated metrics: {str(e)}",
                'last_updated': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    @cache.memoize(timeout=600)  # Cache for 10 minutes
    def get_platform_distribution():
        """
        Get distribution of influencers and metrics across different platforms.
        This is a heavy calculation so we cache it for 10 minutes.
        
        Returns:
            dict: Platform distribution statistics
        """
        try:
            # Get counts by platform
            platform_counts = db.session.query(
                Influencer.platform,
                func.count(Influencer.id).label('count'),
                func.avg(Influencer.followers_count).label('avg_followers'),
                func.avg(Influencer.engagement_rate).label('avg_engagement')
            ).group_by(Influencer.platform).all()
            
            result = {
                'counts': {},
                'followers': {},
                'engagement': {},
                'last_updated': datetime.utcnow().isoformat()
            }
            
            total_influencers = 0
            for platform, count, avg_followers, avg_engagement in platform_counts:
                total_influencers += count
                result['counts'][platform] = count
                result['followers'][platform] = round(avg_followers or 0)
                result['engagement'][platform] = round((avg_engagement or 0) * 100, 2)  # Convert to percentage
            
            # Calculate percentages
            result['percentages'] = {}
            for platform in result['counts'].keys():
                result['percentages'][platform] = round((result['counts'][platform] / total_influencers) * 100, 2)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating platform distribution: {str(e)}")
            return {
                'error': f"Failed to calculate platform distribution: {str(e)}",
                'last_updated': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def get_category_insights():
        """
        Get insights about performance across different categories.
        This changes rarely so we cache it for 24 hours.
        
        Returns:
            dict: Category insights
        """
        try:
            # Get all categories
            categories = Category.query.all()
            
            result = {
                'categories': {},
                'top_categories': [],
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # Get metrics for each category
            for category in categories:
                # Get influencers in this category
                influencers = category.influencers.all()
                
                if not influencers:
                    continue
                
                # Calculate average metrics
                followers = [i.followers_count for i in influencers if i.followers_count]
                engagement = [i.engagement_rate for i in influencers if i.engagement_rate]
                
                avg_followers = np.mean(followers) if followers else 0
                avg_engagement = np.mean(engagement) if engagement else 0
                
                # Store category metrics
                result['categories'][category.name] = {
                    'influencer_count': len(influencers),
                    'avg_followers': round(avg_followers),
                    'avg_engagement': round(avg_engagement * 100, 2),  # Convert to percentage
                    'most_common_platform': AnalyticsService._get_most_common_platform(influencers)
                }
                
                # Add to top categories list
                result['top_categories'].append({
                    'name': category.name,
                    'influencer_count': len(influencers),
                    'avg_followers': round(avg_followers),
                    'avg_engagement': round(avg_engagement * 100, 2)
                })
            
            # Sort top categories by influencer count
            result['top_categories'].sort(key=lambda x: x['influencer_count'], reverse=True)
            result['top_categories'] = result['top_categories'][:10]  # Limit to top 10
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating category insights: {str(e)}")
            return {
                'error': f"Failed to calculate category insights: {str(e)}",
                'last_updated': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _get_most_common_platform(influencers):
        """Helper method to find the most common platform in a list of influencers."""
        if not influencers:
            return None
            
        platform_counts = {}
        for influencer in influencers:
            if influencer.platform not in platform_counts:
                platform_counts[influencer.platform] = 0
            platform_counts[influencer.platform] += 1
            
        if not platform_counts:
            return None
            
        return max(platform_counts.items(), key=lambda x: x[1])[0]