"""
JSON schemas for analytics API.
"""
from marshmallow import Schema, fields, validate

# Import visualization schemas
from app.api.analytics.schemas.visualization import (
    EngagementVisualizationSchema,
    ReachVisualizationSchema,
    GrowthVisualizationSchema,
    ScoreVisualizationSchema,
    DashboardOverviewSchema,
    ComparisonVisualizationSchema
)


class MetricsRequestSchema(Schema):
    """Schema for metrics request parameters."""
    timeframe = fields.String(
        validate=validate.OneOf(['day', 'week', 'month', 'year']),
        default='month'
    )


class PlatformMetricsSchema(Schema):
    """Schema for platform-specific metrics."""
    followers = fields.Integer()
    engagement = fields.Float()
    engagement_rate = fields.Float()
    posts = fields.Integer()
    likes = fields.Integer()
    comments = fields.Integer()
    shares = fields.Integer()
    views = fields.Integer()


class TopPerformingPostSchema(Schema):
    """Schema for top performing posts."""
    platform = fields.String()
    post_id = fields.String()
    date = fields.String()
    engagement = fields.Float()
    likes = fields.Integer()
    comments = fields.Integer()
    shares = fields.Integer()
    views = fields.Integer()


class GrowthDataPointSchema(Schema):
    """Schema for growth data points."""
    date = fields.String()
    platform = fields.String()
    followers = fields.Integer()
    engagement = fields.Float()


class ConsolidatedMetricsSchema(Schema):
    """Schema for consolidated metrics response."""
    platforms = fields.List(fields.String())
    total_followers = fields.Integer()
    total_engagement = fields.Float()
    average_engagement_rate = fields.Float()
    platform_metrics = fields.Dict(keys=fields.String(), values=fields.Nested(PlatformMetricsSchema))
    top_performing_posts = fields.List(fields.Nested(TopPerformingPostSchema))
    growth_trend = fields.List(fields.Nested(GrowthDataPointSchema))
    last_updated = fields.String()
    error = fields.String(required=False)


class PlatformDistributionSchema(Schema):
    """Schema for platform distribution response."""
    counts = fields.Dict(keys=fields.String(), values=fields.Integer())
    followers = fields.Dict(keys=fields.String(), values=fields.Integer())
    engagement = fields.Dict(keys=fields.String(), values=fields.Float())
    percentages = fields.Dict(keys=fields.String(), values=fields.Float())
    last_updated = fields.String()
    error = fields.String(required=False)


class CategoryMetricsSchema(Schema):
    """Schema for category metrics."""
    social_page_count = fields.Integer()
    avg_followers = fields.Integer()
    avg_engagement = fields.Float()
    most_common_platform = fields.String()


class TopCategorySchema(Schema):
    """Schema for top categories."""
    name = fields.String()
    social_page_count = fields.Integer()
    avg_followers = fields.Integer()
    avg_engagement = fields.Float()


class CategoryInsightsSchema(Schema):
    """Schema for category insights response."""
    categories = fields.Dict(keys=fields.String(), values=fields.Nested(CategoryMetricsSchema))
    top_categories = fields.List(fields.Nested(TopCategorySchema))
    last_updated = fields.String()
    error = fields.String(required=False)


class DashboardResponseSchema(Schema):
    """Schema for dashboard response."""
    metrics = fields.Nested(ConsolidatedMetricsSchema)
    distribution = fields.Nested(PlatformDistributionSchema)
    insights = fields.Nested(CategoryInsightsSchema)


# New schemas for sentiment analysis

class SentimentAnalysisRequestSchema(Schema):
    """Schema for sentiment analysis request."""
    text = fields.String(required=True, validate=validate.Length(min=1))


class CommentSchema(Schema):
    """Schema for a social media comment."""
    id = fields.Integer()
    comment_id = fields.String()
    post_id = fields.Integer(required=False)
    post_url = fields.String(required=False)
    author_username = fields.String()
    author_display_name = fields.String()
    author_picture = fields.String()
    content = fields.String()
    posted_at = fields.String()
    likes_count = fields.Integer()
    sentiment = fields.String()
    sentiment_score = fields.Float()
    is_critical = fields.Boolean(required=False)


class SentimentDistributionSchema(Schema):
    """Schema for sentiment distribution."""
    counts = fields.Dict(keys=fields.String(), values=fields.Integer())
    percentages = fields.Dict(keys=fields.String(), values=fields.Float())


class SentimentTrendPointSchema(Schema):
    """Schema for sentiment trend data points."""
    date = fields.String()
    average_score = fields.Float()
    comments_count = fields.Integer()
    sentiment_counts = fields.Dict(keys=fields.String(), values=fields.Integer())


class PostSentimentAnalysisSchema(Schema):
    """Schema for post sentiment analysis response."""
    post_id = fields.Integer()
    platform = fields.String()
    comments_count = fields.Integer()
    sentiment_distribution = fields.Nested(SentimentDistributionSchema)
    critical_comments = fields.List(fields.Nested(CommentSchema))
    top_positive = fields.List(fields.Nested(CommentSchema))
    top_negative = fields.List(fields.Nested(CommentSchema))
    average_sentiment_score = fields.Float()
    last_updated = fields.String()
    error = fields.String(required=False)


class SocialPageSentimentAnalysisSchema(Schema):
    """Schema for social_page sentiment analysis response."""
    social_page_id = fields.Integer()
    posts_count = fields.Integer()
    comments_count = fields.Integer()
    sentiment_distribution = fields.Nested(SentimentDistributionSchema)
    sentiment_trend = fields.List(fields.Nested(SentimentTrendPointSchema))
    critical_comments = fields.List(fields.Nested(CommentSchema))
    average_sentiment_score = fields.Float()
    last_updated = fields.String()
    error = fields.String(required=False)


class SentimentAnalysisResponseSchema(Schema):
    """Schema for sentiment analysis response."""
    text = fields.String()
    sentiment = fields.String()
    score = fields.Float()
    is_critical = fields.Boolean()
    error = fields.String(required=False)