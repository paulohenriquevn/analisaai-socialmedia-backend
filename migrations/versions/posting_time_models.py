"""Add fields for posting time analysis

Revision ID: posting_time_001
Revises: sentiment_analysis_001
Create Date: 2025-04-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'posting_time_001'
down_revision = 'sentiment_analysis_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to social_post table
    op.add_column('social_post', sa.Column('content_type', sa.String(length=20), nullable=True))
    op.add_column('social_post', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('social_post', sa.Column('engagement_rate', sa.Float(), nullable=True))
    
    # Create indexes for efficient queries
    op.create_index(op.f('ix_social_post_content_type'), 'social_post', ['content_type'], unique=False)
    op.create_index(op.f('ix_social_post_category'), 'social_post', ['category'], unique=False)
    op.create_index(op.f('ix_social_post_posted_at'), 'social_post', ['posted_at'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_social_post_posted_at'), table_name='social_post')
    op.drop_index(op.f('ix_social_post_category'), table_name='social_post')
    op.drop_index(op.f('ix_social_post_content_type'), table_name='social_post')
    
    # Drop columns
    op.drop_column('social_post', 'engagement_rate')
    op.drop_column('social_post', 'category')
    op.drop_column('social_post', 'content_type')