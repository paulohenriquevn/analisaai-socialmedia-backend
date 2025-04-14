"""Adiciona relação Many-to-Many entre usuários e influenciadores

Revision ID: 0e71c31f2410
Revises: update_social_post_url_fields
Create Date: 2025-04-14 16:10:54.030487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e71c31f2410'
down_revision = 'update_social_post_url_fields'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('influencer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('influencer_engagement', schema=None) as batch_op:
        batch_op.drop_index('ix_influencer_engagement_date')
        batch_op.drop_index('ix_influencer_engagement_influencer_id')

    with op.batch_alter_table('influencer_growth', schema=None) as batch_op:
        batch_op.drop_index('ix_influencer_growth_date')
        batch_op.drop_index('ix_influencer_growth_influencer_id')

    with op.batch_alter_table('influencer_reach', schema=None) as batch_op:
        batch_op.drop_index('ix_influencer_reach_date')
        batch_op.drop_index('ix_influencer_reach_influencer_id')

    with op.batch_alter_table('influencer_score', schema=None) as batch_op:
        batch_op.drop_index('ix_influencer_score_date')
        batch_op.drop_index('ix_influencer_score_influencer_id')

    with op.batch_alter_table('post_comment', schema=None) as batch_op:
        batch_op.drop_index('ix_post_comment_is_critical')
        batch_op.drop_index('ix_post_comment_platform')
        batch_op.drop_index('ix_post_comment_post_id')
        batch_op.drop_index('ix_post_comment_sentiment')

    with op.batch_alter_table('social_post', schema=None) as batch_op:
        batch_op.drop_index('ix_social_post_category')
        batch_op.drop_index('ix_social_post_content_type')
        batch_op.drop_index('ix_social_post_influencer_id')
        batch_op.drop_index('ix_social_post_platform')
        batch_op.drop_index('ix_social_post_posted_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('social_post', schema=None) as batch_op:
        batch_op.create_index('ix_social_post_posted_at', ['posted_at'], unique=False)
        batch_op.create_index('ix_social_post_platform', ['platform'], unique=False)
        batch_op.create_index('ix_social_post_influencer_id', ['influencer_id'], unique=False)
        batch_op.create_index('ix_social_post_content_type', ['content_type'], unique=False)
        batch_op.create_index('ix_social_post_category', ['category'], unique=False)

    with op.batch_alter_table('post_comment', schema=None) as batch_op:
        batch_op.create_index('ix_post_comment_sentiment', ['sentiment'], unique=False)
        batch_op.create_index('ix_post_comment_post_id', ['post_id'], unique=False)
        batch_op.create_index('ix_post_comment_platform', ['platform'], unique=False)
        batch_op.create_index('ix_post_comment_is_critical', ['is_critical'], unique=False)

    with op.batch_alter_table('influencer_score', schema=None) as batch_op:
        batch_op.create_index('ix_influencer_score_influencer_id', ['influencer_id'], unique=False)
        batch_op.create_index('ix_influencer_score_date', ['date'], unique=False)

    with op.batch_alter_table('influencer_reach', schema=None) as batch_op:
        batch_op.create_index('ix_influencer_reach_influencer_id', ['influencer_id'], unique=False)
        batch_op.create_index('ix_influencer_reach_date', ['date'], unique=False)

    with op.batch_alter_table('influencer_growth', schema=None) as batch_op:
        batch_op.create_index('ix_influencer_growth_influencer_id', ['influencer_id'], unique=False)
        batch_op.create_index('ix_influencer_growth_date', ['date'], unique=False)

    with op.batch_alter_table('influencer_engagement', schema=None) as batch_op:
        batch_op.create_index('ix_influencer_engagement_influencer_id', ['influencer_id'], unique=False)
        batch_op.create_index('ix_influencer_engagement_date', ['date'], unique=False)

    with op.batch_alter_table('influencer', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
