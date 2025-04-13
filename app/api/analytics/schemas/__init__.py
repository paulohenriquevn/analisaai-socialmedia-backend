"""
JSON schemas for analytics API.
"""
from marshmallow import Schema, fields, validate


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
    influencer_count = fields.Integer()
    avg_followers = fields.Integer()
    avg_engagement = fields.Float()
    most_common_platform = fields.String()


class TopCategorySchema(Schema):
    """Schema for top categories."""
    name = fields.String()
    influencer_count = fields.Integer()
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