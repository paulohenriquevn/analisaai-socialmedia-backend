"""
Add reach metrics models.

Revision ID: 54b29e2f7a1d
Revises: 828233b29ccb
Create Date: 2023-04-14 15:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54b29e2f7a1d'
down_revision = '828233b29ccb'  # Adjust this to the actual latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Create influencer_reach table
    op.create_table(
        'influencer_reach',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('influencer_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('impressions', sa.Integer(), nullable=True, default=0),
        sa.Column('reach', sa.Integer(), nullable=True, default=0),
        sa.Column('story_views', sa.Integer(), nullable=True, default=0),
        sa.Column('profile_views', sa.Integer(), nullable=True, default=0),
        sa.Column('stories_count', sa.Integer(), nullable=True, default=0),
        sa.Column('story_engagement_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('story_exit_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('story_completion_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('avg_watch_time', sa.Float(), nullable=True, default=0.0),
        sa.Column('audience_growth', sa.Float(), nullable=True, default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['influencer_id'], ['influencer.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add index for faster lookups
    op.create_index(
        'ix_influencer_reach_influencer_date', 
        'influencer_reach', 
        ['influencer_id', 'date']
    )


def downgrade():
    # Drop index and table
    op.drop_index('ix_influencer_reach_influencer_date', 'influencer_reach')
    op.drop_table('influencer_reach')