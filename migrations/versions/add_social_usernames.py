"""add social usernames

Revision ID: add_social_usernames
Revises: 828233b29ccb, sentiment_analysis_models, posting_time_models
Create Date: 2024-04-13 20:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_social_usernames'
down_revision = '828233b29ccb'
branch_labels = None
depends_on = None


def upgrade():
    # Add social media username columns
    op.add_column('user', sa.Column('facebook_username', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('instagram_username', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('tiktok_username', sa.String(length=100), nullable=True))


def downgrade():
    # Remove added columns
    op.drop_column('user', 'facebook_username')
    op.drop_column('user', 'instagram_username')
    op.drop_column('user', 'tiktok_username')