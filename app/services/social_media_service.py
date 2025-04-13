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
        logger.info(f"Fetching Instagram profile for user_id={user_id}, username={username}")
        token_data = get_token(user_id, 'instagram')
        if not token_data:
            logger.error(f"No Instagram token found for user {user_id}")
            return None
        
        access_token = token_data['access_token']
        logger.info(f"Using Instagram access token for user {user_id}")
        
        # First we need to get all connected Instagram accounts through the Facebook Graph API
        try:
            # The correct approach is to first get the Facebook pages that the user has access to
            accounts_url = "https://graph.facebook.com/v16.0/me/accounts"
            params = {
                'access_token': access_token,
                'fields': 'instagram_business_account,name,id'
            }
            logger.info(f"Requesting Facebook Pages with Instagram Business accounts")
            response = requests.get(accounts_url, params=params)
            response.raise_for_status()
            
            accounts_data = response.json()
            logger.info(f"Found {len(accounts_data.get('data', []))} Facebook Pages")
            
            # Filter to find pages with Instagram business accounts
            instagram_accounts = []
            for page in accounts_data.get('data', []):
                if 'instagram_business_account' in page:
                    instagram_accounts.append({
                        'page_id': page['id'],
                        'page_name': page['name'],
                        'instagram_business_account_id': page['instagram_business_account']['id']
                    })
            
            if not instagram_accounts:
                logger.warning(f"No Instagram Business accounts found for user {user_id}")
                return {
                    'error': 'no_business_account',
                    'message': 'No Instagram Business accounts found. Please make sure your Instagram account is connected to a Facebook Page and is set as a Business or Creator account.'
                }
            
            logger.info(f"Found {len(instagram_accounts)} Instagram Business accounts")
            
            # Now get data for the Instagram account
            # If username is specified, find that specific account
            instagram_account = None
            if username:
                # Find the specific account with this username
                for account in instagram_accounts:
                    ig_id = account['instagram_business_account_id']
                    ig_url = f"https://graph.facebook.com/v16.0/{ig_id}"
                    params = {
                        'fields': 'username',
                        'access_token': access_token
                    }
                    ig_response = requests.get(ig_url, params=params)
                    ig_response.raise_for_status()
                    ig_data = ig_response.json()
                    
                    if ig_data.get('username') == username:
                        instagram_account = account
                        instagram_user_id = ig_id
                        break
                
                if not instagram_account:
                    logger.error(f"Instagram account with username {username} not found")
                    return None
            else:
                # Just use the first account
                instagram_account = instagram_accounts[0]
                instagram_user_id = instagram_account['instagram_business_account_id']
                logger.info(f"Using first Instagram account: {instagram_user_id}")
            
            # Now get detailed profile data
            profile_url = f"https://graph.facebook.com/v16.0/{instagram_user_id}"
            params = {
                'fields': 'id,username,name,biography,profile_picture_url,follows_count,followers_count,media_count,website',
                'access_token': access_token
            }
            profile_response = requests.get(profile_url, params=params)
            profile_response.raise_for_status()
            
            profile_data = profile_response.json()
            logger.info(f"Got profile data for Instagram account {profile_data.get('username')}")
            
            # Get recent media for engagement metrics
            media_url = f"https://graph.facebook.com/v16.0/{instagram_user_id}/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count',
                'limit': 25,  # Get more posts for better engagement calculation
                'access_token': access_token
            }
            media_response = requests.get(media_url, params=params)
            media_response.raise_for_status()
            
            media_data = media_response.json()
            media_items = media_data.get('data', [])
            logger.info(f"Retrieved {len(media_items)} media items")
            
            # Calculate engagement metrics
            total_likes = 0
            total_comments = 0
            post_count = len(media_items)
            
            for post in media_items:
                total_likes += post.get('like_count', 0)
                total_comments += post.get('comments_count', 0)
            
            engagement = 0
            followers = profile_data.get('followers_count', 0)
            
            if post_count > 0 and followers > 0:
                engagement = ((total_likes + total_comments) / post_count) / followers * 100
            
            # Get insights if available (business accounts only)
            insights_data = {}
            try:
                insights_url = f"https://graph.facebook.com/v16.0/{instagram_user_id}/insights"
                params = {
                    'metric': 'impressions,reach,profile_views',
                    'period': 'day',
                    'access_token': access_token
                }
                insights_response = requests.get(insights_url, params=params)
                insights_response.raise_for_status()
                insights_data = insights_response.json()
                logger.info(f"Retrieved Instagram insights data")
            except Exception as e:
                logger.warning(f"Failed to get Instagram insights: {str(e)}")
                # Non-fatal error, continue without insights
            
            # Construct the full profile data
            account_data = {
                'platform': 'instagram',
                'username': profile_data.get('username'),
                'full_name': profile_data.get('name', profile_data.get('username')),
                'profile_url': f"https://instagram.com/{profile_data.get('username')}",
                'profile_image': profile_data.get('profile_picture_url'),
                'bio': profile_data.get('biography'),
                'website': profile_data.get('website'),
                'followers_count': followers,
                'following_count': profile_data.get('follows_count', 0),
                'posts_count': profile_data.get('media_count', 0),
                'engagement_rate': engagement,
                'account_type': 'business',  # Since we're using the Instagram Graph API, it's a business account
                'facebook_page_id': instagram_account['page_id'],
                'facebook_page_name': instagram_account['page_name'],
                'metrics': {
                    'followers': followers,
                    'engagement': engagement,
                    'posts': profile_data.get('media_count', 0),
                    'likes': total_likes,
                    'comments': total_comments,
                    'impressions': SocialMediaService._extract_metric_value(insights_data, 'impressions'),
                    'reach': SocialMediaService._extract_metric_value(insights_data, 'reach'),
                    'profile_views': SocialMediaService._extract_metric_value(insights_data, 'profile_views')
                },
                'recent_media': [
                    {
                        'id': post.get('id'),
                        'caption': post.get('caption', ''),
                        'media_type': post.get('media_type'),
                        'url': post.get('permalink'),
                        'thumbnail': post.get('thumbnail_url') or post.get('media_url'),
                        'timestamp': post.get('timestamp'),
                        'likes': post.get('like_count', 0),
                        'comments': post.get('comments_count', 0)
                    }
                    for post in media_items[:5]  # Include only first 5 posts in the response
                ]
            }
            
            return account_data
            
        except Exception as e:
            logger.error(f"Error fetching Instagram profile data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def _extract_metric_value(insights_data, metric_name):
        """Helper to extract the value from Instagram insights response."""
        try:
            for metric in insights_data.get('data', []):
                if metric.get('name') == metric_name:
                    return metric.get('values', [{}])[0].get('value', 0)
            return 0
        except Exception:
            return 0
    
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