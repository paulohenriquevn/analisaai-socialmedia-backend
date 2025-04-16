from marshmallow import Schema, fields

class SaveContentIdeaSchema(Schema):
    ideaId = fields.Int(required=True)
