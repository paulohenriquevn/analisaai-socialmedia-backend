"""
Models for tracking growth metrics for influencers.
"""
from datetime import datetime
from app.extensions import db


class InfluencerGrowth(db.Model):
    """Model for tracking growth metrics such as new followers and retention rates."""
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    
    # Date when metrics were collected
    date = db.Column(db.Date, nullable=False)
    
    # Followers growth metrics
    followers_count = db.Column(db.Integer, default=0)  # Total followers on this date
    new_followers_daily = db.Column(db.Integer, default=0)  # New followers in the last day
    new_followers_weekly = db.Column(db.Integer, default=0)  # New followers in the last week
    new_followers_monthly = db.Column(db.Integer, default=0)  # New followers in the last month
    
    # Retention metrics
    retention_rate = db.Column(db.Float, default=0.0)  # Percentage of followers retained (100 - unfollow_rate)
    churn_rate = db.Column(db.Float, default=0.0)  # Percentage of followers lost (unfollow rate)
    
    # Growth rate metrics
    daily_growth_rate = db.Column(db.Float, default=0.0)  # Daily growth rate as percentage
    weekly_growth_rate = db.Column(db.Float, default=0.0)  # Weekly growth rate as percentage
    monthly_growth_rate = db.Column(db.Float, default=0.0)  # Monthly growth rate as percentage
    
    # Velocity metrics
    growth_velocity = db.Column(db.Float, default=0.0)  # Average new followers per day over a period
    growth_acceleration = db.Column(db.Float, default=0.0)  # Change in growth velocity
    
    # Projection metrics
    projected_followers_30d = db.Column(db.Integer, default=0)  # Projected followers count in 30 days
    projected_followers_90d = db.Column(db.Integer, default=0)  # Projected followers count in 90 days
    
    # Date/time fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    influencer = db.relationship('Influencer', backref=db.backref('growth_metrics', lazy='dynamic'))
    
    def __repr__(self):
        return f'<InfluencerGrowth {self.influencer_id} on {self.date}>'