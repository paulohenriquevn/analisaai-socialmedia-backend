"""
Service for interacting with social media platforms.
"""
import requests
import json
import logging
from datetime import datetime, timedelta
from app.extensions import db
from app.models import Influencer, InfluencerMetric, Category
from app.services.oauth_service import get_token

logger = logging.getLogger(__name__)

class SocialMediaService:
    """Service for interacting with social media platforms."""
    
    @staticmethod
    def fetch_instagram_profile(user_id, username=None):
        """
        Fetch Instagram profile data for a user.
        
        Args:
            user_id: The user ID to get token from
            username: Instagram username (optional)
            
        Returns:
            dict: Instagram profile data or None if error
        """
        token_data = get_token(user_id, 'instagram')
        if not token_data:
            logger.error(f"No Instagram token found for user {user_id}")
            return None
        
        access_token = token_data['access_token']
        
        # First get the user ID if username is provided
        if username:
            try:
                # Search for the username
                search_url = f"https://graph.instagram.com/v18.0/ig_username_search"
                params = {
                    'q': username,
                    'access_token': access_token
                }
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if 'data' not in data or len(data['data']) == 0:
                    logger.error(f"Instagram user {username} not found")
                    return None
                
                instagram_user_id = data['data'][0]['id']
            except Exception as e:
                logger.error(f"Error searching Instagram user {username}: {str(e)}")
                return None
        else:
            # Get the user's own profile
            try:
                self_url = f"https://graph.instagram.com/v18.0/me"
                params = {
                    'fields': 'id,username',
                    'access_token': access_token
                }
                response = requests.get(self_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                instagram_user_id = data['id']
                username = data['username']
            except Exception as e:
                logger.error(f"Error getting Instagram self profile: {str(e)}")
                return None
        
        # Now get the user profile data
        try:
            profile_url = f"https://graph.instagram.com/v18.0/{instagram_user_id}"
            params = {
                'fields': 'id,username,biography,profile_picture_url,follows_count,followed_by_count,media_count',
                'access_token': access_token
            }
            response = requests.get(profile_url, params=params)
            response.raise_for_status()
            
            profile_data = response.json()
            
            # Get recent media to calculate engagement
            media_url = f"https://graph.instagram.com/v18.0/{instagram_user_id}/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count',
                'limit': 10,
                'access_token': access_token
            }
            media_response = requests.get(media_url, params=params)
            media_response.raise_for_status()
            
            media_data = media_response.json()
            
            # Calculate engagement metrics
            total_likes = 0
            total_comments = 0
            post_count = len(media_data.get('data', []))
            
            for post in media_data.get('data', []):
                total_likes += post.get('like_count', 0)
                total_comments += post.get('comments_count', 0)
            
            engagement = 0
            followers = profile_data.get('followed_by_count', 0)
            
            if post_count > 0 and followers > 0:
                engagement = ((total_likes + total_comments) / post_count) / followers * 100
            
            return {
                'platform': 'instagram',
                'username': profile_data.get('username'),
                'full_name': profile_data.get('username'),  # Instagram Graph API doesn't provide full_name
                'profile_url': f"https://instagram.com/{profile_data.get('username')}",
                'profile_image': profile_data.get('profile_picture_url'),
                'bio': profile_data.get('biography'),
                'followers_count': profile_data.get('followed_by_count', 0),
                'following_count': profile_data.get('follows_count', 0),
                'posts_count': profile_data.get('media_count', 0),
                'engagement_rate': engagement,
                'metrics': {
                    'followers': profile_data.get('followed_by_count', 0),
                    'engagement': engagement,
                    'posts': profile_data.get('media_count', 0),
                    'likes': total_likes,
                    'comments': total_comments
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching Instagram profile data: {str(e)}")
            return None
    
    @staticmethod
    def fetch_tiktok_profile(user_id, username=None):
        """
        Fetch TikTok profile data for a user.
        
        Args:
            user_id: The user ID to get token from
            username: TikTok username (optional)
            
        Returns:
            dict: TikTok profile data or None if error
        """
        token_data = get_token(user_id, 'tiktok')
        if not token_data:
            logger.error(f"No TikTok token found for user {user_id}")
            return None
        
        access_token = token_data['access_token']
        
        try:
            if username:
                # TikTok API doesn't have a username search endpoint in v2 API
                # We would need to use the user's own profile and then search for the username
                # This is a simplified approach for demo purposes
                logger.warning("TikTok API doesn't support username search in this version")
                return None
            
            # Get user info
            user_info_url = "https://open.tiktokapis.com/v2/user/info/"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            params = {
                "fields": "display_name,avatar_url,profile_deep_link,follower_count,following_count,likes_count,video_count,bio_description"
            }
            
            response = requests.get(user_info_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            user_data = data.get('data', {}).get('user', {})
            
            # Get recent videos for engagement calculation
            videos_url = "https://open.tiktokapis.com/v2/video/list/"
            params = {
                "fields": "like_count,comment_count,share_count,view_count",
                "max_count": 10
            }
            
            videos_response = requests.get(videos_url, headers=headers, params=params)
            videos_response.raise_for_status()
            
            videos_data = videos_response.json()
            videos = videos_data.get('data', {}).get('videos', [])
            
            # Calculate engagement metrics
            total_likes = 0
            total_comments = 0
            total_shares = 0
            total_views = 0
            video_count = len(videos)
            
            for video in videos:
                total_likes += video.get('like_count', 0)
                total_comments += video.get('comment_count', 0)
                total_shares += video.get('share_count', 0)
                total_views += video.get('view_count', 0)
            
            engagement = 0
            followers = user_data.get('follower_count', 0)
            
            if video_count > 0 and followers > 0:
                engagement = ((total_likes + total_comments + total_shares) / video_count) / followers * 100
            
            return {
                'platform': 'tiktok',
                'username': user_data.get('display_name'),
                'full_name': user_data.get('display_name'),
                'profile_url': user_data.get('profile_deep_link'),
                'profile_image': user_data.get('avatar_url'),
                'bio': user_data.get('bio_description'),
                'followers_count': user_data.get('follower_count', 0),
                'following_count': user_data.get('following_count', 0),
                'posts_count': user_data.get('video_count', 0),
                'engagement_rate': engagement,
                'metrics': {
                    'followers': user_data.get('follower_count', 0),
                    'engagement': engagement,
                    'posts': user_data.get('video_count', 0),
                    'likes': total_likes,
                    'comments': total_comments,
                    'shares': total_shares,
                    'views': total_views
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching TikTok profile data: {str(e)}")
            return None
    
    @staticmethod
    def calculate_social_score(influencer_data):
        """
        Calculate a social score based on various metrics.
        
        Args:
            influencer_data: Dict containing influencer metrics
            
        Returns:
            float: Social score from 0-100
        """
        # Get relevant metrics
        platform = influencer_data.get('platform', '').lower()
        followers = influencer_data.get('followers_count', 0)
        engagement = influencer_data.get('engagement_rate', 0)
        posts = influencer_data.get('posts_count', 0)
        
        # Platform-specific weights
        platform_weights = {
            'instagram': {
                'followers': 0.4,
                'engagement': 0.5,
                'posts': 0.1
            },
            'tiktok': {
                'followers': 0.3,
                'engagement': 0.6,
                'posts': 0.1
            },
            'facebook': {
                'followers': 0.5,
                'engagement': 0.4,
                'posts': 0.1
            }
        }
        
        # Default weights if platform not recognized
        weights = platform_weights.get(platform, {
            'followers': 0.4,
            'engagement': 0.5,
            'posts': 0.1
        })
        
        # Normalize metrics to 0-100 scale
        # These thresholds can be adjusted based on industry standards
        normalized_followers = min(100, (followers / 100000) * 100) if followers else 0
        normalized_engagement = min(100, engagement * 10) if engagement else 0  # 10% engagement -> 100 points
        normalized_posts = min(100, (posts / 1000) * 100) if posts else 0
        
        # Calculate weighted score
        score = (
            weights['followers'] * normalized_followers +
            weights['engagement'] * normalized_engagement +
            weights['posts'] * normalized_posts
        )
        
        return score
    
    @staticmethod
    def save_influencer_data(profile_data):
        """
        Save or update influencer profile data in the database.
        
        Args:
            profile_data: Dict containing influencer profile data
            
        Returns:
            Influencer: Saved influencer object
        """
        if not profile_data:
            return None
        
        platform = profile_data.get('platform')
        username = profile_data.get('username')
        
        # Check if influencer already exists
        influencer = Influencer.query.filter_by(
            platform=platform,
            username=username
        ).first()
        
        # Calculate social score
        social_score = SocialMediaService.calculate_social_score(profile_data)
        
        if influencer:
            # Update existing influencer
            influencer.full_name = profile_data.get('full_name')
            influencer.profile_url = profile_data.get('profile_url')
            influencer.profile_image = profile_data.get('profile_image')
            influencer.bio = profile_data.get('bio')
            influencer.followers_count = profile_data.get('followers_count', 0)
            influencer.following_count = profile_data.get('following_count', 0)
            influencer.posts_count = profile_data.get('posts_count', 0)
            influencer.engagement_rate = profile_data.get('engagement_rate', 0)
            influencer.social_score = social_score
            influencer.updated_at = datetime.utcnow()
        else:
            # Create new influencer
            influencer = Influencer(
                username=username,
                full_name=profile_data.get('full_name'),
                platform=platform,
                profile_url=profile_data.get('profile_url'),
                profile_image=profile_data.get('profile_image'),
                bio=profile_data.get('bio'),
                followers_count=profile_data.get('followers_count', 0),
                following_count=profile_data.get('following_count', 0),
                posts_count=profile_data.get('posts_count', 0),
                engagement_rate=profile_data.get('engagement_rate', 0),
                social_score=social_score
            )
            db.session.add(influencer)
        
        # Save metrics
        metrics = profile_data.get('metrics', {})
        if metrics:
            metric = InfluencerMetric(
                influencer=influencer,
                date=datetime.utcnow().date(),
                followers=metrics.get('followers'),
                engagement=metrics.get('engagement'),
                posts=metrics.get('posts'),
                likes=metrics.get('likes'),
                comments=metrics.get('comments'),
                shares=metrics.get('shares'),
                views=metrics.get('views')
            )
            db.session.add(metric)
        
        db.session.commit()
        return influencer
    
    @staticmethod
    def analyze_sentiment(text):
        """
        Simple sentiment analysis function.
        In a real implementation, this would use a more sophisticated NLP approach.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Sentiment analysis result
        """
        # This is a very simple implementation
        # In a real system, you'd use a proper NLP library like NLTK, spaCy, or a cloud service
        
        positive_words = ['good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'best', 'fantastic']
        negative_words = ['bad', 'worst', 'terrible', 'awful', 'hate', 'disappointing', 'poor']
        
        if not text:
            return {
                'sentiment': 'neutral',
                'score': 0
            }
        
        text = text.lower()
        words = text.split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        score = (positive_count - negative_count) / len(words) if words else 0
        
        if score > 0.05:
            sentiment = 'positive'
        elif score < -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': score
        }