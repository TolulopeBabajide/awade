"""add password_reset_token to users

Revision ID: e5f2a3b4c6d8
Revises: f3a1c9d2b847
Create Date: 2026-05-04 00:00:00.000000

AWD-H-68: Password reset was a non-functional stub. These two columns support a
real token-based reset flow: the service stores the SHA-256 hash of the raw token
(never the raw token itself) and a UTC expiry timestamp. The reset endpoint verifies
by hashing the submitted token and comparing against this stored digest.
"""
from typing import Union, Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f2a3b4c6d8'
down_revision: Union[str, Sequence[str], None] = 'f3a1c9d2b847'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('users', recreate='always') as batch_op:
        batch_op.add_column(
            sa.Column('password_reset_token', sa.String(64), nullable=True)
        )
        batch_op.add_column(
            sa.Column('password_reset_expires', sa.DateTime, nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table('users', recreate='always') as batch_op:
        batch_op.drop_column('password_reset_expires')
        batch_op.drop_column('password_reset_token')
