"""Update SocialPost URL fields to Text

Revision ID: update_social_post_url_fields
Revises: 000229020789
Create Date: 2025-04-14 17:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_social_post_url_fields'
down_revision = '000229020789'
branch_labels = None
depends_on = None


def upgrade():
    # Check if social_post table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'social_post' in tables:
        # Modify post_url and media_url columns to use Text instead of String(255)
        op.alter_column('social_post', 'post_url',
                        existing_type=sa.VARCHAR(length=255),
                        type_=sa.Text(),
                        existing_nullable=True)
        op.alter_column('social_post', 'media_url',
                        existing_type=sa.VARCHAR(length=255),
                        type_=sa.Text(),
                        existing_nullable=True)
    else:
        # If table doesn't exist yet, it will be created with the correct types
        # from the model definitions (no action needed)
        pass


def downgrade():
    # Check if social_post table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'social_post' in tables:
        # Convert back to VARCHAR(255) - note: this might fail if the data is too long
        op.alter_column('social_post', 'post_url',
                        existing_type=sa.Text(),
                        type_=sa.VARCHAR(length=255),
                        existing_nullable=True)
        op.alter_column('social_post', 'media_url',
                        existing_type=sa.Text(),
                        type_=sa.VARCHAR(length=255),
                        existing_nullable=True)