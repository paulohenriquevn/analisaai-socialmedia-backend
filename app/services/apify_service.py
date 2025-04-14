"""
Service for interacting with Apify API to fetch social media data.
"""
import logging
import time
from flask import current_app
from apify_client import ApifyClient

logger = logging.getLogger(__name__)

class ApifyService:
    """Service for interacting with Apify API to fetch social media data."""
    
    @staticmethod
    def fetch_instagram_profile(username):
        """
        Fetch Instagram profile data for a username using Apify.
        
        Args:
            username: Instagram username (without @)
            
        Returns:
            dict: Instagram profile data or None if error
        """
        logger.info(f"Fetching Instagram profile for username={username} using Apify")
        
        # Clean username
        username = username.replace('@', '').strip()
        
        # Get API key from config
        api_key = current_app.config.get('APIFY_API_KEY')
        if not api_key:
            logger.error("Missing Apify API key in configuration")
            return {
                'error': 'missing_api_key',
                'message': 'Apify API key is not configured'
            }
        
        try:
            # Initialize the ApifyClient with the API token
            client = ApifyClient(api_key)
            
            # Prepare the Actor input
            run_input = {
                "directUrls": [f"https://www.instagram.com/{username}/"],
                "resultsType": "details",
                "addParentData": True
            }
            
            logger.info(f"Starting Apify run for Instagram profile: {username}")
            
            # Run the actor and wait for it to finish
            # Using Instagram Scraper actor (shu8hvrXbJbY3Eb9W)
            run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
            
            logger.info(f"Apify run completed with ID: {run['id']}")
            
            # Get dataset ID for the run
            dataset_id = run["defaultDatasetId"]
            
            # Fetch results from the dataset
            items = list(client.dataset(dataset_id).iterate_items())
            
            if not items or len(items) == 0:
                logger.warning(f"No results found for Instagram profile: {username}")
                return {
                    'error': 'no_results',
                    'message': f'No data found for Instagram profile: {username}'
                }
            
            # Process the results - extract the profile data
            profile_data = None
            for item in items:
                # Look for user profile info
                if item.get('id') == username or item.get('username') == username:
                    profile_data = item
                    break
            
            if not profile_data:
                # If we didn't find exact profile match, use the first item
                profile_data = items[0]
            
            # Transform Apify data to match our standard format
            transformed_data = ApifyService._transform_instagram_data(profile_data)
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Unexpected error when using Apify API: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': 'unexpected_error',
                'message': f'An unexpected error occurred: {str(e)}'
            }
    
    @staticmethod
    def fetch_tiktok_profile(username):
        """
        Fetch TikTok profile data for a username using Apify.
        
        Args:
            username: TikTok username (without @)
            
        Returns:
            dict: TikTok profile data or None if error
        """
        logger.info(f"Fetching TikTok profile for username={username} using Apify")
        
        # Clean username
        username = username.replace('@', '').strip()
        
        # Get API key from config
        api_key = current_app.config.get('APIFY_API_KEY')
        if not api_key:
            logger.error("Missing Apify API key in configuration")
            return {
                'error': 'missing_api_key',
                'message': 'Apify API key is not configured'
            }
        
        try:
            # Initialize the ApifyClient with the API token
            client = ApifyClient(api_key)
            
            # Prepare the Actor input
            run_input = {
                "profiles": [username],
                "scrapeType": "profile"
            }
            
            logger.info(f"Starting Apify run for TikTok profile: {username}")
            
            # Run the actor and wait for it to finish
            # Using TikTok Scraper actor (qhzXbQKch8FfpyG4T)
            run = client.actor("qhzXbQKch8FfpyG4T").call(run_input=run_input)
            
            logger.info(f"Apify run completed with ID: {run['id']}")
            
            # Get dataset ID for the run
            dataset_id = run["defaultDatasetId"]
            
            # Fetch results from the dataset
            items = list(client.dataset(dataset_id).iterate_items())
            
            if not items or len(items) == 0:
                logger.warning(f"No results found for TikTok profile: {username}")
                return {
                    'error': 'no_results',
                    'message': f'No data found for TikTok profile: {username}'
                }
            
            # Process the results - extract the profile data
            profile_data = None
            for item in items:
                # Look for user profile info
                if item.get('uniqueId') == username or item.get('username') == username:
                    profile_data = item
                    break
            
            if not profile_data:
                # If we didn't find exact profile match, use the first item
                profile_data = items[0]
            
            # Transform Apify data to match our standard format
            transformed_data = ApifyService._transform_tiktok_data(profile_data)
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Unexpected error when using Apify API: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': 'unexpected_error',
                'message': f'An unexpected error occurred: {str(e)}'
            }
    
    @staticmethod
    def fetch_facebook_profile(username):
        """
        Fetch Facebook profile data for a username using Apify.
        
        Args:
            username: Facebook username or page name (without @)
            
        Returns:
            dict: Facebook profile data or None if error
        """
        logger.info(f"Fetching Facebook profile for username={username} using Apify")
        
        # Clean username
        username = username.replace('@', '').strip()
        
        # Get API key from config
        api_key = current_app.config.get('APIFY_API_KEY')
        if not api_key:
            logger.error("Missing Apify API key in configuration")
            return {
                'error': 'missing_api_key',
                'message': 'Apify API key is not configured'
            }
        
        try:
            # Initialize the ApifyClient with the API token
            client = ApifyClient(api_key)
            
            # Prepare the Actor input
            run_input = {
                "startUrls": [{"url": f"https://www.facebook.com/{username}"}],
                "resultsType": "details",
                "proxyConfiguration": {"useApifyProxy": True}
            }
            
            logger.info(f"Starting Apify run for Facebook profile: {username}")
            
            # Run the actor and wait for it to finish
            # Using Facebook Scraper actor (dtrungtin/facebook-page-scraper)
            run = client.actor("dtrungtin/facebook-page-scraper").call(run_input=run_input)
            
            logger.info(f"Apify run completed with ID: {run['id']}")
            
            # Get dataset ID for the run
            dataset_id = run["defaultDatasetId"]
            
            # Fetch results from the dataset
            items = list(client.dataset(dataset_id).iterate_items())
            
            if not items or len(items) == 0:
                logger.warning(f"No results found for Facebook profile: {username}")
                return {
                    'error': 'no_results',
                    'message': f'No data found for Facebook profile: {username}'
                }
            
            # Process the results - find the profile data
            profile_data = None
            for item in items:
                # Look for the main profile info
                if item.get('type') == 'profile' or item.get('type') == 'page':
                    profile_data = item
                    break
            
            # If we didn't find a profile or page type item, use the first item
            if not profile_data and items:
                profile_data = items[0]
            
            if not profile_data:
                logger.warning(f"Could not find profile info in results for Facebook profile: {username}")
                return {
                    'error': 'no_profile_data',
                    'message': f'Could not extract profile data for Facebook profile: {username}'
                }
            
            # Transform Apify data to match our standard format
            transformed_data = ApifyService._transform_facebook_data(profile_data)
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Unexpected error when using Apify API: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': 'unexpected_error',
                'message': f'An unexpected error occurred: {str(e)}'
            }
    
    @staticmethod
    def _transform_instagram_data(apify_data):
        """
        Transform Instagram data from Apify format to our standard format.
        
        Args:
            apify_data: Raw data from Apify
            
        Returns:
            dict: Transformed data in our standard format
        """
        # Calculate engagement rate if possible
        engagement_rate = 0.0
        followers = apify_data.get('followersCount', 0)
        posts = apify_data.get('postsCount', 0)
        
        if 'latestPosts' in apify_data and followers > 0 and len(apify_data['latestPosts']) > 0:
            total_likes = sum(post.get('likesCount', 0) for post in apify_data['latestPosts'])
            total_comments = sum(post.get('commentsCount', 0) for post in apify_data['latestPosts'])
            post_count = len(apify_data['latestPosts'])
            
            if post_count > 0 and followers > 0:
                engagement_rate = ((total_likes + total_comments) / post_count) / followers * 100
        
        # Transform to our standard format
        transformed_data = {
            'platform': 'instagram',
            'username': apify_data.get('username'),
            'full_name': apify_data.get('fullName', apify_data.get('username')),
            'profile_url': f"https://instagram.com/{apify_data.get('username')}",
            'profile_image': apify_data.get('profilePicUrl'),
            'bio': apify_data.get('biography'),
            'website': apify_data.get('externalUrl'),
            'followers_count': followers,
            'following_count': apify_data.get('followsCount', 0),
            'posts_count': posts,
            'engagement_rate': engagement_rate,
            'account_type': 'business' if apify_data.get('isBusinessAccount') else 'personal',
            'is_verified': apify_data.get('isVerified', False),
            'metrics': {
                'followers': followers,
                'engagement': engagement_rate,
                'posts': posts
            }
        }
        
        # Add recent media if available
        if 'latestPosts' in apify_data and len(apify_data['latestPosts']) > 0:
            recent_media = []
            for post in apify_data['latestPosts'][:5]:  # Include only first 5 posts
                recent_media.append({
                    'id': post.get('id'),
                    'caption': post.get('caption', ''),
                    'media_type': post.get('type', 'IMAGE'),
                    'url': post.get('url'),
                    'thumbnail': post.get('displayUrl'),
                    'timestamp': post.get('timestamp'),
                    'likes': post.get('likesCount', 0),
                    'comments': post.get('commentsCount', 0)
                })
            
            transformed_data['recent_media'] = recent_media
            
            # Update metrics with likes and comments
            transformed_data['metrics']['likes'] = sum(post.get('likes', 0) for post in recent_media)
            transformed_data['metrics']['comments'] = sum(post.get('comments', 0) for post in recent_media)
        
        return transformed_data
    
    @staticmethod
    def _transform_tiktok_data(apify_data):
        """
        Transform TikTok data from Apify format to our standard format.
        
        Args:
            apify_data: Raw data from Apify
            
        Returns:
            dict: Transformed data in our standard format
        """
        # Calculate engagement rate if possible
        engagement_rate = 0.0
        followers = apify_data.get('followerCount', 0)
        
        if 'videos' in apify_data and followers > 0 and len(apify_data['videos']) > 0:
            total_likes = sum(video.get('likeCount', 0) for video in apify_data['videos'])
            total_comments = sum(video.get('commentCount', 0) for video in apify_data['videos'])
            total_shares = sum(video.get('shareCount', 0) for video in apify_data['videos'])
            video_count = len(apify_data['videos'])
            
            if video_count > 0 and followers > 0:
                engagement_rate = ((total_likes + total_comments + total_shares) / video_count) / followers * 100
        
        # Transform to our standard format
        transformed_data = {
            'platform': 'tiktok',
            'username': apify_data.get('username'),
            'full_name': apify_data.get('nickname', apify_data.get('username')),
            'profile_url': f"https://tiktok.com/@{apify_data.get('username')}",
            'profile_image': apify_data.get('avatarThumb') or apify_data.get('avatarMedium'),
            'bio': apify_data.get('signature', ''),
            'followers_count': followers,
            'following_count': apify_data.get('followingCount', 0),
            'posts_count': apify_data.get('videoCount', 0),
            'engagement_rate': engagement_rate,
            'is_verified': apify_data.get('verified', False),
            'metrics': {
                'followers': followers,
                'engagement': engagement_rate,
                'posts': apify_data.get('videoCount', 0),
                'likes': apify_data.get('heartCount', 0)
            }
        }
        
        # Add recent videos if available
        if 'videos' in apify_data and len(apify_data['videos']) > 0:
            recent_media = []
            for video in apify_data['videos'][:5]:  # Include only first 5 videos
                recent_media.append({
                    'id': video.get('id'),
                    'caption': video.get('description', ''),
                    'media_type': 'VIDEO',
                    'url': video.get('webVideoUrl'),
                    'thumbnail': video.get('covers', [None])[0] if video.get('covers') else None,
                    'timestamp': video.get('createTime'),
                    'likes': video.get('likeCount', 0),
                    'comments': video.get('commentCount', 0),
                    'shares': video.get('shareCount', 0),
                    'views': video.get('playCount', 0)
                })
            
            transformed_data['recent_media'] = recent_media
            
            # Update metrics with additional data
            transformed_data['metrics']['likes'] = sum(video.get('likes', 0) for video in recent_media)
            transformed_data['metrics']['comments'] = sum(video.get('comments', 0) for video in recent_media)
            transformed_data['metrics']['shares'] = sum(video.get('shares', 0) for video in recent_media)
            transformed_data['metrics']['views'] = sum(video.get('views', 0) for video in recent_media)
        
        return transformed_data
        
    @staticmethod
    def _transform_facebook_data(apify_data):
        """
        Transform Facebook data from Apify format to our standard format.
        
        Args:
            apify_data: Raw data from Apify
            
        Returns:
            dict: Transformed data in our standard format
        """
        # Extract basic profile info
        profile_type = apify_data.get('type', 'profile')
        is_page = profile_type == 'page'
        username = apify_data.get('username') or apify_data.get('pageUrl', '').split('/')[-1]
        followers = apify_data.get('followersCount') or apify_data.get('likesCount', 0)
        
        # Calculate engagement rate if possible
        engagement_rate = 0.0
        recent_posts = apify_data.get('posts', [])
        
        if recent_posts and followers > 0:
            total_likes = sum(post.get('likesCount', 0) for post in recent_posts)
            total_comments = sum(post.get('commentsCount', 0) for post in recent_posts)
            total_shares = sum(post.get('sharesCount', 0) for post in recent_posts)
            post_count = len(recent_posts)
            
            if post_count > 0:
                engagement_rate = ((total_likes + total_comments + total_shares) / post_count) / followers * 100
        
        # Transform to our standard format
        transformed_data = {
            'platform': 'facebook',
            'username': username,
            'full_name': apify_data.get('name', username),
            'profile_url': apify_data.get('url') or f"https://facebook.com/{username}",
            'profile_image': apify_data.get('profilePhoto'),
            'bio': apify_data.get('description') or apify_data.get('about'),
            'website': apify_data.get('website'),
            'followers_count': followers,
            'following_count': apify_data.get('followingCount', 0),
            'posts_count': len(recent_posts) if recent_posts else 0,
            'engagement_rate': engagement_rate,
            'account_type': 'page' if is_page else 'profile',
            'is_verified': apify_data.get('verified', False),
            'metrics': {
                'followers': followers,
                'engagement': engagement_rate,
                'likes': apify_data.get('likesCount', 0),
                'posts': len(recent_posts) if recent_posts else 0
            }
        }
        
        # Add recent posts if available
        if recent_posts:
            recent_media = []
            for post in recent_posts[:5]:  # Include only first 5 posts
                recent_media.append({
                    'id': post.get('postId') or post.get('url', '').split('/')[-1],
                    'caption': post.get('text', ''),
                    'media_type': 'IMAGE' if post.get('photos') else 'VIDEO' if post.get('video') else 'STATUS',
                    'url': post.get('url'),
                    'thumbnail': post.get('photos', [None])[0] if post.get('photos') else None,
                    'timestamp': post.get('time'),
                    'likes': post.get('likesCount', 0),
                    'comments': post.get('commentsCount', 0),
                    'shares': post.get('sharesCount', 0)
                })
            
            transformed_data['recent_media'] = recent_media
            
            # Update metrics with likes and comments
            transformed_data['metrics']['likes'] = sum(post.get('likes', 0) for post in recent_media)
            transformed_data['metrics']['comments'] = sum(post.get('comments', 0) for post in recent_media)
            transformed_data['metrics']['shares'] = sum(post.get('shares', 0) for post in recent_media)
        
        return transformed_data