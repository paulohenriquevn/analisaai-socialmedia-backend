"""Fix profile image length

Revision ID: fix_profile_image_length
Revises: merge_heads
Create Date: 2024-04-14 10:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_profile_image_length'
down_revision = 'merge_heads'
branch_labels = None
depends_on = None


def upgrade():
    # Alter profile_url column to be a longer string
    op.alter_column('influencer', 'profile_url',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=1024),
               existing_nullable=True)
    
    # Alter profile_image column to be Text type instead of limited varchar
    op.alter_column('influencer', 'profile_image',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=True)


def downgrade():
    # This might truncate data in production, so be careful with downgrades
    op.alter_column('influencer', 'profile_url',
               existing_type=sa.String(length=1024),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
    
    op.alter_column('influencer', 'profile_image',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)