"""
Models related to social media integrations.
"""
from datetime import datetime
from app.extensions import db


class SocialToken(db.Model):
    """Store OAuth tokens for social media platforms."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    platform = db.Column(db.String(20), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SocialToken {self.platform} for user {self.user_id}>'


class SocialPost(db.Model):
    """Social media post model."""
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)
    post_id = db.Column(db.String(100), nullable=False, unique=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    content = db.Column(db.Text)
    post_url = db.Column(db.String(255))
    media_url = db.Column(db.String(255))
    posted_at = db.Column(db.DateTime)
    content_type = db.Column(db.String(20))  # 'image', 'video', 'carousel', 'text', etc.
    category = db.Column(db.String(50))  # 'product', 'lifestyle', 'education', etc.
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float)  # Calculated engagement rate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('PostComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SocialPost {self.platform}:{self.post_id}>'
        
    @property
    def day_of_week(self):
        """Get the day of week when the post was published."""
        if self.posted_at:
            return self.posted_at.strftime('%A')  # Monday, Tuesday, etc.
        return None
        
    @property
    def hour_of_day(self):
        """Get the hour of day when the post was published."""
        if self.posted_at:
            return self.posted_at.hour
        return None
        
    @property
    def engagement(self):
        """Calculate engagement (sum of likes, comments, shares)."""
        return (self.likes_count or 0) + (self.comments_count or 0) + (self.shares_count or 0)


class PostComment(db.Model):
    """Model for storing comments on social media posts."""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('social_post.id'), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    comment_id = db.Column(db.String(100), nullable=False, unique=True)
    author_username = db.Column(db.String(100))
    author_display_name = db.Column(db.String(100))
    author_picture = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    posted_at = db.Column(db.DateTime)
    likes_count = db.Column(db.Integer, default=0)
    replied_to_id = db.Column(db.String(100))  # ID of parent comment if this is a reply
    
    # Sentiment analysis data
    sentiment = db.Column(db.String(10))  # positive, neutral, negative
    sentiment_score = db.Column(db.Float)  # -1.0 to 1.0
    is_critical = db.Column(db.Boolean, default=False)  # Flag for critical comments
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PostComment {self.platform}:{self.comment_id}>'