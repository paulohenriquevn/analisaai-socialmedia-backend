"""
Schemas for social media connection.
"""
from marshmallow import Schema, fields, validate


class SocialMediaConnectRequest(Schema):
    """Schema for social media connection request."""
    platform = fields.String(
        required=True, 
        validate=validate.OneOf(["instagram", "facebook", "tiktok"])
    )
    username = fields.String(required=True)
    external_id = fields.String(required=False)  # Now optional, will be auto-detected if not provided


class EngagementMetricsSchema(Schema):
    """Schema for engagement metrics."""
    date = fields.String()
    posts_count = fields.Integer()
    engagement_rate = fields.Float()
    avg_likes_per_post = fields.Float()
    avg_comments_per_post = fields.Float()
    avg_shares_per_post = fields.Float()
    total_likes = fields.Integer()
    total_comments = fields.Integer()
    total_shares = fields.Integer()
    growth_rate = fields.Float()


class ReachMetricsSchema(Schema):
    """Schema for reach metrics."""
    date = fields.String()
    timestamp = fields.String()
    impressions = fields.Integer()
    reach = fields.Integer()
    story_views = fields.Integer()
    profile_views = fields.Integer()
    stories_count = fields.Integer()
    story_engagement_rate = fields.Float()
    story_completion_rate = fields.Float()
    audience_growth = fields.Float()


class GrowthMetricsSchema(Schema):
    """Schema for growth metrics."""
    date = fields.String()
    followers_count = fields.Integer()
    new_followers_daily = fields.Integer()
    new_followers_weekly = fields.Integer()
    new_followers_monthly = fields.Integer()
    retention_rate = fields.Float()
    churn_rate = fields.Float()
    daily_growth_rate = fields.Float()
    weekly_growth_rate = fields.Float()
    monthly_growth_rate = fields.Float()
    growth_velocity = fields.Float()
    growth_acceleration = fields.Float()
    projected_followers_30d = fields.Integer()
    projected_followers_90d = fields.Integer()


class ScoreMetricsSchema(Schema):
    """Schema for relevance score metrics."""
    date = fields.String()
    overall_score = fields.Float()
    engagement_score = fields.Float()
    reach_score = fields.Float()
    growth_score = fields.Float()
    consistency_score = fields.Float()
    audience_quality_score = fields.Float()


class SocialMediaConnectResponse(Schema):
    """Schema for social media connection response."""
    id = fields.Integer()
    user_id = fields.Integer()
    platform = fields.String()
    external_id = fields.String()
    username = fields.String()
    created_at = fields.DateTime()
    social_page_id = fields.Integer(allow_none=True)
    relevance_score = fields.Float(required=False)
    engagement_metrics = fields.Nested(EngagementMetricsSchema, required=False)
    reach_metrics = fields.Nested(ReachMetricsSchema, required=False)
    growth_metrics = fields.Nested(GrowthMetricsSchema, required=False)
    score_metrics = fields.Nested(ScoreMetricsSchema, required=False)