"""
Add score metrics models.

Revision ID: 89e43f7a1b2c
Revises: 67a21f5b7c3d
Create Date: 2023-04-14 17:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89e43f7a1b2c'
down_revision = '67a21f5b7c3d'  # This should match the growth metrics migration
branch_labels = None
depends_on = None


def upgrade():
    # Add relevance_score column to the influencer table
    op.add_column('influencer', sa.Column('relevance_score', sa.Float(), nullable=True, default=0.0))
    
    # Create influencer_score table
    op.create_table(
        'influencer_score',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('influencer_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('engagement_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('reach_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('growth_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('consistency_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('audience_quality_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('engagement_weight', sa.Float(), nullable=True, default=0.3),
        sa.Column('reach_weight', sa.Float(), nullable=True, default=0.25),
        sa.Column('growth_weight', sa.Float(), nullable=True, default=0.25),
        sa.Column('consistency_weight', sa.Float(), nullable=True, default=0.1),
        sa.Column('audience_quality_weight', sa.Float(), nullable=True, default=0.1),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['influencer_id'], ['influencer.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add index for faster lookups
    op.create_index(
        'ix_influencer_score_influencer_date', 
        'influencer_score', 
        ['influencer_id', 'date']
    )


def downgrade():
    # Drop index and table
    op.drop_index('ix_influencer_score_influencer_date', 'influencer_score')
    op.drop_table('influencer_score')
    
    # Remove the relevance_score column from the influencer table
    op.drop_column('influencer', 'relevance_score')