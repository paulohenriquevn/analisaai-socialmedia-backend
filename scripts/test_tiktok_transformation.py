#!/usr/bin/env python3
"""
Test script for TikTok transformation with requested username
"""
import json
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_tiktok')

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a Flask app context for testing
from flask import Flask
app = Flask(__name__)

# Set up a mock config
app.config['APIFY_API_KEY'] = 'dummy_key'

# Create a test data structure that simulates TikTok data with authorMeta
test_video_data = [
    {
        "id": "7263282903719059747",
        "desc": "Test video",
        "authorMeta": {
            "id": "7492125996552965382",
            "name": "Virgínia Fonseca",
            "nickName": "Virginia Fonseca",
            "verified": True,
            "signature": "Test bio",
            "avatarMedium": "https://example.com/avatar.jpg"
        },
        "stats": {
            "diggCount": 1000,
            "commentCount": 500,
            "shareCount": 200,
            "playCount": 5000
        }
    }
]

with app.app_context():
    # Import the service
    from app.services.apify_service import ApifyService
    
    logger.info("Testing TikTok transformation with authorMeta format")
    
    # Create synthetic profile data like what we'd have in the actual code
    profile_data = {
        'user': test_video_data[0]['authorMeta'],
        'videos': test_video_data,
        'requestedUsername': 'testusername'  # This should be used
    }
    
    # Test with the requestedUsername in the data
    transformed_data1 = ApifyService._transform_tiktok_data(profile_data)
    logger.info(f"Username from data: {transformed_data1['username']}")
    
    # Test with the requested_username parameter
    transformed_data2 = ApifyService._transform_tiktok_data(profile_data, requested_username='virginiafonseca')
    logger.info(f"Username from parameter: {transformed_data2['username']}")
    
    # Test with both - parameter should take precedence
    transformed_data3 = ApifyService._transform_tiktok_data(
        {
            'user': test_video_data[0]['authorMeta'],
            'videos': test_video_data,
            'requestedUsername': 'requestedinternal'
        }, 
        requested_username='virginiafonseca'
    )
    logger.info(f"Username with both sources: {transformed_data3['username']}")
    
    # Test with user_data that contains an ID but no username
    id_only_data = {
        'user': {
            'id': '7492125996552965382',
            'verified': True,
            'signature': 'Test bio',
            'avatarMedium': 'https://example.com/avatar.jpg'
        },
        'videos': test_video_data
    }
    
    transformed_data4 = ApifyService._transform_tiktok_data(id_only_data)
    logger.info(f"Username with ID only: {transformed_data4['username']}")
    
    transformed_data5 = ApifyService._transform_tiktok_data(id_only_data, requested_username='virginiafonseca')
    logger.info(f"Username with ID only + requested_username: {transformed_data5['username']}")
    
    logger.info("All tests complete")