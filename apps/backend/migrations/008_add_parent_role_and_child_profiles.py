"""Add PARENT role and child_profiles / parent_guides tables

Revision ID: 008
Revises: 007
Create Date: 2026-04-16 00:00:00.000000

This migration:
1. Adds PARENT to the userrole enum
2. Creates the child_profiles table
3. Creates the parent_guides table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add PARENT to the userrole enum.
    #    For PostgreSQL we ALTER TYPE; for SQLite the enum is stored as a varchar
    #    so no DDL change is needed.
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'PARENT'")

    # 2. Create child_profiles table
    op.create_table(
        'child_profiles',
        sa.Column('child_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('school_name', sa.String(200), nullable=True),
        sa.Column('country_id', sa.Integer(), sa.ForeignKey('countries.country_id'), nullable=True),
        sa.Column('curricula_id', sa.Integer(), sa.ForeignKey('curricula.curricula_id'), nullable=True),
        sa.Column('grade_level_id', sa.Integer(), sa.ForeignKey('grade_levels.grade_level_id'), nullable=True),
        sa.Column('subjects', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_child_parent', 'child_profiles', ['parent_id'])

    # 3. Create parent_guides table
    op.create_table(
        'parent_guides',
        sa.Column('guide_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('child_id', sa.Integer(), sa.ForeignKey('child_profiles.child_id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic_id', sa.Integer(), sa.ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False),
        sa.Column('ai_generated_content', sa.Text(), nullable=True),
        sa.Column('user_edited_content', sa.Text(), nullable=True),
        sa.Column('is_bookmarked', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_guide_child_topic', 'parent_guides', ['child_id', 'topic_id'])


def downgrade():
    op.drop_index('idx_guide_child_topic', table_name='parent_guides')
    op.drop_table('parent_guides')
    op.drop_index('idx_child_parent', table_name='child_profiles')
    op.drop_table('child_profiles')

    # Note: Removing an enum value from PostgreSQL is complex and often
    # not worth doing in a downgrade. The PARENT value will remain in the
    # enum type but will not be used.
