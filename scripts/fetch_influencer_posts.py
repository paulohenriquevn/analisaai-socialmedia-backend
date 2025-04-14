#!/usr/bin/env python3
"""
Script to fetch and save recent posts for all influencers in the database.
This script is intended to be run as a scheduled job to keep post data up-to-date.
"""
import os
import sys
import logging
import argparse
from datetime import datetime

# Add the parent directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Import Flask app and required modules
from app import create_app
from app.extensions import db
from app.models.influencer import Influencer
from app.services.apify_service import ApifyService
from app.services.social_media_service import SocialMediaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_posts_for_influencer(influencer):
    """Fetch and save posts for a single influencer."""
    logger.info(f"Processing influencer {influencer.id} - {influencer.username} ({influencer.platform})")
    
    try:
        # Fetch profile data based on platform
        if influencer.platform == 'instagram':
            profile_data = ApifyService.fetch_instagram_profile(influencer.username)
        elif influencer.platform == 'tiktok':
            profile_data = ApifyService.fetch_tiktok_profile(influencer.username)
        elif influencer.platform == 'facebook':
            profile_data = ApifyService.fetch_facebook_profile(influencer.username)
        else:
            logger.warning(f"Unsupported platform: {influencer.platform} for {influencer.username}")
            return False
        
        if not profile_data or 'error' in profile_data:
            error_msg = profile_data.get('message', 'Unknown error') if profile_data else 'Failed to fetch profile data'
            logger.error(f"Error fetching profile data for {influencer.username}: {error_msg}")
            return False
        
        # Extract and save recent posts
        if 'recent_media' in profile_data and profile_data['recent_media']:
            posts_count = SocialMediaService.save_recent_posts(
                influencer.id, 
                profile_data['recent_media'], 
                influencer.platform
            )
            logger.info(f"Saved {posts_count} posts for {influencer.username}")
            
            # Update the influencer's data as well
            updated_influencer = SocialMediaService.save_influencer_data(profile_data)
            if updated_influencer:
                logger.info(f"Updated influencer data for {influencer.username}")
                return True
            else:
                logger.warning(f"Failed to update influencer data for {influencer.username}")
                return posts_count > 0
        else:
            logger.warning(f"No recent media found for {influencer.username}")
            return False
    
    except Exception as e:
        logger.error(f"Error processing influencer {influencer.username}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main(platform=None, limit=None):
    """
    Main function to process influencers.
    
    Args:
        platform (str, optional): Filter by platform ('instagram', 'tiktok', 'facebook')
        limit (int, optional): Maximum number of influencers to process
    """
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Build the query
        query = Influencer.query
        
        # Apply platform filter if specified
        if platform:
            logger.info(f"Filtering influencers by platform: {platform}")
            query = query.filter_by(platform=platform)
        
        # Get all influencers, order by updated_at (oldest first)
        influencers = query.order_by(Influencer.updated_at.asc())
        
        # Apply limit if specified
        if limit:
            logger.info(f"Limiting to {limit} influencers")
            influencers = influencers.limit(limit)
        
        # Fetch and convert to list
        influencers = influencers.all()
        
        if not influencers:
            logger.info("No influencers found matching the criteria")
            return
        
        logger.info(f"Found {len(influencers)} influencers to process")
        
        # Process each influencer
        success_count = 0
        fail_count = 0
        
        for influencer in influencers:
            result = fetch_posts_for_influencer(influencer)
            if result:
                success_count += 1
            else:
                fail_count += 1
        
        logger.info(f"Processing complete. Successfully processed: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fetch recent posts for influencers')
    parser.add_argument('--platform', choices=['instagram', 'tiktok', 'facebook'], 
                        help='Filter by platform')
    parser.add_argument('--limit', type=int, help='Maximum number of influencers to process')
    
    args = parser.parse_args()
    
    # Run the main function
    main(platform=args.platform, limit=args.limit)