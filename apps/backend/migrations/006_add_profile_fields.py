"""
Migration: Add profile fields to users table

This migration adds new fields to support enhanced user profiles:
- profile_image_url: URL to user's profile image
- phone: User's phone number
- bio: User's bio/description

Revision ID: 006
Revises: 005_add_user_id_to_lesson_plans
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005_add_user_id_to_lesson_plans'
branch_labels = None
depends_on = None

def upgrade():
    """Add profile fields to users table."""
    # Add profile_image_url column
    op.add_column('users', sa.Column('profile_image_url', sa.String(500), nullable=True))
    
    # Add phone column
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    
    # Add bio column
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))

def downgrade():
    """Remove profile fields from users table."""
    # Remove bio column
    op.drop_column('users', 'bio')
    
    # Remove phone column
    op.drop_column('users', 'phone')
    
    # Remove profile_image_url column
    op.drop_column('users', 'profile_image_url')
