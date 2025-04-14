"""
Models for tracking relevance scores for influencers.
"""
from datetime import datetime
from app.extensions import db


class InfluencerScore(db.Model):
    """Model for tracking overall relevance scores for influencers."""
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    
    # Date when score was calculated
    date = db.Column(db.Date, nullable=False)
    
    # Overall score (0-100)
    overall_score = db.Column(db.Float, default=0.0)
    
    # Component scores (0-100)
    engagement_score = db.Column(db.Float, default=0.0)  # Based on engagement metrics
    reach_score = db.Column(db.Float, default=0.0)  # Based on reach metrics
    growth_score = db.Column(db.Float, default=0.0)  # Based on growth metrics
    consistency_score = db.Column(db.Float, default=0.0)  # Based on posting consistency
    audience_quality_score = db.Column(db.Float, default=0.0)  # Based on audience quality
    
    # Weight factors used for calculation
    engagement_weight = db.Column(db.Float, default=0.3)
    reach_weight = db.Column(db.Float, default=0.25)
    growth_weight = db.Column(db.Float, default=0.25)
    consistency_weight = db.Column(db.Float, default=0.1)
    audience_quality_weight = db.Column(db.Float, default=0.1)
    
    # Date/time fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    influencer = db.relationship('Influencer', backref=db.backref('score_metrics', lazy='dynamic'))
    
    def __repr__(self):
        return f'<InfluencerScore {self.influencer_id} on {self.date}: {self.overall_score}>'