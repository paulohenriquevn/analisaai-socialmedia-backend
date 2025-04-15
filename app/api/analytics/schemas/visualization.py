"""
JSON schemas for visualization API endpoints.
"""
from marshmallow import Schema, fields, validate


class DataPointSchema(Schema):
    """Schema for data points in time series visualization."""
    date = fields.String()
    value = fields.Float()
    

class MetricTimeSeriesSchema(Schema):
    """Schema for a metric time series visualization."""
    metric_name = fields.String()
    data_points = fields.List(fields.Nested(DataPointSchema))
    color = fields.String(required=False)
    unit = fields.String(required=False)
    

class VisualizationMetaSchema(Schema):
    """Schema for metadata about the visualization."""
    social_page_id = fields.Integer()
    social_page_name = fields.String()
    platform = fields.String()
    time_range = fields.Integer()
    start_date = fields.String()
    end_date = fields.String()
    

class TrendInfoSchema(Schema):
    """Schema for trend information."""
    trend_direction = fields.String(validate=validate.OneOf(['up', 'down', 'stable']))
    trend_percentage = fields.Float()
    trend_description = fields.String()
    compared_to_previous = fields.String()
    

class InsightSchema(Schema):
    """Schema for insights about the metrics."""
    title = fields.String()
    description = fields.String()
    type = fields.String(validate=validate.OneOf(['positive', 'negative', 'neutral', 'warning']))
    

class EngagementVisualizationSchema(Schema):
    """Schema for engagement visualization."""
    meta = fields.Nested(VisualizationMetaSchema)
    time_series = fields.List(fields.Nested(MetricTimeSeriesSchema))
    summary = fields.Dict(keys=fields.String(), values=fields.Float())
    trend = fields.Nested(TrendInfoSchema)
    insights = fields.List(fields.Nested(InsightSchema))
    best_performing_day = fields.String(required=False)
    worst_performing_day = fields.String(required=False)
    

class ReachVisualizationSchema(Schema):
    """Schema for reach visualization."""
    meta = fields.Nested(VisualizationMetaSchema)
    time_series = fields.List(fields.Nested(MetricTimeSeriesSchema))
    summary = fields.Dict(keys=fields.String(), values=fields.Float())
    trend = fields.Nested(TrendInfoSchema)
    insights = fields.List(fields.Nested(InsightSchema))
    best_performing_content = fields.Dict(required=False)
    

class GrowthVisualizationSchema(Schema):
    """Schema for growth visualization."""
    meta = fields.Nested(VisualizationMetaSchema)
    time_series = fields.List(fields.Nested(MetricTimeSeriesSchema))
    summary = fields.Dict(keys=fields.String(), values=fields.Float())
    trend = fields.Nested(TrendInfoSchema)
    insights = fields.List(fields.Nested(InsightSchema))
    projected_growth = fields.Dict(keys=fields.String(), values=fields.Float(), required=False)
    
    
class ScoreVisualizationSchema(Schema):
    """Schema for score visualization."""
    meta = fields.Nested(VisualizationMetaSchema)
    time_series = fields.List(fields.Nested(MetricTimeSeriesSchema))
    summary = fields.Dict(keys=fields.String(), values=fields.Float())
    trend = fields.Nested(TrendInfoSchema)
    insights = fields.List(fields.Nested(InsightSchema))
    component_breakdown = fields.Dict(keys=fields.String(), values=fields.Float(), required=False)
    

class DashboardOverviewSchema(Schema):
    """Schema for dashboard overview visualization."""
    meta = fields.Nested(VisualizationMetaSchema)
    engagement = fields.Nested(EngagementVisualizationSchema)
    reach = fields.Nested(ReachVisualizationSchema)
    growth = fields.Nested(GrowthVisualizationSchema)
    score = fields.Nested(ScoreVisualizationSchema)
    overall_health = fields.String(validate=validate.OneOf(['excellent', 'good', 'fair', 'poor']))
    recommended_actions = fields.List(fields.String())
    

class SocialPageComparisonItemSchema(Schema):
    """Schema for an item in the socialpage comparison."""
    social_page_id = fields.Integer()
    social_page_name = fields.String()
    platform = fields.String()
    metrics = fields.Dict(keys=fields.String(), values=fields.Float())
    

class ComparisonVisualizationSchema(Schema):
    """Schema for comparison visualization."""
    metrics_compared = fields.List(fields.String())
    social_pages = fields.List(fields.Nested(SocialPageComparisonItemSchema))
    recommendations = fields.List(fields.String())