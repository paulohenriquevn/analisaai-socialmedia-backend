"""merge heads

Revision ID: merge_heads
Revises: add_social_usernames, posting_time_001, sentiment_analysis_001
Create Date: 2024-04-13 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = None
branch_labels = None
depends_on = ('add_social_usernames', 'posting_time_001', 'sentiment_analysis_001')


def upgrade():
    # This is a merge migration, no schema changes
    pass


def downgrade():
    # This is a merge migration, no schema changes
    pass