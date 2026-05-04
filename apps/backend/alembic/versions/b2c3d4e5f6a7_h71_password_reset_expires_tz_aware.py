"""h71_password_reset_expires_tz_aware

AWD-H-71: Change password_reset_expires from tz-naive DateTime to tz-aware
DateTime(timezone=True) (TIMESTAMP WITH TIME ZONE on PostgreSQL).

A tz-naive column compared against a tz-aware Python value works only when the
PostgreSQL server timezone is UTC (which is true for Render's current deployment),
but silently breaks if the timezone drifts or changes.  Storing TIMESTAMP WITH
TIME ZONE removes the dependency on server timezone configuration and aligns the
column type with how auth_service.py writes it
(datetime.now(timezone.utc) + timedelta(hours=1)).

Revision ID: b2c3d4e5f6a7
Revises: e5f2a3b4c6d8
Create Date: 2026-05-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'e5f2a3b4c6d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch_alter_table with recreate='always' so the migration works on
    # both SQLite (used in tests — no native ALTER TYPE) and PostgreSQL.
    # On PostgreSQL this rewrites the 'users' table; on SQLite it does so via
    # CREATE/INSERT/DROP.  Existing NULL values are preserved as-is; existing
    # non-NULL tz-naive values are reinterpreted as UTC by psycopg2 when
    # timezone=True is set on the ORM column.
    with op.batch_alter_table('users', schema=None, recreate='always') as batch_op:
        batch_op.alter_column(
            'password_reset_expires',
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=True,
        )


def downgrade() -> None:
    # Revert to tz-naive DateTime.  Any stored UTC offsets are stripped — rows
    # with non-UTC timestamps would shift silently.  Safe on Render (UTC server)
    # but noted as a caveat for other deployments.
    with op.batch_alter_table('users', schema=None, recreate='always') as batch_op:
        batch_op.alter_column(
            'password_reset_expires',
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=True,
        )
