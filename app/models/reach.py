"""
Models for tracking reach metrics for influencers.
"""
from datetime import datetime
from app.extensions import db


class InfluencerReach(db.Model):
    """Model for tracking reach metrics such as impressions and story views."""
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    
    # Date when metrics were collected
    date = db.Column(db.Date, nullable=False)
    
    # Time-specific data for detailed analysis
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Reach metrics
    impressions = db.Column(db.Integer, default=0)  # Number of times content was displayed
    reach = db.Column(db.Integer, default=0)  # Number of unique accounts that saw the content
    story_views = db.Column(db.Integer, default=0)  # Number of views on stories
    profile_views = db.Column(db.Integer, default=0)  # Number of profile visits
    
    # Story-specific metrics
    stories_count = db.Column(db.Integer, default=0)  # Number of stories posted
    story_engagement_rate = db.Column(db.Float, default=0.0)  # Engagement rate on stories
    story_exit_rate = db.Column(db.Float, default=0.0)  # Rate at which users exit stories
    story_completion_rate = db.Column(db.Float, default=0.0)  # Percentage of users who view stories to completion
    
    # Retention and audience metrics
    avg_watch_time = db.Column(db.Float, default=0.0)  # Average watch time in seconds (for video content)
    audience_growth = db.Column(db.Float, default=0.0)  # Growth rate of audience since last measurement
    
    # Date/time fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    influencer = db.relationship('Influencer', backref=db.backref('reach_metrics', lazy='dynamic'))
    
    def __repr__(self):
        return f'<InfluencerReach {self.influencer_id} on {self.date}>'