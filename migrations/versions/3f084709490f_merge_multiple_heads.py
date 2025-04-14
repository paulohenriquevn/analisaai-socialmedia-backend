"""merge_multiple_heads

Revision ID: 3f084709490f
Revises: add_engagement_metrics, add_social_usernames, posting_time_001, 89e43f7a1b2c
Create Date: 2025-04-14 11:09:22.261323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f084709490f'
down_revision = ('add_engagement_metrics', 'add_social_usernames', 'posting_time_001', '89e43f7a1b2c')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass