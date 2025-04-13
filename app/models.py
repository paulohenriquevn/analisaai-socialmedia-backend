from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Association table for User-Role relationship
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

# Association table for Organization-User relationship
organization_users = db.Table('organization_users',
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    users = db.relationship('User', secondary=organization_users, backref=db.backref('organizations', lazy='dynamic'))
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    plan = db.relationship('Plan', backref='organizations')

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    features = db.relationship('PlanFeature', backref='plan')

class PlanFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    feature = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100))

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(100))
    platform = db.Column(db.String(20), nullable=False)
    profile_url = db.Column(db.String(255))
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float)
    social_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    categories = db.relationship('Category', secondary='influencer_categories', backref=db.backref('influencers', lazy='dynamic'))
    metrics = db.relationship('InfluencerMetric', backref='influencer', lazy='dynamic')

# Association table for Influencer-Category relationship
influencer_categories = db.Table('influencer_categories',
    db.Column('influencer_id', db.Integer, db.ForeignKey('influencer.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))

class InfluencerMetric(db.Model):
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

class SocialToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    platform = db.Column(db.String(20), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('social_tokens', lazy='dynamic')) 