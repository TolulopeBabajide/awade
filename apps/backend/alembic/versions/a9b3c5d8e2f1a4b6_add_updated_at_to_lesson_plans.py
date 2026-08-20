"""add_updated_at_to_lesson_plans

AWD-M-192: LessonPlanResponse.updated_at was always aliased to created_at
because the lesson_plans table had no updated_at column.  This migration
adds the column with a server default of now() so existing rows are back-filled
to their creation time.  When the update endpoint is implemented the ORM
onupdate clause will keep this column current on every UPDATE.

Revision ID: a9b3c5d8e2f1a4b6
Revises: d7a4b2e9f1c5
Create Date: 2026-06-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9b3c5d8e2f1a4b6'
down_revision: Union[str, Sequence[str], None] = 'd7a4b2e9f1c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'lesson_plans',
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('lesson_plans', 'updated_at')
