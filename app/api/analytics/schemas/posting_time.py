"""
JSON schemas for posting time optimization API.
"""
from marshmallow import Schema, fields, validate


class PostingTimeRequestSchema(Schema):
    """Schema for posting time request parameters."""
    platform = fields.String(required=False)
    content_type = fields.String(required=False)
    days = fields.Integer(required=False, validate=validate.Range(min=30, max=365), default=90)


class HourRecommendationSchema(Schema):
    """Schema for hour-based posting time recommendation."""
    hour = fields.Integer()
    formatted_hour = fields.String()
    avg_engagement = fields.Float()
    post_count = fields.Integer()
    confidence = fields.Float(required=False)


class DayRecommendationSchema(Schema):
    """Schema for day of week recommendation."""
    day = fields.String()
    avg_engagement = fields.Float()
    post_count = fields.Integer()


class ContentTypeRecommendationSchema(Schema):
    """Schema for content type recommendation."""
    type = fields.String()
    avg_engagement = fields.Float()
    post_count = fields.Integer()
    confidence = fields.Float(required=False)
    benchmark_engagement = fields.Float(required=False)
    relative_performance = fields.Float(required=False)
    source = fields.String(required=False)


class PlatformRecommendationSchema(Schema):
    """Schema for platform-specific recommendation."""
    avg_engagement = fields.Float()
    post_count = fields.Integer()
    reliability = fields.Float(required=False)
    benchmark_engagement = fields.Float(required=False)
    relative_performance = fields.Float(required=False)
    source = fields.String(required=False)


class DayTimeRecommendationSchema(Schema):
    """Schema for day+time recommendations."""
    recommended = fields.List(fields.Nested(HourRecommendationSchema))
    benchmark_comparison = fields.List(fields.Nested(HourRecommendationSchema), required=False)
    source = fields.String(required=False)


class PostingTimeRecommendationsSchema(Schema):
    """Schema for posting time recommendations."""
    best_times = fields.Dict(keys=fields.String(), values=fields.Nested(DayTimeRecommendationSchema))
    best_days = fields.List(fields.Nested(DayRecommendationSchema), required=False)
    best_content_types = fields.List(fields.Nested(ContentTypeRecommendationSchema))
    by_platform = fields.Dict(keys=fields.String(), values=fields.Nested(PlatformRecommendationSchema))


class PostingTimeResponseSchema(Schema):
    """Schema for posting time analysis response."""
    recommendations = fields.Nested(PostingTimeRecommendationsSchema)
    source = fields.String(required=False)
    message = fields.String(required=False)
    data_points = fields.Integer(required=False)
    user_data_points = fields.Integer(required=False)
    analyzed_period_days = fields.Integer(required=False)
    is_reliable = fields.Boolean(required=False)
    last_updated = fields.String()
    error = fields.String(required=False)


class ContentTypePerformanceSchema(Schema):
    """Schema for content type performance data."""
    post_count = fields.Integer()
    percentage = fields.Float()
    avg_engagement = fields.Float()
    avg_likes = fields.Float()
    avg_comments = fields.Float()
    avg_shares = fields.Float()
    best_days = fields.List(fields.Dict())
    best_hours = fields.List(fields.Dict())


class ContentTypeAnalysisResponseSchema(Schema):
    """Schema for content type analysis response."""
    performance = fields.Dict(keys=fields.String(), values=fields.Nested(ContentTypePerformanceSchema))
    total_posts = fields.Integer()
    analyzed_period_days = fields.Integer()
    is_reliable = fields.Boolean()
    last_updated = fields.String()
    error = fields.String(required=False)


class DayOfWeekDetailsSchema(Schema):
    """Schema for day of week analysis details."""
    post_count = fields.Integer()
    avg_engagement = fields.Float()
    avg_likes = fields.Float()
    avg_comments = fields.Float()
    avg_shares = fields.Float()
    top_content_types = fields.List(fields.Dict())
    top_hours = fields.List(fields.Dict())


class DayOfWeekAnalysisResponseSchema(Schema):
    """Schema for day of week analysis response."""
    by_day = fields.Dict(keys=fields.String(), values=fields.Nested(DayOfWeekDetailsSchema))
    best_days = fields.List(fields.Dict())
    total_posts = fields.Integer()
    analyzed_period_days = fields.Integer()
    is_reliable = fields.Boolean()
    last_updated = fields.String()
    error = fields.String(required=False)


class IndustryBenchmarksResponseSchema(Schema):
    """Schema for industry benchmarks response."""
    benchmarks = fields.Dict()
    total_posts = fields.Integer()
    analyzed_period_days = fields.Integer()
    category = fields.String(required=False, allow_none=True)
    platform = fields.String(required=False, allow_none=True)
    is_reliable = fields.Boolean()
    last_updated = fields.String()
    error = fields.String(required=False)