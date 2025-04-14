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
                "addParentData": True,
                "maxPosts": 30,  # Request more posts to get a full week's worth
                "searchType": "user",
                "searchLimit": 1
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
        original_username = username
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
            
            # Prepare the Actor input - using updated TikTok Scraper
            run_input = {
                "profiles": [username],
                "resultsPerPage": 30,  # Get more posts to ensure a week's worth
                "profileScrapeSections": ["videos"],
                "profileSorting": "latest",
                "excludePinnedPosts": False,
                "maxProfilesPerQuery": 1,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False,
                "shouldDownloadSubtitles": False,
                "shouldDownloadSlideshowImages": False
            }
            
            logger.info(f"Starting Apify run for TikTok profile: {username}")
            
            # Run the actor and wait for it to finish
            # Using updated TikTok Scraper actor (OtzYfK1ndEGdwWFKQ)
            run = client.actor("OtzYfK1ndEGdwWFKQ").call(run_input=run_input)
            
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
            
            # Log the structure of the first item to understand what we're getting
            if len(items) > 0:
                logger.info(f"First TikTok item: {type(items[0])}")
                if isinstance(items[0], dict):
                    logger.info(f"First item keys: {list(items[0].keys())}")
                    
                    # Check if this is a video item vs a profile item
                    if 'authorMeta' in items[0]:
                        logger.info("Found author metadata in video item")
                        author_data = items[0].get('authorMeta', {})
                        logger.info(f"Author data keys: {list(author_data.keys()) if isinstance(author_data, dict) else 'Not a dict'}")
            
            # Check if we're getting video items with author metadata
            if len(items) > 0 and 'authorMeta' in items[0] and isinstance(items[0]['authorMeta'], dict):
                # First modify the data to include profile info
                author_meta = items[0]['authorMeta']
                
                # Extract videos from all items
                videos = items.copy()
                
                # Create a synthetic profile with author meta and videos
                profile_data = {
                    'user': author_meta,
                    'videos': videos,
                    'requestedUsername': username  # Add the requested username to ensure we use it
                }
            else:
                # Find profile data in the standard way
                profile_data = None
                for item in items:
                    # Look for user profile info
                    if item.get('uniqueId') == username or item.get('username') == username:
                        profile_data = item
                        break
                
                if not profile_data:
                    # If we didn't find exact profile match, use the first item
                    profile_data = items[0]
                    # Add the requested username to ensure we use it
                    profile_data['requestedUsername'] = username
            
            # Transform Apify data to match our standard format
            transformed_data = ApifyService._transform_tiktok_data(profile_data, requested_username=username)
            
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
        
        # Ensure we have the latestPosts field
        if 'latestPosts' not in apify_data:
            apify_data['latestPosts'] = []
            
        # Use all available posts for engagement calculation
        if followers > 0 and len(apify_data['latestPosts']) > 0:
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
            for post in apify_data['latestPosts']:  # Include all available posts
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
    def _transform_tiktok_data(apify_data, requested_username=None):
        """
        Transform TikTok data from Apify format to our standard format.
        
        Args:
            apify_data: Raw data from Apify
            requested_username: The username that was originally requested, takes precedence over extracted usernames
            
        Returns:
            dict: Transformed data in our standard format
        """
        logger.info(f"Transforming TikTok data: {type(apify_data)}")
        
        # Log a sample of the data for debugging
        if isinstance(apify_data, dict):
            logger.info(f"TikTok data keys: {list(apify_data.keys())}")
        elif isinstance(apify_data, list) and len(apify_data) > 0:
            logger.info(f"TikTok data is a list with {len(apify_data)} items")
            if isinstance(apify_data[0], dict):
                logger.info(f"First item keys: {list(apify_data[0].keys())}")
        
        # Check if we're dealing with the new format (list of items with user data)
        if isinstance(apify_data, list):
            # Find the user profile data (usually first item with "userInfo")
            user_data = None
            user_videos = []
            
            for item in apify_data:
                if isinstance(item, dict):
                    if 'userInfo' in item and isinstance(item['userInfo'], dict) and 'user' in item['userInfo']:
                        user_data = item['userInfo']['user']
                    if 'itemList' in item and isinstance(item['itemList'], list):
                        user_videos.extend(item['itemList'])
            
            # If we couldn't find user data, use the first item as a fallback
            if not user_data and len(apify_data) > 0 and isinstance(apify_data[0], dict):
                if 'author' in apify_data[0]:
                    user_data = apify_data[0]['author']
                elif 'userInfo' in apify_data[0]:
                    # Try to extract nested data
                    user_info = apify_data[0]['userInfo']
                    if isinstance(user_info, dict) and 'user' in user_info:
                        user_data = user_info['user']
                    
            # If we still couldn't find videos, check if the items themselves are videos
            if not user_videos:
                for item in apify_data:
                    if isinstance(item, dict) and 'id' in item and 'desc' in item:  # Looks like a video
                        user_videos.append(item)
                        
            # Now use the extracted data
            apify_data = {
                'user': user_data or {},  # Ensure user_data is not None
                'videos': user_videos
            }
        
        # Extract user data (handling both old and new format)
        user_data = apify_data.get('user', apify_data) or {}
        videos = apify_data.get('videos', [])
        if not videos and isinstance(apify_data, dict) and 'itemList' in apify_data:
            videos = apify_data['itemList']
            
        # Calculate engagement rate if possible
        engagement_rate = 0.0
        followers = user_data.get('followerCount', 0)
        if not followers and 'stats' in user_data and isinstance(user_data['stats'], dict):
            followers = user_data['stats'].get('followerCount', 0)
        
        if videos and followers > 0:
            # Handle different field names in the new format
            total_likes = 0
            total_comments = 0
            total_shares = 0
            
            for video in videos:
                if not isinstance(video, dict):
                    continue
                    
                # Try all possible field names for different API versions
                like_count = 0
                if 'likeCount' in video:
                    like_count = video['likeCount']
                elif 'stats' in video and isinstance(video['stats'], dict):
                    like_count = video['stats'].get('diggCount', 0) or video['stats'].get('likeCount', 0)
                
                comment_count = 0
                if 'commentCount' in video:
                    comment_count = video['commentCount']
                elif 'stats' in video and isinstance(video['stats'], dict):
                    comment_count = video['stats'].get('commentCount', 0)
                
                share_count = 0
                if 'shareCount' in video:
                    share_count = video['shareCount']
                elif 'stats' in video and isinstance(video['stats'], dict):
                    share_count = video['stats'].get('shareCount', 0)
                
                total_likes += like_count
                total_comments += comment_count
                total_shares += share_count
            
            video_count = len(videos)
            
            if video_count > 0 and followers > 0:
                engagement_rate = ((total_likes + total_comments + total_shares) / video_count) / followers * 100
        
        # First check if we have a requested username - this takes precedence
        username = ''
        if requested_username:
            username = requested_username
            logger.info(f"Using requested username: {username}")
        else:
            # Check if the requested username is stored in the data
            if isinstance(apify_data, dict) and 'requestedUsername' in apify_data:
                username = apify_data['requestedUsername']
                logger.info(f"Using requestedUsername from data: {username}")
            else:
                # Fall back to extracted usernames from various fields
                if 'username' in user_data:
                    username = user_data['username']
                elif 'uniqueId' in user_data:
                    username = user_data['uniqueId']
                elif 'nickname' in user_data:
                    username = user_data['nickname']
                
                # If we still don't have a username, try to find an identifier
                if not username and 'id' in user_data:
                    username = f"user_{user_data['id']}"
                
                # Ensure we have a valid username
                if not username:
                    # Generate a random username as a last resort
                    import random
                    import string
                    username = 'tiktok_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                    logger.warning(f"Could not find username in TikTok data, generated random username: {username}")
        
        nickname = ''
        if 'nickname' in user_data:
            nickname = user_data['nickname']
        elif 'fullName' in user_data:
            nickname = user_data['fullName']
        else:
            nickname = username  # Fall back to username
        
        bio = ''
        if 'signature' in user_data:
            bio = user_data['signature']
        elif 'biography' in user_data:
            bio = user_data['biography']
        elif 'bio' in user_data:
            bio = user_data['bio']
        
        profile_image = ''
        for img_field in ['avatarThumb', 'avatarMedium', 'avatarLarger', 'profileImage']:
            if img_field in user_data and user_data[img_field]:
                profile_image = user_data[img_field]
                break
        
        # Stats might be nested or directly on the user object
        stats = user_data.get('stats', {}) if isinstance(user_data.get('stats'), dict) else user_data
        
        # Get followers count
        if 'followerCount' in stats:
            followers = stats['followerCount']
        
        # Get following count
        following = 0
        if 'followingCount' in stats:
            following = stats['followingCount']
        elif 'followingCount' in user_data:
            following = user_data['followingCount']
        
        # Get posts count
        posts_count = 0
        if 'videoCount' in stats:
            posts_count = stats['videoCount']
        elif 'videoCount' in user_data:
            posts_count = user_data['videoCount']
        else:
            posts_count = len(videos)  # Fallback to video count
        
        # Get likes count
        likes_count = 0
        if 'heartCount' in stats:
            likes_count = stats['heartCount']
        elif 'diggCount' in stats:
            likes_count = stats['diggCount']
        elif 'heartCount' in user_data:
            likes_count = user_data['heartCount']
        
        # Transform to our standard format
        transformed_data = {
            'platform': 'tiktok',  # Always set platform to 'tiktok'
            'username': username,  # Ensure username is never empty
            'full_name': nickname,
            'profile_url': f"https://tiktok.com/@{username}",
            'profile_image': profile_image,
            'bio': bio,
            'followers_count': followers,
            'following_count': following,
            'posts_count': posts_count,
            'engagement_rate': engagement_rate,
            'is_verified': bool(user_data.get('verified', False) or user_data.get('isVerified', False)),
            'metrics': {
                'followers': followers,
                'engagement': engagement_rate,
                'posts': posts_count,
                'likes': likes_count
            }
        }
        
        # Add recent videos if available
        if videos:
            recent_media = []
            for video in videos:
                if not isinstance(video, dict):
                    continue
                    
                # Try to extract video ID
                video_id = ''
                if 'id' in video:
                    video_id = str(video['id'])
                elif 'videoId' in video:
                    video_id = str(video['videoId'])
                elif 'itemId' in video:
                    video_id = str(video['itemId'])
                else:
                    # Generate a random ID as a last resort
                    import random
                    video_id = f"video_{random.randint(10000, 99999)}"
                
                # Get video caption/description
                caption = ''
                if 'description' in video:
                    caption = video['description']
                elif 'desc' in video:
                    caption = video['desc']
                elif 'text' in video:
                    caption = video['text']
                
                # Get video URL
                url = ''
                if 'webVideoUrl' in video:
                    url = video['webVideoUrl']
                elif 'shareUrl' in video:
                    url = video['shareUrl']
                elif 'video' in video and isinstance(video['video'], dict) and 'playAddr' in video['video']:
                    url = video['video']['playAddr']
                else:
                    # Construct URL from username and video ID
                    url = f"https://www.tiktok.com/@{username}/video/{video_id}"
                
                # Try to get thumbnail from various possible fields
                thumbnail = None
                if 'covers' in video:
                    if isinstance(video['covers'], list) and video['covers']:
                        thumbnail = video['covers'][0]
                    elif isinstance(video['covers'], str):
                        thumbnail = video['covers']
                elif 'thumbnailUrl' in video:
                    thumbnail = video['thumbnailUrl']
                elif 'thumbnail' in video:
                    thumbnail = video['thumbnail']
                elif 'cover' in video:
                    thumbnail = video['cover']
                
                # Get timestamp, which could be in various formats
                timestamp = None
                if 'createTime' in video:
                    timestamp = video['createTime']
                elif 'createTimeISO' in video:
                    timestamp = video['createTimeISO']
                elif 'timestamp' in video:
                    timestamp = video['timestamp']
                
                # Get engagement statistics
                stats = video.get('stats', {}) if isinstance(video.get('stats'), dict) else video
                
                likes = 0
                if 'likeCount' in stats:
                    likes = stats['likeCount']
                elif 'diggCount' in stats:
                    likes = stats['diggCount']
                
                comments = 0
                if 'commentCount' in stats:
                    comments = stats['commentCount']
                
                shares = 0
                if 'shareCount' in stats:
                    shares = stats['shareCount']
                
                views = 0
                if 'playCount' in stats:
                    views = stats['playCount']
                elif 'viewCount' in stats:
                    views = stats['viewCount']
                
                # Add to recent media list
                recent_media.append({
                    'id': video_id,
                    'caption': caption,
                    'media_type': 'VIDEO',
                    'url': url,
                    'thumbnail': thumbnail,
                    'timestamp': timestamp,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'views': views
                })
            
            # Add recent media to transformed data
            if recent_media:
                transformed_data['recent_media'] = recent_media
                
                # Update metrics with totals
                transformed_data['metrics']['likes'] = sum(post.get('likes', 0) for post in recent_media)
                transformed_data['metrics']['comments'] = sum(post.get('comments', 0) for post in recent_media)
                transformed_data['metrics']['shares'] = sum(post.get('shares', 0) for post in recent_media)
                transformed_data['metrics']['views'] = sum(post.get('views', 0) for post in recent_media)
        
        # Log the transformed data structure
        logger.info(f"Transformed TikTok data: username={transformed_data['username']}, platform={transformed_data['platform']}")
        
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
            for post in recent_posts:  # Include all available posts
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