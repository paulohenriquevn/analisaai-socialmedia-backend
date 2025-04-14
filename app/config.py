"""
Configuration settings for the application.
Each environment has its own configuration class.
"""
import os
from datetime import timedelta

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Social Media OAuth
    INSTAGRAM_CLIENT_ID = os.getenv('INSTAGRAM_CLIENT_ID', '')
    INSTAGRAM_CLIENT_SECRET = os.getenv('INSTAGRAM_CLIENT_SECRET', '')
    INSTAGRAM_REDIRECT_URI = os.getenv('INSTAGRAM_REDIRECT_URI', 'http://localhost:5000/api/auth/instagram/callback')
    
    FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID', '')
    FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET', '')
    FACEBOOK_REDIRECT_URI = os.getenv('FACEBOOK_REDIRECT_URI', 'http://localhost:5000/api/auth/facebook/callback')
    
    TIKTOK_CLIENT_ID = os.getenv('TIKTOK_CLIENT_ID', '')
    TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET', '')
    TIKTOK_REDIRECT_URI = os.getenv('TIKTOK_REDIRECT_URI', 'http://localhost:5000/api/auth/tiktok/callback')
    
    # Frontend URL
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:4200')
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', '')
    
    # Apify API
    APIFY_API_KEY = os.getenv('APIFY_API_KEY', '')


class DevelopmentConfig(Config):
    """Development configuration settings."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/analisaai')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    """Testing configuration settings."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/analisaai_test')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """Production configuration settings."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/analisaai')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # In production, ensure these are properly set
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


# Dictionary to map environment names to configuration classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}