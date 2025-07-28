"""
Migration: Add missing fields to User table

This migration adds the missing fields to the User table that are required for the authentication and authorization system.

Author: Tolulope Babajide
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_user_fields'
down_revision = '002_curriculum_schema'
branch_labels = None
depends_on = None

def upgrade():
    """Add missing fields to User table."""
    # Add role column
    op.add_column('users', sa.Column('role', sa.Enum('educator', 'admin', name='userrole'), nullable=False, server_default='educator'))
    
    # Add profile fields
    op.add_column('users', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('region', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('school_name', sa.String(200), nullable=True))
    op.add_column('users', sa.Column('subjects', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('grade_levels', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('languages_spoken', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

def downgrade():
    """Remove added fields from User table."""
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'languages_spoken')
    op.drop_column('users', 'grade_levels')
    op.drop_column('users', 'subjects')
    op.drop_column('users', 'school_name')
    op.drop_column('users', 'region')
    op.drop_column('users', 'country')
    op.drop_column('users', 'role') 