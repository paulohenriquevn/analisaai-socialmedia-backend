"""
Influencer-related models.
"""
from datetime import datetime
from app.extensions import db

# Association table for Influencer-Category relationship
influencer_categories = db.Table('influencer_categories',
    db.Column('influencer_id', db.Integer, db.ForeignKey('influencer.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)


class Influencer(db.Model):
    """Influencer model representing social media influencers."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(100))
    platform = db.Column(db.String(20), nullable=False)
    profile_url = db.Column(db.String(1024))
    profile_image = db.Column(db.Text)
    bio = db.Column(db.Text)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float)
    social_score = db.Column(db.Float)
    relevance_score = db.Column(db.Float, default=0.0)  # Current relevance score (0-100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    categories = db.relationship('Category', secondary=influencer_categories, backref=db.backref('influencers', lazy='dynamic'))
    metrics = db.relationship('InfluencerMetric', backref='influencer', lazy='dynamic')
    posts = db.relationship('SocialPost', backref='influencer', lazy='dynamic')
    # Relationship to reach metrics is defined in the InfluencerReach model
    # Relationship to growth metrics is defined in the InfluencerGrowth model
    # Relationship to score metrics is defined in the InfluencerScore model
    
    def __repr__(self):
        return f'<Influencer {self.username} ({self.platform})>'


class Category(db.Model):
    """Category model for classifying influencers."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Category {self.name}>'


class InfluencerMetric(db.Model):
    """Model for storing historical metrics about influencers."""
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    date = db.Column(db.Date, nullable=False)
    followers = db.Column(db.Integer)
    engagement = db.Column(db.Float)
    posts = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    shares = db.Column(db.Integer)
    views = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<InfluencerMetric {self.influencer_id} {self.date}>'