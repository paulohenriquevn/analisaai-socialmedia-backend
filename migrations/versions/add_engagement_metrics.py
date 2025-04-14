"""Add engagement metrics table

Revision ID: add_engagement_metrics
Revises: fix_profile_image_length
Create Date: 2024-04-14 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_engagement_metrics'
down_revision = 'fix_profile_image_length'
branch_labels = None
depends_on = None


def upgrade():
    # Create influencer_engagement table
    op.create_table('influencer_engagement',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('influencer_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('posts_count', sa.Integer(), nullable=True, default=0),
        sa.Column('avg_likes_per_post', sa.Float(), nullable=True, default=0.0),
        sa.Column('avg_comments_per_post', sa.Float(), nullable=True, default=0.0),
        sa.Column('avg_shares_per_post', sa.Float(), nullable=True, default=0.0),
        sa.Column('engagement_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_likes', sa.Integer(), nullable=True, default=0),
        sa.Column('total_comments', sa.Integer(), nullable=True, default=0),
        sa.Column('total_shares', sa.Integer(), nullable=True, default=0),
        sa.Column('growth_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('video_views', sa.Integer(), nullable=True, default=0),
        sa.Column('reach', sa.Integer(), nullable=True, default=0),
        sa.Column('impressions', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['influencer_id'], ['influencer.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for faster lookups
    op.create_index(op.f('ix_influencer_engagement_date'), 'influencer_engagement', ['date'], unique=False)
    op.create_index(op.f('ix_influencer_engagement_influencer_id'), 'influencer_engagement', ['influencer_id'], unique=False)


def downgrade():
    # Remove indexes first
    op.drop_index(op.f('ix_influencer_engagement_influencer_id'), table_name='influencer_engagement')
    op.drop_index(op.f('ix_influencer_engagement_date'), table_name='influencer_engagement')
    
    # Then drop the table
    op.drop_table('influencer_engagement')