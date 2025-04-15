"""
Service for analyzing and recommending optimal posting times.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from collections import defaultdict
from sqlalchemy import func, desc, extract, and_
from app.extensions import db, cache
from app.models import SocialPagePost, SocialPage, User
from app.models.social_media import SocialToken

logger = logging.getLogger(__name__)

class PostingTimeService:
    """Service for analyzing optimal posting times based on engagement data."""
    
    # Days of week for reference
    DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Content type mapping
    CONTENT_TYPES = ['image', 'video', 'carousel', 'text', 'link', 'story', 'reel']
    
    @staticmethod
    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def get_best_posting_times(user_id, platform=None, content_type=None, days=90):
        """
        Analyze historical post data to determine best posting times.
        
        Args:
            user_id: User ID
            platform: Optional platform filter (instagram, facebook, tiktok)
            content_type: Optional content type filter (image, video, etc)
            days: Number of days of historical data to analyze (default: 90)
            
        Returns:
            dict: Best posting times by day of week and content type
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user's social media connections if platform is not specified
            platforms = []
            if platform:
                platforms = [platform]
            else:
                user = User.query.get(user_id)
                if not user:
                    return {'error': 'User not found'}
                
                if user.facebook_id:
                    platforms.append('facebook')
                if user.instagram_id:
                    platforms.append('instagram')
                if user.tiktok_id:
                    platforms.append('tiktok')
            
            if not platforms:
                return {'error': 'No connected social media platforms found'}
            
            # Get posts to analyze
            query = SocialPagePost.query.filter(
                SocialPagePost.posted_at >= start_date,
                SocialPagePost.posted_at <= end_date
            )
            
            # Add platform filter if specified
            if platforms:
                query = query.filter(SocialPagePost.platform.in_(platforms))
            
            # Add content type filter if specified
            if content_type:
                query = query.filter(SocialPagePost.content_type == content_type)
            
            # Get all posts
            posts = query.all()
            
            if not posts:
                return {
                    'error': 'Not enough data for analysis',
                    'message': 'Unable to analyze posting times due to insufficient historical data',
                    'recommendations': {},
                    'is_reliable': False
                }
            
            # Initialize data structures
            hourly_engagement = {day: {hour: {'count': 0, 'total_engagement': 0, 'avg_engagement': 0} 
                             for hour in range(24)} for day in PostingTimeService.DAYS_OF_WEEK}
            
            content_type_engagement = {}
            platform_engagement = {}
            
            # Process post data
            for post in posts:
                if not post.posted_at:
                    continue
                
                day = post.day_of_week
                hour = post.hour_of_day
                
                if not day or hour is None:
                    continue
                
                # Calculate engagement
                engagement = post.engagement
                
                # Update hourly engagement data
                hourly_engagement[day][hour]['count'] += 1
                hourly_engagement[day][hour]['total_engagement'] += engagement
                
                # Update content type data
                post_type = post.content_type or 'unknown'
                if post_type not in content_type_engagement:
                    content_type_engagement[post_type] = {
                        'count': 0,
                        'total_engagement': 0,
                        'avg_engagement': 0
                    }
                
                content_type_engagement[post_type]['count'] += 1
                content_type_engagement[post_type]['total_engagement'] += engagement
                
                # Update platform data
                post_platform = post.platform
                if post_platform not in platform_engagement:
                    platform_engagement[post_platform] = {
                        'count': 0,
                        'total_engagement': 0,
                        'avg_engagement': 0
                    }
                
                platform_engagement[post_platform]['count'] += 1
                platform_engagement[post_platform]['total_engagement'] += engagement
            
            # Calculate averages for hourly data
            for day in PostingTimeService.DAYS_OF_WEEK:
                for hour in range(24):
                    count = hourly_engagement[day][hour]['count']
                    total = hourly_engagement[day][hour]['total_engagement']
                    
                    if count > 0:
                        hourly_engagement[day][hour]['avg_engagement'] = total / count
            
            # Calculate averages for content types
            for content_type, data in content_type_engagement.items():
                if data['count'] > 0:
                    data['avg_engagement'] = data['total_engagement'] / data['count']
            
            # Calculate averages for platforms
            for platform, data in platform_engagement.items():
                if data['count'] > 0:
                    data['avg_engagement'] = data['total_engagement'] / data['count']
            
            # Find best posting times for each day
            best_times = {}
            for day in PostingTimeService.DAYS_OF_WEEK:
                day_data = hourly_engagement[day]
                
                # Sort hours by average engagement
                sorted_hours = sorted(
                    [(hour, data['avg_engagement'], data['count']) 
                     for hour, data in day_data.items() if data['count'] > 0],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Get top 3 hours
                top_hours = []
                for hour, avg_engagement, count in sorted_hours[:3]:
                    top_hours.append({
                        'hour': hour,
                        'formatted_hour': f"{hour:02d}:00",
                        'avg_engagement': round(avg_engagement, 2),
                        'post_count': count,
                        'confidence': min(1.0, count / 10)  # Confidence based on sample size
                    })
                
                best_times[day] = top_hours
            
            # Find best content types
            sorted_content_types = sorted(
                [(ct, data['avg_engagement'], data['count']) 
                 for ct, data in content_type_engagement.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            best_content_types = []
            for ct, avg_engagement, count in sorted_content_types:
                best_content_types.append({
                    'type': ct,
                    'avg_engagement': round(avg_engagement, 2),
                    'post_count': count,
                    'confidence': min(1.0, count / 10)
                })
            
            # Get data by platform
            platform_data = {}
            for platform, data in platform_engagement.items():
                platform_data[platform] = {
                    'avg_engagement': round(data['avg_engagement'], 2),
                    'post_count': data['count']
                }
            
            # Determine overall best day and time
            day_totals = {}
            for day in PostingTimeService.DAYS_OF_WEEK:
                day_posts = sum(data['count'] for hour, data in hourly_engagement[day].items())
                day_engagement = sum(data['total_engagement'] for hour, data in hourly_engagement[day].items())
                
                if day_posts > 0:
                    day_totals[day] = {
                        'post_count': day_posts,
                        'avg_engagement': day_engagement / day_posts
                    }
            
            # Sort days by average engagement
            sorted_days = sorted(
                [(day, data['avg_engagement'], data['post_count']) for day, data in day_totals.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            best_days = []
            for day, avg_engagement, count in sorted_days:
                best_days.append({
                    'day': day,
                    'avg_engagement': round(avg_engagement, 2),
                    'post_count': count
                })
            
            # Determine if we have enough data for reliable recommendations
            total_posts = len(posts)
            is_reliable = total_posts >= 30  # At least 30 posts for reliable analysis
            
            return {
                'recommendations': {
                    'by_day': best_times,
                    'best_days': best_days[:3],
                    'best_content_types': best_content_types,
                    'by_platform': platform_data
                },
                'data_points': total_posts,
                'analyzed_period_days': days,
                'is_reliable': is_reliable,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing posting times: {str(e)}")
            return {'error': f"Failed to analyze posting times: {str(e)}"}
    
    @staticmethod
    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def get_content_type_performance(user_id, platform=None, days=90):
        """
        Analyze performance of different content types.
        
        Args:
            user_id: User ID
            platform: Optional platform filter (instagram, facebook, tiktok)
            days: Number of days of historical data to analyze (default: 90)
            
        Returns:
            dict: Performance metrics by content type
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user's social media connections if platform is not specified
            platforms = []
            if platform:
                platforms = [platform]
            else:
                user = User.query.get(user_id)
                if not user:
                    return {'error': 'User not found'}
                
                if user.facebook_id:
                    platforms.append('facebook')
                if user.instagram_id:
                    platforms.append('instagram')
                if user.tiktok_id:
                    platforms.append('tiktok')
            
            if not platforms:
                return {'error': 'No connected social media platforms found'}
            
            # Get posts to analyze
            query = SocialPagePost.query.filter(
                SocialPagePost.posted_at >= start_date,
                SocialPagePost.posted_at <= end_date
            )
            
            # Add platform filter if specified
            if platforms:
                query = query.filter(SocialPagePost.platform.in_(platforms))
            
            # Get all posts
            posts = query.all()
            
            if not posts:
                return {
                    'error': 'Not enough data for analysis',
                    'message': 'Unable to analyze content type performance due to insufficient historical data',
                    'performance': {},
                    'is_reliable': False
                }
            
            # Initialize data structure for content types
            content_types = {}
            
            # Process post data
            for post in posts:
                content_type = post.content_type or 'unknown'
                
                if content_type not in content_types:
                    content_types[content_type] = {
                        'count': 0,
                        'total_engagement': 0,
                        'total_likes': 0,
                        'total_comments': 0,
                        'total_shares': 0,
                        'by_day': {day: 0 for day in PostingTimeService.DAYS_OF_WEEK},
                        'by_hour': {hour: 0 for hour in range(24)}
                    }
                
                # Update counts
                content_types[content_type]['count'] += 1
                content_types[content_type]['total_engagement'] += post.engagement
                content_types[content_type]['total_likes'] += post.likes_count or 0
                content_types[content_type]['total_comments'] += post.comments_count or 0
                content_types[content_type]['total_shares'] += post.shares_count or 0
                
                # Update day and hour distributions if posted_at is available
                if post.posted_at:
                    day = post.day_of_week
                    hour = post.hour_of_day
                    
                    if day and hour is not None:
                        content_types[content_type]['by_day'][day] += 1
                        content_types[content_type]['by_hour'][hour] += 1
            
            # Calculate averages and percentages
            performance = {}
            total_posts = len(posts)
            
            for content_type, data in content_types.items():
                count = data['count']
                
                if count > 0:
                    performance[content_type] = {
                        'post_count': count,
                        'percentage': round((count / total_posts) * 100, 2),
                        'avg_engagement': round(data['total_engagement'] / count, 2),
                        'avg_likes': round(data['total_likes'] / count, 2),
                        'avg_comments': round(data['total_comments'] / count, 2),
                        'avg_shares': round(data['total_shares'] / count, 2),
                        'best_days': [],
                        'best_hours': []
                    }
                    
                    # Get best days
                    best_days = sorted(
                        [(day, data['by_day'][day]) for day in PostingTimeService.DAYS_OF_WEEK],
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    for day, day_count in best_days[:3]:
                        if day_count > 0:
                            performance[content_type]['best_days'].append({
                                'day': day,
                                'post_count': day_count,
                                'percentage': round((day_count / count) * 100, 2)
                            })
                    
                    # Get best hours
                    best_hours = sorted(
                        [(hour, data['by_hour'][hour]) for hour in range(24)],
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    for hour, hour_count in best_hours[:3]:
                        if hour_count > 0:
                            performance[content_type]['best_hours'].append({
                                'hour': hour,
                                'formatted_hour': f"{hour:02d}:00",
                                'post_count': hour_count,
                                'percentage': round((hour_count / count) * 100, 2)
                            })
            
            # Determine if we have enough data for reliable recommendations
            is_reliable = total_posts >= 30  # At least 30 posts for reliable analysis
            
            return {
                'performance': performance,
                'total_posts': total_posts,
                'analyzed_period_days': days,
                'is_reliable': is_reliable,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content type performance: {str(e)}")
            return {'error': f"Failed to analyze content type performance: {str(e)}"}
    
    @staticmethod
    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def get_day_of_week_analysis(user_id, platform=None, days=90):
        """
        Analyze post engagement by day of week.
        
        Args:
            user_id: User ID
            platform: Optional platform filter (instagram, facebook, tiktok)
            days: Number of days of historical data to analyze (default: 90)
            
        Returns:
            dict: Engagement analysis by day of week
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user's social media connections if platform is not specified
            platforms = []
            if platform:
                platforms = [platform]
            else:
                user = User.query.get(user_id)
                if not user:
                    return {'error': 'User not found'}
                
                if user.facebook_id:
                    platforms.append('facebook')
                if user.instagram_id:
                    platforms.append('instagram')
                if user.tiktok_id:
                    platforms.append('tiktok')
            
            if not platforms:
                return {'error': 'No connected social media platforms found'}
            
            # Get posts to analyze
            query = SocialPagePost.query.filter(
                SocialPagePost.posted_at >= start_date,
                SocialPagePost.posted_at <= end_date
            )
            
            # Add platform filter if specified
            if platforms:
                query = query.filter(SocialPagePost.platform.in_(platforms))
            
            # Get all posts
            posts = query.all()
            
            if not posts:
                return {
                    'error': 'Not enough data for analysis',
                    'message': 'Unable to analyze day of week performance due to insufficient historical data',
                    'by_day': {},
                    'is_reliable': False
                }
            
            # Initialize data structure for days of week
            days_data = {day: {
                'post_count': 0,
                'total_engagement': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_shares': 0,
                'by_content_type': {},
                'by_hour': {hour: 0 for hour in range(24)}
            } for day in PostingTimeService.DAYS_OF_WEEK}
            
            # Process post data
            for post in posts:
                if not post.posted_at:
                    continue
                
                day = post.day_of_week
                if not day:
                    continue
                
                content_type = post.content_type or 'unknown'
                hour = post.hour_of_day
                
                # Update day counts
                days_data[day]['post_count'] += 1
                days_data[day]['total_engagement'] += post.engagement
                days_data[day]['total_likes'] += post.likes_count or 0
                days_data[day]['total_comments'] += post.comments_count or 0
                days_data[day]['total_shares'] += post.shares_count or 0
                
                # Update content type distribution
                if content_type not in days_data[day]['by_content_type']:
                    days_data[day]['by_content_type'][content_type] = 0
                days_data[day]['by_content_type'][content_type] += 1
                
                # Update hour distribution
                if hour is not None:
                    days_data[day]['by_hour'][hour] += 1
            
            # Calculate averages and organize results
            day_analysis = {}
            
            for day in PostingTimeService.DAYS_OF_WEEK:
                count = days_data[day]['post_count']
                
                if count > 0:
                    # Calculate averages
                    avg_engagement = days_data[day]['total_engagement'] / count
                    avg_likes = days_data[day]['total_likes'] / count
                    avg_comments = days_data[day]['total_comments'] / count
                    avg_shares = days_data[day]['total_shares'] / count
                    
                    # Get top content types
                    content_types = sorted(
                        [(ct, ct_count) for ct, ct_count in days_data[day]['by_content_type'].items()],
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    top_content_types = []
                    for ct, ct_count in content_types[:3]:
                        top_content_types.append({
                            'type': ct,
                            'post_count': ct_count,
                            'percentage': round((ct_count / count) * 100, 2)
                        })
                    
                    # Get top hours
                    hours = sorted(
                        [(hour, hour_count) for hour, hour_count in days_data[day]['by_hour'].items()],
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    top_hours = []
                    for hour, hour_count in hours[:3]:
                        if hour_count > 0:
                            top_hours.append({
                                'hour': hour,
                                'formatted_hour': f"{hour:02d}:00",
                                'post_count': hour_count,
                                'percentage': round((hour_count / count) * 100, 2)
                            })
                    
                    # Organize day data
                    day_analysis[day] = {
                        'post_count': count,
                        'avg_engagement': round(avg_engagement, 2),
                        'avg_likes': round(avg_likes, 2),
                        'avg_comments': round(avg_comments, 2),
                        'avg_shares': round(avg_shares, 2),
                        'top_content_types': top_content_types,
                        'top_hours': top_hours
                    }
            
            # Get an ordered list of days by engagement
            ordered_days = sorted(
                [(day, day_analysis[day]['avg_engagement'], day_analysis[day]['post_count']) 
                 for day in day_analysis.keys()],
                key=lambda x: x[1],
                reverse=True
            )
            
            best_days = []
            for day, avg_engagement, count in ordered_days:
                best_days.append({
                    'day': day,
                    'avg_engagement': avg_engagement,
                    'post_count': count
                })
            
            # Determine if we have enough data for reliable recommendations
            total_posts = len(posts)
            is_reliable = total_posts >= 30  # At least 30 posts for reliable analysis
            
            return {
                'by_day': day_analysis,
                'best_days': best_days,
                'total_posts': total_posts,
                'analyzed_period_days': days,
                'is_reliable': is_reliable,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing day of week performance: {str(e)}")
            return {'error': f"Failed to analyze day of week performance: {str(e)}"}
    
    @staticmethod
    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def get_industry_benchmarks(category=None, platform=None):
        """
        Get industry benchmarks for posting times and engagement.
        
        Args:
            category: Optional category filter
            platform: Optional platform filter
            
        Returns:
            dict: Industry benchmarks
        """
        try:
            # Get posts from the past 90 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
            
            # Build query
            query = SocialPagePost.query.join(SocialPage).filter(
                SocialPagePost.posted_at >= start_date,
                SocialPagePost.posted_at <= end_date
            )
            
            # Apply filters if provided
            if category:
                query = query.join(SocialPage.categories).filter_by(name=category)
            
            if platform:
                query = query.filter(SocialPagePost.platform == platform)
            
            # Get all posts
            posts = query.all()
            
            if not posts:
                return {
                    'error': 'Not enough data for benchmarks',
                    'message': 'Unable to provide industry benchmarks due to insufficient data',
                    'benchmarks': {},
                    'is_reliable': False
                }
            
            # Initialize data structures
            day_data = {day: {
                'post_count': 0,
                'total_engagement': 0,
                'by_hour': {hour: {'count': 0, 'engagement': 0} for hour in range(24)}
            } for day in PostingTimeService.DAYS_OF_WEEK}
            
            content_type_data = {}
            platform_data = {}
            
            # Process post data
            for post in posts:
                if not post.posted_at:
                    continue
                
                day = post.day_of_week
                hour = post.hour_of_day
                content_type = post.content_type or 'unknown'
                post_platform = post.platform
                
                if not day or hour is None:
                    continue
                
                engagement = post.engagement
                
                # Update day data
                day_data[day]['post_count'] += 1
                day_data[day]['total_engagement'] += engagement
                day_data[day]['by_hour'][hour]['count'] += 1
                day_data[day]['by_hour'][hour]['engagement'] += engagement
                
                # Update content type data
                if content_type not in content_type_data:
                    content_type_data[content_type] = {
                        'count': 0,
                        'total_engagement': 0
                    }
                
                content_type_data[content_type]['count'] += 1
                content_type_data[content_type]['total_engagement'] += engagement
                
                # Update platform data
                if post_platform not in platform_data:
                    platform_data[post_platform] = {
                        'count': 0,
                        'total_engagement': 0
                    }
                
                platform_data[post_platform]['count'] += 1
                platform_data[post_platform]['total_engagement'] += engagement
            
            # Calculate best times by day
            best_times = {}
            for day in PostingTimeService.DAYS_OF_WEEK:
                day_count = day_data[day]['post_count']
                
                if day_count > 0:
                    # Calculate average engagement for each hour
                    hour_engagement = []
                    for hour in range(24):
                        hour_count = day_data[day]['by_hour'][hour]['count']
                        hour_total = day_data[day]['by_hour'][hour]['engagement']
                        
                        if hour_count > 0:
                            avg = hour_total / hour_count
                            hour_engagement.append((hour, avg, hour_count))
                    
                    # Sort by average engagement
                    sorted_hours = sorted(hour_engagement, key=lambda x: x[1], reverse=True)
                    
                    # Get top 3 hours
                    top_hours = []
                    for hour, avg, count in sorted_hours[:3]:
                        if count >= 5:  # Require at least 5 posts for reliability
                            top_hours.append({
                                'hour': hour,
                                'formatted_hour': f"{hour:02d}:00",
                                'avg_engagement': round(avg, 2),
                                'post_count': count
                            })
                    
                    if top_hours:
                        best_times[day] = top_hours
            
            # Calculate best content types
            best_content_types = []
            for content_type, data in content_type_data.items():
                count = data['count']
                
                if count >= 10:  # Require at least 10 posts for reliability
                    avg_engagement = data['total_engagement'] / count
                    best_content_types.append({
                        'type': content_type,
                        'avg_engagement': round(avg_engagement, 2),
                        'post_count': count
                    })
            
            # Sort by average engagement
            best_content_types.sort(key=lambda x: x['avg_engagement'], reverse=True)
            
            # Calculate platform stats
            platforms = []
            for platform_name, data in platform_data.items():
                count = data['count']
                
                if count > 0:
                    avg_engagement = data['total_engagement'] / count
                    platforms.append({
                        'platform': platform_name,
                        'avg_engagement': round(avg_engagement, 2),
                        'post_count': count
                    })
            
            # Sort by average engagement
            platforms.sort(key=lambda x: x['avg_engagement'], reverse=True)
            
            # Determine if we have enough data for reliable benchmarks
            total_posts = len(posts)
            is_reliable = total_posts >= 100  # Higher threshold for industry benchmarks
            
            return {
                'benchmarks': {
                    'best_times': best_times,
                    'best_content_types': best_content_types[:5],
                    'platforms': platforms
                },
                'total_posts': total_posts,
                'analyzed_period_days': 90,  # Fixed at 90 days for benchmarks
                'category': category,
                'platform': platform,
                'is_reliable': is_reliable,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting industry benchmarks: {str(e)}")
            return {'error': f"Failed to get industry benchmarks: {str(e)}"}
    
    @staticmethod
    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def get_personalized_recommendations(user_id, platform=None, content_type=None):
        """
        Generate personalized posting time recommendations based on user's data and industry benchmarks.
        
        Args:
            user_id: User ID
            platform: Optional platform filter
            content_type: Optional content type filter
            
        Returns:
            dict: Personalized posting recommendations
        """
        try:
            # Get user data
            user_data = PostingTimeService.get_best_posting_times(user_id, platform, content_type)
            
            # Check if we have user data
            if 'error' in user_data:
                # If no user data, rely solely on industry benchmarks
                user = User.query.get(user_id)
                if not user:
                    return {'error': 'User not found'}
                
                # Try to get any category the user might belong to
                category = None  # This would need to be retrieved from user data if available
                
                # Get industry benchmarks
                benchmarks = PostingTimeService.get_industry_benchmarks(category, platform)
                
                if 'error' in benchmarks:
                    return {
                        'error': 'Insufficient data',
                        'message': 'Unable to generate recommendations due to insufficient data',
                        'recommendations': {}
                    }
                
                # Use industry benchmarks as recommendations
                return {
                    'recommendations': benchmarks['benchmarks'],
                    'source': 'industry_benchmarks',
                    'message': 'Recommendations based on industry benchmarks due to insufficient user data',
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            # Get industry benchmarks for comparison
            benchmarks = PostingTimeService.get_industry_benchmarks(None, platform)
            
            # Combine user data with industry benchmarks
            personalized_recommendations = {
                'best_times': {},
                'best_content_types': [],
                'by_platform': {}
            }
            
            # Process best times
            user_best_times = user_data['recommendations']['by_day']
            benchmark_best_times = benchmarks.get('benchmarks', {}).get('best_times', {})
            
            for day in PostingTimeService.DAYS_OF_WEEK:
                user_times = user_best_times.get(day, [])
                benchmark_times = benchmark_best_times.get(day, [])
                
                if user_times and user_data['is_reliable']:
                    # If user has reliable data, prioritize it but add benchmark comparison
                    personalized_recommendations['best_times'][day] = {
                        'recommended': user_times[:2],  # Top 2 user times
                        'benchmark_comparison': benchmark_times[:1] if benchmark_times else []  # Top benchmark time
                    }
                elif benchmark_times:
                    # If no reliable user data, rely on benchmarks
                    personalized_recommendations['best_times'][day] = {
                        'recommended': benchmark_times[:2],  # Top 2 benchmark times
                        'source': 'industry_benchmark'
                    }
            
            # Process best content types
            user_content_types = user_data['recommendations'].get('best_content_types', [])
            benchmark_content_types = benchmarks.get('benchmarks', {}).get('best_content_types', [])
            
            if user_content_types and user_data['is_reliable']:
                # If user has reliable data, prioritize it
                top_types = user_content_types[:3]
                for ct in top_types:
                    # Find corresponding benchmark data if available
                    benchmark_data = next((b for b in benchmark_content_types if b['type'] == ct['type']), None)
                    
                    recommendation = {
                        'type': ct['type'],
                        'avg_engagement': ct['avg_engagement'],
                        'confidence': ct['confidence']
                    }
                    
                    if benchmark_data:
                        recommendation['benchmark_engagement'] = benchmark_data['avg_engagement']
                        recommendation['relative_performance'] = round(
                            (ct['avg_engagement'] / benchmark_data['avg_engagement'] - 1) * 100, 2
                        ) if benchmark_data['avg_engagement'] > 0 else 0
                    
                    personalized_recommendations['best_content_types'].append(recommendation)
            elif benchmark_content_types:
                # If no reliable user data, rely on benchmarks
                personalized_recommendations['best_content_types'] = benchmark_content_types[:3]
                for ct in personalized_recommendations['best_content_types']:
                    ct['source'] = 'industry_benchmark'
            
            # Add platform-specific recommendations
            user_platforms = user_data['recommendations'].get('by_platform', {})
            benchmark_platforms = {p['platform']: p for p in benchmarks.get('benchmarks', {}).get('platforms', [])}
            
            for platform_name, platform_data in user_platforms.items():
                benchmark_data = benchmark_platforms.get(platform_name)
                
                if platform_data and platform_data['post_count'] >= 10:
                    # If user has enough platform data
                    recommendation = {
                        'avg_engagement': platform_data['avg_engagement'],
                        'post_count': platform_data['post_count'],
                        'reliability': min(1.0, platform_data['post_count'] / 30)  # Reliability score
                    }
                    
                    if benchmark_data:
                        recommendation['benchmark_engagement'] = benchmark_data['avg_engagement']
                        recommendation['relative_performance'] = round(
                            (platform_data['avg_engagement'] / benchmark_data['avg_engagement'] - 1) * 100, 2
                        ) if benchmark_data['avg_engagement'] > 0 else 0
                    
                    personalized_recommendations['by_platform'][platform_name] = recommendation
                elif benchmark_data:
                    # If no reliable user data, rely on benchmarks
                    personalized_recommendations['by_platform'][platform_name] = {
                        'avg_engagement': benchmark_data['avg_engagement'],
                        'post_count': benchmark_data['post_count'],
                        'source': 'industry_benchmark'
                    }
            
            # Add overall recommendation and message
            source = 'user_data' if user_data['is_reliable'] else 'mixed'
            message = "Recommendations based on your posting history." if user_data['is_reliable'] else \
                      "Recommendations based on a combination of your data and industry benchmarks."
            
            return {
                'recommendations': personalized_recommendations,
                'source': source,
                'message': message,
                'user_data_points': user_data['data_points'],
                'is_reliable': user_data['is_reliable'],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {str(e)}")
            return {'error': f"Failed to generate personalized recommendations: {str(e)}"}