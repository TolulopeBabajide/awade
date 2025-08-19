"""Add profile image data fields

Revision ID: 007
Revises: 006
Create Date: 2025-08-18 22:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None

def upgrade():
    # Add new profile image data fields
    op.add_column('users', sa.Column('profile_image_data', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('profile_image_type', sa.String(50), nullable=True))

def downgrade():
    # Remove the new columns
    op.drop_column('users', 'profile_image_data')
    op.drop_column('users', 'profile_image_type')
