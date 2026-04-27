"""fix_parent_guide_is_bookmarked_boolean

Revision ID: c4d2e8f1a9b3
Revises: b3f92c1d4e87
Create Date: 2026-04-27 00:00:00.000000

AWD-L-06 — ParentGuide.is_bookmarked stored as Integer(0/1); migrate to proper
Boolean column. The Pydantic response schema already declares is_bookmarked as
bool, so the ORM type now matches the application contract.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d2e8f1a9b3'
down_revision: Union[str, Sequence[str], None] = 'b3f92c1d4e87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL: cast existing 0/1 integer values to boolean.
    op.alter_column(
        'parent_guides',
        'is_bookmarked',
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        postgresql_using='is_bookmarked::boolean',
        server_default=sa.false(),
        existing_nullable=False,
        nullable=False,
    )


def downgrade() -> None:
    # Revert to Integer; cast boolean values back to 0/1.
    op.alter_column(
        'parent_guides',
        'is_bookmarked',
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        postgresql_using='is_bookmarked::integer',
        server_default=sa.text('0'),
        existing_nullable=False,
        nullable=False,
    )
