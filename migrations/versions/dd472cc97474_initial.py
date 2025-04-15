"""initial

Revision ID: dd472cc97474
Revises: 
Create Date: 2025-04-14 22:39:00.678369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd472cc97474'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('plan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('social_page_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('social_page_category', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_social_page_category_name'), ['name'], unique=True)

    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('facebook_id', sa.String(length=100), nullable=True),
    sa.Column('instagram_id', sa.String(length=100), nullable=True),
    sa.Column('tiktok_id', sa.String(length=100), nullable=True),
    sa.Column('facebook_username', sa.String(length=100), nullable=True),
    sa.Column('instagram_username', sa.String(length=100), nullable=True),
    sa.Column('tiktok_username', sa.String(length=100), nullable=True),
    sa.Column('profile_image', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('facebook_id'),
    sa.UniqueConstraint('instagram_id'),
    sa.UniqueConstraint('tiktok_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('organization',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('plan_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('plan_feature',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=True),
    sa.Column('feature', sa.String(length=100), nullable=False),
    sa.Column('value', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('social_page',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('full_name', sa.String(length=100), nullable=True),
    sa.Column('platform', sa.String(length=20), nullable=False),
    sa.Column('profile_url', sa.String(length=1024), nullable=True),
    sa.Column('profile_image', sa.Text(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('followers_count', sa.Integer(), nullable=True),
    sa.Column('following_count', sa.Integer(), nullable=True),
    sa.Column('posts_count', sa.Integer(), nullable=True),
    sa.Column('engagement_rate', sa.Float(), nullable=True),
    sa.Column('social_score', sa.Float(), nullable=True),
    sa.Column('relevance_score', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username', 'platform', name='uix_social_page_username_platform')
    )
    with op.batch_alter_table('social_page', schema=None) as batch_op:
        batch_op.create_index('idx_social_page_user_platform', ['user_id', 'platform'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_platform'), ['platform'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_user_id'), ['user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_username'), ['username'], unique=False)

    op.create_table('social_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('platform', sa.String(length=20), nullable=False),
    sa.Column('access_token', sa.Text(), nullable=False),
    sa.Column('refresh_token', sa.Text(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'platform', name='uix_social_token_user_platform')
    )
    with op.batch_alter_table('social_token', schema=None) as batch_op:
        batch_op.create_index('idx_social_token_user_platform', ['user_id', 'platform'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_token_expires_at'), ['expires_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_token_platform'), ['platform'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_token_user_id'), ['user_id'], unique=False)

    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.create_table('organization_users',
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('organization_id', 'user_id')
    )
    op.create_table('social_page_categories',
    sa.Column('social_page_id', sa.Integer(), nullable=False),
    sa.Column('social_page_category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['social_page_category_id'], ['social_page_category.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['social_page_id'], ['social_page.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('social_page_id', 'social_page_category_id')
    )
    op.create_table('social_page_engagement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('social_page_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('posts_count', sa.Integer(), nullable=True),
    sa.Column('avg_likes_per_post', sa.Float(), nullable=True),
    sa.Column('avg_comments_per_post', sa.Float(), nullable=True),
    sa.Column('avg_shares_per_post', sa.Float(), nullable=True),
    sa.Column('engagement_rate', sa.Float(), nullable=True),
    sa.Column('total_likes', sa.Integer(), nullable=True),
    sa.Column('total_comments', sa.Integer(), nullable=True),
    sa.Column('total_shares', sa.Integer(), nullable=True),
    sa.Column('growth_rate', sa.Float(), nullable=True),
    sa.Column('video_views', sa.Integer(), nullable=True),
    sa.Column('reach', sa.Integer(), nullable=True),
    sa.Column('impressions', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['social_page_id'], ['social_page.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_page_id', 'date', name='uix_social_page_engagement_page_date')
    )
    with op.batch_alter_table('social_page_engagement', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_social_page_engagement_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_engagement_social_page_id'), ['social_page_id'], unique=False)

    op.create_table('social_page_growth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('social_page_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('followers_count', sa.Integer(), nullable=True),
    sa.Column('new_followers_daily', sa.Integer(), nullable=True),
    sa.Column('new_followers_weekly', sa.Integer(), nullable=True),
    sa.Column('new_followers_monthly', sa.Integer(), nullable=True),
    sa.Column('retention_rate', sa.Float(), nullable=True),
    sa.Column('churn_rate', sa.Float(), nullable=True),
    sa.Column('daily_growth_rate', sa.Float(), nullable=True),
    sa.Column('weekly_growth_rate', sa.Float(), nullable=True),
    sa.Column('monthly_growth_rate', sa.Float(), nullable=True),
    sa.Column('growth_velocity', sa.Float(), nullable=True),
    sa.Column('growth_acceleration', sa.Float(), nullable=True),
    sa.Column('projected_followers_30d', sa.Integer(), nullable=True),
    sa.Column('projected_followers_90d', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['social_page_id'], ['social_page.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_page_id', 'date', name='uix_social_page_growth_page_date')
    )
    with op.batch_alter_table('social_page_growth', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_social_page_growth_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_growth_social_page_id'), ['social_page_id'], unique=False)

    op.create_table('social_page_metric',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('social_page_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('followers', sa.Integer(), nullable=True),
    sa.Column('engagement', sa.Float(), nullable=True),
    sa.Column('posts', sa.Integer(), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('comments', sa.Integer(), nullable=True),
    sa.Column('shares', sa.Integer(), nullable=True),
    sa.Column('views', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['social_page_id'], ['social_page.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_page_id', 'date', name='uix_social_page_metric_page_date')
    )
    with op.batch_alter_table('social_page_metric', schema=None) as batch_op:
        batch_op.create_index('idx_social_page_metrics_date', ['social_page_id', 'date'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_metric_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_metric_social_page_id'), ['social_page_id'], unique=False)

    op.create_table('social_page_post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('platform', sa.String(length=20), nullable=False),
    sa.Column('post_id', sa.String(length=100), nullable=False),
    sa.Column('social_page_id', sa.Integer(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('post_url', sa.Text(), nullable=True),
    sa.Column('media_url', sa.Text(), nullable=True),
    sa.Column('posted_at', sa.DateTime(), nullable=True),
    sa.Column('content_type', sa.String(length=20), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('likes_count', sa.Integer(), nullable=True),
    sa.Column('comments_count', sa.Integer(), nullable=True),
    sa.Column('shares_count', sa.Integer(), nullable=True),
    sa.Column('views_count', sa.Integer(), nullable=True),
    sa.Column('engagement_rate', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['social_page_id'], ['social_page.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('social_page_post', schema=None) as batch_op:
        batch_op.create_index('idx_social_page_post_page_date', ['social_page_id', 'posted_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_category'), ['category'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_content_type'), ['content_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_platform'), ['platform'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_post_id'), ['post_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_social_page_post_posted_at'), ['posted_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_social_page_id'), ['social_page_id'], unique=False)

    op.create_table('social_page_reach',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('social_page_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('impressions', sa.Integer(), nullable=True),
    sa.Column('reach', sa.Integer(), nullable=True),
    sa.Column('story_views', sa.Integer(), nullable=True),
    sa.Column('profile_views', sa.Integer(), nullable=True),
    sa.Column('stories_count', sa.Integer(), nullable=True),
    sa.Column('story_engagement_rate', sa.Float(), nullable=True),
    sa.Column('story_exit_rate', sa.Float(), nullable=True),
    sa.Column('story_completion_rate', sa.Float(), nullable=True),
    sa.Column('avg_watch_time', sa.Float(), nullable=True),
    sa.Column('audience_growth', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['social_page_id'], ['social_page.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_page_id', 'date', name='uix_social_page_reach_page_date')
    )
    with op.batch_alter_table('social_page_reach', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_social_page_reach_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_reach_social_page_id'), ['social_page_id'], unique=False)

    op.create_table('social_page_score',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('social_page_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('overall_score', sa.Float(), nullable=True),
    sa.Column('engagement_score', sa.Float(), nullable=True),
    sa.Column('reach_score', sa.Float(), nullable=True),
    sa.Column('growth_score', sa.Float(), nullable=True),
    sa.Column('consistency_score', sa.Float(), nullable=True),
    sa.Column('audience_quality_score', sa.Float(), nullable=True),
    sa.Column('engagement_weight', sa.Float(), nullable=True),
    sa.Column('reach_weight', sa.Float(), nullable=True),
    sa.Column('growth_weight', sa.Float(), nullable=True),
    sa.Column('consistency_weight', sa.Float(), nullable=True),
    sa.Column('audience_quality_weight', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['social_page_id'], ['social_page.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_page_id', 'date', name='uix_social_page_score_page_date')
    )
    with op.batch_alter_table('social_page_score', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_social_page_score_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_score_social_page_id'), ['social_page_id'], unique=False)

    op.create_table('social_page_post_comment',
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
    sa.ForeignKeyConstraint(['post_id'], ['social_page_post.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('social_page_post_comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_social_page_post_comment_author_username'), ['author_username'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_comment_comment_id'), ['comment_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_social_page_post_comment_is_critical'), ['is_critical'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_comment_platform'), ['platform'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_comment_post_id'), ['post_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_comment_posted_at'), ['posted_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_comment_replied_to_id'), ['replied_to_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_social_page_post_comment_sentiment'), ['sentiment'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('social_page_post_comment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_post_comment_sentiment'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_comment_replied_to_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_comment_posted_at'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_comment_post_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_comment_platform'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_comment_is_critical'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_comment_comment_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_comment_author_username'))

    op.drop_table('social_page_post_comment')
    with op.batch_alter_table('social_page_score', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_score_social_page_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_score_date'))

    op.drop_table('social_page_score')
    with op.batch_alter_table('social_page_reach', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_reach_social_page_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_reach_date'))

    op.drop_table('social_page_reach')
    with op.batch_alter_table('social_page_post', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_post_social_page_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_posted_at'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_post_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_platform'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_content_type'))
        batch_op.drop_index(batch_op.f('ix_social_page_post_category'))
        batch_op.drop_index('idx_social_page_post_page_date')

    op.drop_table('social_page_post')
    with op.batch_alter_table('social_page_metric', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_metric_social_page_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_metric_date'))
        batch_op.drop_index('idx_social_page_metrics_date')

    op.drop_table('social_page_metric')
    with op.batch_alter_table('social_page_growth', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_growth_social_page_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_growth_date'))

    op.drop_table('social_page_growth')
    with op.batch_alter_table('social_page_engagement', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_engagement_social_page_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_engagement_date'))

    op.drop_table('social_page_engagement')
    op.drop_table('social_page_categories')
    op.drop_table('organization_users')
    op.drop_table('user_roles')
    with op.batch_alter_table('social_token', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_token_user_id'))
        batch_op.drop_index(batch_op.f('ix_social_token_platform'))
        batch_op.drop_index(batch_op.f('ix_social_token_expires_at'))
        batch_op.drop_index('idx_social_token_user_platform')

    op.drop_table('social_token')
    with op.batch_alter_table('social_page', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_username'))
        batch_op.drop_index(batch_op.f('ix_social_page_user_id'))
        batch_op.drop_index(batch_op.f('ix_social_page_platform'))
        batch_op.drop_index('idx_social_page_user_platform')

    op.drop_table('social_page')
    op.drop_table('plan_feature')
    op.drop_table('organization')
    op.drop_table('user')
    with op.batch_alter_table('social_page_category', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_social_page_category_name'))

    op.drop_table('social_page_category')
    op.drop_table('role')
    op.drop_table('plan')
    # ### end Alembic commands ###
