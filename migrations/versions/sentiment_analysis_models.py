"""Add sentiment analysis models for posts and comments

Revision ID: sentiment_analysis_001
Revises: 828233b29ccb
Create Date: 2025-04-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'sentiment_analysis_001'
down_revision = '828233b29ccb'
branch_labels = None
depends_on = None


def upgrade():
    # Create social_post table
    op.create_table('social_post',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('post_id', sa.String(length=100), nullable=False),
        sa.Column('influencer_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('post_url', sa.String(length=255), nullable=True),
        sa.Column('media_url', sa.String(length=255), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True),
        sa.Column('comments_count', sa.Integer(), nullable=True),
        sa.Column('shares_count', sa.Integer(), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['influencer_id'], ['influencer.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id')
    )
    
    # Create post_comment table
    op.create_table('post_comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('comment_id', sa.String(length=100), nullable=False),
        sa.Column('author_username', sa.String(length=100), nullable=True),
        sa.Column('author_display_name', sa.String(length=100), nullable=True),
        sa.Column('author_picture', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True),
        sa.Column('replied_to_id', sa.String(length=100), nullable=True),
        sa.Column('sentiment', sa.String(length=10), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('is_critical', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['social_post.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('comment_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_social_post_influencer_id'), 'social_post', ['influencer_id'], unique=False)
    op.create_index(op.f('ix_social_post_platform'), 'social_post', ['platform'], unique=False)
    op.create_index(op.f('ix_post_comment_platform'), 'post_comment', ['platform'], unique=False)
    op.create_index(op.f('ix_post_comment_post_id'), 'post_comment', ['post_id'], unique=False)
    op.create_index(op.f('ix_post_comment_sentiment'), 'post_comment', ['sentiment'], unique=False)
    op.create_index(op.f('ix_post_comment_is_critical'), 'post_comment', ['is_critical'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_post_comment_is_critical'), table_name='post_comment')
    op.drop_index(op.f('ix_post_comment_sentiment'), table_name='post_comment')
    op.drop_index(op.f('ix_post_comment_post_id'), table_name='post_comment')
    op.drop_index(op.f('ix_post_comment_platform'), table_name='post_comment')
    op.drop_index(op.f('ix_social_post_platform'), table_name='social_post')
    op.drop_index(op.f('ix_social_post_influencer_id'), table_name='social_post')
    op.drop_table('post_comment')
    op.drop_table('social_post')