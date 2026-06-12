"""add_themes_and_pedagogy_tables

Revision ID: d7a4b2e9f1c5
Revises: b2c3d4e5f6a7, c4d2e8f1a9b3
Create Date: 2026-06-04 00:00:00.000000

NERDC full-curriculum capture: adds the ``themes`` table (grouping topics
within a curriculum structure), a nullable ``theme_id`` FK on ``topics``,
and four pedagogy child tables mirroring the LearningObjective/TopicContent
pattern: ``teacher_activities``, ``student_activities``,
``teaching_learning_materials``, ``evaluation_guides``.

This revision also MERGES the two pre-existing Alembic heads
(b2c3d4e5f6a7 — password-reset tz fix; c4d2e8f1a9b3 — parent-guide
is_bookmarked fix) so ``alembic upgrade head`` resolves to a single head
again. Both parents are schema-independent of the changes below.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7a4b2e9f1c5'
down_revision: Union[str, Sequence[str], None] = ('b2c3d4e5f6a7', 'c4d2e8f1a9b3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'themes',
        sa.Column('theme_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('curriculum_structure_id', sa.Integer(), nullable=False),
        sa.Column('theme_number', sa.Integer(), nullable=True),
        sa.Column('theme_title', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ['curriculum_structure_id'],
            ['curriculum_structures.curriculum_structure_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('theme_id'),
    )
    op.create_index(
        'idx_theme_structure_number',
        'themes',
        ['curriculum_structure_id', 'theme_number'],
        unique=True,
    )

    op.add_column('topics', sa.Column('theme_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_topics_theme_id',
        'topics',
        'themes',
        ['theme_id'],
        ['theme_id'],
        ondelete='SET NULL',
    )

    op.create_table(
        'teacher_activities',
        sa.Column('teacher_activity_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('activity', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.topic_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('teacher_activity_id'),
    )
    op.create_table(
        'student_activities',
        sa.Column('student_activity_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('activity', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.topic_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_activity_id'),
    )
    op.create_table(
        'teaching_learning_materials',
        sa.Column('material_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('material', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.topic_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('material_id'),
    )
    op.create_table(
        'evaluation_guides',
        sa.Column('evaluation_guide_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('guide_item', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.topic_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('evaluation_guide_id'),
    )


def downgrade() -> None:
    op.drop_table('evaluation_guides')
    op.drop_table('teaching_learning_materials')
    op.drop_table('student_activities')
    op.drop_table('teacher_activities')
    op.drop_constraint('fk_topics_theme_id', 'topics', type_='foreignkey')
    op.drop_column('topics', 'theme_id')
    op.drop_index('idx_theme_structure_number', table_name='themes')
    op.drop_table('themes')
