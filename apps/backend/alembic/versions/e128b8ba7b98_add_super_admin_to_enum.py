"""add_super_admin_to_enum

Revision ID: e128b8ba7b98
Revises: 1143e4a30048
Create Date: 2026-01-10 23:30:31.192931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e128b8ba7b98'
down_revision: Union[str, Sequence[str], None] = '1143e4a30048'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # PostgreSQL specific: Add value to enum
    # 'commit_as_batch' is not needed for this direct SQL but we must use it outside transactions if possible
    op.execute("ALTER TYPE userrole ADD VALUE 'SUPER_ADMIN'")


def downgrade() -> None:
    """Downgrade schema."""
    # Enum values cannot be easily removed in PostgreSQL without recreating the type
    pass
