from marshmallow import Schema, fields, validate

class UpdateUserSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=64))

class UpdatePasswordSchema(Schema):
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
