"""
Service for interacting with social media platforms.
"""
import requests
import json
import logging
import random
import re
import html
import time
from datetime import datetime, timedelta
from app.extensions import db
from app.models import Influencer, InfluencerMetric, Category
from app.services.oauth_service import get_token
from app.services.apify_service import ApifyService

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
        
        # Try to use official API first
        try:
            token_data = get_token(user_id, 'instagram')
            if token_data:
                profile_data = SocialMediaService._fetch_instagram_via_api(token_data, username)
                if profile_data and 'error' not in profile_data:
                    logger.info(f"Successfully fetched Instagram profile via official API")
                    return profile_data
        except Exception as e:
            logger.warning(f"Error using official Instagram API: {str(e)}")
        
        # Fallback to Apify service if username is provided
        if username:
            try:
                logger.info(f"Attempting to fetch Instagram profile via Apify: {username}")
                profile_data = ApifyService.fetch_instagram_profile(username)
                if profile_data and 'error' not in profile_data:
                    logger.info(f"Successfully fetched Instagram profile via Apify")
                    return profile_data
            except Exception as e:
                logger.warning(f"Error fetching Instagram data via Apify: {str(e)}")
        
        # Fallback to scraping public data if available
        try:
            logger.info(f"Attempting to fetch Instagram profile via web scraping: {username}")
            profile_data = SocialMediaService._fetch_instagram_public_data(username)
            if profile_data and 'error' not in profile_data:
                logger.info(f"Successfully fetched Instagram profile via web scraping")
                return profile_data
        except Exception as e:
            logger.warning(f"Error fetching public Instagram data: {str(e)}")
            
        # Return None if all methods fail
        logger.error(f"All methods to fetch Instagram profile failed")
        return None
    
    @staticmethod
    def _fetch_instagram_via_api(token_data, username=None):
        """
        Fetch Instagram profile using the official API.
        """
        access_token = token_data['access_token']
        
        # First we need to get all connected Instagram accounts through the Facebook Graph API
        try:
            # The correct approach is to first get the Facebook pages that the user has access to
            accounts_url = "https://graph.facebook.com/v16.0/me/accounts"
            params = {
                'access_token': access_token,
                'fields': 'instagram_business_account,name,id'
            }
            logger.info(f"Requesting Facebook Pages with Instagram Business accounts")
            
            try:
                response = requests.get(accounts_url, params=params, timeout=10)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                logger.error("Timeout when connecting to Facebook Graph API")
                return {
                    'error': 'api_timeout',
                    'message': 'Connection to Facebook API timed out. Please try again later.'
                }
            except requests.exceptions.HTTPError as http_err:
                status_code = getattr(http_err.response, 'status_code', 0)
                error_msg = getattr(http_err.response, 'text', str(http_err))
                
                if status_code == 401 or status_code == 403:
                    logger.error(f"Authentication error when connecting to Facebook API: {error_msg}")
                    return {
                        'error': 'auth_error',
                        'message': 'Authentication failed. Please reconnect your Facebook account.'
                    }
                elif status_code == 429:
                    logger.error(f"Rate limit exceeded for Facebook API: {error_msg}")
                    return {
                        'error': 'rate_limit',
                        'message': 'Facebook API rate limit exceeded. Please try again later.'
                    }
                else:
                    logger.error(f"HTTP error when connecting to Facebook API: {error_msg}")
                    return {
                        'error': 'api_error',
                        'message': f"Facebook API error: {error_msg}"
                    }
            except requests.exceptions.ConnectionError:
                logger.error("Network connection error when connecting to Facebook API")
                return {
                    'error': 'connection_error',
                    'message': 'Network connection error. Please check your internet connection.'
                }
            except Exception as e:
                logger.error(f"Unexpected error when connecting to Facebook API: {str(e)}")
                return {
                    'error': 'api_error',
                    'message': 'An unexpected error occurred while connecting to Facebook API.'
                }
            
            try:
                accounts_data = response.json()
            except ValueError:
                logger.error("Invalid JSON response from Facebook API")
                return {
                    'error': 'invalid_response',
                    'message': 'Invalid response from Facebook API.'
                }
            
            logger.info(f"Found {len(accounts_data.get('data', []))} Facebook Pages")
            
            # Check for API errors in the response
            if 'error' in accounts_data:
                error_msg = accounts_data.get('error', {}).get('message', 'Unknown API error')
                error_code = accounts_data.get('error', {}).get('code', 0)
                
                logger.error(f"Facebook API error: {error_code} - {error_msg}")
                return {
                    'error': 'facebook_api_error',
                    'message': f"Facebook API error: {error_msg}",
                    'code': error_code
                }
            
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
                logger.warning(f"No Instagram Business accounts found")
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
                    
                    try:
                        ig_response = requests.get(ig_url, params=params, timeout=10)
                        ig_response.raise_for_status()
                        ig_data = ig_response.json()
                        
                        if ig_data.get('username') == username:
                            instagram_account = account
                            instagram_user_id = ig_id
                            break
                    except Exception as e:
                        logger.warning(f"Error checking Instagram account {ig_id}: {str(e)}")
                        continue
                
                if not instagram_account:
                    logger.error(f"Instagram account with username {username} not found")
                    return {
                        'error': 'account_not_found',
                        'message': f"Instagram account with username {username} was not found among your connected business accounts."
                    }
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
            
            try:
                profile_response = requests.get(profile_url, params=params, timeout=10)
                profile_response.raise_for_status()
                profile_data = profile_response.json()
                logger.info(f"Got profile data for Instagram account {profile_data.get('username')}")
            except Exception as e:
                logger.error(f"Error fetching Instagram profile data: {str(e)}")
                return {
                    'error': 'profile_fetch_error',
                    'message': f"Failed to fetch Instagram profile data: {str(e)}"
                }
            
            # Get recent media for engagement metrics
            media_url = f"https://graph.facebook.com/v16.0/{instagram_user_id}/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count',
                'limit': 25,  # Get more posts for better engagement calculation
                'access_token': access_token
            }
            
            try:
                media_response = requests.get(media_url, params=params, timeout=10)
                media_response.raise_for_status()
                media_data = media_response.json()
                media_items = media_data.get('data', [])
                logger.info(f"Retrieved {len(media_items)} media items")
            except Exception as e:
                logger.warning(f"Error fetching Instagram media: {str(e)}")
                # Non-fatal error, continue with empty media items
                media_items = []
            
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
                insights_response = requests.get(insights_url, params=params, timeout=10)
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
            
            # Try to determine categories based on bio and content
            categories = SocialMediaService._determine_categories(
                bio=profile_data.get('biography', ''),
                recent_content=[post.get('caption', '') for post in media_items if 'caption' in post]
            )
            if categories:
                account_data['categories'] = categories
            
            return account_data
            
        except Exception as e:
            logger.error(f"Error fetching Instagram profile data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': 'unexpected_error',
                'message': f"An unexpected error occurred: {str(e)}"
            }
    
    @staticmethod
    def _fetch_instagram_public_data(username):
        """
        Fetch publicly available Instagram profile data by scraping.
        This is a fallback method when official API access is not available.
        
        Note: Web scraping may be against Instagram's terms of service.
        This should only be used for educational purposes.
        """
        if not username:
            return {
                'error': 'missing_username',
                'message': 'Username is required to fetch Instagram profile data'
            }
            
        # Remove @ if present
        username = username.replace('@', '').strip()
        
        try:
            # Attempt to get public profile page
            logger.info(f"Attempting to fetch public data for Instagram user: {username}")
            
            # Use a reasonably modern user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            # Request profile page with proper error handling
            url = f"https://www.instagram.com/{username}/"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                logger.error(f"Timeout when fetching Instagram page for {username}")
                return {
                    'error': 'timeout',
                    'message': 'Connection timed out while fetching Instagram profile. Please try again later.'
                }
            except requests.exceptions.HTTPError as http_err:
                status_code = getattr(http_err.response, 'status_code', 0)
                
                if status_code == 404:
                    logger.error(f"Instagram profile not found for {username}")
                    return {
                        'error': 'profile_not_found',
                        'message': f"Instagram profile '@{username}' does not exist or is not publicly accessible."
                    }
                elif status_code == 429:
                    logger.error(f"Rate limit exceeded when fetching Instagram profile for {username}")
                    return {
                        'error': 'rate_limit',
                        'message': 'Too many requests. Please try again later.'
                    }
                else:
                    logger.error(f"HTTP error {status_code} when fetching Instagram profile for {username}")
                    return {
                        'error': 'http_error',
                        'message': f"Failed to fetch Instagram profile: HTTP error {status_code}"
                    }
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error when fetching Instagram profile for {username}")
                return {
                    'error': 'connection_error',
                    'message': 'Network connection error. Please check your internet connection.'
                }
            except Exception as e:
                logger.error(f"Unexpected error when fetching Instagram page for {username}: {str(e)}")
                return {
                    'error': 'request_error',
                    'message': 'An error occurred while fetching the Instagram profile.'
                }
                
            # Look for JSON data in the page
            html_content = response.text
            
            # Common pattern in Instagram HTML where profile data is stored
            # This pattern may change as Instagram updates their site
            json_data_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            json_matches = re.findall(json_data_pattern, html_content, re.DOTALL)
            
            if not json_matches:
                # Try alternative pattern used by Instagram
                json_data_pattern = r'window\._sharedData = (.*?);</script>'
                json_matches = re.findall(json_data_pattern, html_content, re.DOTALL)
            
            if not json_matches:
                # Try newer pattern that Instagram might be using
                json_data_pattern = r'window\.__additionalDataLoaded\s*\(\s*[\'"]profilePage[\'"]\s*,\s*(.*?)\);<\/script>'
                json_matches = re.findall(json_data_pattern, html_content, re.DOTALL)
            
            if not json_matches:
                logger.warning(f"Could not find profile data in Instagram page for {username}")
                return {
                    'error': 'data_extraction_failed',
                    'message': 'Could not extract profile data from Instagram. The page structure may have changed.'
                }
                
            # Attempt to parse JSON data
            parsed_data = None
            error_messages = []
            
            for json_str in json_matches:
                try:
                    # Unescape HTML entities if present
                    json_str = html.unescape(json_str)
                    data = json.loads(json_str)
                    
                    # Extract profile info based on Instagram's current structure
                    # First try LD+JSON structure
                    if '@type' in data and data.get('@type') == 'ProfilePage':
                        followers = 0
                        if 'mainEntityofPage' in data and 'interactionStatistic' in data['mainEntityofPage']:
                            for stat in data['mainEntityofPage']['interactionStatistic']:
                                if stat.get('name') == 'followers':
                                    followers = int(stat.get('userInteractionCount', 0))
                        
                        # Build profile data
                        profile_data = {
                            'platform': 'instagram',
                            'username': username,
                            'full_name': data.get('name', username),
                            'profile_url': url,
                            'profile_image': data.get('image', ''),
                            'bio': data.get('description', ''),
                            'followers_count': followers,
                            'engagement_rate': 0.0,  # Can't accurately calculate without post data
                            'account_type': 'personal'  # Assumption for public profiles
                        }
                        
                        # Try to determine categories
                        categories = SocialMediaService._determine_categories(bio=profile_data.get('bio', ''))
                        if categories:
                            profile_data['categories'] = categories
                            
                        parsed_data = profile_data
                        break
                        
                    # Try shared data structure
                    elif 'entry_data' in data and 'ProfilePage' in data['entry_data']:
                        profile = data['entry_data']['ProfilePage'][0]['graphql']['user']
                        
                        # Build profile data
                        profile_data = {
                            'platform': 'instagram',
                            'username': profile.get('username', username),
                            'full_name': profile.get('full_name', username),
                            'profile_url': url,
                            'profile_image': profile.get('profile_pic_url_hd', profile.get('profile_pic_url', '')),
                            'bio': profile.get('biography', ''),
                            'followers_count': profile.get('edge_followed_by', {}).get('count', 0),
                            'following_count': profile.get('edge_follow', {}).get('count', 0),
                            'posts_count': profile.get('edge_owner_to_timeline_media', {}).get('count', 0),
                            'engagement_rate': 0.0,  # Calculate if post data is available
                            'account_type': 'verified' if profile.get('is_verified', False) else 'personal'
                        }
                        
                        # Try to extract post data if available
                        if 'edge_owner_to_timeline_media' in profile and 'edges' in profile['edge_owner_to_timeline_media']:
                            posts = profile['edge_owner_to_timeline_media']['edges']
                            if posts:
                                total_likes = sum(post['node'].get('edge_liked_by', {}).get('count', 0) for post in posts)
                                total_comments = sum(post['node'].get('edge_media_to_comment', {}).get('count', 0) for post in posts)
                                
                                if len(posts) > 0 and profile_data['followers_count'] > 0:
                                    profile_data['engagement_rate'] = ((total_likes + total_comments) / len(posts)) / profile_data['followers_count'] * 100
                        
                        # Try to determine categories
                        categories = SocialMediaService._determine_categories(bio=profile_data.get('bio', ''))
                        if categories:
                            profile_data['categories'] = categories
                            
                        parsed_data = profile_data
                        break
                        
                    # Try newer data structure
                    elif 'graphql' in data and 'user' in data['graphql']:
                        profile = data['graphql']['user']
                        
                        # Build profile data (similar to structure above)
                        profile_data = {
                            'platform': 'instagram',
                            'username': profile.get('username', username),
                            'full_name': profile.get('full_name', username),
                            'profile_url': url,
                            'profile_image': profile.get('profile_pic_url_hd', profile.get('profile_pic_url', '')),
                            'bio': profile.get('biography', ''),
                            'followers_count': profile.get('edge_followed_by', {}).get('count', 0),
                            'following_count': profile.get('edge_follow', {}).get('count', 0),
                            'posts_count': profile.get('edge_owner_to_timeline_media', {}).get('count', 0),
                            'engagement_rate': 0.0,
                            'account_type': 'verified' if profile.get('is_verified', False) else 'personal'
                        }
                        
                        # Determine categories and calculate engagement similarly to above
                        categories = SocialMediaService._determine_categories(bio=profile_data.get('bio', ''))
                        if categories:
                            profile_data['categories'] = categories
                            
                        parsed_data = profile_data
                        break
                        
                except Exception as e:
                    error_message = f"Error parsing Instagram profile JSON: {str(e)}"
                    logger.warning(error_message)
                    error_messages.append(error_message)
                    continue
            
            # If we successfully parsed the data, return it
            if parsed_data:
                return parsed_data
                
            # If we get here, we couldn't extract the data
            logger.warning(f"Failed to extract profile data from Instagram page for {username}")
            
            # Return detailed error with the specific parsing errors encountered
            return {
                'error': 'parsing_failed',
                'message': 'Failed to parse Instagram profile data',
                'details': error_messages[:3]  # Include the first few error messages for debugging
            }
            
        except Exception as e:
            logger.error(f"Error fetching public Instagram data for {username}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': 'unexpected_error',
                'message': f"An unexpected error occurred while fetching Instagram data: {str(e)}"
            }
    
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
        logger.info(f"Fetching TikTok profile for user_id={user_id}, username={username}")
        
        # Try to use official API first
        try:
            token_data = get_token(user_id, 'tiktok')
            if token_data:
                profile_data = SocialMediaService._fetch_tiktok_via_api(token_data, username)
                if profile_data and 'error' not in profile_data:
                    logger.info(f"Successfully fetched TikTok profile via official API")
                    return profile_data
        except Exception as e:
            logger.warning(f"Error using official TikTok API: {str(e)}")
        
        # Fallback to Apify service if username is provided
        if username:
            try:
                logger.info(f"Attempting to fetch TikTok profile via Apify: {username}")
                profile_data = ApifyService.fetch_tiktok_profile(username)
                if profile_data and 'error' not in profile_data:
                    logger.info(f"Successfully fetched TikTok profile via Apify")
                    return profile_data
            except Exception as e:
                logger.warning(f"Error fetching TikTok data via Apify: {str(e)}")
        
        # Fallback to scraping public data if available
        try:
            logger.info(f"Attempting to fetch TikTok profile via web scraping: {username}")
            profile_data = SocialMediaService._fetch_tiktok_public_data(username)
            if profile_data and 'error' not in profile_data:
                logger.info(f"Successfully fetched TikTok profile via web scraping")
                return profile_data
        except Exception as e:
            logger.warning(f"Error fetching public TikTok data: {str(e)}")
            
        # Return None if all methods fail
        logger.error(f"All methods to fetch TikTok profile failed")
        return None
        
    @staticmethod
    def _fetch_tiktok_via_api(token_data, username=None):
        """Fetch TikTok profile using the official API."""
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
            
            profile_data = {
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
            
            # Try to determine categories
            categories = SocialMediaService._determine_categories(bio=user_data.get('bio_description', ''))
            if categories:
                profile_data['categories'] = categories
                
            return profile_data
            
        except Exception as e:
            logger.error(f"Error fetching TikTok profile data: {str(e)}")
            return None
    
    @staticmethod
    def _fetch_tiktok_public_data(username):
        """
        Fetch publicly available TikTok profile data by scraping.
        This is a fallback method when official API access is not available.
        
        Note: Web scraping may be against TikTok's terms of service.
        This should only be used for educational purposes.
        """
        if not username:
            return None
            
        # Remove @ if present
        username = username.replace('@', '').strip()
        
        try:
            # Attempt to get public profile page
            logger.info(f"Attempting to fetch public data for TikTok user: {username}")
            
            # Use a reasonably modern user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            # Request profile page
            url = f"https://www.tiktok.com/@{username}"
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check for successful response
            if response.status_code != 200:
                logger.warning(f"Failed to fetch TikTok profile page, status: {response.status_code}")
                return None
                
            # Look for JSON data in the page
            html_content = response.text
            
            # TikTok typically has a JSON blob with user data
            json_data_pattern = r'<script id="SIGI_STATE" type="application/json">(.*?)</script>'
            json_matches = re.findall(json_data_pattern, html_content, re.DOTALL)
            
            if not json_matches:
                logger.warning("Could not find profile data in TikTok page")
                return None
                
            # Attempt to parse JSON data
            try:
                json_str = json_matches[0]
                data = json.loads(json_str)
                
                # TikTok's structure varies, but often has a "UserModule" or similar
                user_data = None
                
                # Try common paths for user data
                for key in ['UserModule', 'userInfo', 'users']:
                    if key in data:
                        if 'users' in data[key] and username in data[key]['users']:
                            user_data = data[key]['users'][username]
                            break
                        elif 'userInfo' in data[key] and 'user' in data[key]['userInfo']:
                            user_data = data[key]['userInfo']['user']
                            break
                
                if not user_data:
                    logger.warning("Could not locate user data in TikTok JSON")
                    return None
                
                # Extract profile info
                profile_data = {
                    'platform': 'tiktok',
                    'username': username,
                    'full_name': user_data.get('nickname', username),
                    'profile_url': url,
                    'profile_image': user_data.get('avatarLarger', user_data.get('avatarMedium', '')),
                    'bio': user_data.get('signature', ''),
                    'followers_count': user_data.get('followerCount', 0),
                    'following_count': user_data.get('followingCount', 0),
                    'posts_count': user_data.get('videoCount', 0),
                    'engagement_rate': 0.0,  # Hard to calculate without post data
                    'metrics': {
                        'followers': user_data.get('followerCount', 0),
                        'likes': user_data.get('heartCount', 0),
                        'posts': user_data.get('videoCount', 0)
                    }
                }
                
                # Try to determine categories
                categories = SocialMediaService._determine_categories(bio=profile_data.get('bio', ''))
                if categories:
                    profile_data['categories'] = categories
                    
                return profile_data
                
            except Exception as e:
                logger.warning(f"Error parsing TikTok profile JSON: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching public TikTok data: {str(e)}")
            return None
    
    @staticmethod
    def fetch_facebook_profile(user_id, username=None):
        """
        Fetch Facebook profile data for a user.
        
        Args:
            user_id: The user ID to get token from
            username: Facebook username (optional)
            
        Returns:
            dict: Facebook profile data or None if error
        """
        logger.info(f"Fetching Facebook profile for user_id={user_id}, username={username}")
        
        # Try to use official API first (if implemented)
        # try:
        #     token_data = get_token(user_id, 'facebook')
        #     if token_data:
        #         # Call Facebook API using the token
        #         pass
        # except Exception as e:
        #     logger.warning(f"Error using official Facebook API: {str(e)}")
        
        # Use Apify service if username is provided
        if username:
            try:
                logger.info(f"Attempting to fetch Facebook profile via Apify: {username}")
                profile_data = ApifyService.fetch_facebook_profile(username)
                if profile_data and 'error' not in profile_data:
                    logger.info(f"Successfully fetched Facebook profile via Apify")
                    return profile_data
            except Exception as e:
                logger.warning(f"Error fetching Facebook data via Apify: {str(e)}")
        
        # If we couldn't fetch the profile, return None
        logger.error(f"All methods to fetch Facebook profile failed")
        return None
    
    @staticmethod
    def _determine_categories(bio='', recent_content=None):
        """
        Determine likely categories for an influencer based on bio and content.
        This is a simple keyword-based approach - in a production system, 
        you would use a more sophisticated ML-based classification.
        """
        if recent_content is None:
            recent_content = []
            
        # Combine bio and recent content for analysis
        text = bio.lower() + ' ' + ' '.join([content.lower() for content in recent_content])
        
        # Dictionary of categories and their associated keywords
        category_keywords = {
            'lifestyle': ['lifestyle', 'life', 'daily', 'day', 'routine', 'home', 'living', 'travel'],
            'moda': ['fashion', 'moda', 'style', 'estilo', 'clothes', 'roupa', 'outfit', 'look'],
            'beleza': ['beauty', 'beleza', 'makeup', 'maquiagem', 'skin', 'skincare', 'pele', 'hair', 'cabelo'],
            'família': ['family', 'família', 'mom', 'mãe', 'dad', 'pai', 'kids', 'filhos', 'baby', 'bebê'],
            'fitness': ['fitness', 'workout', 'treino', 'gym', 'academia', 'exercise', 'exercício', 'health', 'saúde'],
            'comida': ['food', 'comida', 'recipe', 'receita', 'cooking', 'cozinha', 'chef', 'baking'],
            'música': ['music', 'música', 'singer', 'cantor', 'song', 'música', 'artist', 'artista'],
            'humor': ['comedy', 'comédia', 'funny', 'engraçado', 'humor', 'joke', 'piada', 'laugh'],
            'tecnologia': ['tech', 'technology', 'tecnologia', 'gadget', 'code', 'código', 'programming', 'developer'],
            'gaming': ['game', 'gaming', 'gamer', 'videogame', 'streamer', 'stream'],
            'business': ['business', 'negócio', 'entrepreneur', 'empreendedor', 'marketing', 'finance', 'finanças'],
            'arte': ['art', 'arte', 'artist', 'artista', 'design', 'drawing', 'desenho', 'painting', 'pintura'],
            'educação': ['education', 'educação', 'teacher', 'professor', 'learn', 'aprender', 'school', 'escola']
        }
        
        # Find matching categories
        matches = {}
        for category, keywords in category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                matches[category] = score
        
        # Sort by score and return top categories
        sorted_categories = sorted(matches.items(), key=lambda x: x[1], reverse=True)
        return [category for category, score in sorted_categories[:3] if score > 0]
    
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
        
        if not platform or not username:
            logger.error(f"Missing required fields in profile data: platform or username")
            return None
        
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
            logger.info(f"Updated existing influencer: {username} on {platform}")
        else:
            # Create new influencer
            try:
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
                logger.info(f"Created new influencer: {username} on {platform}")
            except Exception as e:
                logger.error(f"Error creating influencer {username} on {platform}: {str(e)}")
                db.session.rollback()
                return None
        
        try:
            # Save metrics
            metrics = profile_data.get('metrics', {})
            if metrics:
                # Check if we already have metrics for today
                today = datetime.utcnow().date()
                existing_metric = InfluencerMetric.query.filter_by(
                    influencer=influencer,
                    date=today
                ).first()
                
                if existing_metric:
                    # Update existing metric
                    if 'followers' in metrics:
                        existing_metric.followers = metrics.get('followers')
                    if 'engagement' in metrics:
                        existing_metric.engagement = metrics.get('engagement')
                    if 'posts' in metrics:
                        existing_metric.posts = metrics.get('posts')
                    if 'likes' in metrics:
                        existing_metric.likes = metrics.get('likes')
                    if 'comments' in metrics:
                        existing_metric.comments = metrics.get('comments')
                    if 'shares' in metrics:
                        existing_metric.shares = metrics.get('shares')
                    if 'views' in metrics:
                        existing_metric.views = metrics.get('views')
                    logger.info(f"Updated existing metrics for {username} on {platform}")
                else:
                    # Create new metric
                    metric = InfluencerMetric(
                        influencer=influencer,
                        date=today,
                        followers=metrics.get('followers'),
                        engagement=metrics.get('engagement'),
                        posts=metrics.get('posts'),
                        likes=metrics.get('likes'),
                        comments=metrics.get('comments'),
                        shares=metrics.get('shares'),
                        views=metrics.get('views')
                    )
                    db.session.add(metric)
                    logger.info(f"Created new metrics for {username} on {platform}")
            
            # Add categories if available
            if 'categories' in profile_data and isinstance(profile_data['categories'], list):
                for cat_name in profile_data['categories']:
                    # Check if category exists
                    category = Category.query.filter_by(name=cat_name).first()
                    if not category:
                        # Create new category
                        category = Category(name=cat_name, description=f"Category for {cat_name}")
                        db.session.add(category)
                    
                    # Add category to influencer if not already present
                    if category not in influencer.categories:
                        influencer.categories.append(category)
                logger.info(f"Added {len(profile_data['categories'])} categories to {username}")
            
            # Save recent posts if available
            if 'recent_media' in profile_data and profile_data['recent_media']:
                SocialMediaService.save_recent_posts(influencer.id, profile_data['recent_media'], platform)
            
            db.session.commit()
            
            # After saving all the data, calculate all metrics
            try:
                # Import here to avoid circular imports
                from app.services.engagement_service import EngagementService
                logger.info(f"Calculating engagement metrics for influencer {influencer.id} - {username}")
                # Calculate metrics in a try-except block so it doesn't block the main flow if it fails
                EngagementService.calculate_engagement_metrics(influencer.id)
                
                # Calculate reach metrics
                from app.services.reach_service import ReachService
                logger.info(f"Calculating reach metrics for influencer {influencer.id} - {username}")
                ReachService.calculate_reach_metrics(influencer.id)
                
                # Calculate growth metrics
                from app.services.growth_service import GrowthService
                logger.info(f"Calculating growth metrics for influencer {influencer.id} - {username}")
                GrowthService.calculate_growth_metrics(influencer.id)
                
                # Calculate relevance score (must be calculated after all other metrics)
                from app.services.score_service import ScoreService
                logger.info(f"Calculating relevance score for influencer {influencer.id} - {username}")
                ScoreService.calculate_relevance_score(influencer.id)
            except Exception as e:
                logger.error(f"Error calculating metrics for {username}: {str(e)}")
                # Continue anyway, as the basic influencer data is already saved
            
            return influencer
            
        except Exception as e:
            logger.error(f"Error saving influencer data for {username} on {platform}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def save_recent_posts(influencer_id, recent_media, platform):
        """
        Save recent social media posts for an influencer.
        
        Args:
            influencer_id (int): The ID of the influencer
            recent_media (list): List of recent posts from social media platform
            platform (str): Social media platform (instagram, tiktok, facebook)
            
        Returns:
            int: Number of posts saved
        """
        from app.models.social_media import SocialPost
        
        if not recent_media or not influencer_id:
            return 0
        
        logger.info(f"Saving {len(recent_media)} recent posts for influencer {influencer_id}")
        posts_saved = 0
        
        try:
            # Parse datetime based on platform-specific format
            for post_data in recent_media:
                # Generate a unique post ID if not provided
                post_id = post_data.get('id')
                if not post_id:
                    # Create a deterministic ID based on influencer ID, URL and timestamp
                    import hashlib
                    url = post_data.get('url', '')
                    timestamp = post_data.get('timestamp', '')
                    data_to_hash = f"{influencer_id}:{url}:{timestamp}"
                    post_id = hashlib.md5(data_to_hash.encode()).hexdigest()
                
                # Check if post already exists in database
                existing_post = SocialPost.query.filter_by(
                    platform=platform,
                    post_id=post_id
                ).first()
                
                # Parse timestamp to datetime object
                posted_at = None
                if 'timestamp' in post_data and post_data['timestamp']:
                    try:
                        timestamp = post_data['timestamp']
                        # Handle different timestamp formats
                        if isinstance(timestamp, datetime):
                            posted_at = timestamp
                        elif isinstance(timestamp, str):
                            # Try different formats based on platform
                            try:
                                # ISO format (common for API responses): 2023-04-14T15:30:45Z
                                posted_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            except ValueError:
                                try:
                                    # Facebook/Instagram format: 2023-04-14T15:30:45+0000
                                    posted_at = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
                                except ValueError:
                                    try:
                                        # Unix timestamp (common for TikTok)
                                        posted_at = datetime.fromtimestamp(int(timestamp))
                                    except ValueError:
                                        logger.warning(f"Could not parse timestamp: {timestamp}")
                        elif isinstance(timestamp, (int, float)):
                            # Unix timestamp
                            posted_at = datetime.fromtimestamp(timestamp)
                    except Exception as e:
                        logger.warning(f"Error parsing post timestamp: {str(e)}")
                
                # Default to current time if we couldn't parse the timestamp
                if not posted_at:
                    posted_at = datetime.utcnow()
                
                # Determine content type based on media_type field
                content_type = post_data.get('media_type', '').lower()
                if content_type == '':
                    # Try to infer from other data
                    if 'video' in post_data.get('url', '').lower():
                        content_type = 'video'
                    elif 'photo' in post_data.get('url', '').lower() or 'image' in post_data.get('url', '').lower():
                        content_type = 'image'
                    else:
                        content_type = 'unknown'
                
                # Calculate engagement rate for this post
                engagement_rate = 0.0
                total_engagement = (
                    post_data.get('likes', 0) + 
                    post_data.get('comments', 0) + 
                    post_data.get('shares', 0)
                )
                
                # Fetch the influencer to get follower count
                influencer = Influencer.query.get(influencer_id)
                if influencer and influencer.followers_count > 0:
                    engagement_rate = (total_engagement / influencer.followers_count) * 100
                
                # Get the data with fallbacks for missing fields
                content = post_data.get('caption', '')
                post_url = post_data.get('url', '')
                media_url = post_data.get('thumbnail', '')
                
                if existing_post:
                    # Update existing post
                    existing_post.content = content
                    existing_post.post_url = post_url
                    existing_post.media_url = media_url
                    existing_post.posted_at = posted_at
                    existing_post.content_type = content_type
                    existing_post.likes_count = post_data.get('likes', 0)
                    existing_post.comments_count = post_data.get('comments', 0)
                    existing_post.shares_count = post_data.get('shares', 0)
                    existing_post.views_count = post_data.get('views', 0)
                    existing_post.engagement_rate = engagement_rate
                    existing_post.updated_at = datetime.utcnow()
                    logger.info(f"Updated existing post {post_id} for influencer {influencer_id}")
                else:
                    # Create new post
                    new_post = SocialPost(
                        platform=platform,
                        post_id=post_id,
                        influencer_id=influencer_id,
                        content=content,
                        post_url=post_url,
                        media_url=media_url,
                        posted_at=posted_at,
                        content_type=content_type,
                        likes_count=post_data.get('likes', 0),
                        comments_count=post_data.get('comments', 0),
                        shares_count=post_data.get('shares', 0),
                        views_count=post_data.get('views', 0),
                        engagement_rate=engagement_rate
                    )
                    db.session.add(new_post)
                    posts_saved += 1
                    logger.info(f"Created new post {post_id} for influencer {influencer_id}")
            
            # Commit the session to save all posts at once
            db.session.commit()
            logger.info(f"Successfully saved {posts_saved} new posts for influencer {influencer_id}")
            return posts_saved
            
        except Exception as e:
            logger.error(f"Error saving posts for influencer {influencer_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            db.session.rollback()
            return 0
    
    @staticmethod
    def fetch_influencer_recent_posts(influencer_id, days=7, limit=None):
        """
        Fetch recent posts for an influencer from the database.
        
        Args:
            influencer_id (int): The ID of the influencer
            days (int): Number of days to look back (default: 7)
            limit (int, optional): Maximum number of posts to return
            
        Returns:
            list: List of SocialPost objects
        """
        from app.models.social_media import SocialPost
        
        try:
            # Get posts from the last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Query posts for this influencer in the date range
            query = SocialPost.query.filter(
                SocialPost.influencer_id == influencer_id,
                SocialPost.posted_at >= start_date
            ).order_by(SocialPost.posted_at.desc())
            
            # Apply limit if specified
            if limit:
                query = query.limit(limit)
                
            posts = query.all()
            logger.info(f"Fetched {len(posts)} recent posts for influencer {influencer_id}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching recent posts for influencer {influencer_id}: {str(e)}")
            return []
            
    @staticmethod
    def fetch_influencer_posts_by_platform(platform, days=7, limit=None):
        """
        Fetch recent posts for all influencers of a specific platform.
        
        Args:
            platform (str): Social media platform (instagram, tiktok, facebook)
            days (int): Number of days to look back (default: 7)
            limit (int, optional): Maximum number of posts to return
            
        Returns:
            list: List of SocialPost objects
        """
        from app.models.social_media import SocialPost
        
        try:
            # Get posts from the last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Query posts for this platform in the date range
            query = SocialPost.query.filter(
                SocialPost.platform == platform,
                SocialPost.posted_at >= start_date
            ).order_by(SocialPost.posted_at.desc())
            
            # Apply limit if specified
            if limit:
                query = query.limit(limit)
                
            posts = query.all()
            logger.info(f"Fetched {len(posts)} recent posts for platform {platform}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching recent posts for platform {platform}: {str(e)}")
            return []
    
    @staticmethod
    def find_social_media_id(platform, username, user_id=None):
        """
        Find the external ID for a social media account from a username.
        
        Args:
            platform (str): The social media platform (instagram, facebook, tiktok)
            username (str): The username to look up
            user_id (int, optional): If provided, will use this user's credentials for API calls
            
        Returns:
            str: The external ID if found, None otherwise
        """
        # First, try to find in our database
        existing_account = Influencer.query.filter_by(
            platform=platform,
            username=username.replace('@', '')  # Remove @ if present
        ).first()
        
        if existing_account and existing_account.id:
            # We already have this account in our database with its ID
            logger.info(f"Found existing {platform} account for {username} in database")
            return str(existing_account.id)
        
        # Try to fetch from the platform API
        if platform == "instagram":
            # Try to use the API if we have a user_id with Instagram permissions
            if user_id:
                try:
                    profile_data = SocialMediaService.fetch_instagram_profile(user_id, username.replace('@', ''))
                    if profile_data and 'instagram_business_account_id' in profile_data:
                        logger.info(f"Found Instagram ID for {username} via API")
                        return profile_data['instagram_business_account_id']
                except Exception as e:
                    logger.warning(f"Error fetching Instagram profile via API: {str(e)}")
            
            # If we can't find via API, generate a deterministic ID based on username
            # This is just a fallback and should be replaced with proper API integration
            logger.warning(f"Could not find Instagram ID for {username}, generating placeholder")
            # Remove @ if present and convert to lowercase
            clean_username = username.replace('@', '').lower()
            # Use a hash function to generate a consistent ID
            import hashlib
            return f"ig_{hashlib.md5(clean_username.encode()).hexdigest()[:16]}"
            
        elif platform == "facebook":
            # Similar approach for Facebook
            # In a real implementation, you would use the Facebook Graph API
            clean_username = username.replace('@', '').lower()
            import hashlib
            return f"fb_{hashlib.md5(clean_username.encode()).hexdigest()[:16]}"
            
        elif platform == "tiktok":
            # Similar approach for TikTok
            clean_username = username.replace('@', '').lower()
            import hashlib
            return f"tt_{hashlib.md5(clean_username.encode()).hexdigest()[:16]}"
        
        # Default fallback - generate a unique ID based on the username
        import hashlib
        clean_username = username.replace('@', '').lower()
        platform_prefix = platform[:2]
        return f"{platform_prefix}_{hashlib.md5(clean_username.encode()).hexdigest()[:16]}"
    
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