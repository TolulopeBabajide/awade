"""m254_rename_curricula_title

AWD-M-254: The Curriculum model used plural-prefixed attribute `curricula_title`
while route parameters adopted the singular form `curriculum_id` after AWD-M-251.
Rename column to `curriculum_title` for consistency.

Revision ID: f4a5b6c7d8e9f0a1
Revises: a9b3c5d8e2f1a4b6
Create Date: 2026-06-30

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f4a5b6c7d8e9f0a1'
down_revision: Union[str, Sequence[str], None] = 'a9b3c5d8e2f1a4b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('curricula', 'curricula_title', new_column_name='curriculum_title')


def downgrade() -> None:
    op.alter_column('curricula', 'curriculum_title', new_column_name='curricula_title')
