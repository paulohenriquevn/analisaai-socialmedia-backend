"""
Import all models so they're available when importing from app.models.
"""
from app.models.user import User, Role, user_roles
from app.models.organization import Organization, Plan, PlanFeature
from app.models.social_media import (
    SocialToken,
    SocialPage,
    SocialPageMetric,
    SocialPageEngagement,
    SocialPageGrowth,
    SocialPageReach,
    SocialPageScore,
    SocialPagePost,
    SocialPagePostComment,
    SocialPageCategory
)

# For convenience, create a list of all models that can be used with db.create_all()
__all__ = [
    'User', 'Role', 
    'Organization', 'Plan', 'PlanFeature',
    "SocialToken",
    "SocialPage",
    "SocialPageMetric",
    "SocialPageEngagement",
    "SocialPageGrowth",
    "SocialPageReach",
    "SocialPageScore",
    "SocialPagePost",
    "SocialPagePostComment",
    "SocialPageCategory"
]