"""
Add growth metrics models.

Revision ID: 67a21f5b7c3d
Revises: 54b29e2f7a1d
Create Date: 2023-04-14 16:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67a21f5b7c3d'
down_revision = '54b29e2f7a1d'  # This should match the reach metrics migration
branch_labels = None
depends_on = None


def upgrade():
    # Create influencer_growth table
    op.create_table(
        'influencer_growth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('influencer_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('followers_count', sa.Integer(), nullable=True, default=0),
        sa.Column('new_followers_daily', sa.Integer(), nullable=True, default=0),
        sa.Column('new_followers_weekly', sa.Integer(), nullable=True, default=0),
        sa.Column('new_followers_monthly', sa.Integer(), nullable=True, default=0),
        sa.Column('retention_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('churn_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('daily_growth_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('weekly_growth_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('monthly_growth_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('growth_velocity', sa.Float(), nullable=True, default=0.0),
        sa.Column('growth_acceleration', sa.Float(), nullable=True, default=0.0),
        sa.Column('projected_followers_30d', sa.Integer(), nullable=True, default=0),
        sa.Column('projected_followers_90d', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['influencer_id'], ['influencer.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add index for faster lookups
    op.create_index(
        'ix_influencer_growth_influencer_date', 
        'influencer_growth', 
        ['influencer_id', 'date']
    )


def downgrade():
    # Drop index and table
    op.drop_index('ix_influencer_growth_influencer_date', 'influencer_growth')
    op.drop_table('influencer_growth')