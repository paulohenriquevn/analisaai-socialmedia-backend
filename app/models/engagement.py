"""
Models for tracking engagement metrics for influencers.
"""
from datetime import datetime
from app.extensions import db


class InfluencerEngagement(db.Model):
    """Model for tracking detailed engagement metrics for influencers."""
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    
    # Date when metrics were calculated
    date = db.Column(db.Date, nullable=False)
    
    # Post level metrics
    posts_count = db.Column(db.Integer, default=0)
    avg_likes_per_post = db.Column(db.Float, default=0.0)
    avg_comments_per_post = db.Column(db.Float, default=0.0)
    avg_shares_per_post = db.Column(db.Float, default=0.0)
    
    # Overall engagement metrics
    engagement_rate = db.Column(db.Float, default=0.0)
    total_likes = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    total_shares = db.Column(db.Integer, default=0)
    
    # Performance metrics
    growth_rate = db.Column(db.Float, default=0.0)  # Growth rate compared to previous period
    
    # Platform-specific metrics (can be used or left null based on platform)
    video_views = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    
    # Date/time fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    influencer = db.relationship('Influencer', backref=db.backref('engagement_metrics', lazy='dynamic'))
    
    def __repr__(self):
        return f'<InfluencerEngagement {self.influencer_id} on {self.date}>'