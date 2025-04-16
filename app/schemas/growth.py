from marshmallow import Schema, fields

class GrowthGoalSchema(Schema):
    platform = fields.Str(required=True)
    followersGoal = fields.Int(required=True)
    engagementGoal = fields.Int(required=False)
    deadline = fields.Date(required=False)

class GrowthGoalsListSchema(Schema):
    goals = fields.List(fields.Nested(GrowthGoalSchema), required=True)
