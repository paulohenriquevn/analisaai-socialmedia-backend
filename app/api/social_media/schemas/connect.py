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


class SocialMediaConnectResponse(Schema):
    """Schema for social media connection response."""
    id = fields.Integer()
    user_id = fields.Integer()
    platform = fields.String()
    external_id = fields.String()
    username = fields.String()
    created_at = fields.DateTime()
    influencer_id = fields.Integer(allow_none=True)