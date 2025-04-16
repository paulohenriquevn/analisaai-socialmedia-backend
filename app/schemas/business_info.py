from marshmallow import Schema, fields, validate

class BusinessInfoSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=128))
    description = fields.Str(required=False, allow_none=True)
    industry = fields.Str(required=False, allow_none=True)
    website = fields.Url(required=False, allow_none=True)

class SocialAccountSchema(Schema):
    platform = fields.Str(required=True)
    username = fields.Str(required=True)
    followers = fields.Int(required=False)
    postsCount = fields.Int(required=False)
