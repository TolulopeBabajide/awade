"""
Migration to add contexts table for storing lesson plan context information.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_contexts_table'
down_revision = '003_add_user_fields'
branch_labels = None
depends_on = None

def upgrade():
    """Add contexts table."""
    op.create_table('contexts',
        sa.Column('context_id', sa.Integer(), nullable=False),
        sa.Column('lesson_plan_id', sa.Integer(), nullable=False),
        sa.Column('context_text', sa.Text(), nullable=False),
        sa.Column('context_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['lesson_plan_id'], ['lesson_plans.lesson_plan_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('context_id')
    )
    
    # Add index for better query performance
    op.create_index(op.f('ix_contexts_lesson_plan_id'), 'contexts', ['lesson_plan_id'], unique=False)

def downgrade():
    """Remove contexts table."""
    op.drop_index(op.f('ix_contexts_lesson_plan_id'), table_name='contexts')
    op.drop_table('contexts') 