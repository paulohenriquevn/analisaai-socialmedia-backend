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
    external_id = fields.String(required=True)
    username = fields.String(required=True)


class SocialMediaConnectResponse(Schema):
    """Schema for social media connection response."""
    id = fields.Integer()
    user_id = fields.Integer()
    platform = fields.String()
    external_id = fields.String()
    username = fields.String()
    created_at = fields.DateTime()